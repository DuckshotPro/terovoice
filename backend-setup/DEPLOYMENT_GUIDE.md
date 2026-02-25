# Deployment Guide: Hugging Face + IONOS Setup

## Your Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INCOMING CALL (Twilio)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ SIP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              IONOS VPS (Docker Containers)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ LiveKit Server (Port 5060 SIP, 7880 WebSocket)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │ Agent Worker (Python)                              │  │
│  │  - Router (phone → client)                         │  │
│  │  - Call handler                                    │  │
│  │  - Analytics logger                               │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │ Flask Dashboard (Port 5000)                        │  │
│  │  - Real-time stats                                 │  │
│  │  - Call logs                                       │  │
│  │  - Revenue tracking                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ SQLite Database (data/analytics.db)                │  │
│  │  - Call records                                    │  │
│  │  - Client stats                                   │  │
│  │  - Revenue tracking                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ HTTPS             │ HTTPS              │ HTTPS
         ▼                    ▼                    ▼
    ┌─────────┐          ┌──────────┐        ┌──────────┐
    │Deepgram │          │Cartesia  │        │Hugging   │
    │(STT)    │          │(TTS)     │        │Face VPS  │
    │Cloud    │          │Cloud     │        │(LLM)     │
    └─────────┘          └──────────┘        └──────────┘
```

## Step-by-Step Deployment

### Phase 1: Prepare IONOS VPS

**1. SSH into IONOS**
```bash
ssh root@your-ionos-ip
```

**2. Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**3. Install Docker Compose**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**4. Clone your repo**
```bash
git clone <your-repo-url> ultimate-ai-receptionist
cd ultimate-ai-receptionist
```

### Phase 2: Configure Environment

**1. Copy .env template**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

**2. Fill in required values:**

```env
# LiveKit (generate these in LiveKit Cloud console)
LIVEKIT_URL=wss://livekit.yourdomain.com
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Your Hugging Face VPS endpoint
HUGGINGFACE_API_URL=https://your-hf-vps-ip:8000
HUGGINGFACE_API_KEY=optional

# Get from Deepgram console
DEEPGRAM_API_KEY=your_deepgram_key

# Get from Cartesia console
CARTESIA_API_KEY=your_cartesia_key

# Generate random strings
FLASK_SECRET_KEY=generate_random_string_here
DASHBOARD_API_KEY=generate_random_string_here
```

### Phase 3: Deploy Containers

**1. Build and start**
```bash
docker-compose up -d --build
```

**2. Verify containers are running**
```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND             STATUS
livekit-server      /livekit server     Up 2 minutes
ai-agent-worker     python entrypoint   Up 2 minutes
ai-dashboard        python -m ui.app    Up 2 minutes
```

**3. Check logs**
```bash
# Agent logs
docker-compose logs -f agent

# Dashboard logs
docker-compose logs -f dashboard

# LiveKit logs
docker-compose logs -f livekit
```

### Phase 4: Configure LiveKit SIP

**1. Get LiveKit credentials**
- Go to LiveKit Cloud console
- Create API key/secret
- Note your LiveKit URL

**2. Configure SIP trunk in LiveKit**

Create `livekit.yaml`:
```yaml
port: 7880
bind_addresses:
  - "0.0.0.0"

sip:
  enabled: true
  port: 5060
  inbound_trunk:
    - name: "twilio-trunk"
      numbers: ["+12025551234"]  # Your Twilio number
      allowed_addresses:
        - "54.172.60.0/23"       # Twilio IP range
        - "54.244.51.0/24"
      auth_username: "twilio"
      auth_password: "your_sip_password"

dispatch_rules:
  - rule_id: "default"
    type: "sip_inbound"
    trunk_ids: ["twilio-trunk"]
    room_prefix: "call-"
    agent_name: "default"
```

### Phase 5: Configure Twilio

**1. Create SIP Trunk in Twilio**
- Go to Elastic SIP Trunking
- Create new trunk
- **Origination URI**: `sip://your-ionos-ip:5060`
- **Authentication**: Use credentials from livekit.yaml

**2. Assign phone number**
- Go to Phone Numbers
- Select your number
- Set SIP Trunk to the one you just created

### Phase 6: Onboard First Client

**1. SSH into IONOS**
```bash
cd ultimate-ai-receptionist
```

**2. Run onboarding script**
```bash
docker-compose exec agent python scripts/onboard_new_client.py
```

**3. Follow prompts**
```
Client name: Dr Mike Dentistry
Phone number: +12025551234
Profession: dentist
Voice ID: af_sarah
```

**4. Verify client was added**
```bash
cat data/clients.json
```

### Phase 7: Test the System

**1. Make a test call**
- Call your Twilio number
- You should hear the AI receptionist answer

**2. Check dashboard**
- Open `https://your-ionos-ip:5000`
- Use `DASHBOARD_API_KEY` from .env
- Should see call logged in real-time

**3. Check analytics**
```bash
docker-compose exec agent sqlite3 data/analytics.db "SELECT * FROM calls LIMIT 5;"
```

## Monitoring & Maintenance

### Daily Checks

```bash
# Check container health
docker-compose ps

# View recent logs
docker-compose logs --tail=50 agent

# Check disk usage
df -h

# Check memory
free -h
```

### Backup Data

```bash
# Backup analytics database
cp data/analytics.db data/analytics.db.backup

# Backup client config
cp data/clients.json data/clients.json.backup
```

### Update Code

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose up -d --build

# Verify
docker-compose ps
```

## Troubleshooting

### Calls not routing

**Check 1: Verify SIP trunk**
```bash
docker-compose logs livekit | grep -i sip
```

**Check 2: Verify client config**
```bash
cat data/clients.json
```

**Check 3: Test LiveKit connection**
```bash
docker-compose exec agent livekit-cli test-connection
```

### LLM not responding

**Check 1: Verify HF VPS is running**
```bash
curl https://your-hf-vps:8000/api/v1/generate
```

**Check 2: Check agent logs**
```bash
docker-compose logs agent | grep -i "hugging\|hf\|llm"
```

**Check 3: Verify .env has correct URL**
```bash
grep HUGGINGFACE .env
```

### Dashboard not loading

**Check 1: Verify Flask is running**
```bash
docker-compose logs dashboard
```

**Check 2: Check port 5000 is open**
```bash
netstat -tlnp | grep 5000
```

**Check 3: Verify API key**
```bash
curl -H "X-API-Key: your_key" http://localhost:5000/api/clients
```

## Scaling to Multiple Clients

Each new client:
1. Gets their own SIP routing rule
2. Gets their own voice clone
3. Gets their own dashboard
4. Shares the same infrastructure

To add a new client:
```bash
docker-compose exec agent python scripts/onboard_new_client.py
```

## Cost Breakdown (Monthly)

| Component | Cost | Notes |
|-----------|------|-------|
| IONOS VPS | $10-20 | 4 vCPU, 8GB RAM |
| Deepgram STT | $0.005/min | ~$15 for 50 clients |
| Cartesia TTS | $0.03/min | ~$90 for 50 clients |
| Twilio SIP | $1 | Per phone number |
| **Total** | **~$120** | For 50 clients @ $499/mo = **$24,950/mo revenue** |

## Next Steps

1. ✅ Deploy containers
2. ✅ Configure LiveKit SIP
3. ✅ Configure Twilio
4. ✅ Onboard first client
5. ⏭️ Set up Stripe billing
6. ⏭️ Create landing page
7. ⏭️ Launch Facebook ads

---

**Questions?** Check the README.md or review the code comments.
