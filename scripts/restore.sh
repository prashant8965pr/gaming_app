#!/bin/bash
# Gaming Platform - Database Restore Script
# Usage: ./restore.sh [backup_file]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
BACKUP_FILE=$1

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gaming Platform - Database Restore${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# If no backup file specified, list available backups
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lht $BACKUP_DIR/backup_*.sql.gz | nl
    echo ""
    read -p "Enter backup number to restore (or 'latest' for most recent): " choice

    if [ "$choice" == "latest" ]; then
        BACKUP_FILE=$(ls -t $BACKUP_DIR/backup_*.sql.gz | head -1)
    else
        BACKUP_FILE=$(ls -t $BACKUP_DIR/backup_*.sql.gz | sed -n "${choice}p")
    fi
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will REPLACE the current database!${NC}"
echo -e "Database: $POSTGRES_DB"
echo -e "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Restore cancelled${NC}"
    exit 0
fi

# Create a safety backup before restore
echo -e "\n${YELLOW}Creating safety backup...${NC}"
./scripts/backup.sh

# Stop backend services
echo -e "\n${YELLOW}Stopping backend services...${NC}"
docker-compose -f $COMPOSE_FILE stop backend celery_worker celery_beat

# Drop and recreate database
echo -e "\n${YELLOW}Dropping existing database...${NC}"
docker-compose -f $COMPOSE_FILE exec -T postgres psql -U $POSTGRES_USER -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
docker-compose -f $COMPOSE_FILE exec -T postgres psql -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB;"

# Restore backup
echo -e "\n${YELLOW}Restoring database from backup...${NC}"
gunzip < $BACKUP_FILE | docker-compose -f $COMPOSE_FILE exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restored successfully${NC}"
else
    echo -e "${RED}✗ Restore failed${NC}"
    exit 1
fi

# Restart services
echo -e "\n${YELLOW}Restarting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
sleep 10

# Health check
echo -e "\n${YELLOW}Running health checks...${NC}"
./scripts/health-check.sh

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Database restored successfully!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
else
    echo -e "\n${RED}Health check failed after restore${NC}"
    echo -e "${YELLOW}Please check the logs${NC}\n"
    exit 1
fi
