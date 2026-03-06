# AI Receptionist Backend - IONOS + Hugging Face Setup

Production-ready multi-tenant AI voice agent service.

**Architecture:**
- **Inference**: Hugging Face VPS (Llama3/Mistral)
- **Hosting**: IONOS VPS (LiveKit + Agent + Dashboard)
- **STT**: Deepgram (cloud, fast)
- **TTS**: Cartesia (cloud, ultra-low latency)
- **Telephony**: LiveKit SIP + Twilio

## Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo> ultimate-ai-receptionist
cd ultimate-ai-receptionist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
# - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# - HUGGINGFACE_API_URL (your HF VPS endpoint)
# - DEEPGRAM_API_KEY
# - CARTESIA_API_KEY
```

### 3. Deploy on IONOS

```bash
# SSH into IONOS VPS
ssh root@your-ionos-ip

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone <your-repo>
cd ultimate-ai-receptionist

# Copy .env
cp .env.example .env
# Edit .env with your keys

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f agent
```

### 4. Onboard First Client

```bash
python scripts/onboard_new_client.py
```

Follow the prompts to add a client. This creates:
- Client config in `data/clients.json`
- SIP routing rule
- Dashboard URL

### 5. Configure Twilio SIP Trunk

In Twilio Console:
1. Go to **Elastic SIP Trunking** → Create Trunk
2. **Origination URI**: `sip://your-ionos-ip:5060`
3. **Authentication**: Use LiveKit SIP credentials
4. Assign your phone number to this trunk

## Architecture

```
Incoming Call (Twilio)
    ↓ SIP
LiveKit Server (IONOS)
    ↓ WebSocket
Agent Worker
    ├→ Router (phone → client)
    ├→ STT (Deepgram)
    ├→ LLM (Hugging Face VPS)
    ├→ TTS (Cartesia)
    └→ Analytics (SQLite)
    ↓
Dashboard (Flask)
```

## File Structure

```
ultimate-ai-receptionist/
├── config/
│   └── settings.py              # Configuration management
├── services/
│   ├── llm/
│   │   └── huggingface_provider.py  # HF inference calls
│   ├── stt/
│   │   └── deepgram_provider.py     # Cloud STT
│   └── tts/
│       └── cartesia_provider.py     # Cloud TTS
├── agent/
│   ├── base_agent.py            # Main call handler
│   ├── router.py                # Multi-tenant routing
│   └── professions/             # Profession-specific prompts
├── analytics/
│   └── db.py                    # Call logging & revenue tracking
├── ui/
│   └── app.py                   # Flask dashboard
├── scripts/
│   └── onboard_new_client.py    # Client onboarding
├── data/
│   ├── clients.json             # Client database
│   └── analytics.db             # Call analytics
├── entrypoint.py                # LiveKit agent entry point
├── docker-compose.yml           # Container orchestration
├── Dockerfile                   # Container image
└── requirements.txt             # Python dependencies
```

## Environment Variables

```
# LiveKit (IONOS)
LIVEKIT_URL=wss://livekit.yourdomain.com
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# Hugging Face (Remote VPS)
HUGGINGFACE_API_URL=https://your-hf-vps:8000
HUGGINGFACE_API_KEY=optional

# Cloud APIs
DEEPGRAM_API_KEY=your_key
CARTESIA_API_KEY=your_key

# Dashboard
FLASK_SECRET_KEY=random_secret
DASHBOARD_API_KEY=your_api_key
```

## Monitoring

```bash
# View agent logs
docker-compose logs -f agent

# View dashboard logs
docker-compose logs -f dashboard

# Check container status
docker-compose ps

# View call analytics
sqlite3 data/analytics.db "SELECT * FROM calls LIMIT 10;"
```

## Scaling

Each client runs in isolation:
- Separate SIP routing rule
- Separate voice clone
- Separate analytics record
- Shared infrastructure (LiveKit, LLM, STT, TTS)

To add a new client:
```bash
python scripts/onboard_new_client.py
```

## Troubleshooting

**Calls not routing:**
- Check LiveKit SIP trunk configuration
- Verify phone number in `data/clients.json`
- Check agent logs: `docker-compose logs agent`

**LLM not responding:**
- Verify Hugging Face VPS is running
- Check `HUGGINGFACE_API_URL` in .env
- Test: `curl https://your-hf-vps:8000/api/v1/generate`

**Dashboard not loading:**
- Check Flask is running: `docker-compose ps dashboard`
- Verify port 5000 is open on IONOS
- Check logs: `docker-compose logs dashboard`

## Pricing Model

- **$299/month** - Solo Pro (1 phone number)
- **$499/month** - Pro (3 phone numbers)
- **$799/month** - White-Label (unlimited)

All plans include:
- Unlimited minutes
- Voice cloning
- Custom profession scripts
- Real-time dashboard
- 24/7 support

## Revenue Tracking

Dashboard shows:
- Total calls this month
- Revenue captured
- Average call duration
- Sentiment analysis
- Call transcripts

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review `.env` configuration
3. Verify all API keys are valid
4. Test LiveKit connection: `livekit-cli test-connection`

---

**Built with:**
- LiveKit (open-source real-time communication)
- Hugging Face (local LLM inference)
- Deepgram (cloud STT)
- Cartesia (cloud TTS)
- Flask (dashboard)
- Docker (deployment)
