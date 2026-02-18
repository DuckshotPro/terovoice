# Hugging Face VPS Setup for Inference

Your LLM inference runs on Hugging Face VPS. This guide shows how to set it up.

## Option 1: Hugging Face Spaces (Easiest)

**1. Create a Space**
- Go to huggingface.co/spaces
- Click "Create new Space"
- Choose "Docker" runtime
- Name: `ai-receptionist-llm`

**2. Use text-generation-webui Docker image**

Create `Dockerfile`:
```dockerfile
FROM ghcr.io/oobabooga/text-generation-webui:latest

# Install Llama3
RUN python download-model.py TheBloke/Llama-2-7B-Chat-GGUF

EXPOSE 5000 5001 5002 5003 5004 5005 5006 5007 5008 5009

CMD ["python", "server.py", "--listen", "0.0.0.0", "--api"]
```

**3. Deploy**
- Push to your Space
- HF will build and host it
- Get the API endpoint from Space settings

## Option 2: Hugging Face Inference API (Simplest)

**1. Get API token**
- Go to huggingface.co/settings/tokens
- Create new token with "Inference" permission

**2. Update .env**
```env
HUGGINGFACE_API_URL=https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf
HUGGINGFACE_API_KEY=hf_your_token_here
```

**3. Update huggingface_provider.py**
```python
# Use HF Inference API instead of local endpoint
response = await self.client.post(
    f"{self.api_url}",
    json={"inputs": full_prompt},
    headers={"Authorization": f"Bearer {self.api_key}"}
)
```

## Option 3: Self-Hosted on Hugging Face VPS (Recommended)

**1. Rent a Hugging Face VPS**
- Go to huggingface.co/hardware
- Choose GPU instance (A100 or H100)
- Cost: $1-3/hour

**2. SSH into VPS**
```bash
ssh root@your-hf-vps-ip
```

**3. Install text-generation-webui**
```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui

# Install dependencies
pip install -r requirements.txt

# Download Llama3
python download-model.py meta-llama/Llama-2-7b-chat-hf
```

**4. Start API server**
```bash
python server.py --listen 0.0.0.0 --api --port 8000
```

**5. Test the endpoint**
```bash
curl -X POST https://your-hf-vps:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "max_new_tokens": 100
  }'
```

**6. Update .env**
```env
HUGGINGFACE_API_URL=https://your-hf-vps:8000
HUGGINGFACE_API_KEY=optional
```

## Performance Tuning

### For Llama3 8B (Recommended)

```bash
# Start with quantization for speed
python server.py \
  --listen 0.0.0.0 \
  --api \
  --port 8000 \
  --model meta-llama/Llama-2-7b-chat-hf \
  --load-in-8bit \
  --max-seq-len 2048
```

**Expected latency:**
- First token: 200-400ms
- Subsequent tokens: 50-100ms each
- Total response (50 tokens): 2-5 seconds

### For Llama3 70B (Faster but needs more VRAM)

```bash
python server.py \
  --listen 0.0.0.0 \
  --api \
  --port 8000 \
  --model meta-llama/Llama-2-70b-chat-hf \
  --load-in-4bit \
  --max-seq-len 4096
```

**Expected latency:**
- First token: 100-200ms
- Subsequent tokens: 30-50ms each
- Total response (50 tokens): 1.5-3 seconds

## Monitoring HF VPS

```bash
# Check GPU usage
nvidia-smi

# Check memory
free -h

# Check disk
df -h

# View API logs
tail -f logs/api.log
```

## Cost Comparison

| Option | Cost | Latency | Setup Time |
|--------|------|---------|-----------|
| HF Spaces | Free | 5-10s | 5 min |
| HF Inference API | $0.06/1k tokens | 2-3s | 2 min |
| Self-hosted VPS | $1-3/hour | 1-2s | 30 min |

## Recommended Setup

For production with 50+ clients:

**Use self-hosted on Hugging Face VPS:**
- Cost: ~$50-100/month (A100 instance)
- Latency: 1-2 seconds (acceptable for phone)
- Throughput: 100+ concurrent calls

**Configuration:**
```bash
# Start script (save as start-api.sh)
#!/bin/bash
cd /root/text-generation-webui
python server.py \
  --listen 0.0.0.0 \
  --api \
  --port 8000 \
  --model meta-llama/Llama-2-7b-chat-hf \
  --load-in-8bit \
  --max-seq-len 2048 \
  --n-gpu-layers 40
```

**Systemd service (save as /etc/systemd/system/hf-api.service):**
```ini
[Unit]
Description=Hugging Face API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/text-generation-webui
ExecStart=/bin/bash /root/start-api.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
systemctl enable hf-api
systemctl start hf-api
systemctl status hf-api
```

## Integration with IONOS Agent

Your IONOS agent calls the HF VPS like this:

```python
# From services/llm/huggingface_provider.py
response = await self.client.post(
    f"{self.api_url}/api/v1/generate",
    json={
        "prompt": full_prompt,
        "max_new_tokens": 256,
        "temperature": 0.7,
    }
)
```

**Network flow:**
```
IONOS Agent (5000 clients)
    ↓ HTTPS
Hugging Face VPS (LLM inference)
    ↓ Response
IONOS Agent
    ↓ TTS
Cartesia (voice synthesis)
```

## Troubleshooting

### API not responding

```bash
# Check if server is running
ps aux | grep server.py

# Check port 8000
netstat -tlnp | grep 8000

# Restart
systemctl restart hf-api
```

### Slow responses

```bash
# Check GPU usage
nvidia-smi

# Check memory
free -h

# If memory full, reduce batch size or use quantization
```

### Connection refused

```bash
# Check firewall
ufw status

# Allow port 8000
ufw allow 8000

# Check if listening on 0.0.0.0
netstat -tlnp | grep 8000
```

## Next Steps

1. ✅ Set up HF VPS with text-generation-webui
2. ✅ Test API endpoint
3. ✅ Update IONOS .env with HF URL
4. ✅ Deploy IONOS containers
5. ✅ Make test call

---

**Your final setup:**
- **IONOS**: LiveKit + Agent + Dashboard ($10-20/mo)
- **Hugging Face**: Llama3 inference ($50-100/mo)
- **Deepgram**: STT ($15/mo for 50 clients)
- **Cartesia**: TTS ($90/mo for 50 clients)
- **Twilio**: SIP ($1/mo per number)
- **Total**: ~$170/mo for 50 clients @ $499/mo = **$24,650/mo profit**
