# PayPal Webhook Processing Guide

Complete guide to PayPal webhook handling, signature verification, and event processing.

---

## Overview

The webhook system handles all PayPal events including:
- Subscription lifecycle events (created, activated, cancelled, suspended)
- Payment events (completed, denied, refunded)
- Billing events (updated, renewed)

Key features:
- **Signature Verification**: Validates all webhooks are from PayPal
- **Idempotent Processing**: Prevents duplicate processing of the same event
- **Automatic Retry**: Exponential backoff retry for failed webhooks
- **Performance Monitoring**: Tracks processing time and alerts on slowdowns
- **Error Recovery**: Comprehensive error handling and logging

---

## Setup

### 1. Configure PayPal Webhook

In PayPal Developer Dashboard:

1. Go to **Accounts** → **Webhooks**
2. Create new webhook endpoint:
   - **URL**: `https://yourdomain.com/api/webhooks/paypal`
   - **Events**: Select all subscription and payment events
3. Copy the **Webhook ID** to your `.env`:

```bash
PAYPAL_WEBHOOK_ID=WH_xxxxxxxxxxxxx
PAYPAL_WEBHOOK_SECRET=your_webhook_secret
```

### 2. Register Webhook Endpoint

In your Express app:

```javascript
import paypalWebhookRouter from '@/api/webhooks/paypal.js';

app.use('/api/webhooks/paypal', paypalWebhookRouter);
```

### 3. Verify Configuration

Test the health endpoint:

```bash
curl https://yourdomain.com/api/webhooks/paypal/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "paypal-webhook-receiver",
  "timestamp": "2026-01-12T10:30:00Z"
}
```

---

## Webhook Events

### Subscription Events

#### BILLING.SUBSCRIPTION.CREATED
Fired when customer initiates subscription (before approval).

```javascript
{
  "event_type": "BILLING.SUBSCRIPTION.CREATED",
  "resource": {
    "id": "I-ABC123XYZ",
    "status": "APPROVAL_PENDING",
    "subscriber": {
      "name": { "given_name": "John", "surname": "Doe" },
      "email_address": "john@example.com",
      "payer_id": "PAYERID123"
    }
  }
}
```

**Handler**: `handleSubscriptionCreated()`  
**Status Change**: `CREATED` → `APPROVAL_PENDING`

#### BILLING.SUBSCRIPTION.ACTIVATED
Fired when customer approves subscription.

```javascript
{
  "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
  "resource": {
    "id": "I-ABC123XYZ",
    "status": "ACTIVE",
    "subscriber": { "payer_id": "PAYERID123" }
  }
}
```

**Handler**: `handleSubscriptionActivated()`  
**Status Change**: `APPROVAL_PENDING` → `ACTIVE`  
**Side Effects**: Updates customer status to ACTIVE

#### BILLING.SUBSCRIPTION.CANCELLED
Fired when subscription is cancelled.

```javascript
{
  "event_type": "BILLING.SUBSCRIPTION.CANCELLED",
  "resource": {
    "id": "I-ABC123XYZ",
    "status": "CANCELLED",
    "status_update_note": "Customer requested cancellation"
  }
}
```

**Handler**: `handleSubscriptionCancelled()`  
**Status Change**: `ACTIVE` → `CANCELLED`  
**Side Effects**: Updates customer status to CANCELLED

#### BILLING.SUBSCRIPTION.SUSPENDED
Fired when subscription is suspended (e.g., payment failure).

```javascript
{
  "event_type": "BILLING.SUBSCRIPTION.SUSPENDED",
  "resource": {
    "id": "I-ABC123XYZ",
    "status": "SUSPENDED",
    "status_update_note": "Payment failed"
  }
}
```

**Handler**: `handleSubscriptionSuspended()`  
**Status Change**: `ACTIVE` → `SUSPENDED`  
**Side Effects**: Updates customer status to SUSPENDED

#### BILLING.SUBSCRIPTION.UPDATED
Fired when subscription is updated (e.g., plan change).

```javascript
{
  "event_type": "BILLING.SUBSCRIPTION.UPDATED",
  "resource": {
    "id": "I-ABC123XYZ",
    "plan_id": "plan_professional",
    "status": "ACTIVE"
  }
}
```

**Handler**: `handleSubscriptionUpdated()`  
**Status Change**: Current → `UPDATED`

### Payment Events

#### PAYMENT.CAPTURE.COMPLETED
Fired when payment is successfully captured.

```javascript
{
  "event_type": "PAYMENT.CAPTURE.COMPLETED",
  "resource": {
    "id": "PAY123456",
    "status": "COMPLETED",
    "amount": { "value": "499.00", "currency_code": "USD" },
    "supplementary_data": {
      "related_ids": { "subscription_id": "I-ABC123XYZ" }
    }
  }
}
```

**Handler**: `handlePaymentCompleted()`  
**Status Change**: `ACTIVE` → `PAYMENT_RECEIVED`

#### PAYMENT.CAPTURE.DENIED
Fired when payment is denied.

