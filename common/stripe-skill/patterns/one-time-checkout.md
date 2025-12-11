# One-Time Payment with Stripe Checkout

The simplest integration pattern. Stripe hosts the payment page - you just redirect users there.

## When to Use

- Selling products or services with fixed prices
- You want minimal frontend work
- PCI compliance is a concern (Stripe handles card data)

## Architecture

```
User clicks "Buy" → Your server creates Checkout Session → Redirect to Stripe →
Stripe handles payment → Redirect back to your success page → Webhook confirms payment
```

## Implementation

### Step 1: Create Product and Price in Stripe

Option A: Via Dashboard
1. Go to https://dashboard.stripe.com/products
2. Click "Add product"
3. Set name, description, and one-time price
4. Copy the Price ID (starts with `price_`)

Option B: Via API
```javascript
// Create product
const product = await stripe.products.create({
  name: 'My Product',
  description: 'Product description',
});

// Create price
const price = await stripe.prices.create({
  product: product.id,
  unit_amount: 1999, // $19.99 in cents
  currency: 'usd',
});

console.log('Price ID:', price.id); // Save this
```

### Step 2: Server Endpoint

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

app.post('/create-checkout-session', async (req, res) => {
  const { priceId } = req.body;

  // Validate priceId against your allowed prices
  const allowedPrices = ['price_xxx', 'price_yyy'];
  if (!allowedPrices.includes(priceId)) {
    return res.status(400).json({ error: 'Invalid price' });
  }

  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    success_url: `${process.env.DOMAIN}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.DOMAIN}/canceled`,
    // Optional: collect customer email
    // customer_email: req.user.email,
    // Optional: attach metadata
    metadata: {
      userId: req.user?.id,
      orderId: generateOrderId(),
    },
  });

  // Option 1: Redirect server-side
  res.redirect(303, session.url);

  // Option 2: Return URL for client-side redirect
  // res.json({ url: session.url });
});
```

### Step 3: Frontend Button

```html
<form action="/create-checkout-session" method="POST">
  <input type="hidden" name="priceId" value="price_xxx" />
  <button type="submit">Buy Now - $19.99</button>
</form>
```

Or with JavaScript:
```javascript
async function handleBuy() {
  const response = await fetch('/create-checkout-session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priceId: 'price_xxx' }),
  });
  const { url } = await response.json();
  window.location.href = url;
}
```

### Step 4: Success Page

```javascript
// Server: Verify the session on success page load
app.get('/success', async (req, res) => {
  const { session_id } = req.query;

  if (!session_id) {
    return res.redirect('/');
  }

  const session = await stripe.checkout.sessions.retrieve(session_id);

  // Verify payment was successful
  if (session.payment_status !== 'paid') {
    return res.redirect('/payment-failed');
  }

  // Show success page with order details
  res.render('success', {
    customerEmail: session.customer_details.email,
    amountTotal: session.amount_total / 100,
  });
});
```

### Step 5: Webhook Handler

**IMPORTANT**: Don't rely only on the success page redirect. Users can close the browser, network can fail. Always use webhooks for fulfillment.

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
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the checkout.session.completed event
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;

    // Check idempotency
    const existing = await db.orders.findByStripeSessionId(session.id);
    if (existing) {
      return res.status(200).json({ received: true });
    }

    // Fulfill the order
    await fulfillOrder(session);
  }

  res.status(200).json({ received: true });
});

async function fulfillOrder(session) {
  // 1. Save order to database
  await db.orders.create({
    stripeSessionId: session.id,
    customerEmail: session.customer_details.email,
    amountTotal: session.amount_total,
    metadata: session.metadata,
    status: 'completed',
  });

  // 2. Send confirmation email
  await sendOrderConfirmationEmail(session.customer_details.email);

  // 3. Grant access / ship product / etc.
  if (session.metadata.userId) {
    await grantProductAccess(session.metadata.userId);
  }
}
```

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
DOMAIN=http://localhost:3000
```

## Common Customizations

### Add Customer Email Collection
```javascript
const session = await stripe.checkout.sessions.create({
  // ...
  customer_email: req.user?.email, // Pre-fill if known
  // OR let Stripe collect it:
  // customer_creation: 'always',
});
```

### Add Shipping Address
```javascript
const session = await stripe.checkout.sessions.create({
  // ...
  shipping_address_collection: {
    allowed_countries: ['US', 'CA', 'GB'],
  },
});
```

### Add Tax Calculation
```javascript
const session = await stripe.checkout.sessions.create({
  // ...
  automatic_tax: { enabled: true },
});
```

### Add Discount Codes
```javascript
const session = await stripe.checkout.sessions.create({
  // ...
  allow_promotion_codes: true,
  // OR apply a specific coupon:
  // discounts: [{ coupon: 'SAVE20' }],
});
```

## Checklist

- [ ] Price ID is validated on server (don't trust client)
- [ ] Webhook endpoint is set up
- [ ] Webhook signature is verified
- [ ] Order fulfillment is idempotent
- [ ] Success page verifies session status
- [ ] Metadata includes userId/orderId for tracking
