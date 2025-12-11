# Idempotency in Stripe Integrations

Idempotency ensures operations happen exactly once, even if requests are retried.

## Why Idempotency Matters

Without idempotency:
- Network timeout → retry → customer charged twice
- Webhook delivered twice → order fulfilled twice
- User double-clicks → two payments created

## Two Levels of Idempotency

### 1. Stripe API Idempotency Keys

For API requests to Stripe:

```javascript
const paymentIntent = await stripe.paymentIntents.create(
  {
    amount: 1999,
    currency: 'usd',
  },
  {
    idempotencyKey: 'unique_key_for_this_operation',
  }
);
```

- Same key + same parameters = same result returned
- Keys expire after 24 hours
- Different parameters with same key = error

### 2. Application-Level Idempotency

For your own business logic (webhooks, fulfillment):

```javascript
async function fulfillOrder(paymentIntentId) {
  // Check if already fulfilled
  const existing = await db.orders.findByPaymentIntentId(paymentIntentId);
  if (existing && existing.status === 'fulfilled') {
    console.log('Order already fulfilled, skipping');
    return existing;
  }

  // Fulfill the order
  const order = await createAndFulfillOrder(paymentIntentId);
  return order;
}
```

## Idempotency Key Strategies

### Strategy 1: Order-Based Key

Best for checkout flows:

```javascript
app.post('/create-payment-intent', async (req, res) => {
  const { orderId } = req.body;

  const paymentIntent = await stripe.paymentIntents.create(
    {
      amount: order.total,
      currency: 'usd',
      metadata: { orderId },
    },
    {
      idempotencyKey: `order_${orderId}_payment`,
    }
  );

  res.json({ clientSecret: paymentIntent.client_secret });
});
```

### Strategy 2: User + Action + Timestamp Bucket

For actions that can be repeated but not rapidly:

```javascript
function getIdempotencyKey(userId, action) {
  // Bucket to 10-minute windows
  const timeBucket = Math.floor(Date.now() / (10 * 60 * 1000));
  return `${userId}_${action}_${timeBucket}`;
}

// User can retry within 10 minutes safely
const key = getIdempotencyKey(user.id, 'subscribe_pro');
```

### Strategy 3: Hash of Request Parameters

For variable requests:

```javascript
const crypto = require('crypto');

function createIdempotencyKey(params) {
  const normalized = JSON.stringify(params, Object.keys(params).sort());
  return crypto.createHash('sha256').update(normalized).digest('hex');
}

const key = createIdempotencyKey({
  userId: user.id,
  productId: product.id,
  quantity: 1,
});
```

## Webhook Idempotency

### Using Event ID

```javascript
app.post('/webhook', async (req, res) => {
  const event = verifyWebhook(req);

  // Use Stripe's event ID as idempotency key
  const processed = await db.processedEvents.findById(event.id);
  if (processed) {
    return res.status(200).json({ received: true, duplicate: true });
  }

  // Process event
  await handleEvent(event);

  // Mark as processed
  await db.processedEvents.create({
    id: event.id,
    type: event.type,
    processedAt: new Date(),
  });

  res.status(200).json({ received: true });
});
```

### With Transaction

```javascript
async function handlePaymentSucceeded(paymentIntent) {
  const txn = await db.transaction();

  try {
    // Check and mark as processed in single transaction
    const [processed] = await txn.query(
      `INSERT INTO processed_payments (payment_intent_id, processed_at)
       VALUES ($1, NOW())
       ON CONFLICT (payment_intent_id) DO NOTHING
       RETURNING *`,
      [paymentIntent.id]
    );

    if (!processed) {
      // Already processed by another request
      await txn.rollback();
      return;
    }

    // Create order
    await txn.query(
      `INSERT INTO orders (payment_intent_id, amount, status)
       VALUES ($1, $2, 'completed')`,
      [paymentIntent.id, paymentIntent.amount]
    );

    await txn.commit();
  } catch (error) {
    await txn.rollback();
    throw error;
  }
}
```

## Database Schema for Idempotency

```sql
-- For webhook event tracking
CREATE TABLE processed_events (
  id VARCHAR(255) PRIMARY KEY,  -- Stripe event ID
  type VARCHAR(100) NOT NULL,
  processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- For payment tracking
CREATE TABLE processed_payments (
  payment_intent_id VARCHAR(255) PRIMARY KEY,
  processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Add index for cleanup
CREATE INDEX idx_processed_events_processed_at ON processed_events(processed_at);
```

### Cleanup Old Records

```javascript
// Run daily to clean up old idempotency records
async function cleanupOldRecords() {
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  await db.query(
    'DELETE FROM processed_events WHERE processed_at < $1',
    [thirtyDaysAgo]
  );
}
```

## Common Pitfalls

### Pitfall 1: Non-Deterministic Keys

```javascript
// WRONG - Different key each time
const key = `payment_${Date.now()}`;

// CORRECT - Same key for same operation
const key = `order_${orderId}_payment`;
```

### Pitfall 2: Checking After Side Effects

```javascript
// WRONG - Email sent before idempotency check
async function handlePayment(pi) {
  await sendEmail(user, 'Payment received!');  // Sent every time!

  const existing = await db.orders.findByPI(pi.id);
  if (existing) return;

  await db.orders.create({ paymentIntentId: pi.id });
}

// CORRECT - Check first
async function handlePayment(pi) {
  const existing = await db.orders.findByPI(pi.id);
  if (existing) return;

  await db.orders.create({ paymentIntentId: pi.id });
  await sendEmail(user, 'Payment received!');  // Only sent once
}
```

### Pitfall 3: Race Conditions

```javascript
// WRONG - Race condition between check and insert
async function handlePayment(pi) {
  const existing = await db.orders.findByPI(pi.id);
  if (existing) return;
  // Another request could insert here!
  await db.orders.create({ paymentIntentId: pi.id });
}

// CORRECT - Use unique constraint or transaction
async function handlePayment(pi) {
  try {
    await db.orders.create({
      paymentIntentId: pi.id,  // Has UNIQUE constraint
      // ...
    });
  } catch (error) {
    if (error.code === '23505') {  // Unique violation
      return; // Already processed
    }
    throw error;
  }
}
```

## Testing Idempotency

```javascript
describe('Payment idempotency', () => {
  it('should not create duplicate orders', async () => {
    const paymentIntent = { id: 'pi_test_123', amount: 1999 };

    // Process twice
    await handlePaymentSucceeded(paymentIntent);
    await handlePaymentSucceeded(paymentIntent);

    // Should only have one order
    const orders = await db.orders.findByPaymentIntentId(paymentIntent.id);
    expect(orders.length).toBe(1);
  });

  it('should return same PaymentIntent for same order', async () => {
    const pi1 = await createPaymentForOrder('order_123');
    const pi2 = await createPaymentForOrder('order_123');

    expect(pi1.id).toBe(pi2.id);
  });
});
```

## Checklist

- [ ] Stripe API calls use idempotency keys for mutations
- [ ] Idempotency keys are deterministic (same input = same key)
- [ ] Webhook handlers check event.id before processing
- [ ] Database has unique constraints on Stripe IDs
- [ ] Side effects (email, fulfillment) happen after idempotency check
- [ ] Race conditions handled with transactions or constraints
- [ ] Old idempotency records cleaned up periodically
