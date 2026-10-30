# Architectural Drivers — `drivers/README.md`: retail-store-ecs

- **Date**: 2026-10-09
- **Owner**: workload owner (ST-1) — to confirm; drafted by ST-2
- **Status**: draft
- **QA model**: ISO/IEC 25010:2023
- **Design purpose**: brownfield — as-built architecture recovery of an existing deployment (input to an assessment; possible later brownfield extension)
- **Stakeholders**: [stakeholders.md](stakeholders.md)

> **How this register was built.** No requirements documents exist for this deployment and no
> stakeholder has been interviewed. Every driver below was **derived from the deployed AWS
> environment** (read-only evidence in [`../../aws/`](../../aws/README.md)) and from the upstream
> project README, following the SEI brownfield-intake procedure ([intake note](../brownfield-intake.md)).
> All of them are **derived — confirm**. Response measures are proposed targets, not recovered facts.

## Driver inventory

### Business goals — [`business-goals/`](business-goals/README.md)
| ID | Goal (short) | File |
|----|--------------|------|
| BG-1 | The account owner and the sample-app maintainers (ST-1, ST-6) need a working, representative polyglot microservice store running on Amazon ECS with AWS managed backing services so that container and managed-service patterns on AWS can be demonstrated, learned and evaluated. | [BG-1](business-goals/BG-1.md) |
| BG-2 | Shoppers (ST-5) need to browse, search, fill a cart and check out so that every completed checkout produces a stored order — the storefront's functional purpose. | [BG-2](business-goals/BG-2.md) |
| BG-3 | The account owner (ST-1) needs the environment's running cost to stay proportionate to a demonstration / non-production workload so that the shared account's budget is not consumed by it. | [BG-3](business-goals/BG-3.md) |
| BG-4 | The account owner and the security function (ST-1, ST-4) need the environment to protect shopper data, detect misuse and recover from failure so that it can stay exposed on the public internet inside a shared account — and, if ST-1 decides so, be promoted beyond demonstration use — without unacceptable risk. | [BG-4](business-goals/BG-4.md) |

### Use cases — [`use-cases/`](use-cases/README.md)  (primary functional requirements)
| ID | Use case | Primary actor | Diagram | File |
|----|----------|---------------|---------|------|
| UC-1 | Browse product catalogue | Shopper | [UC-1](use-cases/diagrams/UC-1.png) | [UC-1](use-cases/UC-1.md) |
| UC-2 | Search products | Shopper | [UC-2](use-cases/diagrams/UC-2.png) | [UC-2](use-cases/UC-2.md) |
| UC-3 | Manage shopping cart | Shopper | [UC-3](use-cases/diagrams/UC-3.png) | [UC-3](use-cases/UC-3.md) |
| UC-4 | Check out | Shopper | [UC-4](use-cases/diagrams/UC-4.png) | [UC-4](use-cases/UC-4.md) |
| UC-5 | Place order | Shopper | [UC-5](use-cases/diagrams/UC-5.png) | [UC-5](use-cases/UC-5.md) |
| UC-6 | Deploy a new service version | Operator | [UC-6](use-cases/diagrams/UC-6.png) | [UC-6](use-cases/UC-6.md) |
| UC-7 | Diagnose a running service | Operator | [UC-7](use-cases/diagrams/UC-7.png) | [UC-7](use-cases/UC-7.md) |

Overview use case diagrams: [`use-cases/diagrams/overview-shopper.png`](use-cases/diagrams/overview-shopper.png) · [`use-cases/diagrams/overview-operator.png`](use-cases/diagrams/overview-operator.png)

