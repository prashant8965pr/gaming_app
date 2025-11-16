#!/bin/bash
# Gaming Platform - Health Check Script
# Usage: ./health-check.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
MAX_RETRIES=10
RETRY_DELAY=5
BASE_URL=${BASE_URL:-http://localhost}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gaming Platform - Health Check${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    echo -e "${YELLOW}Checking: $description${NC}"
    echo -e "  Endpoint: $endpoint"

    for i in $(seq 1 $MAX_RETRIES); do
        response=$(curl -s -o /dev/null -w "%{http_code}" $endpoint 2>/dev/null || echo "000")

        if [ "$response" == "$expected_status" ]; then
            echo -e "  ${GREEN}✓ Status: $response (OK)${NC}\n"
            return 0
        fi

        if [ $i -lt $MAX_RETRIES ]; then
            echo -e "  ${YELLOW}Status: $response (Retry $i/$MAX_RETRIES in ${RETRY_DELAY}s...)${NC}"
            sleep $RETRY_DELAY
        fi
    done

    echo -e "  ${RED}✗ Status: $response (FAILED)${NC}\n"
    return 1
}

# Function to check Docker service
check_docker_service() {
    local service=$1
    local description=$2

    echo -e "${YELLOW}Checking Docker service: $description${NC}"

    status=$(docker-compose -f docker-compose.prod.yml ps $service 2>/dev/null | grep "Up" || echo "Down")

    if [[ $status == *"Up"* ]]; then
        echo -e "  ${GREEN}✓ Service is running${NC}\n"
        return 0
    else
        echo -e "  ${RED}✗ Service is not running${NC}\n"
        return 1
    fi
}

# Check Docker services
echo -e "${GREEN}=== Docker Services ===${NC}\n"
check_docker_service "postgres" "PostgreSQL Database" || FAILED=1
check_docker_service "redis" "Redis Cache" || FAILED=1
check_docker_service "backend" "Backend API" || FAILED=1
check_docker_service "nginx" "Nginx Proxy" || FAILED=1

# Check API endpoints
echo -e "${GREEN}=== API Endpoints ===${NC}\n"
check_endpoint "$BASE_URL/health" "200" "Health Check" || FAILED=1
check_endpoint "$BASE_URL/api/v1/games/catalog" "200" "Games Catalog" || FAILED=1

# Check database connectivity
echo -e "${GREEN}=== Database Connectivity ===${NC}\n"
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
db_check=$(docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U $POSTGRES_USER 2>&1 || echo "failed")

if [[ $db_check == *"accepting connections"* ]]; then
    echo -e "  ${GREEN}✓ PostgreSQL is accepting connections${NC}\n"
else
    echo -e "  ${RED}✗ PostgreSQL is not responding${NC}\n"
    FAILED=1
fi

# Check Redis connectivity
echo -e "${GREEN}=== Redis Connectivity ===${NC}\n"
echo -e "${YELLOW}Checking Redis connection...${NC}"
redis_check=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping 2>&1 || echo "failed")

if [[ $redis_check == *"PONG"* ]]; then
    echo -e "  ${GREEN}✓ Redis is responding${NC}\n"
else
    echo -e "  ${RED}✗ Redis is not responding${NC}\n"
    FAILED=1
fi

# Check disk space
echo -e "${GREEN}=== Disk Space ===${NC}\n"
echo -e "${YELLOW}Checking disk usage...${NC}"
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $disk_usage -lt 80 ]; then
    echo -e "  ${GREEN}✓ Disk usage: ${disk_usage}% (OK)${NC}\n"
else
    echo -e "  ${YELLOW}⚠ Disk usage: ${disk_usage}% (WARNING)${NC}\n"
fi

# Check memory usage
echo -e "${GREEN}=== Memory Usage ===${NC}\n"
echo -e "${YELLOW}Checking memory usage...${NC}"
mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')

if [ $mem_usage -lt 90 ]; then
    echo -e "  ${GREEN}✓ Memory usage: ${mem_usage}% (OK)${NC}\n"
else
    echo -e "  ${YELLOW}⚠ Memory usage: ${mem_usage}% (WARNING)${NC}\n"
fi

# Final result
echo -e "${GREEN}========================================${NC}"
if [ -z "$FAILED" ]; then
    echo -e "${GREEN}✓ All health checks passed!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    exit 0
else
    echo -e "${RED}✗ Some health checks failed!${NC}"
    echo -e "${RED}========================================${NC}\n"
    echo -e "${YELLOW}View logs with:${NC}"
    echo -e "  docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    exit 1
fi