```javascript
{
  "event_type": "PAYMENT.CAPTURE.DENIED",
  "resource": {
    "id": "PAY123456",
    "status": "DENIED",
    "status_details": { "reason": "INSUFFICIENT_FUNDS" }
  }
}
```

**Handler**: `handlePaymentDenied()`  
**Status Change**: `ACTIVE` → `PAYMENT_FAILED`

#### PAYMENT.CAPTURE.REFUNDED
Fired when payment is refunded.

```javascript
{
  "event_type": "PAYMENT.CAPTURE.REFUNDED",
  "resource": {
    "id": "REF123456",
    "status": "COMPLETED",
    "amount": { "value": "499.00", "currency_code": "USD" }
  }
}
```

**Handler**: `handlePaymentRefunded()`  
**Status Change**: `PAYMENT_RECEIVED` → `REFUNDED`

---

## Signature Verification

All webhooks are signed by PayPal. Verify signatures to ensure authenticity:

```javascript
import { verifyWebhookSignature } from '@/services/paypal';

// In your webhook endpoint
const isValid = verifyWebhookSignature(
  req.headers,
  req.body,
  process.env.PAYPAL_WEBHOOK_ID
);

if (!isValid) {
  return res.status(401).json({ error: 'Invalid signature' });
}
```

**Required Headers**:
- `paypal-transmission-id` - Unique webhook ID
- `paypal-transmission-time` - Timestamp
- `paypal-cert-url` - Certificate URL
- `paypal-auth-algo` - Algorithm (SHA256withRSA)
- `paypal-transmission-sig` - Signature

---

## Idempotent Processing

Webhooks may be delivered multiple times. The system prevents duplicate processing:

```javascript
import { isWebhookProcessed, markWebhookProcessed } from '@/services/paypal';

// Check if already processed
if (isWebhookProcessed(event.id)) {
  console.log('Webhook already processed');
  return res.status(200).json({ success: true });
}

// Process webhook...

// Mark as processed
markWebhookProcessed(event.id);
```

**How it works**:
- Each webhook has a unique ID from PayPal
- Processed webhooks are stored in memory with 24-hour retention
- Duplicate webhooks are detected and skipped
- Old records are automatically cleaned up

---

## Retry Logic

Failed webhooks are automatically retried with exponential backoff:

```javascript
import { queueWebhookForRetry, getRetryStatus } from '@/services/paypal';

try {
  await processWebhookEvent(event);
} catch (error) {
  // Queue for retry
  await queueWebhookForRetry(event, 0, error);
}
```

**Retry Configuration**:
- **Max Retries**: 5 attempts
- **Initial Delay**: 1 second
- **Max Delay**: 1 minute
- **Backoff**: Exponential (2x multiplier)
- **Jitter**: ±10% to prevent thundering herd

**Retry Schedule**:
1. Attempt 1: Immediate
2. Attempt 2: ~1 second delay
3. Attempt 3: ~2 second delay
4. Attempt 4: ~4 second delay
5. Attempt 5: ~8 second delay
6. Attempt 6: ~16 second delay (max 60s)

**Check Retry Status**:

```javascript
const status = getRetryStatus('webhook_id');
console.log(status);
// {
//   webhookId: 'webhook_id',
//   retryCount: 2,
//   scheduledTime: Date,
//   delay: 1000,
//   error: 'Connection timeout',
//   createdAt: Date,
//   attempts: [...]
// }
```

---

## Performance Monitoring

The system monitors webhook processing performance:

```javascript
import { monitorPerformance } from '@/services/paypal';

const processingTime = 15000; // 15 seconds
const perf = monitorPerformance(processingTime);

console.log(perf);
// {
//   processingTimeMs: 15000,
//   targetMs: 30000,
//   percentOfTarget: 50,
//   withinTarget: true,
//   warning: false,
//   critical: false
// }
```

**Performance Targets**:
- **Target**: 30 seconds (PayPal timeout)
- **Warning**: >80% of target (24 seconds)
- **Critical**: >100% of target (>30 seconds)

**Get Statistics**:

```javascript
import { getRetryStats } from '@/services/paypal';

const stats = getRetryStats();
console.log(stats);
// {
//   totalPending: 5,
//   byRetryCount: { 1: 2, 2: 3 },
//   oldestRetry: Date,
//   newestRetry: Date,
//   averageRetries: 1.6
// }
```

---

## Error Handling

### Common Errors

#### Invalid Signature
```
Error: Invalid webhook signature
Status: 401
Action: Reject webhook, do not process
```

#### Invalid Event Structure
```
Error: Invalid event structure
Status: 400
Action: Reject webhook, log for investigation
```

#### Processing Timeout
```
Error: Processing exceeded 30 seconds
Status: 200 (accepted)
Action: Queue for retry, alert operations
```

#### Database Error
```
Error: Failed to update subscription status
Status: 200 (accepted)
Action: Queue for retry, alert operations
```

### Error Recovery

