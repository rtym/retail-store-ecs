# AC-2: Infrastructure-as-code source and state not available

- **Concern**: The Terraform configuration and state for this environment are not in this repository and their location is unknown.
- **Kind**: general (process)
- **Raised by**: ST-2 (architecture reconstruction)
- **Priority**: high
- **Status**: open

## Why it matters

Drift cannot be detected; the reconstruction cannot be compared to intent; remediation has no agreed change path.

## Related drivers

[CON-6](../constraints/CON-6.md), [DQA-1](../quality-attributes/DQA-1.md)
