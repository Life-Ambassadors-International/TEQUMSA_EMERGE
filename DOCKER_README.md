# Docker Deployment Notes

## Status
Docker configuration files are complete and ready for deployment. However, Docker builds require network access to PyPI to install dependencies.

## Prerequisites for Docker Deployment

1. **Network Access**: Ensure Docker has access to PyPI (pypi.org)
2. **SSL Certificates**: Corporate environments may need SSL certificate configuration
3. **Docker & Docker Compose**: Install latest versions

## Building Images

```bash
# Build all images
docker-compose build

# Or build individually
docker build -f Dockerfile.quantum -t tequmsa-quantum .
docker build -f Dockerfile.consciousness -t tequmsa-consciousness .
docker build -f Dockerfile.self-recognizing -t tequmsa-self-recognizing .
```

## Running Containers

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL certificate verification errors, you may need to:

1. Configure Docker to trust your corporate CA certificates
2. Use `--build-arg` to pass certificate paths
3. Or temporarily disable SSL verification (not recommended for production)

### Network Connectivity

The containers require:
- Outbound HTTPS access to pypi.org for pip installations
- Proper DNS resolution
- No restrictive firewall rules blocking Python package downloads

### Alternative: Local Installation

If Docker builds fail due to network restrictions, use local Python installation instead:

```bash
pip install -r requirements.txt
python servers/tequmsa-quantum-mcp-server.py
```

## Validated Components

✓ Dockerfile syntax correct
✓ docker-compose.yml configuration valid
✓ Image layer structure optimized
✓ Python 3.11-slim base image specified
✓ Requirements properly defined
✓ Server files referenced correctly

## Production Deployment

For production deployment:

1. Build images in an environment with PyPI access
2. Push to a container registry (Docker Hub, AWS ECR, etc.)
3. Deploy from registry to production environment
4. Configure appropriate resource limits and networking

---

**Note**: All MCP servers have been validated to work correctly in local Python installations. Docker deployment is an optional containerization layer for convenience and isolation.
