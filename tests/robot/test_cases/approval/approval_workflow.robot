*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/api_resources.robot
Suite Setup    Wait For API

*** Test Cases ***
Create Approval Request
    ${fw}=    Register Firmware API    name=Approval-FW    version=1.0.0    device=OBC-750
    ${req}=    Create Approval Request API    target_id=${fw}[id]    target_type=firmware
    Assert JSON Contains    ${req}    id
    Assert JSON Contains    ${req}    status    pending
    Assert JSON Contains    ${req}    request_type    deployment
    Set Suite Variable    ${CREATED_REQ_ID}    ${req}[id]
    Set Suite Variable    ${FW_ID}    ${fw}[id]

Get Approval Request By ID
    ${headers}=    Set Test Headers
    ${resp}=    GET    /approvals/requests/${CREATED_REQ_ID}    headers=${headers}    expected_status=200
    ${req}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${req}    id    ${CREATED_REQ_ID}
    Assert JSON Contains    ${req}    status    pending

List Approval Requests
    ${headers}=    Set Test Headers
    ${params}=    Create Dictionary    page=1    per_page=10    status=pending
    ${resp}=    GET    /approvals/requests    params=${params}    headers=${headers}    expected_status=200
    ${list}=    Set Variable    ${resp.json()}
    Assert Paginated Response    ${list}

Approve Request
    ${result}=    Review Approval API    ${CREATED_REQ_ID}    approve
    Assert JSON Contains    ${result}    status    approved
    Assert JSON Contains    ${result}    approved_by

Get Approval Audit Log
    ${headers}=    Set Test Headers
    ${resp}=    GET    /approvals/requests/${CREATED_REQ_ID}/audit    headers=${headers}    expected_status=200
    ${log}=    Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${log}    items
    Dictionary Should Contain Key    ${log}    total
    Should Be True    ${log}[total] >= 1

Reject Approval Request
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary
    ...    request_type=deployment
    ...    target_id=${FW_ID}
    ...    target_type=firmware
    ...    title=Rejection Test
    ${resp}=    POST    /approvals/requests    json=${body}    headers=${headers}    expected_status=201
    ${req}=    Set Variable    ${resp.json()}
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary    action=reject    comment=Security review failed
    ${resp}=    POST    /approvals/requests/${req}[id]/review    json=${body}    headers=${headers}    expected_status=200
    ${result}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${result}    status    rejected
    Assert JSON Contains    ${result}    rejection_reason    Security review failed

Create Approval Policy
    ${headers}=    Set Test Headers
    ${rules}=    Create Dictionary    min_approvers=2    require_security_review=True
    ${body}=    Create Dictionary
    ...    name=Critical-Deployment-Policy
    ...    policy_type=deployment
    ...    target_type=firmware
    ...    rules=${rules}
    ...    required_approvers=2
    ${resp}=    POST    /approvals/policies    json=${body}    headers=${headers}    expected_status=201
    ${policy}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${policy}    name    Critical-Deployment-Policy
    Assert JSON Contains    ${policy}    required_approvers    2

List Approval Policies
    ${headers}=    Set Test Headers
    ${resp}=    GET    /approvals/policies    headers=${headers}    expected_status=200
    ${policies}=    Set Variable    ${resp.json()}
    ${count}=    Get Length    ${policies}
    Should Be True    ${count} >= 1
