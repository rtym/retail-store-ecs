# CON-6: Infrastructure defined as Terraform

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: technical
- **Constraint**: The infrastructure was created by Terraform (the upstream ECS Terraform configuration); changes should be made there, not in the console.
- **Source**: Derived: timestamp-suffixed names (e.g. `retail-store-ecs-orders-2026100914501960110000001c`) and tags match the upstream Terraform; no CloudFormation stack owns the resources. Terraform source/state location unknown (AC-2).
- **Nature**: negotiable
- **Priority**: medium
- **Status**: open

## Rationale

Keeps the environment reproducible and avoids drift.

## Impact on the architecture

All remediation from the ATAM should land as Terraform changes.

## Conflicts

none

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md), [BG-3](../business-goals/BG-3.md)
