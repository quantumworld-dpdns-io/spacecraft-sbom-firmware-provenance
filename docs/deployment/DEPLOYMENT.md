# Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose

## Local Development

```bash
# Clone and setup
git clone <repo>
cd spacecraft-sbom-firmware-provenance

# Install dependencies
make dev
make install-all

# Initialize database
make migrate

# Start server
make run
```

## Docker Deployment

```bash
# Build and start services
docker compose -f docker/docker-compose.yml up -d

# Run migrations
docker compose exec app alembic upgrade head

# Check health
curl http://localhost:8000/health
```

## Production Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/sbom
REDIS_URL=redis://host:6379/0
SECRET_KEY=<generate-random-256-bit-key>
ENVIRONMENT=production
LOG_LEVEL=info
```

### Kubernetes (via Helm)
```bash
helm upgrade --install sbom-provenance ./charts/sbom-provenance \
  --set image.tag=v0.1.0 \
  --set secrets.secretKey=<key>
```

## CI/CD Pipeline

1. **CI** (on push/PR):
   - Lint & format check
   - Unit tests (Python 3.11, 3.12)
   - Integration tests
   - Security scanning (Bandit, Safety, CodeQL)
   - Robot Framework tests
   - Build & package

2. **CD** (on tag v*):
   - Build Docker image
   - Push to registry
   - Deploy to staging
   - Health check
   - Deploy to production
   - Rollback on failure

## Monitoring

- Prometheus metrics at `/metrics`
- Grafana dashboards for:
  - Request rate/latency/errors
  - Database connections
  - Cache hit ratio
  - Security events
  - SBOM/firmware counts
