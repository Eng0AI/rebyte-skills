# Stripe Integration with Express.js

Express-specific patterns for Stripe integration.

## Project Setup

```bash
npm install express stripe dotenv
```

## Project Structure

```
├── server.js           # Main server file
├── routes/
│   ├── checkout.js     # Checkout routes
│   ├── payment.js      # PaymentIntent routes
│   └── webhook.js      # Webhook handler
├── middleware/
│   └── auth.js         # Authentication
├── services/
│   └── stripe.js       # Stripe client
├── public/
│   └── checkout.html   # Frontend
├── .env
└── package.json
```

## Stripe Client Setup

```javascript
// services/stripe.js
const Stripe = require('stripe');

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
});

module.exports = stripe;
```

## Server Configuration

```javascript
// server.js
require('dotenv').config();
const express = require('express');
const path = require('path');

const app = express();

// IMPORTANT: Webhook route must come BEFORE json middleware
// to preserve raw body for signature verification
app.use('/webhook', require('./routes/webhook'));

// JSON parsing for all other routes
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static files
app.use(express.static('public'));

// Routes
app.use('/api/checkout', require('./routes/checkout'));
app.use('/api/payment', require('./routes/payment'));

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## Checkout Routes

```javascript
// routes/checkout.js
const express = require('express');
const router = express.Router();
const stripe = require('../services/stripe');

// Create Checkout Session
router.post('/create-session', async (req, res) => {
  try {
    const { priceId, quantity = 1 } = req.body;

    // Validate price ID against whitelist
    const allowedPrices = {
      'price_basic': true,
      'price_pro': true,
    };

    if (!allowedPrices[priceId]) {
      return res.status(400).json({ error: 'Invalid price' });
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [
        {
          price: priceId,
          quantity,
        },
      ],
      success_url: `${process.env.DOMAIN}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.DOMAIN}/cancel.html`,
      metadata: {
        userId: req.user?.id, // If authenticated
      },
    });

    res.json({ url: session.url, sessionId: session.id });
  } catch (error) {
    console.error('Checkout session error:', error);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// Get session details (for success page)
router.get('/session/:sessionId', async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.retrieve(
      req.params.sessionId
    );

    res.json({
      status: session.payment_status,
      customerEmail: session.customer_details?.email,
      amountTotal: session.amount_total,
    });
  } catch (error) {
    console.error('Session retrieval error:', error);
    res.status(500).json({ error: 'Failed to retrieve session' });
  }
});

module.exports = router;
```

## PaymentIntent Routes

```javascript
// routes/payment.js
const express = require('express');
const router = express.Router();
const stripe = require('../services/stripe');

// Create PaymentIntent
router.post('/create-intent', async (req, res) => {
  try {
    const { productId } = req.body;

    // IMPORTANT: Get price from YOUR database, not client
    const product = await getProductFromDatabase(productId);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount: product.priceInCents,
      currency: 'usd',
      automatic_payment_methods: {
        enabled: true,
      },
      metadata: {
        productId,
        userId: req.user?.id,
      },
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
      amount: paymentIntent.amount,
    });
  } catch (error) {
    console.error('PaymentIntent error:', error);
    res.status(500).json({ error: 'Failed to create payment' });
  }
});

// Placeholder - replace with your database call
async function getProductFromDatabase(productId) {
  const products = {
    'prod_1': { id: 'prod_1', name: 'Basic', priceInCents: 999 },
    'prod_2': { id: 'prod_2', name: 'Pro', priceInCents: 1999 },
  };
  return products[productId];
}

module.exports = router;
```

## Webhook Handler

```javascript
// routes/webhook.js
const express = require('express');
const router = express.Router();
const stripe = require('../services/stripe');

// CRITICAL: Use raw body for webhook signature verification
router.post(
  '/',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];

    let event;

    try {
      event = stripe.webhooks.constructEvent(
        req.body,
        sig,
        process.env.STRIPE_WEBHOOK_SECRET
      );
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Handle events
    try {
      switch (event.type) {
        case 'checkout.session.completed':
          await handleCheckoutComplete(event.data.object);
          break;

        case 'payment_intent.succeeded':
          await handlePaymentSuccess(event.data.object);
          break;

        case 'payment_intent.payment_failed':
          await handlePaymentFailed(event.data.object);
          break;

        case 'customer.subscription.created':
        case 'customer.subscription.updated':
          await handleSubscriptionChange(event.data.object);
          break;

        case 'customer.subscription.deleted':
          await handleSubscriptionCanceled(event.data.object);
          break;

        case 'invoice.paid':
          await handleInvoicePaid(event.data.object);
          break;

        case 'invoice.payment_failed':
          await handleInvoiceFailed(event.data.object);
          break;

        default:
          console.log(`Unhandled event type: ${event.type}`);
      }

      res.json({ received: true });
    } catch (err) {
      console.error(`Error processing ${event.type}:`, err);
      // Still return 200 to prevent Stripe retries for processing errors
      // Log for manual investigation
      res.json({ received: true, error: 'Processing error' });
    }
  }
);

// Event handlers
async function handleCheckoutComplete(session) {
  console.log('Checkout completed:', session.id);

  // Idempotency check
  const existing = await findOrderBySessionId(session.id);
  if (existing) {
    console.log('Order already exists, skipping');
    return;
  }

  // Create order in your database
  await createOrder({
    stripeSessionId: session.id,
    customerEmail: session.customer_details?.email,
    amount: session.amount_total,
    status: 'completed',
    metadata: session.metadata,
  });

  // Send confirmation email, etc.
}

