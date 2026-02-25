# AI Voice Agent Backend - Implementation Tasks

## Overview

This implementation plan enhances the **existing AI voice agent infrastructure** in `backend-setup/` with additional features from the comprehensive design. The core voice agent, multi-tenant routing, analytics, and HuggingFace LLM integration are already built and working.

**What's Already Built ✅:**
- `AIReceptionistAgent` with LiveKit integration
- `ClientRouter` for multi-tenant phone number routing
- `HuggingFaceLLMProvider` for remote LLM inference
- Analytics database with call logging and revenue tracking
- Profession-specific prompts system (dentist.json)
- Complete backend services (billing, payments, subscriptions)
- Deployment infrastructure (Docker/Podman)

**What Needs Implementation 🔧:**
- Provider abstraction layer for swappable STT/LLM/TTS
- Local inference options (Ollama fallback)
- Enhanced analytics with latency tracking
- 8 additional profession prompts
- Property-based testing for voice components
- Multi-tenant security hardening

## Tasks

### 1. Provider Abstraction Layer

- [ ] 1.1 Create base provider interfaces
  - Create `services/stt/base.py` with BaseSTTProvider abstract class
  - Create `services/tts/base.py` with BaseTTSProvider abstract class
  - Create `services/llm/base.py` with BaseLLMProvider abstract class
  - Define standard interface methods: transcribe/synthesize/generate_response
  - _Requirements: 2.1, 3.1, 4.1_

- [ ] 1.2 Refactor existing providers to implement base classes
  - Update `HuggingFaceLLMProvider` to implement `BaseLLMProvider`
  - Create `DeepgramSTTProvider` implementing `BaseSTTProvider`
  - Create `CartesiaTTSProvider` implementing `BaseTTSProvider`
  - Add provider factory pattern in `services/provider_factory.py`
  - _Requirements: 2.1, 3.1, 4.1_

- [ ] 1.3 Add provider health checking and failover
  - Implement health check methods in each provider base class
  - Add latency tracking for each provider operation
  - Create failover logic to switch providers on failure
  - Add metrics collection for provider performance
  - _Requirements: 8.1, 8.2, 9.1_

- [ ]* 1.4 Write property test for provider abstraction
  - **Property 3: Provider Fallback Resilience**
  - **Validates: Requirements 2.3, 4.4, 8.1, 8.2**

### 2. Local LLM Integration (Ollama Fallback)

- [ ] 2.1 Implement Ollama LLM provider
  - Create `services/llm/ollama_provider.py` implementing `BaseLLMProvider`
  - Add Ollama client initialization with configurable host/port
  - Implement `generate_response()` method using Ollama API
  - Implement `stream_response()` for streaming token generation
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 2.2 Add LLM failover logic
  - Enhance `HuggingFaceLLMProvider` with fallback to Ollama
  - Implement health checking for remote HF endpoint
  - Add automatic provider switching on timeout/error
  - Add cost tracking for both providers (HF vs local)
  - _Requirements: 3.4, 8.1, 8.2_

- [ ]* 2.3 Write property test for LLM failover
  - **Property 3: Provider Fallback Resilience (LLM component)**
  - **Validates: Requirements 3.4, 8.1, 8.2**

### 3. Local STT Provider (faster-whisper)

- [ ] 3.1 Implement faster-whisper STT provider
  - Create `services/stt/whisper_provider.py` implementing `BaseSTTProvider`
  - Add faster-whisper model loading (tiny/base/small models)
  - Implement `transcribe_stream()` for real-time audio processing
  - Add audio preprocessing and VAD integration
  - _Requirements: 2.1, 2.3, 2.5_

- [ ] 3.2 Enhance Deepgram STT provider
  - Create `services/stt/deepgram_provider.py` implementing `BaseSTTProvider`
  - Add confidence scoring and error handling
  - Implement streaming optimizations for lower latency
  - Add fallback to faster-whisper on API errors
  - _Requirements: 2.1, 2.2, 2.5_

- [ ]* 3.3 Write property test for STT latency
  - **Property 2: End-to-End Latency Bounds (STT component)**
  - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**

### 4. Local TTS Provider (Kokoro)

- [ ] 4.1 Implement Kokoro local TTS provider
  - Create `services/tts/kokoro_provider.py` implementing `BaseTTSProvider`
  - Add Kokoro ONNX model loading and initialization
  - Implement `synthesize_stream()` for real-time audio generation
  - Add voice selection and audio format conversion
  - _Requirements: 4.1, 4.4, 4.5_

- [ ] 4.2 Enhance Cartesia TTS provider
  - Create `services/tts/cartesia_provider.py` implementing `BaseTTSProvider`
  - Add voice cloning integration and management
  - Implement streaming synthesis optimizations
  - Add fallback to Kokoro on API errors
  - _Requirements: 4.1, 4.2, 4.3, 10.1, 10.2_

- [ ]* 4.3 Write property test for voice consistency
  - **Property 6: Voice Clone Consistency**
  - **Validates: Requirements 10.1, 10.2, 10.3, 10.5**

