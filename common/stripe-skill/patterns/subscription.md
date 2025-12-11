# Subscription Billing with Stripe

Recurring payments with automatic billing cycles.

## When to Use

- SaaS products with monthly/yearly plans
- Membership sites
- Any recurring billing scenario

## Key Concepts

- **Customer**: The person paying (stored in Stripe)
- **Product**: What you're selling (e.g., "Pro Plan")
- **Price**: How much and how often (e.g., $10/month)
- **Subscription**: The ongoing relationship between Customer and Price

## Architecture

```
User selects plan → Create/retrieve Customer → Create Checkout Session (mode: subscription) →
Stripe handles payment → Webhook: customer.subscription.created → Grant access →
Monthly: Webhook: invoice.paid → Continue access →
Cancel/Fail: Webhook: customer.subscription.deleted → Revoke access
```

## Implementation

### Step 1: Create Products and Prices

```javascript
// Create product
const product = await stripe.products.create({
  name: 'Pro Plan',
  description: 'Full access to all features',
});

// Create monthly price
const monthlyPrice = await stripe.prices.create({
  product: product.id,
  unit_amount: 999, // $9.99
  currency: 'usd',
  recurring: {
    interval: 'month',
  },
});

// Create yearly price (with discount)
const yearlyPrice = await stripe.prices.create({
  product: product.id,
  unit_amount: 9990, // $99.90 (save ~$20)
  currency: 'usd',
  recurring: {
    interval: 'year',
  },
});
```

### Step 2: Database Schema

```sql
-- Users table needs Stripe customer ID
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255);
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'inactive';
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50);
ALTER TABLE users ADD COLUMN subscription_current_period_end TIMESTAMP;
```

### Step 3: Create or Get Customer

```javascript
async function getOrCreateStripeCustomer(user) {
  // Return existing customer if we have one
  if (user.stripeCustomerId) {
    return user.stripeCustomerId;
  }

  // Create new customer
  const customer = await stripe.customers.create({
    email: user.email,
    metadata: {
      userId: user.id,
    },
  });

  // Save to database
  await db.users.update(user.id, {
    stripeCustomerId: customer.id,
  });

  return customer.id;
}
```

### Step 4: Create Checkout Session

```javascript
app.post('/create-subscription-checkout', async (req, res) => {
  const { priceId } = req.body;
  const user = req.user; // From your auth middleware

  // Validate price
  const allowedPrices = {
    'price_monthly_xxx': 'pro',
    'price_yearly_xxx': 'pro',
  };

  if (!allowedPrices[priceId]) {
    return res.status(400).json({ error: 'Invalid price' });
  }

  const customerId = await getOrCreateStripeCustomer(user);

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    customer: customerId,
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    success_url: `${process.env.DOMAIN}/subscription/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.DOMAIN}/pricing`,
    metadata: {
      userId: user.id,
    },
    subscription_data: {
      metadata: {
        userId: user.id,
      },
    },
  });

  res.json({ url: session.url });
});
```

### Step 5: Webhook Handler

```javascript
app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;

  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object;
      if (session.mode === 'subscription') {
        await handleSubscriptionCreated(session);
      }
      break;
    }

    case 'customer.subscription.updated': {
      const subscription = event.data.object;
      await handleSubscriptionUpdated(subscription);
      break;
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object;
      await handleSubscriptionCanceled(subscription);
      break;
    }

    case 'invoice.paid': {
      const invoice = event.data.object;
      await handleInvoicePaid(invoice);
      break;
    }

    case 'invoice.payment_failed': {
      const invoice = event.data.object;
      await handlePaymentFailed(invoice);
      break;
    }
  }

  res.status(200).json({ received: true });
});

async function handleSubscriptionCreated(session) {
  const userId = session.metadata.userId;

  // Retrieve the subscription to get details
  const subscription = await stripe.subscriptions.retrieve(session.subscription);

  await db.users.update(userId, {
    subscriptionStatus: 'active',
    subscriptionTier: 'pro', // Map from price ID
    subscriptionCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
  });

  await sendWelcomeEmail(userId);
}

async function handleSubscriptionUpdated(subscription) {
  const userId = subscription.metadata.userId;

  await db.users.update(userId, {
    subscriptionStatus: subscription.status,
    subscriptionCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
  });
}

async function handleSubscriptionCanceled(subscription) {
  const userId = subscription.metadata.userId;

  await db.users.update(userId, {
    subscriptionStatus: 'canceled',
    subscriptionTier: null,
  });

  await sendCancellationEmail(userId);
}

async function handleInvoicePaid(invoice) {
  // Subscription renewed successfully
  if (invoice.subscription) {
    const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
    const userId = subscription.metadata.userId;

    await db.users.update(userId, {
      subscriptionCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
    });
  }
}

async function handlePaymentFailed(invoice) {
  // Payment failed - Stripe will retry automatically
  // Consider sending a notification to the user
  if (invoice.subscription) {
    const subscription = await stripe.subscriptions.retrieve(invoice.subscription);
    const userId = subscription.metadata.userId;

    await sendPaymentFailedEmail(userId);
  }
}
```

