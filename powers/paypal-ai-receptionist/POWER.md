---
name: "paypal-ai-receptionist"
displayName: "PayPal AI Receptionist Billing"
description: "Complete PayPal integration for AI voice agent SaaS with subscription management, webhook processing, and automated billing for $299-$799/month plans."
keywords: ["paypal", "billing", "subscription", "ai-receptionist", "saas", "webhook", "invoice"]
author: "AI Voice Agent SaaS"
---

# PayPal AI Receptionist Billing

## Overview

This power provides complete PayPal integration specifically designed for AI voice agent SaaS businesses. It handles subscription billing, webhook processing, invoice generation, and payment tracking for multi-tier pricing ($299-$799/month plans).

The power integrates PayPal's Subscriptions API, Webhooks API, and Invoicing API to provide a complete billing solution for your AI receptionist service. It supports automated client onboarding, subscription management, and revenue tracking.

Key capabilities include subscription plan management, automated billing cycles, webhook event processing, invoice generation, payment failure handling, and comprehensive reporting for your AI voice agent business.

## Onboarding

### Prerequisites

- PayPal Business Account
- PayPal Developer Account access
- Client ID and Client Secret from PayPal Developer Dashboard
- Webhook endpoint URL (your server that will receive PayPal webhooks)
- SSL certificate for webhook endpoint (required by PayPal)

### PayPal Developer Setup

1. **Create PayPal App:**
   - Go to https://developer.paypal.com/developer/applications/
   - Click "Create App"
   - Choose "Default Application" 
   - Select your business account
   - Enable these features:
     - Subscriptions
     - Webhooks
     - Invoicing
     - Payments

2. **Get API Credentials:**
   - Copy Client ID and Client Secret
   - Note the environment (Sandbox vs Live)

3. **Configure Webhook Endpoint:**
   - Add your webhook URL: `https://yourdomain.com/webhooks/paypal`
   - Subscribe to these events:
     - `BILLING.SUBSCRIPTION.CREATED`
     - `BILLING.SUBSCRIPTION.ACTIVATED`
     - `BILLING.SUBSCRIPTION.CANCELLED`
     - `BILLING.SUBSCRIPTION.SUSPENDED`
     - `BILLING.SUBSCRIPTION.PAYMENT.FAILED`
     - `PAYMENT.SALE.COMPLETED`

### Installation

The PayPal MCP server provides tools for subscription management, webhook processing, and payment tracking.

### Configuration

Set these environment variables in your MCP configuration:

- `PAYPAL_CLIENT_ID`: Your PayPal app client ID
- `PAYPAL_CLIENT_SECRET`: Your PayPal app client secret  
- `PAYPAL_ENVIRONMENT`: "sandbox" or "live"
- `PAYPAL_WEBHOOK_ID`: Your webhook ID from PayPal dashboard

## Common Workflows

### Workflow 1: Create Subscription Plans

**Goal:** Set up your AI receptionist pricing tiers in PayPal

**Steps:**
1. Create product for AI receptionist service
2. Create subscription plans for each tier
3. Configure billing cycles and pricing

**Example:**
```javascript
// Create AI Receptionist product
const product = await paypal.createProduct({
  name: "AI Voice Receptionist Service",
  description: "24/7 AI receptionist for service businesses",
  type: "SERVICE",
  category: "SOFTWARE"
});

// Create subscription plans
const plans = [
  {
    name: "Solo Pro Plan",
    description: "Perfect for individual practitioners",
    price: "299.00",
    currency: "USD",
    interval: "MONTH"
  },
  {
    name: "Pro Plan", 
    description: "Most popular for growing businesses",
    price: "499.00",
    currency: "USD", 
    interval: "MONTH"
  },
  {
    name: "Enterprise Plan",
    description: "For multi-location businesses",
    price: "799.00",
    currency: "USD",
    interval: "MONTH"
  }
];
```

### Workflow 2: Client Subscription Creation

**Goal:** Automatically create subscriptions when clients sign up

**Steps:**
1. Client selects plan on your website
2. Create PayPal subscription
3. Redirect client to PayPal approval
4. Handle approval callback
5. Activate client's AI receptionist service

**Example:**
```javascript
// Create subscription for new client
const subscription = await paypal.createSubscription({
  plan_id: "P-5ML4271244454362WXNWU5NQ", // Pro Plan ID
  subscriber: {
    name: {
      given_name: "Dr. Mike",
      surname: "Thompson"
    },
    email_address: "mike@dentalpractice.com"
  },
  application_context: {
    brand_name: "AI Voice Receptionist",
    return_url: "https://yourdomain.com/subscription/success",
    cancel_url: "https://yourdomain.com/subscription/cancel"
  }
});

// Redirect client to PayPal approval URL
window.location.href = subscription.links.find(link => link.rel === 'approve').href;
```

