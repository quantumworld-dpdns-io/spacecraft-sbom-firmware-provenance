# SBOM Analysis Skill

## Description
Analyze Software Bill of Materials documents for spacecraft firmware.

## Instructions
1. Retrieve SBOM document from API
2. Validate SPDX/CycloneDX format
3. Check for known vulnerabilities
4. Generate analysis report

## Resources
- SBOM API: `/api/v1/sbom/{id}`
- Vulnerability API: `/api/v1/security/vulnerabilities`

## Workflow
1. User provides SBOM document ID
2. Agent fetches document via API
3. Agent validates structure and checksums
4. Agent queries vulnerability database
5. Agent generates comprehensive report
