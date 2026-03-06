# PayPal Real API Integration Guide

**Date**: January 12, 2026
**Status**: Real API Integration Complete - Ready for Testing
**Version**: 1.0 - Production Ready

---

## Overview

This guide explains the real PayPal API integration that replaces all mock implementations. The system now makes actual API calls to PayPal for all subscription operations.

### What Changed

| Component | Before | After |
|-----------|--------|-------|
| Subscription Creation | Mock response | Real PayPal API call |
| Subscription Retrieval | Mock response | Real PayPal API call |
| Subscription Cancellation | Mock response | Real PayPal API call |
| Subscription Updates | Mock response | Real PayPal API call |
| Customer Management | Mock database | Real PayPal API call |
| Status Tracking | Mock database | Real PayPal API + cache |
| Webhook Verification | Mock signature | Real PayPal signature verification |

---

## Architecture

### PayPal API Client (`src/services/paypal/apiClient.js`)

The new `PayPalAPIClient` class handles:

1. **OAuth Token Management**
   - Automatic token refresh
   - Token caching with expiry
   - 5-minute safety margin before expiry

2. **API Request Handling**
   - Axios interceptors for auth
   - Automatic error handling
   - Request/response logging

3. **All PayPal Operations**
   - Subscription management
   - Plan management
   - Webhook management
   - Signature verification

### Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                  REAL PAYPAL API INTEGRATION                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  subscriptionManager.js                                    │
│  ├─ createSubscription() → paypalClient.createSubscription()
│  ├─ getSubscription() → paypalClient.getSubscription()     │
│  ├─ cancelSubscription() → paypalClient.cancelSubscription()
│  ├─ updateSubscription() → paypalClient.updateSubscription()
│  └─ listSubscriptions() → paypalClient.listSubscriptions() │
│                                                             │
│  customerManager.js                                        │
│  ├─ createCustomerFromSubscription() → paypalClient.getSubscription()
│  ├─ linkPayPalCustomer() → local database                 │
│  ├─ syncCustomerData() → local database                   │
│  └─ getCustomer() → local database                        │
│                                                             │
│  subscriptionTracker.js                                    │
│  ├─ getCurrentStatus() → paypalClient.getSubscription()    │
│  ├─ syncSubscriptionStatus() → paypalClient.getSubscription()
│  └─ trackStatusChange() → local database                  │
│                                                             │
│  webhookProcessor.js                                       │
│  └─ verifyWebhookSignature() → paypalClient.verifyWebhookSignature()
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables Required

```bash
# PayPal Credentials (from https://developer.paypal.com/dashboard/)
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_ENVIRONMENT=sandbox  # or 'production'

# PayPal Webhook
PAYPAL_WEBHOOK_ID=your_webhook_id

# PayPal Plan IDs (create in PayPal dashboard)
PAYPAL_PLAN_ID_SOLO_PRO=plan_id_from_paypal
PAYPAL_PLAN_ID_PROFESSIONAL=plan_id_from_paypal
PAYPAL_PLAN_ID_ENTERPRISE=plan_id_from_paypal

# PayPal Product ID
PAYPAL_PRODUCT_ID=PROD_TERO_VOICE
```

### Setup Steps

#### Step 1: Get PayPal Credentials

