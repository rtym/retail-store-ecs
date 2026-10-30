# Rationale — retail-store-ecs

- **Date**: 2026-10-09

No ADD session or ADR exists for this deployment; the decisions below are **recovered** from the
as-built system. Their rationale is *derived — confirm*: it states the most plausible reason given the
evidence and the upstream project, not a recorded intent. No new decisions were taken during the
reconstruction; proposed changes are recommendations in the [ATAM report](../atam/atam-report.md).

## Recovered decisions

| # | Decision (and where it shows) | Rationale, assumptions, alternatives (derived — confirm) | Drivers |
|---|-------------------------------|-----------------------------------------------------------|---------|
| RD-1 | Five microservices, one per business capability, each with its own store ([module view](view-module-decomposition.md)) | Upstream design, deliberately "over-engineered" to show containers with varied dependencies. Alternative: a modular monolith — cheaper and more available, but defeats the demonstration purpose. | BG-1, CON-3, MQA-1 |
| RD-2 | Amazon ECS on Fargate, `awsvpc`, no EC2 capacity ([deployment view](view-allocation-deployment.md)) | No hosts to manage; the ECS variant of the upstream deployment options (EKS and App Runner are the alternatives). | CON-2, BG-1 |
| RD-3 | Service-to-service discovery with ECS Service Connect in `retailstore.local` ([C&C view](view-cnc-runtime.md)) | Gives names, client-side load balancing and per-call metrics without internal load balancers. Alternatives: Cloud Map DNS only (no proxy), internal ALB per service (cost). TLS not enabled — simpler, but plaintext. | UC-1–UC-5, SQA-1 |
| RD-4 | One managed store per service: DynamoDB, Aurora MySQL + OpenSearch, ElastiCache Redis, Aurora PostgreSQL + Amazon MQ | Each service exercises a different AWS managed service through the provider it supports. | BG-1, CON-4, MQA-1 |
| RD-5 | Asynchronous order events over RabbitMQ | Decouples future consumers from `orders`. Alternative (SQS/SNS) not supported by the image. | INQA-1, UC-5, CON-4 |
| RD-6 | Single instance of everything: 1 task per service, single-AZ data stores, 1 NAT Gateway, burstable classes | Keeps the cost of a demonstration low. **Assumption**: availability is not required. Conflicts with AQA-1, AQA-2, RQA-1. | BG-3, AQA-1, AQA-2 |
| RD-7 | Public HTTP:80 listener only, no domain or certificate | Works with the generated load balancer DNS name; no certificate management. **Assumption**: no real shopper data. Conflicts with SQA-1. | BG-1, SQA-1, CON-5 |
| RD-8 | Credentials in Secrets Manager, scoped per execution role; per-store security groups | Least privilege for the data zone, done well. | SQA-2, BG-4 |
| RD-9 | Rolling deployments 100/200, circuit breaker off, ECS Exec on | ECS defaults plus debugging access. Alternatives: circuit breaker with rollback; blue/green. | DQA-1, UC-6, UC-7 |
| RD-10 | Observability = Container Insights (enhanced) + one log group; no alarms | Enough to explore a demo; not enough to operate it. | OQA-1, UC-7 |

## Cross-cutting observations

- The **network is multi-AZ, the workload is not** (RD-6): the cheapest path to better availability is
  configuration, not redesign.
- The **data zone is tighter than the application zone** (RD-8 vs. the open task security groups): an
  inconsistency, not a deliberate trade-off.
- Every decision is constrained by the images being upstream ([CON-3](../drivers/constraints/CON-3.md)):
  application-level tactics (retries, outbox, idempotency) cannot be changed here.

## ADR log

None recorded. Decisions taken in a future `/add` iteration (for the ATAM risk themes) should be
recorded as ADRs under `architecture/add/adr/` and linked from here.

---

**Navigation**: [docs roadmap](README.md) · [architecture package](../README.md)
