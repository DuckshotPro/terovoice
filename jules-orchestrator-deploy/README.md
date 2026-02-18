# Deployment Guide for Jules Orchestrator (Podman)

This guide helps you deploy the **Antigravity-Jules Orchestration** server on your VM using **Podman**.

## Prerequisites
- Podman and `podman-compose` installed on your VM.
- A valid **Jules API Key**.

## 1. Get the Code
On your remote VM, create a directory and clone the official repository:
```bash
git clone https://github.com/Scarmonit/antigravity-jules-orchestration.git jules-orchestrator
cd jules-orchestrator
```

## 2. Add Deployment Files
Copy the `Dockerfile` and `docker-compose.yml` from this folder into that `jules-orchestrator` directory on your VM.

## 3. Configure API Key
Create a `.env` file in the same directory:
```bash
echo "JULES_API_KEY=your_actual_api_key_here" > .env
```

## 4. Launch with Podman
Run the service:
```bash
podman-compose up -d --build
```

## 5. Verify
Check if it represents itself on port 3000:
```bash
curl http://localhost:3000/health
# Or just open http://your-vm-ip:3000 in your browser
```

## 6. Connect n8n
In your n8n workflows, you can now direct HTTP Requests to:
- URL: `http://localhost:3000/api/...` (if n8n is on the same host)
- Or use `http://jules-orchestrator:3000` if they are in the same Podman network.