### Step 6: Customer Portal (Manage Subscription)

Let users manage their subscription without you building UI:

```javascript
app.post('/create-portal-session', async (req, res) => {
  const user = req.user;

  if (!user.stripeCustomerId) {
    return res.status(400).json({ error: 'No subscription found' });
  }

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: user.stripeCustomerId,
    return_url: `${process.env.DOMAIN}/account`,
  });

  res.json({ url: portalSession.url });
});
```

Configure portal in Dashboard: https://dashboard.stripe.com/settings/billing/portal

### Step 7: Check Subscription Status

```javascript
// Middleware to check subscription
function requireSubscription(tier = 'pro') {
  return async (req, res, next) => {
    const user = req.user;

    if (user.subscriptionStatus !== 'active') {
      return res.status(403).json({ error: 'Subscription required' });
    }

    // Check if subscription is still valid
    if (new Date() > user.subscriptionCurrentPeriodEnd) {
      // Subscription expired - sync with Stripe
      await syncSubscriptionStatus(user);

      if (user.subscriptionStatus !== 'active') {
        return res.status(403).json({ error: 'Subscription expired' });
      }
    }

    next();
  };
}

// Usage
app.get('/api/premium-feature', requireSubscription('pro'), (req, res) => {
  // Only subscribed users can access
});
```

## Subscription Lifecycle

```
                    ┌─────────────────────┐
                    │   User signs up     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Checkout Session   │
                    │  (mode: subscription)│
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐ ┌─────▼─────┐ ┌───────▼───────┐
     │ checkout.session│ │ customer. │ │   invoice.    │
     │   .completed    │ │subscription│ │    paid       │
     └────────┬────────┘ │ .created  │ └───────┬───────┘
              │          └───────────┘         │
              │                                │
     ┌────────▼────────────────────────────────▼────────┐
     │              Grant Access (active)               │
     └────────────────────────┬─────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
 ┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼───────┐
 │  invoice.paid   │ │invoice.payment_ │ │  customer.    │
 │   (renewal)     │ │    failed       │ │ subscription. │
 └────────┬────────┘ └────────┬────────┘ │   deleted     │
          │                   │          └───────┬───────┘
          │                   │                  │
 ┌────────▼────────┐ ┌────────▼────────┐ ┌──────▼───────┐
 │ Continue access │ │ Notify user,    │ │ Revoke access│
 │ Update period   │ │ Stripe retries  │ │ (canceled)   │
 └─────────────────┘ └─────────────────┘ └──────────────┘
```

## Common Customizations

### Free Trial
```javascript
const session = await stripe.checkout.sessions.create({
  // ...
  subscription_data: {
    trial_period_days: 14,
  },
});
```

### Proration on Plan Change
```javascript
// Upgrade/downgrade mid-cycle
const subscription = await stripe.subscriptions.update(subscriptionId, {
  items: [{
    id: subscription.items.data[0].id,
    price: newPriceId,
  }],
  proration_behavior: 'create_prorations', // or 'none'
});
```

### Cancel at Period End
```javascript
// User cancels but keeps access until period ends
await stripe.subscriptions.update(subscriptionId, {
  cancel_at_period_end: true,
});
```

## Checklist

- [ ] Customer is created/linked before checkout
- [ ] userId is in both session.metadata and subscription_data.metadata
- [ ] All subscription webhook events are handled
- [ ] Database has subscription status fields
- [ ] Customer Portal is configured
- [ ] Grace period logic for failed payments
- [ ] Email notifications for lifecycle events
