# PayPal Implementation - Code Reference

**Date**: January 12, 2026  
**Purpose**: Quick reference to all PayPal code that's been implemented

⚠️ **SECURITY NOTE**: Never commit credentials to this file. Use `.env` files instead.

## Quick Links to Code Files

### Core Services
1. **Webhook Processing**: `src/services/paypal/webhookProcessor.js`
2. **Webhook Retry**: `src/services/paypal/webhookRetry.js`
3. **Subscription Manager**: `src/services/paypal/subscriptionManager.js`
4. **Customer Manager**: `src/services/paypal/customerManager.js`
5. **Status Tracker**: `src/services/paypal/subscriptionTracker.js`

### API Endpoints
1. **Webhook Endpoint**: `src/api/webhooks/paypal.js`

### Configuration
1. **MCP Configuration**: `.kiro/settings/mcp.json`
2. **Environment Variables**: `.env.example`

### Documentation
1. **Webhook Guide**: `src/services/paypal/WEBHOOK_GUIDE.md`
2. **Usage Guide**: `src/services/paypal/USAGE_GUIDE.md`
3. **Security Guide**: `SECURITY_NOTICE.md`

---

## Code Examples

### Example 1: Using Subscription Manager

```javascript
import {
  createSubscription,
  getSubscription,
  cancelSubscription,
  listSubscriptions,
  getAllPlans,
  SUBSCRIPTION_PLANS
} from '@/services/paypal';

// Get all available plans
const plans = getAllPlans();
console.log('Available plans:', plans);
// Output:
// [
//   { id: 'plan_299', name: 'Solo Pro', price: 299, features: [...] },
//   { id: 'plan_499', name: 'Professional', price: 499, features: [...] },
//   { id: 'plan_799', name: 'Enterprise', price: 799, features: [...] }
// ]

// Create a subscription
const subscription = createSubscription('plan_499', 'customer_123');
console.log('Created subscription:', subscription);
// Output:
// {
//   id: 'SUB_1234567890',
//   plan_id: 'plan_499',
//   customer_id: 'customer_123',
//   status: 'ACTIVE',
//   created_at: '2026-01-12T10:00:00Z',
//   next_billing_date: '2026-02-12T10:00:00Z'
// }

// Get subscription details
const details = getSubscription('SUB_1234567890');
console.log('Subscription details:', details);

// List all subscriptions
const allSubs = listSubscriptions();
console.log('All subscriptions:', allSubs);

// Cancel a subscription
const cancelled = cancelSubscription('SUB_1234567890');
console.log('Cancelled:', cancelled);
```

---

### Example 2: Using Customer Manager

```javascript
import {
  createCustomerFromSubscription,
  getCustomer,
  updateCustomerStatus,
  listCustomers
} from '@/services/paypal';

// Create customer from subscription
const customer = createCustomerFromSubscription({
  subscription_id: 'SUB_1234567890',
  email: 'customer@example.com',
  name: 'John Doe',
  plan_id: 'plan_499'
});
console.log('Created customer:', customer);
// Output:
// {
//   id: 'CUST_1234567890',
//   email: 'customer@example.com',
//   name: 'John Doe',
//   subscription_id: 'SUB_1234567890',
//   plan_id: 'plan_499',
//   status: 'ACTIVE',
//   created_at: '2026-01-12T10:00:00Z'
// }

// Get customer details
const details = getCustomer('CUST_1234567890');
console.log('Customer details:', details);

// Update customer status
const updated = updateCustomerStatus('CUST_1234567890', 'SUSPENDED');
console.log('Updated customer:', updated);

// List all customers
const allCustomers = listCustomers();
console.log('All customers:', allCustomers);
```

---

### Example 3: Using Status Tracker

