---
name: build-and-deploy
description: Build and deploy this Stripe Subscription application. Use when building, deploying, or preparing the project for production.
---

# Build and Deploy Stripe Subscription

This is an Express.js backend application. Deploying to serverless platforms (Vercel/Netlify) requires creating API wrapper files.

## Tech Stack

- **Backend**: Express.js
- **Payments**: Stripe Checkout + Customer Portal
- **Language**: JavaScript
- **Package Manager**: npm
- **Port**: 4242

## Environment Variables

**Required:**
- `STRIPE_SECRET_KEY` - Your Stripe secret key (sk_test_xxx or sk_live_xxx)
- `STRIPE_PUBLISHABLE_KEY` - Your Stripe publishable key (pk_test_xxx or pk_live_xxx)

**Optional (auto-created if not set):**
- `BASIC_PRICE` - Price ID for Starter plan. If not set, $12/month plan will be auto-created.
- `PRO_PRICE` - Price ID for Professional plan. If not set, $18/month plan will be auto-created.
- `DOMAIN` - Your production domain (auto-detected if not set)

## Deploy to Vercel

### Step 1: Create Serverless API Wrapper

Create `api/index.js`:

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-11-20.acacia',
});

let BASIC_PRICE_ID = process.env.BASIC_PRICE;
let PRO_PRICE_ID = process.env.PRO_PRICE;
let initialized = false;

async function ensureProductsAndPrices() {
  if (initialized && BASIC_PRICE_ID && PRO_PRICE_ID) {
    return { basicPrice: BASIC_PRICE_ID, proPrice: PRO_PRICE_ID };
  }
  if (BASIC_PRICE_ID && PRO_PRICE_ID) {
    initialized = true;
    return { basicPrice: BASIC_PRICE_ID, proPrice: PRO_PRICE_ID };
  }

  const existingProducts = await stripe.products.list({ limit: 20 });

  // Basic plan
  let basicProduct = existingProducts.data.find(p =>
    p.metadata?.created_by === 'eng0-stripe-subscription' && p.metadata?.plan === 'basic'
  );
  if (!basicProduct) {
    basicProduct = await stripe.products.create({
      name: 'Starter Plan',
      description: 'Perfect for getting started',
      metadata: { created_by: 'eng0-stripe-subscription', plan: 'basic' }
    });
  }

  // Pro plan
  let proProduct = existingProducts.data.find(p =>
    p.metadata?.created_by === 'eng0-stripe-subscription' && p.metadata?.plan === 'pro'
  );
  if (!proProduct) {
    proProduct = await stripe.products.create({
      name: 'Professional Plan',
      description: 'For professionals who need more',
      metadata: { created_by: 'eng0-stripe-subscription', plan: 'pro' }
    });
  }

  // Basic price
  if (!BASIC_PRICE_ID) {
    const basicPrices = await stripe.prices.list({ product: basicProduct.id, active: true, limit: 1 });
    if (basicPrices.data.length > 0) {
      BASIC_PRICE_ID = basicPrices.data[0].id;
    } else {
      const price = await stripe.prices.create({
        product: basicProduct.id, unit_amount: 1200, currency: 'usd', recurring: { interval: 'month' }
      });
      BASIC_PRICE_ID = price.id;
    }
  }

  // Pro price
  if (!PRO_PRICE_ID) {
    const proPrices = await stripe.prices.list({ product: proProduct.id, active: true, limit: 1 });
    if (proPrices.data.length > 0) {
      PRO_PRICE_ID = proPrices.data[0].id;
    } else {
      const price = await stripe.prices.create({
        product: proProduct.id, unit_amount: 1800, currency: 'usd', recurring: { interval: 'month' }
      });
      PRO_PRICE_ID = price.id;
    }
  }

  initialized = true;
  return { basicPrice: BASIC_PRICE_ID, proPrice: PRO_PRICE_ID };
}

module.exports = async (req, res) => {
  const path = req.url.split('?')[0];

  if (path === '/config') {
    const prices = await ensureProductsAndPrices();
    return res.json({
      publicKey: process.env.STRIPE_PUBLISHABLE_KEY,
      basicPrice: prices.basicPrice,
      proPrice: prices.proPrice,
    });
  }

  if (path === '/checkout-session') {
    const session = await stripe.checkout.sessions.retrieve(req.query.sessionId);
    return res.json(session);
  }

  if (path === '/create-checkout-session' && req.method === 'POST') {
    await ensureProductsAndPrices();
    const host = req.headers.host;
    const domainURL = process.env.DOMAIN || `https://${host}`;
    const priceId = req.body?.priceId;

    if (!priceId) return res.status(400).json({ error: 'Missing priceId' });

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${domainURL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${domainURL}/canceled.html`,
    });

    res.setHeader('Location', session.url);
    return res.status(303).end();
  }

  if (path === '/customer-portal' && req.method === 'POST') {
    const sessionId = req.body?.sessionId;
    if (!sessionId) return res.status(400).json({ error: 'Missing sessionId' });

    const checkoutSession = await stripe.checkout.sessions.retrieve(sessionId);
    const host = req.headers.host;
    const domainURL = process.env.DOMAIN || `https://${host}`;

    const portalSession = await stripe.billingPortal.sessions.create({
      customer: checkoutSession.customer,
      return_url: domainURL,
    });

    res.setHeader('Location', portalSession.url);
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
    { "source": "/create-checkout-session", "destination": "/api" },
    { "source": "/customer-portal", "destination": "/api" }
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

[[redirects]]
  from = "/customer-portal"
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

## Customer Portal Configuration

Before going live, configure the Customer Portal in Stripe Dashboard:

1. Go to [Settings > Billing > Customer Portal](https://dashboard.stripe.com/settings/billing/portal)
2. Enable: Update payment method, Cancel subscription, Switch plans
3. Save configuration

## Going Live Checklist

1. Replace test keys (sk_test_/pk_test_) with live keys (sk_live_/pk_live_)
2. Create subscription products in Stripe Dashboard Live mode (or let auto-create)
3. Complete Stripe account verification (KYC)
4. Configure Customer Portal for live mode
5. Test with a real subscription
