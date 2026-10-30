# CON-4: Backing services limited to supported providers

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: technical
- **Constraint**: Each service binds its persistence/messaging provider by environment variable, among the providers the application supports: carts → DynamoDB, catalog → MySQL (+ OpenSearch search), checkout → Redis, orders → PostgreSQL + RabbitMQ.
- **Source**: Environment variables `RETAIL_*_PROVIDER` in the task definitions.
- **Nature**: hard
- **Priority**: medium
- **Status**: open

## Rationale

Provider choice is a deployment-time binding the app exposes; anything else needs code changes (CON-3).

## Impact on the architecture

Rules out e.g. SQS/SNS for orders events or Aurora DSQL without upstream support.

## Conflicts

none

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md), [BG-2](../business-goals/BG-2.md)