```javascript
import {
  trackStatusChange,
  getStatusHistory,
  getCurrentStatus,
  isSubscriptionActive,
  getSubscriptionMetrics
} from '@/services/paypal';

// Track a status change
trackStatusChange('SUB_1234567890', 'ACTIVE', 'SUSPENDED', {
  reason: 'Payment failed',
  timestamp: new Date()
});

// Get status history
const history = getStatusHistory('SUB_1234567890');
console.log('Status history:', history);
// Output:
// [
//   { status: 'ACTIVE', timestamp: '2026-01-12T10:00:00Z', reason: 'Created' },
//   { status: 'SUSPENDED', timestamp: '2026-01-12T11:00:00Z', reason: 'Payment failed' }
// ]

// Get current status
const currentStatus = getCurrentStatus('SUB_1234567890');
console.log('Current status:', currentStatus);
// Output: 'SUSPENDED'

// Check if subscription is active
const isActive = isSubscriptionActive('SUB_1234567890');
console.log('Is active:', isActive);
// Output: false

// Get subscription metrics
const metrics = getSubscriptionMetrics('SUB_1234567890');
console.log('Metrics:', metrics);
// Output:
// {
//   total_status_changes: 2,
//   current_status: 'SUSPENDED',
//   active_duration_days: 1,
//   status_timeline: [...]
// }
```

---

### Example 4: Using Webhook Processor

```javascript
import {
  verifyWebhookSignature,
  processWebhookEvent,
  isWebhookProcessed,
  markWebhookProcessed
} from '@/services/paypal';

// Verify webhook signature
const isValid = verifyWebhookSignature(
  webhookBody,
  webhookSignature,
  webhookId
);
console.log('Signature valid:', isValid);

// Check if webhook was already processed
const alreadyProcessed = isWebhookProcessed('WH_1234567890');
console.log('Already processed:', alreadyProcessed);

// Process webhook event
const result = processWebhookEvent({
  id: 'WH_1234567890',
  event_type: 'BILLING.SUBSCRIPTION.CREATED',
  resource: {
    id: 'SUB_1234567890',
    status: 'ACTIVE',
    plan_id: 'plan_499'
  }
});
console.log('Processing result:', result);
// Output:
// {
//   success: true,
//   processed: true,
//   event_type: 'BILLING.SUBSCRIPTION.CREATED',
//   subscription_id: 'SUB_1234567890',
//   customer_id: 'CUST_1234567890'
// }

// Mark webhook as processed
markWebhookProcessed('WH_1234567890');
```

---

### Example 5: Using Webhook Retry

```javascript
import {
  queueWebhookForRetry,
  getRetryStatus,
  getPendingRetries,
  getRetryStats
} from '@/services/paypal';

// Queue a webhook for retry
queueWebhookForRetry('WH_1234567890', new Error('Processing failed'));
console.log('Queued for retry');

// Get retry status
const status = getRetryStatus('WH_1234567890');
console.log('Retry status:', status);
// Output:
// {
//   webhook_id: 'WH_1234567890',
//   queued: true,
//   attempts: 1,
//   max_attempts: 5,
//   next_retry: '2026-01-12T10:05:00Z',
//   last_error: 'Processing failed',
//   created_at: '2026-01-12T10:00:00Z'
// }

// Get all pending retries
const pending = getPendingRetries();
console.log('Pending retries:', pending);
// Output:
// [
//   { webhook_id: 'WH_1234567890', attempts: 1, next_retry: '2026-01-12T10:05:00Z' },
//   { webhook_id: 'WH_0987654321', attempts: 2, next_retry: '2026-01-12T10:10:00Z' }
// ]

// Get retry statistics
const stats = getRetryStats();
console.log('Retry stats:', stats);
// Output:
// {
//   total_queued: 2,
//   total_attempts: 3,
//   average_attempts: 1.5,
//   oldest_retry: '2026-01-12T10:00:00Z',
//   success_rate: 0.95
// }
```

---

### Example 6: Express Webhook Endpoint

```javascript
// In your Express app
import paypalWebhookRouter from '@/api/webhooks/paypal.js';

app.use('/api/webhooks/paypal', paypalWebhookRouter);

// Now PayPal can POST to: https://yourdomain.com/api/webhooks/paypal

// The endpoint will:
// 1. Verify the signature
// 2. Validate the event
// 3. Check for duplicates
// 4. Route to appropriate handler
// 5. Update subscription status
// 6. Update customer status
// 7. Track status changes
// 8. Return 200 OK
// 9. Queue for retry if error
```

---

### Example 7: Webhook Event Types

