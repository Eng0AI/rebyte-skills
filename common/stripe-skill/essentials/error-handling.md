# Error Handling in Stripe Integrations

Proper error handling prevents lost payments and bad user experiences.

## Error Types

Stripe errors have a `type` property:

| Type | Cause | Action |
|------|-------|--------|
| `StripeCardError` | Card declined | Show message to user, let them try again |
| `StripeRateLimitError` | Too many requests | Retry with backoff |
| `StripeInvalidRequestError` | Invalid parameters | Fix your code (bug) |
| `StripeAPIError` | Stripe's servers | Retry with backoff |
| `StripeConnectionError` | Network issue | Retry with backoff |
| `StripeAuthenticationError` | Invalid API key | Fix configuration |
| `StripeIdempotencyError` | Idempotency conflict | Check idempotency key usage |

## Server-Side Error Handling

```javascript
async function createPaymentIntent(amount, currency) {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency,
    });
    return { success: true, paymentIntent };
  } catch (error) {
    return handleStripeError(error);
  }
}

function handleStripeError(error) {
  switch (error.type) {
    case 'StripeCardError':
      // Card was declined
      return {
        success: false,
        error: {
          type: 'card_error',
          message: error.message, // Safe to show to user
          code: error.code,
          declineCode: error.decline_code,
        },
      };

    case 'StripeRateLimitError':
      // Too many requests - should retry
      console.error('Rate limited by Stripe');
      return {
        success: false,
        error: {
          type: 'rate_limit',
          message: 'Too many requests. Please try again.',
          retryable: true,
        },
      };

    case 'StripeInvalidRequestError':
      // Invalid parameters - this is a bug
      console.error('Invalid Stripe request:', error.message);
      return {
        success: false,
        error: {
          type: 'invalid_request',
          message: 'Something went wrong. Please try again.',
          // Don't expose internal error to user
        },
      };

    case 'StripeAPIError':
      // Stripe issue - retry may work
      console.error('Stripe API error:', error.message);
      return {
        success: false,
        error: {
          type: 'api_error',
          message: 'Payment service temporarily unavailable.',
          retryable: true,
        },
      };

    case 'StripeConnectionError':
      // Network issue
      console.error('Stripe connection error:', error.message);
      return {
        success: false,
        error: {
          type: 'connection_error',
          message: 'Connection issue. Please try again.',
          retryable: true,
        },
      };

    case 'StripeAuthenticationError':
      // Bad API key - critical configuration error
      console.error('CRITICAL: Stripe authentication failed');
      // Alert your team immediately
      return {
        success: false,
        error: {
          type: 'configuration_error',
          message: 'Payment system configuration error.',
        },
      };

    default:
      console.error('Unknown Stripe error:', error);
      return {
        success: false,
        error: {
          type: 'unknown',
          message: 'An unexpected error occurred.',
        },
      };
  }
}
```

## Card Decline Codes

When `error.type === 'StripeCardError'`, check `error.decline_code`:

```javascript
function getDeclineMessage(declineCode) {
  const messages = {
    'insufficient_funds': 'Your card has insufficient funds.',
    'lost_card': 'This card has been reported lost.',
    'stolen_card': 'This card has been reported stolen.',
    'expired_card': 'Your card has expired.',
    'incorrect_cvc': 'The CVC code is incorrect.',
    'processing_error': 'An error occurred processing your card. Please try again.',
    'incorrect_number': 'The card number is incorrect.',
    'card_velocity_exceeded': 'You have exceeded your card limit. Please try again later.',
    'do_not_honor': 'Your card was declined. Please contact your bank.',
    'generic_decline': 'Your card was declined. Please try a different card.',
  };

  return messages[declineCode] || 'Your card was declined. Please try a different card.';
}
```

## Client-Side Error Handling

```javascript
// Using Stripe.js
const { error, paymentIntent } = await stripe.confirmPayment({
  elements,
  confirmParams: {
    return_url: 'https://example.com/success',
  },
  redirect: 'if_required',
});

if (error) {
  // Show error to customer
  if (error.type === 'card_error' || error.type === 'validation_error') {
    showError(error.message);
  } else {
    showError('An unexpected error occurred.');
  }
}
```

## Retry Logic with Exponential Backoff

```javascript
async function stripeWithRetry(operation, maxRetries = 3) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;

      // Only retry on retryable errors
      const retryableTypes = [
        'StripeRateLimitError',
        'StripeAPIError',
        'StripeConnectionError',
      ];

      if (!retryableTypes.includes(error.type)) {
        throw error; // Don't retry non-retryable errors
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt) * 1000;
      console.log(`Stripe error, retrying in ${delay}ms...`);
      await sleep(delay);
    }
  }

  throw lastError;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage
const paymentIntent = await stripeWithRetry(() =>
  stripe.paymentIntents.create({
    amount: 1000,
    currency: 'usd',
  })
);
```

## Idempotency for Safe Retries

Use idempotency keys to safely retry requests:

```javascript
const crypto = require('crypto');

async function createPaymentWithIdempotency(orderId, amount) {
  // Generate deterministic key from order ID
  const idempotencyKey = `payment_${orderId}`;

  const paymentIntent = await stripe.paymentIntents.create(
    {
      amount,
      currency: 'usd',
      metadata: { orderId },
    },
    {
      idempotencyKey,
    }
  );

  return paymentIntent;
}

// Safe to call multiple times - Stripe returns same result
await createPaymentWithIdempotency('order_123', 1999);
await createPaymentWithIdempotency('order_123', 1999); // Returns same PI
```

## Logging Best Practices

```javascript
function logStripeError(error, context = {}) {
  const logData = {
    timestamp: new Date().toISOString(),
    type: error.type,
    code: error.code,
    message: error.message,
    requestId: error.requestId, // Useful for Stripe support
    ...context,
  };

  // Don't log sensitive data
  if (error.raw) {
    logData.rawType = error.raw.type;
    logData.rawCode = error.raw.code;
    // Don't log error.raw.message - might contain card details
  }

  console.error('Stripe error:', JSON.stringify(logData));

  // Alert on critical errors
  if (error.type === 'StripeAuthenticationError') {
    alertOncall('CRITICAL: Stripe API key invalid');
  }
}
```

## Error Recovery Patterns

### Payment Failed - Allow Retry
```javascript
app.post('/retry-payment', async (req, res) => {
  const { paymentIntentId } = req.body;

  // Retrieve existing PaymentIntent
  const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);

  if (paymentIntent.status === 'succeeded') {
    return res.json({ error: 'Payment already succeeded' });
  }

  // Return client secret for retry
  res.json({ clientSecret: paymentIntent.client_secret });
});
```

### Subscription Payment Failed - Notify User
```javascript
async function handleInvoicePaymentFailed(invoice) {
  const customer = await stripe.customers.retrieve(invoice.customer);

  await sendEmail(customer.email, {
    subject: 'Payment Failed - Action Required',
    template: 'payment-failed',
    data: {
      amount: invoice.amount_due / 100,
      updatePaymentUrl: `${process.env.DOMAIN}/update-payment`,
    },
  });

  // Stripe will retry automatically, but user should update card
}
```

## Checklist

- [ ] All Stripe calls wrapped in try-catch
- [ ] Different error types handled appropriately
- [ ] User-friendly messages for card errors
- [ ] Retryable errors use exponential backoff
- [ ] Idempotency keys used for safe retries
- [ ] Errors logged with request ID (for Stripe support)
- [ ] Critical errors trigger alerts
- [ ] Sensitive data not exposed in error messages
