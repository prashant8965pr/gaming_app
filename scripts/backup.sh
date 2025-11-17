#!/bin/bash

# Gaming Platform - Database Backup Script
# This script creates a backup of the PostgreSQL database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/gaming_platform_$TIMESTAMP.sql"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================="
echo "Gaming Platform - Database Backup"
echo "=================================="
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if PostgreSQL container is running
if ! docker ps | grep -q gaming_platform_postgres; then
    echo -e "${RED}ERROR:${NC} PostgreSQL container is not running"
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} Starting backup..."
echo -e "${BLUE}[INFO]${NC} Backup file: $BACKUP_FILE"

# Create backup
if docker exec gaming_platform_postgres pg_dump -U postgres gaming_platform > "$BACKUP_FILE"; then
    echo -e "${GREEN}[SUCCESS]${NC} Database backup created successfully"
    
    # Compress backup
    echo -e "${BLUE}[INFO]${NC} Compressing backup..."
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}[SUCCESS]${NC} Backup compressed: $BACKUP_FILE ($SIZE)"
    
    # Clean old backups (keep last 7 days)
    echo -e "${BLUE}[INFO]${NC} Cleaning old backups (keeping last 7 days)..."
    find "$BACKUP_DIR" -name "gaming_platform_*.sql.gz" -mtime +7 -delete
    
    # List recent backups
    echo ""
    echo "Recent backups:"
    ls -lh "$BACKUP_DIR"/gaming_platform_*.sql.gz 2>/dev/null | tail -5
    
else
    echo -e "${RED}[ERROR]${NC} Backup failed"
    exit 1
fi

echo ""
echo "=================================="
echo "Backup Complete"
echo "=================================="