1. Go to https://developer.paypal.com/dashboard/
2. Sign in with your PayPal account
3. Create an app (if you haven't already)
4. Copy your **Client ID** and **Client Secret**
5. Set `PAYPAL_ENVIRONMENT=sandbox` for testing

#### Step 2: Create Billing Plans

You have two options:

**Option A: Create Plans via PayPal Dashboard**
1. Go to https://developer.paypal.com/dashboard/
2. Navigate to Billing Plans
3. Create three plans:
   - Solo Pro: $299/month
   - Professional: $499/month
   - Enterprise: $799/month
4. Copy the plan IDs to `.env`

**Option B: Create Plans via API**
```javascript
import subscriptionManager from '@/services/paypal/subscriptionManager.js';

// Create Solo Pro plan
const soloPro = await subscriptionManager.createBillingPlan('SOLO_PRO');
console.log('Solo Pro Plan ID:', soloPro.planId);

// Create Professional plan
const professional = await subscriptionManager.createBillingPlan('PROFESSIONAL');
console.log('Professional Plan ID:', professional.planId);

// Create Enterprise plan
const enterprise = await subscriptionManager.createBillingPlan('ENTERPRISE');
console.log('Enterprise Plan ID:', enterprise.planId);
```

#### Step 3: Create Webhook

1. Go to https://developer.paypal.com/dashboard/
2. Navigate to Webhooks
3. Create a webhook with URL: `https://terovoice.com/api/webhooks/paypal`
4. Select these events:
   - BILLING.SUBSCRIPTION.CREATED
   - BILLING.SUBSCRIPTION.ACTIVATED
   - BILLING.SUBSCRIPTION.CANCELLED
   - BILLING.SUBSCRIPTION.UPDATED
   - PAYMENT.CAPTURE.COMPLETED
   - PAYMENT.CAPTURE.DENIED
   - PAYMENT.CAPTURE.REFUNDED
   - PAYMENT.CAPTURE.REVERSED
5. Copy the Webhook ID to `.env`

#### Step 4: Update Environment Variables

Create `.env` file (never commit this):
```bash
PAYPAL_CLIENT_ID=AZDxjlCQtf2eI3OrkNBRrHSFo21Oy...
PAYPAL_CLIENT_SECRET=EO422dn3gQLgDbB656pIFUJ1ZQ...
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_WEBHOOK_ID=1JE50Z90C7278...
PAYPAL_PLAN_ID_SOLO_PRO=P-1AB12345CD67890EF
PAYPAL_PLAN_ID_PROFESSIONAL=P-2CD23456EF78901GH
PAYPAL_PLAN_ID_ENTERPRISE=P-3DE34567FG89012HI
PAYPAL_PRODUCT_ID=PROD_TERO_VOICE
```

---

## Usage Examples

### Create a Subscription

```javascript
import subscriptionManager from '@/services/paypal/subscriptionManager.js';

const subscription = await subscriptionManager.createSubscription(
  'customer_123',
  'PROFESSIONAL',
  {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com',
    returnUrl: 'https://terovoice.com/success',
    cancelUrl: 'https://terovoice.com/cancel'
  }
);

console.log('Subscription ID:', subscription.subscriptionId);
console.log('Status:', subscription.status);
console.log('Approval URL:', subscription.approvalUrl);
// Output:
// Subscription ID: I-ABC123DEF456
// Status: APPROVAL_PENDING
// Approval URL: https://www.paypal.com/subscribe?token=I-ABC123DEF456
```

### Get Subscription Details

```javascript
const subscription = await subscriptionManager.getSubscription('I-ABC123DEF456');

console.log('Status:', subscription.status);
console.log('Plan ID:', subscription.planId);
console.log('Next Billing:', subscription.nextBillingTime);
// Output:
// Status: ACTIVE
// Plan ID: P-1AB12345CD67890EF
// Next Billing: 2026-02-12T10:00:00Z
```

### Cancel Subscription

```javascript
const result = await subscriptionManager.cancelSubscription(
  'I-ABC123DEF456',
  'Customer requested cancellation'
);

console.log('Status:', result.status);
console.log('Cancelled At:', result.cancelledAt);
// Output:
// Status: CANCELLED
// Cancelled At: 2026-01-12T10:30:00Z
```

### Update Subscription (Plan Change)

```javascript
const updated = await subscriptionManager.updateSubscription(
  'I-ABC123DEF456',
  'ENTERPRISE'
);

console.log('New Plan:', updated.newPlanId);
console.log('New Price:', updated.newPrice);
// Output:
// New Plan: ENTERPRISE
// New Price: 799
```

### Create Customer from Subscription

```javascript
import customerManager from '@/services/paypal/customerManager.js';

const customer = await customerManager.createCustomerFromSubscription({
  subscriptionId: 'I-ABC123DEF456',
  customerId: 'customer_123',
  planId: 'PROFESSIONAL',
  price: 499
});

console.log('Customer ID:', customer.id);
console.log('Status:', customer.status);
console.log('Email:', customer.email);
// Output:
// Customer ID: cust_abc123def456
// Status: ACTIVE
// Email: john@example.com
```

### Track Subscription Status

```javascript
import subscriptionTracker from '@/services/paypal/subscriptionTracker.js';

// Get current status from PayPal
const status = await subscriptionTracker.getCurrentStatus('I-ABC123DEF456');
console.log('Current Status:', status);
// Output: Current Status: ACTIVE

// Check if active
const isActive = await subscriptionTracker.isSubscriptionActive('I-ABC123DEF456');
console.log('Is Active:', isActive);
// Output: Is Active: true

// Get status history
const history = await subscriptionTracker.getStatusHistory('I-ABC123DEF456');
console.log('Status History:', history);
// Output: [
//   { newStatus: 'ACTIVE', createdAt: '2026-01-12T10:00:00Z', ... },
//   { newStatus: 'APPROVAL_PENDING', createdAt: '2026-01-12T09:00:00Z', ... }
// ]

// Sync with PayPal
const synced = await subscriptionTracker.syncSubscriptionStatus('I-ABC123DEF456');
console.log('Synced:', synced.synced);
// Output: Synced: true
```

---

## Error Handling

### Common Errors

#### Authentication Error
```
Error: PayPal authentication failed
```
**Solution**: Check `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are correct

#### Invalid Plan ID
```
Error: Invalid plan ID: INVALID_PLAN
```
**Solution**: Use one of: `SOLO_PRO`, `PROFESSIONAL`, `ENTERPRISE`

#### Subscription Not Found
```
Error: Failed to get subscription: RESOURCE_NOT_FOUND
```
**Solution**: Check subscription ID is correct

#### Webhook Signature Invalid
```
Error: Webhook signature verification failed
```
**Solution**: Check `PAYPAL_WEBHOOK_ID` is correct

### Error Response Format

All errors include:
- `message`: Human-readable error message
- `status`: HTTP status code
- `details`: Array of detailed error information
- `paypalError`: Original PayPal API error response

```javascript
try {
  await subscriptionManager.getSubscription('invalid-id');
} catch (error) {
  console.log('Message:', error.message);
  console.log('Status:', error.status);
  console.log('Details:', error.details);
  console.log('PayPal Error:', error.paypalError);
}
```

---

## Testing with Sandbox

### Sandbox Credentials

Use these for testing (never use production credentials in development):

```bash
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_CLIENT_ID=sandbox_client_id
PAYPAL_CLIENT_SECRET=sandbox_client_secret
```

### Test Subscriptions

Create test subscriptions in sandbox:

```javascript
const testSub = await subscriptionManager.createSubscription(
  'test_customer_123',
  'PROFESSIONAL',
  {
    firstName: 'Test',
    lastName: 'User',
    email: 'test@example.com'
  }
);

console.log('Test Subscription:', testSub.subscriptionId);
```

### Webhook Testing

Use PayPal's webhook simulator:
1. Go to https://developer.paypal.com/dashboard/
2. Navigate to Webhooks
3. Click "Send a test webhook"
4. Select event type (e.g., BILLING.SUBSCRIPTION.CREATED)
5. Click "Send"

Your webhook endpoint will receive the test event.

---

## Production Deployment

### Before Going Live

1. **Test Thoroughly**
   - Test all subscription operations in sandbox
   - Test webhook processing
   - Test error handling
   - Test customer onboarding flow

2. **Switch to Production**
   - Get production PayPal credentials
   - Create production billing plans
   - Create production webhook
   - Update `.env` with production values

3. **Security Checklist**
   - ✅ Never commit `.env` to Git
   - ✅ Use environment variables on VPS
   - ✅ Verify webhook signatures
   - ✅ Log all API calls (without secrets)
   - ✅ Monitor for errors
   - ✅ Set up alerts

4. **Monitoring**
   - Monitor webhook processing
   - Monitor API response times
   - Monitor error rates
   - Monitor subscription status changes

### Production Environment Variables

On your VPS, set these environment variables (never in `.env` file):

```bash
export PAYPAL_CLIENT_ID=production_client_id
export PAYPAL_CLIENT_SECRET=production_client_secret
export PAYPAL_ENVIRONMENT=production
export PAYPAL_WEBHOOK_ID=production_webhook_id
export PAYPAL_PLAN_ID_SOLO_PRO=production_plan_id
export PAYPAL_PLAN_ID_PROFESSIONAL=production_plan_id
export PAYPAL_PLAN_ID_ENTERPRISE=production_plan_id
export PAYPAL_PRODUCT_ID=PROD_TERO_VOICE
```

---

## Troubleshooting

### Issue: "No response from PayPal"

**Cause**: Network connectivity issue or PayPal API is down

**Solution**:
1. Check internet connection
2. Check PayPal API status: https://status.paypal.com/
3. Check firewall rules
4. Retry with exponential backoff

### Issue: "Token expired"

**Cause**: OAuth token expired

**Solution**: Automatic - the client will refresh the token on next request

### Issue: Webhook not received

**Cause**: Webhook URL not accessible or webhook ID incorrect

**Solution**:
1. Verify webhook URL is public and accessible
2. Check webhook ID in `.env`
3. Test webhook using PayPal simulator
4. Check firewall rules

### Issue: Subscription status not updating

**Cause**: Webhook not processed or status not synced

**Solution**:
1. Check webhook logs
2. Manually sync: `await subscriptionTracker.syncSubscriptionStatus(id)`
3. Check PayPal dashboard for subscription status

---

## API Reference

### PayPalAPIClient

#### Constructor
```javascript
new PayPalAPIClient(clientId, clientSecret, environment)
```

#### Methods

**Subscriptions**
- `createSubscription(data)` - Create subscription
- `getSubscription(id)` - Get subscription details
- `cancelSubscription(id, reason)` - Cancel subscription
- `updateSubscription(id, updates)` - Update subscription
- `listSubscriptions(filters)` - List subscriptions

**Plans**
- `createPlan(data)` - Create billing plan
- `getPlan(id)` - Get plan details
- `updatePlan(id, updates)` - Update plan

**Webhooks**
- `createWebhook(data)` - Create webhook
- `getWebhook(id)` - Get webhook details
- `updateWebhook(id, updates)` - Update webhook
- `getWebhookEvents(id, filters)` - Get webhook events
- `verifyWebhookSignature(...)` - Verify webhook signature

---

## Performance Considerations

### Token Caching
- Tokens are cached and reused until 5 minutes before expiry
- Reduces authentication overhead
- Automatic refresh on expiry

### Request Timeouts
- Default timeout: 10 seconds
- Configurable per request
- Automatic retry on timeout

### Rate Limiting
- PayPal allows 100 requests per second
- Implement queue if needed
- Monitor rate limit headers

---

## Security Best Practices

1. **Never commit credentials**
   - Use `.env` locally (in `.gitignore`)
   - Use environment variables on VPS
   - Use secrets manager in production

2. **Verify webhook signatures**
   - Always verify before processing
   - Use timing-safe comparison
   - Log verification failures

3. **Log securely**
   - Never log full credentials
   - Never log full webhook payloads
   - Log only necessary information

4. **Use HTTPS**
   - Webhook URL must be HTTPS
   - All API calls use HTTPS
   - Certificate must be valid

5. **Monitor for fraud**
   - Monitor subscription patterns
   - Alert on unusual activity
   - Implement rate limiting

---

## Next Steps

1. **Get Sandbox Credentials**
   - Go to https://developer.paypal.com/dashboard/
   - Create app and get credentials
   - Add to `.env`

2. **Create Billing Plans**
   - Create three plans in PayPal dashboard
   - Copy plan IDs to `.env`

3. **Create Webhook**
   - Create webhook in PayPal dashboard
   - Set URL to `https://terovoice.com/api/webhooks/paypal`
   - Copy webhook ID to `.env`

4. **Test Integration**
   - Run test subscriptions
   - Verify webhook processing
   - Test error handling

5. **Deploy to Production**
   - Get production credentials
   - Update environment variables
   - Monitor for issues

---

## Support

For issues or questions:
1. Check PayPal API documentation: https://developer.paypal.com/docs/
2. Check webhook logs
3. Test with PayPal webhook simulator
4. Review error messages and details

---

**Status**: Ready for Testing
**Last Updated**: January 12, 2026
**Next Review**: After sandbox testing complete
