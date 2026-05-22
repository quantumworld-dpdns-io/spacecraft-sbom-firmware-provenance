*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/security_keywords.robot
Suite Setup    Wait For API

*** Test Cases ***
A01-Broken Access Control - Unauthenticated Access
    [Tags]    owasp    a01    security
    ${resp}=    Test Unauthenticated Access    ${BASE_URL}${API_PREFIX}/sbom
    Should Be Equal As Numbers    ${resp.status_code}    401
    ${body}=    Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${body}    detail

A01-Broken Access Control - Insufficient Role
    [Tags]    owasp    a01    security
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${resp}=    DELETE    ${API_PREFIX}/sbom/test-id    headers=${headers}    expected_status=401
    Should Be Equal As Numbers    ${resp.status_code}    401

A02-Cryptographic Failures - HSTS Headers Present
    [Tags]    owasp    a02    security
    Test Missing HTTPS Header    ${BASE_URL}/health

A03-Injection - SQL Injection Protection
    [Tags]    owasp    a03    security
    ${resp}=    Test SQL Injection Payload    ${API_PREFIX}/search    "' OR '1'='1"
    ${resp}=    Test SQL Injection Payload    ${API_PREFIX}/search    "'; DROP TABLE sbom_documents; --"
    ${resp}=    Test SQL Injection Payload    ${API_PREFIX}/search    "' UNION SELECT * FROM users --"

A03-Injection - NoSQL Injection Protection
    [Tags]    owasp    a03    security
    Test NoSQL Injection Payload    ${API_PREFIX}/search    '{"$ne": null}'
    Test NoSQL Injection Payload    ${API_PREFIX}/search    '{"$gt": ""}'

A04-Insecure Design - Input Validation
    [Tags]    owasp    a04    security
    ${body}=    Create Dictionary    name=${EMPTY}    version=${EMPTY}
    Test Input Validation    ${API_PREFIX}/sbom    ${body}

A05-Security Misconfiguration - Default Headers
    [Tags]    owasp    a05    security
    Test Default Headers    ${BASE_URL}/health

A06-Vulnerable Components - Dependency Check
    [Tags]    owasp    a06    security
    Log    Dependency scanning runs in CI pipeline

A07-Authentication Failures - Token Validation
    [Tags]    owasp    a07    security
    ${resp}=    Test Token Expiry    expired.jwt.token.here
    Should Be Equal As Numbers    ${resp.status_code}    401

A08-Software Integrity Failures - SBOM Verification
    [Tags]    owasp    a08    security
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary    name=Integrity-Test    version=1.0.0
    ${resp}=    POST    /sbom    json=${body}    headers=${headers}    expected_status=201
    ${doc}=    Set Variable    ${resp.json()}
    ${verified}=    Test SBOM Signature    ${doc}[id]
    Should Be Equal As Strings    ${verified}    False

A09-Logging Failures - Audit Trail
    [Tags]    owasp    a09    security
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    request_type=test
    ...    target_id=test-audit-001
    ...    target_type=firmware
    ...    title=Audit Test
    ${resp}=    POST    /approvals/requests    json=${body}    headers=${headers}    expected_status=201
    ${req}=    Set Variable    ${resp.json()}
    Test Audit Log Exists    ${req}[id]

A10-SSRF - Server Side Request Forgery Protection
    [Tags]    owasp    a10    security
    Test SSRF Protection    ${API_PREFIX}/sbom    http://169.254.169.254/latest/meta-data/
    Test SSRF Protection    ${API_PREFIX}/sbom    http://localhost:5432
    Test SSRF Protection    ${API_PREFIX}/sbom    file:///etc/passwd
