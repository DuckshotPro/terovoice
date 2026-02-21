# DP1 System Setup Guide for System Administrators

**Version:** 1.0
**Date:** December 26, 2025
**Target Audience:** System Administrators & DevOps Engineers

---

## Quick Start

### Verify System Status
```bash
# SSH into server
ssh password@74.208.227.161

# Check all services
ps aux | grep -E "ollama|postgres|redis"

# Check ports
ss -tlnp | grep -E "5432|6379|11434"
```

### Expected Output
```
✅ Ollama: /bin/ollama serve (port 11434)
✅ PostgreSQL: postgres (port 5432)
✅ Redis: redis-server (port 6379)
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IONOS VPS (74.208.227.161)               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Ollama Service (LLM Inference)                       │  │
│  │ - Process: /bin/ollama serve                         │  │
│  │ - Port: 11434                                        │  │
│  │ - User: root                                         │  │
│  │ - Status: ✅ Running                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ PostgreSQL 15 (Database with pgvector)              │  │
│  │ - Port: 5432                                         │  │
│  │ - User: ollama (process owner)                       │  │
│  │ - Database: ai_receptionist                          │  │
│  │ - Extensions: pgvector                               │  │
│  │ - Status: ✅ Running                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Redis 7 (Cache Layer)                               │  │
│  │ - Port: 6379                                         │  │
│  │ - User: ollama (process owner)                       │  │
│  │ - Status: ✅ Running                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Podman Containers (Optional)                         │  │
│  │ - dp1-db01: PostgreSQL container (not running)       │  │
│  │ - dp1-redis01: Redis container (not running)         │  │
│  │ - dp1-orch01: Orchestrator (not running)             │  │
│  │ - dp1-dash01: Dashboard (not running)                │  │
│  │ - ducksnap-worker: Python worker (not running)       │  │
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

---

## Database Configuration

### PostgreSQL Details
```
Host: 74.208.227.161
Port: 5432
Database: ai_receptionist
Username: user
Password: password
```

### Connection String
```
postgresql://user:password@localhost:5432/ai_receptionist
```

### Available Extensions
```sql
-- Check installed extensions
SELECT * FROM pg_extension;

-- pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;
```

### Database Tables
To list all tables:
```bash
ssh password@74.208.227.161 "python3 << 'EOF'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5432))
if result == 0:
    print('✅ PostgreSQL is accessible on port 5432')
else:
    print('❌ Cannot connect to PostgreSQL')
sock.close()
EOF"
```

---

## Service Management

### Ollama Service

**Check Status:**
```bash
ssh password@74.208.227.161 "ps aux | grep 'ollama serve'"
```

**Restart Ollama:**
```bash
ssh password@74.208.227.161 "pkill -f 'ollama serve' && sleep 2 && /bin/ollama serve &"
```

**View Logs:**
```bash
ssh password@74.208.227.161 "journalctl -u ollama -n 50 -f"
```

### PostgreSQL Service

**Check Status:**
```bash
ssh password@74.208.227.161 "ps aux | grep postgres | head -1"
```

**Restart PostgreSQL:**
```bash
ssh password@74.208.227.161 "sudo systemctl restart postgresql"
```

**Note:** May require sudo password or passwordless sudo configuration.

### Redis Service

**Check Status:**
```bash
ssh password@74.208.227.161 "ps aux | grep redis-server"
```

**Test Connection:**
```bash
ssh password@74.208.227.161 "redis-cli ping"
```

---

## Troubleshooting

### Problem: Ollama Not Responding

**Symptoms:**
- Cannot connect to port 11434
- Inference requests timeout

**Solution:**
```bash
# 1. Check if process is running
ssh password@74.208.227.161 "ps aux | grep ollama"

# 2. Check port
ssh password@74.208.227.161 "ss -tlnp | grep 11434"

# 3. Restart service
ssh password@74.208.227.161 "pkill -f 'ollama serve'"
sleep 2
ssh password@74.208.227.161 "/bin/ollama serve &"

# 4. Verify
ssh password@74.208.227.161 "curl http://localhost:11434/api/tags"
```

### Problem: PostgreSQL Connection Failed

**Symptoms:**
- "Connection refused" errors
- Cannot query database

**Solution:**
```bash
# 1. Check if PostgreSQL is running
ssh password@74.208.227.161 "ps aux | grep postgres"

# 2. Check port
ssh password@74.208.227.161 "ss -tlnp | grep 5432"

# 3. Test connection
ssh password@74.208.227.161 "python3 << 'EOF'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5432))
print('Connected' if result == 0 else 'Failed')
sock.close()
EOF"

# 4. Restart PostgreSQL (may need sudo)
ssh password@74.208.227.161 "sudo systemctl restart postgresql"
```

### Problem: Port Already in Use

**Symptoms:**
- "Address already in use" when starting containers
- Ports 5432, 6379 conflicts

**Solution:**
```bash
# Option 1: Use native services (current setup)
# Keep PostgreSQL and Redis running on host