```javascript
// Supported webhook events:

// Subscription Events
'BILLING.SUBSCRIPTION.CREATED'      // New subscription created
'BILLING.SUBSCRIPTION.ACTIVATED'    // Subscription activated
'BILLING.SUBSCRIPTION.CANCELLED'    // Subscription cancelled
'BILLING.SUBSCRIPTION.SUSPENDED'    // Subscription suspended
'BILLING.SUBSCRIPTION.UPDATED'      // Subscription updated

// Payment Events
'PAYMENT.CAPTURE.COMPLETED'         // Payment completed
'PAYMENT.CAPTURE.DENIED'            // Payment denied
'PAYMENT.CAPTURE.REFUNDED'          // Payment refunded

// Each event is routed to appropriate handler
// Status is updated automatically
// Customer is notified
// Metrics are tracked
```

---

### Example 8: Configuration

```javascript
// .env file
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_ENVIRONMENT=sandbox  // or production
PAYPAL_WEBHOOK_ID=your_webhook_id

// .kiro/settings/mcp.json
{
  "mcpServers": {
    "paypal": {
      "command": "node",
      "args": ["src/mcp/paypal-server.js"],
      "env": {
        "PAYPAL_CLIENT_ID": "${PAYPAL_CLIENT_ID}",
        "PAYPAL_CLIENT_SECRET": "${PAYPAL_CLIENT_SECRET}",
        "PAYPAL_ENVIRONMENT": "${PAYPAL_ENVIRONMENT}",
        "PAYPAL_WEBHOOK_ID": "${PAYPAL_WEBHOOK_ID}"
      },
      "disabled": false,
      "autoApprove": [
        "create_subscription",
        "get_subscription",
        "cancel_subscription",
        "update_subscription",
        "list_subscriptions",
        "create_plan",
        "get_plan",
        "list_plans",
        "create_invoice",
        "get_invoice",
        "send_invoice",
        "verify_webhook_signature",
        "get_transaction",
        "list_transactions",
        "refund_transaction"
      ]
    }
  }
}
```

---

### Example 9: Error Handling

```javascript
import { processWebhookEvent } from '@/services/paypal';

try {
  const result = processWebhookEvent(event);
  
  if (!result.success) {
    console.error('Webhook processing failed:', result.error);
    // Webhook will be queued for retry automatically
  } else {
    console.log('Webhook processed successfully');
  }
} catch (error) {
  console.error('Unexpected error:', error);
  // Error is logged but doesn't crash the app
  // Webhook will be queued for retry
}
```

---

### Example 10: Testing

```javascript
// Test webhook signature verification
import { verifyWebhookSignature } from '@/services/paypal';

const webhookBody = JSON.stringify({
  id: 'WH_123',
  event_type: 'BILLING.SUBSCRIPTION.CREATED'
});

const signature = 'your_signature_here';
const webhookId = 'your_webhook_id';

const isValid = verifyWebhookSignature(webhookBody, signature, webhookId);
console.assert(isValid === true, 'Signature verification failed');

// Test subscription creation
import { createSubscription } from '@/services/paypal';

const sub = createSubscription('plan_499', 'customer_123');
console.assert(sub.id !== undefined, 'Subscription creation failed');
console.assert(sub.status === 'ACTIVE', 'Subscription status incorrect');

// Test customer creation
import { createCustomerFromSubscription } from '@/services/paypal';

const customer = createCustomerFromSubscription({
  subscription_id: sub.id,
  email: 'test@example.com',
  name: 'Test User',
  plan_id: 'plan_499'
});
console.assert(customer.id !== undefined, 'Customer creation failed');
console.assert(customer.subscription_id === sub.id, 'Customer subscription link failed');
```

---

## File Sizes

| File | Lines | Size |
|------|-------|------|
| webhookProcessor.js | 450+ | ~15KB |
| webhookRetry.js | 300+ | ~10KB |
| subscriptionManager.js | 180 | ~6KB |
| customerManager.js | 160 | ~5KB |
| subscriptionTracker.js | 200 | ~7KB |
| paypal.js (endpoint) | 80 | ~3KB |
| index.js (exports) | 50 | ~2KB |
| **Total** | **1,420+** | **~48KB** |

