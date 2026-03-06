# Tero Voice - Proper Deployment Structure

**Goal:** Keep everything on IONOS VPS with Podman (no external services)
**Status:** Reorganizing for production deployment

---

## Current State Analysis

### ✅ What We Have (Properly Organized)
```
backend-setup/
├── api/                    # Flask API code
├── db/                     # Database models
├── config/                 # Configuration
├── services/               # Business logic
├── podman-compose.yml      # Container orchestration
├── Dockerfile              # Backend container
├── requirements.txt        # Python dependencies
└── [20+ docs]             # Documentation

src/
├── components/             # React components
├── pages/                  # Page components
├── services/               # API client
├── config/                 # Frontend config
├── styles/                 # CSS/Tailwind
└── App.jsx                # Main app

Root Config Files:
├── package.json            # Frontend dependencies
├── vite.config.js          # Vite build config
├── tailwind.config.js      # Tailwind config
├── tsconfig.json           # TypeScript config
└── index.html              # HTML entry point
```

### ❌ Problem: 50+ Documentation Files in Root
These should be organized:
```
TERO_VOICE_READY.txt
TERO_VOICE_LAUNCH_PLAN.md
TERO_VOICE_BRANDING.md
DEPLOYMENT_READY.md
QUICK_START_MVP.md
README_MVP.md
... 40+ more scattered files
```

---

## Proper Deployment Architecture

### Option 1: Single VPS (Recommended - What You Should Do)

```
IONOS VPS (74.208.227.161)
├── Podman Container 1: Backend API (Flask)
│   ├── Port 8000 (internal)
│   ├── Nginx reverse proxy → https://api.terovoice.ai
│   └── Connected to PostgreSQL
│
├── Podman Container 2: Frontend (Nginx serving React build)
│   ├── Port 3000 (internal)
│   ├── Nginx reverse proxy → https://app.terovoice.ai
│   └── Static files from `npm run build`
│
├── Podman Container 3: Ollama (LLM inference)
│   ├── Port 11434 (internal)
│   └── GPU support
│
├── Podman Container 4: Redis (cache)
│   ├── Port 6379 (internal)
│   └── Session storage
│
├── PostgreSQL (external or container)
│   └── 74.208.227.161:5432
│
└── Nginx (host level)
    ├── Reverse proxy for all containers
    ├── SSL termination (Let's Encrypt)
    ├── api.terovoice.ai → :8000
    └── app.terovoice.ai → :3000
```

**Cost:** $15-30/month (single VPS)
**Complexity:** Low
**Control:** 100%
**Scalability:** Good for 100+ customers

---

## What You Need to Deploy

### 1. Backend (Already Ready)
```
backend-setup/
├── podman-compose.yml      ✅ Ready
├── Dockerfile              ✅ Ready
├── requirements.txt        ✅ Ready
├── api/app.py              ✅ Ready
└── config/                 ✅ Ready
```

### 2. Frontend (Needs Dockerfile)
```
src/                        ✅ Code ready
package.json                ✅ Dependencies ready
vite.config.js              ✅ Build config ready
Dockerfile                  ❌ MISSING - Need to create
nginx.conf                  ❌ MISSING - Need to create
```

### 3. Orchestration (Needs Update)
```
podman-compose.yml          ⚠️ Needs frontend service added
```

### 4. Documentation (Needs Organization)
```
docs/
├── deployment/
│   ├── DEPLOYMENT_READY.md
│   ├── PODMAN_DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── api/
│   └── API_DOCUMENTATION.md
├── brand/
│   ├── TERO_VOICE_BRANDING.md
│   └── TERO_VOICE_LAUNCH_PLAN.md
└── guides/
    ├── QUICK_START_MVP.md
    └── README_MVP.md
```

---

## What's Missing for Deployment

