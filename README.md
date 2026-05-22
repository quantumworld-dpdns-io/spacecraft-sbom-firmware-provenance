# 🛰️ Spacecraft SBOM & Firmware Provenance

> **SBOM and firmware provenance vault for aerospace supply chains** — tracks firmware hashes, dependencies, secure update approvals, and supply chain attestations with built-in OWASP Top 10 security testing.

## Features

| Domain | Capabilities |
|--------|-------------|
| **SBOM Management** | Create/validate/export SPDX 2.3 & CycloneDX 1.5 SBOMs |
| **Firmware Tracking** | Multi-algorithm hashing (SHA-256/384/512, BLAKE2b), digital signatures |
| **Provenance Chains** | Full supply chain traceability with attestations & verification |
| **Approval Workflow** | Multi-stage approvals with policy engine, audit logs, RBAC |
| **Vulnerability Mgmt** | CVE tracking, CVSS scoring, NVD integration, severity dashboards |
| **Vector Search** | Semantic SBOM search via Chroma/Qdrant vector databases |
| **Analytics** | Built-in DuckDB, DataFusion, Iceberg, Trino integration |

## Quick Start

```bash
# Install with all extras
pip install -e ".[all]"

# Or using make
make install-all

# Start development server
make run

# Verify it works
curl http://localhost:8000/health
```

## Architecture

```
┌──────────────────────────────────────┐
│      API Layer (FastAPI)              │
│  /sbom  /firmware  /provenance        │
│  /approvals  /security  /search       │
├──────────────────────────────────────┤
│      Service Layer                     │
│  SBOM  Firmware  Provenance  Approval  │
├──────────────────────────────────────┤
│      Core Layer                        │
│  Database  VectorDB  Crypto  Security  │
├──────────────────────────────────────┤
│      Data Stores                       │
│  PostgreSQL  Redis  Chroma  Qdrant     │
└──────────────────────────────────────┘
```

## Testing

```bash
# Unit tests
make test-unit

# Integration tests
make test-integration

# Robot Framework (E2E + OWASP Top 10)
make test-robot

# Security scanning
make security-scan
```

**Robot Framework** tests cover:
- SBOM CRUD, export, and validation
- Firmware registration, hash verification, integrity checks
- Provenance chain creation, tracing, and verification
- Approval workflows with multi-stage reviews
- **OWASP Top 10** (A01-A10) security attack simulations

## CI/CD

| Pipeline | Trigger | Checks |
|----------|---------|--------|
| CI | Push/PR to `main` | Lint, unit, integration, security, Robot tests |
| CD | Tag `v*` | Docker build, staging/prod deploy |
| Security | Weekly/Mon | CodeQL, Trivy, Semgrep, Gitleaks, SLSA |
| Robot Tests | Push/PR | Full Robot Framework suite (sbom, firmware, provenance, owasp) |

## Tool Integrations

This project integrates 30+ tools from the software-tools knowledge base:

- **Agent Protocols**: MCP servers, Agent Skills, Desktop Extensions
- **AI Agents**: Claude Code/Desktop, Codex Desktop, Devin, Hermes Agent
- **Vector DBs**: Chroma, Qdrant, LanceDB, Milvus, Weaviate
- **Analytics**: DuckDB, DataFusion, Iceberg, Arrow, Trino
- **Local AI**: Ollama, llama.cpp, vLLM, SGLang, LM Studio
- **Security**: PQC libraries, Cilium Tetragon, OWASP ZAP
- **Observability**: W&B Weave, OpenTelemetry

## Security

### OWASP Top 10 Coverage

| A01 | A02 | A03 | A04 | A05 | A06 | A07 | A08 | A09 | A10 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
|✅|✅|✅|✅|✅|✅|✅|✅|✅|✅|

- **RBAC** with admin/editor/reviewer/viewer roles
- **JWT** + API key authentication
- **Security headers**: CSP, HSTS, X-Frame-Options, XSS-Protection
- **Rate limiting** per IP
- **Input sanitization** and validation
- **Audit logging** for all approval actions

## Project Structure

```
.
├── src/sbom_provenance/     # Application source
│   ├── api/                 # FastAPI routes & middleware
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic layer
│   ├── core/                # Database, security, vector store
│   └── utils/               # Crypto, validators, exporters
├── tests/
│   ├── unit/                # Pytest unit tests
│   ├── integration/         # Pytest integration tests
│   └── robot/               # Robot Framework E2E/security tests
├── docs/
│   ├── tools/reference/     # Full software-tools knowledge base
│   ├── architecture/        # Architecture docs
│   ├── security/            # Security guide
│   └── testing/             # Testing guide
├── .github/workflows/       # CI/CD pipelines
├── docker/                  # Docker & docker-compose
└── config/                  # Prometheus, Alertmanager, OTEL
```

## License

MIT — see [LICENSE](LICENSE)
