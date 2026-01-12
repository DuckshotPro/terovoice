# Design Document: Member Portal Billing Integration

## Overview

The Member Portal Billing Integration transforms the existing Member Portal dashboard into a complete billing and account management hub. This design integrates PayPal subscription management, usage tracking, and billing operations into a cohesive user experience.

The system provides customers with real-time visibility into their subscription status, usage metrics, billing history, and account management capabilities—all while maintaining security, performance, and reliability.

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Member Portal (React)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Billing Dashboard Components                        │   │
│  │  - SubscriptionStatus                               │   │
│  │  - UsageMetrics                                      │   │
│  │  - BillingHistory                                    │   │
│  │  - PaymentMethod                                     │   │
│  │  - PlanUpgrade                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Billing Service Layer (Node.js)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BillingService                                      │   │
│  │  - getSubscriptionStatus()                           │   │
│  │  - getUsageMetrics()                                 │   │
│  │  - getBillingHistory()                               │   │
│  │  - updatePaymentMethod()                             │   │
│  │  - changePlan()                                      │   │
│  │  - cancelSubscription()                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PayPal API Integration Layer                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PayPalAPIClient (existing)                          │   │
│  │  - getSubscription()                                 │   │
│  │  - updateSubscription()                              │   │
│  │  - cancelSubscription()                              │   │
│  │  - listSubscriptions()                               │   │
│  │  - verifyWebhookSignature()                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PayPal API                                          │   │
│  │  - Subscriptions                                     │   │
│  │  - Webhooks                                          │   │
│  │  - Billing Plans                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Subscription Status Flow**
   - User accesses Member Portal → BillingService.getSubscriptionStatus() → PayPalAPIClient.getSubscription() → PayPal API → Response cached in Redux/Context → UI renders status badge

2. **Usage Metrics Flow**
   - System tracks call minutes → UsageService.recordUsage() → Database → BillingService.getUsageMetrics() → UI renders progress bar

3. **Webhook Flow**
   - PayPal sends webhook → Webhook handler validates signature → Updates subscription status in database → Triggers real-time update to UI via WebSocket/polling

## Components and Interfaces

### Frontend Components

#### 1. SubscriptionStatus Component
Displays current subscription plan, status, and renewal information.

```javascript
// src/components/billing/SubscriptionStatus.jsx
interface SubscriptionStatusProps {
  subscriptionId: string;
  onRefresh?: () => void;
}

interface SubscriptionData {
  planName: 'Solo Pro' | 'Professional' | 'Enterprise';
  status: 'ACTIVE' | 'PENDING' | 'CANCELLED' | 'SUSPENDED';
  monthlyPrice: number;
  nextBillingDate: string;
  renewalDate: string;
  cancellationDate?: string;
  suspensionReason?: string;
}
```

#### 2. UsageMetrics Component
Displays usage relative to plan limits with visual progress indicators.

```javascript
// src/components/billing/UsageMetrics.jsx
interface UsageMetricsProps {
  planTier: string;
  onUpgradeClick?: () => void;
}

interface UsageData {
  callMinutesUsed: number;
  callMinutesLimit: number;
  percentageUsed: number;
  warningThreshold: 80;
  alertThreshold: 100;
  features: Feature[];
}

interface Feature {
  name: string;
  included: boolean;
  limit?: number;
  used?: number;
}
```

#### 3. BillingHistory Component
Displays invoice list with filtering and download capabilities.

```javascript
// src/components/billing/BillingHistory.jsx
interface BillingHistoryProps {
  customerId: string;
  pageSize?: number;
}

interface Invoice {
  invoiceId: string;
  date: string;
  amount: number;
  status: 'Paid' | 'Pending' | 'Failed';
  planName: string;
  downloadUrl: string;
}
```

#### 4. PaymentMethod Component
Displays and manages payment method information.

```javascript
// src/components/billing/PaymentMethod.jsx
interface PaymentMethodProps {
  subscriptionId: string;
  onUpdateSuccess?: () => void;
}

interface PaymentMethodData {
  lastFourDigits: string;
  cardBrand: string;
  expiryDate: string;
  updateDate: string;
}
```

#### 5. PlanUpgrade Component
Handles plan changes with prorated pricing calculations.

```javascript
// src/components/billing/PlanUpgrade.jsx
interface PlanUpgradeProps {
  currentPlanId: string;
  onUpgradeSuccess?: () => void;
}

interface PlanOption {
  planId: string;
  name: string;
  price: number;
  features: string[];
  callMinutes: number;
}

interface PricingCalculation {
  currentPlanPrice: number;
  newPlanPrice: number;
  priceDifference: number;
  prorationCredit?: number;
  effectiveDate: string;
}
```

### Backend Services

#### 1. BillingService
Main service orchestrating billing operations.

