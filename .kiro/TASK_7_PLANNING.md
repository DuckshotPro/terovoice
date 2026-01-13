# Task 7 Planning: Comprehensive Implementation Strategy for Tasks 7.1-25

## Executive Summary

This document outlines the complete implementation strategy for the remaining 19 tasks (7.1-25) of the Member Portal Billing Integration. The plan is organized by phase, with clear dependencies, testing strategies, and integration points.

**Current Status:** Task 7 (PlanService) is complete. Tasks 7.1-25 require property-based tests, subscription cancellation, feature display, webhooks, notifications, frontend components, and integration testing.

**Total Remaining Tasks:** 19 (7.1 through 25)
**Estimated Implementation Time:** 40-50 hours
**Recommended Approach:** Implement backend services first (7.1-11.1), then frontend components (13-18), then integration and testing (19-25)

---

## Phase 1: Backend Services (Tasks 7.1-11.1)

### Task 7.1: Write Property Tests for Plan Changes
**Requirements:** 5.3, 5.4, 5.5, 5.6, 5.7
**Property:** Plan Change Pricing Accuracy

**Implementation Strategy:**
- Use Hypothesis to generate random plan combinations (all 3 tiers)
- Generate random billing dates and remaining days in cycle
- Verify pricing calculations match expected prorations
- Test upgrade scenarios (Solo Pro → Professional, Professional → Enterprise)
- Test downgrade scenarios (Enterprise → Professional, Professional → Solo Pro)
- Verify effective dates are set correctly
- Verify next billing dates are preserved
- Test edge cases: plan change on last day of cycle, first day of cycle
- Verify PayPal subscription update is called with correct parameters

**Test File:** `backend-setup/tests/test_plan_service_properties.py`
**Expected Tests:** 8-10 property-based tests with 100+ examples each

**Key Assertions:**
```python
# For upgrades: amount_due should be positive (customer pays)
# For downgrades: amount_due should be zero (credit applied)
# Proration credit = (new_daily_rate - current_daily_rate) * days_remaining
# Effective date should be current time
# Next billing date should remain unchanged
```

---

### Task 8: Implement Subscription Cancellation
**Requirements:** 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
**Service:** BillingService.cancelSubscription()

**Implementation Strategy:**
- Add `CancellationReason` enum (customer_request, too_expensive, switching_services, other)
- Create `CancellationData` class with reason, feedback, cancellation_date
- Implement `cancelSubscription(subscription_id, reason, feedback)` method
- Call PayPal API to cancel subscription
- Update subscription status to CANCELLED in database
- Record cancellation date and reason
- Return remaining service access period (if any)
- Handle errors gracefully (PayPal API failures, invalid subscription)
- Implement cache invalidation for subscription data

**Key Methods:**
```python
async def cancelSubscription(
    self,
    subscription_id: str,
    reason: CancellationReason,
    feedback: Optional[str] = None
) -> CancellationResult
```

**Error Handling:**
- Invalid subscription ID → return error
- PayPal API failure → retry with exponential backoff
- Already cancelled → return error
- Suspended subscription → allow cancellation

---

### Task 8.1: Write Property Tests for Cancellation
**Requirements:** 6.4, 6.5, 6.6
**Property:** Subscription Cancellation Finality

**Implementation Strategy:**
- Generate random subscriptions in various states (ACTIVE, PENDING, SUSPENDED)
- Verify cancellation sets status to CANCELLED
- Verify cancellation date is recorded
- Verify cancellation is idempotent (cancelling twice = same result)
- Verify cancelled subscriptions cannot be reactivated
- Verify cancellation reason is stored
- Test edge cases: cancel immediately after creation, cancel on renewal date

**Test File:** `backend-setup/tests/test_cancellation_service_properties.py`
**Expected Tests:** 5-6 property-based tests

---

### Task 9: Implement Feature Display and Comparison
**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
**Service:** BillingService.getFeatures()

**Implementation Strategy:**
- Create `FeatureMatrix` class mapping features to plan tiers
- Implement `getFeatures(plan_tier)` → returns list of Feature objects
- Implement `compareFeatures(plan1, plan2)` → returns comparison
- Implement `getUpgradeRecommendations(current_plan)` → suggests plans with needed features
- Features include: call_minutes, multi_location_support, custom_prompts, priority_support, api_access, sso_enabled
- Each feature has: name, included (bool), limit (optional), current_usage (optional)

