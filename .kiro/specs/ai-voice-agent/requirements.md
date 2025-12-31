# AI Voice Agent Backend - Requirements Document

## Introduction

The AI Voice Agent Backend is the core orchestration system that powers the AI Receptionist SaaS. It handles incoming phone calls via SIP, processes speech-to-text, generates intelligent responses using local LLM inference, synthesizes natural-sounding speech, and logs all interactions for analytics and billing.

This system must support multiple professions (dentist, plumber, locksmith, etc.) with profession-specific prompts, handle multi-tenant routing, and maintain sub-800ms latency for natural conversation flow.

## Glossary

- **LiveKit**: Open-source real-time communication framework for voice/video
- **Ollama**: Local LLM inference engine running Llama3
- **STT (Speech-to-Text)**: Converts audio to text (Deepgram or faster-whisper)
- **TTS (Text-to-Speech)**: Converts text to audio (Cartesia or Kokoro)
- **SIP**: Session Initiation Protocol for telephony
- **Profession**: Business type (dentist, plumber, locksmith, etc.)
- **Voice Clone**: AI-generated voice that sounds like the business owner
- **Multi-Tenant**: System serving multiple independent clients
- **Latency**: Time from user speech to agent response (target: <800ms)
- **Webhook**: HTTP callback for event notifications

## Requirements

### Requirement 1: Call Reception and Routing

**User Story:** As a service business owner, I want incoming calls to be automatically routed to the correct AI agent based on my phone number, so that each client's calls are handled with their specific prompts and voice.

#### Acceptance Criteria

1. WHEN a call arrives on a Twilio SIP trunk, THE System SHALL route it to LiveKit based on the incoming phone number
2. WHEN a call is routed, THE System SHALL load the correct profession-specific prompt from the database
3. WHEN a call is routed, THE System SHALL load the correct voice clone ID for that client
4. IF the phone number is not found in the database, THEN THE System SHALL reject the call with a professional message
5. WHEN a call is established, THE System SHALL log the call start time, caller ID, and client ID to the database

### Requirement 2: Speech-to-Text Processing

**User Story:** As a system, I want to convert incoming audio to text with minimal latency, so that the LLM can process customer requests quickly.

#### Acceptance Criteria

1. WHEN audio is received from the caller, THE STT Provider SHALL transcribe it within 200-400ms
2. WHEN transcription is complete, THE System SHALL pass the text to the LLM for processing
3. IF the STT provider fails, THEN THE System SHALL retry with the fallback provider (Deepgram → faster-whisper)
4. WHEN transcription confidence is below 60%, THE System SHALL request clarification from the caller
5. THE STT Provider SHALL support streaming for real-time transcription

### Requirement 3: LLM Response Generation

**User Story:** As a system, I want to generate contextually appropriate responses using a local LLM, so that responses are fast, private, and cost-effective.

#### Acceptance Criteria

1. WHEN text is received from STT, THE LLM Handler SHALL generate a response using Ollama Llama3 within 300-600ms
2. WHEN generating a response, THE LLM Handler SHALL use the profession-specific system prompt
3. WHEN generating a response, THE LLM Handler SHALL maintain conversation history for context
4. IF the LLM response is empty or invalid, THEN THE System SHALL generate a fallback response ("I didn't quite catch that, could you repeat?")
5. WHEN a response is generated, THE System SHALL log the prompt, response, and latency to the database

### Requirement 4: Text-to-Speech Synthesis

**User Story:** As a system, I want to convert generated text to natural-sounding speech, so that callers experience a human-like conversation.

#### Acceptance Criteria

1. WHEN text is ready to be spoken, THE TTS Provider SHALL synthesize it within 100-300ms
2. WHEN synthesizing, THE TTS Provider SHALL use the client's voice clone ID
3. WHEN synthesizing, THE TTS Provider SHALL maintain consistent tone and pacing across responses
4. IF the TTS provider fails, THEN THE System SHALL retry with the fallback provider (Cartesia → Kokoro)
5. WHEN audio is synthesized, THE System SHALL stream it to the caller in real-time

### Requirement 5: Multi-Tenant Isolation

