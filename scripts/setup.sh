#!/bin/bash

# Gaming Platform - Initial Setup Script
# This script sets up the environment for first-time deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================="
echo "Gaming Platform - Initial Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is not recommended for production."
fi

# Check prerequisites
print_info "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || {
    print_error "Docker is not installed. Please install Docker first."
    exit 1
}
print_success "Docker is installed"

command -v docker-compose >/dev/null 2>&1 || {
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}
print_success "Docker Compose is installed"

# Navigate to project root
cd "$PROJECT_ROOT"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p logs
mkdir -p backups
mkdir -p uploads
mkdir -p data/postgres
mkdir -p data/redis
print_success "Directories created"

# Environment setup
print_info "Setting up environment files..."

if [ ! -f backend/.env ]; then
    if [ -f backend/.env.example ]; then
        cp backend/.env.example backend/.env
        print_success "Created backend/.env from .env.example"
        print_warning "Please edit backend/.env with your actual configuration"
    else
        print_error "backend/.env.example not found"
    fi
else
    print_info "backend/.env already exists"
fi

# Generate secrets if needed
print_info "Checking for secrets..."

if ! grep -q "JWT_SECRET=changeme" backend/.env 2>/dev/null; then
    print_info "JWT_SECRET appears to be configured"
else
    print_warning "JWT_SECRET needs to be changed in backend/.env"
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "PLEASE_CHANGE_THIS_$(date +%s)")
    print_info "Generated JWT_SECRET: $JWT_SECRET"
    echo "Please update JWT_SECRET in backend/.env with the above value"
fi

# Database setup
print_info "Setting up database..."

# Check if database is already running
if docker ps | grep -q gaming_platform_postgres; then
    print_info "Database container is already running"
else
    print_info "Starting database container..."
    docker-compose up -d postgres
    print_success "Database container started"

    print_info "Waiting for database to be ready..."
    sleep 10
fi

# Run migrations
print_info "Running database migrations..."
if [ -d "backend/alembic" ]; then
    docker-compose exec -T backend alembic upgrade head 2>/dev/null || {
        print_warning "Could not run migrations automatically. Please run manually:"
        echo "  docker-compose exec backend alembic upgrade head"
    }
else
    print_warning "Alembic directory not found. Migrations may need to be set up."
fi

# Redis setup
print_info "Starting Redis..."
docker-compose up -d redis
print_success "Redis container started"

# Set up file permissions
print_info "Setting up file permissions..."
chmod +x scripts/*.sh
print_success "Scripts made executable"

# Pull required Docker images
print_info "Pulling Docker images..."
docker-compose pull
print_success "Docker images pulled"

# Build backend image
print_info "Building backend image..."
docker-compose build backend
print_success "Backend image built"

# Network setup
print_info "Checking Docker networks..."
if ! docker network ls | grep -q gaming_platform_network; then
    docker network create gaming_platform_network 2>/dev/null || true
    print_success "Docker network created"
else
    print_info "Docker network already exists"
fi

# Health check
print_info "Performing initial health check..."
sleep 5

if docker ps | grep -q gaming_platform_postgres; then
    print_success "PostgreSQL is running"
else
    print_warning "PostgreSQL is not running"
fi

if docker ps | grep -q gaming_platform_redis; then
    print_success "Redis is running"
else
    print_warning "Redis is not running"
fi

# Summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
print_info "Next steps:"
echo "  1. Edit backend/.env with your configuration"
echo "  2. Run: docker-compose up -d"
echo "  3. Check health: ./scripts/health-check.sh"
echo "  4. View logs: docker-compose logs -f"
echo ""
print_info "Useful commands:"
echo "  - Start all services: docker-compose up -d"
echo "  - Stop all services: docker-compose down"
echo "  - View logs: docker-compose logs -f"
echo "  - Run migrations: docker-compose exec backend alembic upgrade head"
echo ""
print_success "Setup completed successfully!"
