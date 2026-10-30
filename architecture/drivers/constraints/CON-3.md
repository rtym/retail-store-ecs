# CON-3: Upstream pre-built images, version 1.6.3

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: technical
- **Constraint**: Application code is not owned: images are `public.ecr.aws/aws-containers/retail-store-sample-{ui,catalog,cart,checkout,orders}:1.6.3`. Only infrastructure and configuration (environment variables, secrets) can be changed.
- **Source**: Task definitions `retail-store-ecs-*:1`.
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

The workload is a deployment of an open-source sample, not a product under development here.

## Impact on the architecture

Application-level tactics (retries, outbox, idempotency, TLS client settings) are fixed by upstream; architecture changes are limited to the platform.

## Conflicts

BG-4 (application-level hardening cannot be added locally).

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md)