```javascript
// src/services/billing/BillingService.js
class BillingService {
  constructor(paypalClient, database, usageService) {
    this.paypalClient = paypalClient;
    this.database = database;
    this.usageService = usageService;
  }

  async getSubscriptionStatus(customerId) {
    // Fetch from PayPal, cache in database
  }

  async getUsageMetrics(customerId) {
    // Aggregate usage data from database
  }

  async getBillingHistory(customerId, filters) {
    // Query invoices from database
  }

  async updatePaymentMethod(subscriptionId, redirectUrl) {
    // Redirect to PayPal for payment method update
  }

  async changePlan(subscriptionId, newPlanId) {
    // Update subscription via PayPal API
  }

  async cancelSubscription(subscriptionId, reason) {
    // Cancel subscription via PayPal API
  }

  async syncSubscriptionData(subscriptionId) {
    // Force sync with PayPal
  }
}
```

#### 2. UsageService
Tracks and aggregates usage metrics.

```javascript
// src/services/billing/UsageService.js
class UsageService {
  async recordUsage(customerId, usageData) {
    // Record call minutes, features used, etc.
  }

  async getUsageMetrics(customerId, planTier) {
    // Calculate usage vs limits
  }

  async checkUsageThresholds(customerId) {
    // Check if usage exceeds 80% or 100%
  }
}
```

#### 3. WebhookService
Processes PayPal webhook events.

```javascript
// src/services/billing/WebhookService.js
class WebhookService {
  async processWebhook(webhookEvent) {
    // Verify signature
    // Update subscription status
    // Trigger notifications
    // Emit real-time updates
  }

  async handleSubscriptionCreated(event) {}
  async handleSubscriptionActivated(event) {}
  async handleSubscriptionCancelled(event) {}
  async handleSubscriptionUpdated(event) {}
  async handlePaymentCompleted(event) {}
  async handlePaymentFailed(event) {}
}
```

## Data Models

### Subscription Model
```javascript
{
  _id: ObjectId,
  customerId: string,
  paypalSubscriptionId: string,
  planId: string,
  planName: 'Solo Pro' | 'Professional' | 'Enterprise',
  status: 'ACTIVE' | 'PENDING' | 'CANCELLED' | 'SUSPENDED',
  monthlyPrice: number,
  currency: 'USD',
  startDate: Date,
  nextBillingDate: Date,
  renewalDate: Date,
  cancellationDate: Date,
  suspensionReason: string,
  paymentMethod: {
    lastFourDigits: string,
    cardBrand: string,
    expiryDate: string,
    updateDate: Date
  },
  features: {
    callMinutesLimit: number,
    multiLocationSupport: number,
    prioritySupport: boolean,
    dedicatedAccount: boolean
  },
  createdAt: Date,
  updatedAt: Date,
  syncedAt: Date
}
```

### Usage Model
```javascript
{
  _id: ObjectId,
  customerId: string,
  subscriptionId: string,
  billingPeriodStart: Date,
  billingPeriodEnd: Date,
  callMinutesUsed: number,
  callMinutesLimit: number,
  featuresUsed: {
    multiLocationCount: number,
    customPromptsCount: number
  },
  createdAt: Date,
  updatedAt: Date
}
```

