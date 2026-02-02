#!/bin/bash
# System Resource Monitoring - Systemd Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}System Metrics Exporter Installer${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Variables
INSTALL_DIR="/opt/system-monitoring"
SERVICE_FILE="/etc/systemd/system/system-metrics-exporter.service"
USER="monitoring"
GROUP="monitoring"

# Create user and group
echo -e "${YELLOW}Creating user and group...${NC}"
if ! id -u $USER > /dev/null 2>&1; then
    useradd -r -s /bin/false $USER
    echo -e "${GREEN}✓ User created${NC}"
else
    echo -e "${YELLOW}User already exists${NC}"
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p $INSTALL_DIR
mkdir -p /var/log/system-monitoring

# Copy files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r src $INSTALL_DIR/
cp requirements.txt $INSTALL_DIR/

# Set permissions
chown -R $USER:$GROUP $INSTALL_DIR
chown -R $USER:$GROUP /var/log/system-monitoring
chmod 755 $INSTALL_DIR

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r $INSTALL_DIR/requirements.txt

# Copy systemd service file
echo -e "${YELLOW}Installing systemd service...${NC}"
cp systemd/system-metrics-exporter.service $SERVICE_FILE
chmod 644 $SERVICE_FILE

# Reload systemd
systemctl daemon-reload

# Enable and start service
echo -e "${YELLOW}Enabling and starting service...${NC}"
systemctl enable system-metrics-exporter.service
systemctl start system-metrics-exporter.service

# Check status
sleep 2
if systemctl is-active --quiet system-metrics-exporter.service; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    systemctl status system-metrics-exporter.service
    exit 1
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Service status: ${GREEN}Running${NC}"
echo -e "Metrics endpoint: http://localhost:9100/metrics"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status system-metrics-exporter  # Check status"
echo "  sudo systemctl stop system-metrics-exporter    # Stop service"
echo "  sudo systemctl restart system-metrics-exporter # Restart service"
echo "  sudo journalctl -u system-metrics-exporter -f  # View logs"
echo ""