**User Story:** As a service business owner, I want my client data, calls, and voice to be completely isolated from other clients, so that I maintain privacy and security.

#### Acceptance Criteria

1. WHEN a call arrives, THE System SHALL verify the phone number belongs to a valid client
2. WHEN processing a call, THE System SHALL use only that client's prompts, voice, and configuration
3. WHEN logging call data, THE System SHALL tag all records with the client ID
4. IF a client's subscription is inactive, THEN THE System SHALL reject incoming calls
5. WHEN querying analytics, THE System SHALL return only data for the authenticated client

### Requirement 6: Profession-Specific Prompts

**User Story:** As a system, I want to load and apply profession-specific prompts, so that the AI agent behaves appropriately for dentists, plumbers, locksmiths, etc.

#### Acceptance Criteria

1. WHEN a call is routed, THE System SHALL load the profession-specific prompt from the database
2. WHEN the LLM generates a response, THE System SHALL prepend the profession prompt to the user message
3. WHEN a profession is changed, THE System SHALL immediately apply the new prompt to subsequent calls
4. THE System SHALL support at least 9 professions (dentist, plumber, mechanic, locksmith, massage, photographer, realtor, tattoo artist, inspector)
5. WHERE a custom profession is requested, THE System SHALL allow clients to upload custom prompts

### Requirement 7: Call Logging and Analytics

**User Story:** As a business owner, I want detailed logs of every call, so that I can track revenue, analyze performance, and improve the AI agent.

#### Acceptance Criteria

1. WHEN a call ends, THE System SHALL log the call duration, STT latency, LLM latency, TTS latency, and total latency
2. WHEN a call ends, THE System SHALL save the full transcript (caller + agent messages)
3. WHEN a call ends, THE System SHALL calculate sentiment analysis of the conversation
4. WHEN a call ends, THE System SHALL estimate the revenue value based on the outcome (booked appointment, qualified lead, etc.)
5. WHEN a call ends, THE System SHALL send a webhook to the client's CRM (if configured)

### Requirement 8: Error Handling and Resilience

**User Story:** As a system, I want to handle errors gracefully and maintain call quality, so that dropped calls and poor experiences are minimized.

#### Acceptance Criteria

1. IF any component fails (STT, LLM, TTS), THEN THE System SHALL use a fallback provider
2. IF all providers fail, THEN THE System SHALL play a professional message and end the call gracefully
3. WHEN a network timeout occurs, THEN THE System SHALL retry the operation up to 3 times
4. WHEN a call is interrupted, THE System SHALL save the partial transcript and log the interruption
5. WHEN an error occurs, THE System SHALL log the error with full context for debugging

### Requirement 9: Performance and Latency

**User Story:** As a system, I want to maintain sub-800ms latency for all operations, so that conversations feel natural and human-like.

#### Acceptance Criteria

1. WHEN a caller speaks, THE System SHALL respond within 800ms (STT + LLM + TTS combined)
2. WHEN processing high volume (100+ concurrent calls), THE System SHALL maintain <800ms latency for 95% of calls
3. WHEN running on IONOS VPS with RTX 5090, THE System SHALL achieve <600ms latency for 99% of calls
4. WHEN running on local hardware (Starlink + RTX 4070), THE System SHALL achieve <800ms latency for 95% of calls
5. THE System SHALL monitor and log latency metrics for every call

### Requirement 10: Voice Cloning Integration

**User Story:** As a business owner, I want my AI agent to sound like me, so that callers feel like they're talking to a real person from my business.

#### Acceptance Criteria

1. WHEN a client uploads a 30-second voice sample, THE System SHALL clone the voice using Cartesia or ElevenLabs API
2. WHEN a voice clone is created, THE System SHALL store the voice ID in the database
3. WHEN generating speech, THE System SHALL use the cloned voice ID for that client
4. IF voice cloning fails, THEN THE System SHALL use a professional default voice
5. WHEN a client requests a new voice clone, THE System SHALL replace the old one and apply immediately

### Requirement 11: SIP Telephony Configuration

