# Week 1 Action Checklist - Tero Voice Launch

**Goal:** Deploy infrastructure and get all systems live
**Timeline:** 7 days
**Status:** Starting today

---

## 📋 Day 1-2: Domain & Branding Setup

### Domain Registration
- [ ] Go to **Namecheap.com** or **Porkbun.com**
- [ ] Search for `terovoice.ai`
- [ ] Register for 1 year (~$10-15)
- [ ] Note the nameservers provided
- [ ] **Time:** 15 minutes

### GitHub Organization
- [ ] Go to **github.com/new/organization**
- [ ] Create organization: `terovoice`
- [ ] Add description: "AI Receptionist That Sounds Human"
- [ ] Create team: `developers`
- [ ] **Time:** 10 minutes

### Docker Registry
- [ ] Go to **hub.docker.com**
- [ ] Create account or login
- [ ] Create organization: `terovoice`
- [ ] Create repositories:
  - `terovoice/backend`
  - `terovoice/frontend`
  - `terovoice/agent`
- [ ] **Time:** 15 minutes

### Email Setup
- [ ] Go to your domain registrar
- [ ] Set up email forwarding:
  - `hello@terovoice.ai` → your email
  - `support@terovoice.ai` → your email
  - `sales@terovoice.ai` → your email
- [ ] **Time:** 10 minutes

**Day 1-2 Total Time:** ~50 minutes

---

## 🖥️ Day 3-4: Backend Deployment

### SSH to IONOS VPS
```bash
# Connect to your VPS
ssh root@74.208.227.161

# Verify you're in the right place
pwd
# Should show: /root or similar

# Navigate to project
cd ultimate-ai-receptionist/backend-setup
ls -la
```

**Checklist:**
- [ ] SSH connection successful
- [ ] Can see backend-setup directory
- [ ] Can see podman-compose.yml
- [ ] Can see .env.example

### Configure Environment
```bash
# Copy example to actual config
cp .env.example .env

# Edit the file
nano .env
```

**Update these values in .env:**
```
# Database
DATABASE_URL=postgresql://user:cira@postgres:5432/ai_receptionist

# JWT
JWT_SECRET=your-super-secret-key-change-this

# API
API_HOST=0.0.0.0
API_PORT=8000

# Domain
API_DOMAIN=api.terovoice.ai

# Stripe (optional for now)
STRIPE_API_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**Checklist:**
- [ ] .env file created
- [ ] DATABASE_URL set correctly
- [ ] JWT_SECRET changed to random value
- [ ] API_DOMAIN set to api.terovoice.ai

### Deploy with Podman
```bash
# Start all services
podman-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Check status
podman-compose ps

# Should show:
# - postgres (healthy)
# - redis (running)
# - api (running)
```

**Checklist:**
- [ ] podman-compose up -d executed
- [ ] All services running
- [ ] No errors in logs

### Verify API is Working
```bash
# Test the API
curl http://localhost:8000/health

# Should return:
# {"status":"healthy"}

# Test database connection
curl http://localhost:8000/api/v1/health

# Should return:
# {"database":"connected","redis":"connected"}
```

**Checklist:**
- [ ] Health endpoint responds
- [ ] Database connected
- [ ] Redis connected
- [ ] No errors

**Day 3-4 Total Time:** ~1.5 hours

---

## 🌐 Day 5-6: Frontend Deployment (Self-Hosted on IONOS)

### Build Frontend Locally
```bash
# From your local machine
cd ultimate-ai-receptionist/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Verify dist folder created
ls -la dist/
```

**Checklist:**
- [ ] npm install completed
- [ ] npm run build completed
- [ ] dist/ folder exists
- [ ] dist/index.html exists

### Push to GitHub
```bash
# From your local machine
cd ultimate-ai-receptionist/frontend

# Initialize git (if not already)
git init
git add .
git commit -m "Initial Tero Voice frontend"

# Add remote
git remote add origin https://github.com/terovoice/frontend.git

# Push to GitHub
git push -u origin main
```

**Checklist:**
- [ ] Code pushed to GitHub
- [ ] Repository is public
- [ ] All files visible on GitHub

### Deploy to IONOS VPS
```bash
# SSH to IONOS
ssh root@74.208.227.161

# Create frontend directory
mkdir -p /var/www/terovoice
cd /var/www/terovoice

# Clone from GitHub
git clone https://github.com/terovoice/frontend.git .

# Install dependencies on server
npm install

# Build on server
npm run build