### Workflow 3: Webhook Processing

**Goal:** Handle PayPal webhook events to update client status

**Steps:**
1. Receive webhook from PayPal
2. Verify webhook signature
3. Process event based on type
4. Update client subscription status
5. Trigger service activation/deactivation

**Example:**
```javascript
// Process subscription activation
if (event.event_type === 'BILLING.SUBSCRIPTION.ACTIVATED') {
  const subscriptionId = event.resource.id;
  const clientEmail = event.resource.subscriber.email_address;
  
  // Activate AI receptionist service
  await activateClientService(clientEmail, subscriptionId);
  
  // Send welcome email with setup instructions
  await sendWelcomeEmail(clientEmail);
}

// Process payment failure
if (event.event_type === 'BILLING.SUBSCRIPTION.PAYMENT.FAILED') {
  const subscriptionId = event.resource.id;
  
  // Suspend service after grace period
  await scheduleServiceSuspension(subscriptionId, gracePeriodDays: 3);
  
  // Send payment failure notification
  await sendPaymentFailureEmail(subscriptionId);
}
```

### Workflow 4: Invoice Generation

**Goal:** Generate invoices for custom services or one-time fees

**Steps:**
1. Create invoice for setup fees or custom work
2. Send invoice to client
3. Track payment status
4. Update client account

**Example:**
```javascript
// Create setup fee invoice
const invoice = await paypal.createInvoice({
  detail: {
    invoice_number: `SETUP-${clientId}-${Date.now()}`,
    invoice_date: new Date().toISOString().split('T')[0],
    currency_code: "USD",
    note: "AI Voice Receptionist Setup Fee",
    payment_term: {
      term_type: "NET_10"
    }
  },
  invoicer: {
    name: {
      business_name: "AI Voice Receptionist"
    },
    email_address: "billing@yourcompany.com"
  },
  primary_recipients: [{
    billing_info: {
      name: {
        given_name: "Dr. Mike",
        surname: "Thompson"
      },
      email_address: "mike@dentalpractice.com"
    }
  }],
  items: [{
    name: "Voice Cloning & Setup",
    description: "Custom voice cloning and AI receptionist setup",
    quantity: "1",
    unit_amount: {
      currency_code: "USD",
      value: "497.00"
    }
  }]
});

// Send invoice
await paypal.sendInvoice(invoice.id);
```

### Workflow 5: Revenue Reporting

**Goal:** Track revenue and subscription metrics

**Steps:**
1. Fetch subscription data
2. Calculate monthly recurring revenue (MRR)
3. Track churn and growth rates
4. Generate revenue reports

**Example:**
```javascript
// Get subscription analytics
const analytics = await paypal.getSubscriptionAnalytics({
  start_date: "2025-01-01",
  end_date: "2025-01-31"
});

// Calculate MRR by plan
const mrrByPlan = {
  solo: analytics.subscriptions.filter(s => s.plan_id === SOLO_PLAN_ID).length * 299,
  pro: analytics.subscriptions.filter(s => s.plan_id === PRO_PLAN_ID).length * 499,
  enterprise: analytics.subscriptions.filter(s => s.plan_id === ENTERPRISE_PLAN_ID).length * 799
};

const totalMRR = Object.values(mrrByPlan).reduce((sum, mrr) => sum + mrr, 0);
```

## Troubleshooting

### MCP Server Connection Issues

**Problem:** PayPal MCP server won't start or connect
**Symptoms:**
- Error: "Connection refused"
- Server not responding to PayPal API calls

**Solutions:**
1. Verify PayPal credentials are set correctly
2. Check environment variables: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`
3. Ensure PayPal environment is set to "sandbox" or "live"
4. Test API connectivity: `curl -v https://api.paypal.com/v1/oauth2/token`
5. Restart Kiro and try again

### Webhook Verification Failures

**Error:** "Webhook signature verification failed"
**Cause:** Invalid webhook signature or incorrect webhook ID
**Solution:**
1. Verify `PAYPAL_WEBHOOK_ID` matches PayPal dashboard
2. Ensure webhook endpoint uses HTTPS
3. Check webhook event types are subscribed
4. Verify webhook URL is accessible from PayPal servers
5. Test webhook endpoint: `curl -X POST https://yourdomain.com/webhooks/paypal`

### Subscription Creation Errors

