# Implementation Plan: PayPal Purchase & Onboarding Portal

## Overview

Build a complete post-purchase experience using open-source components and existing code. Integrate PayPal, multi-step onboarding, interactive demo, and customer portal.

## Tasks

- [x] 1. Set up project structure and database schema
  - Create React frontend folder structure
  - Create Node.js backend folder structure
  - Design PostgreSQL schema for customers, onboarding state, call logs, conversations, analytics
  - Set up environment variables and configuration
  - _Requirements: 1.1, 2.1, 11.1, 12.1_

- [ ] 2. Implement PayPal integration
  - [ ] 2.1 Create PayPal order creation endpoint
    - Integrate PayPal SDK
    - Create order with plan details
    - Return order ID to frontend
    - _Requirements: 1.1_

  - [ ] 2.2 Create PayPal capture endpoint
    - Capture approved order
    - Verify transaction
    - Create customer account in database
    - _Requirements: 1.1, 1.2_

  - [ ] 2.3 Create customer account and portal URL generation
    - Generate unique customer ID
    - Create portal URL
    - Send welcome email
    - _Requirements: 1.2, 1.3, 9.1_

  - [ ] 2.4 Write property test for payment verification consistency
    - **Property 1: Payment Verification Consistency**
    - **Validates: Requirements 1.1, 1.2**

- [ ] 3. Implement onboarding workflow backend
  - [ ] 3.1 Create onboarding state management endpoints
    - GET /api/onboarding/:customerId (retrieve current state)
    - POST endpoints for each step (business-info, phone-config, caller-responses, calendar, complete)
    - Update progress tracking
    - _Requirements: 2.1, 2.2, 3.1, 4.1, 5.1, 7.1_

  - [ ] 3.2 Implement business information step
    - Validate and save business name, industry, phone, description
    - Handle document uploads (store in S3/local storage)
    - Update progress to 20%
    - _Requirements: 2.1, 2.2_

  - [ ] 3.3 Implement phone configuration step
    - Validate phone number format
    - Save forwarding configuration
    - Enable/disable SMS service
    - Send test SMS
    - Update progress to 40%
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 3.4 Implement caller responses step
    - Accept text field input for custom responses
    - Accept file uploads for business documents
    - Store responses in database
    - Update progress to 60%
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 3.5 Implement calendar integration step (use pre-built open-source from GitHub)
    - Integrate open-source calendar sync library
    - Implement OAuth flow for Google/Outlook
    - Verify connection and retrieve availability
    - Update progress to 80%
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ] 3.6 Write property test for onboarding progress monotonicity
    - **Property 2: Onboarding Progress Monotonicity**
    - **Validates: Requirements 7.1, 7.2_

