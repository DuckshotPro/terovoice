# PayPal MCP Integration - Quick Start Guide

Get up and running with PayPal subscription management in 5 minutes.

---

## 1. Setup (1 minute)

### Ensure PayPal Credentials are Set

Add to your `.env` file:
```bash
PAYPAL_CLIENT_ID=your_paypal_app_client_id
PAYPAL_CLIENT_SECRET=your_paypal_app_client_secret
PAYPAL_ENVIRONMENT=sandbox  # or production
PAYPAL_WEBHOOK_ID=your_paypal_webhook_id
```

### Verify MCP Configuration

Check `.kiro/settings/mcp.json` has PayPal server configured:
```json
{
  "paypal": {
    "command": "uvx",
    "args": ["paypal-mcp-server@latest"],
    "disabled": false
  }
}
```

---

## 2. Import Services (1 minute)

```javascript
// In your component or service file
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
  listCustomers
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

---

## 3. Create Your First Subscription (1 minute)

```javascript
// Create a subscription
const subscription = await createSubscription(
  'paypal_customer_123',
  'PROFESSIONAL', // SOLO_PRO, PROFESSIONAL, or ENTERPRISE
  {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com'
  }
);

console.log('Subscription created:', subscription.subscriptionId);
console.log('Approval URL:', subscription.approvalUrl);
```

---

## 4. Create Customer Record (1 minute)

```javascript
// Create customer record
const customer = await createCustomerFromSubscription({
  subscriptionId: subscription.subscriptionId,
  customerId: 'paypal_customer_123',
  planId: 'PROFESSIONAL',
  price: 499
});

console.log('Customer created:', customer.id);
```

---

## 5. Track Status Changes (1 minute)

```javascript
// When webhook arrives, track the status change
await trackStatusChange(
  subscription.subscriptionId,
  'ACTIVE',
  {
    oldStatus: 'APPROVAL_PENDING',
    reason: 'Customer approved subscription',
    source: 'webhook'
  }
);

// Verify subscription is active
const isActive = await isSubscriptionActive(subscription.subscriptionId);
console.log('Subscription active:', isActive);
```

---

## Common Tasks

### Get Subscription Details
```javascript
const details = await getSubscription('I-ABC123XYZ');
console.log(details.status, details.nextBillingAmount);
```

### Upgrade Plan
```javascript
const updated = await updateSubscription('I-ABC123XYZ', 'ENTERPRISE');
console.log('Upgraded to:', updated.newPlanId);
```

### Cancel Subscription
```javascript
const cancelled = await cancelSubscription('I-ABC123XYZ', 'Customer requested');
console.log('Cancelled at:', cancelled.cancelledAt);
```

### Get Plan Details
```javascript
const plan = getPlanDetails('PROFESSIONAL');
console.log(plan.price, plan.features);
```

### Get All Plans
```javascript
const allPlans = getAllPlans();
Object.entries(allPlans).forEach(([key, plan]) => {
  console.log(`${plan.name}: $${plan.price}/month`);
});
```

### Get Customer
```javascript
const customer = await getCustomer('cust_abc123xyz');
console.log(customer.email, customer.status);
```

### Get Subscription Metrics
```javascript
const metrics = await getSubscriptionMetrics('I-ABC123XYZ');
console.log(`Active for ${metrics.daysActive} days`);
console.log(`Status: ${metrics.currentStatus}`);
```

### Get Status Summary
```javascript
const summary = await getStatusSummary();
console.log(`Total subscriptions: ${summary.total}`);
console.log(`Active: ${summary.byStatus.ACTIVE}`);
console.log(`Cancelled: ${summary.byStatus.CANCELLED}`);
```

---

## Complete Workflow Example

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

// 2. Create customer
const customer = await createCustomerFromSubscription({
  subscriptionId: subscription.subscriptionId,
  customerId: 'paypal_customer_123',
  planId: 'PROFESSIONAL',
  price: 499
});

// 3. Send user to PayPal approval
console.log('Redirect to:', subscription.approvalUrl);

// 4. When webhook arrives (from PayPal)
await trackStatusChange(
  subscription.subscriptionId,
  'ACTIVE',
  { oldStatus: 'APPROVAL_PENDING', reason: 'Webhook received' }
);

// 5. Verify and display
const isActive = await isSubscriptionActive(subscription.subscriptionId);
const metrics = await getSubscriptionMetrics(subscription.subscriptionId);

console.log('Subscription active:', isActive);
console.log('Days active:', metrics.daysActive);
console.log('Current status:', metrics.currentStatus);
```

---

## Subscription Plans

| Plan | Price | Best For |
|------|-------|----------|
| Solo Pro | $299/month | Solo practitioners |
| Professional | $499/month | Growing businesses |
| Enterprise | $799/month | Large organizations |

Each plan includes:
- Unlimited minutes
- Voice cloning
- Custom scripts
- Tiered analytics and support

---

## Error Handling

```javascript
try {
  const subscription = await getSubscription('invalid_id');
} catch (error) {
  console.error('Error:', error.message);
  // Handle error appropriately
}
```

---

## Debugging

### Check Subscription Status
```javascript
const status = await getCurrentStatus('I-ABC123XYZ');
console.log('Current status:', status);
```

### View Status History
```javascript
const history = await getStatusHistory('I-ABC123XYZ');
history.forEach(record => {
  console.log(`${record.createdAt}: ${record.oldStatus} → ${record.newStatus}`);
});
```

### Get Status Timeline
```javascript
const timeline = await getStatusTimeline('I-ABC123XYZ');
timeline.forEach(event => {
  console.log(`${event.timestamp}: ${event.status} (${event.reason})`);
});
```

### List All Customers
```javascript
const customers = await listCustomers();
console.log(`Total customers: ${customers.length}`);
customers.forEach(c => {
  console.log(`${c.id}: ${c.status}`);
});
```

---

## Next Steps

1. **Implement Webhook Processing** (Task 3)
   - Create webhook endpoint
   - Verify PayPal signatures
   - Process subscription events

2. **Add Email Notifications** (Task 8)
   - Welcome emails
   - Billing notifications
   - Cancellation confirmations

3. **Integrate with Member Portal** (Task 7)
   - Display subscription status
   - Show billing information
   - Allow plan changes

4. **Build Analytics** (Task 6)
   - Track MRR
   - Calculate churn
   - Generate reports

---

## Documentation

- **Full Usage Guide**: `src/services/paypal/USAGE_GUIDE.md`
- **Implementation Guide**: `.kiro/specs/paypal-mcp-integration/IMPLEMENTATION_GUIDE.md`
- **Progress Tracking**: `PAYPAL_MCP_IMPLEMENTATION_PROGRESS.md`

---

## Support

For issues or questions:
1. Check the usage guide for examples
2. Review the implementation guide for details
3. Check error messages and logs
4. Refer to PayPal MCP server documentation

---

**Ready to go!** Start with the complete workflow example above. 🚀
