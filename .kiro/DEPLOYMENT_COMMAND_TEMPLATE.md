# Deployment Command Template

**Use this template to provide your server details.**

---

## 📋 Fill In Your Server Details

Replace the placeholders with your actual server information:

```powershell
.\scripts\deploy-phase1-to-server.ps1 `
  -ServerHost "YOUR_SERVER_IP_OR_HOSTNAME" `
  -ServerUser "root" `
  -ProjectDir "/root/ai-phone-sas" `
  -SSHKey ".kiro/private-keys/id_kiro"
```

---

## 🔧 Examples

### Example 1: Using IP Address
```powershell
.\scripts\deploy-phase1-to-server.ps1 `
  -ServerHost "45.76.123.45" `
  -ServerUser "root" `
  -ProjectDir "/root/ai-phone-sas" `
  -SSHKey ".kiro/private-keys/id_kiro"
```

### Example 2: Using Hostname
```powershell
.\scripts\deploy-phase1-to-server.ps1 `
  -ServerHost "vps.yourdomain.com" `
  -ServerUser "root" `
  -ProjectDir "/root/ai-phone-sas" `
  -SSHKey ".kiro/private-keys/id_kiro"
```

### Example 3: Using Different SSH User
```powershell
.\scripts\deploy-phase1-to-server.ps1 `
  -ServerHost "192.168.1.100" `
  -ServerUser "deploy" `
  -ProjectDir "/home/deploy/ai-phone-sas" `
  -SSHKey ".kiro/private-keys/id_kiro"
```

---

## 📝 What to Provide

**Minimum required:**
- `ServerHost`: Your server's IP address or hostname

**Optional (defaults provided):**
- `ServerUser`: SSH username (default: root)
- `ProjectDir`: Project directory on server (default: /root/ai-phone-sas)
- `SSHKey`: Path to SSH key (default: .kiro/private-keys/id_kiro)

---

## 🚀 Once You Have Your Details

1. **Copy the template above**
2. **Replace `YOUR_SERVER_IP_OR_HOSTNAME`** with your actual server address
3. **Run the command** in PowerShell
4. **Watch the deployment** complete in ~5-10 minutes

---

## ✅ Expected Output

When deployment succeeds, you'll see:

```
========================================
Phase 1: Billing Service Deployment
========================================

Step 1: Verifying SSH key...
✅ SSH key found

Step 2: Testing SSH connection...
✅ SSH connection successful

Step 3: Pushing code to server...
✅ Code pushed to repository

Step 4: Pulling latest code on server...
✅ Code pulled on server

Step 5: Installing Python dependencies...
✅ Dependencies installed

Step 6: Creating database tables...
✅ Database tables created

Step 7: Running property-based tests...
✅ Tests completed

Step 8: Verifying deployment...
✅ Deployment verified

========================================
✅ Phase 1 Deployment Complete!
========================================

Deployed Components:
  ✅ BillingService
  ✅ UsageService
  ✅ Usage Database Model
  ✅ Property-Based Tests (20+ tests)

Next Steps:
  1. Verify tests passed on server
  2. Begin Phase 2: Subscription Management
  3. Implement subscription status retrieval
```

---

## 🔍 Troubleshooting

### "Could not resolve hostname"
- Check your server IP/hostname is correct
- Verify server is running
- Try using IP address instead of hostname

### "Permission denied (publickey)"
- Verify SSH key exists: `ls .kiro/private-keys/id_kiro`
- Check key permissions: `chmod 600 .kiro/private-keys/id_kiro`
- Verify server has your public key

### "Connection refused"
- Check SSH port (default 22)
- Verify server is running
- Check firewall allows SSH

---

## 📞 Need Help?

See these files for more information:
- `.kiro/SSH_KEY_SETUP.md` - SSH configuration
- `.kiro/DEPLOYMENT_CHECKLIST_BILLING.md` - Full deployment guide
- `.kiro/BILLING_IMPLEMENTATION_ROADMAP.md` - Phase overview

---

**Ready to deploy?** Provide your server address and I'll run the deployment! 🚀
