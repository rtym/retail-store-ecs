# Quality Attribute Utility Tree: retail-store-ecs

- **Date**: 2026-10-09
- **Purpose**: prioritise the reconstructed quality-attribute requirements as scenarios (input to the ATAM)
- **Basis**: built by the architect (ST-2) from the as-built evidence — **no QAW was held**; `(V, R)` values are the architect's proposal for ST-1 to confirm. ISO/IEC 25010:2023 is the quality model.

`(V, R)` = business value and technical risk (`H`/`M`/`L`). `★` marks `(H, H)` leaves.

## Utility tree — Root: Utility (fitness for purpose)

| Quality attribute | Refinement (concern) | Leaf scenario (ID — one line, with the response measure) | Priority (V, R) | Status |
|-------------------|----------------------|---------------------------------------------------------|:---------------:|:------:|
| Reliability | availability | `AQA-1` — Single task failure of the storefront: 0 failed shopper requests and < 1 % 5xx over the 5 min after a single-task failure | (H, M) | at risk |
| Reliability | availability / fault tolerance | `AQA-2` — Loss of Availability Zone eu-central-1a: browse + cart restored within 5 min; 0 committed orders lost | (H, H) `★` | at risk |
| Reliability | recoverability | `RQA-1` — Restore after data corruption or deletion: orders RPO ≤ 5 min and RTO ≤ 4 h; carts RPO ≤ 24 h | (H, M) | at risk |
| Performance efficiency | time behaviour | `PQA-1` — Catalogue page responsiveness: Application Load Balancer TargetResponseTime p95 ≤ 1 s, 0 % 5xx | (M, M) | open |
| Performance efficiency | resource utilisation | `PQA-2` — Provisioned capacity is used: average CPU utilisation ≥ 40 % on tasks and data nodes, or a documented reason why not | (M, L) | open |
| Flexibility | scalability | `SCQA-1` — Demand spike: capacity added within 5 min, < 1 % 5xx during the spike; back to baseline within 30 min after it | (M, H) | at risk |
| Flexibility | installability (deployability) | `DQA-1` — Safe rollout of a bad version: 0 shopper-visible errors; automatic rollback within 10 min | (M, L) | at risk |
| Security | confidentiality | `SQA-1` — Shopper traffic confidentiality in transit: 100 % of external requests on TLS 1.2+; 0 plaintext listeners; 0 plaintext connections to stores holding PII | (H, L) | at risk |
| Security | integrity | `SQA-2` — Containment of a compromised service: 0 network paths outside the intended graph (verified by VPC Reachability Analyzer); 0 secrets readable by a non-owning task role | (H, M) | at risk |
| Security | accountability | `SQA-3` — Detection of suspicious control-plane activity: 100 % of API calls recorded; alert within 15 min | (H, L) | at risk |
| Maintainability | modifiability | `MQA-1` — Swap a backing-service provider: 0 lines of application code; ≤ 1 task-definition revision; done within 1 person-day | (M, L) | addressed |
| Observability (cross-cutting) | monitorability | `OQA-1` — Operators learn of failures before shoppers: notification within 5 min; 100 % of services covered by an alarm | (H, L) | at risk |
| Integrability (cross-cutting) | integrability | `INQA-1` — Add a consumer of order events: 0 changes to the orders service; consumer receiving events within 2 days of effort | (M, L) | addressed |

## Reading the tree

- **Reliability** carries the only `★` leaf (`AQA-2`, Availability Zone loss): the single-AZ data tier
  and the single NAT Gateway make it both valuable and hard — it touches every data store.
- **Security** and **Observability** leaves are high value but low difficulty: the tactics are
  configuration changes (TLS listener, CloudTrail/GuardDuty, alarms), not structural redesign.
- **Usability**, **Compatibility** and **Portability** have no leaf — not investigated, because the
  application code is fixed (CON-3); raise them in a QAW if ST-1 wants them.
- No leaf is `addressed` yet; `MQA-1` and `INQA-1` are already supported by tactics present in the
  deployment (configuration-time binding, broker intermediary) — candidates for non-risks in the ATAM.

## Analysis targets

The `(H, H)` and `(H, M)` leaves are analysed first: `AQA-2`, `AQA-1`, `RQA-1`, `SQA-2`, then the
`(H, L)` security and observability leaves `SQA-1`, `SQA-3`, `OQA-1`.

---

**Navigation**: [quality attributes index](README.md) · [drivers README](../README.md) · [architecture package](../../README.md)