### Constraints — [`constraints/`](constraints/README.md)
| ID | Type | Constraint (short) | Hard / negotiable | File |
|----|------|--------------------|-------------------|------|
| CON-1 | technical | AWS eu-central-1 in a shared account | negotiable | [CON-1](constraints/CON-1.md) |
| CON-2 | technical | Amazon ECS on AWS Fargate | hard | [CON-2](constraints/CON-2.md) |
| CON-3 | technical | Upstream pre-built images, version 1.6.3 | hard | [CON-3](constraints/CON-3.md) |
| CON-4 | technical | Backing services limited to supported providers | hard | [CON-4](constraints/CON-4.md) |
| CON-5 | business | Upstream: educational use, not production | hard | [CON-5](constraints/CON-5.md) |
| CON-6 | technical | Infrastructure defined as Terraform | negotiable | [CON-6](constraints/CON-6.md) |

### Architectural concerns — [`concerns/`](concerns/README.md)  (ADD input; not traced to a BG)
| ID | Concern (short) | Kind | Priority | File |
|----|-----------------|------|:--------:|------|
| AC-1 | Shared-account co-tenancy | general (technology / organisation) | high | [AC-1](concerns/AC-1.md) |
| AC-2 | Infrastructure-as-code source and state not available | general (process) | high | [AC-2](concerns/AC-2.md) |
| AC-3 | Missing account security baseline | general (technology mandate) | high | [AC-3](concerns/AC-3.md) |
| AC-4 | Version currency of managed engines and images | quality of the design | medium | [AC-4](concerns/AC-4.md) |
| AC-5 | No defined operations model | general (process) | high | [AC-5](concerns/AC-5.md) |

### Quality attribute scenarios — [`quality-attributes/`](quality-attributes/README.md)
| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Diagram | File |
|----|-------------------------------|-------------------|:------:|---------|------|
| AQA-1 | Reliability / availability | Single task failure of the storefront — 0 failed shopper requests and < 1 % 5xx over the 5 min after a single-task failure | (H, M) | [scenario](quality-attributes/diagrams/scenario-AQA-1.png) | [AQA-1](quality-attributes/AQA-1.md) |
| AQA-2 | Reliability / availability / fault tolerance | Loss of Availability Zone eu-central-1a — browse + cart restored within 5 min; 0 committed orders lost | (H, H) | [scenario](quality-attributes/diagrams/scenario-AQA-2.png) | [AQA-2](quality-attributes/AQA-2.md) |
| RQA-1 | Reliability / recoverability | Restore after data corruption or deletion — orders RPO ≤ 5 min and RTO ≤ 4 h; carts RPO ≤ 24 h | (H, M) | [scenario](quality-attributes/diagrams/scenario-RQA-1.png) | [RQA-1](quality-attributes/RQA-1.md) |
| PQA-1 | Performance efficiency / time behaviour | Catalogue page responsiveness — Application Load Balancer TargetResponseTime p95 ≤ 1 s, 0 % 5xx | (M, M) | [scenario](quality-attributes/diagrams/scenario-PQA-1.png) | [PQA-1](quality-attributes/PQA-1.md) |
| PQA-2 | Performance efficiency / resource utilisation | Provisioned capacity is used — average CPU utilisation ≥ 40 % on tasks and data nodes, or a documented reason why not | (M, L) | [scenario](quality-attributes/diagrams/scenario-PQA-2.png) | [PQA-2](quality-attributes/PQA-2.md) |
| SCQA-1 | Flexibility / scalability | Demand spike — capacity added within 5 min, < 1 % 5xx during the spike; back to baseline within 30 min after it | (M, H) | [scenario](quality-attributes/diagrams/scenario-SCQA-1.png) | [SCQA-1](quality-attributes/SCQA-1.md) |
| SQA-1 | Security / confidentiality | Shopper traffic confidentiality in transit — 100 % of external requests on TLS 1.2+; 0 plaintext listeners; 0 plaintext connections to stores holding PII | (H, L) | [scenario](quality-attributes/diagrams/scenario-SQA-1.png) | [SQA-1](quality-attributes/SQA-1.md) |
| SQA-2 | Security / integrity | Containment of a compromised service — 0 network paths outside the intended graph (verified by VPC Reachability Analyzer); 0 secrets readable by a non-owning task role | (H, M) | [scenario](quality-attributes/diagrams/scenario-SQA-2.png) | [SQA-2](quality-attributes/SQA-2.md) |
| SQA-3 | Security / accountability | Detection of suspicious control-plane activity — 100 % of API calls recorded; alert within 15 min | (H, L) | [scenario](quality-attributes/diagrams/scenario-SQA-3.png) | [SQA-3](quality-attributes/SQA-3.md) |
| OQA-1 | Observability (cross-cutting) / monitorability | Operators learn of failures before shoppers — notification within 5 min; 100 % of services covered by an alarm | (H, L) | [scenario](quality-attributes/diagrams/scenario-OQA-1.png) | [OQA-1](quality-attributes/OQA-1.md) |
| DQA-1 | Flexibility / installability (deployability) | Safe rollout of a bad version — 0 shopper-visible errors; automatic rollback within 10 min | (M, L) | [scenario](quality-attributes/diagrams/scenario-DQA-1.png) | [DQA-1](quality-attributes/DQA-1.md) |
| MQA-1 | Maintainability / modifiability | Swap a backing-service provider — 0 lines of application code; ≤ 1 task-definition revision; done within 1 person-day | (M, L) | [scenario](quality-attributes/diagrams/scenario-MQA-1.png) | [MQA-1](quality-attributes/MQA-1.md) |
| INQA-1 | Integrability (cross-cutting) / integrability | Add a consumer of order events — 0 changes to the orders service; consumer receiving events within 2 days of effort | (M, L) | [scenario](quality-attributes/diagrams/scenario-INQA-1.png) | [INQA-1](quality-attributes/INQA-1.md) |

