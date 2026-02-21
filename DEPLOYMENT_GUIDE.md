# Tero Voice - Production Deployment Guide

**Status:** Ready for VPS deployment
**Target:** dev.terovoice.com (staging) → terovoice.com (production)
**CI/CD:** GitHub → VPS with rollback capability
**Architecture:** Docker Compose with separate backend/frontend services

---

## Quick Start

### Prerequisites
- Docker and Docker Compose installed on VPS
- Git repository access
- Admin agents configured for VPS management

### Deploy to VPS

```bash
# SSH to VPS
ssh root@your-vps-ip

# Clone repository
git clone https://github.com/terovoice/terovoice.git
cd terovoice

# Set environment variables
cp .env.example .env
nano .env  # Edit with your settings

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

---

## Architecture

### Services

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (Port 3000)          Backend API (Port 8000)       │
│  ├─ React + Vite               ├─ Flask                      │
│  ├─ Nginx server               ├─ JWT Auth                   │
│  └─ SPA routing                ├─ Multi-tenant               │
│                                └─ RESTful API                │
│                                                               │
│  Ollama LLM (Port 11434)       Redis Cache (Port 6379)       │
│  ├─ Local inference            ├─ Session storage            │
│  ├─ Llama3 model               ├─ Rate limiting              │
│  └─ GPU support                └─ Data caching               │
│                                                               │
│  PostgreSQL (Port 5432)                                      │
│  ├─ Multi-tenant database                                    │
│  ├─ pgvector support                                         │
│  └─ Persistent storage                                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Service Communication

- **Frontend** → **Backend**: HTTP/REST via `/api/` proxy
- **Backend** → **PostgreSQL**: Direct connection
- **Backend** → **Ollama**: HTTP requests for LLM inference
- **Backend** → **Redis**: Cache operations
- **All services**: Connected via `terovoice-network` bridge

---

## Environment Configuration

### .env File

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/ai_receptionist

# Security
JWT_SECRET=your-super-secret-key-change-this-in-production

# Flask
FLASK_ENV=production
FLASK_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,https://app.dev.terovoice.com,https://app.terovoice.com

# Ollama
OLLAMA_HOST=http://ollama:11434

# Redis
REDIS_URL=redis://redis:6379/0

# Debug (set to False in production)
DEBUG=False
```

---

## Deployment Workflow

### 1. Local Development

```bash
# Install dependencies
npm install
pip install -r backend-setup/requirements.txt

# Run locally
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Ollama: http://localhost:11434
```

### 2. Staging Deployment (dev.terovoice.com)

```bash
# Push to GitHub
git add .
git commit -m "Feature: Add new functionality"
git push origin main

# SSH to staging VPS
ssh root@staging-vps-ip

# Pull latest code
cd /var/www/terovoice
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs -f
```

### 3. Production Deployment (terovoice.com)

```bash
# After testing on staging, tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# SSH to production VPS
ssh root@production-vps-ip

# Create backup
docker-compose exec postgres pg_dump -U user ai_receptionist > backup-$(date +%Y%m%d-%H%M%S).sql

# Pull latest code
cd /var/www/terovoice
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs -f
```

---

## Rollback Procedure

### Quick Rollback (Last Commit)

```bash
# SSH to VPS
ssh root@your-vps-ip
cd /var/www/terovoice

# Revert to previous commit
git revert HEAD
git push origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose ps
```

### Full Rollback (Specific Version)

```bash
# SSH to VPS
ssh root@your-vps-ip
cd /var/www/terovoice

# Checkout specific tag
git checkout v1.0.0

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose ps
```

### Database Rollback

```bash
# SSH to VPS
ssh root@your-vps-ip

# Restore from backup
docker-compose exec postgres psql -U user ai_receptionist < backup-20240101-120000.sql

# Verify
docker-compose exec postgres psql -U user -d ai_receptionist -c "SELECT COUNT(*) FROM users;"
```

---

## Monitoring & Maintenance

### Check Service Status

```bash
# View all services
docker-compose ps

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# View resource usage
docker stats

# Check health
curl http://localhost:8000/api/health
curl http://localhost:3000/
curl http://localhost:11434/api/tags
```

### Common Commands

```bash
# Restart a service
docker-compose restart backend

# Rebuild a service
docker-compose build --no-cache backend
docker-compose up -d backend

# View logs with timestamps
docker-compose logs --timestamps -f backend

# Execute command in container
docker-compose exec backend python -c "import sys; print(sys.version)"

# Remove all containers and volumes
docker-compose down -v

# Prune unused images and volumes
docker system prune -a --volumes
```

