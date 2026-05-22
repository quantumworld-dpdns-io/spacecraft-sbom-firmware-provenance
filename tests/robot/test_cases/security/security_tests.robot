*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/security_keywords.robot
Suite Setup    Wait For API

*** Test Cases ***
XSS Protection In Search
    [Tags]    security    xss
    Test XSS Protection    ${API_PREFIX}/search    '<script>alert("xss")</script>'
    Test XSS Protection    ${API_PREFIX}/search    '<img src=x onerror=alert(1)>'
    Test XSS Protection    ${API_PREFIX}/search    'javascript:alert("xss")'

Rate Limiting Enforcement
    [Tags]    security    rate-limit
    ${status}=    Test Rate Limiting    ${API_PREFIX}/health
    Log    Rate limit status code: ${status}

Security Headers Check
    [Tags]    security    headers
    ${resp}=    GET    ${BASE_URL}/health
    ${headers}=    Set Variable    ${resp.headers}
    Dictionary Should Contain Key    ${headers}    X-Content-Type-Options
    Dictionary Should Contain Key    ${headers}    X-Frame-Options
    Dictionary Should Contain Key    ${headers}    Content-Security-Policy
    Dictionary Should Contain Key    ${headers}    Strict-Transport-Security
    Dictionary Should Contain Key    ${headers}    Referrer-Policy
    ${csp}=    Get From Dictionary    ${headers}    Content-Security-Policy
    Should Contain    ${csp}    default-src

API Key Authentication
    [Tags]    security    auth
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${resp}=    GET    ${API_PREFIX}/sbom    headers=${headers}    expected_status=401
    Should Be Equal As Numbers    ${resp.status_code}    401

CORS Headers Check
    [Tags]    security    cors
    ${headers}=    Create Dictionary    Origin=http://malicious-site.com
    ${resp}=    GET    ${BASE_URL}/health    headers=${headers}
    ${cors}=    Get From Dictionary    ${resp.headers}    Access-Control-Allow-Origin    default=NONE
    Log    CORS header: ${cors}

Content Type Verification
    [Tags]    security    content-type
    ${headers}=    Create Dictionary    Content-Type=text/plain    X-API-Key=test-key
    ${body}=    Create Dictionary    name=Test    version=1.0.0
    ${resp}=    POST    ${API_PREFIX}/sbom    json=${body}    headers=${headers}    expected_status=201
    Should Be Equal As Numbers    ${resp.status_code}    201

Input Sanitization
    [Tags]    security    sanitization
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    name=<script>malicious</script>
    ...    version=1.0.0
    ${resp}=    POST    /sbom    json=${body}    headers=${headers}    expected_status=201
    ${doc}=    Set Variable    ${resp.json()}
    Should Not Contain    ${doc}[name]    <script>