**Utility tree** (summary of the quality attributes in these drivers, **as a table**):
[`quality-attributes/utility-tree.md`](quality-attributes/utility-tree.md) — one leaf per row, `★` on each `(H, H)` leaf.

**QA ID legend** (attribute → prefix): AQA availability · RQA reliability(other) · PQA performance
· SQA security · SCQA scalability · DQA deployability · MQA modifiability · OQA observability ·
INQA integrability. Never `QAS-`.

## Traceability matrix

| Driver | File | Supports BG | Realised / constrained by | Addressed in | Status |
|--------|------|-------------|---------------------------|--------------|--------|
| UC-1 | [UC-1](use-cases/UC-1.md) | BG-1, BG-2 | PQA-1, AQA-1, CON-2 | as-built: docs/view-cnc-runtime.md | open |
| UC-2 | [UC-2](use-cases/UC-2.md) | BG-2 | PQA-1, AQA-2, MQA-1 | as-built: docs/view-cnc-runtime.md | open |
| UC-3 | [UC-3](use-cases/UC-3.md) | BG-2 | AQA-2, SCQA-1 | as-built: docs/view-cnc-runtime.md | open |
| UC-4 | [UC-4](use-cases/UC-4.md) | BG-2, BG-4 | AQA-1, SQA-1, SQA-2 | as-built: docs/view-cnc-runtime.md | open |
| UC-5 | [UC-5](use-cases/UC-5.md) | BG-1, BG-2, BG-4 | INQA-1, RQA-1, AQA-2 | as-built: docs/view-cnc-runtime.md | open |
| UC-6 | [UC-6](use-cases/UC-6.md) | BG-1, BG-3, BG-4 | DQA-1, CON-3, CON-6 | as-built: docs/view-cnc-runtime.md | open |
| UC-7 | [UC-7](use-cases/UC-7.md) | BG-4 | OQA-1, SQA-3 | as-built: docs/view-cnc-runtime.md | open |
| AQA-1 | [AQA-1](quality-attributes/AQA-1.md) | BG-2, BG-4 | — | ATAM R-1 (RT-1) | at risk |
| AQA-2 | [AQA-2](quality-attributes/AQA-2.md) | BG-2, BG-4 | — | ATAM R-2, R-3 (RT-1) | at risk |
| RQA-1 | [RQA-1](quality-attributes/RQA-1.md) | BG-4 | — | ATAM R-4 (RT-4) | at risk |
| PQA-1 | [PQA-1](quality-attributes/PQA-1.md) | BG-1, BG-2 | — | not analysed — no load data | open |
| PQA-2 | [PQA-2](quality-attributes/PQA-2.md) | BG-3 | — | not analysed — no utilisation data | open |
| SCQA-1 | [SCQA-1](quality-attributes/SCQA-1.md) | BG-2, BG-3 | — | ATAM R-12 (RT-1) | at risk |
| SQA-1 | [SQA-1](quality-attributes/SQA-1.md) | BG-4 | — | ATAM R-5, R-6 (RT-2) | at risk |
| SQA-2 | [SQA-2](quality-attributes/SQA-2.md) | BG-4 | — | ATAM R-6–R-9 (RT-2) | at risk |
| SQA-3 | [SQA-3](quality-attributes/SQA-3.md) | BG-4 | — | ATAM R-9, R-10 (RT-3) | at risk |
| OQA-1 | [OQA-1](quality-attributes/OQA-1.md) | BG-1, BG-4 | — | ATAM R-11 (RT-3) | at risk |
| DQA-1 | [DQA-1](quality-attributes/DQA-1.md) | BG-1, BG-4 | — | ATAM R-13, N-5 (RT-3) | at risk |
| MQA-1 | [MQA-1](quality-attributes/MQA-1.md) | BG-1 | — | as-built AA-9; ATAM N-3 | addressed |
| INQA-1 | [INQA-1](quality-attributes/INQA-1.md) | BG-1 | — | as-built AA-3; ATAM N-4 | addressed |
| CON-1 | [CON-1](constraints/CON-1.md) | BG-1, BG-3 | — | as-built: docs/view-allocation-deployment.md | open |
| CON-2 | [CON-2](constraints/CON-2.md) | BG-1 | — | as-built: docs/view-allocation-deployment.md | open |
| CON-3 | [CON-3](constraints/CON-3.md) | BG-1 | — | as-built: docs/view-allocation-deployment.md | open |
| CON-4 | [CON-4](constraints/CON-4.md) | BG-1, BG-2 | — | as-built: docs/view-allocation-deployment.md | open |
| CON-5 | [CON-5](constraints/CON-5.md) | BG-1, BG-4 | — | as-built: docs/view-allocation-deployment.md | open |
| CON-6 | [CON-6](constraints/CON-6.md) | BG-1, BG-3 | — | as-built: docs/view-allocation-deployment.md | open |
| BG-1 | [BG-1](business-goals/BG-1.md) | — | UC-1, UC-5, UC-6, PQA-1, DQA-1, MQA-1, INQA-1, OQA-1 | — | open |
| BG-2 | [BG-2](business-goals/BG-2.md) | — | UC-1, UC-2, UC-3, UC-4, UC-5, AQA-1, AQA-2, PQA-1, SCQA-1 | — | at risk |
| BG-3 | [BG-3](business-goals/BG-3.md) | — | UC-6, PQA-2, SCQA-1 | — | open |
| BG-4 | [BG-4](business-goals/BG-4.md) | — | UC-4, UC-6, UC-7, AQA-1, AQA-2, RQA-1, SQA-1, SQA-2, SQA-3, OQA-1, DQA-1 | — | at risk |

