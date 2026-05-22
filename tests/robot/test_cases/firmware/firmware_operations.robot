*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/api_resources.robot
Suite Setup    Wait For API

*** Test Cases ***
Register Firmware Image Successfully
    ${fw}=    Register Firmware API    name=Firmware-Test-1    version=2.1.0    device=ADCS-300
    Assert JSON Contains    ${fw}    id
    Assert JSON Contains    ${fw}    name    Firmware-Test-1
    Assert JSON Contains    ${fw}    version    2.1.0
    Assert JSON Contains    ${fw}    device    ADCS-300
    Assert JSON Contains    ${fw}    hash_algorithm    sha256
    Set Suite Variable    ${CREATED_FW_ID}    ${fw}[id]

Get Firmware Image By ID
    ${fw}=    Get Firmware API    ${CREATED_FW_ID}
    Assert JSON Contains    ${fw}    id    ${CREATED_FW_ID}
    Assert JSON Contains    ${fw}    name    Firmware-Test-1
    Assert JSON Contains    ${fw}    status    pending

Verify Firmware Image
    ${result}=    Verify Firmware API    ${CREATED_FW_ID}
    Assert JSON Contains    ${result}    firmware_id    ${CREATED_FW_ID}
    Assert JSON Contains    ${result}    hash_verified

List Firmware Images
    ${headers}=    Set Test Headers
    ${params}=    Create Dictionary    page=1    per_page=10
    ${resp}=    GET    /firmware    params=${params}    headers=${headers}    expected_status=200
    ${list}=    Set Variable    ${resp.json()}
    Assert Paginated Response    ${list}
    Should Be True    ${list}[total] >= 1

Register Firmware With Multiple Hashes
    ${headers}=    Set Test Headers
    ${hash1}=    Create Dictionary    algorithm=sha256    hash_value=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890    is_primary=True
    ${hash2}=    Create Dictionary    algorithm=sha512    hash_value=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890     is_primary=False
    ${hashes}=    Create List    ${hash1}    ${hash2}
    ${body}=    Create Dictionary
    ...    name=Multi-Hash-FW
    ...    version=1.0.0
    ...    device=EPS-200
    ...    hashes=${hashes}
    ${resp}=    POST    /firmware    json=${body}    headers=${headers}    expected_status=201
    ${fw}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${fw}    name    Multi-Hash-FW
    ${fw_hashes}=    Get From Dictionary    ${fw}    hashes
    ${hash_count}=    Get Length    ${fw_hashes}
    Should Be Equal As Integers    ${hash_count}    2

Verify Firmware Hash
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    firmware_id=${CREATED_FW_ID}
    ...    expected_hash=${EMPTY}
    ...    algorithm=sha256
    ${resp}=    POST    /firmware/hash/verify    json=${body}    headers=${headers}    expected_status=200
    ${result}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${result}    firmware_id    ${CREATED_FW_ID}
    Assert JSON Contains    ${result}    match

Get Firmware Statistics
    ${headers}=    Set Test Headers
    ${resp}=    GET    /firmware/stats/summary    headers=${headers}    expected_status=200
    ${stats}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${stats}    total_images
    Assert JSON Contains    ${stats}    signed_images
