# Quick Reference Card

## Deployment Checklist

### Pre-Deployment
- [ ] IONOS VPS rented (4 vCPU, 8GB RAM minimum)
- [ ] Hugging Face VPS running with text-generation-webui
- [ ] Deepgram API key obtained
- [ ] Cartesia API key obtained
- [ ] Twilio account with SIP trunk capability
- [ ] LiveKit Cloud account created

### Deployment
- [ ] SSH into IONOS
- [ ] Install Docker & Docker Compose
- [ ] Clone backend repo
- [ ] Copy .env.example → .env
- [ ] Fill in all API keys
- [ ] Run `docker-compose up -d --build`
- [ ] Verify containers: `docker-compose ps`

### Configuration
- [ ] Configure LiveKit SIP trunk
- [ ] Configure Twilio SIP trunk
- [ ] Test incoming call
- [ ] Verify dashboard loads

### First Client
- [ ] Run `docker-compose exec agent python scripts/onboard_new_client.py`
- [ ] Assign phone number
- [ ] Make test call
- [ ] Check analytics dashboard

## Common Commands

```bash
# View logs
docker-compose logs -f agent
docker-compose logs -f dashboard
docker-compose logs -f livekit

# Check status
docker-compose ps

# Restart services
docker-compose restart agent
docker-compose restart dashboard

# Add new client
docker-compose exec agent python scripts/onboard_new_client.py

# View analytics
docker-compose exec agent sqlite3 data/analytics.db "SELECT * FROM calls LIMIT 10;"

# Backup data
cp data/analytics.db data/analytics.db.backup
cp data/clients.json data/clients.json.backup

# Stop all
docker-compose down

# Rebuild
docker-compose up -d --build
```

## Environment Variables

```env
# Required
LIVEKIT_URL=wss://livekit.yourdomain.com
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
HUGGINGFACE_API_URL=https://your-hf-vps:8000
DEEPGRAM_API_KEY=your_key
CARTESIA_API_KEY=your_key
FLASK_SECRET_KEY=random_string
DASHBOARD_API_KEY=random_string

# Optional
HUGGINGFACE_API_KEY=optional
FLASK_PORT=5000
```

## API Endpoints

```
GET  /api/client/<name>/stats      - Get client stats
GET  /api/client/<name>/calls      - Get recent calls
GET  /api/clients                  - List all clients
POST /api/client                   - Create new client
```

## File Structure

```
ultimate-ai-receptionist/
├── config/settings.py             - Configuration
├── services/llm/huggingface_provider.py - LLM
├── agent/base_agent.py            - Call handler
├── agent/router.py                - Routing
├── analytics/db.py                - Analytics
├── ui/app.py                      - Dashboard
├── entrypoint.py                  - Entry point
├── docker-compose.yml             - Containers
├── requirements.txt               - Dependencies
└── data/
    ├── clients.json               - Client database
    └── analytics.db               - Call logs
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Calls not routing | Check SIP trunk config, verify phone in clients.json |
| LLM not responding | Verify HF VPS is running, check HUGGINGFACE_API_URL |
| Dashboard not loading | Check Flask is running, verify port 5000 is open |
| Containers won't start | Check .env has all required keys, view logs |
| High latency | Check HF VPS GPU usage, reduce max_tokens |

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|-----------|
| STT latency | <500ms | <1s |
| LLM latency | <1s | <2s |
| TTS latency | <500ms | <1s |
| Total latency | <2s | <3s |
| Call success rate | >95% | >90% |

## Pricing

| Plan | Price | Includes |
|------|-------|----------|
| Solo | $299/mo | 1 phone number |
| Pro | $499/mo | 3 phone numbers |
| White-Label | $799/mo | Unlimited |

## Revenue Math

```
50 clients × $499/month = $24,950/month revenue
50 clients × $3.42/month cost = $171/month cost
Profit = $24,779/month (99.3% margin)
```

## Next Steps

1. Deploy on IONOS
2. Configure Twilio
3. Onboard first client
4. Add Stripe billing
5. Launch ads

## Support Resources

- **Deployment**: DEPLOYMENT_GUIDE.md
- **Hugging Face**: HF_SETUP.md
- **Quick Start**: README.md
- **Full Summary**: SUMMARY.md

## Key Contacts

- **LiveKit**: support@livekit.io
- **Deepgram**: support@deepgram.com
- **Cartesia**: support@cartesia.ai
- **Twilio**: support@twilio.com
- **Hugging Face**: support@huggingface.co

---

**Last Updated**: December 2025
**Version**: 1.0
**Status**: Production Ready ✅
