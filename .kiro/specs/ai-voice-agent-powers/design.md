# Design Document: AI Voice Agent Powers & MCP Integration

## Overview

This design document specifies the architecture for a comprehensive Kiro Powers ecosystem that enables rapid deployment and management of AI voice agents for service businesses. The system integrates voice processing (LiveKit + Ollama), billing (Stripe), telephony (Twilio SIP), and multi-tenant client management into a unified, modular power platform.

**Key Design Principles:**
- **Modularity**: Each power is independently deployable and testable
- **Swappability**: STT/TTS/LLM providers can be swapped via configuration
- **Multi-tenancy**: Complete isolation between client deployments
- **Cost Optimization**: Support for both local (Ollama) and cloud (Deepgram/Cartesia) inference
- **Observability**: Real-time analytics and revenue tracking built-in
- **Scalability**: Horizontal scaling via containerization (Podman/Docker)

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kiro Powers Ecosystem                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Core AI Voice   │  │  Multi-Tenant    │  │  Telephony   │  │
│  │  Agent Power     │  │  SaaS Management │  │  Integration │  │
│  │  (LiveKit+Ollama)│  │  (Stripe+Auth)   │  │  (Twilio SIP)│  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘  │
│           │                     │                    │           │
│  ┌────────▼─────────┐  ┌────────▼─────────┐  ┌──────▼───────┐  │
│  │ Voice Processing │  │ Client Onboarding│  │ Analytics &  │  │
│  │ Pipeline Power   │  │ Automation Power │  │ Monitoring   │  │
│  │ (STT/LLM/TTS)    │  │ (Voice Cloning)  │  │ Power        │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Development &    │  │ Security &       │  │ MCP Server   │  │
│  │ Testing Power    │  │ Compliance Power │  │ Configuration│  │
│  │ (PBT/Simulation) │  │ (RBAC/Encryption)│  │ Management   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Shared Infrastructure Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  • Podman/Docker Containerization                               │
│  • SQLite Analytics Database (per-client)                       │
│  • Stripe Billing Integration                                   │
│  • Twilio SIP Trunk Management                                  │
│  • Voice Cloning Service (ElevenLabs/Cartesia)                  │
│  • Ollama Local Inference (optional)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Incoming Call (SIP)
    │
    ▼
┌─────────────────────────────────────┐
│  Telephony Power (Twilio SIP)       │
│  • Route to correct client          │
│  • Authenticate SIP trunk           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Core AI Voice Agent Power          │
│  • Connect to LiveKit room          │
│  • Load client-specific prompt      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Voice Processing Pipeline          │
│  • STT: Transcribe audio            │
│  • LLM: Generate response (Ollama)  │
│  • TTS: Synthesize voice            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Analytics & Monitoring Power       │
│  • Log call metrics                 │
│  • Calculate revenue impact         │
│  • Update dashboard                 │
└─────────────────────────────────────┘
```

---

## Components and Interfaces

### 1. Core AI Voice Agent Power

**Purpose**: Orchestrates the complete voice agent lifecycle using LiveKit and Ollama.

**Key Components:**
- **LiveKit Agent Orchestrator**: Manages WebRTC connections and call state
- **Profession-Specific Prompt Manager**: Loads and manages 9+ industry prompts
- **Call State Machine**: Handles greeting → listening → processing → response → logging
- **Voice Cloning Integration**: Applies client-specific voice characteristics

**Interfaces:**
```python
class CoreVoiceAgentPower:
    async def initialize_call(client_id: str, phone_number: str) -> CallSession
    async def process_audio_frame(session: CallSession, audio: bytes) -> None
    async def get_agent_response(session: CallSession) -> str
    async def end_call(session: CallSession) -> CallMetrics
    async def load_profession_prompt(profession: str) -> PromptTemplate
