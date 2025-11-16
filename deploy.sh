#!/bin/bash

# Gaming Platform - Production Deployment Script
# This script deploys the gaming platform to production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_warn "Running as root is not recommended. Consider using a regular user with sudo."
fi

# Banner
echo "============================================="
echo "  Gaming Platform - Production Deployment"
echo "============================================="
echo ""

# Step 1: Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

log_info "Prerequisites check passed!"

# Step 2: Check environment file
if [ ! -f .env ]; then
    log_error ".env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

if [ ! -f backend/.env.production ]; then
    log_error "backend/.env.production not found. Please copy backend/.env.production.example and configure it."
    exit 1
fi

log_info "Environment files found!"

# Step 3: Backup database (if exists)
log_info "Creating database backup..."
if docker ps | grep -q gaming_postgres_prod; then
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

    docker exec gaming_postgres_prod pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE 2>/dev/null || true

    if [ -f "$BACKUP_FILE" ]; then
        log_info "Database backup created: $BACKUP_FILE"
    fi
else
    log_warn "Database container not running, skipping backup."
fi

# Step 4: Pull latest code
log_info "Pulling latest code from repository..."
git pull origin main || log_warn "Git pull failed or not in a git repository"

# Step 5: Build Docker images
log_info "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Step 6: Stop existing containers
log_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Step 7: Start services
log_info "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Step 8: Wait for database
log_info "Waiting for database to be ready..."
sleep 10

# Step 9: Run database migrations
log_info "Running database migrations..."
docker exec gaming_backend_prod alembic upgrade head

# Step 10: Health check
log_info "Performing health checks..."
sleep 15

# Check backend
if curl -f http://localhost:8000/health &> /dev/null; then
    log_info "Backend is healthy!"
else
    log_error "Backend health check failed!"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost &> /dev/null; then
    log_info "Frontend is accessible!"
else
    log_warn "Frontend may not be ready yet. Check logs with: docker-compose -f docker-compose.prod.yml logs frontend"
fi

# Step 11: Display status
echo ""
echo "============================================="
log_info "Deployment completed successfully!"
echo "============================================="
echo ""
echo "Services status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  - Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "  - View metrics: http://localhost:9090 (Prometheus)"
echo "  - View dashboards: http://localhost:3000 (Grafana)"
echo ""
log_info "Deployment completed! Your platform should be accessible at http://localhost"
echo "============================================="
