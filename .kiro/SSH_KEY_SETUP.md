# SSH Key Setup for Server Deployment

**Status:** ✅ Complete
**Date:** January 12, 2025

---

## 📁 SSH Keys Location

All SSH keys have been moved to the private Kiro directory for security:

```
.kiro/private-keys/
├── id_ed25519      # ED25519 SSH key
└── id_kiro         # Primary SSH key for server access
```

**Security:** These keys are stored in the private Kiro directory and should never be committed to git.

---

## 🔐 Key Files

### id_kiro
- **Purpose:** Primary SSH key for connecting to the AI Phone SaaS server
- **Type:** RSA or ED25519 (depending on server configuration)
- **Permissions:** Read-only (restricted to owner)
- **Usage:** `ssh -i .kiro/private-keys/id_kiro root@ai-phone-sas`

### id_ed25519
- **Purpose:** Alternative ED25519 SSH key
- **Type:** ED25519
- **Permissions:** Read-only (restricted to owner)
- **Usage:** `ssh -i .kiro/private-keys/id_ed25519 root@ai-phone-sas`

---

## 🚀 Deployment Scripts

Two deployment scripts have been created to automate Phase 1 deployment:

### Bash Script (Linux/Mac)
```bash
./scripts/deploy-phase1-to-server.sh
```

**What it does:**
1. Verifies SSH key exists
2. Tests SSH connection to server
3. Pushes code to git repository
4. Pulls latest code on server
5. Installs Python dependencies
6. Creates database tables
7. Runs property-based tests
8. Verifies deployment

### PowerShell Script (Windows)
```powershell
.\scripts\deploy-phase1-to-server.ps1
```

**Parameters:**
- `-ServerHost` (default: "ai-phone-sas")
- `-ServerUser` (default: "root")
- `-ProjectDir` (default: "/root/ai-phone-sas")
- `-SSHKey` (default: ".kiro/private-keys/id_kiro")

**Example:**
```powershell
.\scripts\deploy-phase1-to-server.ps1 -ServerHost "your-server.com" -ServerUser "deploy"
```

---

## 📋 Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### Step 1: Connect to Server
```bash
ssh -i .kiro/private-keys/id_kiro root@ai-phone-sas
```

### Step 2: Navigate to Project
```bash
cd /root/ai-phone-sas
```

### Step 3: Pull Latest Code
```bash
git pull origin main
```

### Step 4: Install Dependencies
```bash
pip install -r backend-setup/requirements.txt
```

### Step 5: Create Database Tables
```bash
python << 'EOF'
from backend_setup.db.models import Base
from backend_setup.db.connection import engine
Base.metadata.create_all(engine)
print('✅ Database tables created successfully')
EOF
```

### Step 6: Run Tests
```bash
python -m pytest backend-setup/tests/test_billing_service_properties.py -v
```

### Step 7: Verify Deployment
```bash
python << 'EOF'
from backend_setup.services import BillingService, UsageService
from backend_setup.db.models import Subscription, Usage, Invoice
print('✅ Services imported successfully')
print('✅ Models imported successfully')
print('✅ Deployment verified!')
EOF
```

---

## 🔒 Security Best Practices

### ✅ DO
- Keep SSH keys in `.kiro/private-keys/` directory
- Use restrictive file permissions (read-only for owner)
- Never commit SSH keys to git
- Use SSH keys instead of passwords
- Rotate keys periodically
- Use different keys for different servers

### ❌ DON'T
- Share SSH keys via email or chat
- Commit SSH keys to git repository
- Use the same key for multiple servers
- Store keys in plain text outside `.kiro/private-keys/`
- Use weak or default passwords
- Leave SSH keys unencrypted on shared machines

---

## 📝 .gitignore Configuration

The `.kiro/private-keys/` directory should be in `.gitignore`:

```
# SSH Keys
.kiro/private-keys/
.kiro/private-keys/*
!.kiro/private-keys/.gitkeep
```

This ensures SSH keys are never accidentally committed to git.

---

## 🔧 Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution:**
1. Verify SSH key exists: `ls -la .kiro/private-keys/id_kiro`
2. Check key permissions: `chmod 600 .kiro/private-keys/id_kiro`
3. Verify server has public key: `ssh-keyscan ai-phone-sas`

### Issue: "SSH connection timeout"
**Solution:**
1. Verify server is running
2. Check server hostname/IP: `ping ai-phone-sas`
3. Verify SSH port is open: `ssh -v -i .kiro/private-keys/id_kiro root@ai-phone-sas`

### Issue: "No such file or directory"
**Solution:**
1. Verify SSH key path is correct
2. Check working directory: `pwd`
3. Use absolute path if needed: `/full/path/to/.kiro/private-keys/id_kiro`

---

## 📊 Deployment Status

| Component | Status | Location |
|-----------|--------|----------|
| SSH Keys | ✅ Stored | `.kiro/private-keys/` |
| Bash Script | ✅ Created | `scripts/deploy-phase1-to-server.sh` |
| PowerShell Script | ✅ Created | `scripts/deploy-phase1-to-server.ps1` |
| Documentation | ✅ Complete | `.kiro/SSH_KEY_SETUP.md` |

---

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

**On Linux/Mac:**
```bash
chmod +x scripts/deploy-phase1-to-server.sh
./scripts/deploy-phase1-to-server.sh
```

**On Windows:**
```powershell
.\scripts\deploy-phase1-to-server.ps1
```

### Option 2: Manual Deployment

Follow the manual steps in the "Manual Deployment Steps" section above.

---

## 📞 Support

For deployment issues:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review `.kiro/DEPLOYMENT_CHECKLIST_BILLING.md`
3. Check SSH key permissions: `ls -la .kiro/private-keys/`
4. Verify server connectivity: `ssh -i .kiro/private-keys/id_kiro root@ai-phone-sas "echo 'Connected'"`

---

## ✅ Next Steps

1. **Run Deployment Script:**
   - Bash: `./scripts/deploy-phase1-to-server.sh`
   - PowerShell: `.\scripts\deploy-phase1-to-server.ps1`

2. **Verify Deployment:**
   - Check test output
   - Verify services imported successfully
   - Confirm database tables created

3. **Begin Phase 2:**
   - Review `.kiro/BILLING_IMPLEMENTATION_ROADMAP.md`
   - Start Task 2: Subscription Management
   - Implement subscription status retrieval

---

**Last Updated:** January 12, 2025
**Status:** Ready for Deployment
