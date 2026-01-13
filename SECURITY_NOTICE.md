# Security Notice - Sensitive Files

**CRITICAL**: This document outlines sensitive files that contain API keys and secrets.

---

## Files Containing Secrets

### ⚠️ PAYPAL_INTEGRATION_OPTIONS.md
- **Status**: Added to .gitignore
- **Contains**: PayPal Client ID and Secret Key
- **Action**: NEVER commit this file to Git
- **Location**: Root directory
- **Access**: Local development only

---

## What's Protected

The following sensitive information is in PAYPAL_INTEGRATION_OPTIONS.md:

```
Client ID: AVV11iRY56xUM6Itf80s3RlNmo5bgicA1Y0vRS6nnMuQqelxe4O4K2TsOvpIFlgJSQXBf8uR8peNo1Ud

Secret Key: EOaAuwlOQpjHEVDDqcDFFhQ1Ot3DL-gsZD3a-HxkUoYVKRHf4rhcRnsGCaLQdJq5UxStPqUZ__vD0pKG
```

---

## Security Best Practices

### ✅ DO

1. **Use .env files** for all secrets
   ```bash
   PAYPAL_CLIENT_ID=your_client_id
   PAYPAL_CLIENT_SECRET=your_secret_key
   ```

2. **Add to .gitignore**
   ```
   .env
   .env.local
   PAYPAL_INTEGRATION_OPTIONS.md
   ```

3. **Use environment variables** in code
   ```javascript
   const clientId = process.env.PAYPAL_CLIENT_ID;
   const secret = process.env.PAYPAL_CLIENT_SECRET;
   ```

4. **Rotate keys regularly** (every 90 days recommended)

5. **Use different keys** for sandbox and production

6. **Monitor API usage** for suspicious activity

### ❌ DON'T

1. **Never commit secrets** to Git
2. **Never hardcode** API keys in source code
3. **Never share** secrets in chat, email, or Slack
4. **Never use** the same key for multiple environments
5. **Never log** sensitive information
6. **Never push** to public repositories with secrets

---

## If Secrets Are Compromised

### Immediate Actions

1. **Revoke the key** in PayPal Developer Dashboard
2. **Generate new keys** immediately
3. **Update .env** with new keys
4. **Restart services** to use new keys
5. **Check logs** for unauthorized access
6. **Monitor account** for suspicious activity

### Reporting

If you suspect a security breach:
1. Contact PayPal Security Team immediately
2. Document the incident
3. Review access logs
4. Implement additional monitoring

---

## Git Configuration

### Verify .gitignore is Working

```bash
# Check if file would be ignored
git check-ignore -v PAYPAL_INTEGRATION_OPTIONS.md

# Should output:
# .gitignore:XX:PAYPAL_INTEGRATION_OPTIONS.md  PAYPAL_INTEGRATION_OPTIONS.md
```

### If File Was Already Committed

```bash
# Remove from Git history (DANGEROUS - use with caution)
git rm --cached PAYPAL_INTEGRATION_OPTIONS.md
git commit -m "Remove sensitive file from history"

# Force push (only if you own the repo)
git push origin main --force-with-lease
```

---

## Environment Setup

### Local Development

1. Create `.env.local` file:
   ```bash
   PAYPAL_CLIENT_ID=your_sandbox_client_id
   PAYPAL_CLIENT_SECRET=your_sandbox_secret_key
   PAYPAL_ENVIRONMENT=sandbox
   PAYPAL_WEBHOOK_ID=your_webhook_id
   PAYPAL_WEBHOOK_SECRET=your_webhook_secret
   ```

2. Add to .gitignore:
   ```
   .env.local
   ```

3. Load in your app:
   ```javascript
   import dotenv from 'dotenv';
   dotenv.config({ path: '.env.local' });
   ```

### Production Deployment

1. Use environment variables from your hosting provider:
   - AWS: Secrets Manager or Parameter Store
   - Heroku: Config Vars
   - Docker: Environment variables
   - Kubernetes: Secrets

2. Never commit production secrets

3. Use different keys for production

---

## Monitoring & Alerts

### Set Up Alerts

1. **PayPal Dashboard**
   - Enable email notifications for API activity
   - Monitor for unusual transaction patterns
   - Review API logs regularly

2. **Application Monitoring**
   - Log all API calls (without secrets)
   - Alert on failed authentication
   - Monitor rate limiting

3. **Git Monitoring**
   - Use pre-commit hooks to prevent secret commits
   - Use tools like `git-secrets` or `detect-secrets`

---

## Pre-Commit Hook (Recommended)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Prevent committing sensitive files
if git diff --cached --name-only | grep -E "(PAYPAL_INTEGRATION_OPTIONS|\.env)" > /dev/null; then
    echo "ERROR: Attempting to commit sensitive file!"
    echo "Add to .gitignore and try again."
    exit 1
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Checklist

- [x] PAYPAL_INTEGRATION_OPTIONS.md added to .gitignore
- [ ] All secrets moved to .env.local
- [ ] .env.local added to .gitignore
- [ ] Pre-commit hook installed
- [ ] Team members notified
- [ ] Production secrets configured
- [ ] Monitoring alerts set up
- [ ] Regular key rotation scheduled

---

## References

- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [PayPal Security Best Practices](https://developer.paypal.com/docs/api/overview/)
- [Git Security](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

---

**Last Updated**: January 12, 2026  
**Status**: Active - Review Regularly

