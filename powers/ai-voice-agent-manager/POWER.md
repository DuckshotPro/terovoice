---
name: "ai-voice-agent-manager"
displayName: "AI Voice Agent Manager"
description: "Complete management system for AI voice agents using LiveKit, Ollama, and swappable STT/TTS providers. Handles deployment, monitoring, and client management for AI receptionist SaaS."
keywords: ["ai-voice-agent", "livekit", "ollama", "stt", "tts", "receptionist", "voice-cloning"]
author: "AI Voice Agent SaaS"
---

# AI Voice Agent Manager

## Overview

This power provides comprehensive management for AI voice agents built with LiveKit Agents framework, Ollama for local LLM inference, and swappable STT/TTS providers. It's specifically designed for AI receptionist SaaS businesses running multi-tenant voice agent deployments.

The power handles voice agent lifecycle management, client onboarding, voice cloning, profession-specific prompt deployment, and real-time monitoring. It supports both local and cloud deployments with cost optimization for different hardware configurations.

Key capabilities include automated client provisioning, voice agent deployment, performance monitoring, profession-specific customization, and integration with billing systems for usage tracking.

## Onboarding

### Prerequisites

- LiveKit server (local or cloud)
- Ollama installation with Llama3 model
- STT provider (Deepgram or local Whisper)
- TTS provider (Cartesia or local Kokoro)
- SIP trunk provider (Twilio recommended)
- Docker/Podman for containerization

### Installation

1. **Install LiveKit Agents:**
   ```bash
   pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram
   ```

2. **Install Ollama:**
   ```bash
   # Linux/Mac
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows
   # Download from https://ollama.ai/download
   ```

3. **Pull Llama3 Model:**
   ```bash
   ollama pull llama3.2:3b
   ```

4. **Install Voice Processing Dependencies:**
   ```bash
   pip install faster-whisper kokoro-onnx cartesia deepgram-sdk
   ```

### Configuration

Set these environment variables:

- `LIVEKIT_URL`: Your LiveKit server URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `STT_PROVIDER`: "deepgram" or "whisper"
- `TTS_PROVIDER`: "cartesia" or "kokoro"
- `DEEPGRAM_API_KEY`: Deepgram API key (if using Deepgram)
- `CARTESIA_API_KEY`: Cartesia API key (if using Cartesia)

## Common Workflows

### Workflow 1: Deploy New Voice Agent

**Goal:** Deploy a voice agent for a new client with custom voice and profession

**Steps:**
1. Create client configuration
2. Clone client's voice from sample
3. Deploy profession-specific prompts
4. Configure SIP routing
5. Start voice agent container

**Example:**
```python
# Deploy voice agent for dental practice
client_config = {
    "client_id": "dr-mike-dentistry",
    "profession": "dentist",
    "voice_sample": "./samples/dr-mike-voice.wav",
    "phone_number": "+1234567890",
    "business_name": "Dr. Mike's Family Dentistry"
}

# Deploy agent
agent_id = await deploy_voice_agent(client_config)
print(f"Voice agent deployed: {agent_id}")
```

### Workflow 2: Voice Cloning Setup

**Goal:** Clone client's voice for personalized AI receptionist

**Steps:**
1. Process voice sample (30-60 seconds)
2. Generate voice model
3. Test voice quality
4. Deploy to production

**Example:**
```python
# Clone voice from sample
voice_clone = await clone_voice({
    "client_id": "dr-mike-dentistry",
    "sample_path": "./samples/dr-mike-voice.wav",
    "voice_name": "Dr. Mike Professional",
    "language": "en-US"
})

# Test voice quality
test_audio = await synthesize_test({
    "voice_id": voice_clone.id,
    "text": "Thank you for calling Dr. Mike's Family Dentistry. How may I help you today?"
})
```

### Workflow 3: Profession-Specific Deployment

**Goal:** Deploy voice agent with profession-specific prompts and behavior

**Steps:**
1. Select profession template
2. Customize prompts for business
3. Configure appointment booking
4. Set up knowledge base
5. Deploy with monitoring

**Example:**
```python
# Deploy dentist receptionist
profession_config = {
    "profession": "dentist",
    "business_info": {
        "name": "Dr. Mike's Family Dentistry",
        "services": ["cleanings", "fillings", "crowns", "emergency"],
        "hours": "Mon-Fri 8AM-6PM",
        "booking_system": "calendly"
    },
    "prompts": {
        "greeting": "Thank you for calling Dr. Mike's Family Dentistry. How may I help you today?",
        "emergency": "I understand you're having a dental emergency. Let me get you scheduled right away.",
        "booking": "I'd be happy to schedule your appointment. What type of service do you need?"
    }
}

await deploy_profession_agent(profession_config)
```

### Workflow 4: Multi-Tenant Monitoring

**Goal:** Monitor all client voice agents from central dashboard

**Steps:**
1. Collect agent metrics
2. Track call volume and quality
3. Monitor system resources
4. Generate client reports
5. Alert on issues