`Status` ∈ open / in design / partially / addressed / at risk (set by ATAM) / retired.

**Coverage check**: every BG is supported by ≥ 1 UC or QA scenario (BG-1: UC-1, UC-5, UC-6 + 5 QA;
BG-2: UC-1–UC-5 + 4 QA; BG-3: UC-6, PQA-2, SCQA-1; BG-4: UC-4, UC-6, UC-7 + 8 QA); every UC, QA
scenario and CON traces up to ≥ 1 BG. Gaps found: none. Open question that could change the set:
BG-4's scope depends on ST-1's demo-vs-production decision (CON-5).

## Prioritised driver list (input to ADD / ATAM)

1. [AQA-2](quality-attributes/AQA-2.md) (H,H) — Loss of Availability Zone eu-central-1a
2. [AQA-1](quality-attributes/AQA-1.md) (H,M) — Single task failure of the storefront
3. [RQA-1](quality-attributes/RQA-1.md) (H,M) — Restore after data corruption or deletion
4. [SQA-2](quality-attributes/SQA-2.md) (H,M) — Containment of a compromised service
5. [SQA-1](quality-attributes/SQA-1.md) (H,L) — Shopper traffic confidentiality in transit
6. [SQA-3](quality-attributes/SQA-3.md) (H,L) — Detection of suspicious control-plane activity
7. [OQA-1](quality-attributes/OQA-1.md) (H,L) — Operators learn of failures before shoppers
8. [UC-1](use-cases/UC-1.md) — Browse product catalogue: Dominant read load; crosses the internet trust boundary; exercises Service Connect and the catalogue database.
9. [UC-2](use-cases/UC-2.md) — Search products: Extends UC-1 conditionally (feature flag); adds a second data store to the catalogue service — a consistency and availability concern.
10. [UC-3](use-cases/UC-3.md) — Manage shopping cart: State-changing; the only data path that leaves the VPC (to a regional AWS endpoint), making it depend on the NAT Gateway.
11. [UC-4](use-cases/UC-4.md) — Check out: Carries PII across three services; the synchronous chain ui → checkout → orders → databases is the longest call path.
12. [UC-5](use-cases/UC-5.md) — Place order: The integration point of the system (asynchronous event); the only use case that writes PII to a database; included by UC-4.
13. [CON-2](constraints/CON-2.md) (hard) — Amazon ECS on AWS Fargate
14. [CON-3](constraints/CON-3.md) (hard) — Upstream pre-built images, version 1.6.3
15. [CON-4](constraints/CON-4.md) (hard) — Backing services limited to supported providers
16. [CON-5](constraints/CON-5.md) (hard) — Upstream: educational use, not production
17. [SCQA-1](quality-attributes/SCQA-1.md) (M,H) — Demand spike
18. [PQA-1](quality-attributes/PQA-1.md) (M,M) — Catalogue page responsiveness
19. [PQA-2](quality-attributes/PQA-2.md) (M,L) — Provisioned capacity is used
20. [DQA-1](quality-attributes/DQA-1.md) (M,L) — Safe rollout of a bad version
21. [MQA-1](quality-attributes/MQA-1.md) (M,L) — Swap a backing-service provider
22. [INQA-1](quality-attributes/INQA-1.md) (M,L) — Add a consumer of order events

## Change log

| Date | Change |
|------|--------|
| 2026-10-09 | initial driver set derived from the as-built AWS evidence (brownfield intake): 4 BG, 7 UC, 6 CON, 5 AC, 13 QA scenarios |
| 2026-10-09 | `/atam` (lightweight) write-back: AQA-1, AQA-2, RQA-1, SQA-1, SQA-2, SQA-3, OQA-1, SCQA-1, DQA-1 → at risk (R-1–R-13); MQA-1, INQA-1 → addressed (N-3, N-4); BG-2, BG-4 → at risk (RT-1–RT-4) |
| 2026-10-09 | scenario diagrams redrawn in PlantUML (UML palette); Mermaid sources removed |

---

**Navigation**: [architecture package](../README.md) · [stakeholders](stakeholders.md) · [brownfield intake](../brownfield-intake.md) · [ATAM report](../atam/atam-report.md) · [docs](../docs/README.md)
