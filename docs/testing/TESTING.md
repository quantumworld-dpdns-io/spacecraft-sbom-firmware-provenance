# Testing Guide

## Test Framework Overview

| Layer | Framework | Location |
|-------|-----------|----------|
| Unit | Pytest | `tests/unit/` |
| Integration | Pytest + HTTPX | `tests/integration/` |
| E2E/API | Robot Framework | `tests/robot/` |
| Security | Robot Framework + Bandit | `tests/robot/test_cases/security/` |
| OWASP | Robot Framework | `tests/robot/test_cases/security/owasp_top_10.robot` |

## Running Tests

### All Tests
```bash
make test
```

### Unit Tests
```bash
make test-unit
# or
pytest tests/unit -v
```

### Integration Tests
```bash
make test-integration
# or
pytest tests/integration -v
```

### Robot Framework Tests
```bash
make test-robot
# or
robot --outputdir tests/robot/output tests/robot/
```

### Security Tests
```bash
make test-security
# or
bandit -r src/ -ll
safety check --full-report
```

### Coverage
```bash
make coverage
# or
pytest --cov=src --cov-report=html --cov-report=term
```

## Robot Framework Test Categories

| Test Suite | Path | Description |
|------------|------|-------------|
| SBOM CRUD | `tests/robot/test_cases/sbom/` | SBOM create/read/update/delete/export |
| Firmware | `tests/robot/test_cases/firmware/` | Firmware register/verify/hash |
| Provenance | `tests/robot/test_cases/provenance/` | Provenance chains/trace/verify |
| Approvals | `tests/robot/test_cases/approval/` | Approval workflow/policies/audit |
| OWASP Top 10 | `tests/robot/test_cases/security/` | A01-A10 security tests |
| Security | `tests/robot/test_cases/security/` | XSS, rate limit, auth, headers |

## Writing Tests

### Unit Test Example
```python
async def test_sbom_service_create(db_session):
    service = SBOMService(db_session)
    doc = await service.create(SBOMDocumentCreate(
        name="Test", version="1.0.0"
    ))
    assert doc.name == "Test"
```

### Robot Framework Test Example
```robot
*** Test Cases ***
Create SBOM Document
    ${doc}=    Create SBOM API    name=Test-SBOM    version=1.0.0
    Assert JSON Contains    ${doc}    name    Test-SBOM
```