**Example:**
```python
# Get system overview
dashboard = await get_agent_dashboard()

print(f"Active Agents: {dashboard.active_agents}")
print(f"Total Calls Today: {dashboard.calls_today}")
print(f"Average Response Time: {dashboard.avg_response_time}ms")

# Get client-specific metrics
client_metrics = await get_client_metrics("dr-mike-dentistry")
print(f"Calls Handled: {client_metrics.calls_handled}")
print(f"Appointments Booked: {client_metrics.appointments_booked}")
print(f"Customer Satisfaction: {client_metrics.satisfaction_score}")
```

### Workflow 5: Performance Optimization

**Goal:** Optimize voice agent performance for cost and quality

**Steps:**
1. Analyze current performance
2. Identify bottlenecks
3. Optimize model selection
4. Adjust resource allocation
5. Monitor improvements

**Example:**
```python
# Performance analysis
perf_analysis = await analyze_performance("dr-mike-dentistry")

if perf_analysis.avg_latency > 800:  # ms
    # Switch to faster TTS
    await update_agent_config("dr-mike-dentistry", {
        "tts_provider": "cartesia",  # Faster than local
        "model_size": "small"  # Faster inference
    })

if perf_analysis.cost_per_minute > 0.10:  # USD
    # Switch to local providers
    await update_agent_config("dr-mike-dentistry", {
        "stt_provider": "whisper",  # Local, free
        "tts_provider": "kokoro",   # Local, free
        "llm_provider": "ollama"    # Local, free
    })
```

## Troubleshooting

### Voice Agent Won't Start

**Problem:** Voice agent fails to start or connect
**Symptoms:**
- Error: "LiveKit connection failed"
- Agent not responding to calls

**Solutions:**
1. Check LiveKit server status: `curl -v https://your-livekit-server.com`
2. Verify API credentials in environment variables
3. Ensure Ollama is running: `ollama list`
4. Check SIP trunk configuration
5. Review agent logs: `docker logs voice-agent-container`

### Poor Voice Quality

**Problem:** Synthesized voice sounds robotic or unclear
**Symptoms:**
- Choppy audio
- Unnatural intonation
- Audio artifacts

**Solutions:**
1. Improve voice sample quality (clear, 30+ seconds)
2. Switch TTS provider: Cartesia > Kokoro > built-in
3. Adjust audio settings: sample rate, bitrate
4. Test with different voice models
5. Check network latency to TTS provider

### High Latency Issues

**Problem:** Voice agent responds too slowly
**Symptoms:**
- Response time > 1 second
- Awkward conversation pauses
- Timeout errors

**Solutions:**
1. Optimize model selection: smaller models for speed
2. Use local providers to reduce network hops
3. Implement response caching for common queries
4. Upgrade hardware: more RAM, faster CPU/GPU
5. Use edge deployment closer to users

### Memory/Resource Issues

**Problem:** System running out of memory or CPU
**Symptoms:**
- Agent crashes
- Slow response times
- High system load

**Solutions:**
1. Monitor resource usage: `htop`, `nvidia-smi`
2. Optimize model sizes: use quantized models
3. Implement agent pooling and load balancing
4. Scale horizontally: multiple agent instances
5. Use GPU acceleration for inference

## Best Practices

- **Use voice samples of 30-60 seconds** for best cloning quality
- **Test voice agents thoroughly** before client deployment
- **Monitor performance metrics** continuously
- **Implement graceful fallbacks** for service failures
- **Use local providers** for cost optimization when possible
- **Cache common responses** to reduce latency
- **Implement proper logging** for debugging and analytics
- **Regular model updates** for improved performance
- **Backup voice models and configurations** regularly
- **Use staging environment** for testing changes

## Configuration

### Profession Templates

Available profession templates with optimized prompts:

```python
PROFESSIONS = {
    "dentist": {
        "greeting": "Thank you for calling {business_name}. How may I help you today?",
        "services": ["cleaning", "filling", "crown", "emergency", "consultation"],
        "booking_questions": ["What type of service?", "Preferred date/time?", "Insurance information?"]
    },
    "plumber": {
        "greeting": "This is {business_name}, what plumbing issue can I help you with?",
        "services": ["leak repair", "drain cleaning", "installation", "emergency"],
        "urgency_detection": ["emergency", "flooding", "no water", "burst pipe"]
    },
    "mechanic": {
        "greeting": "Thank you for calling {business_name}. What's going on with your vehicle?",
        "services": ["oil change", "brake repair", "engine diagnostic", "towing"],
        "vehicle_info": ["year", "make", "model", "mileage"]
    }
    # ... 6 more professions
}
```

### Hardware Recommendations

**Minimum (1-5 clients):**
- CPU: 8-core Intel/AMD
- RAM: 16GB
- Storage: 100GB SSD
- Network: 100Mbps

**Recommended (10-50 clients):**
- CPU: 16-core with AVX512
- RAM: 64GB
- GPU: RTX 4070 or better
- Storage: 500GB NVMe SSD
- Network: 1Gbps

**Enterprise (100+ clients):**
- Multiple servers with load balancing
- GPU cluster for inference
- Dedicated database servers
- CDN for voice model distribution

---

**Framework:** LiveKit Agents
**LLM:** Ollama + Llama3
**Deployment:** Docker/Podman