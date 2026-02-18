# DP1 System Admin Onboarding Checklist

**For:** New System Administrators
**Duration:** 2-3 hours
**Date Started:** _______________
**Date Completed:** _______________
**Completed By:** _______________

---

## Phase 1: Documentation Review (30 minutes)

### Read Essential Documentation
- [ ] Read `SYSTEM_STATUS_REPORT.md` (5 min)
- [ ] Read `SETUP_GUIDE_ADMIN.md` - Overview section (10 min)
- [ ] Read `TROUBLESHOOTING_QUICK_REF.md` (10 min)
- [ ] Print `TROUBLESHOOTING_QUICK_REF.md` and keep at desk (5 min)

### Understand System Architecture
- [ ] Review system diagram in `SETUP_GUIDE_ADMIN.md`
- [ ] Understand three main services: Ollama, PostgreSQL, Redis
- [ ] Know the server IP: 74.208.227.161
- [ ] Know the database name: ai_receptionist

---

## Phase 2: Access Verification (30 minutes)

### SSH Access
- [ ] Verify SSH key is configured: `ls ~/.ssh/id_rsa`
- [ ] Test SSH connection: `ssh cira@74.208.227.161`
- [ ] Verify you can run commands: `ssh cira@74.208.227.161 "whoami"`
- [ ] Document any access issues: _______________

### Database Access
- [ ] Get database credentials from manager
- [ ] Test database connection: `psql -h 74.208.227.161 -U user -d ai_receptionist`
- [ ] List tables: `\dt`
- [ ] Exit: `\q`
- [ ] Document any connection issues: _______________

### Service Verification
- [ ] Check Ollama: `ssh cira@74.208.227.161 "ps aux | grep ollama"`
- [ ] Check PostgreSQL: `ssh cira@74.208.227.161 "ss -tlnp | grep 5432"`
- [ ] Check Redis: `ssh cira@74.208.227.161 "ss -tlnp | grep 6379"`
- [ ] All services running? Yes [ ] No [ ]

---

## Phase 3: Hands-On Practice (45 minutes)

### Service Management
- [ ] Restart Ollama (practice command)
- [ ] Check PostgreSQL status
- [ ] Check Redis status
- [ ] View system logs: `journalctl -n 50`
- [ ] View Ollama logs (if available)

### Database Operations
- [ ] Connect to database
- [ ] List all tables: `SELECT * FROM information_schema.tables WHERE table_schema='public';`
- [ ] Count records in a table
- [ ] Understand pgvector extension
- [ ] Disconnect from database

### Monitoring
- [ ] Check disk usage: `df -h`
- [ ] Check memory usage: `free -h`
- [ ] Check CPU usage: `top -b -n 1 | head -20`
- [ ] Check network connections: `ss -tlnp`

### Troubleshooting Practice
- [ ] Simulate service failure (stop Ollama)
- [ ] Diagnose the issue
- [ ] Restart the service
- [ ] Verify it's running again

---

## Phase 4: Documentation Review (30 minutes)

### Read Detailed Guides
- [ ] Read `SETUP_GUIDE_ADMIN.md` - Service Management section
- [ ] Read `SETUP_GUIDE_ADMIN.md` - Troubleshooting section
- [ ] Read `SETUP_GUIDE_ADMIN.md` - Backup & Recovery section
- [ ] Read `DEPLOYMENT_LOG.md` - Known Issues section

### Understand Procedures
- [ ] Know how to restart each service
- [ ] Know how to backup the database
- [ ] Know how to restore from backup
- [ ] Know the escalation path

### Create Personal Notes
- [ ] Create a personal cheat sheet
- [ ] Document any custom procedures
- [ ] Note any local variations
- [ ] Save frequently used commands

---

## Phase 5: Knowledge Assessment (15 minutes)

### Answer These Questions

**Q1: What are the three main services?**
A: _______________________________________________

**Q2: How do you check if Ollama is running?**
A: _______________________________________________

**Q3: What's the database connection string?**
A: _______________________________________________

**Q4: How do you restart PostgreSQL?**
A: _______________________________________________

**Q5: What should you do if a service is down?**
A: _______________________________________________

**Q6: Where are the logs located?**
A: _______________________________________________

**Q7: How do you backup the database?**
A: _______________________________________________

**Q8: What's the escalation path?**
A: _______________________________________________

---

## Phase 6: Daily Operations Setup (15 minutes)

### Set Up Monitoring
- [ ] Create daily health check script
- [ ] Set up log monitoring
- [ ] Configure alerts (if available)
- [ ] Test monitoring setup

