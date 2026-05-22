*** Settings ***
Resource    ../../resources/common.robot
Resource    ../../resources/api_resources.robot
Suite Setup    Wait For API
Test Setup    Set Test Headers

*** Test Cases ***
Create SBOM Document Successfully
    ${doc}=    Create SBOM API    name=SBOM-CRUD-TEST    version=2.0.0    organization=ESA
    Assert JSON Contains    ${doc}    id
    Assert JSON Contains    ${doc}    name    SBOM-CRUD-TEST
    Assert JSON Contains    ${doc}    version    2.0.0
    Assert JSON Contains    ${doc}    organization    ESA
    Assert JSON Contains    ${doc}    spec_version    SPDX-2.3
    Set Suite Variable    ${CREATED_DOC_ID}    ${doc}[id]

Get SBOM Document By ID
    ${doc}=    Get SBOM API    ${CREATED_DOC_ID}
    Assert JSON Contains    ${doc}    id    ${CREATED_DOC_ID}
    Assert JSON Contains    ${doc}    name    SBOM-CRUD-TEST

List SBOM Documents
    ${list}=    List SBOMs API    page=1    per_page=10
    Assert Paginated Response    ${list}
    Should Be True    ${list}[total] >= 1

Create SBOM With Packages
    ${headers}=    Set Test Headers
    ${pkg}=    Create Dictionary
    ...    spdx_id=SPDXRef-LinuxKernel
    ...    name=linux-kernel
    ...    version=5.15.0
    ...    supplier=Organization: Linux Foundation
    ...    license_declared=GPL-2.0-only
    ${packages}=    Create List    ${pkg}
    ${body}=    Create Dictionary
    ...    name=SBOM-With-Packages
    ...    version=1.0.0
    ...    packages=${packages}
    ${resp}=    POST    /sbom    json=${body}    headers=${headers}    expected_status=201
    ${doc}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${doc}    name    SBOM-With-Packages
    ${pkg_list}=    Get From Dictionary    ${doc}    packages
    ${pkg_count}=    Get Length    ${pkg_list}
    Should Be Equal As Integers    ${pkg_count}    1

Delete SBOM Document
    ${headers}=    Set Test Headers
    DELETE    /sbom/${CREATED_DOC_ID}    headers=${headers}    expected_status=204

Verify SBOM Deletion Returns 404
    ${headers}=    Set Test Headers
    GET    /sbom/${CREATED_DOC_ID}    headers=${headers}    expected_status=404

Export SBOM As SPDX
    ${doc}=    Create SBOM API    name=SBOM-Export-Test    version=1.0.0
    ${headers}=    Set Test Headers
    ${resp}=    GET    /sbom/${doc}[id]/export    params=fmt=spdx    headers=${headers}    expected_status=200
    ${exported}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${exported}    spdxVersion    SPDX-2.3

Export SBOM As CycloneDX
    ${doc}=    Create SBOM API    name=SBOM-CDX-Test    version=1.0.0
    ${headers}=    Set Test Headers
    ${resp}=    GET    /sbom/${doc}[id]/export    params=fmt=cyclonedx    headers=${headers}    expected_status=200
    ${exported}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${exported}    bomFormat    CycloneDX

Validate SBOM Document
    ${doc}=    Create SBOM API    name=SBOM-Validate-Test    version=1.0.0
    ${headers}=    Set Test Headers
    ${body}=    Create Dictionary    document_id=${doc}[id]    checks=${EMPTY_LIST}
    ${resp}=    POST    /sbom/${doc}[id]/validate    json=${body}    headers=${headers}    expected_status=200
    ${validation}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${validation}    is_valid

Get SBOM Statistics
    ${headers}=    Set Test Headers
    ${resp}=    GET    /sbom/stats/summary    headers=${headers}    expected_status=200
    ${stats}=    Set Variable    ${resp.json()}
    Assert JSON Contains    ${stats}    total_documents
    Assert JSON Contains    ${stats}    total_packages
