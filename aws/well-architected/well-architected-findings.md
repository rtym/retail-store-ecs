# AWS Well-Architected Review -- Findings for `retail-store-ecs`

_Account 111122223333 · eu-central-1 · evidence collected 2026-10-09 (read-only)_

**Scope.** The account is shared with other workloads (happy-nmt, TMG, sklad-kontrol, Terra, quiz-scanner, ...).
These findings are about the `retail-store-ecs` workload, identified by the tag `environment-name=retail-store-ecs`.
Account-wide controls (CloudTrail, GuardDuty, IAM users, ...) are included because the workload inherits them.

**Evidence sources**

| Source | Path |
|---|---|
| Account inventory (aws-architecture-discovery) | `aws/discovery/architecture-inventory.json` |
| Workload-scoped evidence | `aws/scoped/retail-store-ecs-evidence.json`, `aws/scoped/supplementary-checks.json` |
| Well-Architected evidence pack | `aws/well-architected/wa-evidence.json`, `well-architected-evidence.md` |
| Security scan (aws-security-review) | `aws/security/security-findings.json`, `security-review.md` |

**Verdicts.** Yes · Partial · No · Not verified via API (NV). Risk: **HRI** = High Risk Issue, **MRI** = Medium Risk Issue.
Process-only questions are marked NV until the workload owner confirms them.

## Summary

| Pillar | Yes | Partial | No | NV | HRI | MRI |
|---|---|---|---|---|---|---|
| Operational Excellence | 0 | 2 | 2 | 7 | 2 | 2 |
| Security | 0 | 5 | 3 | 3 | 5 | 4 |
| Reliability | 2 | 4 | 5 | 2 | 5 | 4 |
| Performance Efficiency | 2 | 3 | 0 | 0 | 0 | 3 |
| Cost Optimization | 1 | 4 | 1 | 5 | 0 | 5 |
| Sustainability | 1 | 3 | 0 | 2 | 0 | 3 |

## Operational Excellence

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| OPS01 Priorities | NV | -- | Process question | Confirm what the workload is for (demo or production) and its owners |
| OPS02 Organization | NV | -- | Process question | Name an owning team; the cluster has no tags (`Ecs.Cluster[0].tags = []`) |
| OPS03 Culture | NV | -- | Process question | -- |
| OPS04 Understand state | Partial | MRI | Container Insights `enhanced` is on and all 5 task definitions log to `retail-store-ecs-tasks`. AWS Config recorder is **not recording**. Two tags on 44 resources, but the Application Load Balancer, ECS cluster and task definitions are not tagged. | Turn on AWS Config; tag every resource (owner, cost-centre) |
| OPS05 Defects / flow | NV | -- | Resources are Terraform-generated (timestamped names), with images pinned to `1.6.3` from `public.ecr.aws`. No pipeline evidence. | Confirm the CI/CD pipeline and where Terraform state is stored |
| OPS06 Deployment risk | Partial | MRI | All 5 services: `ROLLING`, min 100 % / max 200 %, **deployment circuit breaker disabled** (`enable: false, rollback: false`) | Enable the circuit breaker with rollback |
| OPS07 Readiness | NV | -- | Process question | Write runbooks |
| OPS08 Observability | No | HRI | 0 CloudWatch alarms and 0 dashboards for the workload; no Application Load Balancer access logs; no Amazon MQ general logs (`Logs.General=false`) | Alarm on ALB 5xx, unhealthy hosts, ECS CPU/memory and database health |
| OPS09 Operations health | No | HRI | Same as OPS08 -- nobody is notified of anything | Route alarms to SNS/on-call |
| OPS10 Events | NV | -- | GuardDuty and Security Hub are off, so no event source exists | -- |
| OPS11 Evolve | NV | -- | Process question | -- |

