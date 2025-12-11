# Stripe Connect - Multi-Party Payments

Handle payments between multiple parties: platforms, marketplaces, and vendors.

## When to Use

- Marketplace (buyers pay sellers, platform takes fee)
- Platform with service providers (Uber, DoorDash model)
- SaaS with sub-accounts
- Any scenario where money flows to multiple parties

## Connect Account Types

| Type | Control | Onboarding | Use Case |
|------|---------|------------|----------|
| **Standard** | Low | Stripe-hosted | Established businesses, minimal platform control |
| **Express** | Medium | Stripe-hosted | Gig workers, freelancers |
| **Custom** | High | You build it | Full white-label, complex requirements |

**Recommendation**: Start with Express unless you have specific needs.

## Architecture (Express Accounts)

```
Buyer → Pay on your platform → Platform's Stripe →
Split: Platform fee + Vendor payout →
Vendor receives funds in their Stripe account
```

## Implementation

### Step 1: Create Connected Account

```javascript
app.post('/create-connected-account', async (req, res) => {
  const { vendorId, email } = req.body;

  // Create Express account
  const account = await stripe.accounts.create({
    type: 'express',
    email,
    capabilities: {
      card_payments: { requested: true },
      transfers: { requested: true },
    },
    metadata: {
      vendorId,
    },
  });

  // Save to your database
  await db.vendors.update(vendorId, {
    stripeAccountId: account.id,
  });

  res.json({ accountId: account.id });
});
```

### Step 2: Onboarding Link

```javascript
app.post('/create-onboarding-link', async (req, res) => {
  const vendor = await db.vendors.findById(req.body.vendorId);

  const accountLink = await stripe.accountLinks.create({
    account: vendor.stripeAccountId,
    refresh_url: `${process.env.DOMAIN}/vendor/onboarding/refresh`,
    return_url: `${process.env.DOMAIN}/vendor/onboarding/complete`,
    type: 'account_onboarding',
  });

  res.json({ url: accountLink.url });
});
```

### Step 3: Check Onboarding Status

```javascript
app.get('/vendor/onboarding/complete', async (req, res) => {
  const vendor = req.user.vendor;

  const account = await stripe.accounts.retrieve(vendor.stripeAccountId);

  if (account.charges_enabled && account.payouts_enabled) {
    await db.vendors.update(vendor.id, {
      stripeOnboardingComplete: true,
    });
    res.redirect('/vendor/dashboard');
  } else {
    // Onboarding incomplete, generate new link
    res.redirect('/vendor/onboarding/continue');
  }
});
```

### Step 4: Payment with Platform Fee

#### Option A: Direct Charges (Charge on connected account)

```javascript
// Customer pays vendor directly, platform takes fee
app.post('/create-payment-intent', async (req, res) => {
  const { productId } = req.body;
  const product = await db.products.findById(productId);
  const vendor = await db.vendors.findById(product.vendorId);

  const platformFee = Math.round(product.priceInCents * 0.10); // 10% fee

  const paymentIntent = await stripe.paymentIntents.create({
    amount: product.priceInCents,
    currency: 'usd',
    application_fee_amount: platformFee,
    transfer_data: {
      destination: vendor.stripeAccountId,
    },
    metadata: {
      productId,
      vendorId: vendor.id,
    },
  }, {
    stripeAccount: vendor.stripeAccountId, // Charge appears on vendor's account
  });

  res.json({ clientSecret: paymentIntent.client_secret });
});
```

#### Option B: Destination Charges (Charge on platform, transfer to vendor)

```javascript
// Charge on platform account, automatically transfer to vendor
const paymentIntent = await stripe.paymentIntents.create({
  amount: product.priceInCents,
  currency: 'usd',
  application_fee_amount: platformFee,
  transfer_data: {
    destination: vendor.stripeAccountId,
  },
  metadata: {
    productId,
    vendorId: vendor.id,
  },
});
// Note: No stripeAccount header - charges on YOUR account
```