```

**Configuration:**
- `LIVEKIT_URL`: WebSocket endpoint for LiveKit server
- `OLLAMA_MODEL`: LLM model (default: llama3.2:3b)
- `PROFESSION`: Service industry type (dentist, plumber, etc.)
- `VOICE_ID`: Client-specific voice clone identifier

---

### 2. Multi-Tenant SaaS Management Power

**Purpose**: Manages client subscriptions, provisioning, and billing lifecycle.

**Key Components:**
- **Stripe Subscription Manager**: Creates/updates/cancels subscriptions
- **Client Provisioning Engine**: Spins up isolated agent instances
- **Dashboard Generator**: Creates unique client subdomains
- **Billing Event Processor**: Handles subscription webhooks

**Interfaces:**
```python
class SaaSManagementPower:
    async def create_client(client_data: ClientInfo) -> Client
    async def setup_subscription(client_id: str, plan_id: str) -> Subscription
    async def provision_infrastructure(client_id: str) -> InfrastructureConfig
    async def generate_dashboard_url(client_id: str) -> str
    async def handle_subscription_event(event: StripeEvent) -> None
    async def cancel_client(client_id: str, reason: str) -> None
```

**Pricing Tiers:**
- **Solo ($299/month)**: 500 minutes, 1 phone number, basic analytics
- **Pro ($499/month)**: 2000 minutes, 5 phone numbers, advanced analytics
- **Enterprise ($799/month)**: Unlimited minutes, unlimited numbers, white-label

---

### 3. Telephony Integration Power

**Purpose**: Manages SIP trunks, phone number provisioning, and call routing.

**Key Components:**
- **Twilio SIP Trunk Manager**: Configures inbound/outbound trunks
- **Phone Number Provisioner**: Purchases and assigns numbers
- **Call Router**: Routes incoming calls to correct client agent
- **Call Quality Monitor**: Tracks latency, jitter, packet loss

**Interfaces:**
```python
class TelephonyPower:
    async def create_sip_trunk(client_id: str) -> SIPTrunk
    async def purchase_phone_number(area_code: str, quantity: int) -> List[PhoneNumber]
    async def assign_number_to_client(client_id: str, phone_number: str) -> None
    async def route_incoming_call(phone_number: str) -> ClientAgent
    async def get_call_quality_metrics(call_id: str) -> CallQuality
    async def handle_call_failure(call_id: str) -> DiagnosticReport
```

**SIP Configuration:**
- Twilio SIP Trunk with authentication
- Automatic failover to backup trunk
- Call recording (optional, per client)
- DTMF tone handling for menu systems

---

### 4. Voice Processing Pipeline Power

**Purpose**: Provides modular, swappable STT/LLM/TTS components.

**Key Components:**
- **STT Provider Abstraction**: Deepgram, Whisper, Silero
- **LLM Provider Abstraction**: Ollama (local), OpenAI (cloud)
- **TTS Provider Abstraction**: Cartesia, Kokoro, Piper
- **Latency Optimizer**: Measures and optimizes sub-800ms response time

**Interfaces:**
```python
class VoiceProcessingPipeline:
    async def transcribe_audio(audio: bytes, provider: str) -> str
    async def generate_response(prompt: str, context: str) -> str
    async def synthesize_speech(text: str, voice_id: str) -> bytes
    async def measure_latency() -> LatencyMetrics
    async def optimize_for_latency(target_ms: int) -> OptimizationReport
    async def switch_provider(component: str, new_provider: str) -> None
```

**Provider Matrix:**
| Component | Local | Cloud | Latency | Cost |
|-----------|-------|-------|---------|------|
| STT | Whisper | Deepgram | 200-400ms | $0.005/min |
| LLM | Ollama | OpenAI | 300-600ms | $0.01/min |
| TTS | Kokoro | Cartesia | 100-300ms | $0.03/min |

---

### 5. Analytics and Monitoring Power

**Purpose**: Tracks call metrics, revenue impact, and system health.

**Key Components:**
- **Call Metrics Logger**: Records duration, latency, sentiment, success
- **Revenue Calculator**: Estimates booked appointments and revenue
- **Dashboard Generator**: Real-time metrics visualization
- **Alert System**: Notifies on anomalies or failures

**Interfaces:**
```python
class AnalyticsPower:
    async def log_call_metrics(call_id: str, metrics: CallMetrics) -> None
    async def calculate_revenue_impact(call_id: str) -> RevenueImpact
    async def get_client_dashboard(client_id: str) -> DashboardData
    async def export_analytics(client_id: str, format: str) -> bytes
    async def set_alert_threshold(metric: str, threshold: float) -> None
    async def get_roi_calculation(client_id: str) -> ROIReport
