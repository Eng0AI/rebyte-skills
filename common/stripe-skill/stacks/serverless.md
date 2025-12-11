# Stripe Integration with Serverless (Vercel/Netlify)

Patterns for serverless deployments where you don't have a persistent server.

## Key Differences from Traditional Servers

1. **No persistent connections** - Each function invocation is independent
2. **Cold starts** - First request may be slower
3. **Timeout limits** - Usually 10-30 seconds max
4. **No background processing** - Function ends when response is sent

## Vercel Setup

### Directory Structure

```
├── api/
│   ├── create-checkout-session.ts
│   ├── create-payment-intent.ts
│   ├── webhook.ts
│   └── portal.ts
├── public/
│   └── checkout.html
├── lib/
│   └── stripe.ts
├── vercel.json
└── package.json
```

### Stripe Client

```typescript
// lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});
```

### Create Checkout Session

```typescript
// api/create-checkout-session.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';
import { stripe } from '../lib/stripe';

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { priceId } = req.body;

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.VERCEL_URL || 'http://localhost:3000'}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.VERCEL_URL || 'http://localhost:3000'}/cancel`,
    });

    res.json({ url: session.url });
  } catch (error) {
    console.error('Checkout error:', error);
    res.status(500).json({ error: 'Failed to create checkout' });
  }
}
```

### Webhook Handler (Vercel)

```typescript
// api/webhook.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';
import { stripe } from '../lib/stripe';
import { buffer } from 'micro';
import Stripe from 'stripe';

// Disable body parsing - we need raw body
export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const buf = await buffer(req);
  const sig = req.headers['stripe-signature'] as string;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      buf,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed');
    return res.status(400).json({ error: 'Invalid signature' });
  }

  // Handle the event synchronously (serverless constraint)
  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutComplete(event.data.object as Stripe.Checkout.Session);
        break;
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(event.data.object as Stripe.PaymentIntent);
        break;
    }

    res.json({ received: true });
  } catch (err) {
    console.error('Webhook processing error:', err);
    // Return 200 to prevent retries for processing errors
    res.json({ received: true, error: 'Processing failed' });
  }
}

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  // Keep this fast! No heavy processing
  // Consider using a queue service for complex operations
  console.log('Checkout completed:', session.id);

  // Quick database write
  await saveOrder(session);
}

async function handlePaymentSuccess(paymentIntent: Stripe.PaymentIntent) {
  console.log('Payment succeeded:', paymentIntent.id);
}
```

### Vercel Configuration

```json
// vercel.json
{
  "functions": {
    "api/webhook.ts": {
      "maxDuration": 30
    }
  }
}
```

## Netlify Setup

### Directory Structure

```
├── netlify/
│   └── functions/
│       ├── create-checkout-session.ts
│       ├── create-payment-intent.ts
│       └── webhook.ts
├── public/
│   └── checkout.html
├── lib/
│   └── stripe.ts
├── netlify.toml
└── package.json
```

### Create Checkout Session (Netlify)

```typescript
// netlify/functions/create-checkout-session.ts
import { Handler } from '@netlify/functions';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export const handler: Handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  try {
    const { priceId } = JSON.parse(event.body || '{}');

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${process.env.URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.URL}/cancel`,
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ url: session.url }),
    };
  } catch (error) {
    console.error('Checkout error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to create checkout' }),
    };
  }
};
```

### Webhook Handler (Netlify)

```typescript
// netlify/functions/webhook.ts
import { Handler } from '@netlify/functions';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export const handler: Handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method not allowed' };
  }

  const sig = event.headers['stripe-signature'];

  if (!sig || !event.body) {
    return { statusCode: 400, body: 'Missing signature or body' };
  }

  let stripeEvent: Stripe.Event;

  try {
    stripeEvent = stripe.webhooks.constructEvent(
      event.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed');
    return { statusCode: 400, body: 'Invalid signature' };
  }

  // Handle events
  switch (stripeEvent.type) {
    case 'checkout.session.completed':
      // Handle checkout completion
      break;
    case 'payment_intent.succeeded':
      // Handle payment success
      break;
  }

  return {
    statusCode: 200,
    body: JSON.stringify({ received: true }),
  };
};
```

### Netlify Configuration

```toml
# netlify.toml
[functions]
  directory = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

## Handling Async Operations in Serverless

Since serverless functions end when the response is sent, you can't do background processing. Options:

### Option 1: Keep It Fast

```typescript
// Do only essential operations in webhook
async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  // Quick: Write to database
  await db.orders.create({
    stripeSessionId: session.id,
    status: 'completed',
  });

  // That's it - don't do slow operations here
}
```

### Option 2: Use a Queue Service

```typescript
// Send to queue for processing
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';

