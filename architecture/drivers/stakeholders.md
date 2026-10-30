# Stakeholders — retail-store-ecs

- **Date**: 2026-10-09
- **Owner**: workload owner (ST-1) — to confirm

> The single stakeholder register for the whole `architecture/` package. Reconstructed from the
> deployment; **no stakeholder has been interviewed yet** — names marked "to be named" must be filled
> by ST-1 before a QAW or a full ATAM Phase 2.

| ID | Name / representative | Role | Concerns | QAW | ATAM Phase 2 | V&B reader |
|----|-----------------------|------|----------|:---:|:------------:|:----------:|
| ST-1 | AWS account owner of 111122223333 (identity to confirm) | sponsor / workload owner | purpose of the environment, cost, exposure of a shared account | ✓ | ✓ | ✓ |
| ST-2 | Architecture reconstruction author | architect | accurate as-built description, traceable risks | ✓ | ✓ | ✓ |
| ST-3 | Operator / SRE (to be named) | operations | deployability, observability, recovery, on-call load | ✓ | ✓ | ✓ |
| ST-4 | Security and compliance (to be named) | security | data protection in transit/at rest, detection, least privilege | ✓ | ✓ | ✓ |
| ST-5 | Shopper (end-user representative) | end user | store available and responsive, personal data protected | ✓ | ✓ |  |
| ST-6 | Upstream maintainers of aws-containers/retail-store-sample-app | developers of the container images | supported configuration, provider options, versions |  |  | ✓ |
| ST-7 | Owners of co-tenant workloads in the same account | downstream / neighbours | blast radius, quotas, cost attribution in the shared account |  | ✓ |  |

---

**Navigation**: [drivers README](README.md) · [architecture package](../README.md)