```

**Metrics Tracked:**
- Call duration, STT latency, LLM latency, TTS latency
- Sentiment analysis (positive/negative/neutral)
- Appointment booking success rate
- Revenue per call (estimated)
- System uptime and error rates

---

### 6. Development and Testing Power

**Purpose**: Provides tools for rapid iteration and validation.

**Key Components:**
- **Conversation Simulator**: Generates synthetic conversations
- **Property-Based Test Framework**: Validates correctness properties
- **Blue-Green Deployment Manager**: Zero-downtime updates
- **Load Testing Engine**: Simulates concurrent calls

**Interfaces:**
```python
class DevelopmentPower:
    async def simulate_conversation(prompt: str, num_turns: int) -> Conversation
    async def run_property_tests(property_set: str) -> TestResults
    async def deploy_blue_green(new_version: str) -> DeploymentResult
    async def run_load_test(concurrent_calls: int, duration_sec: int) -> LoadTestReport
    async def ab_test_prompts(prompt_a: str, prompt_b: str, num_samples: int) -> ABTestResult
    async def enable_debug_logging(client_id: str, level: str) -> None
```

---

### 7. Security and Compliance Power

**Purpose**: Ensures data protection, regulatory compliance, and access control.

**Key Components:**
- **Multi-Tenant Isolation**: Separate databases and containers per client
- **Encryption Manager**: AES-256 at rest, TLS 1.3 in transit
- **RBAC Engine**: Role-based access control (Admin, Manager, Agent)
- **Audit Logger**: Immutable log of all actions
- **GDPR Compliance**: Data export and deletion workflows

**Interfaces:**
```python
class SecurityPower:
    async def isolate_client_data(client_id: str) -> IsolationConfig
    async def encrypt_data(data: bytes, key_id: str) -> bytes
    async def decrypt_data(encrypted: bytes, key_id: str) -> bytes
    async def set_user_role(user_id: str, role: str) -> None
    async def check_permission(user_id: str, action: str) -> bool
    async def log_audit_event(event: AuditEvent) -> None
    async def export_client_data(client_id: str) -> bytes
    async def delete_client_data(client_id: str) -> None
```

**Compliance Standards:**
- GDPR: Data export/deletion within 30 days
- PCI DSS: Stripe handles payment data (no local storage)
- SOC 2: Audit logging, encryption, access controls
- HIPAA: Optional for healthcare clients (encrypted storage)

---

### 8. Client Onboarding Automation Power

**Purpose**: Automates 60-second client activation after payment.

**Key Components:**
- **Voice Cloning Engine**: Processes 30-second voice samples
- **Prompt Customizer**: Generates profession-specific prompts
- **Infrastructure Provisioner**: Spins up isolated agent containers
- **Welcome Email Generator**: Sends setup instructions and credentials

**Interfaces:**
```python
class OnboardingPower:
    async def clone_voice(audio_sample: bytes, client_name: str) -> VoiceClone
    async def generate_custom_prompt(profession: str, business_info: dict) -> str
    async def provision_agent_instance(client_id: str) -> AgentConfig
    async def create_dashboard_subdomain(client_id: str) -> str
    async def send_welcome_email(client_id: str, credentials: dict) -> None
    async def send_training_materials(client_id: str) -> None
    async def notify_sales_team(client_id: str) -> None
```

**Onboarding Workflow:**
1. Payment received (Stripe webhook)
2. Voice sample uploaded
3. Voice cloning initiated (parallel)
4. Profession-specific prompt generated
5. Agent container provisioned
6. Dashboard subdomain created
7. Welcome email sent
8. Sales team notified
9. Client ready to use (< 60 seconds)

---

### 9. MCP Server Configuration Management

**Purpose**: Centralized configuration for all MCP servers and integrations.

**Key Components:**
- **Configuration Store**: YAML/JSON configuration files
- **Validation Engine**: Validates connection parameters
- **Health Monitor**: Checks server status and connectivity
- **Hot-Reload Manager**: Updates configs without restart

**Interfaces:**
```python
class MCPConfigurationManager:
    async def add_mcp_server(server_config: MCPServerConfig) -> None
    async def validate_connection(server_id: str) -> ValidationResult
    async def set_auto_approval(tool_name: str, approved: bool) -> None
    async def get_server_health(server_id: str) -> HealthStatus
    async def enable_retry_policy(server_id: str, max_retries: int) -> None
    async def hot_reload_config(server_id: str) -> None
    async def get_environment_config(env: str) -> EnvironmentConfig
