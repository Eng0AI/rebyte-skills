# Stripe Security Checklist

Complete this checklist before going to production.

## API Keys

### Must Do
- [ ] **Secret key in environment variables** - Never in code
- [ ] **Different keys for test/production** - Use `sk_test_` in dev, `sk_live_` in prod
- [ ] **Secret key never exposed to client** - Only `pk_` keys go to frontend
- [ ] **Keys rotated periodically** - At least annually, immediately if compromised
- [ ] **Restricted API keys for specific services** - Use Dashboard to create limited keys

### Verification
```bash
# Check for hardcoded keys
grep -r "sk_live_" --include="*.js" --include="*.ts" .
grep -r "sk_test_" --include="*.js" --include="*.ts" .
# Should return nothing
```

## Webhook Security

### Must Do
- [ ] **Webhook signature verified** - Use `stripe.webhooks.constructEvent()`
- [ ] **Webhook secret in environment variables**
- [ ] **Raw body used for verification** - Not parsed JSON
- [ ] **HTTPS only in production** - HTTP OK for local development only
- [ ] **Webhook endpoint not rate limited** - Stripe needs to reach it

### Verification
```javascript
// REQUIRED in every webhook handler
const event = stripe.webhooks.constructEvent(
  req.body,      // Raw body, not req.body after JSON parsing
  sig,
  process.env.STRIPE_WEBHOOK_SECRET
);
```

## Payment Security

### Must Do
- [ ] **PaymentIntent created server-side** - Never create from client
- [ ] **Amount from YOUR database** - Never trust client-provided amount
- [ ] **Price/Product IDs validated** - Whitelist allowed values
- [ ] **Currency validated** - Don't accept arbitrary currencies
- [ ] **Metadata doesn't contain secrets** - Visible in Dashboard

### Verification
```javascript
// WRONG
app.post('/pay', async (req, res) => {
  const { amount } = req.body;  // NEVER trust client amount
  await stripe.paymentIntents.create({ amount });
});

// CORRECT
app.post('/pay', async (req, res) => {
  const { productId } = req.body;
  const product = await db.products.findById(productId);  // Your database
  await stripe.paymentIntents.create({ amount: product.priceInCents });
});
```

## Data Security

### Must Do
- [ ] **Never log full card numbers** - Stripe handles card data
- [ ] **Never store raw card data** - Use Stripe's tokens/payment methods
- [ ] **Customer email validated** - Prevent injection
- [ ] **Metadata sanitized** - No user input directly in metadata without validation
- [ ] **PII handled according to regulations** - GDPR, CCPA compliance

### Verification
```javascript
// Check logging doesn't include sensitive data
// WRONG
console.log('Payment:', paymentIntent);  // May contain sensitive data

// CORRECT
console.log('Payment:', {
  id: paymentIntent.id,
  amount: paymentIntent.amount,
  status: paymentIntent.status,
});
```

## Infrastructure

### Must Do
- [ ] **HTTPS enforced** - No HTTP in production
- [ ] **TLS 1.2+** - Stripe requires it
- [ ] **Environment variables not in version control** - Use `.env.example` as template
- [ ] **`.env` in `.gitignore`**
- [ ] **Secrets manager in production** - AWS Secrets Manager, Vault, etc.

### Verification
```bash
# Check .gitignore
cat .gitignore | grep -E "^\.env$|^\.env\.local$"

# Check no secrets committed
git log -p | grep -E "sk_(test|live)_" | head -20
```

## Access Control

### Must Do
- [ ] **Dashboard access restricted** - Only necessary team members
- [ ] **2FA enabled on Stripe account**
- [ ] **Separate accounts for test/live** - Or use team permissions
- [ ] **Audit log reviewed regularly** - Check for suspicious activity

## Input Validation

### Must Do
- [ ] **Email format validated** - Before passing to Stripe
- [ ] **Amount is positive integer** - No negative or decimal
- [ ] **Currency is valid ISO code** - Whitelist supported currencies
- [ ] **Quantity is positive integer** - No zero or negative
- [ ] **Metadata values sanitized** - Length limits, no special characters

### Validation Examples
```javascript
function validatePaymentInput(input) {
  const errors = [];

  // Amount
  if (!Number.isInteger(input.amount) || input.amount <= 0) {
    errors.push('Invalid amount');
  }

  // Currency
  const allowedCurrencies = ['usd', 'eur', 'gbp'];
  if (!allowedCurrencies.includes(input.currency?.toLowerCase())) {
    errors.push('Invalid currency');
  }

  // Email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (input.email && !emailRegex.test(input.email)) {
    errors.push('Invalid email');
  }

  // Metadata
  if (input.metadata) {
    for (const [key, value] of Object.entries(input.metadata)) {
      if (key.length > 40) errors.push('Metadata key too long');
      if (String(value).length > 500) errors.push('Metadata value too long');
    }
  }

  return errors;
}
```

## Fraud Prevention

### Must Do
- [ ] **Radar enabled** - Stripe's fraud detection
- [ ] **3D Secure for high-risk** - Use `payment_method_options`
- [ ] **Velocity checks** - Limit purchases per user/IP
- [ ] **Address verification (AVS)** - For card-not-present
- [ ] **Review suspicious orders** - Manual review queue

### Enable 3D Secure
```javascript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 1999,
  currency: 'usd',
  payment_method_options: {
    card: {
      request_three_d_secure: 'any',  // or 'automatic'
    },
  },
});
```

## Error Handling Security

### Must Do
- [ ] **Generic error messages to users** - Don't expose internal details
- [ ] **Detailed errors to logs only** - With request ID for debugging
- [ ] **No stack traces to client** - In production
- [ ] **Rate limit login/payment attempts** - Prevent brute force

### Example
```javascript
// WRONG - Exposes internal details
res.status(500).json({ error: error.stack });

// CORRECT - Generic message, log details
console.error('Stripe error:', {
  type: error.type,
  message: error.message,
  requestId: error.requestId,
});
res.status(500).json({ error: 'Payment processing failed. Please try again.' });
```

## Pre-Launch Final Check

```bash
# 1. No hardcoded secrets
grep -rn "sk_" --include="*.js" --include="*.ts" --include="*.env" .

# 2. Environment variables set
echo $STRIPE_SECRET_KEY | head -c 10  # Should show sk_live_ or sk_test_

# 3. Webhook endpoint accessible
curl -X POST https://yourdomain.com/webhook

# 4. HTTPS working
curl -I https://yourdomain.com

# 5. Test mode disabled (when ready)
# Verify no sk_test_ keys in production config
```

## Incident Response

If you suspect a compromise:

1. **Rotate API keys immediately** - Dashboard → Developers → API keys → Roll key
2. **Review recent transactions** - Check for unauthorized charges
3. **Check webhook endpoints** - Ensure no unauthorized endpoints added
4. **Review team access** - Remove suspicious users
5. **Contact Stripe support** - If customer data potentially exposed
6. **Notify affected customers** - Per legal requirements (GDPR, etc.)

## Resources

- [Stripe Security Documentation](https://stripe.com/docs/security)
- [PCI DSS Compliance](https://stripe.com/docs/security/guide)
- [Stripe Radar](https://stripe.com/radar)
- [Security Best Practices](https://stripe.com/docs/security/guide)
