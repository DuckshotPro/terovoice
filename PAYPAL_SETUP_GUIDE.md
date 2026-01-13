# PayPal Integration Setup Guide

## 🚀 Quick Setup (5 minutes)

Your AI Receptionist landing page is ready for PayPal subscriptions! Follow these steps to connect your PayPal Business account.

### Step 1: Get PayPal Developer Credentials

1. **Go to PayPal Developer Console**: https://developer.paypal.com/
2. **Log in** with your PayPal Business account
3. **Create a new app**:
   - Click "Create App"
   - App Name: "AI Receptionist SaaS"
   - Merchant: Select your business account
   - Features: Check "Subscriptions"
4. **Copy your credentials**:
   - Client ID (starts with `A...`)
   - Client Secret (starts with `E...`)

### Step 2: Create Subscription Plans

1. **Go to PayPal Business**: https://www.paypal.com/businessprofile/
2. **Navigate to**: Products & Services → Subscriptions
3. **Create 3 plans**:

#### Solo Pro Plan ($299/month)
- Plan Name: "AI Receptionist - Solo Pro"
- Plan ID: `SOLO-PRO-299` (you'll get a generated ID like `P-5ML4271244454362WXNWU5NQ`)
- Price: $299.00 USD
- Billing Cycle: Monthly
- Description: "Perfect for solo practitioners"

#### Professional Plan ($499/month) 
- Plan Name: "AI Receptionist - Professional"
- Plan ID: `PROFESSIONAL-499` (you'll get a generated ID)
- Price: $499.00 USD
- Billing Cycle: Monthly
- Description: "Most popular for growing businesses"

#### Enterprise Plan ($799/month)
- Plan Name: "AI Receptionist - Enterprise"
- Plan ID: `ENTERPRISE-799` (you'll get a generated ID)
- Price: $799.00 USD
- Billing Cycle: Monthly
- Description: "For large service networks"

### Step 3: Update Your .env File

Replace the placeholder values in your `.env` file:

```env
# PayPal Configuration
VITE_PAYPAL_CLIENT_ID=your_actual_client_id_here
VITE_PAYPAL_CLIENT_SECRET=your_actual_client_secret_here
VITE_PAYPAL_ENVIRONMENT=sandbox
# Change to 'production' when ready to go live

# PayPal Plan IDs (replace with your actual Plan IDs from Step 2)
VITE_PAYPAL_SOLO_PRO_PLAN_ID=P-5ML4271244454362WXNWU5NQ
VITE_PAYPAL_PROFESSIONAL_PLAN_ID=P-1234567890ABCDEF123456
VITE_PAYPAL_ENTERPRISE_PLAN_ID=P-ABCDEF1234567890123456
```

### Step 4: Test Your Integration

1. **Restart your dev server**: `npm run dev`
2. **Visit**: http://localhost:5175/
3. **Click any PayPal button** - it should now open PayPal subscription pages!

## 🔄 Switching to Production

When ready to accept real payments:

1. **Change environment**: Set `VITE_PAYPAL_ENVIRONMENT=production` in `.env`
2. **Use production credentials**: Get production Client ID/Secret from PayPal Developer Console
3. **Create production plans**: Recreate your subscription plans in the live PayPal Business dashboard
4. **Update Plan IDs**: Replace sandbox Plan IDs with production ones

## 💡 Pro Tips

### Webhook Setup (Optional but Recommended)
Set up webhooks to track subscription events:
- Webhook URL: `https://yourdomain.com/api/paypal/webhook`
- Events to subscribe to:
  - `BILLING.SUBSCRIPTION.CREATED`
  - `BILLING.SUBSCRIPTION.ACTIVATED`
  - `BILLING.SUBSCRIPTION.CANCELLED`
  - `PAYMENT.SALE.COMPLETED`

### Testing Subscriptions
Use PayPal's test credit cards in sandbox mode:
- Visa: `4012888888881881`
- Mastercard: `5555555555554444`
- Expiry: Any future date
- CVV: Any 3 digits

### Pricing Strategy
Your current pricing ($299-$799/month) is perfect for service businesses:
- **Solo Pro ($299)**: Targets individual practitioners (dentists, mechanics)
- **Professional ($499)**: Sweet spot for small businesses (2-5 locations)
- **Enterprise ($799)**: Large operations (franchises, multi-location)

## 🎯 Expected Results

Once live, you should see:
- **Conversion Rate**: 15-25% (industry average for B2B SaaS)
- **Average Customer Value**: $499/month × 12 months = $5,988/year
- **Churn Rate**: 5-10% monthly (typical for business tools)

## 🚨 Troubleshooting

### "PayPal Setup Required" Alert
- Check that all environment variables are set in `.env`
- Restart your development server after updating `.env`
- Verify Plan IDs match exactly (including the `P-` prefix)

### PayPal Page Shows "Plan Not Found"
- Double-check Plan IDs in PayPal Business dashboard
- Ensure you're using the correct environment (sandbox vs production)
- Verify the plan is "Active" in PayPal

### Buttons Not Working
- Check browser console for JavaScript errors
- Ensure `.env` file is in the project root
- Verify environment variables start with `VITE_` (required for Vite)

## 📞 Support

Need help? Check these resources:
- **PayPal Developer Docs**: https://developer.paypal.com/docs/subscriptions/
- **PayPal Business Support**: https://www.paypal.com/businesshelp/
- **This Project's Issues**: Create an issue in your repository

---

**🎉 You're ready to start collecting $299-$799/month subscriptions!**

Your AI Receptionist SaaS now has enterprise-grade PayPal integration that will scale with your business.