# PayPal Services - Usage Guide

Quick reference for using the PayPal subscription management services.

## Installation

All services are available from `src/services/paypal/index.js`:

```javascript
import {
  createSubscription,
  getSubscription,
  cancelSubscription,
  updateSubscription,
  listSubscriptions,
  getPlanDetails,
  getAllPlans,
  SUBSCRIPTION_PLANS
} from '@/services/paypal';

import {
  createCustomerFromSubscription,
  linkPayPalCustomer,
  syncCustomerData,
  getCustomer,
  getCustomerByPayPalId,
  updateCustomerStatus,
  listCustomers,
  deleteCustomer
} from '@/services/paypal';

import {
  trackStatusChange,
  getStatusHistory,
  getCurrentStatus,
  isSubscriptionActive,
  getStatusTimeline,
  getSubscriptionMetrics,
  getSubscriptionsByStatus,
  getStatusSummary
} from '@/services/paypal';
```

## Subscription Management

### Create a Subscription

```javascript
const subscription = await createSubscription(
  'paypal_customer_123',
  'PROFESSIONAL', // SOLO_PRO, PROFESSIONAL, or ENTERPRISE
  {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com'
  }
);

console.log(subscription);
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'APPROVAL_PENDING',
//   planId: 'PROFESSIONAL',
//   customerId: 'paypal_customer_123',
//   createdAt: '2026-01-12T10:30:00Z',
//   approvalUrl: 'https://www.paypal.com/subscribe?token=I-ABC123XYZ'
// }
```

### Get Subscription Details

```javascript
const details = await getSubscription('I-ABC123XYZ');

console.log(details);
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'ACTIVE',
//   planId: 'plan_professional',
//   currentCycle: 1,
//   nextBillingAmount: '499.00',
//   createdAt: '2026-01-12T10:30:00Z',
//   updatedAt: '2026-01-12T10:30:00Z'
// }
```

### Update Subscription (Upgrade/Downgrade)

```javascript
const updated = await updateSubscription(
  'I-ABC123XYZ',
  'ENTERPRISE' // Upgrade to Enterprise plan
);

console.log(updated);
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'ACTIVE',
//   newPlanId: 'ENTERPRISE',
//   newPrice: 799,
//   updatedAt: '2026-01-12T11:00:00Z'
// }
```

### Cancel Subscription

```javascript
const cancelled = await cancelSubscription(
  'I-ABC123XYZ',
  'Customer requested cancellation'
);

console.log(cancelled);
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'CANCELLED',
//   cancelledAt: '2026-01-12T11:30:00Z',
//   reason: 'Customer requested cancellation'
// }
```

### List Subscriptions

```javascript
const subscriptions = await listSubscriptions('paypal_customer_123');

console.log(subscriptions);
// [
//   {
//     subscriptionId: 'I-ABC123XYZ',
//     status: 'ACTIVE',
//     planId: 'PROFESSIONAL',
//     createdAt: '2026-01-12T10:30:00Z',
//     updatedAt: '2026-01-12T10:30:00Z'
//   }
// ]
```

### Get Plan Details

```javascript
const plan = getPlanDetails('PROFESSIONAL');

console.log(plan);
// {
//   id: 'plan_professional',
//   name: 'Professional',
//   price: 499,
//   currency: 'USD',
//   interval: 'MONTH',
//   intervalCount: 1,
//   description: 'For growing businesses',
//   features: [
//     'Unlimited minutes',
//     'Voice cloning',
//     'Custom scripts',
//     'Advanced analytics',
//     'Priority support',
//     'Multi-location support'
//   ]
// }
```

### Get All Plans

```javascript
const allPlans = getAllPlans();

console.log(allPlans);
// {
//   SOLO_PRO: { ... },
//   PROFESSIONAL: { ... },
//   ENTERPRISE: { ... }
// }
```

## Customer Management

### Create Customer from Subscription

