# PayPal Sandbox Setup Checklist

**Status**: Ready to Start Testing
**Timeline**: 30 minutes to complete
**Date**: January 12, 2026

---

## Quick Start (30 Minutes)

### ✅ Step 1: Get Sandbox Credentials (5 minutes)

- [ ] Go to https://developer.paypal.com/dashboard/
- [ ] Sign in with your PayPal account
- [ ] Click "Apps & Credentials"
- [ ] Make sure you're on the "Sandbox" tab
- [ ] Under "REST API apps", click "Create App"
- [ ] Name it "Tero Voice Sandbox"
- [ ] Copy the **Client ID**
- [ ] Copy the **Client Secret**

**Save these values** - you'll need them in Step 3

---

### ✅ Step 2: Create Billing Plans (10 minutes)

Go to https://developer.paypal.com/dashboard/

#### Create Solo Pro Plan ($299/month)
- [ ] Click "Billing Plans" in left menu
- [ ] Click "Create Plan"
- [ ] **Name**: Solo Pro
- [ ] **Description**: Perfect for solo practitioners
- [ ] **Billing Frequency**: Monthly
- [ ] **Price**: $299.00
- [ ] **Currency**: USD
- [ ] Click "Create"
- [ ] **Copy the Plan ID** (looks like: P-1AB12345CD67890EF)

#### Create Professional Plan ($499/month)
- [ ] Click "Create Plan"
- [ ] **Name**: Professional
- [ ] **Description**: For growing businesses
- [ ] **Billing Frequency**: Monthly
- [ ] **Price**: $499.00
- [ ] **Currency**: USD
- [ ] Click "Create"
- [ ] **Copy the Plan ID**

#### Create Enterprise Plan ($799/month)
- [ ] Click "Create Plan"
- [ ] **Name**: Enterprise
- [ ] **Description**: For large organizations
- [ ] **Billing Frequency**: Monthly
- [ ] **Price**: $799.00
- [ ] **Currency**: USD
- [ ] Click "Create"
- [ ] **Copy the Plan ID**

**Save all three Plan IDs** - you'll need them in Step 3

---

### ✅ Step 3: Create Webhook (10 minutes)

Go to https://developer.paypal.com/dashboard/

- [ ] Click "Webhooks" in left menu
- [ ] Click "Create Webhook"
- [ ] **Webhook URL**: `https://terovoice.com/api/webhooks/paypal`
- [ ] Select these events:
  - [ ] BILLING.SUBSCRIPTION.CREATED
  - [ ] BILLING.SUBSCRIPTION.ACTIVATED
  - [ ] BILLING.SUBSCRIPTION.CANCELLED
  - [ ] BILLING.SUBSCRIPTION.UPDATED
  - [ ] PAYMENT.CAPTURE.COMPLETED
  - [ ] PAYMENT.CAPTURE.DENIED
  - [ ] PAYMENT.CAPTURE.REFUNDED
  - [ ] PAYMENT.CAPTURE.REVERSED
- [ ] Click "Create Webhook"
- [ ] **Copy the Webhook ID** (looks like: 1JE50Z90C7278...)

**Save the Webhook ID** - you'll need it in Step 4

---

### ✅ Step 4: Update Environment Variables (5 minutes)

Create or update `.env` file in project root:

```bash
# PayPal Sandbox Configuration
PAYPAL_CLIENT_ID=paste_your_client_id_here
PAYPAL_CLIENT_SECRET=paste_your_client_secret_here
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_WEBHOOK_ID=paste_your_webhook_id_here

# PayPal Plan IDs (from Step 2)
PAYPAL_PLAN_ID_SOLO_PRO=paste_solo_pro_plan_id_here
PAYPAL_PLAN_ID_PROFESSIONAL=paste_professional_plan_id_here
PAYPAL_PLAN_ID_ENTERPRISE=paste_enterprise_plan_id_here

# PayPal Product ID
PAYPAL_PRODUCT_ID=PROD_TERO_VOICE
```

**IMPORTANT**: Never commit `.env` to Git. It's already in `.gitignore`.

---

## Testing (After Setup)

### ✅ Test 1: Create a Subscription

```javascript
import subscriptionManager from '@/services/paypal/subscriptionManager.js';

const subscription = await subscriptionManager.createSubscription(
  'test_customer_123',
  'PROFESSIONAL',
  {
    firstName: 'Test',
    lastName: 'User',
    email: 'test@example.com'
  }
);

console.log('✅ Subscription created:', subscription.subscriptionId);
console.log('📋 Status:', subscription.status);
console.log('🔗 Approval URL:', subscription.approvalUrl);
```

**Expected Output**:
```
✅ Subscription created: I-ABC123DEF456
📋 Status: APPROVAL_PENDING
🔗 Approval URL: https://www.paypal.com/subscribe?token=I-ABC123DEF456
```

### ✅ Test 2: Get Subscription Details

```javascript
const subscription = await subscriptionManager.getSubscription('I-ABC123DEF456');

console.log('✅ Subscription retrieved');
console.log('📋 Status:', subscription.status);
console.log('💰 Plan:', subscription.planId);
```

**Expected Output**:
```
✅ Subscription retrieved
📋 Status: ACTIVE
💰 Plan: P-1AB12345CD67890EF
```

