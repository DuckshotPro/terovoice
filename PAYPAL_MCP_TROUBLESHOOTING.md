# PayPal MCP Server - Troubleshooting Guide

## Issue: MCP Error -32000 - Connection Failed

### Root Cause
The official PayPal MCP server package (`paypal-mcp-server`) is not available via `uvx` or the package name is incorrect.

### Solution
We've created a local PayPal MCP server implementation that provides all the same tools without external dependencies.

---

## Setup Instructions

### 1. Verify Configuration

Check `.kiro/settings/mcp.json` has the correct PayPal server configuration:

```json
{
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
```

### 2. Verify Environment Variables

Ensure `.env` file has PayPal credentials:

```bash
PAYPAL_CLIENT_ID=your_paypal_app_client_id
PAYPAL_CLIENT_SECRET=your_paypal_app_client_secret
PAYPAL_ENVIRONMENT=sandbox  # or production
PAYPAL_WEBHOOK_ID=your_paypal_webhook_id
```

### 3. Restart Kiro IDE

After updating configuration:
1. Close Kiro IDE completely
2. Reopen Kiro IDE
3. Check MCP Server view for PayPal server status

---

## Verification Steps

### Step 1: Check MCP Server Status

1. Open Kiro IDE
2. Go to MCP Server view in feature panel
3. Look for "paypal" server
4. Verify status shows "connected" (green indicator)

### Step 2: Test PayPal Tools

Try calling a simple PayPal tool:

```javascript
import { getAllPlans } from '@/services/paypal';

const plans = getAllPlans();
console.log(plans);
// Should output all subscription plans
```

### Step 3: Check Logs

If connection fails, check:
1. Kiro MCP Logs panel for error messages
2. Browser console for JavaScript errors
3. `.env` file for missing credentials

---

## Common Issues and Solutions

### Issue 1: "MCP error -32000: Error connecting to MCP server"

**Cause**: Server process failed to start

**Solutions**:
1. Verify `src/mcp/paypal-server.js` exists
2. Check Node.js is installed: `node --version`
3. Verify `.env` file has all PayPal variables
4. Check file permissions on `src/mcp/paypal-server.js`

### Issue 2: "Cannot find module '@modelcontextprotocol/sdk'"

**Cause**: MCP SDK not installed

**Solution**:
```bash
npm install @modelcontextprotocol/sdk
```

### Issue 3: "PAYPAL_CLIENT_ID is undefined"

**Cause**: Environment variables not loaded

**Solutions**:
1. Verify `.env` file exists in project root
2. Verify variables are set correctly
3. Restart Kiro IDE to reload environment
4. Check `.env` file is not in `.gitignore`

### Issue 4: "PayPal server disabled"

**Cause**: Server is disabled in MCP configuration

**Solution**:
1. Open `.kiro/settings/mcp.json`
2. Find PayPal server configuration
3. Change `"disabled": true` to `"disabled": false`
4. Restart Kiro IDE

---

## Development vs Production

### Development Mode (Sandbox)

```bash
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_CLIENT_ID=sandbox_client_id
PAYPAL_CLIENT_SECRET=sandbox_client_secret
```

### Production Mode

```bash
PAYPAL_ENVIRONMENT=production
PAYPAL_CLIENT_ID=production_client_id
PAYPAL_CLIENT_SECRET=production_client_secret
```

---

## Testing the Connection

### Test 1: List Plans

```javascript
import { getAllPlans } from '@/services/paypal';

const plans = getAllPlans();
console.log('Plans:', plans);
// Expected output:
// {
//   SOLO_PRO: { id: 'plan_solo_pro', name: 'Solo Pro', price: 299, ... },
//   PROFESSIONAL: { id: 'plan_professional', name: 'Professional', price: 499, ... },
//   ENTERPRISE: { id: 'plan_enterprise', name: 'Enterprise', price: 799, ... }
// }
```

### Test 2: Create Subscription

```javascript
import { createSubscription } from '@/services/paypal';

const subscription = await createSubscription(
  'test_customer_123',
  'PROFESSIONAL',
  {
    firstName: 'Test',
    lastName: 'User',
    email: 'test@example.com'
  }
);

console.log('Subscription:', subscription);
// Expected output:
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'APPROVAL_PENDING',
//   planId: 'PROFESSIONAL',
//   customerId: 'test_customer_123',
//   createdAt: '2026-01-12T...',
//   approvalUrl: 'https://www.paypal.com/subscribe?token=I-ABC123XYZ'
// }
```

### Test 3: Get Subscription

```javascript
import { getSubscription } from '@/services/paypal';

const details = await getSubscription('I-ABC123XYZ');
console.log('Details:', details);
// Expected output:
// {
//   subscriptionId: 'I-ABC123XYZ',
//   status: 'ACTIVE',
//   planId: 'plan_professional',
//   currentCycle: 1,
//   nextBillingAmount: '499.00',
//   createdAt: '2026-01-12T...',
//   updatedAt: '2026-01-12T...'
// }
```

---

## Debugging

### Enable Debug Logging

Add to your code:

```javascript
// Enable detailed logging
const DEBUG = true;

if (DEBUG) {
  console.log('PayPal Service Debug Mode Enabled');
  console.log('Environment:', process.env.PAYPAL_ENVIRONMENT);
  console.log('Client ID:', process.env.PAYPAL_CLIENT_ID?.substring(0, 10) + '...');
}
```

### Check MCP Server Logs

1. Open Kiro IDE
2. Go to "MCP Logs" panel
3. Look for PayPal server messages
4. Check for error codes and messages

### Verify File Structure

```
project-root/
├── src/
│   ├── mcp/
│   │   └── paypal-server.js          ← Should exist
│   └── services/
│       └── paypal/
│           ├── subscriptionManager.js
│           ├── customerManager.js
│           ├── subscriptionTracker.js
│           └── index.js
├── .kiro/
│   └── settings/
│       └── mcp.json                  ← Should have PayPal config
├── .env                              ← Should have PayPal credentials
└── package.json
```

---

## Next Steps

### If Connection Works
1. Proceed with webhook processing (Task 3)
2. Implement email notifications (Task 8)
3. Integrate with Member Portal (Task 7)

### If Connection Still Fails
1. Check all environment variables are set
2. Verify Node.js version is compatible
3. Check file permissions
4. Review MCP logs for specific error messages
5. Try restarting Kiro IDE completely

---

## Support Resources

- **PayPal API Docs**: https://developer.paypal.com/docs/
- **MCP SDK Docs**: https://modelcontextprotocol.io/
- **Local Implementation**: `src/mcp/paypal-server.js`
- **Service Usage**: `src/services/paypal/USAGE_GUIDE.md`

---

## Quick Checklist

- [ ] `.env` file has all PayPal variables
- [ ] `.kiro/settings/mcp.json` has PayPal server config
- [ ] `src/mcp/paypal-server.js` exists
- [ ] Node.js is installed and working
- [ ] Kiro IDE has been restarted
- [ ] MCP Server view shows PayPal as "connected"
- [ ] Test calls to PayPal services work

---

**Status**: Troubleshooting guide complete
**Last Updated**: January 12, 2026
