# API Reference

## Base URL
`http://localhost:8000/api/v1`

## Authentication
- **Bearer Token**: `Authorization: Bearer <token>`
- **API Key**: `X-API-Key: <key>`

## Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/health` | API health check |

### SBOM Documents
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/sbom` | Create SBOM document |
| GET | `/api/v1/sbom` | List SBOM documents |
| GET | `/api/v1/sbom/{id}` | Get SBOM by ID |
| PATCH | `/api/v1/sbom/{id}` | Update SBOM |
| DELETE | `/api/v1/sbom/{id}` | Delete SBOM |
| POST | `/api/v1/sbom/{id}/validate` | Validate SBOM |
| GET | `/api/v1/sbom/{id}/export` | Export SBOM |
| GET | `/api/v1/sbom/stats/summary` | SBOM statistics |

### Firmware Images
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/firmware` | Register firmware |
| GET | `/api/v1/firmware` | List firmware |
| GET | `/api/v1/firmware/{id}` | Get firmware by ID |
| POST | `/api/v1/firmware/{id}/verify` | Verify firmware |
| POST | `/api/v1/firmware/hash/verify` | Verify firmware hash |
| POST | `/api/v1/firmware/hash/compute` | Compute firmware hash |
| GET | `/api/v1/firmware/stats/summary` | Firmware statistics |

### Provenance
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/provenance/chains` | Create chain |
| GET | `/api/v1/provenance/chains` | List chains |
| GET | `/api/v1/provenance/chains/{id}` | Get chain by ID |
| GET | `/api/v1/provenance/trace/{type}/{id}` | Trace provenance |
| POST | `/api/v1/provenance/chains/{id}/verify` | Verify chain |

### Approvals
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/approvals/requests` | Create request |
| GET | `/api/v1/approvals/requests` | List requests |
| GET | `/api/v1/approvals/requests/{id}` | Get request |
| POST | `/api/v1/approvals/requests/{id}/review` | Review request |
| GET | `/api/v1/approvals/requests/{id}/audit` | Audit log |
| POST | `/api/v1/approvals/policies` | Create policy |
| GET | `/api/v1/approvals/policies` | List policies |

### Security
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/security/vulnerabilities` | Create vulnerability |
| GET | `/api/v1/security/vulnerabilities` | List vulnerabilities |
| GET | `/api/v1/security/vulnerabilities/{id}` | Get vulnerability |
| POST | `/api/v1/security/scans` | Start scan |
| GET | `/api/v1/security/scans/{id}` | Get scan result |
| GET | `/api/v1/security/stats/summary` | Security statistics |

### Search
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/search` | Global search |
| GET | `/api/v1/search/sbom` | Search SBOMs |
| GET | `/api/v1/search/firmware` | Search firmware |