### ✅ Test 3: Test Webhook

1. Go to https://developer.paypal.com/dashboard/
2. Click "Webhooks"
3. Find your webhook
4. Click "Send a test webhook"
5. Select event: `BILLING.SUBSCRIPTION.CREATED`
6. Click "Send"

**Expected**: Webhook received and processed without errors

### ✅ Test 4: Cancel Subscription

```javascript
const result = await subscriptionManager.cancelSubscription(
  'I-ABC123DEF456',
  'Testing cancellation'
);

console.log('✅ Subscription cancelled');
console.log('📋 Status:', result.status);
```

**Expected Output**:
```
✅ Subscription cancelled
📋 Status: CANCELLED
```

---

## Troubleshooting

### ❌ Error: "PayPal authentication failed"

**Cause**: Wrong Client ID or Client Secret

**Solution**:
1. Go to https://developer.paypal.com/dashboard/
2. Click "Apps & Credentials"
3. Make sure you're on "Sandbox" tab
4. Copy Client ID and Client Secret again
5. Update `.env`

### ❌ Error: "Invalid plan ID"

**Cause**: Plan ID not in `.env` or wrong format

**Solution**:
1. Go to https://developer.paypal.com/dashboard/
2. Click "Billing Plans"
3. Copy the Plan ID (should look like: P-1AB12345CD67890EF)
4. Update `.env`

### ❌ Error: "Webhook signature verification failed"

**Cause**: Wrong Webhook ID

**Solution**:
1. Go to https://developer.paypal.com/dashboard/
2. Click "Webhooks"
3. Copy the Webhook ID
4. Update `.env`

### ❌ Error: "No response from PayPal"

**Cause**: Network issue or PayPal API down

**Solution**:
1. Check internet connection
2. Check PayPal status: https://status.paypal.com/
3. Try again in a few minutes

---

## What's Ready

✅ **PayPal API Client** - Real API integration
✅ **Subscription Manager** - Create, get, cancel, update subscriptions
✅ **Customer Manager** - Create and manage customers
✅ **Subscription Tracker** - Track status changes
✅ **Webhook Processing** - Receive and process webhooks
✅ **Error Handling** - Comprehensive error handling
✅ **Documentation** - Complete integration guide

---

## What's Next (After Testing)

1. **Write Property Tests** (1-2 days)
   - Test subscription creation
   - Test webhook processing
   - Test error handling
   - Test retry logic

2. **Integrate with Member Portal** (1 day)
   - Display subscription status
   - Show billing information
   - Real-time updates

3. **Add Email Automation** (1 day)
   - Welcome emails
   - Follow-up emails
   - Billing notifications

4. **Deploy to Production** (1 day)
   - Get production credentials
   - Update environment variables
   - Monitor for issues

---

## Files Modified

- ✅ `src/services/paypal/apiClient.js` - NEW: Real PayPal API client
- ✅ `src/services/paypal/subscriptionManager.js` - UPDATED: Real API calls
- ✅ `src/services/paypal/customerManager.js` - UPDATED: Real API calls
- ✅ `src/services/paypal/subscriptionTracker.js` - UPDATED: Real API calls
- ✅ `.env.example` - UPDATED: New configuration options

---

## Estimated Timeline

| Task | Time | Status |
|------|------|--------|
| Get Sandbox Credentials | 5 min | ⏳ Ready |
| Create Billing Plans | 10 min | ⏳ Ready |
| Create Webhook | 10 min | ⏳ Ready |
| Update Environment | 5 min | ⏳ Ready |
| Test Subscriptions | 10 min | ⏳ Ready |
| **Total Setup** | **40 min** | ⏳ Ready |

---

## Support

**Questions?** Check:
1. `PAYPAL_REAL_API_INTEGRATION_GUIDE.md` - Full integration guide
2. `PAYPAL_CODE_REFERENCE.md` - Code examples
3. `SECURITY_NOTICE.md` - Security best practices
4. PayPal Docs: https://developer.paypal.com/docs/

---

**Status**: Ready to Start
**Next Step**: Get Sandbox Credentials (Step 1)
**Estimated Time to Live**: 2-3 days (setup + testing + deployment)

---

## Quick Reference

### Sandbox URLs
- Dashboard: https://developer.paypal.com/dashboard/
- Billing Plans: https://developer.paypal.com/dashboard/billing/plans
- Webhooks: https://developer.paypal.com/dashboard/webhooks
- Status: https://status.paypal.com/

### Environment Variables
```bash
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_ENVIRONMENT=sandbox
PAYPAL_WEBHOOK_ID=your_webhook_id
PAYPAL_PLAN_ID_SOLO_PRO=your_plan_id
PAYPAL_PLAN_ID_PROFESSIONAL=your_plan_id
PAYPAL_PLAN_ID_ENTERPRISE=your_plan_id
PAYPAL_PRODUCT_ID=PROD_TERO_VOICE
```

### Test Subscription
```javascript
const sub = await subscriptionManager.createSubscription(
  'test_customer',
  'PROFESSIONAL',
  { firstName: 'Test', lastName: 'User', email: 'test@example.com' }
);
```

---

**Ready to begin? Start with Step 1 above! 🚀**
