#!/bin/bash
# Gaming Platform - Rollback Script
# Usage: ./rollback.sh [backup_file]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"

echo -e "${RED}========================================${NC}"
echo -e "${RED}Gaming Platform - ROLLBACK${NC}"
echo -e "${RED}========================================${NC}\n"

echo -e "${YELLOW}⚠️  WARNING: This will rollback to a previous version${NC}\n"

# Stop current services
echo -e "${YELLOW}Step 1: Stopping current services...${NC}"
docker-compose -f $COMPOSE_FILE down
echo -e "${GREEN}✓ Services stopped${NC}\n"

# Restore database
echo -e "${YELLOW}Step 2: Restoring database...${NC}"
./scripts/restore.sh $1
echo -e "${GREEN}✓ Database restored${NC}\n"

# Restart services
echo -e "${YELLOW}Step 3: Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d
echo -e "${GREEN}✓ Services started${NC}\n"

# Health check
echo -e "${YELLOW}Step 4: Running health checks...${NC}"
sleep 15
./scripts/health-check.sh

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Rollback completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
else
    echo -e "\n${RED}Health checks failed after rollback${NC}"
    echo -e "${YELLOW}Please investigate the issue${NC}\n"
    exit 1
fi