### 1. Frontend Dockerfile
```dockerfile
# Dockerfile for frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Frontend Nginx Config
```nginx
server {
    listen 3000;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Updated podman-compose.yml
Add frontend service:
```yaml
frontend:
  build:
    context: .
    dockerfile: Dockerfile.frontend
  container_name: terovoice-frontend
  ports:
    - "3000:3000"
  depends_on:
    - api
  networks:
    - ai-receptionist
  restart: unless-stopped
```

### 4. Host-level Nginx Config
```nginx
# /etc/nginx/sites-available/terovoice

upstream api {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name api.terovoice.ai app.terovoice.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.terovoice.ai;

    ssl_certificate /etc/letsencrypt/live/api.terovoice.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.terovoice.ai/privkey.pem;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name app.terovoice.ai;

    ssl_certificate /etc/letsencrypt/live/app.terovoice.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.terovoice.ai/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Deployment Checklist

### Phase 1: Prepare Files (Today)
- [ ] Create `Dockerfile.frontend`
- [ ] Create `nginx.conf` for frontend
- [ ] Update `podman-compose.yml` with frontend service
- [ ] Organize documentation into `docs/` folder
- [ ] Test frontend build locally: `npm run build`

### Phase 2: Deploy to IONOS (Day 1-2)
- [ ] SSH to IONOS VPS
- [ ] Install Nginx on host
- [ ] Configure SSL certificates
- [ ] Update podman-compose.yml
- [ ] Run: `podman-compose up -d`
- [ ] Verify all services running

### Phase 3: Configure Domains (Day 3)
- [ ] Point `api.terovoice.ai` to VPS IP
- [ ] Point `app.terovoice.ai` to VPS IP
- [ ] Wait for DNS propagation
- [ ] Test both domains

### Phase 4: Verify (Day 4)
- [ ] Test API: `https://api.terovoice.ai/health`
- [ ] Test Frontend: `https://app.terovoice.ai`
- [ ] Test login flow
- [ ] Check SSL certificates
- [ ] Monitor logs

---

## Why NOT Vercel?

| Factor | Vercel | IONOS VPS |
|--------|--------|----------|
| **Cost** | $20-100/mo | $15-30/mo |
| **Control** | Limited | Full |
| **Deployment** | Git push | podman-compose |
| **Customization** | Limited | Unlimited |
| **Latency** | Good | Better (same server) |
| **Vendor Lock-in** | High | None |
| **Complexity** | Low | Medium |

**Verdict:** Keep everything on IONOS. You already have the VPS, it's cheaper, and you have full control.

---

## File Organization Plan

### Create This Structure
```
docs/
├── deployment/
│   ├── DEPLOYMENT_READY.md
│   ├── PODMAN_DEPLOYMENT.md
│   ├── TROUBLESHOOTING_QUICK_REF.md
│   └── NGINX_CONFIG.md
├── api/
│   ├── API_DOCUMENTATION.md
│   ├── BACKEND_QUICKSTART.md
│   └── ENDPOINTS.md
├── brand/
│   ├── TERO_VOICE_BRANDING.md
│   ├── TERO_VOICE_LAUNCH_PLAN.md
│   └── TERO_VOICE_READY.txt
├── guides/
│   ├── QUICK_START_MVP.md
│   ├── README_MVP.md
│   ├── WEEK1_ACTION_CHECKLIST.md
│   └── MVP_STATUS_AND_NEXT_STEPS.md
└── reference/
    ├── QUICK_REFERENCE.md
    ├── TROUBLESHOOTING_QUICK_REF.md
    └── SYSTEM_STATUS_REPORT.md
```

### Move These Files
```
From root → docs/deployment/
- DEPLOYMENT_READY.md
- PODMAN_DEPLOYMENT.md
- TROUBLESHOOTING_QUICK_REF.md

From root → docs/api/
- API_DOCUMENTATION.md
- BACKEND_QUICKSTART.md

From root → docs/brand/
- TERO_VOICE_BRANDING.md
- TERO_VOICE_LAUNCH_PLAN.md
- TERO_VOICE_READY.txt

From root → docs/guides/
- QUICK_START_MVP.md
- README_MVP.md
- WEEK1_ACTION_CHECKLIST.md
- MVP_STATUS_AND_NEXT_STEPS.md

Delete (Duplicates/Obsolete):
- PHASE1_*.md (old phase docs)
- PHASE2_*.md (old phase docs)
- FRONTEND_INTEGRATION_*.md (old)
- DOCUMENTATION_*.md (old)
- COMPLETION_REPORT.md (old)
- CURRENT_STATE.md (old)
- etc.
```

---

## Next Steps

1. **Create missing deployment files** (Dockerfile.frontend, nginx.conf)
2. **Update podman-compose.yml** to include frontend service
3. **Organize documentation** into docs/ folder
4. **Update WEEK1_ACTION_CHECKLIST.md** to deploy frontend to IONOS (not Vercel)
5. **Test locally** before deploying to IONOS

---

## Summary

**Current:** Scattered files, frontend deployment unclear
**Target:** Everything on IONOS VPS, organized documentation, clear deployment path

**Cost Savings:** $20-100/month (no Vercel)
**Complexity:** Medium (but worth it)
**Control:** 100%

Ready to create the missing files and reorganize?