---

## Troubleshooting

### Backend not starting

```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend curl http://postgres:5432

# Check environment variables
docker-compose exec backend env | grep DATABASE
```

### Frontend not loading

```bash
# Check logs
docker-compose logs frontend

# Verify Nginx configuration
docker-compose exec frontend nginx -t

# Check API connectivity
docker-compose exec frontend curl http://backend:8000/api/health
```

### Ollama not responding

```bash
# Check logs
docker-compose logs ollama

# Verify service is running
docker-compose exec ollama curl http://localhost:11434/api/tags

# Check available models
docker-compose exec ollama ollama list
```

### Database connection issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U user -l

# Check database size
docker-compose exec postgres psql -U user -d ai_receptionist -c "SELECT pg_size_pretty(pg_database_size('ai_receptionist'));"
```

---

## Performance Optimization

### Resource Limits

Edit `docker-compose.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### Caching Strategy

- **Frontend**: Static assets cached for 1 year
- **Backend**: Redis cache for API responses
- **Database**: Connection pooling enabled

### Database Optimization

```bash
# Analyze query performance
docker-compose exec postgres psql -U user -d ai_receptionist -c "ANALYZE;"

# Check index usage
docker-compose exec postgres psql -U user -d ai_receptionist -c "SELECT * FROM pg_stat_user_indexes;"

# Vacuum database
docker-compose exec postgres psql -U user -d ai_receptionist -c "VACUUM ANALYZE;"
```

---

## Security Considerations

### Environment Variables

- Never commit `.env` file to Git
- Use strong JWT_SECRET (minimum 32 characters)
- Rotate secrets regularly
- Use different secrets for staging and production

### Network Security

- Services communicate via internal Docker network
- Only expose ports 3000 (frontend) and 8000 (backend)
- Use reverse proxy (Nginx) for SSL termination
- Enable firewall rules on VPS

### Database Security

- Use strong PostgreSQL password
- Enable SSL connections
- Regular backups
- Restrict database access to backend service only

### API Security

- JWT token validation on all endpoints
- Rate limiting enabled
- CORS properly configured
- Input validation on all endpoints

---

## Backup & Recovery

### Automated Backups

```bash
# Create backup script
cat > /usr/local/bin/backup-terovoice.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/terovoice"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec postgres pg_dump -U user ai_receptionist > $BACKUP_DIR/db-$TIMESTAMP.sql

# Backup volumes
tar -czf $BACKUP_DIR/volumes-$TIMESTAMP.tar.gz /var/lib/docker/volumes/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x /usr/local/bin/backup-terovoice.sh

# Schedule daily backups (crontab)
0 2 * * * /usr/local/bin/backup-terovoice.sh
```

### Restore from Backup

```bash
# Restore database
docker-compose exec postgres psql -U user ai_receptionist < /backups/terovoice/db-20240101-020000.sql

# Restore volumes
tar -xzf /backups/terovoice/volumes-20240101-020000.tar.gz -C /
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker images
        run: docker-compose build

      - name: Run tests
        run: docker-compose run backend pytest

      - name: Push to registry
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose push

      - name: Deploy to VPS
        run: |
          ssh -i ${{ secrets.VPS_SSH_KEY }} root@${{ secrets.VPS_IP }} << 'EOF'
          cd /var/www/terovoice
          git pull origin main
          docker-compose down
          docker-compose up -d
          EOF
```

---

## Support & Documentation

### Key Files

- `docker-compose.yml` - Service configuration
- `Dockerfile.backend` - Backend container
- `Dockerfile.frontend` - Frontend container
- `nginx.conf` - Frontend Nginx configuration
- `backend-setup/requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies

### Useful Links

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Ollama: http://localhost:11434
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Admin Contacts

- VPS Admin: [Your admin contact]
- DevOps: [Your DevOps contact]
- Support: support@terovoice.com

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database backups created
- [ ] SSL certificates valid
- [ ] Firewall rules configured
- [ ] Admin agents ready
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] All services running
- [ ] Tests passing
- [ ] Documentation updated

---

**Status:** ✅ Ready for VPS Deployment
**Last Updated:** January 4, 2026
**Version:** 1.0.0

🚀 **Deploy with confidence!**