### Create Personal Tools
- [ ] Create alias for SSH: `alias dp1='ssh cira@74.208.227.161'`
- [ ] Create alias for database: `alias dp1db='psql -h 74.208.227.161 -U user -d ai_receptionist'`
- [ ] Create health check script
- [ ] Save useful commands

### Set Up Workspace
- [ ] Print `TROUBLESHOOTING_QUICK_REF.md`
- [ ] Create quick reference card
- [ ] Set up documentation folder
- [ ] Bookmark important files

---

## Phase 7: Handoff & Sign-Off (15 minutes)

### Meet with Previous Admin
- [ ] Review any custom procedures
- [ ] Discuss known issues
- [ ] Get contact information
- [ ] Ask about recent changes

### Document Handoff
- [ ] Note any special considerations: _______________
- [ ] Note any pending tasks: _______________
- [ ] Note any known issues: _______________
- [ ] Get emergency contact: _______________

### Sign Off
- [ ] I understand the system architecture
- [ ] I can perform basic operations
- [ ] I know how to troubleshoot
- [ ] I know the escalation path
- [ ] I have all necessary documentation

---

## Daily Responsibilities

### Every Day
- [ ] Check service status (5 min)
- [ ] Review error logs (5 min)
- [ ] Monitor disk space (2 min)
- [ ] Monitor memory usage (2 min)

### Every Week
- [ ] Database integrity check (15 min)
- [ ] Backup verification (10 min)
- [ ] Performance review (15 min)

### Every Month
- [ ] Security updates (30 min)
- [ ] Database optimization (30 min)
- [ ] Capacity planning (30 min)

---

## Emergency Procedures

### If Ollama is Down
1. SSH into server
2. Check if process is running: `ps aux | grep ollama`
3. If not running, restart: `pkill -f "ollama serve" && /bin/ollama serve &`
4. Verify: `curl http://localhost:11434/api/tags`
5. If still failing, escalate

### If PostgreSQL is Down
1. SSH into server
2. Check if process is running: `ps aux | grep postgres`
3. If not running, restart: `sudo systemctl restart postgresql`
4. Test connection: `psql -h localhost -U user -d ai_receptionist`
5. If still failing, escalate

### If Redis is Down
1. SSH into server
2. Check if process is running: `ps aux | grep redis`
3. If not running, restart: `sudo systemctl restart redis-server`
4. Test: `redis-cli ping`
5. If still failing, escalate

### If Disk is Full
1. Check usage: `df -h`
2. Find large files: `du -sh /var/lib/containers/*`
3. Clean up: `podman system prune -a`
4. If still full, escalate

---

## Useful Commands to Memorize

```bash
# Quick status check
ps aux | grep -E "ollama|postgres|redis"

# Check ports
ss -tlnp | grep -E "5432|6379|11434"

# SSH into server
ssh cira@74.208.227.161

# Connect to database
psql -h 74.208.227.161 -U user -d ai_receptionist

# View logs
journalctl -n 100 -f

# Check disk
df -h /

# Check memory
free -h

# Restart Ollama
pkill -f "ollama serve" && /bin/ollama serve &

# Restart PostgreSQL
sudo systemctl restart postgresql

# Restart Redis
sudo systemctl restart redis-server
```

---

## Resources

### Documentation Files
- `SYSTEM_STATUS_REPORT.md` - Current status
- `SETUP_GUIDE_ADMIN.md` - Administration guide
- `TROUBLESHOOTING_QUICK_REF.md` - Quick reference (PRINT THIS!)
- `DEPLOYMENT_LOG.md` - Change history
- `DOCUMENTATION_SUMMARY.md` - Documentation index

### External Resources
- PostgreSQL docs: https://www.postgresql.org/docs/
- Redis docs: https://redis.io/documentation
- Ollama docs: https://github.com/ollama/ollama
- Podman docs: https://docs.podman.io/

### Contact Information
- Previous Admin: _______________
- Manager: _______________
- Escalation: _______________
- Emergency: _______________

---

## Sign-Off

**I have completed the onboarding checklist and am ready to manage the DP1 system.**

**New Admin Name:** _______________
**Date:** _______________
**Signature:** _______________

**Verified By:** _______________
**Date:** _______________
**Signature:** _______________

---

## Notes

Use this space for any additional notes or observations:

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

_______________________________________________________________

---

**Congratulations! You are now a DP1 System Administrator.**

**Keep `TROUBLESHOOTING_QUICK_REF.md` at your desk at all times!**

**Questions? Refer to the documentation or contact your manager.**
