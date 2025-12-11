# Stripe Integration with Next.js

Next.js-specific patterns for Stripe integration using App Router.

## Project Setup

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

## Environment Variables

```bash
# .env.local
STRIPE_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

Note: Only `NEXT_PUBLIC_` prefixed variables are available on client.

## Directory Structure

```
app/
├── api/
│   ├── create-checkout-session/
│   │   └── route.ts
│   ├── create-payment-intent/
│   │   └── route.ts
│   └── webhook/
│       └── route.ts
├── checkout/
│   └── page.tsx
├── success/
│   └── page.tsx
└── layout.tsx
lib/
└── stripe.ts
```

## Stripe Client Setup

```typescript
// lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
  typescript: true,
});
```

## API Routes

### Create Checkout Session

```typescript
// app/api/create-checkout-session/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function POST(req: NextRequest) {
  try {
    const { priceId } = await req.json();

    // Validate price ID
    const allowedPrices = ['price_xxx', 'price_yyy'];
    if (!allowedPrices.includes(priceId)) {
      return NextResponse.json(
        { error: 'Invalid price' },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${process.env.NEXT_PUBLIC_BASE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL}/checkout`,
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Checkout session error:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
```

### Create PaymentIntent

```typescript
// app/api/create-payment-intent/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function POST(req: NextRequest) {
  try {
    const { productId } = await req.json();

    // Get price from your database
    const product = await getProduct(productId); // Your database call

    const paymentIntent = await stripe.paymentIntents.create({
      amount: product.priceInCents,
      currency: 'usd',
      automatic_payment_methods: {
        enabled: true,
      },
      metadata: {
        productId,
      },
    });

    return NextResponse.json({
      clientSecret: paymentIntent.client_secret,
    });
  } catch (error) {
    console.error('PaymentIntent error:', error);
    return NextResponse.json(
      { error: 'Failed to create payment intent' },
      { status: 500 }
    );
  }
}
```

### Webhook Handler

```typescript
// app/api/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import Stripe from 'stripe';

export async function POST(req: NextRequest) {
  const body = await req.text(); // Raw body for signature verification
  const sig = req.headers.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed');
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 400 }
    );
  }

  // Handle the event
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      await handleCheckoutComplete(session);
      break;
    }
    case 'payment_intent.succeeded': {
      const paymentIntent = event.data.object as Stripe.PaymentIntent;
      await handlePaymentSuccess(paymentIntent);
      break;
    }
    // Add more event handlers as needed
  }

  return NextResponse.json({ received: true });
}

async function handleCheckoutComplete(session: Stripe.Checkout.Session) {
  // Implement your fulfillment logic
  console.log('Checkout completed:', session.id);
}

async function handlePaymentSuccess(paymentIntent: Stripe.PaymentIntent) {
  // Implement your fulfillment logic
  console.log('Payment succeeded:', paymentIntent.id);
}
```

## Client Components

### Stripe Provider

```typescript
// app/providers.tsx
'use client';

import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);

export function StripeProvider({ children }: { children: React.ReactNode }) {
  return <Elements stripe={stripePromise}>{children}</Elements>;
}
```

### Checkout Button

```typescript
// components/checkout-button.tsx
'use client';

import { useState } from 'react';

export function CheckoutButton({ priceId }: { priceId: string }) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId }),
      });

      const { url } = await response.json();
      window.location.href = url;
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Failed to start checkout');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleCheckout} disabled={loading}>
      {loading ? 'Loading...' : 'Buy Now'}
    </button>
  );
}
```

### Payment Form with Payment Element

```typescript
// components/payment-form.tsx
'use client';

import { useState, useEffect } from 'react';
import {
  useStripe,
  useElements,
  PaymentElement,
} from '@stripe/react-stripe-js';

export function PaymentForm({ productId }: { productId: string }) {
  const stripe = useStripe();
  const elements = useElements();
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId }),
    })
      .then((res) => res.json())
      .then((data) => setClientSecret(data.clientSecret));
  }, [productId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setLoading(true);
    setError('');

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/success`,
      },
    });

    if (error) {
      setError(error.message || 'Payment failed');
    }

    setLoading(false);
  };

  if (!clientSecret) {
    return <div>Loading...</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={!stripe || loading}>
        {loading ? 'Processing...' : 'Pay'}
      </button>
    </form>
  );
}
```

### Payment Page with Elements Provider

```typescript
// app/checkout/page.tsx
'use client';

