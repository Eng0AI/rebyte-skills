---
name: build-and-deploy
description: Build and deploy this Stripe One-Time Payment application. Use when building, deploying, or preparing the project for production.
---

# Build and Deploy Stripe One-Time Payment

This is an Express.js backend application. Deploying to serverless platforms (Vercel/Netlify) requires creating API wrapper files.

## Tech Stack

- **Backend**: Express.js
- **Payments**: Stripe Checkout
- **Language**: JavaScript
- **Package Manager**: npm
- **Port**: 4242

## Environment Variables

**Required:**
- `STRIPE_SECRET_KEY` - Your Stripe secret key (sk_test_xxx or sk_live_xxx)
- `STRIPE_PUBLISHABLE_KEY` - Your Stripe publishable key (pk_test_xxx or pk_live_xxx)

**Optional (auto-created if not set):**
- `PRICE` - Price ID from Stripe Dashboard. If not set, a $20 sample product will be auto-created.
- `DOMAIN` - Your production domain (auto-detected if not set)

## Deploy to Vercel

### Step 1: Create Serverless API Wrapper

Create `api/index.js`:

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-11-20.acacia',
});

let PRICE_ID = process.env.PRICE;
let initialized = false;

async function ensureProductAndPrice() {
  if (initialized && PRICE_ID) return PRICE_ID;
  if (PRICE_ID) { initialized = true; return PRICE_ID; }

  const existingProducts = await stripe.products.list({ limit: 10 });
  let product = existingProducts.data.find(p => p.metadata?.created_by === 'eng0-stripe-one-time-payment');

  if (!product) {
    product = await stripe.products.create({
      name: 'Sample Product',
      description: 'A sample product for one-time payment demo',
      metadata: { created_by: 'eng0-stripe-one-time-payment' }
    });
  }

  const existingPrices = await stripe.prices.list({ product: product.id, active: true, limit: 1 });
  let price = existingPrices.data[0];
  if (!price) {
    price = await stripe.prices.create({ product: product.id, unit_amount: 2000, currency: 'usd' });
  }

  PRICE_ID = price.id;
  initialized = true;
  return PRICE_ID;
}

module.exports = async (req, res) => {
  const path = req.url.split('?')[0];

  if (path === '/config') {
    const priceId = await ensureProductAndPrice();
    const price = await stripe.prices.retrieve(priceId);
    return res.json({ publicKey: process.env.STRIPE_PUBLISHABLE_KEY, unitAmount: price.unit_amount, currency: price.currency });
  }

  if (path === '/checkout-session') {
    const session = await stripe.checkout.sessions.retrieve(req.query.sessionId);
    return res.json(session);
  }

  if (path === '/create-checkout-session' && req.method === 'POST') {
    const priceId = await ensureProductAndPrice();
    const host = req.headers.host;
    const domainURL = process.env.DOMAIN || `https://${host}`;
    const quantity = req.body?.quantity || 1;

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: priceId, quantity: parseInt(quantity) }],
      success_url: `${domainURL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${domainURL}/canceled.html`,
    });

    res.setHeader('Location', session.url);
    return res.status(303).end();
  }

  return res.status(404).json({ error: 'Not found' });
};
```

### Step 2: Create Vercel Config

Create `vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "",
  "outputDirectory": "client/html",
  "rewrites": [
    { "source": "/config", "destination": "/api" },
    { "source": "/checkout-session", "destination": "/api" },
    { "source": "/create-checkout-session", "destination": "/api" }
  ]
}
```

### Step 3: Set Environment Variables

```bash
printf "YOUR_SECRET_KEY" | vercel env add STRIPE_SECRET_KEY production -t $VERCEL_TOKEN
printf "YOUR_PUBLISHABLE_KEY" | vercel env add STRIPE_PUBLISHABLE_KEY production -t $VERCEL_TOKEN
```

### Step 4: Deploy

```bash
vercel --prod -t $VERCEL_TOKEN --yes
```

## Deploy to Netlify

### Step 1: Create Netlify Function

Create `netlify/functions/api.js` with similar serverless handler logic.

### Step 2: Create Netlify Config

Create `netlify.toml`:

```toml
[build]
  publish = "client/html"
  functions = "netlify/functions"

[[redirects]]
  from = "/config"
  to = "/.netlify/functions/api"
  status = 200

[[redirects]]
  from = "/checkout-session"
  to = "/.netlify/functions/api"
  status = 200

[[redirects]]
  from = "/create-checkout-session"
  to = "/.netlify/functions/api"
  status = 200
```

### Step 3: Deploy

```bash
netlify deploy --prod
```

## Local Development

```bash
npm install
npm start
```

Opens at http://localhost:4242

## Going Live Checklist

1. Replace test keys (sk_test_/pk_test_) with live keys (sk_live_/pk_live_)
2. Create products in Stripe Dashboard Live mode (or let auto-create)
3. Complete Stripe account verification (KYC)
4. Test with a real payment