```

**Configuration Hierarchy:**
```
~/.kiro/settings/mcp.json (User-level, global)
    ↓
.kiro/settings/mcp.json (Workspace-level, overrides user)
    ↓
.kiro/specs/ai-voice-agent-powers/mcp.json (Spec-level, overrides workspace)
```

---

## Data Models

### Client Model
```python
class Client:
    id: str                          # Unique client identifier
    name: str                        # Business name
    profession: str                  # Service industry (dentist, plumber, etc.)
    subscription_id: str             # Stripe subscription ID
    plan_tier: str                   # Solo, Pro, Enterprise
    phone_numbers: List[str]         # Assigned phone numbers
    voice_clone_id: str              # Voice cloning identifier
    dashboard_url: str               # Unique subdomain
    created_at: datetime
    status: str                      # active, suspended, cancelled
```

### Call Metrics Model
```python
class CallMetrics:
    call_id: str
    client_id: str
    phone_number: str
    duration_seconds: float
    stt_latency_ms: float            # Speech-to-text latency
    llm_latency_ms: float            # LLM processing latency
    tts_latency_ms: float            # Text-to-speech latency
    total_latency_ms: float          # End-to-end latency
    sentiment: str                   # positive, negative, neutral
    transcript: str                  # Full conversation transcript
    success: bool                    # Call completed successfully
    booked_appointment: bool         # Appointment was booked
    estimated_revenue: float         # Estimated value of call
    timestamp: datetime
