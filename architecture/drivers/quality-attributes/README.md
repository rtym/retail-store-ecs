# Quality attribute scenarios

Index for `architecture/drivers/quality-attributes/`. Grouped by ISO/IEC 25010 characteristic (same order as the [utility tree](utility-tree.md)). All scenarios are **derived — confirm**; measures are proposed targets.

| ID | ISO 25010 characteristic / sub | One-line scenario | (V, R) | Status |
|----|-------------------------------|-------------------|:------:|:------:|
| [AQA-1](AQA-1.md) | Reliability / availability | Single task failure of the storefront — 0 failed shopper requests and < 1 % 5xx over the 5 min after a single-task failure | (H, M) | at risk |
| [AQA-2](AQA-2.md) | Reliability / availability / fault tolerance | Loss of Availability Zone eu-central-1a — browse + cart restored within 5 min; 0 committed orders lost | (H, H) ★ | at risk |
| [RQA-1](RQA-1.md) | Reliability / recoverability | Restore after data corruption or deletion — orders RPO ≤ 5 min and RTO ≤ 4 h; carts RPO ≤ 24 h | (H, M) | at risk |
| [PQA-1](PQA-1.md) | Performance efficiency / time behaviour | Catalogue page responsiveness — Application Load Balancer TargetResponseTime p95 ≤ 1 s, 0 % 5xx | (M, M) | open |
| [PQA-2](PQA-2.md) | Performance efficiency / resource utilisation | Provisioned capacity is used — average CPU utilisation ≥ 40 % on tasks and data nodes, or a documented reason why not | (M, L) | open |
| [SCQA-1](SCQA-1.md) | Flexibility / scalability | Demand spike — capacity added within 5 min, < 1 % 5xx during the spike; back to baseline within 30 min after it | (M, H) | at risk |
| [DQA-1](DQA-1.md) | Flexibility / installability (deployability) | Safe rollout of a bad version — 0 shopper-visible errors; automatic rollback within 10 min | (M, L) | at risk |
| [SQA-1](SQA-1.md) | Security / confidentiality | Shopper traffic confidentiality in transit — 100 % of external requests on TLS 1.2+; 0 plaintext listeners; 0 plaintext connections to stores holding PII | (H, L) | at risk |
| [SQA-2](SQA-2.md) | Security / integrity | Containment of a compromised service — 0 network paths outside the intended graph (verified by VPC Reachability Analyzer); 0 secrets readable by a non-owning task role | (H, M) | at risk |
| [SQA-3](SQA-3.md) | Security / accountability | Detection of suspicious control-plane activity — 100 % of API calls recorded; alert within 15 min | (H, L) | at risk |
| [MQA-1](MQA-1.md) | Maintainability / modifiability | Swap a backing-service provider — 0 lines of application code; ≤ 1 task-definition revision; done within 1 person-day | (M, L) | addressed |
| [OQA-1](OQA-1.md) | Observability (cross-cutting) / monitorability | Operators learn of failures before shoppers — notification within 5 min; 100 % of services covered by an alarm | (H, L) | at risk |
| [INQA-1](INQA-1.md) | Integrability (cross-cutting) / integrability | Add a consumer of order events — 0 changes to the orders service; consumer receiving events within 2 days of effort | (M, L) | addressed |

**[Utility tree (table) →](utility-tree.md)** — the summary of these quality attributes, `(V, R)` per leaf.

---

**Navigation**: [drivers README](../README.md) · [architecture package](../../README.md)