- [ ] 4. Implement interactive demo (use open-source TTV chatbot + OpenAI)
  - [ ] 4.1 Set up WebRTC signaling server
    - Create WebRTC peer connection manager
    - Implement signaling endpoints
    - Handle connection lifecycle
    - _Requirements: 6.2, 6.3_

  - [ ] 4.2 Integrate open-source TTV chatbot from GitHub
    - Clone/integrate TTV chatbot repository
    - Configure OpenAI API endpoint
    - Set up audio input/output handling
    - _Requirements: 6.1, 6.4, 6.5_

  - [ ] 4.3 Implement STT/TTS with fallback logic
    - On-site STT (customer's infrastructure)
    - Off-site TTS (IBM Cloud)
    - Implement fallback to IBM Cloud STT if on-site fails
    - Implement fallback to IBM Cloud TTS if primary fails
    - _Requirements: 6.5, 6.8, 6.9, 10.2, 10.3_

  - [ ] 4.4 Implement conversation logging for fine-tuning
    - Capture user utterances and AI responses
    - Store raw audio bytes (WAV format)
    - Log metadata (STT provider, TTS provider, confidence, sentiment)
    - Tag with industry, profession, call type
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 4.5 Implement live transcript display
    - Display user speech in real-time
    - Display AI responses in real-time
    - Show conversation summary after demo ends
    - _Requirements: 6.3, 6.6_

  - [ ] 4.6 Write property test for demo transcript persistence
    - **Property 3: Demo Transcript Persistence**
    - **Validates: Requirements 6.3, 6.6, 11.1_

  - [ ] 4.7 Write property test for STT/TTS failover correctness
    - **Property 6: STT/TTS Failover Correctness**
    - **Validates: Requirements 6.8, 6.9, 10.2, 10.3_

- [ ] 5. Implement onboarding completion and portal activation
  - [ ] 5.1 Create onboarding completion endpoint
    - Mark all steps as complete
    - Set customer status to "active"
    - Generate portal dashboard
    - Send "Go Live" email
    - _Requirements: 7.3, 7.4, 7.5, 9.5_

  - [ ] 5.2 Implement "Go Live" activation
    - Activate AI receptionist for customer
    - Configure phone routing
    - Send confirmation email with next steps
    - _Requirements: 7.5, 9.5_

  - [ ] 5.3 Write property test for onboarding completion idempotence
    - **Property 8: Onboarding Completion Idempotence**
    - **Validates: Requirements 7.3, 7.4, 7.5_

- [ ] 6. Implement customer portal dashboard
  - [ ] 6.1 Create portal dashboard page
    - Display key metrics (calls today, appointments booked, success rate)
    - Display recent call logs with timestamps
    - Show call outcomes and summaries
    - _Requirements: 8.1, 8.2_

  - [ ] 6.2 Implement call detail view
    - Display full transcript for each call
    - Allow listening to call recording (if available)
    - Show caller information and outcomes
    - _Requirements: 8.3_

  - [ ] 6.3 Implement settings management
    - Allow updating business information
    - Allow updating caller responses
    - Allow managing calendar integration
    - _Requirements: 8.4_

  - [ ] 6.4 Implement billing view
    - Display subscription status
    - Show next billing date
    - Display usage metrics
    - _Requirements: 8.5_

  - [ ] 6.5 Implement help section
    - Display FAQs
    - Link to documentation
    - Show support contact options
    - _Requirements: 8.6_

  - [ ] 6.6 Write property test for customer data isolation
    - **Property 7: Customer Data Isolation**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4_

- [ ] 7. Implement notification system
  - [ ] 7.1 Create email notification service
    - Send welcome email after payment
    - Send confirmation emails at each onboarding step
    - Send "Go Live" email when ready
    - Implement retry logic (3 attempts)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.4_

  - [ ] 7.2 Create SMS notification service
    - Send SMS confirmations for phone configuration
    - Send SMS alerts for new appointments
    - Handle SMS delivery failures
    - _Requirements: 3.3, 3.4_

  - [ ] 7.3 Write property test for email delivery reliability
    - **Property 5: Email Delivery Reliability**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.4_

- [ ] 8. Implement analytics and logging
  - [ ] 8.1 Create analytics event logging
    - Log onboarding step completions
    - Log demo interactions
    - Log portal usage
    - Aggregate into dashboards
    - _Requirements: 12.1, 12.2, 12.3_

  - [ ] 8.2 Create analytics dashboard
    - Display conversion rates by step
    - Display customer metrics (total, active, churn)
    - Display demo metrics (duration, bookings, success rate)
    - Implement filtering by date, industry, plan
    - _Requirements: 12.2, 12.3, 12.4, 12.5_

  - [ ] 8.3 Implement error logging
    - Log all errors with context
    - Log stack traces and user actions
    - Create error dashboard for debugging
    - _Requirements: 12.6_

  - [ ] 8.4 Implement conversation export for fine-tuning
    - Export conversations in JSON/CSV format
    - Include metadata and audio files
    - Implement data privacy and encryption
    - _Requirements: 11.5, 11.6_

- [ ] 9. Implement error handling and fallbacks
  - [ ] 9.1 Create error handling middleware
    - Catch and log all errors
    - Display user-friendly error messages
    - Implement retry logic for transient failures
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ] 9.2 Implement calendar integration fallback
    - Allow skipping calendar step if OAuth fails
    - Continue onboarding without calendar
    - _Requirements: 10.1_

  - [ ] 9.3 Implement STT/TTS fallback (already in 4.3)
    - Fallback to IBM Cloud if on-site fails
    - Continue demo without interruption
    - _Requirements: 10.2, 10.3_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all unit tests pass
  - Ensure all property tests pass
  - Ensure all integration tests pass
  - Ask the user if questions arise

- [ ] 11. Frontend implementation
  - [ ] 11.1 Create landing page with PayPal button
    - Display pricing plans
    - Integrate PayPal checkout
    - Redirect to onboarding after payment
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 11.2 Create onboarding workflow UI
    - Multi-step form with progress bar
    - Business information form
    - Phone configuration form
    - Caller responses form
    - Calendar integration UI
    - _Requirements: 2.1, 3.1, 4.1, 5.1_

  - [ ] 11.3 Create interactive demo UI
    - WebRTC audio controls (start/stop)
    - Live transcript display
    - Demo summary and results
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ] 11.4 Create portal dashboard UI
    - Dashboard with metrics
    - Call logs table
    - Settings pages
    - Billing page
    - Help section
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 11.5 Write integration tests for frontend
    - Test PayPal flow
    - Test onboarding workflow
    - Test demo interaction
    - Test portal navigation
    - _Requirements: All_

- [ ] 12. Final checkpoint - Full end-to-end testing
  - Test complete customer journey from landing page to going live
  - Test demo conversation with transcript capture
  - Test portal dashboard functionality
  - Test settings updates and persistence
  - Ask the user if questions arise

## Notes

- Use open-source components where available (calendar sync, TTV chatbot)
- Leverage existing synthetic conversation data for training
- Implement comprehensive logging for analytics and model fine-tuning
- All tests marked with `*` are optional for MVP but recommended for production
- Focus on core functionality first, then optimize
