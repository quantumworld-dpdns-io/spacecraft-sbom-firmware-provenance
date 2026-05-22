*** Settings ***
Library           RequestsLibrary
Library           Collections
Library           JSONLibrary
Library           String
Library           OperatingSystem
Library           FakerLibrary    locale=en_US

*** Variables ***
${BASE_URL}       http://localhost:8000
${API_PREFIX}     /api/v1
${API_KEY}        test-api-key-for-testing

*** Keywords ***
Create API Session
    [Arguments]    ${alias}=default
    Create Session    ${alias}    ${BASE_URL}${API_PREFIX}
    ...    headers=${api_headers}

Set Test Headers
    [Arguments]    ${token}=${NONE}
    ${headers}=    Create Dictionary    Content-Type=application/json    X-API-Key=${API_KEY}
    IF    ${token} != ${NONE}
        Set To Dictionary    ${headers}    Authorization=Bearer ${token}
    END
    RETURN    ${headers}

Generate Random String
    [Arguments]    ${length}=10
    ${result}=    Generate Random String    ${length}    [LETTERS][NUMBERS]
    RETURN    ${result}

Generate Random UUID
    ${uuid}=    Evaluate    str(__import__('uuid').uuid4())
    RETURN    ${uuid}

Health Check Should Pass
    ${headers}=    Set Test Headers
    GET    ${BASE_URL}/health    expected_status=200

Wait For API
    [Arguments]    ${retries}=10    ${delay}=1
    FOR    ${i}    IN RANGE    ${retries}
        ${passed}=    Run Keyword And Return Status
        ...    Health Check Should Pass
        IF    ${passed}    RETURN
        Sleep    ${delay}
    END
    Fail    API did not become ready after ${retries} retries

Assert JSON Contains
    [Arguments]    ${json}    ${key}    ${expected_value}=${NONE}
    Dictionary Should Contain Key    ${json}    ${key}
    IF    ${expected_value} != ${NONE}
        Dictionary Should Contain Item    ${json}    ${key}    ${expected_value}
    END

Assert Paginated Response
    [Arguments]    ${response}
    Assert JSON Contains    ${response}    items
    Assert JSON Contains    ${response}    total
    Assert JSON Contains    ${response}    page
    Assert JSON Contains    ${response}    per_page

Create Test SBOM Document
    [Arguments]    ${name}=Test SBOM    ${version}=1.0.0
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    name=${name}
    ...    version=${version}
    ...    organization=NASA
    ...    spec_version=SPDX-2.3
    ...    format_type=spdx
    POST    /sbom    json=${body}    headers=${headers}    expected_status=201

Create Test Firmware Image
    [Arguments]    ${name}=Test Firmware    ${version}=1.0.0    ${device}=OBC-750
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    name=${name}
    ...    version=${version}
    ...    device=${device}
    ...    manufacturer=SpaceX
    ...    hash_algorithm=sha256
    POST    /firmware    json=${body}    headers=${headers}    expected_status=201