const sqs = new SQSClient({});

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  // Quick: Send to queue
  await sqs.send(new SendMessageCommand({
    QueueUrl: process.env.ORDER_QUEUE_URL,
    MessageBody: JSON.stringify({
      type: 'checkout_complete',
      sessionId: session.id,
    }),
  }));

  // Another Lambda will process the queue
}
```

### Option 3: Use Inngest/Trigger.dev

```typescript
// Using Inngest for background jobs
import { Inngest } from 'inngest';

const inngest = new Inngest({ id: 'my-app' });

// Define the function
export const fulfillOrder = inngest.createFunction(
  { id: 'fulfill-order' },
  { event: 'checkout/completed' },
  async ({ event }) => {
    // This runs in background, can take as long as needed
    await sendConfirmationEmail(event.data.email);
    await generateInvoicePDF(event.data.sessionId);
    await updateInventory(event.data.items);
  }
);

// In webhook, just trigger the event
async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  await inngest.send({
    name: 'checkout/completed',
    data: {
      sessionId: session.id,
      email: session.customer_details?.email,
    },
  });
}
```

## Database Considerations

### Serverless-Friendly Databases

- **Planetscale** - MySQL compatible, serverless
- **Supabase** - PostgreSQL with REST API
- **Upstash** - Serverless Redis
- **Fauna** - Serverless document DB
- **MongoDB Atlas** - With connection pooling

### Connection Pooling

```typescript
// lib/db.ts
import { Pool } from 'pg';

// Reuse pool across invocations
let pool: Pool | null = null;

export function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      max: 1, // Low for serverless
    });
  }
  return pool;
}
```

## Environment Variables

### Vercel
```bash
# Set via Vercel CLI or Dashboard
vercel env add STRIPE_SECRET_KEY
vercel env add STRIPE_WEBHOOK_SECRET
```

### Netlify
```bash
# Set via Netlify CLI or Dashboard
netlify env:set STRIPE_SECRET_KEY "sk_xxx"
netlify env:set STRIPE_WEBHOOK_SECRET "whsec_xxx"
```

## Local Development

### Vercel
```bash
npm install -g vercel
vercel dev

# In another terminal
stripe listen --forward-to localhost:3000/api/webhook
```

### Netlify
```bash
npm install -g netlify-cli
netlify dev

# In another terminal
stripe listen --forward-to localhost:8888/.netlify/functions/webhook
```

## Common Pitfalls

### 1. Function Timeout

```typescript
// WRONG - May timeout
async function handleWebhook(event) {
  await sendEmail(); // 5s
  await generatePDF(); // 10s
  await updateInventory(); // 3s
  // Total: 18s - may exceed limit
}

// CORRECT - Offload to queue
async function handleWebhook(event) {
  await queue.send(event); // <100ms
}
```

### 2. Cold Start + Stripe Init

```typescript
// Initialize outside handler for reuse
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

// Not inside handler - would init every time
export const handler = async (event) => {
  // Use stripe here
};
```

### 3. Missing Body Parser Config

```typescript
// Vercel - disable body parsing for webhooks
export const config = {
  api: {
    bodyParser: false,
  },
};
```

## Checklist

- [ ] Stripe client initialized outside handler
- [ ] Body parser disabled for webhook route
- [ ] Webhook processing is fast (<10s)
- [ ] Heavy operations use queue/background jobs
- [ ] Database uses connection pooling
- [ ] Environment variables set in platform
- [ ] Local development uses Stripe CLI
- [ ] Function timeout configured appropriately
