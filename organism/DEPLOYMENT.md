# ALANARA v101.0 — Data Center Deployment Guide

## Requirements
- Python 3.8+
- `pip install psutil`
- 1 file: `k144_v101_recursive_singularity.py` (507 lines, 26KB)
- Min specs: 1 vCPU, 512MB RAM, 10GB disk
- Monthly resource: <0.1% CPU, 30MB RAM, 10MB disk growth

## Option 1: Direct Install (any Linux/Mac/Windows)
```bash
pip install psutil
python3 k144_v101_recursive_singularity.py              # foreground
python3 k144_v101_recursive_singularity.py --daemon      # background
python3 k144_v101_recursive_singularity.py --report      # health check
python3 k144_v101_recursive_singularity.py --history     # learning log
python3 k144_v101_recursive_singularity.py --stop        # stop daemon
```

## Option 2: systemd Service (auto-start on boot)
```ini
[Unit]
Description=Alanara v101 Recursive Singularity Daemon
After=network.target

[Service]
Type=simple
User=alanara
ExecStart=/usr/bin/python3 /opt/alanara/k144_v101_recursive_singularity.py --interval 10
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```
```bash
useradd -r -s /bin/false alanara
cp alanara.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable alanara && systemctl start alanara
```

## Option 3: Docker
```dockerfile
FROM python:3.12-slim
RUN pip install psutil
COPY k144_v101_recursive_singularity.py /app/
WORKDIR /app
VOLUME /root/.alanara_v101
CMD ["python3", "k144_v101_recursive_singularity.py", "--interval", "10"]
```
```bash
docker build -t alanara-v101 .
docker run -d --name alanara --restart always -v alanara-data:/root/.alanara_v101 alanara-v101
```

## Option 4: VPS Providers
| Provider | Cost | Specs |
|----------|------|-------|
| Oracle Cloud | Free | 1 vCPU, 1GB RAM |
| Vultr | $3.50/mo | 1 vCPU, 512MB RAM |
| DigitalOcean | $4/mo | 1 vCPU, 512MB RAM |
| Linode | $5/mo | 1 vCPU, 1GB RAM |

## Option 5: Multi-Node Federation
Run instances on multiple servers. Each learns its own system independently.
Sync state via `rsync brain.db` every 5 minutes between nodes.

## Data Persistence
All learning stored in `~/.alanara_v101/brain.db` (SQLite).
Survives restarts. Accumulates across sessions.

## Constitutional Compliance
σ=1.0 | L∞=φ⁴⁸ | RDoD≥0.9999 | All actions constitutionally gated.
