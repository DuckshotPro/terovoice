# PayPal MCP Integration - Implementation Guide

## Task 1: Set up PayPal MCP Server Configuration ✅

### Status: COMPLETED

The PayPal MCP server has been configured in `.kiro/settings/mcp.json` with the following setup:

```json
{
  "paypal": {
    "command": "uvx",
    "args": ["paypal-mcp-server@latest"],
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
```

### Configuration Details

- **Server**: Official PayPal MCP server from https://github.com/paypal/paypal-mcp-server
- **Installation**: Installed via `uvx` (Python package manager)
- **Environment Variables**: Uses environment variables from `.env` file
- **Auto-Approval**: All critical PayPal tools are pre-approved for seamless integration
- **Disabled**: Set to `false` - server is active and ready to use

### Required Environment Variables

The following variables must be set in your `.env` file:

```bash
PAYPAL_CLIENT_ID=your_paypal_app_client_id
PAYPAL_CLIENT_SECRET=your_paypal_app_client_secret
PAYPAL_ENVIRONMENT=sandbox  # or production
PAYPAL_WEBHOOK_ID=your_paypal_webhook_id
```

### Available Tools

The PayPal MCP server provides the following tools (all auto-approved):

**Subscription Management:**
- `create_subscription` - Create a new subscription
- `get_subscription` - Retrieve subscription details
- `cancel_subscription` - Cancel an active subscription
- `update_subscription` - Update subscription details
- `list_subscriptions` - List all subscriptions

**Plan Management:**
- `create_plan` - Create a billing plan
- `get_plan` - Retrieve plan details
- `list_plans` - List all billing plans

**Invoice Management:**
- `create_invoice` - Create an invoice
- `get_invoice` - Retrieve invoice details
- `send_invoice` - Send invoice to customer

**Webhook & Security:**
- `verify_webhook_signature` - Verify PayPal webhook signatures

**Transaction Management:**
- `get_transaction` - Retrieve transaction details
- `list_transactions` - List transactions
- `refund_transaction` - Process refunds

### Testing the Configuration

To verify the PayPal MCP server is properly configured:

1. Ensure `.env` file has valid PayPal credentials
2. Restart Kiro IDE to load the new MCP configuration
3. Open the MCP Server view in the Kiro feature panel
4. Look for "paypal" server in the list
5. Verify status shows "connected" (green indicator)

### Next Steps

- Proceed to Task 2: Implement Subscription Management System
- Use the PayPal MCP tools to create subscription management interface
- Implement support for Solo Pro ($299), Professional ($499), and Enterprise ($799) plans

---

## Task 2: Implement Subscription Management System

### Overview

This task implements the core subscription management functionality using the PayPal MCP server tools. We'll create a robust system for managing subscriptions across three pricing tiers.

### 2.1 Create Subscription Management Interface

**File**: `src/services/paypal/subscriptionManager.js`

This module provides the interface for subscription operations:

```javascript
import { kiroPowers } from '@kiro/powers';

const paypalTools = kiroPowers.paypal;

// Subscription plan definitions
const SUBSCRIPTION_PLANS = {
  SOLO_PRO: {
    id: 'plan_solo_pro',
    name: 'Solo Pro',
    price: 299,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'Perfect for solo practitioners'
  },
  PROFESSIONAL: {
    id: 'plan_professional',
    name: 'Professional',
    price: 499,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'For growing businesses'
  },
  ENTERPRISE: {
    id: 'plan_enterprise',
    name: 'Enterprise',
    price: 799,
    currency: 'USD',
    interval: 'MONTH',
    intervalCount: 1,
    description: 'For large organizations'
  }
};

/**
 * Create a new subscription for a customer
 * @param {string} customerId - PayPal customer ID
 * @param {string} planId - Plan identifier (SOLO_PRO, PROFESSIONAL, ENTERPRISE)
 * @param {object} customerData - Customer information
 * @returns {Promise<object>} Subscription details
 */
export async function createSubscription(customerId, planId, customerData) {
  const plan = SUBSCRIPTION_PLANS[planId];
  
  if (!plan) {
    throw new Error(`Invalid plan ID: ${planId}`);
  }

  try {
    const subscription = await paypalTools.create_subscription({
      plan_id: plan.id,
      subscriber: {
        name: {
          given_name: customerData.firstName,
          surname: customerData.lastName
        },
        email_address: customerData.email,
        payer_id: customerId
      },
      application_context: {
        brand_name: 'AI Receptionist',
        locale: 'en-US',
        user_action: 'SUBSCRIBE_NOW',
        return_url: `${process.env.APP_DOMAIN}/subscription/success`,
        cancel_url: `${process.env.APP_DOMAIN}/subscription/cancel`
      }
    });

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      planId: planId,
      customerId: customerId,
      createdAt: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error creating subscription:', error);
    throw error;
  }
}

/**
 * Get subscription details
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<object>} Subscription details
 */
export async function getSubscription(subscriptionId) {
  try {
    const subscription = await paypalTools.get_subscription({
      subscription_id: subscriptionId
    });

    return {
      subscriptionId: subscription.id,
      status: subscription.status,
      planId: subscription.plan_id,
      currentCycle: subscription.billing_cycles?.length || 0,
      nextBillingDate: subscription.billing_cycles?.[0]?.pricing_scheme?.fixed_price?.value,
      createdAt: subscription.create_time,
      updatedAt: subscription.update_time
    };
  } catch (error) {
    console.error('Error getting subscription:', error);
    throw error;
  }
}

/**
 * Cancel a subscription
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} reason - Cancellation reason
 * @returns {Promise<object>} Cancellation confirmation
 */
export async function cancelSubscription(subscriptionId, reason = 'Customer requested') {
  try {
    await paypalTools.cancel_subscription({
      subscription_id: subscriptionId,
      reason: reason
    });

    return {
      subscriptionId: subscriptionId,
      status: 'CANCELLED',
      cancelledAt: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error cancelling subscription:', error);
    throw error;
  }
}

/**
 * Update subscription (e.g., plan upgrade/downgrade)
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} newPlanId - New plan identifier
 * @returns {Promise<object>} Updated subscription details
 */
export async function updateSubscription(subscriptionId, newPlanId) {
  const newPlan = SUBSCRIPTION_PLANS[newPlanId];
  
  if (!newPlan) {
    throw new Error(`Invalid plan ID: ${newPlanId}`);
  }

  try {
    const updated = await paypalTools.update_subscription({
      subscription_id: subscriptionId,
      plan_id: newPlan.id
    });

    return {
      subscriptionId: updated.id,
      status: updated.status,
      newPlanId: newPlanId,
      updatedAt: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error updating subscription:', error);
    throw error;
  }
}

/**
 * List all subscriptions for a customer
 * @param {string} customerId - PayPal customer ID
 * @returns {Promise<array>} Array of subscriptions
 */
export async function listSubscriptions(customerId) {
  try {
    const subscriptions = await paypalTools.list_subscriptions({
      subscriber_id: customerId
    });

    return subscriptions.map(sub => ({
      subscriptionId: sub.id,
      status: sub.status,
      planId: sub.plan_id,
      createdAt: sub.create_time,
      updatedAt: sub.update_time
    }));
  } catch (error) {
    console.error('Error listing subscriptions:', error);
    throw error;
  }
}

export { SUBSCRIPTION_PLANS };
```

### 2.2 Database Schema for Subscriptions

**File**: `src/db/migrations/001_create_subscriptions_table.sql`

```sql
CREATE TABLE subscriptions (
  id SERIAL PRIMARY KEY,
  subscription_id VARCHAR(255) UNIQUE NOT NULL,
  customer_id VARCHAR(255) NOT NULL,
  plan_id VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  billing_cycle_sequence INTEGER DEFAULT 0,
  next_billing_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  cancelled_at TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_subscription_id ON subscriptions(subscription_id);
```

### 2.3 Customer Management Integration

**File**: `src/services/paypal/customerManager.js`