## Security

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| SEC01 Secure operation | No | HRI | 0 CloudTrail trails; AWS Config not recording (account-wide) | Multi-region CloudTrail with log-file validation |
| SEC02 Authentication | Partial | HRI | Workload: ECS tasks use per-service IAM roles; database credentials come from Secrets Manager. Account: 2 console users without MFA, no password policy. | MFA for all console users; IAM Identity Center |
| SEC03 Permissions | Partial | MRI | `retail-store-ecs-checkout-task` has `dynamodb:*` on the carts table, but checkout uses Redis, not DynamoDB. `carts-task` also has `dynamodb:*` (needs only CRUD + Query on the index). ECS Exec (`ssmmessages:*`) is enabled on all services. | Least privilege; remove DynamoDB from checkout; turn ECS Exec off outside debugging |
| SEC04 Detection | No | HRI | GuardDuty, Security Hub and Config are all disabled in eu-central-1 | Enable all three, including GuardDuty ECS Runtime Monitoring |
| SEC05 Network protection | Partial | MRI | Good: tasks run in private subnets (`assignPublicIp DISABLED`); each data store's security group admits only its one client. Weak: all 5 task security groups allow TCP 8080 from `0.0.0.0/0` (in practice anything in the VPC); no VPC Flow Logs; no AWS WAF. | Restrict ingress: UI from the ALB security group, others from their client security groups only; enable Flow Logs |
| SEC06 Compute protection | Partial | MRI | Fargate (no host to patch). Containers run with a writable root filesystem (`readonlyRootFilesystem: false`), no `user` set; public images without scanning. | Read-only root filesystem; mirror images into a private ECR repository with scanning |
| SEC07 Data classification | NV | -- | No classification tags. Orders contain customer PII. | Classify data; tag data stores |
| SEC08 At rest | Partial | MRI | Aurora (both) encrypted; OpenSearch encrypted with KMS; DynamoDB uses an AWS-owned key; MQ uses an AWS-owned key. **ElastiCache Redis is not encrypted at rest** (`AtRestEncryptionEnabled=false`). | Recreate Redis with at-rest encryption |
| SEC09 In transit | No | HRI | Application Load Balancer listener is **HTTP:80 only**, no TLS. Redis has no in-transit encryption or AUTH. Aurora PostgreSQL `rds.force_ssl=0`, MySQL `require_secure_transport` OFF. Service Connect has no TLS. (MQ uses AMQPS 5671 and OpenSearch enforces HTTPS, both correctly.) | HTTPS listener with an ACM certificate and HTTP->HTTPS redirect; TLS for Redis, the databases and Service Connect |
| SEC10 Incidents | NV | HRI | No detection surface (SEC04) | Incident runbooks once detection exists |
| SEC11 AppSec | NV | -- | Upstream sample images | Confirm image provenance and scanning |

## Reliability

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| REL01 Quotas | Yes | -- | Quota headroom checked by the evidence pack; this workload is small | -- |
| REL02 Network topology | Yes | -- | VPC 10.0.0.0/16, 3 public and 3 private /24 subnets across eu-central-1a/b/c | -- |
| REL03 Service architecture | Partial | MRI | 5 microservices, Service Connect discovery, asynchronous orders->RabbitMQ. Every service runs `desiredCount 1`. | -- (see REL05) |
| REL04 Prevent failures | Partial | MRI | Target-group health check `/actuator/health` returns 200; container health checks on all services; circuit breaker off | Enable the circuit breaker |
| REL05 Withstand failures | No | HRI | **Each service runs a single task**: a task or Availability-Zone failure is an outage of that function (UI = total outage). | `desiredCount >= 2`, spread across Availability Zones |
| REL06 Monitoring | No | HRI | 0 alarms | See OPS08 |
| REL07 Adapt to demand | Partial | MRI | DynamoDB on-demand (Yes). No ECS Application Auto Scaling targets or policies; fixed-size Aurora `db.t3.medium` | Target-tracking auto scaling per service |
| REL08 Change | NV | -- | Process question | -- |
| REL09 Backup | Partial | MRI | Aurora 7-day automated backups. DynamoDB point-in-time recovery **disabled**. Redis snapshots 0. No AWS Backup plan. Deletion protection off on Aurora and DynamoDB. | Point-in-time recovery for DynamoDB; AWS Backup; deletion protection |
| REL10 Fault isolation | No | HRI | Data tier is single-AZ: both Aurora writers in 1c, Redis, MQ (`SINGLE_INSTANCE`) and OpenSearch (1 node) in 1a. **One NAT Gateway** (in 1a) serves the private subnets of all three AZs. | Multi-AZ for all data stores; one NAT Gateway per AZ |
| REL11 Component failure | No | HRI | Aurora `MultiAZ: false` (1 instance each); Redis `AutomaticFailover: disabled`; MQ single instance; OpenSearch `ZoneAwareness: false` | Aurora reader replica in a second AZ; Redis replica with failover; MQ cluster deployment; OpenSearch 2-3 AZ |
| REL12 Test reliability | NV | -- | Process question | -- |
| REL13 DR | No | HRI | No cross-region copies; DR tier = none / backup-in-region | Decide on RTO/RPO; at least cross-region backup copies |

