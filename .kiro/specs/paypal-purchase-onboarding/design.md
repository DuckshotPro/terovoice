# Design Document: PayPal Purchase & Onboarding Portal

## Overview

Complete post-purchase experience with multi-step onboarding, interactive demo, and customer portal.

## Architecture

**Frontend:** React with WebRTC for demo
**Backend:** Node.js/Express + Python (agent)
**Database:** PostgreSQL (customer data, onboarding state)
**External:** PayPal API, Google/Outlook Calendar, IBM Cloud (TTS/STT failover)

## Components

### 1. PayPal Integration
- Create/capture orders
- Verify transactions
- Create customer accounts
- Generate portal URLs
- Send welcome emails

### 2. Onboarding Workflow (7 Steps)
1. Business Information (name, industry, phone, services, document upload)
2. Phone Configuration (forwarding setup, SMS service)
3. Caller Responses (text field for custom instructions + file upload for business docs)
4. Calendar Integration (pre-built open-source calendar sync from GitHub)
5. Interactive Demo (open-source TTV chatbot from GitHub + OpenAI endpoint)
6. Review & Confirmation
7. Go Live (activate AI receptionist)

### 3. Interactive Demo (WebRTC)
- Real-time audio streaming
- On-site STT (customer's infrastructure)
- Off-site TTS (IBM Cloud with fallback)
- Live transcript display
- Error handling & fallbacks

**Implementation:** Use open-source TTV chatbot from GitHub + OpenAI API endpoint for LLM responses. Existing synthetic conversation data available for training.

### 4. Customer Portal Dashboard
- Call metrics (today, this week, this month)
- Recent call logs with transcripts
- Settings management
- Billing & subscription info
- Help & support

### 5. Notification System
- Email confirmations at each step
- SMS alerts for new appointments
- Error notifications
- Support escalation

## Data Models

### Customer
```
{
  id, email, businessName, industry, phoneNumber,
  subscriptionPlan, status (active/trial/paused),
  createdAt, updatedAt
}
```

### OnboardingState
```
{
  customerId, currentStep (1-7), progress (0-100),
  businessInfo, phoneConfig, callerResponses,
  calendarIntegration, demoCompleted
}
```

### CallLog
```
{
  customerId, timestamp, duration, transcript,
  appointmentBooked, callerInfo, success
}
```

### ConversationLog (for fine-tuning)
```
{
  id, customerId, callId, timestamp,
  userUtterance, userAudio (raw bytes),
  aiResponse, aiAudio (raw bytes),
  sttProvider (on-site/ibm-cloud),
  ttsProvider (on-site/ibm-cloud),
  confidence, sentiment, intent,
  metadata { industry, profession, callType }
}
```

### AnalyticsEvent
```
{
  id, customerId, eventType, timestamp,
  eventData { step, duration, success, errorCode },
  userId, sessionId, metadata
}
```

## API Endpoints

### PayPal
- POST /api/paypal/create-order
- POST /api/paypal/capture-order
- POST /api/paypal/verify-webhook

### Onboarding
- GET /api/onboarding/:customerId
- POST /api/onboarding/:customerId/business-info
- POST /api/onboarding/:customerId/phone-config
- POST /api/onboarding/:customerId/caller-responses
- POST /api/onboarding/:customerId/calendar/oauth
- POST /api/onboarding/:customerId/complete

### Demo
- POST /api/demo/:customerId/start
- WS /api/demo/:customerId/stream (WebRTC signaling)
- POST /api/demo/:customerId/end

### Portal
- GET /api/portal/:customerId/dashboard
- GET /api/portal/:customerId/calls
- GET /api/portal/:customerId/settings
- POST /api/portal/:customerId/settings/update

### Logging & Analytics
- POST /api/logging/event (log analytics events)
- POST /api/logging/conversation (log conversation for fine-tuning)
- GET /api/analytics/:customerId/dashboard
- GET /api/analytics/:customerId/conversations (for RAG/fine-tuning)
- POST /api/analytics/:customerId/export (export conversation data)

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do.

### Property 1: Payment Verification Consistency
For any PayPal order, capturing the order should create exactly one customer account with matching subscription plan and status set to "active".

### Property 2: Onboarding Progress Monotonicity
For any customer, onboarding progress should only increase or stay the same—never decrease. Completing step N should set progress to at least (N * 14)%.

### Property 3: Demo Transcript Persistence
For any demo conversation, all user utterances and AI responses should be persisted to the database and retrievable via the portal.

### Property 4: Calendar Integration Round-Trip
For any calendar integration, connecting a calendar and then querying availability should return the same events that exist in the connected calendar.

### Property 5: Email Delivery Reliability
For any onboarding step completion, an email should be sent within 5 minutes. If delivery fails, the system should retry up to 3 times.

### Property 6: STT/TTS Failover Correctness
For any demo conversation, if on-site STT fails, the system should automatically use IBM Cloud STT. If TTS fails, it should use IBM Cloud TTS. The conversation should continue without user interruption.

### Property 7: Customer Data Isolation
For any two different customers, querying one customer's data should never return the other customer's data.

### Property 8: Onboarding Completion Idempotence
For any customer, calling the "complete onboarding" endpoint multiple times should result in the same final state (customer marked as "active", portal accessible).

## Error Handling

- Calendar OAuth failure → Allow skip, continue onboarding
- STT failure → Fall back to IBM Cloud
- TTS failure → Fall back to IBM Cloud
- Email delivery failure → Retry 3x, log for support
- Payment verification failure → Display error, offer retry
- WebRTC connection failure → Display error, offer retry

## Testing Strategy

### Unit Tests
- PayPal order creation/capture
- Onboarding state transitions
- Email template rendering
- Calendar OAuth flow
- Customer data validation

### Property-Based Tests
- Payment verification consistency (Property 1)
- Onboarding progress monotonicity (Property 2)
- Demo transcript persistence (Property 3)
- Calendar integration round-trip (Property 4)
- Email delivery reliability (Property 5)
- STT/TTS failover correctness (Property 6)
- Customer data isolation (Property 7)
- Onboarding completion idempotence (Property 8)

### Integration Tests
- Full PayPal → Onboarding → Demo → Portal flow
- Calendar API integration
- Email/SMS delivery
- WebRTC signaling and audio streaming
- Database persistence

### End-to-End Tests
- Complete customer journey from landing page to going live
- Demo conversation with transcript capture
- Portal dashboard functionality
- Settings updates and persistence
