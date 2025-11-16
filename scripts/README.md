# Deployment Scripts

Utility scripts for deploying and managing the Gaming Platform.

## Scripts Overview

### `deploy.sh`
Main deployment script with zero-downtime deployment.

**Usage:**
```bash
./deploy.sh [staging|production]
```

**Features:**
- Creates backup (production only)
- Pulls latest Docker images
- Runs database migrations
- Rolling update for zero downtime
- Health checks
- Automatic cleanup

**Example:**
```bash
# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh production
```

---

### `backup.sh`
Database backup script with automatic rotation.

**Usage:**
```bash
./backup.sh
```

**Features:**
- Creates compressed database backup
- Timestamps all backups
- Automatic cleanup (30 days retention)
- Displays backup size and count

**Output:**
Backups are stored in `./backups/backup_YYYYMMDD_HHMMSS.sql.gz`

---

### `restore.sh`
Database restoration script with safety features.

**Usage:**
```bash
# Interactive mode (lists available backups)
./restore.sh

# Restore specific backup
./restore.sh ./backups/backup_20250116_020000.sql.gz
```

**Features:**
- Interactive backup selection
- Safety backup before restore
- Service management (stops/starts services)
- Post-restore health check

**Warning:** This will replace the current database!

---

### `health-check.sh`
Comprehensive system health check.

**Usage:**
```bash
./health-check.sh
```

**Checks:**
- Docker services status
- API endpoints availability
- Database connectivity
- Redis connectivity
- Disk space usage
- Memory usage

**Exit Codes:**
- 0: All checks passed
- 1: One or more checks failed

---

### `setup.sh`
Initial server setup and configuration.

**Usage:**
```bash
sudo ./setup.sh
```

**Features:**
- System package updates
- Docker and Docker Compose installation
- Additional tools installation
- Firewall configuration (UFW)
- Application user creation
- Log rotation setup
- Automatic backup scheduling
- System optimization

**Note:** Must be run as root (use sudo)

---

### `rollback.sh`
Emergency rollback script.

**Usage:**
```bash
# Rollback to latest backup
./rollback.sh

# Rollback to specific backup
./rollback.sh ./backups/backup_20250116_020000.sql.gz
```

**Features:**
- Stops current services
- Restores database from backup
- Restarts services
- Runs health checks

---

## Environment Variables

All scripts use environment variables from `.env` file:

```bash
POSTGRES_DB=gaming_platform_prod
POSTGRES_USER=gaming_user
POSTGRES_PASSWORD=<password>
```

## Error Handling

All scripts use `set -e` to exit on errors and provide colored output:
- 🟢 Green: Success messages
- 🟡 Yellow: Warnings and progress
- 🔴 Red: Errors

## Logging

Script outputs can be logged:

```bash
# Log deployment
./deploy.sh production 2>&1 | tee logs/deploy_$(date +%Y%m%d_%H%M%S).log

# Log health checks
./health-check.sh >> logs/health.log 2>&1
```

## Automation

### Cron Jobs

Automatic backups are configured during setup:

```cron
# Daily database backup at 2 AM
0 2 * * * gaming cd ~/gaming-platform && ./scripts/backup.sh >> logs/backup.log 2>&1

# Health check every 5 minutes
*/5 * * * * gaming cd ~/gaming-platform && ./health-check.sh >> logs/health.log 2>&1
```

View cron jobs:
```bash
crontab -l
```

## Best Practices

1. **Always test in staging first**
   ```bash
   ./deploy.sh staging
   ./health-check.sh
   ```

2. **Create backups before major changes**
   ```bash
   ./backup.sh
   ```

3. **Monitor health regularly**
   ```bash
   watch -n 60 ./health-check.sh
   ```

4. **Keep scripts executable**
   ```bash
   chmod +x scripts/*.sh
   ```

5. **Review logs after deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Troubleshooting

### Permission Denied
```bash
chmod +x scripts/*.sh
```

### Environment Variables Not Found
```bash
# Ensure .env file exists
ls -la .env

# Load environment manually
export $(cat .env | grep -v '^#' | xargs)
```

### Docker Command Not Found
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Re-login or use
newgrp docker
```

## Quick Reference

| Task | Command |
|------|---------|
| Deploy to production | `./deploy.sh production` |
| Create backup | `./backup.sh` |
| Restore database | `./restore.sh` |
| Check health | `./health-check.sh` |
| Initial setup | `sudo ./setup.sh` |
| Rollback | `./rollback.sh` |

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review DEPLOYMENT.md
- Check health: `./health-check.sh`

---

**Last Updated:** November 16, 2025
**Phase:** 6 - Deployment & DevOps
