# Gaming Platform - Deployment Guide

Complete guide to deploying the Gaming Platform to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Deployment Options](#deployment-options)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [SSL/HTTPS Setup](#sslhttps-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Security Checklist](#security-checklist)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **RAM**: Minimum 4GB (8GB+ recommended for production)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Domain name (for production)
- SSL certificate (for HTTPS)

### Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/gaming_app.git
cd gaming_app
```

### 2. Configure Environment

```bash
# Copy environment files
cp .env.example .env
cp backend/.env.production.example backend/.env.production

# Edit configuration
nano .env
nano backend/.env.production
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. Verify

```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Check backend health
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Small-Medium Scale)

**Pros:**
- Easy to set up and manage
- All services in one place
- Perfect for single-server deployments
- Built-in monitoring with Prometheus & Grafana

**Cons:**
- Limited scalability
- Single point of failure

**Best for:** 1-10k users, single server deployment

### Option 2: Kubernetes (For Large Scale)

**Pros:**
- Auto-scaling
- High availability
- Load balancing
- Self-healing

**Cons:**
- Complex setup
- Higher resource requirements
- Steeper learning curve

**Best for:** 10k+ users, multi-server deployment

### Option 3: Cloud Managed Services

**Pros:**
- Fully managed
- Auto-scaling
- High availability
- Minimal ops work

**Cons:**
- Higher cost
- Vendor lock-in

**Best for:** Rapid deployment, minimal DevOps

---

## Environment Configuration

### Root .env File

```bash
# PostgreSQL
POSTGRES_DB=gaming_platform_prod
POSTGRES_USER=gaming_user
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=<strong-password>

# API URL (for frontend)
API_URL=https://api.yourdomain.com/api/v1
```

### Backend .env.production

See `backend/.env.production.example` for full configuration options.

**Critical settings:**

```bash
SECRET_KEY=<32+ character random string>
JWT_SECRET_KEY=<32+ character random string>
DATABASE_URL=postgresql+asyncpg://...
RAZORPAY_KEY_ID=<your-key>
RAZORPAY_KEY_SECRET=<your-secret>
SMTP_HOST=smtp.gmail.com
SMTP_USER=<your-email>
SMTP_PASSWORD=<app-password>
```

### Generating Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -base64 32
```

---

## Database Setup

### PostgreSQL

The database is automatically created by Docker Compose. For manual setup:

```bash
# Create database
createdb gaming_platform_prod

# Run migrations
docker exec gaming_backend_prod alembic upgrade head
```

### Initial Admin User

```bash
# Connect to database
docker exec -it gaming_postgres_prod psql -U gaming_user -d gaming_platform_prod

# Make user admin
UPDATE users SET role = 'admin' WHERE username = 'your_username';

# Verify
SELECT id, username, email, role FROM users WHERE role = 'admin';
```

---

## Docker Deployment

### Development

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# View status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Restart service
docker-compose -f docker-compose.prod.yml restart backend

# Stop all services
docker-compose -f docker-compose.prod.yml down
```

### Scaling Services

```bash
# Scale backend to 3 replicas
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale frontend to 2 replicas
docker-compose -f docker-compose.prod.yml up -d --scale frontend=2
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: EC2 + Docker Compose

**1. Launch EC2 Instance**

- Type: t3.medium or larger
- OS: Ubuntu 20.04 LTS
- Security Group: Allow ports 80, 443, 22

**2. Connect and Setup**

```bash
# SSH into instance
ssh ubuntu@your-instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone and deploy
git clone https://github.com/yourusername/gaming_app.git
cd gaming_app
./deploy.sh
```

**3. Setup Domain**

- Point domain A record to EC2 IP
- Configure nginx for domain
- Setup SSL with Let's Encrypt

#### Option 2: ECS (Elastic Container Service)

See `docs/AWS_ECS_DEPLOYMENT.md` for detailed guide.

### DigitalOcean Deployment

**1. Create Droplet**

- Size: 4GB RAM minimum
- OS: Ubuntu 20.04
- Add SSH key

**2. Deploy**

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/yourusername/gaming_app.git
cd gaming_app
chmod +x deploy.sh
./deploy.sh
```

### Vercel (Frontend Only)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Deploy admin panel
cd frontend-admin
vercel --prod
```

Update environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1`

---

## SSL/HTTPS Setup

### Option 1: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: Cloudflare (Free + CDN)

1. Add your domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS (Full or Full Strict)
4. Enable Auto HTTPS Rewrites
5. Update origin server to accept Cloudflare IPs

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring & Logging

### Prometheus

Access: `http://your-server:9090`

**Metrics tracked:**
- CPU usage
- Memory usage
- Request rate
- Error rate
- Database connections

### Grafana

Access: `http://your-server:3000`

Default credentials: admin / (from .env)

**Pre-configured dashboards:**
- System Overview
- API Performance
- Database Metrics
- User Activity

### Application Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Export logs
docker-compose -f docker-compose.prod.yml logs --no-color > logs.txt
```

### Error Tracking (Sentry)

1. Create account at sentry.io
2. Create new project
3. Add DSN to `backend/.env.production`:
   ```bash
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```
4. Restart backend

---

## Backup & Recovery

### Database Backup

```bash
# Create backup directory
mkdir -p backups

# Manual backup
docker exec gaming_postgres_prod pg_dump -U gaming_user gaming_platform_prod > backups/backup_$(date +%Y%m%d).sql

# Automated daily backup (crontab)
0 2 * * * /path/to/gaming_app/scripts/backup_db.sh
```

### Restore from Backup

```bash
# Stop backend
docker-compose -f docker-compose.prod.yml stop backend

# Restore database
cat backups/backup_20250116.sql | docker exec -i gaming_postgres_prod psql -U gaming_user -d gaming_platform_prod

# Start backend
docker-compose -f docker-compose.prod.yml start backend
```

### Full System Backup

```bash
# Backup everything
tar -czf gaming_platform_backup_$(date +%Y%m%d).tar.gz \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    .
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up CORS correctly
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity
- [ ] Use non-root user in containers
- [ ] Scan images for vulnerabilities
- [ ] Enable 2FA for admin accounts
- [ ] Regular penetration testing

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check individual service
docker-compose -f docker-compose.prod.yml logs backend

# Rebuild images
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Connection Issues

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker exec gaming_backend_prod python -c "from database import engine; print('OK')"
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart memory-heavy service
docker-compose -f docker-compose.prod.yml restart backend

# Adjust resource limits in docker-compose.prod.yml
```

### 502 Bad Gateway

- Check backend is running: `docker ps | grep backend`
- Check backend logs: `docker logs gaming_backend_prod`
- Verify nginx configuration
- Check CORS settings

---

## Performance Optimization

### Database

```sql
-- Add indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_status ON game_sessions(status);

-- Analyze and vacuum
ANALYZE;
VACUUM;
```

### Redis Caching

Enable caching in `backend/.env.production`:

```bash
REDIS_CACHE_ENABLED=True
REDIS_CACHE_TTL=3600
```

### CDN

Use Cloudflare or AWS CloudFront for static assets.

---

## Maintenance

### Update Platform

```bash
# Pull latest code
git pull origin main

# Rebuild and redeploy
./deploy.sh
```

### Database Migrations

```bash
# Create migration
docker exec gaming_backend_prod alembic revision --autogenerate -m "description"

# Apply migration
docker exec gaming_backend_prod alembic upgrade head

# Rollback
docker exec gaming_backend_prod alembic downgrade -1
```

---

## Support

For deployment issues:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review this guide
- Check GitHub issues
- Contact support

---

**Last Updated:** 2025-01-16
**Version:** 1.0.0
