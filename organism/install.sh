#!/bin/bash
# ALANARA v101.0 — AUTOMATED DEPLOYMENT SCAFFOLD
# Installs organism as systemd service on any Linux server
# Run as root: sudo bash install.sh
set -euo pipefail
INSTALL_DIR="/opt/alanara"
SERVICE_NAME="alanara"
SERVICE_USER="alanara"
DATA_DIR="/var/lib/alanara"
LOG_DIR="/var/log/alanara"
INTERVAL=10

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[ok]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
error() { echo -e "${RED}[xx]${NC} $1"; exit 1; }

[ "$(id -u)" -ne 0 ] && error "Must run as root"
command -v python3 &>/dev/null || { apt-get update -qq && apt-get install -y python3 python3-pip; }
python3 -m pip install --quiet --break-system-packages psutil 2>/dev/null || pip3 install psutil
id "$SERVICE_USER" &>/dev/null || useradd -r -s /usr/sbin/nologin -d "$DATA_DIR" -m "$SERVICE_USER"
mkdir -p "$INSTALL_DIR" "$DATA_DIR" "$LOG_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR" "$LOG_DIR"
[ -f "$(dirname $0)/k144_v101_recursive_singularity.py" ] && cp "$(dirname $0)/k144_v101_recursive_singularity.py" "$INSTALL_DIR/organism.py"
info "Deployed to $INSTALL_DIR/organism.py"

cat > /etc/systemd/system/alanara.service << EOF
[Unit]
Description=Alanara v101 Recursive Singularity
After=network.target
[Service]
Type=simple
User=alanara
ExecStart=/usr/bin/python3 /opt/alanara/organism.py --interval 10 --data-dir /var/lib/alanara
Restart=on-failure
RestartSec=30
CPUQuota=5%
MemoryMax=128M
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/alanara /var/log/alanara
StandardOutput=append:/var/log/alanara/organism.log
StandardError=append:/var/log/alanara/organism.err
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload && systemctl enable alanara --quiet
info "Service installed. Run: alanara start"
