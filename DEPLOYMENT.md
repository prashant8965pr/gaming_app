# Gaming Platform - Deployment Guide

Complete guide for deploying the Gaming Platform to production and staging environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Methods](#deployment-methods)
- [Database Management](#database-management)
- [Monitoring & Logging](#monitoring--logging)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements

**Minimum Requirements (Staging):**
- 2 CPU cores
- 4 GB RAM
- 40 GB SSD storage
- Ubuntu 20.04 LTS or later

**Recommended Requirements (Production):**
- 4 CPU cores
- 8 GB RAM
- 100 GB SSD storage
- Ubuntu 20.04 LTS or later

### Required Software

- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for SSL certificates)

---

## Server Setup

### Automated Setup

Run the automated setup script on a fresh Ubuntu server:

```bash
# Clone repository
git clone <repository-url> /opt/gaming-platform
cd /opt/gaming-platform

# Run setup script as root
sudo ./scripts/setup.sh
```

This script will:
- Update system packages
- Install Docker and Docker Compose
- Install required tools (curl, wget, git, etc.)
- Configure firewall (UFW)
- Create application user
- Setup log rotation
- Configure automatic backups
- Optimize system settings

### Manual Setup

If you prefer manual setup:

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Create application user
sudo useradd -m -s /bin/bash gaming
sudo usermod -aG docker gaming

# 5. Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## Environment Configuration

### 1. Create Environment File

```bash
# Copy example file
cp .env.example .env

# Edit with your values
vim .env
```

### 2. Configure Backend Environment

```bash
# For production
cp backend/.env.production.example backend/.env.production
vim backend/.env.production

# For staging
cp backend/.env.staging.example backend/.env.staging
vim backend/.env.staging
```

### 3. Required Environment Variables

**Critical Variables (Must Change):**

```bash
# Database
POSTGRES_PASSWORD=<strong-password>
POSTGRES_USER=gaming_user
POSTGRES_DB=gaming_platform_prod

# Redis
REDIS_PASSWORD=<strong-redis-password>

# JWT Security
SECRET_KEY=<random-32-char-string>

# Admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_INITIAL_PASSWORD=<strong-admin-password>

# Grafana
GRAFANA_PASSWORD=<strong-grafana-password>
```

**Payment Gateway:**

```bash
# Razorpay
RAZORPAY_KEY_ID=<your-key>
RAZORPAY_KEY_SECRET=<your-secret>
RAZORPAY_WEBHOOK_SECRET=<webhook-secret>
```

**SMS Provider:**

```bash
# Twilio
TWILIO_ACCOUNT_SID=<account-sid>
TWILIO_AUTH_TOKEN=<auth-token>
TWILIO_PHONE_NUMBER=<phone-number>
```

**Email Configuration:**

```bash
# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<app-password>
```

### 4. Generate Secrets

```bash
# Generate random SECRET_KEY
openssl rand -hex 32

# Generate passwords
openssl rand -base64 32
```

---

## Deployment Methods

### Method 1: Using Deployment Script (Recommended)

```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production (with confirmation)
./scripts/deploy.sh production
```

The script will:
1. Create backup (production only)
2. Pull latest Docker images
3. Run database migrations
4. Deploy services with zero downtime
5. Run health checks
6. Clean up old images

### Method 2: Manual Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Pull Docker images
docker-compose -f docker-compose.prod.yml pull

# 3. Run migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 4. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 5. Check health
./scripts/health-check.sh
```

### Method 3: CI/CD Pipeline

Push to respective branches:
- `develop` → Auto-deploy to staging
- Tag `v*.*.*` → Deploy to production (with approval)

```bash
# Create and push tag for production
git tag v1.0.0
git push origin v1.0.0
```

---

## Database Management

### Initial Setup

```bash
# Run all migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Create admin user
docker-compose -f docker-compose.prod.yml run --rm backend python -c "
from core.database import get_db
from models.user import User
from services.auth_service import hash_password
import asyncio

async def create_admin():
    async for db in get_db():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=hash_password('ChangeMe123!'),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print('Admin user created')

asyncio.run(create_admin())
"
```

### Backup

```bash
# Manual backup
./scripts/backup.sh

# Backups are stored in: ./backups/
# Retention: 30 days (configurable)
```

Automatic backups run daily at 2 AM (configured in setup script).

### Restore

```bash
# Interactive restore (lists available backups)
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh ./backups/backup_20250116_020000.sql.gz
```

### Migrations

```bash
# View migration history
docker-compose -f docker-compose.prod.yml run --rm backend alembic history

# View current version
docker-compose -f docker-compose.prod.yml run --rm backend alembic current

# Upgrade to latest
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Downgrade one version
docker-compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1
```

---

## Monitoring & Logging

### Accessing Monitoring Tools

**Prometheus:**
- URL: `http://your-server:9090`
- Metrics scraping interval: 15s
- Retention: 30 days

**Grafana:**
- URL: `http://your-server:3000`
- Default credentials: admin / (from GRAFANA_PASSWORD)
- Pre-configured Prometheus datasource

### Setting Up Dashboards

1. Login to Grafana
2. Import dashboard JSON from `monitoring/grafana/dashboards/`
3. Configure alerts and notifications

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Application logs (inside container)
docker-compose -f docker-compose.prod.yml exec backend tail -f logs/application.log

# Error logs
docker-compose -f docker-compose.prod.yml exec backend tail -f logs/errors.log
```

### Log Files Location

- **Container logs:** Managed by Docker
- **Application logs:** `backend/logs/application.log`
- **Error logs:** `backend/logs/errors.log`
- **Access logs:** `backend/logs/access.log`
- **Nginx logs:** `nginx/logs/`

---

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Copy to nginx/ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Update nginx config with your domain
vim nginx/nginx.prod.conf
# Change: server_name yourdomain.com www.yourdomain.com;

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Auto-renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /opt/gaming-platform/docker-compose.prod.yml restart nginx" | sudo crontab -
```

### Using Self-Signed Certificate (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=IN/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

---

## Backup & Recovery

### Backup Strategy

**Automated Backups:**
- Database: Daily at 2 AM
- Retention: 30 days
- Location: `./backups/`

**What to Backup:**
- Database (automated)
- Environment files (`.env`, `.env.production`)
- Uploaded files (`backend/uploads/`)
- SSL certificates (`nginx/ssl/`)

### Manual Backup

```bash
# Full backup
./scripts/backup.sh

# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/

# Backup environment
cp .env .env.backup
cp backend/.env.production backend/.env.production.backup
```

### Disaster Recovery

```bash
# 1. Restore from backup
./scripts/restore.sh

# 2. Restore uploaded files
tar -xzf uploads_backup_20250116.tar.gz -C backend/

# 3. Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Rollback Deployment

```bash
# Automatic rollback (restores latest backup)
./scripts/rollback.sh

# Rollback to specific backup
./scripts/rollback.sh ./backups/backup_20250116_020000.sql.gz
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs <service-name>

# Restart specific service
docker-compose -f docker-compose.prod.yml restart <service-name>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build <service-name>
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U $POSTGRES_USER

# Check connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;"

# View PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres
```

### High CPU/Memory Usage

```bash
# Check resource usage
docker stats

# Scale backend services
docker-compose -f docker-compose.prod.yml up -d --scale backend=4

# Check system resources
htop

# Clean up Docker resources
docker system prune -af
```

### 502 Bad Gateway

Common causes:
1. Backend service is down
2. Backend is starting up (wait 30s)
3. Port conflict

```bash
# Check backend health
curl http://localhost:8000/health

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend

# Check nginx config
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor health checks
- Review error logs
- Check disk space

**Weekly:**
- Review performance metrics
- Update dependencies (if needed)
- Test backup restoration

**Monthly:**
- Security updates
- Database optimization
- Clean up old logs and backups

### Updates and Upgrades

```bash
# 1. Create backup
./scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Update images
docker-compose -f docker-compose.prod.yml pull

# 4. Run migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 5. Restart services
docker-compose -f docker-compose.prod.yml up -d

# 6. Verify health
./scripts/health-check.sh
```

### Database Optimization

```bash
# Vacuum analyze (reclaim space and update stats)
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "VACUUM ANALYZE;"

# Reindex
docker-compose -f docker-compose.prod.yml exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "REINDEX DATABASE $POSTGRES_DB;"
```

### Scaling Services

```bash
# Scale backend workers
docker-compose -f docker-compose.prod.yml up -d --scale backend=4

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

---

## Security Best Practices

1. **Change all default passwords** in `.env` files
2. **Use strong SECRET_KEY** (minimum 32 characters)
3. **Enable HTTPS** with valid SSL certificate
4. **Restrict database access** to application only
5. **Regular security updates** for system and dependencies
6. **Monitor logs** for suspicious activity
7. **Use firewall** (UFW) to restrict access
8. **Backup encryption** for sensitive data
9. **API rate limiting** already configured in Nginx
10. **Regular penetration testing**

---

## Performance Optimization

### Database

- Connection pooling: Configured in SQLAlchemy
- Indexes: Defined in models
- Query optimization: Use EXPLAIN ANALYZE

### Caching

- Redis for session and cache
- Nginx static file caching
- API response caching (implement as needed)

### Load Balancing

- Nginx upstream with least_conn
- Multiple backend replicas in production
- Health checks for automatic failover

---

## Support and Resources

- **Documentation:** `/docs` endpoint on deployed API
- **Health Check:** `/health` endpoint
- **API Docs:** `https://yourdomain.com/docs`
- **Repository Issues:** GitHub Issues page

---

## Quick Reference

### Common Commands

```bash
# Deploy
./scripts/deploy.sh production

# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh

# Health Check
./scripts/health-check.sh

# View Logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Restart
docker-compose -f docker-compose.prod.yml restart

# Stop All
docker-compose -f docker-compose.prod.yml down

# Start All
docker-compose -f docker-compose.prod.yml up -d
```

---

**Last Updated:** November 16, 2025
**Version:** 1.0.0
**Phase:** 6 - Deployment & DevOps