### Invoice Model
```javascript
{
  _id: ObjectId,
  customerId: string,
  subscriptionId: string,
  paypalInvoiceId: string,
  amount: number,
  currency: 'USD',
  status: 'Paid' | 'Pending' | 'Failed',
  planName: string,
  billingPeriodStart: Date,
  billingPeriodEnd: Date,
  dueDate: Date,
  paidDate: Date,
  pdfUrl: string,
  createdAt: Date,
  updatedAt: Date
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Subscription Status Consistency
**For any** customer with an active subscription, the subscription status displayed in the Member Portal SHALL match the status in PayPal within 30 seconds of any status change.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3**

### Property 2: Usage Metrics Accuracy
**For any** customer, the usage metrics displayed (call minutes used vs limit) SHALL be accurate within the last 5-minute update window, and the percentage calculation SHALL always be between 0% and 100%.

**Validates: Requirements 2.1, 2.2, 2.3, 2.6, 2.7**

### Property 3: Usage Threshold Alerts
**For any** customer whose usage exceeds 80% of their plan limit, the system SHALL display a warning indicator. **For any** customer whose usage exceeds 100%, the system SHALL display an alert and suggest upgrade.

**Validates: Requirements 2.4, 2.5**

### Property 4: Billing History Completeness
**For any** customer, the billing history displayed SHALL include all invoices from the last 12 months, ordered in reverse chronological order (newest first), with no gaps or duplicates.

**Validates: Requirements 3.1, 3.2, 3.3, 3.6**

### Property 5: Invoice Download Availability
**For any** invoice displayed in the billing history, a PDF download link SHALL be available and functional, returning a valid PDF document.

**Validates: Requirements 3.5**

### Property 6: Payment Method Update Round-Trip
**For any** payment method update initiated by a customer, after successful update in PayPal, the Member Portal SHALL display the new payment method (last 4 digits) and update date within 30 seconds.

**Validates: Requirements 4.3, 4.4, 4.5**

### Property 7: Plan Change Pricing Accuracy
**For any** plan change (upgrade or downgrade), the price difference and effective date displayed to the customer SHALL match the actual calculation performed by PayPal, and the change SHALL be processed correctly.

**Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**

### Property 8: Subscription Cancellation Finality
**For any** cancelled subscription, the status SHALL be updated to CANCELLED, the cancellation date SHALL be recorded, and the customer SHALL no longer be charged after the cancellation date.

**Validates: Requirements 6.4, 6.5, 6.6**

### Property 9: Feature Display Accuracy
**For any** plan tier, the features displayed SHALL match the features included in that plan, and features not included SHALL indicate they are available in higher tiers.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**

### Property 10: Webhook Processing Idempotence
**For any** webhook event received multiple times (duplicate), processing it multiple times SHALL result in the same final state as processing it once.

**Validates: Requirements 8.2, 8.4**

### Property 11: Notification Delivery Consistency
**For any** billing event (renewal, payment success, payment failure, cancellation, plan change), the system SHALL send a notification email to the customer, and the notification content SHALL match the event details.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

### Property 12: Notification Preference Respect
**For any** customer who opts out of notifications, the system SHALL NOT send them any billing notifications, regardless of event type.

**Validates: Requirements 9.6, 9.7**

### Property 13: Responsive Design Functionality
**For any** screen size (mobile 320px, tablet 768px, desktop 1024px+), all billing functionality SHALL work correctly, and the page load time SHALL be under 3 seconds on mobile networks.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7**

### Property 14: Authentication Enforcement
**For any** billing page, only authenticated users SHALL be able to access it, and users SHALL only see their own billing information, never another customer's data.

**Validates: Requirements 12.1, 12.2**

### Property 15: Error Recovery
**For any** failed operation (API call, payment update, plan change), the system SHALL display a user-friendly error message, provide a support contact link, and allow the user to retry the operation.

**Validates: Requirements 11.1, 11.2, 11.3, 11.5, 11.7**

## Error Handling

### API Error Handling
- **PayPal API Errors**: Catch and translate to user-friendly messages
- **Network Errors**: Implement retry logic with exponential backoff
- **Timeout Errors**: Display timeout message and suggest manual refresh

### Webhook Error Handling
- **Signature Verification Failure**: Log and reject webhook
- **Processing Failure**: Implement retry queue with exponential backoff (up to 5 retries)
- **Duplicate Events**: Implement idempotent processing using event ID deduplication

### User-Facing Error Messages
- Payment method update failed: "We couldn't update your payment method. Please try again or contact support."
- Plan change failed: "Your plan change couldn't be processed. Please try again or contact support."
- Subscription sync failed: "We couldn't sync your subscription. Click 'Refresh' to try again."

## Testing Strategy

### Unit Tests
- Test BillingService methods with mocked PayPal API
- Test UsageService calculations with various usage scenarios
- Test WebhookService signature verification
- Test component rendering with various subscription states
- Test error handling and recovery flows

### Property-Based Tests
- **Property 1**: Generate random subscription status changes, verify consistency within 30 seconds
- **Property 2**: Generate random usage values, verify accuracy and percentage bounds
- **Property 3**: Generate usage values at 80% and 100% thresholds, verify alerts display
- **Property 4**: Generate random invoice dates, verify completeness and ordering
- **Property 5**: Generate random invoices, verify PDF download links work
- **Property 6**: Generate random payment method updates, verify display updates
- **Property 7**: Generate random plan changes, verify pricing accuracy
- **Property 8**: Generate cancellation events, verify finality
- **Property 9**: Generate random plan tiers, verify feature display
- **Property 10**: Generate duplicate webhook events, verify idempotence
- **Property 11**: Generate billing events, verify notification delivery
- **Property 12**: Generate notification preferences, verify respect
- **Property 13**: Generate requests from various screen sizes, verify functionality and load time
- **Property 14**: Generate authenticated and unauthenticated requests, verify access control
- **Property 15**: Generate failed operations, verify error messages and recovery

### Integration Tests
- Test full subscription creation flow
- Test plan upgrade flow with payment
- Test subscription cancellation flow
- Test webhook processing end-to-end
- Test real-time sync between PayPal and Member Portal

### Performance Tests
- Verify billing pages load within 3 seconds on mobile networks
- Verify subscription status updates within 30 seconds of PayPal change
- Verify usage metrics update within 5 minutes

## Security Considerations

1. **Authentication**: All billing endpoints require authenticated user
2. **Authorization**: Users can only access their own billing data
3. **Data Protection**: No full credit card numbers stored; only last 4 digits
4. **HTTPS**: All billing pages use HTTPS
5. **Input Validation**: All user inputs validated before processing
6. **Audit Logging**: All billing operations logged for compliance
7. **Session Management**: Sensitive data cleared on logout

## Implementation Notes

- Integrate with existing PayPalAPIClient (already implemented)
- Use existing Member Portal component structure
- Leverage existing authentication system
- Implement real-time updates using WebSocket or polling
- Cache subscription data to reduce API calls
- Implement graceful degradation for offline scenarios