#### Option C: Separate Charges and Transfers

```javascript
// Most flexible: charge customer, transfer later
const paymentIntent = await stripe.paymentIntents.create({
  amount: product.priceInCents,
  currency: 'usd',
  metadata: { orderId },
});

// After payment succeeds, create transfer
app.post('/webhook', async (req, res) => {
  const event = verifyWebhook(req);

  if (event.type === 'payment_intent.succeeded') {
    const pi = event.data.object;
    const order = await db.orders.findByPaymentIntentId(pi.id);

    const vendorAmount = order.amount - order.platformFee;

    await stripe.transfers.create({
      amount: vendorAmount,
      currency: 'usd',
      destination: order.vendor.stripeAccountId,
      transfer_group: order.id,
    });
  }
});
```

### Step 5: Checkout Session with Connect

```javascript
const session = await stripe.checkout.sessions.create({
  mode: 'payment',
  line_items: [{
    price_data: {
      currency: 'usd',
      unit_amount: product.priceInCents,
      product_data: {
        name: product.name,
      },
    },
    quantity: 1,
  }],
  payment_intent_data: {
    application_fee_amount: platformFee,
    transfer_data: {
      destination: vendor.stripeAccountId,
    },
  },
  success_url: `${process.env.DOMAIN}/success`,
  cancel_url: `${process.env.DOMAIN}/cancel`,
});
```

### Step 6: Vendor Dashboard (Express Dashboard)

```javascript
app.post('/create-dashboard-link', async (req, res) => {
  const vendor = req.user.vendor;

  const loginLink = await stripe.accounts.createLoginLink(
    vendor.stripeAccountId
  );

  res.json({ url: loginLink.url });
});
```

## Webhook Events for Connect

```javascript
app.post('/webhook', async (req, res) => {
  const event = verifyWebhook(req);

  switch (event.type) {
    // Account updates
    case 'account.updated': {
      const account = event.data.object;
      await handleAccountUpdated(account);
      break;
    }

    // Payout events
    case 'payout.paid': {
      const payout = event.data.object;
      // Vendor received their money
      break;
    }

    case 'payout.failed': {
      const payout = event.data.object;
      // Payout to vendor failed
      break;
    }
  }

  res.status(200).json({ received: true });
});

async function handleAccountUpdated(account) {
  const vendor = await db.vendors.findByStripeAccountId(account.id);

  await db.vendors.update(vendor.id, {
    chargesEnabled: account.charges_enabled,
    payoutsEnabled: account.payouts_enabled,
    detailsSubmitted: account.details_submitted,
  });
}
```

## Fee Structures

### Percentage Fee
```javascript
const platformFee = Math.round(amount * 0.10); // 10%
```

### Fixed + Percentage
```javascript
const platformFee = Math.round(amount * 0.05) + 30; // 5% + $0.30
```

### Tiered Fee
```javascript
function calculateFee(vendorTier, amount) {
  const rates = {
    basic: 0.15,    // 15%
    pro: 0.10,      // 10%
    enterprise: 0.05, // 5%
  };
  return Math.round(amount * rates[vendorTier]);
}
```

## Money Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer pays $100                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Platform's Stripe Account                  │
│                                                              │
│   Stripe fee: $3.20 (2.9% + $0.30)                          │
│   Platform fee: $10.00 (10%)                                │
│   ─────────────────────────────                             │
│   Available for transfer: $86.80                            │
│                                                              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Vendor's Stripe Account                     │
│                                                              │
│   Receives: $86.80                                          │
│   (Vendor sees this in their Express dashboard)             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Checklist

- [ ] Correct account type selected (Express recommended)
- [ ] Onboarding flow handles incomplete accounts
- [ ] `charges_enabled` checked before accepting payments
- [ ] Platform fee calculated correctly
- [ ] `transfer_data.destination` set correctly
- [ ] Connect webhooks registered for account events
- [ ] Refund handling considers who gets refunded
- [ ] Dashboard link available for vendors
