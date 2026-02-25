---
description: Run ESLint to check and fix code quality issues
---

# Lint Workflow

Run this workflow to lint the frontend code.

## Steps

// turbo
1. Run ESLint with auto-fix:
```bash
cd c:\Users\420du\DevEnvironment\Projects\Web\FullStack\ai_website && npm run lint -- --fix
```

2. Report any remaining errors to the user

3. If there are errors that can't be auto-fixed, suggest manual fixes
