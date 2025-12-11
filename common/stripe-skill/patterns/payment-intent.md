# Custom Payment Flow with PaymentIntent

Full control over the payment UI and flow. More work, but maximum flexibility.

## When to Use

- Custom payment form design required
- Need to collect payment method for future use
- Complex checkout flows (multi-step, custom validation)
- Stripe Checkout doesn't fit your UX needs

## Architecture

```
Your form collects card → Create PaymentIntent on server →
Return client_secret → Confirm payment with Stripe.js →
Handle result → Webhook confirms final status
```

## Implementation

### Step 1: Server - Create PaymentIntent

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

app.post('/create-payment-intent', async (req, res) => {
  const { productId, quantity = 1 } = req.body;

  // IMPORTANT: Get price from YOUR database, not from client
  const product = await db.products.findById(productId);
  if (!product) {
    return res.status(404).json({ error: 'Product not found' });
  }

  const amount = product.priceInCents * quantity;

  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: 'usd',
      // Recommended: enable automatic payment methods
      automatic_payment_methods: {
        enabled: true,
      },
      metadata: {
        productId,
        quantity: String(quantity),
        userId: req.user?.id,
      },
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
      amount,
    });
  } catch (error) {
    console.error('PaymentIntent creation failed:', error);
    res.status(500).json({ error: 'Payment initialization failed' });
  }
});
```

### Step 2: Frontend - Payment Form

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://js.stripe.com/v3/"></script>
</head>
<body>
  <form id="payment-form">
    <div id="payment-element"></div>
    <button id="submit-button" type="submit">Pay</button>
    <div id="error-message"></div>
  </form>

  <script>
    const stripe = Stripe('pk_test_xxx');
    let elements;

    initialize();

    async function initialize() {
      // Create PaymentIntent on your server
      const response = await fetch('/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId: 'prod_123' }),
      });
      const { clientSecret, amount } = await response.json();

      // Create Payment Element
      elements = stripe.elements({ clientSecret });
      const paymentElement = elements.create('payment');
      paymentElement.mount('#payment-element');
    }

    // Handle form submission
    document.getElementById('payment-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      setLoading(true);

      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment-complete`,
        },
      });

      // This point is only reached if there's an immediate error
      // (e.g., invalid card). Otherwise, user is redirected to return_url.
      if (error) {
        showError(error.message);
      }

      setLoading(false);
    });

    function setLoading(isLoading) {
      document.getElementById('submit-button').disabled = isLoading;
    }

    function showError(message) {
      document.getElementById('error-message').textContent = message;
    }
  </script>
</body>
</html>
```

### Step 3: Handle Return URL

```javascript
// payment-complete page
app.get('/payment-complete', async (req, res) => {
  const { payment_intent, payment_intent_client_secret } = req.query;

  if (!payment_intent) {
    return res.redirect('/');
  }

  // Retrieve the PaymentIntent to check status
  const paymentIntent = await stripe.paymentIntents.retrieve(payment_intent);

  switch (paymentIntent.status) {
    case 'succeeded':
      res.render('success', { paymentIntent });
      break;
    case 'processing':
      res.render('processing', { message: 'Payment is processing...' });
      break;
    case 'requires_payment_method':
      res.redirect('/checkout?error=payment_failed');
      break;
    default:
      res.redirect('/checkout?error=unknown');
  }
});
```

### Step 4: Webhook Handler

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
    case 'payment_intent.succeeded': {
      const paymentIntent = event.data.object;
      await handlePaymentSuccess(paymentIntent);
      break;
    }

    case 'payment_intent.payment_failed': {
      const paymentIntent = event.data.object;
      await handlePaymentFailure(paymentIntent);
      break;
    }
  }

  res.status(200).json({ received: true });
});

async function handlePaymentSuccess(paymentIntent) {
  const { productId, quantity, userId } = paymentIntent.metadata;

  // Idempotency check
  const existing = await db.orders.findByPaymentIntentId(paymentIntent.id);
  if (existing) return;

  // Create order
  await db.orders.create({
    paymentIntentId: paymentIntent.id,
    userId,
    productId,
    quantity: parseInt(quantity),
    amount: paymentIntent.amount,
    status: 'completed',
  });

  // Fulfill order
  await fulfillOrder(paymentIntent);
}

async function handlePaymentFailure(paymentIntent) {
  console.log('Payment failed:', paymentIntent.id);
  // Log for monitoring, maybe notify user
}
```

## PaymentIntent States

```
                    ┌─────────────────────┐
                    │   requires_payment  │
                    │      _method        │
                    └──────────┬──────────┘
                               │ User enters card
                    ┌──────────▼──────────┐
                    │   requires_        │
                    │   confirmation     │
                    └──────────┬──────────┘
                               │ confirmPayment()
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐       │       ┌───────▼───────┐
     │   requires_     │       │       │    failed     │
     │   action        │       │       │               │
     │ (3D Secure)     │       │       └───────────────┘
     └────────┬────────┘       │
              │                │
              └────────┬───────┘
                       │
              ┌────────▼────────┐
              │   processing    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   succeeded     │
              └─────────────────┘
```

## Advanced Patterns

### Save Card for Future Use

```javascript
// Server: Create PaymentIntent with setup_future_usage
const paymentIntent = await stripe.paymentIntents.create({
  amount: 1999,
  currency: 'usd',
  customer: customerId, // Must have a customer
  setup_future_usage: 'off_session', // Save for future charges
});

// Later: Charge saved card
const paymentIntent = await stripe.paymentIntents.create({
  amount: 999,
  currency: 'usd',
  customer: customerId,
  payment_method: savedPaymentMethodId,
  off_session: true,
  confirm: true,
});
```

### Manual Capture (Auth then Capture)

```javascript
// Step 1: Authorize only
const paymentIntent = await stripe.paymentIntents.create({
  amount: 1999,
  currency: 'usd',
  capture_method: 'manual', // Don't capture yet
});

// Step 2: Later, capture the funds
await stripe.paymentIntents.capture(paymentIntent.id);
```

### Partial Capture

```javascript
// Authorize $100, capture only $75
await stripe.paymentIntents.capture(paymentIntent.id, {
  amount_to_capture: 7500, // Only capture $75
});
```

## Error Handling

```javascript
try {
  const paymentIntent = await stripe.paymentIntents.create({...});
} catch (error) {
  switch (error.type) {
    case 'StripeCardError':
      // Card was declined
      console.log('Card declined:', error.message);
      break;
    case 'StripeRateLimitError':
      // Too many requests
      break;
    case 'StripeInvalidRequestError':
      // Invalid parameters
      break;
    case 'StripeAPIError':
      // Stripe API issue
      break;
    case 'StripeConnectionError':
      // Network issue
      break;
    case 'StripeAuthenticationError':
      // Invalid API key
      break;
    default:
      // Unknown error
      break;
  }
}
```

## Checklist

- [ ] PaymentIntent created server-side with amount from database
- [ ] client_secret sent to frontend (never full PaymentIntent)
- [ ] Payment Element or Card Element used (never raw card data)
- [ ] return_url handles all possible statuses
- [ ] Webhook handles payment_intent.succeeded
- [ ] Idempotency check in webhook handler
- [ ] Error handling for all Stripe error types
