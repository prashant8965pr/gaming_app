#!/bin/bash
# Gaming Platform - Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gaming Platform Deployment${NC}"
echo -e "${GREEN}Environment: $ENVIRONMENT${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo -e "${RED}Error: Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure it${NC}"
    exit 1
fi

# Confirmation for production
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "${YELLOW}⚠️  WARNING: You are about to deploy to PRODUCTION${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 0
    fi
fi

# Step 1: Create backup (production only)
if [ "$ENVIRONMENT" == "production" ]; then
    echo -e "\n${YELLOW}Step 1: Creating backup...${NC}"
    ./scripts/backup.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Backup failed! Aborting deployment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Backup created successfully${NC}"
else
    echo -e "\n${YELLOW}Step 1: Skipping backup (staging environment)${NC}"
fi

# Step 2: Pull latest images
echo -e "\n${YELLOW}Step 2: Pulling latest Docker images...${NC}"
docker-compose -f $COMPOSE_FILE pull
echo -e "${GREEN}✓ Images pulled successfully${NC}"

# Step 3: Run database migrations
echo -e "\n${YELLOW}Step 3: Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE run --rm backend alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "${RED}Migration failed! Aborting deployment.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Migrations completed successfully${NC}"

# Step 4: Deploy services
echo -e "\n${YELLOW}Step 4: Deploying services...${NC}"

if [ "$ENVIRONMENT" == "production" ]; then
    # Rolling update for production
    echo -e "${YELLOW}Performing rolling update...${NC}"

    # Scale up backend
    docker-compose -f $COMPOSE_FILE up -d --no-deps --scale backend=4 backend
    sleep 30

    # Scale down to normal
    docker-compose -f $COMPOSE_FILE up -d --no-deps --scale backend=2 backend
    sleep 10

    # Update other services
    docker-compose -f $COMPOSE_FILE up -d
else
    # Simple update for staging
    docker-compose -f $COMPOSE_FILE up -d --build
fi

echo -e "${GREEN}✓ Services deployed successfully${NC}"

# Step 5: Health check
echo -e "\n${YELLOW}Step 5: Running health checks...${NC}"
./scripts/health-check.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Health check failed!${NC}"

    if [ "$ENVIRONMENT" == "production" ]; then
        echo -e "${YELLOW}Initiating rollback...${NC}"
        ./scripts/rollback.sh
        exit 1
    else
        echo -e "${YELLOW}Check the logs for errors${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Health checks passed${NC}"

# Step 6: Clean up
echo -e "\n${YELLOW}Step 6: Cleaning up...${NC}"
docker image prune -af
echo -e "${GREEN}✓ Cleanup completed${NC}"

# Step 7: Display status
echo -e "\n${YELLOW}Step 7: Service Status${NC}"
docker-compose -f $COMPOSE_FILE ps

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}Environment: $ENVIRONMENT${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Display useful commands
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo -e "  Stop:         docker-compose -f $COMPOSE_FILE down"
echo -e "  Restart:      docker-compose -f $COMPOSE_FILE restart"
echo -e "  Status:       docker-compose -f $COMPOSE_FILE ps"
echo ""