## Performance Efficiency

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| PERF01 Architecture | Yes | -- | Serverless containers (Fargate) and managed data services, each matched to its service: DynamoDB (carts), Aurora MySQL + OpenSearch (catalog), Redis (checkout), Aurora PostgreSQL + RabbitMQ (orders) | -- |
| PERF02 Compute | Partial | MRI | Every task gets 1 vCPU / 2 GB with no measured sizing; x86 (no `runtimePlatform` set, so not Graviton/ARM64) | Right-size from Container Insights; try ARM64 |
| PERF03 Storage | Yes | -- | OpenSearch gp3 50 GB; Aurora storage is managed | -- |
| PERF04 Database | Partial | MRI | Data stores fit their access patterns well. Redis **4.0.10** is an old major version; Aurora on burstable `db.t3.medium`. | Upgrade to Valkey/Redis 7; non-burstable or Serverless v2 Aurora |
| PERF05 Networking | Partial | MRI | No gateway endpoints for DynamoDB/S3, so carts->DynamoDB and image pulls go through the single NAT Gateway | DynamoDB and S3 gateway endpoints; ECR/Logs/Secrets Manager interface endpoints |

## Cost Optimization

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| COST01 Financial management | Partial | MRI | 1 AWS Budget exists in the account; no anomaly monitor evidence | Budget per environment |
| COST02 Govern usage | Partial | MRI | `environment-name` tag on 44 resources; Cost Explorer returns USD 0 for that tag, so it is **not an activated cost-allocation tag** | Activate the tag |
| COST03 Monitor | No | MRI | The workload's cost cannot be seen (see COST02) | -- |
| COST04 Decommission | Yes | -- | No idle EBS/EIP/stopped instances for this workload | -- |
| COST05 Service selection | Partial | MRI | `mq.m5.large` and `r8g.medium.search` are the largest line items for a 1-task-per-service system | Use `mq.t3.micro` for non-production |
| COST06 Resource size | Partial | MRI | 5 x 1 vCPU/2 GB with no utilisation data | Right-size |
| COST07 Pricing models | NV | -- | No Savings Plans data (`DataUnavailableException`); no Fargate Spot capacity provider | Fargate Spot for non-production |
| COST08 Data transfer | NV | -- | Not collected; NAT data processing for DynamoDB is avoidable (PERF05) | -- |
| COST09 Demand/supply | NV | -- | No scaling (REL07) | -- |
| COST10 New services | NV | -- | Process question | -- |
| COST11 Cost of effort | NV | -- | Process question | -- |

## Sustainability

| Q | Verdict | Risk | Evidence | Recommendation |
|---|---|---|---|---|
| SUS01 Region | NV | -- | eu-central-1 | Check against AWS's current renewable-energy region list |
| SUS02 User patterns | Partial | MRI | Always-on; no scale-to-zero schedule | Schedule non-production environments down |
| SUS03 Software patterns | Yes | -- | Fargate, DynamoDB on-demand, managed services | -- |
| SUS04 Data patterns | Partial | MRI | Container Insights logs kept 1 day; task logs **never expire** | Set log retention |
| SUS05 Hardware | Partial | MRI | OpenSearch on Graviton (r8g); tasks x86; Aurora/Redis/MQ x86 t3/m5 | Graviton (t4g/r7g/m7g) |
| SUS06 Dev process | NV | -- | Process question | -- |
