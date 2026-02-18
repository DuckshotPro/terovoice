# Podman Container Deployment Strategy - Phase 1 Billing Service

**Status:** Revised for Podman Architecture
**Date:** January 12, 2025
**Server:** 74.208.227.161 (cira user, Podman rootless)

---

## Understanding Podman Rootless Deployment

Since the server uses **Podman rootless containers**, we need to:

1. **Build a container image** with all dependencies
2. **Push to container registry** (or transfer tar file)
3. **Run container** with proper volume mounts
4. **Persist data** across container restarts

This is fundamentally different from direct SSH deployment.

---

## Deployment Architecture

```
Local Machine
    ↓
Build Docker/Podman image with Phase 1 code
    ↓
Transfer image to server (via tar or registry)
    ↓
Server (Podman rootless)
    ↓
Run container with volumes for:
  - Code
  - Database
  - Logs
    ↓
Tests run inside container
    ↓
Verify deployment
```

---

## Option 1: Dockerfile-Based Deployment (Recommended)

### Step 1: Create Dockerfile

Create `Dockerfile.billing-phase1` in project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY backend-setup/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend-setup/ ./backend-setup/

# Create data directory for database
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command: run tests
CMD ["python3", "-m", "pytest", "backend-setup/tests/test_billing_service_properties.py", "-v"]
```

### Step 2: Build Image Locally

```bash
# Build the image
podman build -f Dockerfile.billing-phase1 -t billing-service:phase1 .

# Verify image
podman images | grep billing-service
```

### Step 3: Transfer Image to Server

**Option A: Via tar file (no registry needed)**

```bash
# Save image as tar
podman save billing-service:phase1 -o billing-service-phase1.tar

# Transfer to server
scp -i .kiro/private-keys/id_kiro billing-service-phase1.tar cira@74.208.227.161:/home/cira/

# On server: Load image
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira
podman load -i billing-service-phase1.tar
podman images | grep billing-service
EOF
```

**Option B: Via Docker Hub or private registry**

```bash
# Tag for registry
podman tag billing-service:phase1 yourusername/billing-service:phase1

# Push to registry
podman push yourusername/billing-service:phase1

# On server: Pull image
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman pull yourusername/billing-service:phase1"
```

### Step 4: Run Container on Server

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
# Create data directory
mkdir -p /home/cira/ai-phone-sas/data

# Run container with volume mounts
podman run --rm \
  -v /home/cira/ai-phone-sas/data:/app/data \
  -e PYTHONUNBUFFERED=1 \
  billing-service:phase1

# This will run tests and exit
EOF
```

### Step 5: Run Container as Service (Persistent)

For long-running service:

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
# Create systemd user service
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/billing-service.service << 'SYSTEMD'
[Unit]
Description=Billing Service Container
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=10
ExecStart=podman run --rm \
  --name billing-service \
  -v /home/cira/ai-phone-sas/data:/app/data \
  -e PYTHONUNBUFFERED=1 \
  billing-service:phase1 \
  python3 -c "from backend_setup.services import BillingService; print('Service running')"

[Install]
WantedBy=default.target
SYSTEMD

# Enable and start service
systemctl --user daemon-reload
systemctl --user enable billing-service
systemctl --user start billing-service

# Check status
systemctl --user status billing-service
EOF
```

---

## Option 2: Podman Compose Deployment (Best for Multi-Container)

### Step 1: Create podman-compose.yml

Create `podman-compose.yml` in project root:

```yaml
version: '3.8'

services:
  billing-service:
    build:
      context: .
      dockerfile: Dockerfile.billing-phase1
    container_name: billing-service
    volumes:
      - ./data:/app/data
      - ./backend-setup:/app/backend-setup
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app
    command: python3 -m pytest backend-setup/tests/test_billing_service_properties.py -v
    restart: unless-stopped

  # Optional: Add database container later
  # postgres:
  #   image: postgres:15-alpine
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   environment:
  #     - POSTGRES_PASSWORD=billing_db_pass

volumes:
  postgres_data:
```

### Step 2: Transfer and Run

```bash
# Transfer compose file
scp -i .kiro/private-keys/id_kiro podman-compose.yml cira@74.208.227.161:/home/cira/ai-phone-sas/

# On server: Run compose
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
cd /home/cira/ai-phone-sas
podman-compose up --build

# Or run in background
podman-compose up -d --build
podman-compose logs -f
EOF
```

---

## Option 3: Direct Container Execution (Simplest)

If you just want to test without building:

```bash
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 << 'EOF'
# Create working directory
mkdir -p /home/cira/ai-phone-sas/backend-setup/{services,db,tests}

# Copy files (already done via SCP)

# Run Python directly in container
podman run --rm \
  -v /home/cira/ai-phone-sas:/app \
  -w /app \
  python:3.12-slim \
  bash -c "
    pip install -r backend-setup/requirements.txt && \
    python3 -m pytest backend-setup/tests/test_billing_service_properties.py -v
  "
EOF
```

---

## Recommended Approach: Hybrid

**Best practice for your setup:**

1. **Build image locally** with Dockerfile
2. **Transfer as tar** (no registry needed)
3. **Load on server** with podman load
4. **Run with podman-compose** for persistence
5. **Use systemd user service** for auto-restart

---

## Quick Deployment Script (Podman-Aware)

```bash
#!/bin/bash

SERVER_HOST="74.208.227.161"
SERVER_USER="cira"
SSH_KEY=".kiro/private-keys/id_kiro"
PROJECT_DIR="/home/cira/ai-phone-sas"

echo "🐳 Building Podman image..."
podman build -f Dockerfile.billing-phase1 -t billing-service:phase1 .

echo "📦 Saving image as tar..."
podman save billing-service:phase1 -o billing-service-phase1.tar

echo "📤 Transferring image to server..."
scp -i $SSH_KEY billing-service-phase1.tar $SERVER_USER@$SERVER_HOST:/home/$SERVER_USER/

echo "🚀 Loading image on server and running tests..."
ssh -i $SSH_KEY $SERVER_USER@$SERVER_HOST << 'EOF'
cd /home/cira
podman load -i billing-service-phase1.tar
mkdir -p ai-phone-sas/data

echo "✅ Running tests in container..."
podman run --rm \
  -v /home/cira/ai-phone-sas/data:/app/data \
  billing-service:phase1

echo "✅ Deployment complete!"
EOF

# Cleanup
rm billing-service-phase1.tar
```

---

## Verification Commands

```bash
# Check if Podman is installed on server
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman --version"

# List running containers
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman ps -a"

# Check image
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman images"

# View container logs
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman logs billing-service"

# Stop container
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman stop billing-service"

# Remove image
ssh -i .kiro/private-keys/id_kiro cira@74.208.227.161 "podman rmi billing-service:phase1"
```

---

## Advantages of Podman Deployment

✅ **Isolation:** Services run in isolated containers
✅ **Reproducibility:** Same image runs everywhere
✅ **Rootless:** No privilege escalation needed
✅ **Persistence:** Volumes survive container restarts
✅ **Scalability:** Easy to run multiple instances
✅ **Security:** Containers are sandboxed

---

## Next Steps

1. **Choose deployment option** (Dockerfile recommended)
2. **Create Dockerfile.billing-phase1** in project root
3. **Build image locally** with podman build
4. **Transfer and deploy** to server
5. **Verify tests pass** in container
6. **Set up systemd service** for persistence

---

**Status:** Ready for Podman deployment
**Action:** Create Dockerfile and build image
**Next:** Transfer image to server and run tests in container