---

## Import Statements

```javascript
// Import everything
import * as paypal from '@/services/paypal';

// Import specific functions
import {
  createSubscription,
  getSubscription,
  cancelSubscription,
  updateSubscription,
  listSubscriptions,
  getAllPlans,
  SUBSCRIPTION_PLANS
} from '@/services/paypal';

// Import webhook functions
import {
  verifyWebhookSignature,
  processWebhookEvent,
  isWebhookProcessed,
  markWebhookProcessed
} from '@/services/paypal';

// Import retry functions
import {
  queueWebhookForRetry,
  getRetryStatus,
  getPendingRetries,
  getRetryStats
} from '@/services/paypal';

// Import customer functions
import {
  createCustomerFromSubscription,
  getCustomer,
  updateCustomerStatus,
  listCustomers
} from '@/services/paypal';

// Import tracking functions
import {
  trackStatusChange,
  getStatusHistory,
  getCurrentStatus,
  isSubscriptionActive,
  getSubscriptionMetrics
} from '@/services/paypal';
```

---

## Constants

```javascript
// Subscription plans
const SUBSCRIPTION_PLANS = {
  SOLO_PRO: {
    id: 'plan_299',
    name: 'Solo Pro',
    price: 299,
    features: ['Up to 1,000 calls/month', 'Basic analytics', 'Email support']
  },
  PROFESSIONAL: {
    id: 'plan_499',
    name: 'Professional',
    price: 499,
    features: ['Up to 5,000 calls/month', 'Advanced analytics', 'Priority support']
  },
  ENTERPRISE: {
    id: 'plan_799',
    name: 'Enterprise',
    price: 799,
    features: ['Unlimited calls', 'Custom analytics', '24/7 phone support']
  }
};

// Webhook events
const WEBHOOK_EVENTS = {
  SUBSCRIPTION_CREATED: 'BILLING.SUBSCRIPTION.CREATED',
  SUBSCRIPTION_ACTIVATED: 'BILLING.SUBSCRIPTION.ACTIVATED',
  SUBSCRIPTION_CANCELLED: 'BILLING.SUBSCRIPTION.CANCELLED',
  SUBSCRIPTION_SUSPENDED: 'BILLING.SUBSCRIPTION.SUSPENDED',
  SUBSCRIPTION_UPDATED: 'BILLING.SUBSCRIPTION.UPDATED',
  PAYMENT_COMPLETED: 'PAYMENT.CAPTURE.COMPLETED',
  PAYMENT_DENIED: 'PAYMENT.CAPTURE.DENIED',
  PAYMENT_REFUNDED: 'PAYMENT.CAPTURE.REFUNDED'
};

// Retry configuration
const RETRY_CONFIG = {
  MAX_ATTEMPTS: 5,
  INITIAL_DELAY: 60000,        // 1 minute
  MAX_DELAY: 3600000,           // 1 hour
  BACKOFF_MULTIPLIER: 2,
  RETENTION_TIME: 86400000      // 24 hours
};

// Webhook retention
const WEBHOOK_RETENTION_TIME = 86400000; // 24 hours
```

---

## Next Steps

### To Use This Code

1. **Import the functions** you need
2. **Call the functions** with appropriate parameters
3. **Handle the results** with try/catch
4. **Test locally** with mock data
5. **Deploy to production** when ready

### To Integrate Real PayPal API

1. **Create PayPal API client** (see NEXT_STEPS_DECISION_GUIDE.md)
2. **Replace mock implementations** with real API calls
3. **Test with PayPal sandbox**
4. **Deploy to production**

### To Write Tests

1. **Use the examples above** as test cases
2. **Test each function** independently
3. **Test error handling**
4. **Test webhook processing**
5. **Test retry logic**

---

## Questions?

Refer to:
1. `src/services/paypal/WEBHOOK_GUIDE.md` - Complete webhook documentation
2. `src/services/paypal/USAGE_GUIDE.md` - Usage examples
3. `SECURITY_NOTICE.md` - Security best practices
4. `PAYPAL_MCP_TROUBLESHOOTING.md` - Troubleshooting guide

---

**Status**: Ready to use  
**Last Updated**: January 12, 2026

