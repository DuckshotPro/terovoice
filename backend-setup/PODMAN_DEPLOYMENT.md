# Podman Deployment Guide

**Status:** ✅ Ready for Podman
**Platform:** DP12 (Podman-based)
**Date:** December 26, 2025

---

## 🐳 Podman Setup

### 1. Install Podman (if not already installed)

**On IONOS VPS:**
```bash
# For RHEL/CentOS/Fedora
sudo dnf install -y podman podman-compose

# For Ubuntu/Debian
sudo apt-get install -y podman podman-compose

# Verify installation
podman --version
podman-compose --version
```

### 2. Enable Rootless Podman (Recommended)

```bash
# Set up user namespace
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER

# Enable lingering (keep containers running after logout)
loginctl enable-linger $USER

# Start podman socket
systemctl --user start podman.socket
systemctl --user enable podman.socket
```

---

## 🚀 Deploy with Podman Compose

### 1. Navigate to Backend Directory
```bash
cd backend-setup
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_receptionist
JWT_SECRET=your_random_secret_key_here
FLASK_PORT=8000
DEBUG=False
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 3. Build and Start Containers
```bash
# Build the API image
podman-compose build

# Start all services
podman-compose up -d

# View logs
podman-compose logs -f api
```

### 4. Verify Services Are Running
```bash
# List running containers
podman ps

# Check API health
curl http://localhost:8000/api/health

# Check Ollama
curl http://localhost:11434/api/tags
```

---

## 📊 Container Architecture

```
┌─────────────────────────────────────────┐
│         Podman Network                  │
│  (ai-receptionist)                      │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   API        │  │   Ollama     │   │
│  │ (Flask)      │  │   (LLM)      │   │
│  │ :8000        │  │   :11434     │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐                      │
│  │   Redis      │                      │
│  │   (Cache)    │                      │
│  │   :6379      │                      │
│  └──────────────┘                      │
│                                         │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│   PostgreSQL (External)                 │
│   74.208.227.161:5432                   │
└─────────────────────────────────────────┘
```

---

## 🔧 Common Podman Commands

### View Logs
```bash
# All services
podman-compose logs

# Specific service
podman-compose logs api
podman-compose logs ollama

# Follow logs
podman-compose logs -f api
```

### Stop Services
```bash
# Stop all
podman-compose down

# Stop specific service
podman stop ai-receptionist-api
```

### Restart Services
```bash
# Restart all
podman-compose restart

# Restart specific service
podman-compose restart api
```

### Execute Commands in Container
```bash
# Run command in API container
podman exec ai-receptionist-api python -c "from backend_setup.db.connection import test_connection; test_connection()"

# Interactive shell
podman exec -it ai-receptionist-api /bin/bash
```

### View Container Stats
```bash
# Real-time stats
podman stats

# Specific container
podman stats ai-receptionist-api
```

---

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "ai-receptionist-api",
  "version": "1.0.0"
}
```

### 2. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### 3. Create Client
```bash
TOKEN="<token_from_register>"

curl -X POST http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Mike'\''s Dental",
    "phone_number": "+1-555-0100",
    "profession": "dentist",
    "voice_name": "af_sarah"
  }'
```

---

## 📦 Volume Management

### View Volumes
```bash
podman volume ls
```

### Inspect Volume
```bash
podman volume inspect ollama_data
```

### Backup Volume
```bash
# Backup Ollama models
podman run --rm -v ollama_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ollama_backup.tar.gz -C /data .
```

### Restore Volume
```bash
# Restore Ollama models
podman run --rm -v ollama_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/ollama_backup.tar.gz -C /data
```

---

## 🔒 Security Best Practices

### 1. Use Rootless Podman
```bash
# Already configured above
# Containers run as non-root user
```

### 2. Network Isolation
```bash
# Services only accessible within podman network
# External access through exposed ports only
```

### 3. Environment Variables
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use secrets for sensitive data
podman secret create jwt_secret -
```

### 4. Resource Limits
```bash
# Add to podman-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🚀 Production Deployment

### 1. Create Systemd Service
```bash
sudo tee /etc/systemd/system/ai-receptionist.service > /dev/null <<EOF
[Unit]
Description=AI Receptionist Services
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/backend-setup
ExecStart=/usr/bin/podman-compose up
ExecStop=/usr/bin/podman-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ai-receptionist
sudo systemctl start ai-receptionist
```

### 2. Monitor Service
```bash
# Check status
sudo systemctl status ai-receptionist

# View logs
sudo journalctl -u ai-receptionist -f
```

### 3. Set Up Reverse Proxy (Nginx)
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
podman-compose logs api

# Check image
podman images

# Rebuild image
podman-compose build --no-cache
```

### Database Connection Error
```bash
# Test connection from container
podman exec ai-receptionist-api \
  psql -h 74.208.227.161 -U user -d ai_receptionist -c "SELECT 1"

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in .env
FLASK_PORT=8001
```

### Ollama Models Not Loading
```bash
# Pull model in container
podman exec ollama ollama pull llama3

# Check available models
podman exec ollama ollama list
```

---

## 📊 Monitoring

### CPU and Memory Usage
```bash
podman stats --no-stream
```

### Container Logs
```bash
# Last 100 lines
podman logs --tail 100 ai-receptionist-api

# Follow logs
podman logs -f ai-receptionist-api

# With timestamps
podman logs -f --timestamps ai-receptionist-api
```

### Network Inspection
```bash
# Inspect network
podman network inspect ai-receptionist

# Test connectivity between containers
podman exec ai-receptionist-api ping ollama
```

---

## 🔄 Updates and Maintenance

### Update Container Image
```bash
# Pull latest base images
podman pull python:3.11-slim
podman pull ollama/ollama:latest

# Rebuild
podman-compose build --no-cache

# Restart
podman-compose restart
```

### Clean Up
```bash
# Remove unused images
podman image prune

# Remove unused volumes
podman volume prune

# Remove unused networks
podman network prune

# Full cleanup
podman system prune -a
```

---

## 📝 Deployment Checklist

- [ ] Podman installed
- [ ] Rootless podman configured
- [ ] .env file created and configured
- [ ] Dockerfile builds successfully
- [ ] podman-compose up works
- [ ] Health check passes
- [ ] API endpoints respond
- [ ] Database connection works
- [ ] Ollama service running
- [ ] Redis cache running
- [ ] Logs are clean
- [ ] Systemd service created (production)
- [ ] Reverse proxy configured (production)
- [ ] SSL certificates installed (production)
- [ ] Monitoring set up (production)

---

## 🎯 Next Steps

1. ✅ Backend API containerized
2. 🔄 Deploy to DP12 with podman-compose
3. 🔄 Build React frontend
4. 🔄 Deploy frontend
5. 🔄 Set up monitoring

---

## 📞 Support

### Quick Commands
```bash
# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# View logs
podman-compose logs -f api

# Restart API
podman-compose restart api

# Execute command
podman exec ai-receptionist-api <command>
```

### Documentation
- `BACKEND_QUICKSTART.md` - Quick start guide
- `API_DOCUMENTATION.md` - API reference
- `podman-compose.yml` - Container configuration

---

**Podman deployment ready! 🚀**

Deploy with: `podman-compose up -d`