**Key Methods:**
```python
def getFeatures(self, plan_tier: PlanTier) -> List[Feature]
def compareFeatures(self, plan1: PlanTier, plan2: PlanTier) -> FeatureComparison
def getUpgradeRecommendations(self, current_plan: PlanTier) -> List[UpgradeRecommendation]
```

**Feature Data Structure:**
```python
@dataclass
class Feature:
    name: str
    included: bool
    limit: Optional[int]
    current_usage: Optional[int]
    available_in_higher_tiers: List[str]  # Plan names
```

---

### Task 9.1: Write Property Tests for Feature Display
**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
**Property:** Feature Display Accuracy

**Implementation Strategy:**
- Generate random plan tiers
- Verify features match plan tier configuration
- Verify feature limits are correct for each tier
- Verify unavailable features indicate higher tiers
- Verify feature comparison is symmetric (compare A to B = reverse of B to A)
- Verify upgrade recommendations only suggest higher tiers
- Test edge cases: compare same plan, compare lowest to highest tier

**Test File:** `backend-setup/tests/test_feature_service_properties.py`
**Expected Tests:** 6-7 property-based tests

---

### Task 10: Implement Webhook Processing and Real-time Sync
**Requirements:** 8.1, 8.2, 8.4, 8.5, 8.6
**Service:** WebhookService.processWebhook()

**Implementation Strategy:**
- Create `WebhookService` class
- Implement `processWebhook(webhook_event)` method
- Add signature verification using PayPal webhook signing
- Implement handlers for subscription events:
  - `BILLING.SUBSCRIPTION.CREATED`
  - `BILLING.SUBSCRIPTION.ACTIVATED`
  - `BILLING.SUBSCRIPTION.UPDATED`
  - `BILLING.SUBSCRIPTION.CANCELLED`
  - `BILLING.SUBSCRIPTION.SUSPENDED`
  - `PAYMENT.CAPTURE.COMPLETED`
  - `PAYMENT.CAPTURE.FAILED`
- Implement idempotent processing (use event ID for deduplication)
- Update subscription status in database
- Invalidate cache for affected subscriptions
- Emit real-time updates (WebSocket or polling)
- Implement retry logic for failed webhook processing

**Key Methods:**
```python
async def processWebhook(self, webhook_event: Dict) -> WebhookResult
async def verifySignature(self, webhook_event: Dict, signature: str) -> bool
async def handleSubscriptionEvent(self, event_type: str, event_data: Dict) -> None
```

**Webhook Event Structure:**
```python
{
    "id": "webhook_event_id",
    "event_type": "BILLING.SUBSCRIPTION.UPDATED",
    "create_time": "2025-01-13T12:00:00Z",
    "resource": {
        "id": "paypal_subscription_id",
        "status": "ACTIVE",
        "plan_id": "plan_id",
        "subscriber": {
            "email_address": "customer@example.com"
        }
    }
}
```

---

### Task 10.1: Write Property Tests for Webhook Processing
**Requirements:** 8.2, 8.4
**Property:** Webhook Processing Idempotence

**Implementation Strategy:**
- Generate random webhook events
- Process same event multiple times
- Verify final state is identical regardless of number of processing attempts
- Verify event ID deduplication works
- Test various event types (subscription created, updated, cancelled, payment completed)
- Verify database state is consistent after duplicate processing
- Test edge cases: process events out of order, process with delays

**Test File:** `backend-setup/tests/test_webhook_service_properties.py`
**Expected Tests:** 5-6 property-based tests

---

### Task 11: Implement Billing Notifications
**Requirements:** 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
**Service:** NotificationService

**Implementation Strategy:**
- Create `NotificationService` class
- Create email templates for each notification type:
  - Renewal reminder (7 days before)
  - Payment successful
  - Payment failed
  - Subscription cancelled
  - Plan upgraded/downgraded
- Implement `sendNotification(notification_type, customer_data)` method
- Implement notification scheduling (use background job queue)
- Implement notification preference management (opt-in/opt-out)
- Store notification history in database
- Implement retry logic for failed email sends

**Notification Types:**
```python
class NotificationType(Enum):
    RENEWAL_REMINDER = "renewal_reminder"
    PAYMENT_SUCCESSFUL = "payment_successful"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PLAN_UPGRADED = "plan_upgraded"
    PLAN_DOWNGRADED = "plan_downgraded"
```

**Key Methods:**
```python
async def sendNotification(
    self,
    notification_type: NotificationType,
    customer_id: str,
    data: Dict
) -> NotificationResult

async def scheduleRenewalReminder(
    self,
    subscription_id: str,
    renewal_date: datetime
) -> None

async def updateNotificationPreferences(
    self,
    customer_id: str,
    preferences: NotificationPreferences
) -> None
```

