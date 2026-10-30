# BG-1: Representative container reference workload on ECS

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Statement**: The account owner and the sample-app maintainers (ST-1, ST-6) need a working, representative polyglot microservice store running on Amazon ECS with AWS managed backing services so that container and managed-service patterns on AWS can be demonstrated, learned and evaluated.
- **Primary stakeholder**: ST-1 — AWS account owner (see [stakeholders](../stakeholders.md))
- **SEI business-goal category**: managing change
- **Measure of success**: All five services RUNNING and HEALTHY behind the public endpoint; every backing-service type of the app exercised (DynamoDB, Aurora MySQL, Aurora PostgreSQL, ElastiCache, Amazon MQ, OpenSearch).
- **Priority**: high
- **Status**: open

## Context

The upstream README states the application exists to demonstrate container concepts on AWS and is deliberately over-engineered (decoupled services with different infrastructure dependencies). The deployment tags `created-by=retail-store-sample-app` confirm it is that project's Terraform ECS deployment.

## Supported by

- Use cases: [UC-1](../use-cases/UC-1.md), [UC-5](../use-cases/UC-5.md), [UC-6](../use-cases/UC-6.md)
- Quality attribute scenarios: [PQA-1](../quality-attributes/PQA-1.md), [DQA-1](../quality-attributes/DQA-1.md), [MQA-1](../quality-attributes/MQA-1.md), [INQA-1](../quality-attributes/INQA-1.md), [OQA-1](../quality-attributes/OQA-1.md)

## Notes

Source: upstream README (stated purpose). Whether *this* deployment is a demo, a training lab or a pre-production candidate is not recorded anywhere — ask ST-1.
