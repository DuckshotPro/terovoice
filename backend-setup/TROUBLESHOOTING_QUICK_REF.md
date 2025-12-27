# DP1 Troubleshooting Quick Reference

**Print this page and keep it handy!**

---

## 🚨 Emergency Checks (Do These First)

```bash
# 1. Are services running?
ps aux | grep -E "ollama|postgres|redis"

# 2. Are ports open?
ss -tlnp | grep -E "5432|6379|11434"

# 3. Is disk full?
df -h /

# 4. Is memory full?
free -h
```

---

## ✅ Service Status Quick Check

| Service | Port | Check Command | Expected |
|---------|------|---------------|----------|
| Ollama | 11434 | `ss -tlnp \| grep 11434` | LISTEN |
| PostgreSQL | 5432 | `ss -tlnp \| grep 5432` | LISTEN |
| Redis | 6379 | `ss -tlnp \| grep 6379` | LISTEN |

---

## 🔧 Quick Fixes

### Ollama Not Working
```bash
# Kill and restart
pkill -f "ollama serve"
sleep 2
/bin/ollama serve &

# Test
curl http://localhost:11434/api/tags
```

### PostgreSQL Not Responding
```bash
# Check if running
ps aux | grep postgres

# Restart (may need sudo)
sudo systemctl restart postgresql

# Test connection
python3 << 'EOF'
import socket
sock = socket.socket()
result = sock.connect_ex(('localhost', 5432))
print('✅ OK' if result == 0 else '❌ FAILED')
sock.close()
EOF
```

### Redis Not Responding
```bash
# Check if running
ps aux | grep redis

# Test
redis-cli ping

# Should return: PONG
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :5432  # for PostgreSQL
lsof -i :6379  # for Redis
lsof -i :11434 # for Ollama

# Kill the process (if needed)
kill -9 <PID>
```

---

## 📊 Performance Checks

```bash
# CPU Usage
top -b -n 1 | head -20

# Memory Usage
free -h

# Disk I/O
iostat -x 1 5

# Network
netstat -an | grep ESTABLISHED | wc -l
```

---

## 🔍 Log Locations

| Service | Log Command |
|---------|------------|
| Ollama | `journalctl -u ollama -n 50` |
| PostgreSQL | `journalctl -u postgresql -n 50` |
| System | `journalctl -n 100` |
| Podman | `podman logs container_name` |

---

## 🆘 When Everything Fails

```bash
# 1. Reboot the server (last resort)
sudo reboot

# 2. Check hardware
dmesg | tail -50

# 3. Check disk errors
sudo fsck -n /

# 4. Check system logs
journalctl --priority=err -n 50
```

---

## 📞 Escalation Path

1. **Check this guide** - Most issues are here
2. **Check logs** - `journalctl -n 100`
3. **Restart service** - Kill and restart the process
4. **Reboot server** - Last resort
5. **Contact admin** - If still failing

---

## 🔐 Database Access

```bash
# Connect to database
psql -h 74.208.227.161 -U user -d ai_receptionist

# Or use environment variable
export DATABASE_URL="postgresql://user:cira@74.208.227.161:5432/ai_receptionist"
psql $DATABASE_URL

# List tables
\dt

# Exit
\q
```

---

## 📋 Daily Checklist

- [ ] Ollama running: `ps aux | grep ollama`
- [ ] PostgreSQL running: `ss -tlnp | grep 5432`
- [ ] Redis running: `ss -tlnp | grep 6379`
- [ ] Disk usage < 80%: `df -h /`
- [ ] Memory usage < 90%: `free -h`
- [ ] No error logs: `journalctl --priority=err -n 10`

---

## 🎯 Common Issues & Solutions

### Issue: "Connection refused"
**Solution:** Service not running → Restart it
```bash
ps aux | grep service_name
# If not running, start it
```

### Issue: "Address already in use"
**Solution:** Port conflict → Find and kill process
```bash
lsof -i :port_number
kill -9 <PID>
```

### Issue: "Out of memory"
**Solution:** Memory leak → Restart service
```bash
free -h
pkill -f service_name
sleep 2
# Restart service
```

### Issue: "Disk full"
**Solution:** Clean up space
```bash
df -h
du -sh /var/lib/containers/*
# Remove old containers/images
podman system prune
```

### Issue: "Slow performance"
**Solution:** Check load
```bash
uptime
top -b -n 1 | head -20
# Restart heavy services if needed
```

---

## 🚀 Performance Optimization

```bash
# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches

# Optimize database
psql -U user -d ai_receptionist << 'EOF'
VACUUM ANALYZE;
REINDEX DATABASE ai_receptionist;
EOF

# Clean Podman
podman system prune -a
```

---

## 📱 Remote Access

```bash
# SSH into server
ssh cira@74.208.227.161

# Copy files from server
scp cira@74.208.227.161:/path/to/file ./local/path

# Copy files to server
scp ./local/file cira@74.208.227.161:/remote/path

# Run command remotely
ssh cira@74.208.227.161 "command here"
```

---

## 🔔 Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 80% | > 95% |
| Disk Usage | > 80% | > 95% |
| Load Average | > 4 | > 8 |
| Response Time | > 1s | > 5s |

---

**Last Updated:** December 26, 2025  
**Version:** 1.0  
**Keep this guide accessible!**