---

### Task 11.1: Write Property Tests for Notifications
**Requirements:** 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7
**Properties:** Notification Delivery Consistency, Notification Preference Respect

**Implementation Strategy:**
- Generate random notification events
- Verify notifications are sent for all event types
- Verify notification content matches event details
- Verify notification preferences are respected (opt-out prevents sending)
- Verify notification history is recorded
- Test edge cases: send to invalid email, send with missing data, send to opted-out customer

**Test File:** `backend-setup/tests/test_notification_service_properties.py`
**Expected Tests:** 6-7 property-based tests

---

## Phase 2: Frontend Components (Tasks 13-18)

### Task 13: Create SubscriptionStatus Component
**Requirements:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
**Component:** `src/components/billing/SubscriptionStatus.jsx`

**Implementation Strategy:**
- Display current plan name (Solo Pro, Professional, Enterprise)
- Display status badge with color coding:
  - ACTIVE: green
  - PENDING: yellow
  - CANCELLED: red
  - SUSPENDED: orange
- Display renewal date in readable format
- Display monthly price
- Add refresh button to manually sync with PayPal
- Handle loading and error states
- Implement error boundary

**Component Props:**
```javascript
{
  subscriptionId: string,
  onRefresh?: () => void,
  onUpgradeClick?: () => void
}
```

**Component State:**
```javascript
{
  subscription: SubscriptionData,
  loading: boolean,
  error: string | null,
  lastSyncTime: Date
}
```

---

### Task 13.1: Write Unit Tests for SubscriptionStatus Component
**Requirements:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

**Test Cases:**
- Render with ACTIVE subscription
- Render with PENDING subscription
- Render with CANCELLED subscription
- Render with SUSPENDED subscription
- Refresh button triggers sync
- Error state displays error message
- Loading state shows spinner
- Correct badge colors for each status

---

### Task 14: Create UsageMetrics Component
**Requirements:** 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
**Component:** `src/components/billing/UsageMetrics.jsx`

**Implementation Strategy:**
- Display call minutes used vs limit (e.g., "450 / 1000 minutes")
- Display visual progress bar with percentage
- Display warning indicator at 80% usage
- Display alert indicator at 100% usage
- Display available features for plan tier
- Add upgrade suggestion when usage exceeds 100%
- Handle loading and error states

**Component Props:**
```javascript
{
  planTier: string,
  onUpgradeClick?: () => void
}
```

---

### Task 14.1: Write Unit Tests for UsageMetrics Component
**Requirements:** 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7

**Test Cases:**
- Render with various usage levels (0%, 50%, 80%, 100%, 150%)
- Warning indicator displays at 80%
- Alert indicator displays at 100%
- Progress bar width matches percentage
- Upgrade suggestion displays at 100%
- Features list displays correctly

---

### Task 15: Create BillingHistory Component
**Requirements:** 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
**Component:** `src/components/billing/BillingHistory.jsx`

**Implementation Strategy:**
- Display table of invoices with columns: date, amount, status, plan name
- Implement search/filter by date range
- Implement filter by status (Paid, Pending, Failed)
- Add download link for each invoice PDF
- Implement pagination (10 invoices per page)
- Display "No billing history" message when empty
- Handle loading and error states

**Component Props:**
```javascript
{
  customerId: string,
  pageSize?: number
}
```

---

### Task 15.1: Write Unit Tests for BillingHistory Component
**Requirements:** 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7

**Test Cases:**
- Render invoice table with data
- Filter by date range
- Filter by status
- Download link works
- Pagination works
- Empty state displays message

---

### Task 16: Create PaymentMethod Component
**Requirements:** 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
**Component:** `src/components/billing/PaymentMethod.jsx`

**Implementation Strategy:**
- Display current payment method (last 4 digits, card brand)
- Display update date
- Add "Update Payment Method" button
- Button redirects to PayPal for update
- Display confirmation after update
- Handle errors (card declined, expired, etc.)
- Display error message with instructions

**Component Props:**
```javascript
{
  subscriptionId: string,
  onUpdateSuccess?: () => void
}
```

---

### Task 16.1: Write Unit Tests for PaymentMethod Component
**Requirements:** 4.1, 4.2, 4.3, 4.4, 4.5, 4.6