```javascript
try {
  await processWebhookEvent(event);
} catch (error) {
  console.error('Webhook processing error:', error);

  // Queue for retry
  await queueWebhookForRetry(event, 0, error);

  // Alert operations
  await alertOperations({
    type: 'webhook_error',
    webhookId: event.id,
    error: error.message
  });

  // Return success to PayPal (we'll retry)
  res.status(200).json({ success: true });
}
```

---

## Complete Workflow Example

```javascript
import express from 'express';
import {
  verifyWebhookSignature,
  processWebhookEvent,
  monitorPerformance
} from '@/services/paypal';

const app = express();

app.post('/api/webhooks/paypal', async (req, res) => {
  const startTime = Date.now();

  try {
    // 1. Verify signature
    const isValid = verifyWebhookSignature(
      req.headers,
      JSON.stringify(req.body),
      process.env.PAYPAL_WEBHOOK_ID
    );

    if (!isValid) {
      console.warn('Invalid webhook signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // 2. Process event
    const event = req.body;
    console.log(`Processing webhook: ${event.event_type}`);

    const result = await processWebhookEvent(event);

    // 3. Monitor performance
    const processingTime = Date.now() - startTime;
    const perf = monitorPerformance(processingTime);

    if (perf.critical) {
      console.error(`CRITICAL: Webhook processing took ${processingTime}ms`);
      // Alert operations
    }

    // 4. Return success
    res.status(200).json({
      success: true,
      webhookId: event.id,
      processingTime,
      performance: perf
    });

  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

---

## Testing Webhooks

### Using PayPal Webhook Simulator

1. Go to PayPal Developer Dashboard
2. Select your webhook
3. Click "Send a test webhook"
4. Choose event type and send

### Manual Testing

```bash
# Test webhook endpoint
curl -X POST https://yourdomain.com/api/webhooks/paypal \
  -H "Content-Type: application/json" \
  -H "paypal-transmission-id: test-123" \
  -H "paypal-transmission-time: 2026-01-12T10:30:00Z" \
  -H "paypal-cert-url: https://api.paypal.com/cert" \
  -H "paypal-auth-algo: SHA256withRSA" \
  -H "paypal-transmission-sig: test-sig" \
  -d '{
    "id": "WH-TEST123",
    "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
    "resource": {
      "id": "I-TEST123",
      "status": "ACTIVE"
    }
  }'
```

### Local Testing with ngrok

```bash
# Start ngrok tunnel
ngrok http 3000

# Update PayPal webhook URL to ngrok URL
# https://xxxx-xx-xxx-xxx-xx.ngrok.io/api/webhooks/paypal

# Send test webhook from PayPal dashboard
```

---

## Debugging

### View Webhook Logs

```javascript
// Enable detailed logging
process.env.DEBUG = 'paypal:*';

// View webhook processing logs
console.log('Webhook received:', event.id);
console.log('Event type:', event.event_type);
console.log('Processing time:', processingTime);
```

### Check Retry Queue

```javascript
import { getPendingRetries, getRetryStats } from '@/services/paypal';

// View pending retries
const pending = getPendingRetries();
console.log('Pending retries:', pending);

// View retry statistics
const stats = getRetryStats();
console.log('Retry stats:', stats);
```

### Verify Webhook Delivery

In PayPal Developer Dashboard:
1. Go to **Webhooks** → Your webhook
2. Click **View Webhook Deliveries**
3. Check delivery status and response

---

## Best Practices

1. **Always verify signatures** - Never trust unsigned webhooks
2. **Implement idempotency** - Handle duplicate webhooks gracefully
3. **Return quickly** - Process webhooks asynchronously if needed
4. **Monitor performance** - Alert on slow webhook processing
5. **Implement retry logic** - Handle transient failures automatically
6. **Log everything** - Maintain detailed logs for debugging
7. **Test thoroughly** - Use PayPal sandbox for testing
8. **Handle errors gracefully** - Never crash on webhook errors

---

## Troubleshooting

### Webhooks Not Received

1. Check webhook URL is publicly accessible
2. Verify webhook is enabled in PayPal dashboard
3. Check firewall/security group allows PayPal IPs
4. Review PayPal webhook delivery logs

### Signature Verification Fails

1. Verify `PAYPAL_WEBHOOK_ID` is correct
2. Verify `PAYPAL_WEBHOOK_SECRET` is correct
3. Check webhook headers are not modified
4. Ensure raw body is used for verification

### Processing Timeouts

1. Optimize database queries
2. Implement async processing
3. Use connection pooling
4. Monitor system resources

### Duplicate Processing

1. Verify idempotency check is working
2. Check webhook retention time
3. Review processed webhook logs
4. Ensure webhook ID is unique

---

## Next Steps

1. **Integrate with Member Portal** - Display subscription status
2. **Add Email Notifications** - Send confirmation emails
3. **Build Analytics** - Track subscription metrics
4. **Implement Billing** - Handle plan upgrades/downgrades

---

**Last Updated**: January 12, 2026  
**Status**: Production Ready

