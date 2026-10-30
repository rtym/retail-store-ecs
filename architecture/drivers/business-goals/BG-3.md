# BG-3: Cost proportionate to a non-production workload

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Statement**: The account owner (ST-1) needs the environment's running cost to stay proportionate to a demonstration / non-production workload so that the shared account's budget is not consumed by it.
- **Primary stakeholder**: ST-1 — AWS account owner (see [stakeholders](../stakeholders.md))
- **SEI business-goal category**: financial
- **Measure of success**: Monthly cost of resources tagged `environment-name=retail-store-ecs` within a budget ST-1 sets (not measurable today: the tag is not an activated cost-allocation tag).
- **Priority**: medium
- **Status**: open

## Context

Inferred from sizing choices: one task per service, burstable `db.t3.medium` / `cache.t3.micro`, single-instance broker and single-node search domain, one NAT Gateway.

## Supported by

- Use cases: [UC-6](../use-cases/UC-6.md)
- Quality attribute scenarios: [PQA-2](../quality-attributes/PQA-2.md), [SCQA-1](../quality-attributes/SCQA-1.md)

## Notes

Derived from sizing evidence — a hypothesis. Tension with BG-4: every redundancy fix adds cost.
