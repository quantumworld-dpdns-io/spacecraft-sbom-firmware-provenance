# Security Guide

## OWASP Top 10 Coverage

| Category | Implementation | Status |
|----------|---------------|--------|
| A01: Broken Access Control | RBAC, JWT validation, API key auth | ✅ |
| A02: Cryptographic Failures | SHA-256/384/512, BLAKE2b, bcrypt, HSTS | ✅ |
| A03: Injection | SQLAlchemy ORM, input sanitization | ✅ |
| A04: Insecure Design | Input validation schemas, rate limiting | ✅ |
| A05: Security Misconfiguration | Security headers middleware, CORS | ✅ |
| A06: Vulnerable Components | pip-audit, safety, dependency scanning | ✅ |
| A07: Auth Failures | JWT with expiry, refresh tokens | ✅ |
| A08: Integrity Failures | SBOM signing, firmware hash verification | ✅ |
| A09: Logging Failures | Audit logging for approvals | ✅ |
| A10: SSRF | URL validation, restricted outbound | ✅ |

## Security Headers

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## Authentication Methods

### JWT Tokens
- Access token: 30 min expiry
- Refresh token: 7 day expiry
- Signed with HS256

### API Keys
- Format: `sbom_<random>`
- Used for service-to-service communication

### Role Hierarchy
- `admin`: Full access
- `editor`: Create/update resources
- `reviewer`: Review and verify
- `viewer`: Read-only access

## Encryption

- Passwords: bcrypt (12 rounds)
- Data at rest: PostgreSQL TDE
- Data in transit: TLS 1.3
- Firmware hashes: SHA-256/384/512, BLAKE2b

## Security Testing

### SAST Tools
- Bandit (Python)
- Semgrep (custom rules)
- CodeQL (GitHub)

### DAST Tools
- OWASP ZAP
- Robot Framework security tests

### Dependency Scanning
- pip-audit
- Safety
- Dependabot
- Trivy (container)
