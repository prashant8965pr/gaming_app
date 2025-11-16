#!/bin/bash
# Gaming Platform - Database Backup Script
# Usage: ./backup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gaming Platform - Database Backup${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating database backup...${NC}"
echo -e "Database: $POSTGRES_DB"
echo -e "Backup file: $BACKUP_DIR/$BACKUP_FILE\n"

# Create backup
docker-compose -f $COMPOSE_FILE exec -T postgres \
    pg_dump -U $POSTGRES_USER $POSTGRES_DB | \
    gzip > $BACKUP_DIR/$BACKUP_FILE

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)
    echo -e "${GREEN}✓ Backup created successfully${NC}"
    echo -e "  File: $BACKUP_FILE"
    echo -e "  Size: $BACKUP_SIZE"
else
    echo -e "${RED}✗ Backup failed${NC}"
    exit 1
fi

# Clean up old backups
echo -e "\n${YELLOW}Cleaning up old backups (keeping last $RETENTION_DAYS days)...${NC}"
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

BACKUP_COUNT=$(ls -1 $BACKUP_DIR/backup_*.sql.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Current backup count: $BACKUP_COUNT${NC}"

# List recent backups
echo -e "\n${YELLOW}Recent backups:${NC}"
ls -lh $BACKUP_DIR/backup_*.sql.gz | tail -5

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"
