# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (CLI / API / Webhooks / AI Agents / MCP Clients)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 API Gateway / Load Balancer                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Application                         │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────────────┐    │
│  │ Auth Layer  │ │ Rate Limiter │ │ Security Headers   │    │
│  └──────┬──────┘ └──────┬───────┘ └────────┬───────────┘    │
│         │               │                   │                │
│  ┌──────▼───────────────▼───────────────────▼──────────────┐│
│  │                    API Routes                             ││
│  │  /sbom  /firmware  /provenance  /approvals  /security    ││
│  └──────────────────────┬──────────────────────────────────┘│
│         │               │                   │                │
│  ┌──────▼───────────────▼───────────────────▼──────────────┐│
│  │                   Service Layer                           ││
│  │  SBOM  Firmware  Provenance  Approval  Vulnerability      ││
│  └──────────────────────┬──────────────────────────────────┘│
│         │               │                   │                │
│  ┌──────▼───────────────▼───────────────────▼──────────────┐│
│  │                   Core Layer                              ││
│  │  Database  Vector Store  Security  Crypto  Logging        ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Data Stores                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │PostgreSQL│ │  Redis   │ │  Chroma  │ │    Qdrant      │  │
│  │ (Primary)│ │ (Cache)  │ │(VectorDB)│ │ (VectorDB alt) │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python 3.11+) |
| Database | PostgreSQL 16 (async via SQLAlchemy 2.0) |
| Caching | Redis 7 |
| Vector DB | Chroma / Qdrant |
| Auth | JWT / API Keys / OAuth2 |
| Testing | Pytest + Robot Framework |
| CI/CD | GitHub Actions |
| Container | Docker / Docker Compose |
| Monitoring | Prometheus + Grafana |

## Data Flow

1. Client sends request via API Gateway
2. Auth middleware validates credentials
3. Rate limiter checks request limits
4. Security headers middleware adds protections
5. Route handler processes request
6. Service layer executes business logic
7. Core layer handles data persistence
8. Response flows back through middleware chain

## Security Architecture

- JWT-based authentication with refresh tokens
- API key authentication for service-to-service
- Role-based access control (admin/editor/reviewer/viewer)
- Rate limiting per IP
- Security headers (CSP, HSTS, X-Frame-Options)
- Input sanitization and validation
- SQL injection prevention via ORM
- CORS configuration
- Audit logging for all approval actions
