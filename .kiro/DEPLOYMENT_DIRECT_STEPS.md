# Direct Deployment Steps - Phase 1 Billing Service

**Status:** Ready to Deploy  
**Date:** January 12, 2025  
**Server:** 74.208.227.161 (cira user)

---

## Quick Connectivity Test

Before running the full deployment, test SSH connectivity manually:

```bash
# Test SSH connection (should respond immediately)
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "echo 'Connected'"

# If that works, test Python availability
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "python3 --version"
```

---

## Manual Deployment Steps (If Script Times Out)

If the automated script times out, follow these manual steps:

### Step 1: Transfer Files via SCP

```bash
# Create project directory on server
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "mkdir -p /home/cira/ai-phone-sas/backend-setup/{services,db,tests}"

# Transfer backend services
scp -i .kiro/private-keys/id_kiro backend-setup/services/billing_service.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/services/
scp -i .kiro/private-keys/id_kiro backend-setup/services/usage_service.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/services/
scp -i .kiro/private-keys/id_kiro backend-setup/services/__init__.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/services/

# Transfer database models
scp -i .kiro/private-keys/id_kiro backend-setup/db/models.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/db/

# Transfer tests
scp -i .kiro/private-keys/id_kiro backend-setup/tests/test_billing_service_properties.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/tests/
scp -i .kiro/private-keys/id_kiro backend-setup/tests/__init__.py cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/tests/

# Transfer requirements
scp -i .kiro/private-keys/id_kiro backend-setup/requirements.txt cira@74.208.227.161:/home/cira/ai-phone-sas/backend-setup/
```

### Step 2: Set Up Virtual Environment

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira/ai-phone-sas
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r backend-setup/requirements.txt
EOF
```

### Step 3: Create Database Tables

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira/ai-phone-sas
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from backend_setup.db.models import Base
from backend_setup.db.connection import engine
Base.metadata.create_all(engine)
print('✅ Database tables created')
PYEOF
EOF
```

### Step 4: Run Tests

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira/ai-phone-sas
source venv/bin/activate
python3 -m pytest backend-setup/tests/test_billing_service_properties.py -v
EOF
```

### Step 5: Verify Deployment

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira/ai-phone-sas
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from backend_setup.services import BillingService, UsageService
from backend_setup.db.models import Subscription, Usage, Invoice
print('✅ All services and models imported successfully')
print('✅ Deployment verified!')
PYEOF
EOF
```

---

## Troubleshooting

### SSH Connection Hangs

**Symptom:** SSH command hangs or times out

**Solutions:**
1. Check if server is reachable: `ping 74.208.227.161`
2. Try with explicit timeout: `ssh -o ConnectTimeout=10 -i .kiro/private-keys/id_kiro cira@74.208.227.161 "echo test"`
3. Check SSH key permissions: `ls -la .kiro/private-keys/id_kiro` (should be 600)
4. Verify SSH key is correct: `ssh-keygen -l -f .kiro/private-keys/id_kiro`

### Python Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'backend_setup'`

**Solution:** Ensure `sys.path.insert(0, '.')` is at the top of Python scripts

### Virtual Environment Issues

**Symptom:** `command not found: python3` or pip errors

**Solution:** 
```bash
# Check Python installation
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "which python3"

# If not found, install Python
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
```

---

## Files Ready for Transfer

All these files are ready in the local workspace:

```
✅ backend-setup/services/billing_service.py (300+ lines)
✅ backend-setup/services/usage_service.py (200+ lines)
✅ backend-setup/services/__init__.py
✅ backend-setup/db/models.py (with Usage model)
✅ backend-setup/tests/test_billing_service_properties.py (20+ tests)
✅ backend-setup/tests/__init__.py
✅ backend-setup/requirements.txt (with pytest, hypothesis)
```

---

## Next Steps After Successful Deployment

1. ✅ Verify all tests pass on server
2. ✅ Confirm services can be imported
3. ✅ Begin Phase 2: Subscription Status Retrieval
4. ✅ Implement PayPal API integration

---

## Quick Reference Commands

```bash
# Test connectivity
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "echo 'OK'"

# Check server status
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "uname -a"

# List deployed files
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "ls -la /home/cira/ai-phone-sas/backend-setup/"

# Run tests again
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "cd /home/cira/ai-phone-sas && source venv/bin/activate && python3 -m pytest backend-setup/tests/ -v"

# Check virtual environment
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "cd /home/cira/ai-phone-sas && source venv/bin/activate && pip list"
```

---

**Status:** Ready for manual deployment  
**Action:** Run connectivity test first, then follow manual steps if script times out  
**Support:** All files are prepared and ready to transfer