**Error:** "INVALID_REQUEST" when creating subscriptions
**Cause:** Missing required fields or invalid plan configuration
**Solution:**
1. Verify subscription plan exists and is active
2. Check required subscriber information is provided
3. Ensure return_url and cancel_url are valid HTTPS URLs
4. Verify plan pricing matches your configuration
5. Test with PayPal sandbox environment first

### Payment Processing Issues

**Error:** "PAYMENT_DENIED" or payment failures
**Cause:** Insufficient funds, expired cards, or PayPal account issues
**Solution:**
1. Implement retry logic for failed payments
2. Send payment failure notifications to clients
3. Provide grace period before service suspension
4. Offer alternative payment methods
5. Monitor payment failure rates and patterns

### API Rate Limiting

**Error:** "RATE_LIMIT_REACHED"
**Cause:** Too many API requests in short time period
**Solution:**
1. Implement exponential backoff retry logic
2. Cache subscription data to reduce API calls
3. Use webhook events instead of polling for status updates
4. Batch API operations when possible
5. Monitor API usage in PayPal dashboard

## Best Practices

- **Always verify webhook signatures** to prevent fraudulent events
- **Use sandbox environment** for testing before going live
- **Implement proper error handling** for all PayPal API calls
- **Store subscription IDs** in your database for reference
- **Monitor payment failures** and implement retry logic
- **Provide clear billing information** to reduce customer disputes
- **Use descriptive invoice numbers** for easy tracking
- **Implement proper logging** for all PayPal transactions
- **Set up monitoring alerts** for webhook failures
- **Regular backup** of subscription and payment data

## Configuration

### Environment Variables

- `PAYPAL_CLIENT_ID`: Your PayPal application client ID (required)
- `PAYPAL_CLIENT_SECRET`: Your PayPal application client secret (required)
- `PAYPAL_ENVIRONMENT`: "sandbox" for testing, "live" for production (required)
- `PAYPAL_WEBHOOK_ID`: Webhook ID from PayPal developer dashboard (required)
- `PAYPAL_WEBHOOK_SECRET`: Webhook secret for signature verification (optional)

### Subscription Plan Configuration

Configure your AI receptionist pricing tiers:

```javascript
const SUBSCRIPTION_PLANS = {
  SOLO_PRO: {
    name: "Solo Pro Plan",
    price: "299.00",
    features: ["Unlimited minutes", "Voice cloning", "Basic analytics"]
  },
  PRO: {
    name: "Pro Plan", 
    price: "499.00",
    features: ["Everything in Solo", "Advanced analytics", "Priority support"]
  },
  ENTERPRISE: {
    name: "Enterprise Plan",
    price: "799.00", 
    features: ["Everything in Pro", "Multi-location", "Custom integrations"]
  }
};
```

## MCP Config Placeholders

**IMPORTANT:** Before using this power, replace the following placeholders in `mcp.json` with your actual values:

- **`YOUR_PAYPAL_CLIENT_ID`**: Your PayPal application client ID.
  - **How to get it:**
    1. Go to https://developer.paypal.com/developer/applications/
    2. Select your application or create a new one
    3. Copy the "Client ID" from the app details
    4. Paste the client ID value here

- **`YOUR_PAYPAL_CLIENT_SECRET`**: Your PayPal application client secret.
  - **How to get it:**
    1. In the same PayPal developer application
    2. Click "Show" next to "Client Secret"
    3. Copy the secret value
    4. Paste the secret value here

- **`YOUR_PAYPAL_ENVIRONMENT`**: PayPal environment setting.
  - **How to set it:** Use "sandbox" for testing or "live" for production
  - Start with "sandbox" for development and testing
  - Switch to "live" only when ready for production

- **`YOUR_WEBHOOK_ID`**: Your PayPal webhook ID for signature verification.
  - **How to get it:**
    1. Go to https://developer.paypal.com/developer/applications/
    2. Select your application
    3. Scroll to "Webhooks" section
    4. Copy the webhook ID
    5. Paste the webhook ID here

**After replacing placeholders, your mcp.json should look like:**
```json
{
  "mcpServers": {
    "paypal": {
      "command": "uvx",
      "args": ["mcp-server-paypal@latest"],
      "env": {
        "PAYPAL_CLIENT_ID": "your-actual-client-id-here",
        "PAYPAL_CLIENT_SECRET": "your-actual-client-secret-here",
        "PAYPAL_ENVIRONMENT": "sandbox",
        "PAYPAL_WEBHOOK_ID": "your-actual-webhook-id-here"
      }
    }
  }
}
```

---

**Package:** `mcp-server-paypal`
**MCP Server:** paypal