### 5. Enhanced Analytics with Latency Tracking

- [ ] 5.1 Add latency tracking to analytics
  - Enhance `analytics/db.py` to track STT/LLM/TTS latencies separately
  - Update `log_call_to_db()` to accept latency metrics
  - Add sentiment analysis using local Ollama
  - Implement revenue estimation based on conversation outcomes
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 5.2 Update AIReceptionistAgent to measure latencies
  - Modify `base_agent.py` to track timing for each component
  - Pass latency metrics to analytics logging
  - Add conversation quality metrics
  - _Requirements: 7.1, 7.2, 9.1_

- [ ]* 5.3 Write property test for analytics completeness
  - **Property 8: Analytics Completeness**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### 6. Additional Profession Prompts

- [ ] 6.1 Create 8 additional profession prompt templates
  - Create `agent/professions/plumber.json` with plumbing-specific prompt
  - Create `agent/professions/mechanic.json` for auto repair
  - Create `agent/professions/locksmith.json` for locksmith services
  - Create `agent/professions/massage_therapist.json` for massage/spa
  - Create `agent/professions/photographer.json` for photography
  - Create `agent/professions/realtor.json` for real estate
  - Create `agent/professions/tattoo_artist.json` for tattoo shops
  - Create `agent/professions/home_inspector.json` for home inspection
  - Follow existing `dentist.json` format and structure
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 6.2 Enhance profession prompt system
  - Add prompt validation in `ClientRouter.get_profession_prompt()`
  - Implement prompt customization per client in database
  - Add prompt testing endpoint in API
  - _Requirements: 6.1, 6.4_

- [ ]* 6.3 Write property test for profession prompts
  - **Property 7: Profession Prompt Application**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### 7. Multi-Tenant Security Hardening

- [ ] 7.1 Add subscription validation to router
  - Enhance `ClientRouter` with subscription status checking
  - Add call rejection for inactive subscriptions
  - Implement usage tracking and limits per client
  - _Requirements: 5.1, 5.4_

- [ ] 7.2 Implement security hardening
  - Add data scrubbing for sensitive information in logs
  - Implement audit logging for all voice agent events
  - Add mutual TLS support for inter-service communication
  - Create immutable audit trail in database
  - _Requirements: 5.2, 5.3, 8.1_

- [ ]* 7.3 Write property test for multi-tenant isolation
  - **Property 4: Multi-Tenant Data Isolation (with security hardening)**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### 8. Configuration and Deployment

- [ ] 8.1 Update configuration system
  - Enhance `config/settings.py` with provider selection options
  - Add environment variables for STT/LLM/TTS provider selection
  - Add provider-specific configuration (model names, API keys, etc.)
  - _Requirements: 2.3, 4.4, 8.1_

- [ ] 8.2 Update deployment configuration
  - Update `podman-compose.yml` to include Ollama service
  - Add Kokoro model download script
  - Update `.env.example` with new provider options
  - Create deployment validation script
  - _Requirements: 9.1, 9.2, 8.1_

### 9. Property-Based Testing

- [ ] 9.1 Set up property-based testing framework
  - Add hypothesis library to requirements.txt
  - Create `tests/conftest.py` with test fixtures
  - Create test data generators for audio, text, and call data
  - _Requirements: All requirements_

- [ ] 9.2 Implement core property tests
  - Write tests for all properties defined in design document
  - Test provider abstraction with multiple implementations
  - Test multi-tenant isolation with random client data
  - Test latency bounds under various conditions
  - _Requirements: All requirements_

- [ ] 9.3 Add integration tests
  - Create end-to-end call flow tests
  - Test provider failover scenarios
  - Test analytics logging completeness
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

### 10. Checkpoint - Core Features Complete

- [ ] 10.1 Verify all core features working
  - Test provider abstraction with all implementations
  - Verify failover logic works correctly
  - Confirm analytics tracking all metrics
  - Validate all profession prompts load correctly
  - Ensure property tests pass
  - _Requirements: All requirements_

## Notes

- **Existing Infrastructure**: The core voice agent system is already built and functional in `backend-setup/`
- **Focus**: These tasks implement the provider abstraction layer, local inference options, and enhanced analytics
- **Minimal Disruption**: All enhancements are designed to work with the existing `AIReceptionistAgent` and `ClientRouter`
- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation leverages existing patterns while adding the comprehensive design features

## Integration with Existing Code

These enhancements integrate with the existing infrastructure:

1. **Provider Abstraction**: Wraps existing HuggingFace/Deepgram/Cartesia providers with base classes
2. **Enhanced Analytics**: Extends existing `analytics/db.py` with latency tracking
3. **Multi-Tenant Routing**: Enhances existing `ClientRouter` with subscription validation
4. **Configuration**: Extends existing `settings.py` with new provider options
5. **Deployment**: Updates existing Podman setup with Ollama and Kokoro

The result is a production-ready enhancement of the existing AI Voice Agent system with comprehensive provider abstractions, local inference options, and advanced analytics.