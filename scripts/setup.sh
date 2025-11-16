#!/bin/bash
# Gaming Platform - Initial Server Setup Script
# Usage: sudo ./setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Gaming Platform - Server Setup${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
echo -e "${GREEN}✓ System updated${NC}\n"

# Install Docker
echo -e "${YELLOW}Step 2: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed${NC}\n"
else
    echo -e "${GREEN}✓ Docker already installed${NC}\n"
fi

# Install Docker Compose
echo -e "${YELLOW}Step 3: Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION="2.23.0"
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}\n"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}\n"
fi

# Install additional tools
echo -e "${YELLOW}Step 4: Installing additional tools...${NC}"
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    certbot \
    python3-certbot-nginx
echo -e "${GREEN}✓ Additional tools installed${NC}\n"

# Configure firewall
echo -e "${YELLOW}Step 5: Configuring firewall...${NC}"
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
echo -e "${GREEN}✓ Firewall configured${NC}\n"

# Create application user
echo -e "${YELLOW}Step 6: Creating application user...${NC}"
if ! id -u gaming &> /dev/null; then
    useradd -m -s /bin/bash gaming
    usermod -aG docker gaming
    echo -e "${GREEN}✓ User 'gaming' created${NC}\n"
else
    echo -e "${GREEN}✓ User 'gaming' already exists${NC}\n"
fi

# Create application directory
echo -e "${YELLOW}Step 7: Setting up application directory...${NC}"
APP_DIR="/home/gaming/gaming-platform"
mkdir -p $APP_DIR/{backups,logs,uploads,nginx/ssl}
chown -R gaming:gaming $APP_DIR
echo -e "${GREEN}✓ Application directory created${NC}\n"

# Setup log rotation
echo -e "${YELLOW}Step 8: Configuring log rotation...${NC}"
cat > /etc/logrotate.d/gaming-platform << EOF
$APP_DIR/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 gaming gaming
    sharedscripts
    postrotate
        docker-compose -f $APP_DIR/docker-compose.prod.yml restart backend
    endscript
}
EOF
echo -e "${GREEN}✓ Log rotation configured${NC}\n"

# Setup automatic backups
echo -e "${YELLOW}Step 9: Setting up automatic backups...${NC}"
cat > /etc/cron.d/gaming-backup << EOF
# Daily database backup at 2 AM
0 2 * * * gaming cd $APP_DIR && ./scripts/backup.sh >> $APP_DIR/logs/backup.log 2>&1
EOF
echo -e "${GREEN}✓ Automatic backups configured${NC}\n"

# Setup system monitoring
echo -e "${YELLOW}Step 10: Configuring system monitoring...${NC}"
cat > /etc/cron.d/gaming-monitoring << EOF
# Health check every 5 minutes
*/5 * * * * gaming cd $APP_DIR && ./scripts/health-check.sh >> $APP_DIR/logs/health.log 2>&1
EOF
echo -e "${GREEN}✓ System monitoring configured${NC}\n"

# Setup swap (if not exists)
echo -e "${YELLOW}Step 11: Configuring swap space...${NC}"
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo -e "${GREEN}✓ Swap configured (4GB)${NC}\n"
else
    echo -e "${GREEN}✓ Swap already configured${NC}\n"
fi

# Optimize system settings
echo -e "${YELLOW}Step 12: Optimizing system settings...${NC}"
cat >> /etc/sysctl.conf << EOF

# Gaming Platform Optimizations
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.ip_local_port_range=1024 65535
EOF
sysctl -p
echo -e "${GREEN}✓ System settings optimized${NC}\n"

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Server setup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Switch to gaming user: ${GREEN}su - gaming${NC}"
echo -e "2. Clone repository: ${GREEN}git clone <repo-url> ~/gaming-platform${NC}"
echo -e "3. Configure environment: ${GREEN}cp .env.example .env${NC}"
echo -e "4. Edit .env file: ${GREEN}vim .env${NC}"
echo -e "5. Deploy application: ${GREEN}./scripts/deploy.sh production${NC}"
echo ""

echo -e "${YELLOW}Installed versions:${NC}"
docker --version
docker-compose --version
echo ""

echo -e "${YELLOW}Application directory:${NC} $APP_DIR"
echo -e "${YELLOW}Application user:${NC} gaming"
echo ""