# Verify build
ls -la dist/
```

**Checklist:**
- [ ] SSH connection successful
- [ ] /var/www/terovoice directory created
- [ ] Code cloned from GitHub
- [ ] npm install completed
- [ ] npm run build completed
- [ ] dist/ folder exists

### Configure Nginx for Frontend
```bash
# SSH to IONOS (if not already connected)
ssh root@74.208.227.161

# Create nginx config for frontend
nano /etc/nginx/sites-available/app.terovoice.ai

# Add this config:
server {
    listen 80;
    server_name app.terovoice.ai;

    root /var/www/terovoice/dist;
    index index.html;

    # Serve static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Route all other requests to index.html (for React Router)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/app.terovoice.ai /etc/nginx/sites-enabled/

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
```

**Checklist:**
- [ ] Nginx config created
- [ ] nginx -t passes
- [ ] Nginx restarted
- [ ] No errors

### Test Frontend
```bash
# Open in browser
http://app.terovoice.ai

# Should see:
# - Tero Voice logo
# - Login page
# - No errors in console
```

**Checklist:**
- [ ] Frontend loads
- [ ] No console errors
- [ ] Can see login page
- [ ] Responsive on mobile
- [ ] API requests work

**Day 5-6 Total Time:** ~1.5 hours

---

## 🔒 Day 7: SSL & Final Testing

### Configure SSL for Backend
```bash
# SSH to IONOS
ssh root@74.208.227.161

# Install certbot
apt-get update
apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot certonly --standalone -d api.terovoice.ai

# Follow prompts and verify email
```

**Checklist:**
- [ ] SSL certificate obtained
- [ ] Certificate stored in /etc/letsencrypt/
- [ ] No errors

### Configure Nginx (if using)
```bash
# Create nginx config
nano /etc/nginx/sites-available/api.terovoice.ai

# Add this config:
server {
    listen 443 ssl;
    server_name api.terovoice.ai;

    ssl_certificate /etc/letsencrypt/live/api.terovoice.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.terovoice.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/api.terovoice.ai /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**Checklist:**
- [ ] Nginx configured
- [ ] SSL certificate linked
- [ ] Nginx restarted
- [ ] No errors

### End-to-End Testing
```bash
# Test API with SSL
curl https://api.terovoice.ai/health

# Should return:
# {"status":"healthy"}

# Test frontend connection
# Open https://app.terovoice.ai
# Try to login (will fail without account, but no CORS errors)
```

**Checklist:**
- [ ] API responds over HTTPS
- [ ] Frontend loads over HTTPS
- [ ] No SSL warnings
- [ ] No CORS errors
- [ ] Database connected
- [ ] All services healthy

### Update DNS Records
- [ ] Go to domain registrar
- [ ] Update DNS records:
  - `api.terovoice.ai` → IONOS VPS IP (74.208.227.161)
  - `app.terovoice.ai` → Vercel nameservers
  - `terovoice.ai` → Vercel nameservers
- [ ] Wait for DNS propagation (5-30 minutes)

**Checklist:**
- [ ] DNS records updated
- [ ] Domains resolving correctly
- [ ] SSL certificates valid

**Day 7 Total Time:** ~1.5 hours

---

## ✅ Week 1 Summary

### What You've Accomplished
- ✅ Registered terovoice.ai domain
- ✅ Set up GitHub organization
- ✅ Set up Docker registry
- ✅ Deployed backend to IONOS
- ✅ Deployed frontend to Vercel
- ✅ Configured SSL certificates
- ✅ Set up email forwarding
- ✅ Verified all systems working

### Services Now Live
- **API:** https://api.terovoice.ai
- **Dashboard:** https://app.terovoice.ai
- **Email:** hello@terovoice.ai, support@terovoice.ai, sales@terovoice.ai
- **GitHub:** github.com/terovoice
- **Docker:** docker.io/terovoice

### Ready for Week 2
- ✅ Infrastructure deployed
- ✅ All systems operational
- ✅ SSL certificates active
- ✅ Domains configured
- ✅ Ready for marketing setup

---

## 📊 Week 1 Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Domain registered | ✅ | |
| Backend deployed | ✅ | |
| Frontend deployed | ✅ | |
| SSL configured | ✅ | |
| All services healthy | ✅ | |
| Zero downtime | ✅ | |

---

## 🚀 Next: Week 2 - Marketing Setup

Once Week 1 is complete, move to Week 2:
- Create landing page
- Set up payment processing
- Create sales materials
- Prepare demo materials

See `TERO_VOICE_LAUNCH_PLAN.md` for Week 2 details.

---

**Status:** ✅ READY TO START
**Timeline:** 7 days
**Estimated Time:** 4-5 hours total
**Next:** Execute Day 1 today!

🚀 **Let's launch Tero Voice!**