```javascript
const customer = await createCustomerFromSubscription({
  subscriptionId: 'I-ABC123XYZ',
  customerId: 'paypal_customer_123',
  planId: 'PROFESSIONAL',
  price: 499
});

console.log(customer);
// {
//   id: 'cust_abc123xyz',
//   paypalCustomerId: 'paypal_customer_123',
//   subscriptionId: 'I-ABC123XYZ',
//   planId: 'PROFESSIONAL',
//   status: 'ACTIVE',
//   createdAt: '2026-01-12T10:30:00Z',
//   updatedAt: '2026-01-12T10:30:00Z'
// }
```

### Link PayPal Customer

```javascript
const linked = await linkPayPalCustomer(
  'cust_abc123xyz', // Internal customer ID
  'paypal_customer_123' // PayPal customer ID
);

console.log(linked);
// {
//   id: 'cust_abc123xyz',
//   paypalCustomerId: 'paypal_customer_123',
//   ...
// }
```

### Sync Customer Data

```javascript
const synced = await syncCustomerData(
  'cust_abc123xyz',
  {
    email: 'newemail@example.com',
    firstName: 'Jane',
    lastName: 'Smith',
    phone: '+1234567890',
    company: 'Acme Corp'
  }
);

console.log(synced);
// {
//   id: 'cust_abc123xyz',
//   email: 'newemail@example.com',
//   firstName: 'Jane',
//   lastName: 'Smith',
//   phone: '+1234567890',
//   company: 'Acme Corp',
//   updatedAt: '2026-01-12T11:00:00Z'
// }
```

### Get Customer

```javascript
const customer = await getCustomer('cust_abc123xyz');

console.log(customer);
// {
//   id: 'cust_abc123xyz',
//   paypalCustomerId: 'paypal_customer_123',
//   subscriptionId: 'I-ABC123XYZ',
//   planId: 'PROFESSIONAL',
//   status: 'ACTIVE',
//   ...
// }
```

### Get Customer by PayPal ID

```javascript
const customer = await getCustomerByPayPalId('paypal_customer_123');

console.log(customer);
// {
//   id: 'cust_abc123xyz',
//   paypalCustomerId: 'paypal_customer_123',
//   ...
// }
```

### Update Customer Status

```javascript
const updated = await updateCustomerStatus(
  'cust_abc123xyz',
  'SUSPENDED'
);

console.log(updated);
// {
//   id: 'cust_abc123xyz',
//   status: 'SUSPENDED',
//   updatedAt: '2026-01-12T11:30:00Z'
// }
```

### List All Customers

```javascript
const customers = await listCustomers();

console.log(customers);
// [
//   {
//     id: 'cust_abc123xyz',
//     paypalCustomerId: 'paypal_customer_123',
//     status: 'ACTIVE',
//     ...
//   },
//   ...
// ]
```

## Subscription Tracking

### Track Status Change

```javascript
const statusRecord = await trackStatusChange(
  'I-ABC123XYZ',
  'ACTIVE',
  {
    oldStatus: 'APPROVAL_PENDING',
    reason: 'Customer approved subscription',
    source: 'webhook'
  }
);

console.log(statusRecord);
// {
//   id: 'status_abc123xyz',
//   subscriptionId: 'I-ABC123XYZ',
//   oldStatus: 'APPROVAL_PENDING',
//   newStatus: 'ACTIVE',
//   metadata: { ... },
//   createdAt: '2026-01-12T10:35:00Z'
// }
```

### Get Status History

```javascript
const history = await getStatusHistory('I-ABC123XYZ');

console.log(history);
// [
//   {
//     id: 'status_abc123xyz',
//     subscriptionId: 'I-ABC123XYZ',
//     oldStatus: 'APPROVAL_PENDING',
//     newStatus: 'ACTIVE',
//     createdAt: '2026-01-12T10:35:00Z'
//   },
//   ...
// ]
```

### Get Current Status

```javascript
const status = await getCurrentStatus('I-ABC123XYZ');

console.log(status);
// 'ACTIVE'
```

### Check if Subscription is Active

