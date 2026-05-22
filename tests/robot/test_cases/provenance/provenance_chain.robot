*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/api_resources.robot
Suite Setup    Wait For API

*** Test Cases ***
Create Provenance Chain Successfully
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    name=Provenance-Test-Chain
    ...    target_type=firmware
    ...    target_id=test-fw-001
    ...    description=Test provenance chain
    ${resp}=    POST    /provenance/chains    json=${body}    headers=${headers}    expected_status=201
    ${chain}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${chain}    id
    Assert JSON Contains    ${chain}    name    Provenance-Test-Chain
    Assert JSON Contains    ${chain}    target_type    firmware
    Set Suite Variable    ${CREATED_CHAIN_ID}    ${chain}[id]

Get Provenance Chain By ID
    ${headers}=    Set Test Headers
    ${resp}=    GET    /provenance/chains/${CREATED_CHAIN_ID}    headers=${headers}    expected_status=200
    ${chain}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${chain}    id    ${CREATED_CHAIN_ID}
    Assert JSON Contains    ${chain}    name    Provenance-Test-Chain

List Provenance Chains
    ${headers}=    Set Test Headers
    ${params}=    Create Dictionary    page=1    per_page=10
    ${resp}=    GET    /provenance/chains    params=${params}    headers=${headers}    expected_status=200
    ${list}=    Set Variable    ${resp.json()}
    Assert Paginated Response    ${list}
    Should Be True    ${list}[total] >= 1

Create Chain With Provenance Nodes
    ${headers}=    Set Test Headers
    ${node}=    Create Dictionary
    ...    node_type=build
    ...    entity_name=Build Server
    ...    entity_type=system
    ...    entity_id=build-srv-001
    ...    action=compiled
    ...    signer=admin@spacecraft
    ${nodes}=    Create List    ${node}
    ${body}=    Create Dictionary
    ...    name=Chain-With-Nodes
    ...    target_type=firmware
    ...    target_id=test-fw-002
    ...    nodes=${nodes}
    ${resp}=    POST    /provenance/chains    json=${body}    headers=${headers}    expected_status=201
    ${chain}=    Set Variable    ${resp.json()}
    ${node_list}=    Get From Dictionary    ${chain}    nodes
    ${node_count}=    Get Length    ${node_list}
    Should Be Equal As Integers    ${node_count}    1

Trace Provenance For Target
    ${fw}=    Register Firmware API    name=Trace-Test-FW    version=1.0.0    device=OBC-750
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    name=Trace-Chain
    ...    target_type=firmware
    ...    target_id=${fw}[id]
    ${resp}=    POST    /provenance/chains    json=${body}    headers=${headers}    expected_status=201
    ${headers}=    Set Test Headers
    ${resp}=    GET    /provenance/trace/firmware/${fw}[id]    headers=${headers}    expected_status=200
    ${trace}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${trace}    chain_id
    Assert JSON Contains    ${trace}    target_id    ${fw}[id]
    Assert JSON Contains    ${trace}    target_type    firmware

Verify Provenance Chain
    ${headers}=    Set Test Headers
    ${resp}=    POST    /provenance/chains/${CREATED_CHAIN_ID}/verify    headers=${headers}    expected_status=200
    ${result}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${result}    verified
    Assert JSON Contains    ${result}    complete
