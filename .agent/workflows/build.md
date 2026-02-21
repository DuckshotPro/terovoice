---
description: Build the frontend for production deployment
---

# Build Workflow

Run this workflow to create a production build.

## Steps

// turbo-all

1. Run the production build:
npm run build

2. Check for build errors

3. If successful, report:
   - Build output location (`dist/`)
   - Bundle size if available
   - Ready for deployment status

4. If failed:
   - Show the error message
   - Suggest fixes for common build issues
