# Firmware Verification Skill

## Description
Verify spacecraft firmware image integrity and authenticity.

## Instructions
1. Register firmware image in system
2. Compute cryptographic hashes
3. Verify against stored values
4. Check digital signatures
5. Verify provenance chain

## Resources
- Firmware API: `/api/v1/firmware`
- Provenance API: `/api/v1/provenance`

## Workflow
1. Agent receives firmware binary
2. Computes SHA-256/SHA-512 hashes
3. Registers firmware via API
4. Verifies hashes match expectations
5. Traces provenance chain
6. Reports verification status