**User Story:** As a system, I want to receive calls via SIP from Twilio, so that clients can use standard phone numbers and existing telephony infrastructure.

#### Acceptance Criteria

1. WHEN a SIP call arrives from Twilio, THE System SHALL accept it and establish a WebRTC connection to LiveKit
2. WHEN a call is established, THE System SHALL negotiate audio codec (G.711, Opus, etc.)
3. WHEN a call ends, THE System SHALL properly close the SIP connection and release resources
4. IF the SIP connection drops, THEN THE System SHALL attempt to reconnect or gracefully end the call
5. THE System SHALL support multiple SIP trunks for redundancy

### Requirement 12: Conversation Context and Memory

**User Story:** As a system, I want to maintain conversation context across multiple exchanges, so that the AI agent can handle complex interactions and remember what was discussed.

#### Acceptance Criteria

1. WHEN a conversation begins, THE System SHALL initialize a conversation history buffer
2. WHEN the caller speaks, THE System SHALL add their message to the history
3. WHEN the agent responds, THE System SHALL add the response to the history
4. WHEN generating the next response, THE System SHALL include the last 5-10 exchanges in the LLM prompt
5. WHEN a call ends, THE System SHALL save the full conversation history to the database

---

## Acceptance Criteria Testing Prework

### 1.1 Call routing by phone number
**Thoughts:** This is a core system behavior that must work for all incoming calls. We can test by generating random phone numbers, checking if they route to the correct client, and verifying the correct prompt is loaded.
**Testable:** yes - property

### 1.2 Profession prompt loading
**Thoughts:** This is a rule that should apply to all professions. We can generate random profession types and verify the correct prompt is loaded from the database.
**Testable:** yes - property

### 1.3 Call rejection for unknown numbers
**Thoughts:** This is an edge case - when a phone number is not in the database, the system should reject it. We can test this with a random unknown number.
**Testable:** yes - edge-case

### 2.1 STT latency requirement
**Thoughts:** This is a performance requirement. We can measure the time from audio input to text output and verify it's under 400ms.
**Testable:** yes - property

### 2.2 STT fallback on failure
**Thoughts:** This is a resilience requirement. We can simulate STT provider failure and verify the fallback provider is used.
**Testable:** yes - property

### 3.1 LLM response generation
**Thoughts:** This is a core behavior. We can generate random user inputs and verify the LLM produces valid responses within latency bounds.
**Testable:** yes - property

### 3.2 Conversation history maintenance
**Thoughts:** This is a state management requirement. We can generate a multi-turn conversation and verify the history is maintained correctly.
**Testable:** yes - property

### 4.1 TTS synthesis latency
**Thoughts:** This is a performance requirement. We can measure the time from text input to audio output and verify it's under 300ms.
**Testable:** yes - property

### 5.1 Multi-tenant isolation
**Thoughts:** This is a security requirement. We can generate multiple clients and verify that each client's data is isolated from others.
**Testable:** yes - property

### 6.1 Profession prompt application
**Thoughts:** This is a behavior that should apply to all professions. We can generate random professions and verify the correct prompt is applied.
**Testable:** yes - property

### 7.1 Call logging completeness
**Thoughts:** This is a data integrity requirement. We can complete a call and verify all required fields are logged.
**Testable:** yes - property

### 8.1 Error handling and fallback
**Thoughts:** This is a resilience requirement. We can simulate component failures and verify fallbacks are used.
**Testable:** yes - property

### 9.1 End-to-end latency
**Thoughts:** This is a performance requirement. We can measure the total time from caller speech to agent response and verify it's under 800ms.
**Testable:** yes - property

### 10.1 Voice cloning integration
**Thoughts:** This is an integration requirement. We can upload a voice sample and verify the voice ID is stored and used.
**Testable:** yes - property

### 11.1 SIP call acceptance
**Thoughts:** This is a telephony requirement. We can send a SIP call and verify it's accepted and routed correctly.
**Testable:** yes - property

### 12.1 Conversation history round-trip
**Thoughts:** This is a data persistence requirement. We can generate a conversation, save it, and verify it can be retrieved with all exchanges intact.
**Testable:** yes - property
