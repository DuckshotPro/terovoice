# DP1 Deployment & Changes Log

**Last Updated:** December 26, 2025
**System:** IONOS VPS (74.208.227.161)
**Status:** ✅ Operational

---

## System Overview

### Current Infrastructure
- **Inference Server:** Hugging Face VPS (separate)
- **Main VPS:** IONOS (74.208.227.161)
- **Database:** PostgreSQL 15 with pgvector extension
- **Cache:** Redis 7
- **Container Runtime:** Podman (rootless)
- **LLM Service:** Ollama (running as root)

### Running Services
```
✅ PostgreSQL (port 5432) - Running under ollama user
✅ Redis (port 6379) - Running under ollama user
✅ Ollama (port 11434) - Running as root (/bin/ollama serve)
✅ Podman containers - Created but not all running
```

---

## Changes Made to DP1 System

### 1. MCP Configuration Added
**File:** `.kiro/settings/mcp.json`

**Added pgvector MCP:**
```json
"pgvector": {
  "command": "uvx",
  "args": ["mcp-server-pgvector@latest"],
  "env": {
    "DATABASE_URL": "postgresql://user:cira@74.208.227.161:5432/ai_receptionist"
  },
  "disabled": false,
  "autoApprove": ["query_database", "search_vectors"]
}
```

**Existing MCPs:**
- `fetch` - HTTP requests
- `postgres` - PostgreSQL queries
- `ssh` - SSH command execution
- `github` - GitHub integration
- `notion` - Notion integration

### 2. Database Status
- **Database Name:** `ai_receptionist`
- **User:** `user` (password: `cira`)
- **Port:** 5432
- **Extensions:** pgvector (for vector embeddings)
- **Status:** ✅ Running and accessible

### 3. Ollama Service Status
- **Process:** `/bin/ollama serve`
- **User:** root
- **Port:** 11434
- **Status:** ✅ Running (44:31 uptime)
- **Models:** Available for inference

### 4. Container Status
**Created but not running:**
- `dp1-db01` - PostgreSQL container (port conflict - native PostgreSQL running)
- `dp1-redis01` - Redis container (port conflict - native Redis running)
- `dp1-orch01` - Orchestrator (port 8000)
- `dp1-dash01` - Dashboard (nginx)
- `ducksnap-worker` - Python worker

**Note:** Native services (PostgreSQL, Redis) are running directly on the host, not in containers.

---

## Database Connection Details

### PostgreSQL Access
```bash
# Direct connection
psql -h 74.208.227.161 -U user -d ai_receptionist -p 5432

# Environment variable
export DATABASE_URL="postgresql://user:cira@74.208.227.161:5432/ai_receptionist"
```

### Python Connection
```python
import psycopg2
conn = psycopg2.connect(
    host='74.208.227.161',
    database='ai_receptionist',
    user='user',
    password='cira',
    port=5432
)
```

### pgvector Queries
```sql
-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;

-- Search vectors (example)
SELECT * FROM embeddings
ORDER BY embedding <-> '[0.1, 0.2, 0.3]' LIMIT 5;
```

---

## Known Issues & Resolutions

### Issue 1: Port Conflicts (5432, 6379)
**Problem:** Container startup fails due to ports already in use
**Cause:** Native PostgreSQL and Redis running on host
**Resolution:** Either:
- Stop native services and use containers, OR
- Keep native services and don't start containers

**Current Status:** Native services preferred (more stable)

### Issue 2: psycopg2 Not Available
**Problem:** Python environment restrictions prevent pip install
**Cause:** System-wide Python package management restrictions
**Resolution:** Use virtual environment or container-based Python

### Issue 3: SSH Key Authentication for Sudo
**Problem:** Cannot use SSH keys for sudo commands
**Cause:** Server security restrictions on admin access
**Resolution:** Use direct SSH commands without sudo, or configure passwordless sudo

---

## Troubleshooting Guide

### Check Ollama Status
```bash
ssh cira@74.208.227.161 "ps aux | grep ollama"
```

### Check PostgreSQL Status
```bash
ssh cira@74.208.227.161 "ss -tlnp | grep 5432"
```

### Check Redis Status
```bash
ssh cira@74.208.227.161 "ss -tlnp | grep 6379"
```

### Test Database Connection
```bash
ssh cira@74.208.227.161 "python3 << 'EOF'
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5432))
print('PostgreSQL: ' + ('✅ Connected' if result == 0 else '❌ Failed'))
sock.close()
EOF"
```

### View Container Status
```bash
ssh cira@74.208.227.161 "podman ps -a"
```

### Start Ollama Container (if needed)
```bash
ssh cira@74.208.227.161 "podman start ollama"
```

---

## Maintenance Tasks

### Daily Checks
- [ ] Verify Ollama is running: `ps aux | grep ollama`
- [ ] Check PostgreSQL connectivity: `ss -tlnp | grep 5432`
- [ ] Monitor disk usage: `df -h`
- [ ] Check memory: `free -h`

### Weekly Tasks
- [ ] Backup database: `pg_dump ai_receptionist > backup.sql`
- [ ] Review logs: `journalctl -u ollama -n 100`
- [ ] Check container health: `podman ps -a`

### Monthly Tasks
- [ ] Full system backup
- [ ] Update Ollama models
- [ ] Review and optimize database indexes
- [ ] Audit user access logs

---

## Deployment Checklist

- [x] PostgreSQL running with pgvector
- [x] Redis running for caching
- [x] Ollama service operational
- [x] Database credentials configured
- [x] SSH access verified
- [x] MCP configuration updated
- [ ] Frontend deployment (pending)
- [ ] SSL certificates configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented

---

## Contact & Support

**System Admin:** [Your Name]
**Last Verified:** December 26, 2025
**Next Review:** January 2, 2026

For issues or questions, refer to the SETUP_GUIDE.md file.
