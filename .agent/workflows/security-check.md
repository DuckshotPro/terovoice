---
description: Run security audit on dependencies and code
---

# Security Check Workflow

Run this workflow before deployment to check for vulnerabilities.

## Steps

// turbo-all

1. Run npm audit:
```bash
cd c:\Users\420du\DevEnvironment\Projects\Web\FullStack\ai_website && npm audit
```

2. Check for critical/high vulnerabilities in the output

3. If vulnerabilities found:
   - List each vulnerability with severity
   - Suggest `npm audit fix` for auto-fixable issues
   - For breaking changes, suggest `npm audit fix --force` with caution

4. Report security status to user:
   - ✅ All clear - safe to deploy
   - ⚠️ Warnings - review before deploy
   - ❌ Critical issues - must fix before deploy