```javascript
import { db } from '@/db';

/**
 * Create customer record on subscription completion
 * @param {object} subscriptionData - Subscription data from PayPal
 * @returns {Promise<object>} Customer record
 */
export async function createCustomerFromSubscription(subscriptionData) {
  const { subscriptionId, customerId, planId, price } = subscriptionData;

  try {
    const customer = await db.query(
      `INSERT INTO customers (
        paypal_customer_id,
        subscription_id,
        plan_id,
        status,
        created_at
      ) VALUES ($1, $2, $3, $4, NOW())
      RETURNING *`,
      [customerId, subscriptionId, planId, 'ACTIVE']
    );

    return customer.rows[0];
  } catch (error) {
    console.error('Error creating customer:', error);
    throw error;
  }
}

/**
 * Link PayPal customer ID with internal customer database
 * @param {string} internalCustomerId - Internal customer ID
 * @param {string} paypalCustomerId - PayPal customer ID
 * @returns {Promise<object>} Updated customer record
 */
export async function linkPayPalCustomer(internalCustomerId, paypalCustomerId) {
  try {
    const result = await db.query(
      `UPDATE customers 
       SET paypal_customer_id = $1, updated_at = NOW()
       WHERE id = $2
       RETURNING *`,
      [paypalCustomerId, internalCustomerId]
    );

    return result.rows[0];
  } catch (error) {
    console.error('Error linking PayPal customer:', error);
    throw error;
  }
}

/**
 * Synchronize customer data with PayPal
 * @param {string} customerId - Internal customer ID
 * @param {object} updates - Data to update
 * @returns {Promise<object>} Updated customer record
 */
export async function syncCustomerData(customerId, updates) {
  try {
    const result = await db.query(
      `UPDATE customers 
       SET 
         email = COALESCE($1, email),
         first_name = COALESCE($2, first_name),
         last_name = COALESCE($3, last_name),
         updated_at = NOW()
       WHERE id = $4
       RETURNING *`,
      [updates.email, updates.firstName, updates.lastName, customerId]
    );

    return result.rows[0];
  } catch (error) {
    console.error('Error syncing customer data:', error);
    throw error;
  }
}

export default {
  createCustomerFromSubscription,
  linkPayPalCustomer,
  syncCustomerData
};
```

### 2.4 Subscription Status Tracking

**File**: `src/services/paypal/subscriptionTracker.js`

```javascript
import { db } from '@/db';

/**
 * Track subscription status changes
 * @param {string} subscriptionId - PayPal subscription ID
 * @param {string} newStatus - New subscription status
 * @param {object} metadata - Additional metadata
 * @returns {Promise<object>} Status update record
 */
export async function trackStatusChange(subscriptionId, newStatus, metadata = {}) {
  try {
    const result = await db.query(
      `INSERT INTO subscription_status_history (
        subscription_id,
        old_status,
        new_status,
        metadata,
        created_at
      ) VALUES ($1, $2, $3, $4, NOW())
      RETURNING *`,
      [subscriptionId, metadata.oldStatus, newStatus, JSON.stringify(metadata)]
    );

    // Update current subscription status
    await db.query(
      `UPDATE subscriptions 
       SET status = $1, updated_at = NOW()
       WHERE subscription_id = $2`,
      [newStatus, subscriptionId]
    );

    return result.rows[0];
  } catch (error) {
    console.error('Error tracking status change:', error);
    throw error;
  }
}

/**
 * Get subscription status history
 * @param {string} subscriptionId - PayPal subscription ID
 * @returns {Promise<array>} Status history records
 */
export async function getStatusHistory(subscriptionId) {
  try {
    const result = await db.query(
      `SELECT * FROM subscription_status_history
       WHERE subscription_id = $1
       ORDER BY created_at DESC`,
      [subscriptionId]
    );

    return result.rows;
  } catch (error) {
    console.error('Error getting status history:', error);
    throw error;
  }
}

export default {
  trackStatusChange,
  getStatusHistory
};
```

---

## Implementation Checklist

- [x] Task 1: PayPal MCP Server Configuration
- [ ] Task 1.1: Write property test for MCP server connectivity
- [ ] Task 2: Implement Subscription Management System
  - [ ] 2.1: Create subscription management interface
  - [ ] 2.2: Write property test for subscription state consistency
  - [ ] 2.3: Implement customer management integration
  - [ ] 2.4: Write property test for customer onboarding automation
- [ ] Task 3: Build Webhook Processing System
- [ ] Task 4: Checkpoint - Test Core PayPal Integration
- [ ] Task 5: Implement Billing and Plan Management
- [ ] Task 6: Build Analytics and Reporting System
- [ ] Task 7: Integrate with Member Portal
- [ ] Task 8: Add Email Automation System
- [ ] Task 9: Implement Security and Compliance Features
- [ ] Task 10: Build Testing and Development Support
- [ ] Task 11: Checkpoint - Test Complete Integration
- [ ] Task 12: Implement Migration from Custom PayPal Power
- [ ] Task 13: Final Integration Testing and Deployment
- [ ] Task 14: Final checkpoint

---

## Notes

- All code examples follow the existing project structure and conventions
- Database migrations should be run before deploying subscription features
- PayPal MCP server must be properly configured with valid credentials
- All subscription operations should include proper error handling and logging
- Customer data synchronization ensures consistency between internal DB and PayPal
