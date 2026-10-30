# AWS evidence — retail-store-ecs

Read-only evidence collected on 2026-10-09 from account 111122223333, region eu-central-1, with the
`aws-well-architected-and-analysis` plugin plus a workload-scoped collector. It is the evidence base
for the SEI architecture package in [`../architecture/`](../architecture/README.md).

| Folder | Produced by | Contents |
|--------|-------------|----------|
| [`discovery/`](discovery/architecture-discovery.md) | `aws-architecture-discovery` | account-wide inventory JSON + Markdown/HTML/PDF report (the account is shared — only the `retail-store-ecs` resources are used by the architecture package) |
| [`scoped/`](scoped/retail-store-ecs-evidence.json) | `scoped/collect_retail_store.py` (read-only) | ECS services, task definitions (sensitive environment values redacted), Service Connect, load balancer, data stores, IAM, logging; `supplementary-checks.json` |
| [`well-architected/`](well-architected/well-architected-findings.md) | `aws-well-architected-review` | evidence pack (md/html/pdf/json) + scored findings for this workload |
| [`security/`](security/security-review.md) | `aws-security-review` | account security posture (md/html/pdf/json) |

## Notes on collection

- Only `Describe*`, `List*` and `Get*` API calls were made; no resource was changed. Secrets Manager was
  queried for metadata only; secret values were never read.
- The workstation could not reach the IPv4 regional Elastic Load Balancing endpoint, so the collectors ran
  with `AWS_USE_DUALSTACK_ENDPOINT=true`.
- The Well-Architected collector was run through a wrapper that tolerates `DataUnavailableException` (no
  Savings Plans history) and an unavailable Trusted Advisor (Basic support plan); the plugin itself was
  not modified.
