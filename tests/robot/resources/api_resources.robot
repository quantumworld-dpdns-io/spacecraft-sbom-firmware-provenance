*** Settings ***
Resource    common.robot

*** Keywords ***
# SBOM API Keywords
Create SBOM API
    [Arguments]    ${name}=SBOM-DOC-${GENERATED_ID}    ${version}=1.0.0
    ...    ${organization}=TestOrg    ${spec_version}=SPDX-2.3
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary
    ...    name=${name}
    ...    version=${version}
    ...    organization=${organization}
    ...    spec_version=${spec_version}
    ${resp}=    POST    /sbom    json=${body}    headers=${headers}    expected_status=201
    RETURN    ${resp.json()}

Get SBOM API
    [Arguments]    ${document_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${resp}=    GET    /sbom/${document_id}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

List SBOMs API
    [Arguments]    ${page}=1    ${per_page}=20
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${params}=    Create Dictionary    page=${page}    per_page=${per_page}
    ${resp}=    GET    /sbom    params=${params}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

Delete SBOM API
    [Arguments]    ${document_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    DELETE    /sbom/${document_id}    headers=${headers}    expected_status=204

Validate SBOM API
    [Arguments]    ${document_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary    document_id=${document_id}    checks=${EMPTY_LIST}
    ${resp}=    POST    /sbom/${document_id}/validate    json=${body}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

# Firmware API Keywords
Register Firmware API
    [Arguments]    ${name}=FW-${GENERATED_ID}    ${version}=1.0.0    ${device}=OBC-750
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary
    ...    name=${name}
    ...    version=${version}
    ...    device=${device}
    ${resp}=    POST    /firmware    json=${body}    headers=${headers}    expected_status=201
    RETURN    ${resp.json()}

Get Firmware API
    [Arguments]    ${firmware_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${resp}=    GET    /firmware/${firmware_id}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

Verify Firmware API
    [Arguments]    ${firmware_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${resp}=    POST    /firmware/${firmware_id}/verify    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

# Provenance API Keywords
Create Provenance Chain API
    [Arguments]    ${target_type}=firmware    ${target_id}=${NONE}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary
    ...    name=Test Chain
    ...    target_type=${target_type}
    ...    target_id=${target_id}
    ${resp}=    POST    /provenance/chains    json=${body}    headers=${headers}    expected_status=201
    RETURN    ${resp.json()}

Trace Provenance API
    [Arguments]    ${target_type}    ${target_id}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${resp}=    GET    /provenance/trace/${target_type}/${target_id}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

# Approval API Keywords
Create Approval Request API
    [Arguments]    ${target_id}    ${target_type}=firmware
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary
    ...    request_type=deployment
    ...    target_id=${target_id}
    ...    target_type=${target_type}
    ...    title=Test Approval
    ...    priority=high
    ${resp}=    POST    /approvals/requests    json=${body}    headers=${headers}    expected_status=201
    RETURN    ${resp.json()}

Review Approval API
    [Arguments]    ${request_id}    ${action}=approve
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${body}=    Create Dictionary    action=${action}
    ${resp}=    POST    /approvals/requests/${request_id}/review    json=${body}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}

# Search API Keywords
Global Search API
    [Arguments]    ${query}
    ${headers}=    Set Test Headers    ${ACCESS_TOKEN}
    ${params}=    Create Dictionary    q=${query}
    ${resp}=    GET    /search    params=${params}    headers=${headers}    expected_status=200
    RETURN    ${resp.json()}