```

### Subscription Model
```python
class Subscription:
    id: str
    client_id: str
    stripe_subscription_id: str
    plan_tier: str                   # Solo, Pro, Enterprise
    monthly_cost: float
    minutes_included: int
    phone_numbers_included: int
    status: str                      # active, past_due, cancelled
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
```

---

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Multi-Tenant Data Isolation
**For any** two clients A and B, data from client A should never be accessible to client B, even if they share the same infrastructure.

**Validates: Requirements 2.1, 7.1**

### Property 2: Voice Processing Latency Bound
**For any** incoming audio frame, the total latency (STT + LLM + TTS) should not exceed 800ms in 95% of calls.

**Validates: Requirements 4.4**

### Property 3: Subscription Billing Accuracy
**For any** client subscription, the monthly charge should exactly match the agreed plan tier price, and usage should be tracked accurately.

**Validates: Requirements 2.1, 2.6**

### Property 4: Call Routing Correctness
**For any** incoming call to a phone number, the call should be routed to the correct client's agent, never to another client.

**Validates: Requirements 3.1, 3.2**

### Property 5: Voice Cloning Consistency
**For any** client voice clone, the synthesized speech should maintain consistent voice characteristics across all calls.

**Validates: Requirements 4.5, 8.1**

### Property 6: Analytics Completeness
**For any** completed call, all metrics (duration, latency, sentiment, transcript) should be logged and queryable within 5 seconds.

**Validates: Requirements 5.2, 5.3**

### Property 7: Onboarding Atomicity
**For any** client payment, either the complete onboarding workflow succeeds (voice clone + prompt + infrastructure + dashboard) or none of it succeeds (no partial state).

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 8: Encryption Round-Trip
**For any** sensitive data (voice recordings, transcripts), encrypting then decrypting should produce the original data unchanged.

**Validates: Requirements 7.2**

### Property 9: GDPR Data Export Completeness
**For any** client requesting data export, the exported file should contain all personal data associated with that client, including calls, transcripts, and metrics.

**Validates: Requirements 7.3**

### Property 10: SIP Trunk Failover
**For any** SIP trunk failure, calls should automatically failover to backup trunk within 2 seconds without dropping the call.

**Validates: Requirements 3.7**

### Property 11: Profession Prompt Correctness
**For any** profession type, the loaded prompt should match the profession and contain all required fields (greeting, qualification questions, booking logic).

**Validates: Requirements 1.5**

### Property 12: Configuration Hot-Reload Safety
**For any** MCP server configuration update, the hot-reload should not interrupt active calls or drop existing connections.

**Validates: Requirements 9.7**

---

## Error Handling

### Call Processing Errors
- **STT Failure**: Retry with fallback provider (Whisper if Deepgram fails)
- **LLM Timeout**: Return generic response ("I didn't catch that, can you repeat?")
- **TTS Failure**: Use fallback voice or text-only response
- **Network Latency**: Implement adaptive buffering to maintain <800ms target

### Billing Errors
- **Stripe API Failure**: Queue event for retry (exponential backoff)
- **Subscription Webhook Failure**: Implement idempotent webhook handler
- **Payment Declined**: Notify client and suspend service after 3 days

### Telephony Errors
- **SIP Trunk Unavailable**: Failover to backup trunk
- **Phone Number Unavailable**: Return error to client, suggest alternative
- **Call Routing Failure**: Log error and route to fallback queue

### Data Errors
- **Encryption Failure**: Log error, alert security team, do not proceed
- **Database Connection Loss**: Implement connection pooling with retry
- **Analytics Write Failure**: Queue metrics for batch retry

---

## Testing Strategy

### Unit Tests
- Test each power independently with mocked dependencies
- Validate configuration loading and validation
- Test error handling and retry logic
- Verify data model serialization/deserialization

### Property-Based Tests
- **Property 1 (Isolation)**: Generate random client IDs and verify data access boundaries
- **Property 2 (Latency)**: Generate random audio frames and measure end-to-end latency
- **Property 3 (Billing)**: Generate random subscriptions and verify charge calculations
- **Property 4 (Routing)**: Generate random phone numbers and verify correct routing
- **Property 5 (Voice Cloning)**: Generate random voice samples and verify consistency
- **Property 6 (Analytics)**: Generate random calls and verify metric logging
- **Property 7 (Onboarding)**: Generate random client data and verify atomic completion
- **Property 8 (Encryption)**: Generate random data and verify round-trip correctness
- **Property 9 (GDPR Export)**: Generate random client data and verify export completeness
- **Property 10 (Failover)**: Simulate trunk failures and verify failover within 2 seconds
- **Property 11 (Prompts)**: Generate random professions and verify prompt correctness
- **Property 12 (Hot-Reload)**: Simulate config updates and verify no call interruption

### Integration Tests
- Test complete call flow: SIP → LiveKit → STT → LLM → TTS → Analytics
- Test multi-tenant isolation with concurrent clients
- Test billing workflow: subscription → usage tracking → invoice
- Test onboarding workflow: payment → voice clone → provisioning → dashboard

### Performance Tests
- Load test: 100+ concurrent calls
- Latency test: Measure p50, p95, p99 latencies
- Throughput test: Measure calls/second capacity
- Memory test: Monitor memory usage under load

---

## Deployment Architecture

### Local Deployment (Starlink/Home Lab)
```
┌─────────────────────────────────────┐
│  Home Lab / Office PC               │
│  (Ryzen 7 + RTX 4070 + 32GB RAM)    │
├─────────────────────────────────────┤
│  Podman Rootless                    │
│  ├─ Ollama (LLM inference)          │
│  ├─ LiveKit Agent (voice agent)     │
│  ├─ Analytics DB (SQLite)           │
│  └─ Dashboard (Flask)               │
└────────────┬────────────────────────┘
             │ Starlink (25-45ms latency)
             ▼
┌─────────────────────────────────────┐
│  Twilio SIP Trunk                   │
│  (Phone number routing)             │
└─────────────────────────────────────┘
```

### Cloud Deployment (Hetzner/AWS)
```
┌─────────────────────────────────────┐
│  Hetzner AX162 / AWS EC2            │
│  (2x RTX 5090 + 256GB RAM)          │
├─────────────────────────────────────┤
│  Kubernetes / Docker Swarm          │
│  ├─ Ollama (shared inference)       │
│  ├─ LiveKit Server (multi-tenant)   │
│  ├─ PostgreSQL (analytics)          │
│  ├─ Redis (caching)                 │
│  └─ Dashboard (React)               │
└────────────┬────────────────────────┘
             │ Direct connection (1-5ms)
             ▼
┌─────────────────────────────────────┐
│  Twilio SIP Trunk                   │
│  (Phone number routing)             │
└─────────────────────────────────────┘
```

### Containerization Strategy
- **Per-Client Isolation**: Each client gets isolated Podman pod
- **Shared Inference**: Ollama runs once, shared across clients
- **Volume Mounts**: Client data stored in separate volumes
- **Network Policies**: Strict network isolation between pods

---

## Configuration Management

### Environment-Specific Settings
```yaml
# development.yaml
LIVEKIT_URL: ws://localhost:7880
OLLAMA_MODEL: llama3.2:3b
STT_PROVIDER: whisper
TTS_PROVIDER: kokoro
STRIPE_MODE: test
LOG_LEVEL: debug