async function handlePaymentSuccess(paymentIntent) {
  console.log('Payment succeeded:', paymentIntent.id);
  // Fulfill the order
}

async function handlePaymentFailed(paymentIntent) {
  console.log('Payment failed:', paymentIntent.id);
  // Notify user, log for analysis
}

async function handleSubscriptionChange(subscription) {
  console.log('Subscription updated:', subscription.id);
  // Update user's subscription status in database
}

async function handleSubscriptionCanceled(subscription) {
  console.log('Subscription canceled:', subscription.id);
  // Revoke access
}

async function handleInvoicePaid(invoice) {
  console.log('Invoice paid:', invoice.id);
  // Extend subscription period
}

async function handleInvoiceFailed(invoice) {
  console.log('Invoice failed:', invoice.id);
  // Notify user about payment failure
}

// Placeholder functions - replace with your database calls
async function findOrderBySessionId(sessionId) {
  return null; // Implement
}

async function createOrder(orderData) {
  console.log('Creating order:', orderData);
  // Implement
}

module.exports = router;
```

## Frontend HTML

```html
<!-- public/checkout.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Checkout</title>
  <script src="https://js.stripe.com/v3/"></script>
</head>
<body>
  <h1>Checkout</h1>

  <!-- Option 1: Redirect to Stripe Checkout -->
  <button id="checkout-btn">Buy Now - $19.99</button>

  <!-- Option 2: Embedded Payment Form -->
  <div id="payment-form-container" style="display: none;">
    <form id="payment-form">
      <div id="payment-element"></div>
      <button type="submit" id="submit-btn">Pay</button>
      <div id="error-message"></div>
    </form>
  </div>

  <script>
    const stripe = Stripe('pk_test_xxx');

    // Option 1: Checkout redirect
    document.getElementById('checkout-btn').addEventListener('click', async () => {
      const response = await fetch('/api/checkout/create-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId: 'price_xxx' }),
      });

      const { url } = await response.json();
      window.location.href = url;
    });

    // Option 2: Embedded payment form
    async function initPaymentForm() {
      const response = await fetch('/api/payment/create-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId: 'prod_1' }),
      });

      const { clientSecret } = await response.json();

      const elements = stripe.elements({ clientSecret });
      const paymentElement = elements.create('payment');
      paymentElement.mount('#payment-element');

      document.getElementById('payment-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const { error } = await stripe.confirmPayment({
          elements,
          confirmParams: {
            return_url: window.location.origin + '/success.html',
          },
        });

        if (error) {
          document.getElementById('error-message').textContent = error.message;
        }
      });

      document.getElementById('payment-form-container').style.display = 'block';
    }

    // Uncomment to use embedded form instead
    // initPaymentForm();
  </script>
</body>
</html>
```

## Subscription Management

```javascript
// routes/subscription.js
const express = require('express');
const router = express.Router();
const stripe = require('../services/stripe');

// Create subscription checkout
router.post('/create', async (req, res) => {
  try {
    const { priceId } = req.body;
    const user = req.user;

    // Get or create Stripe customer
    let customerId = user.stripeCustomerId;
    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: { userId: user.id },
      });
      customerId = customer.id;
      await updateUserStripeCustomerId(user.id, customerId);
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.DOMAIN}/subscription/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.DOMAIN}/pricing`,
    });

    res.json({ url: session.url });
  } catch (error) {
    console.error('Subscription creation error:', error);
    res.status(500).json({ error: 'Failed to create subscription' });
  }
});

// Customer portal for managing subscription
router.post('/portal', async (req, res) => {
  try {
    const user = req.user;

    if (!user.stripeCustomerId) {
      return res.status(400).json({ error: 'No subscription found' });
    }

    const session = await stripe.billingPortal.sessions.create({
      customer: user.stripeCustomerId,
      return_url: `${process.env.DOMAIN}/account`,
    });

    res.json({ url: session.url });
  } catch (error) {
    console.error('Portal session error:', error);
    res.status(500).json({ error: 'Failed to create portal session' });
  }
});

module.exports = router;
```

## Error Handling Middleware

```javascript
// middleware/stripe-errors.js
function handleStripeErrors(err, req, res, next) {
  if (err.type && err.type.startsWith('Stripe')) {
    console.error('Stripe error:', {
      type: err.type,
      code: err.code,
      message: err.message,
      requestId: err.requestId,
    });

    switch (err.type) {
      case 'StripeCardError':
        return res.status(400).json({
          error: err.message, // Safe to show to user
        });

      case 'StripeInvalidRequestError':
        return res.status(400).json({
          error: 'Invalid request',
        });

      default:
        return res.status(500).json({
          error: 'Payment processing error',
        });
    }
  }

  next(err);
}

module.exports = handleStripeErrors;
```

## Environment Variables

```bash
# .env
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
DOMAIN=http://localhost:3000
PORT=3000
```

## Checklist

- [ ] Webhook route registered BEFORE `express.json()` middleware
- [ ] Webhook uses `express.raw({ type: 'application/json' })`
- [ ] Prices/products validated against whitelist
- [ ] Amounts come from database, not client
- [ ] Error handling middleware in place
- [ ] Customer ID stored in your database
- [ ] Idempotency checks in webhook handlers
