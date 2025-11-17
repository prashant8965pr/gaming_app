#!/bin/bash

# Gaming Platform - Health Check Script
# This script checks the health of all services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================="
echo "Gaming Platform - Health Check"
echo "=================================="
echo ""

cd "$PROJECT_ROOT"

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local service=$2
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|201\|204"; then
        echo -e "${GREEN}✓${NC} $service is healthy"
        return 0
    else
        echo -e "${RED}✗${NC} $service is unhealthy"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container=$1
    local service=$2
    
    if docker ps | grep -q "$container"; then
        local status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✓${NC} $service container is running"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $service container status: $status"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $service container is not running"
        return 1
    fi
}

# Check Docker daemon
echo -e "${BLUE}[Docker Daemon]${NC}"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker daemon is running"
else
    echo -e "${RED}✗${NC} Docker daemon is not accessible"
    exit 1
fi
echo ""

# Check containers
echo -e "${BLUE}[Containers]${NC}"
check_container "gaming_platform_postgres" "PostgreSQL"
check_container "gaming_platform_redis" "Redis"
check_container "gaming_platform_backend" "Backend API"
echo ""

# Check PostgreSQL
echo -e "${BLUE}[PostgreSQL]${NC}"
if docker exec gaming_platform_postgres pg_isready -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is accepting connections"
    
    # Check database exists
    if docker exec gaming_platform_postgres psql -U postgres -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw gaming_platform; then
        echo -e "${GREEN}✓${NC} gaming_platform database exists"
    else
        echo -e "${YELLOW}⚠${NC} gaming_platform database not found"
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL is not responding"
fi
echo ""

# Check Redis
echo -e "${BLUE}[Redis]${NC}"
if docker exec gaming_platform_redis redis-cli ping >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is responding"
else
    echo -e "${RED}✗${NC} Redis is not responding"
fi
echo ""

# Check Backend API
echo -e "${BLUE}[Backend API]${NC}"
if check_container "gaming_platform_backend" "Backend"; then
    # Wait a moment for the API to be ready
    sleep 2
    
    # Check health endpoint
    if check_http "http://localhost:8000/health" "Health endpoint"; then
        true
    fi
    
    # Check API docs
    if check_http "http://localhost:8000/docs" "API docs"; then
        true
    fi
fi
echo ""

# Check disk space
echo -e "${BLUE}[System Resources]${NC}"
DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓${NC} Disk usage: ${DISK_USAGE}% (healthy)"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠${NC} Disk usage: ${DISK_USAGE}% (warning)"
else
    echo -e "${RED}✗${NC} Disk usage: ${DISK_USAGE}% (critical)"
fi

# Check memory
MEMORY_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
if [ "$MEMORY_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓${NC} Memory usage: ${MEMORY_USAGE}% (healthy)"
elif [ "$MEMORY_USAGE" -lt 90 ]; then
    echo -e "${YELLOW}⚠${NC} Memory usage: ${MEMORY_USAGE}% (warning)"
else
    echo -e "${RED}✗${NC} Memory usage: ${MEMORY_USAGE}% (critical)"
fi
echo ""

# Docker stats
echo -e "${BLUE}[Container Stats]${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep gaming_platform || echo "No containers found"
echo ""

# Recent errors in logs
echo -e "${BLUE}[Recent Errors]${NC}"
ERROR_COUNT=$(docker-compose logs --tail=100 backend 2>/dev/null | grep -i "error\|exception\|critical" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No recent errors in backend logs"
else
    echo -e "${YELLOW}⚠${NC} Found $ERROR_COUNT error entries in recent backend logs"
    echo "  Run: docker-compose logs backend | grep -i error"
fi
echo ""

# Summary
echo "=================================="
echo "Health Check Complete"
echo "=================================="
echo ""
echo "Quick commands:"
echo "  View logs: docker-compose logs -f"
echo "  Restart services: docker-compose restart"
echo "  Check status: docker-compose ps"
echo ""