# staging.yaml
LIVEKIT_URL: wss://staging-livekit.yourdomain.com
OLLAMA_MODEL: llama3:8b
STT_PROVIDER: deepgram
TTS_PROVIDER: cartesia
STRIPE_MODE: test
LOG_LEVEL: info

# production.yaml
LIVEKIT_URL: wss://livekit.yourdomain.com
OLLAMA_MODEL: llama3:8b
STT_PROVIDER: deepgram
TTS_PROVIDER: cartesia
STRIPE_MODE: live
LOG_LEVEL: warning
```

---

## Monitoring and Observability

### Key Metrics
- **Call Volume**: Calls per hour, per client
- **Latency**: P50, P95, P99 latencies
- **Success Rate**: Percentage of successful calls
- **Revenue**: Estimated revenue per call, per client
- **System Health**: CPU, memory, disk usage
- **Error Rate**: Percentage of failed calls

### Alerting Thresholds
- Latency > 1000ms: Warning
- Error rate > 5%: Alert
- System CPU > 80%: Alert
- Disk usage > 90%: Alert
- SIP trunk unavailable: Critical

### Logging Strategy
- **Application Logs**: Structured JSON logs to stdout
- **Call Logs**: Detailed call transcripts and metrics
- **Audit Logs**: All administrative actions
- **Error Logs**: Stack traces and error context

---

## Security Considerations

### Data Protection
- **At Rest**: AES-256 encryption for sensitive data
- **In Transit**: TLS 1.3 for all network communication
- **Voice Data**: Encrypted storage with client-specific keys
- **Transcripts**: Encrypted and access-controlled

### Access Control
- **RBAC**: Admin, Manager, Agent roles
- **API Keys**: Scoped API keys per client
- **OAuth 2.0**: For dashboard authentication
- **MFA**: Optional multi-factor authentication

### Compliance
- **GDPR**: Data export/deletion within 30 days
- **PCI DSS**: Stripe handles all payment data
- **SOC 2**: Audit logging and access controls
- **HIPAA**: Optional encryption for healthcare clients

---

## Future Enhancements

1. **Multi-Language Support**: Support for Spanish, French, German, etc.
2. **Advanced Analytics**: Sentiment analysis, conversation quality scoring
3. **AI Improvements**: Fine-tuned models for specific industries
4. **White-Label**: Fully branded client dashboards
5. **API Marketplace**: Third-party integrations (CRM, calendar, etc.)
6. **Mobile App**: Native iOS/Android apps for client management
7. **Video Calls**: Extend to video-based interactions
8. **Callback Scheduling**: Automatic callback scheduling for busy times

---

## Design Rationale

### Why Modular Powers?
Each power is independently deployable, testable, and scalable. This allows clients to use only the powers they need and upgrade independently.

### Why Swappable Providers?
Different clients have different cost/quality tradeoffs. Local Ollama is free but slower; cloud providers are faster but cost more. Swappability lets each client optimize for their needs.

### Why Multi-Tenant Isolation?
Complete isolation ensures no data leakage between clients and allows independent scaling. Each client can have different SLAs and configurations.

### Why Property-Based Testing?
PBT validates correctness across a wide range of inputs, catching edge cases that unit tests miss. This is critical for a billing system where correctness is non-negotiable.

### Why Podman/Docker?
Containerization provides reproducible deployments, easy scaling, and resource isolation. Podman's rootless mode adds security without sacrificing performance.

### Why SQLite for Analytics?
SQLite is lightweight, requires no separate database server, and works great for per-client analytics. For large-scale deployments, can be upgraded to PostgreSQL.

---

## Success Criteria

✅ All 9 requirements addressed in design
✅ Modular architecture with clear component boundaries
✅ Multi-tenant isolation verified
✅ Sub-800ms latency achievable
✅ 60-second onboarding workflow
✅ Property-based testing framework defined
✅ Security and compliance standards met
✅ Scalable from home lab to enterprise
