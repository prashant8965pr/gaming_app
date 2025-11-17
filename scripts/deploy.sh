#!/bin/bash

# Gaming Platform Deployment Script
# Usage: ./scripts/deploy.sh [environment]
# Environment: development | staging | production

set -e

ENVIRONMENT=${1:-development}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "================================================"
echo "Gaming Platform Deployment Script"
echo "================================================"
echo "Environment: $ENVIRONMENT"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "All prerequisites met ✓"
}

# Load environment variables
load_env() {
    log_info "Loading environment variables..."
    
    ENV_FILE="$PROJECT_ROOT/.env.$ENVIRONMENT"
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "Environment file not found: $ENV_FILE"
        log_warn "Copying from example..."
        cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
        log_error "Please configure $ENV_FILE before deploying"
        exit 1
    fi
    
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    log_info "Environment loaded from $ENV_FILE ✓"
}

# Stop existing containers
stop_containers() {
    log_info "Stopping existing containers..."
    
    if [ "$ENVIRONMENT" == "production" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" down || true
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down || true
    fi
    
    log_info "Containers stopped ✓"
}

# Build images
build_images() {
    log_info "Building Docker images..."
    
    if [ "$ENVIRONMENT" == "production" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" build --no-cache
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" build
    fi
    
    log_info "Images built ✓"
}

# Start containers
start_containers() {
    log_info "Starting containers..."
    
    if [ "$ENVIRONMENT" == "production" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" up -d
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d
    fi
    
    log_info "Containers started ✓"
}

# Wait for services
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    sleep 5
    
    # Wait for database
    log_info "Waiting for database..."
    for i in {1..30}; do
        if docker exec gaming_platform_postgres_prod pg_isready -U postgres > /dev/null 2>&1 || \
           docker exec gaming_platform_postgres pg_isready -U postgres > /dev/null 2>&1; then
            log_info "Database is ready ✓"
            break
        fi
        sleep 2
    done
    
    # Wait for backend
    log_info "Waiting for backend..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Backend is ready ✓"
            break
        fi
        sleep 2
    done
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    
    CONTAINER="gaming_platform_backend"
    if [ "$ENVIRONMENT" == "production" ]; then
        CONTAINER="gaming_platform_backend_prod"
    fi
    
    docker exec $CONTAINER alembic upgrade head
    
    log_info "Migrations completed ✓"
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # Check backend
    BACKEND_HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "")
    if [ -n "$BACKEND_HEALTH" ]; then
        log_info "Backend health check passed ✓"
    else
        log_error "Backend health check failed ✗"
        exit 1
    fi
    
    # Check database
    if docker exec gaming_platform_postgres pg_isready -U postgres > /dev/null 2>&1; then
        log_info "Database health check passed ✓"
    else
        log_error "Database health check failed ✗"
        exit 1
    fi
}

# Show status
show_status() {
    echo ""
    log_info "Deployment Status"
    echo "================================================"
    
    if [ "$ENVIRONMENT" == "production" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.prod.yml" ps
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps
    fi
    
    echo ""
    log_info "Services:"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Database: localhost:5432"
    echo "  Redis: localhost:6379"
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    load_env
    stop_containers
    build_images
    start_containers
    wait_for_services
    run_migrations
    health_check
    show_status
    
    echo ""
    log_info "================================================"
    log_info "Deployment completed successfully! 🎉"
    log_info "================================================"
}

# Run main function
main
