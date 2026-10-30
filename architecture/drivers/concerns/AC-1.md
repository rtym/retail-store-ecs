# AC-1: Shared-account co-tenancy

- **Concern**: The workload shares AWS account 111122223333 with unrelated workloads, so blast radius, IAM, quotas and cost attribution are shared.
- **Kind**: general (technology / organisation)
- **Raised by**: ST-2 (architecture reconstruction)
- **Priority**: high
- **Status**: open

## Why it matters

A compromise or quota exhaustion in any co-tenant affects this workload and vice versa; cost of this workload cannot be isolated (BG-3).

## Related drivers

[BG-3](../business-goals/BG-3.md), [BG-4](../business-goals/BG-4.md), [CON-1](../constraints/CON-1.md), [SQA-3](../quality-attributes/SQA-3.md)