```javascript
const isActive = await isSubscriptionActive('I-ABC123XYZ');

console.log(isActive);
// true
```

### Get Status Timeline

```javascript
const timeline = await getStatusTimeline('I-ABC123XYZ');

console.log(timeline);
// [
//   {
//     status: 'ACTIVE',
//     timestamp: '2026-01-12T10:35:00Z',
//     reason: 'Customer approved subscription',
//     details: { ... }
//   },
//   ...
// ]
```

### Get Subscription Metrics

```javascript
const metrics = await getSubscriptionMetrics('I-ABC123XYZ');

console.log(metrics);
// {
//   subscriptionId: 'I-ABC123XYZ',
//   currentStatus: 'ACTIVE',
//   statusCounts: {
//     APPROVAL_PENDING: 1,
//     ACTIVE: 1
//   },
//   totalStatusChanges: 2,
//   daysActive: 30,
//   createdAt: '2026-01-12T10:30:00Z',
//   lastUpdated: '2026-01-12T10:35:00Z'
// }
```

### Get Subscriptions by Status

```javascript
const activeSubscriptions = await getSubscriptionsByStatus('ACTIVE');

console.log(activeSubscriptions);
// ['I-ABC123XYZ', 'I-DEF456UVW', ...]
```

### Get Status Summary

```javascript
const summary = await getStatusSummary();

console.log(summary);
// {
//   total: 42,
//   byStatus: {
//     ACTIVE: 35,
//     CANCELLED: 5,
//     SUSPENDED: 2
//   },
//   timestamp: '2026-01-12T12:00:00Z'
// }
```

## Common Workflows

### Complete Subscription Flow

```javascript
// 1. Create subscription
const subscription = await createSubscription(
  'paypal_customer_123',
  'PROFESSIONAL',
  {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com'
  }
);

// 2. Create customer record
const customer = await createCustomerFromSubscription({
  subscriptionId: subscription.subscriptionId,
  customerId: 'paypal_customer_123',
  planId: 'PROFESSIONAL',
  price: 499
});

// 3. Track status change (when webhook arrives)
await trackStatusChange(
  subscription.subscriptionId,
  'ACTIVE',
  { oldStatus: 'APPROVAL_PENDING', reason: 'Webhook received' }
);

// 4. Verify subscription is active
const isActive = await isSubscriptionActive(subscription.subscriptionId);
console.log('Subscription active:', isActive);
```

### Plan Upgrade Flow

```javascript
// 1. Get current subscription
const current = await getSubscription('I-ABC123XYZ');

// 2. Update to new plan
const updated = await updateSubscription('I-ABC123XYZ', 'ENTERPRISE');

// 3. Track the change
await trackStatusChange(
  'I-ABC123XYZ',
  'ACTIVE',
  {
    oldStatus: 'ACTIVE',
    reason: 'Plan upgraded from PROFESSIONAL to ENTERPRISE',
    oldPlan: 'PROFESSIONAL',
    newPlan: 'ENTERPRISE'
  }
);

// 4. Sync customer data if needed
await syncCustomerData('cust_abc123xyz', {
  email: 'updated@example.com'
});
```

### Cancellation Flow

```javascript
// 1. Cancel subscription
const cancelled = await cancelSubscription(
  'I-ABC123XYZ',
  'Customer requested cancellation'
);

// 2. Update customer status
await updateCustomerStatus('cust_abc123xyz', 'CANCELLED');

// 3. Track the change
await trackStatusChange(
  'I-ABC123XYZ',
  'CANCELLED',
  {
    oldStatus: 'ACTIVE',
    reason: 'Customer requested cancellation'
  }
);
```

## Error Handling

All services throw errors with descriptive messages:

```javascript
try {
  const subscription = await getSubscription('invalid_id');
} catch (error) {
  console.error('Error:', error.message);
  // Handle error appropriately
}
```

## Notes

- All services use mock implementations for development
- Ready to integrate with official PayPal MCP server
- All operations are async and return Promises
- Consistent error handling across all services
- Services maintain data consistency through tracking
