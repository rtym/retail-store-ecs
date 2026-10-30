# BG-4: Safe to expose and recoverable

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Statement**: The account owner and the security function (ST-1, ST-4) need the environment to protect shopper data, detect misuse and recover from failure so that it can stay exposed on the public internet inside a shared account — and, if ST-1 decides so, be promoted beyond demonstration use — without unacceptable risk.
- **Primary stakeholder**: ST-4 — Security and compliance (see [stakeholders](../stakeholders.md))
- **SEI business-goal category**: responsibility to society & law
- **Measure of success**: Zero plaintext external endpoints; all control-plane activity recorded; documented RPO/RTO met in a restore test.
- **Priority**: high
- **Status**: at risk

## Context

The environment is internet-facing (`retail-store-ecs-ui` Application Load Balancer, HTTP 80 from 0.0.0.0/0) and shares account 111122223333 with unrelated workloads. Orders carry shopper PII (name, address, e-mail).

## Supported by

- Use cases: [UC-4](../use-cases/UC-4.md), [UC-6](../use-cases/UC-6.md), [UC-7](../use-cases/UC-7.md)
- Quality attribute scenarios: [AQA-1](../quality-attributes/AQA-1.md), [AQA-2](../quality-attributes/AQA-2.md), [RQA-1](../quality-attributes/RQA-1.md), [SQA-1](../quality-attributes/SQA-1.md), [SQA-2](../quality-attributes/SQA-2.md), [SQA-3](../quality-attributes/SQA-3.md), [OQA-1](../quality-attributes/OQA-1.md), [DQA-1](../quality-attributes/DQA-1.md)

## Notes

**Open decision for ST-1**: is this environment demo-only (CON-5) or a production candidate? The answer changes the priority of most risks found by the ATAM.