**Test Cases:**
- Display payment method correctly
- Update button redirects to PayPal
- Success message displays after update
- Error message displays on failure

---

### Task 17: Create PlanUpgrade Component
**Requirements:** 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
**Component:** `src/components/billing/PlanUpgrade.jsx`

**Implementation Strategy:**
- Display available plan options (Solo Pro, Professional, Enterprise)
- Highlight current plan
- Display pricing for each plan
- Show price difference when selecting different plan
- Display proration credit/charge calculation
- Show effective date (immediate)
- Show next billing date (unchanged)
- Add upgrade/downgrade confirmation dialog
- Handle errors (plan change failed, PayPal error)

**Component Props:**
```javascript
{
  currentPlanId: string,
  onUpgradeSuccess?: () => void
}
```

---

### Task 17.1: Write Unit Tests for PlanUpgrade Component
**Requirements:** 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8

**Test Cases:**
- Display all plan options
- Highlight current plan
- Show pricing correctly
- Calculate price difference correctly
- Show proration credit for downgrade
- Show proration charge for upgrade
- Confirmation dialog works
- Error message displays on failure

---

### Task 18: Integrate Billing Components into Member Portal
**Requirements:** 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1
**Component:** `src/components/billing/BillingDashboard.jsx`

**Implementation Strategy:**
- Create BillingDashboard container component
- Add billing tab to Member Portal navigation
- Import and render all billing components:
  - SubscriptionStatus
  - UsageMetrics
  - BillingHistory
  - PaymentMethod
  - PlanUpgrade
- Implement state management (Redux or Context)
- Implement data fetching from backend APIs
- Handle loading and error states
- Implement real-time updates (WebSocket or polling)

**Component Structure:**
```
BillingDashboard
├── SubscriptionStatus
├── UsageMetrics
├── BillingHistory
├── PaymentMethod
└── PlanUpgrade
```

---

### Task 18.1: Write Integration Tests for Billing Dashboard
**Requirements:** 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1

**Test Cases:**
- All components render
- Data flows correctly between components
- Refresh button updates all components
- Plan upgrade updates subscription status
- Payment method update refreshes display
- Error in one component doesn't break others

---

## Phase 3: Responsive Design & Error Handling (Tasks 19-21)

### Task 19: Implement Responsive Design
**Requirements:** 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7

**Implementation Strategy:**
- Test on mobile (320px), tablet (768px), desktop (1024px+)
- Use CSS media queries for responsive layouts
- Stack components vertically on mobile
- Use touch-friendly buttons (min 44px height)
- Optimize font sizes for readability
- Implement responsive tables (horizontal scroll on mobile)
- Test page load time on mobile networks (target: <3 seconds)

**Breakpoints:**
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

---

### Task 19.1: Write Property Tests for Responsive Design
**Requirements:** 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
**Property:** Responsive Design Functionality

**Implementation Strategy:**
- Generate random screen sizes
- Verify all components render correctly
- Verify no horizontal scrolling on mobile
- Verify buttons are touch-friendly
- Verify text is readable
- Verify page load time <3 seconds

---

### Task 20: Implement Error Handling and User Feedback
**Requirements:** 11.1, 11.2, 11.3, 11.5, 11.6, 11.7

**Implementation Strategy:**
- Add error boundaries to all components
- Display user-friendly error messages
- Add support contact links in error messages
- Implement retry mechanisms
- Log errors for debugging
- Handle network errors gracefully
- Handle API timeouts

**Error Messages:**
- "We couldn't update your payment method. Please try again or contact support."
- "Your plan change couldn't be processed. Please try again or contact support."
- "We couldn't sync your subscription. Click 'Refresh' to try again."

---

### Task 20.1: Write Unit Tests for Error Handling
**Requirements:** 11.1, 11.2, 11.3, 11.5, 11.6, 11.7

**Test Cases:**
- Error message displays correctly
- Retry button works
- Support link is present
- Error boundary catches errors

---

### Task 21: Implement Security Measures
**Requirements:** 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7

**Implementation Strategy:**
- Add authentication checks to all endpoints
- Implement authorization (users see only their data)
- Add input validation
- Implement audit logging
- Use HTTPS for all billing pages
- Clear sensitive data on logout
- Validate all API responses

---

### Task 21.1: Write Security Tests
**Requirements:** 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7

**Test Cases:**
- Unauthenticated users cannot access billing pages
- Users cannot access other users' data
- Input validation prevents XSS attacks
- API calls use HTTPS
- Sensitive data is cleared on logout

---