# Option 2: Stop native services and use containers
ssh password@74.208.227.161 "sudo systemctl stop postgresql redis-server"
ssh password@74.208.227.161 "podman start dp1-db01 dp1-redis01"

# Option 3: Change container ports
# Edit podman-compose.yml to use different ports (e.g., 5433, 6380)
```

### Problem: High Memory Usage

**Symptoms:**
- System slow or unresponsive
- OOM killer messages

**Solution:**
```bash
# Check memory usage
ssh password@74.208.227.161 "free -h"

# Check process memory
ssh password@74.208.227.161 "ps aux --sort=-%mem | head -10"

# If Ollama is using too much:
ssh password@74.208.227.161 "pkill -f 'ollama serve'"

# Restart with memory limit (if using containers)
ssh password@74.208.227.161 "podman run --memory=4g ollama/ollama"
```

---

## Backup & Recovery

### Backup Database
```bash
ssh password@74.208.227.161 "pg_dump -U user -d ai_receptionist > /tmp/ai_receptionist_backup.sql"
scp password@74.208.227.161:/tmp/ai_receptionist_backup.sql ./backups/
```

### Restore Database
```bash
scp ./backups/ai_receptionist_backup.sql password@74.208.227.161:/tmp/
ssh password@74.208.227.161 "psql -U user -d ai_receptionist < /tmp/ai_receptionist_backup.sql"
```

### Backup Configuration
```bash
ssh password@74.208.227.161 "tar -czf /tmp/dp1_config_backup.tar.gz /home/password/config /home/password/.env"
scp password@74.208.227.161:/tmp/dp1_config_backup.tar.gz ./backups/
```

---

## Monitoring & Alerts

### Key Metrics to Monitor
- Ollama process status
- PostgreSQL connection count
- Redis memory usage
- Disk space (especially /var/lib/containers)
- Network latency to Hugging Face VPS

### Recommended Monitoring Tools
- `htop` - Real-time process monitoring
- `iotop` - Disk I/O monitoring
- `nethogs` - Network monitoring
- `prometheus` + `grafana` - Full monitoring stack

### Health Check Script
```bash
#!/bin/bash
# Save as: /home/password/health_check.sh

echo "=== DP1 System Health Check ==="
echo ""

echo "1. Ollama Status:"
ps aux | grep -q "ollama serve" && echo "   ✅ Running" || echo "   ❌ Not running"

echo "2. PostgreSQL Status:"
ss -tlnp | grep -q 5432 && echo "   ✅ Running" || echo "   ❌ Not running"

echo "3. Redis Status:"
ss -tlnp | grep -q 6379 && echo "   ✅ Running" || echo "   ❌ Not running"

echo "4. Disk Usage:"
df -h / | tail -1

echo "5. Memory Usage:"
free -h | grep Mem

echo "6. Load Average:"
uptime | awk -F'load average:' '{print $2}'
```

---

## Security Considerations

### Database Security
- [ ] Change default password for `user` account
- [ ] Restrict PostgreSQL access to localhost only
- [ ] Enable SSL/TLS for remote connections
- [ ] Regular security updates

### SSH Security
- [ ] Disable password authentication
- [ ] Use SSH keys only
- [ ] Restrict SSH access by IP
- [ ] Monitor failed login attempts

### Service Security
- [ ] Run services with minimal privileges
- [ ] Use firewall rules to restrict ports
- [ ] Enable audit logging
- [ ] Regular security patches

---

## Maintenance Schedule

### Daily
- [ ] Check service status
- [ ] Monitor disk space
- [ ] Review error logs

### Weekly
- [ ] Database integrity check
- [ ] Backup verification
- [ ] Performance review

### Monthly
- [ ] Security updates
- [ ] Database optimization
- [ ] Capacity planning

### Quarterly
- [ ] Full system audit
- [ ] Disaster recovery drill
- [ ] Documentation update

---

## Contact Information

**System Owner:** [Your Name]
**Email:** [Your Email]
**Phone:** [Your Phone]
**Escalation:** [Escalation Contact]

**Last Updated:** December 26, 2025
**Next Review:** January 26, 2026

---

## Appendix: Useful Commands

```bash
# SSH into server
ssh password@74.208.227.161

# Check all running services
ps aux | grep -E "ollama|postgres|redis"

# Monitor real-time
watch -n 1 'ps aux | grep -E "ollama|postgres|redis"'

# Check network connections
ss -tlnp

# View system logs
journalctl -n 100 -f

# Check disk usage
du -sh /var/lib/containers/*

# List Podman containers
podman ps -a

# View container logs
podman logs -f container_name

# Test database connection
python3 -c "import psycopg2; psycopg2.connect('postgresql://user:password@localhost/ai_receptionist')"

# Test Ollama
curl http://localhost:11434/api/tags

# Test Redis
redis-cli ping
```

---

**End of Setup Guide**
