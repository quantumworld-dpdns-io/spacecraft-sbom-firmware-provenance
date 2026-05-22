*** Settings ***
Library    RequestsLibrary
Library    Collections

*** Keywords ***
# OWASP A01 - Broken Access Control Tests
Test Unauthenticated Access
    [Arguments]    ${endpoint}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${resp}=    GET    ${endpoint}    headers=${headers}    expected_status=401
    RETURN    ${resp}

Test Role Based Access
    [Arguments]    ${endpoint}    ${method}=GET    ${expected_status}=403
    ${headers}=    Create Dictionary    Content-Type=application/json
    ...    Authorization=Bearer test_viewer_token
    ${resp}=    ${method}    ${endpoint}    headers=${headers}    expected_status=${expected_status}
    RETURN    ${resp}

# OWASP A02 - Cryptographic Failures Tests
Test Missing HTTPS Header
    [Arguments]    ${endpoint}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${resp}=    GET    ${endpoint}    headers=${headers}
    ${hsts}=    Get From Dictionary    ${resp.headers}    Strict-Transport-Security    default=NONE
    Should Not Be Equal As Strings    ${hsts}    NONE

Test Weak Password Detection
    [Arguments]    ${password}
    ${length}=    Get Length    ${password}
    Should Be True    ${length} >= 8    Password must be at least 8 characters

# OWASP A03 - Injection Tests
Test SQL Injection Payload
    [Arguments]    ${endpoint}    ${payload}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${params}=    Create Dictionary    q=${payload}
    ${resp}=    GET    ${endpoint}    params=${params}    headers=${headers}    expected_status=any
    Should Not Contain    ${resp.text}    SQL syntax
    Should Not Contain    ${resp.text}    sqlite_master
    RETURN    ${resp}

Test NoSQL Injection Payload
    [Arguments]    ${endpoint}    ${payload}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${params}=    Create Dictionary    q=${payload}
    ${resp}=    GET    ${endpoint}    params=${params}    headers=${headers}    expected_status=any
    Should Not Be Equal As Strings    ${resp.status_code}    500

# OWASP A04 - Insecure Design Tests
Test Input Validation
    [Arguments]    ${endpoint}    ${invalid_body}
    ${headers}=    Create Dictionary    Content-Type=application/json    X-API-Key=test-key
    ${resp}=    POST    ${endpoint}    json=${invalid_body}    headers=${headers}    expected_status=422
    RETURN    ${resp}

# OWASP A05 - Security Misconfiguration Tests
Test Default Headers
    [Arguments]    ${endpoint}
    ${resp}=    GET    ${endpoint}
    Dictionary Should Contain Key    ${resp.headers}    X-Content-Type-Options
    Dictionary Should Contain Key    ${resp.headers}    X-Frame-Options
    Dictionary Should Contain Key    ${resp.headers}    Content-Security-Policy

# OWASP A06 - Vulnerable Components Tests
Check Dependency Version
    [Arguments]    ${package_name}    ${current_version}    ${known_vulnerable}
    Should Not Be Equal    ${current_version}    ${known_vulnerable}
    ...    Package ${package_name} ${current_version} has known vulnerabilities

# OWASP A07 - Authentication Failures Tests
Test Token Expiry
    [Arguments]    ${expired_token}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ...    Authorization=Bearer ${expired_token}
    ${resp}=    GET    /api/v1/sbom    headers=${headers}    expected_status=401
    RETURN    ${resp}

# OWASP A08 - Integrity Failures Tests
Test SBOM Signature
    [Arguments]    ${document_id}
    ${headers}=    Create Dictionary    X-API-Key=test-key
    ${resp}=    GET    /api/v1/sbom/${document_id}    headers=${headers}    expected_status=200
    ${body}=    Set Variable    ${resp.json()}
    RETURN    ${body.get('is_verified', False)}

# OWASP A09 - Logging Failures Tests
Test Audit Log Exists
    [Arguments]    ${approval_id}
    ${headers}=    Create Dictionary    X-API-Key=test-key
    ${resp}=    GET    /api/v1/approvals/requests/${approval_id}/audit    headers=${headers}    expected_status=200
    ${body}=    Set Variable    ${resp.json()}
    ${total}=    Get From Dictionary    ${body}    total
    Should Be True    ${total} >= 0

# OWASP A10 - SSRF Tests
Test SSRF Protection
    [Arguments]    ${endpoint}    ${ssrf_url}
    ${headers}=    Create Dictionary    Content-Type=application/json    X-API-Key=test-key
    ${body}=    Create Dictionary    url=${ssrf_url}
    ${resp}=    POST    ${endpoint}    json=${body}    headers=${headers}    expected_status=any
    Should Not Be Equal As Strings    ${resp.status_code}    500

# XSS Test
Test XSS Protection
    [Arguments]    ${endpoint}    ${xss_payload}
    ${headers}=    Create Dictionary    Content-Type=application/json    X-API-Key=test-key
    ${params}=    Create Dictionary    q=${xss_payload}
    ${resp}=    GET    ${endpoint}    params=${params}    headers=${headers}    expected_status=any
    Should Not Contain    ${resp.text}    <script>
    Should Not Contain    ${resp.text}    onerror=
    RETURN    ${resp}

# Rate Limit Test
Test Rate Limiting
    [Arguments]    ${endpoint}    ${max_requests}=100
    ${headers}=    Create Dictionary    Content-Type=application/json    X-API-Key=test-key
    FOR    ${i}    IN RANGE    ${max_requests}
        ${resp}=    GET    ${endpoint}    headers=${headers}    expected_status=any
    END
    ${resp}=    GET    ${endpoint}    headers=${headers}    expected_status=any
    RETURN    ${resp.status_code}