## Phase 4: Integration & Testing (Tasks 22-25)

### Task 22: Checkpoint - Ensure All Frontend Components Pass Tests
**Verification:**
- All component unit tests pass
- All integration tests pass
- Responsive design works on all screen sizes
- Error handling works correctly
- No console errors or warnings

---

### Task 23: End-to-End Testing
**Requirements:** All

**Test Scenarios:**
1. Complete subscription creation flow
2. Plan upgrade flow with payment
3. Plan downgrade flow with proration credit
4. Subscription cancellation flow
5. Webhook processing and real-time sync
6. Payment method update flow
7. Billing history retrieval and filtering
8. Usage metrics tracking and alerts
9. Notification delivery
10. Error recovery and retry

---

### Task 23.1: Write End-to-End Tests
**Requirements:** All

**Test Framework:** Cypress or Playwright
**Test Cases:**
- User logs in
- User views subscription status
- User upgrades plan
- User updates payment method
- User views billing history
- User cancels subscription
- Verify all data is correct

---

### Task 24: Performance Optimization
**Requirements:** 10.7

**Optimization Strategies:**
- Implement API call caching
- Lazy load components
- Optimize database queries
- Minimize bundle size
- Implement code splitting
- Verify load times <3 seconds on mobile

---

### Task 25: Final Checkpoint - Ensure All Tests Pass
**Verification:**
- All unit tests pass
- All property tests pass
- All integration tests pass
- All end-to-end tests pass
- Performance benchmarks met
- No security vulnerabilities
- Code coverage >80%

---

## Implementation Dependencies

```
Task 7 (PlanService) ✓
  ↓
Task 7.1 (Plan Property Tests)
  ↓
Task 8 (Cancellation Service)
  ↓
Task 8.1 (Cancellation Tests)
  ↓
Task 9 (Feature Service)
  ↓
Task 9.1 (Feature Tests)
  ↓
Task 10 (Webhook Service)
  ↓
Task 10.1 (Webhook Tests)
  ↓
Task 11 (Notification Service)
  ↓
Task 11.1 (Notification Tests)
  ↓
Task 12 (Backend Checkpoint)
  ↓
Tasks 13-18 (Frontend Components - can run in parallel)
  ↓
Task 19 (Responsive Design)
  ↓
Task 19.1 (Responsive Tests)
  ↓
Task 20 (Error Handling)
  ↓
Task 20.1 (Error Tests)
  ↓
Task 21 (Security)
  ↓
Task 21.1 (Security Tests)
  ↓
Task 22 (Frontend Checkpoint)
  ↓
Task 23 (E2E Testing)
  ↓
Task 23.1 (E2E Tests)
  ↓
Task 24 (Performance)
  ↓
Task 25 (Final Checkpoint)
```

---

## Testing Strategy Summary

### Property-Based Tests (Tasks 7.1, 8.1, 9.1, 10.1, 11.1, 19.1)
- Use Hypothesis for Python backend tests
- Generate 100+ test examples per property
- Test universal properties across all inputs
- Validate correctness properties from design document

### Unit Tests (Tasks 13.1, 14.1, 15.1, 16.1, 17.1, 20.1, 21.1)
- Test individual components in isolation
- Test specific examples and edge cases
- Use React Testing Library for component tests
- Aim for 80%+ code coverage

### Integration Tests (Task 18.1)
- Test component interactions
- Test data flow between components
- Test state management

### End-to-End Tests (Task 23.1)
- Test complete user workflows
- Test across all browsers
- Test on various devices

---

## Code Quality Standards

- All code follows existing project conventions
- All functions have docstrings
- All components have prop validation
- All services have error handling
- All tests have descriptive names
- Code coverage >80%
- No console errors or warnings
- No security vulnerabilities

---

## Estimated Timeline

| Phase | Tasks | Estimated Hours |
|-------|-------|-----------------|
| Phase 1 | 7.1-11.1 | 20-25 hours |
| Phase 2 | 13-18.1 | 15-20 hours |
| Phase 3 | 19-21.1 | 8-10 hours |
| Phase 4 | 22-25 | 5-8 hours |
| **Total** | **7.1-25** | **48-63 hours** |

---

## Next Steps

1. ✅ Task 7: PlanService implementation (COMPLETE)
2. ⏭️ Task 7.1: Write property tests for plan changes
3. Task 8: Implement subscription cancellation
4. Task 8.1: Write property tests for cancellation
5. ... (continue through Task 25)

**Ready to implement Task 7.1 with Haiku.**
