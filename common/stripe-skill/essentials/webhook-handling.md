# Webhook Handling Best Practices

Webhooks are how Stripe tells you about events (payments, subscriptions, etc.). Getting this right is critical.

## Why Webhooks Matter

- User can close browser before redirect completes
- Network can fail between Stripe and your success page
- Some events have no user interaction (subscription renewals)
- Webhooks are the **source of truth** for payment status

## Core Principles

### 1. Always Verify Signatures

```javascript
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

app.post('/webhook',
  express.raw({ type: 'application/json' }), // MUST be raw body
  async (req, res) => {
    const sig = req.headers['stripe-signature'];

    let event;
    try {
      event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message);
      return res.status(400).send(`Webhook Error: ${err.message}`);
    }

    // Event is verified, safe to process
    await handleEvent(event);
    res.status(200).json({ received: true });
  }
);
```

**Common Mistake**: Using `express.json()` middleware globally breaks signature verification.

```javascript
// WRONG - This breaks webhooks
app.use(express.json());

// CORRECT - Exclude webhook route from JSON parsing
app.use((req, res, next) => {
  if (req.originalUrl === '/webhook') {
    next();
  } else {
    express.json()(req, res, next);
  }
});
```

### 2. Return 2xx Immediately

Stripe expects a response within 20 seconds. Process asynchronously:

```javascript
// WRONG - May timeout
app.post('/webhook', async (req, res) => {
  const event = verifyEvent(req);

  await sendEmail(event);              // 2-5 seconds
  await updateDatabase(event);         // 1-2 seconds
  await callExternalAPI(event);        // 3-10 seconds
  await generatePDF(event);            // 5+ seconds
  // Total: 11-22+ seconds = TIMEOUT RISK

  res.status(200).send();
});

// CORRECT - Respond fast, process later
app.post('/webhook', async (req, res) => {
  const event = verifyEvent(req);

  // Quick: save to queue or database
  await queue.add('stripe-webhook', event);

  // Respond immediately
  res.status(200).json({ received: true });
});

// Process in background worker
queue.process('stripe-webhook', async (job) => {
  const event = job.data;
  await sendEmail(event);
  await updateDatabase(event);
  // ... take as long as needed
});
```

### 3. Handle Idempotency

Stripe may send the same event multiple times:

```javascript
async function handleEvent(event) {
  // Check if we've already processed this event
  const processed = await db.webhookEvents.findById(event.id);
  if (processed) {
    console.log(`Event ${event.id} already processed, skipping`);
    return;
  }

  // Process the event
  await processEvent(event);

  // Mark as processed
  await db.webhookEvents.create({
    id: event.id,
    type: event.type,
    processedAt: new Date(),
  });
}
```

### 4. Handle Events in Correct Order

Events may arrive out of order. Use timestamps:

```javascript
async function handleSubscriptionUpdate(subscription) {
  const existing = await db.subscriptions.findByStripeId(subscription.id);

  // Only update if this event is newer
  if (existing && existing.stripeUpdatedAt >= subscription.created) {
    console.log('Received older event, skipping');
    return;
  }

  await db.subscriptions.update({
    stripeId: subscription.id,
    status: subscription.status,
    stripeUpdatedAt: subscription.created,
  });
}
```

## Essential Events by Use Case

### One-Time Payments
```javascript
switch (event.type) {
  case 'checkout.session.completed':
    // Payment successful via Checkout
    break;
  case 'payment_intent.succeeded':
    // Payment successful via PaymentIntent
    break;
  case 'payment_intent.payment_failed':
    // Payment failed
    break;
}
```

### Subscriptions
```javascript
switch (event.type) {
  case 'customer.subscription.created':
    // New subscription started
    break;
  case 'customer.subscription.updated':
    // Subscription changed (plan, status, etc.)
    break;
  case 'customer.subscription.deleted':
    // Subscription canceled
    break;
  case 'invoice.paid':
    // Successful recurring payment
    break;
  case 'invoice.payment_failed':
    // Failed recurring payment (will retry)
    break;
  case 'invoice.payment_action_required':
    // Needs customer action (3D Secure)
    break;
}
```

### Refunds
```javascript
switch (event.type) {
  case 'charge.refunded':
    // Full or partial refund issued
    break;
  case 'charge.refund.updated':
    // Refund status changed
    break;
}
```

## Local Development with Stripe CLI

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/webhook

# In another terminal, trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

The CLI gives you a webhook signing secret starting with `whsec_...` - use this locally.

## Production Setup

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your URL: `https://yourdomain.com/webhook`
4. Select events to listen for
5. Copy the signing secret to your environment variables

## Error Handling Strategy

```javascript
app.post('/webhook', async (req, res) => {
  let event;

  try {
    event = stripe.webhooks.constructEvent(/*...*/);
  } catch (err) {
    // Signature verification failed - reject
    return res.status(400).send('Invalid signature');
  }

  try {
    await handleEvent(event);
    res.status(200).json({ received: true });
  } catch (err) {
    // Processing failed - log but return 200
    // (otherwise Stripe will retry and we'll fail again)
    console.error(`Error processing ${event.type}:`, err);

    // Save for manual review
    await db.failedWebhooks.create({
      eventId: event.id,
      eventType: event.type,
      error: err.message,
      payload: event.data.object,
    });

    // Still return 200 - we received the event
    // Fix the bug and reprocess manually
    res.status(200).json({ received: true, error: 'Processing failed' });
  }
});
```

## Retry Behavior

Stripe retries failed webhooks (non-2xx response) with exponential backoff:
- Immediately
- 5 minutes
- 30 minutes
- 2 hours
- 5 hours
- 10 hours
- 10 hours (continues for up to 3 days)

After 3 days, the event is marked as failed in your Dashboard.

## Checklist

- [ ] Webhook endpoint uses raw body (not parsed JSON)
- [ ] Signature is verified before processing
- [ ] Response is returned within 20 seconds
- [ ] Events are deduplicated by event.id
- [ ] Failed processing doesn't return non-2xx (prevents infinite retries)
- [ ] Stripe CLI used for local testing
- [ ] All relevant events are subscribed in Dashboard
- [ ] Webhook signing secret is in environment variables
- [ ] Error handling saves failures for manual review