import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import { PaymentForm } from '@/components/payment-form';
import { useEffect, useState } from 'react';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);

export default function CheckoutPage() {
  const [clientSecret, setClientSecret] = useState('');

  useEffect(() => {
    fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId: 'prod_xxx' }),
    })
      .then((res) => res.json())
      .then((data) => setClientSecret(data.clientSecret));
  }, []);

  if (!clientSecret) {
    return <div>Loading...</div>;
  }

  return (
    <Elements
      stripe={stripePromise}
      options={{
        clientSecret,
        appearance: {
          theme: 'stripe',
        },
      }}
    >
      <PaymentForm productId="prod_xxx" />
    </Elements>
  );
}
```

## Success Page

```typescript
// app/success/page.tsx
import { stripe } from '@/lib/stripe';
import { redirect } from 'next/navigation';

export default async function SuccessPage({
  searchParams,
}: {
  searchParams: { session_id?: string };
}) {
  const sessionId = searchParams.session_id;

  if (!sessionId) {
    redirect('/');
  }

  const session = await stripe.checkout.sessions.retrieve(sessionId);

  if (session.payment_status !== 'paid') {
    redirect('/checkout?error=payment_failed');
  }

  return (
    <div>
      <h1>Payment Successful!</h1>
      <p>Thank you for your purchase.</p>
      <p>Amount: ${(session.amount_total! / 100).toFixed(2)}</p>
    </div>
  );
}
```

## Server Actions (Next.js 14+)

```typescript
// app/actions/stripe.ts
'use server';

import { stripe } from '@/lib/stripe';
import { redirect } from 'next/navigation';

export async function createCheckoutSession(priceId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_BASE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL}/checkout`,
  });

  redirect(session.url!);
}

// Usage in component
// <form action={createCheckoutSession.bind(null, 'price_xxx')}>
//   <button type="submit">Buy</button>
// </form>
```

## Middleware for Protected Routes

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check subscription status from cookie/session
  const hasSubscription = request.cookies.get('subscription_active');

  if (request.nextUrl.pathname.startsWith('/premium') && !hasSubscription) {
    return NextResponse.redirect(new URL('/pricing', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/premium/:path*',
};
```

## Common Pitfalls

### 1. Wrong Body Parsing in Webhook

```typescript
// WRONG - body already parsed
export async function POST(req: NextRequest) {
  const body = await req.json(); // This breaks signature verification
}

// CORRECT - use raw body
export async function POST(req: NextRequest) {
  const body = await req.text();
}
```

### 2. Using Server Components for Payment UI

```typescript
// WRONG - Stripe.js needs client-side
export default function CheckoutPage() {
  // This is a server component by default
  return <PaymentElement />; // Won't work
}

// CORRECT - Mark as client component
'use client';
export default function CheckoutPage() {
  return <PaymentElement />;
}
```

### 3. Exposing Secret Key

```typescript
// WRONG - Will be bundled in client
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// CORRECT - Only use in API routes or server components
// And use NEXT_PUBLIC_ for publishable key only
```

## Checklist

- [ ] `@stripe/stripe-js` and `@stripe/react-stripe-js` installed
- [ ] Environment variables in `.env.local`
- [ ] Only `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` exposed to client
- [ ] Webhook route uses `req.text()` for raw body
- [ ] Payment UI components marked with `'use client'`
- [ ] Elements provider wraps payment components
- [ ] Success page validates session status server-side
