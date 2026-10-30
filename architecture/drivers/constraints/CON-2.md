# CON-2: Amazon ECS on AWS Fargate

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: technical
- **Constraint**: All five services run as ECS services with launch type FARGATE, `awsvpc` networking, platform version 1.4.0, in cluster `retail-store-ecs-cluster`.
- **Source**: ECS evidence (`aws/scoped/retail-store-ecs-evidence.json`); upstream Terraform ECS deployment option.
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

The deployment is the ECS variant of the sample app; the purpose (BG-1) is to show containers on ECS.

## Impact on the architecture

No host management; scaling and placement are per-task; networking is per-task ENI and security group.

## Conflicts

none

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md)
