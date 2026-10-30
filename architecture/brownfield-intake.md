# Brownfield intake — retail-store-ecs (as deployed)

- **Date**: 2026-10-09
- **Author**: ST-2 (architecture reconstruction)
- **Scope**: resources tagged `environment-name=retail-store-ecs` in AWS account 111122223333, region
  eu-central-1, plus the untagged resources they reference (Application Load Balancer, task definitions,
  IAM roles, log groups, Cloud Map namespace, secrets). Other workloads in the shared account are out of scope.
- **Mode**: read-only. Only `Describe*` / `List*` / `Get*` calls were made; no secret value was read.

> **The rule that governs this note**: the deployment shows the architecture, never the requirement.
> Every driver drafted from it is *derived — confirm*, and every **missing** tactic is a finding for the
> [ATAM](atam/atam-report.md), not a driver.

## What was read (adapted reading order)

There is no source repository in this project; the **running deployment** stands in for it. The SEI
reading order was mapped onto the evidence that exists:

| # | Intake source (SEI order) | What stood in for it here | Evidence file |
|---|---------------------------|---------------------------|---------------|
| 1 | README / docs / ADRs | Upstream README of `aws-containers/retail-store-sample-app` (purpose, "not for production") | public GitHub |
| 2 | Manifests | Container images and tags in the task definitions | [`retail-store-ecs-evidence.json`](../aws/scoped/retail-store-ecs-evidence.json) |
| 3–4 | Source layout, entry points | 5 ECS services, Service Connect names, ports, health checks | same |
| 5 | Outbound integrations | `RETAIL_*_ENDPOINTS_*` variables, Amazon MQ, OpenSearch, DynamoDB | same |
| 6 | Persistence | Aurora MySQL/PostgreSQL, DynamoDB, ElastiCache, OpenSearch configuration | same |
| 7 | Deployment config | VPC, subnets, routes, security groups, ECS deployment configuration | same + [`architecture-inventory.json`](../aws/discovery/architecture-inventory.json) |
| 8 | Runtime config | Environment variables and Secrets Manager references (names only) | same |
| 9 | Cross-cutting tactics | IAM roles, health checks, Container Insights, ECS Exec | same |
| 10 | Tests | not observable | — |
| 11 | Observability config | Alarms (0), dashboards (0), log retention | same + [`well-architected-evidence.md`](../aws/well-architected/well-architected-evidence.md) |
| 12 | History | Resource creation timestamps (2026-10-09 ~14:48 UTC); no git history | [`supplementary-checks.json`](../aws/scoped/supplementary-checks.json) |

## Evidence table

| Claim | Evidence | Confidence |
|-------|----------|------------|
| The workload is the ECS Terraform deployment of the AWS `retail-store-sample-app` | tag `created-by=retail-store-sample-app`; images `public.ecr.aws/aws-containers/retail-store-sample-*:1.6.3`; timestamp-suffixed Terraform names | high |
| Five microservices: ui, catalog, carts, checkout, orders | ECS services in `retail-store-ecs-cluster`, task definitions `retail-store-ecs-*:1` | high — read from config |
| All services run on Fargate, 1 vCPU / 2 GB, **one task each** | `desiredCount 1`, `cpu 1024`, `memory 2048`, `launchType FARGATE` | high |
| Service-to-service calls use ECS Service Connect in Cloud Map namespace `retailstore.local`, aliases `http://<service>` port 80 → container 8080 | `serviceConnectConfiguration` of each service; `RETAIL_UI_ENDPOINTS_*` | high |
| Only `ui` is exposed, via an internet-facing Application Load Balancer, **HTTP:80 only** | listener `HTTP 80` → target group `ui-application` (HTTP 8080, ip targets) | high |
| catalog → Aurora MySQL 8.0 (3.10.3) and OpenSearch 3.3 (search) | `RETAIL_CATALOG_PERSISTENCE_PROVIDER=mysql`, `RETAIL_CATALOG_SEARCH_OS_ENDPOINT` | high |
| carts → DynamoDB `retail-store-ecs-carts` (on-demand) | `RETAIL_CART_PERSISTENCE_PROVIDER=dynamodb` | high |
| checkout → ElastiCache Redis 4.0.10, single node, no TLS, no AUTH, not encrypted at rest; checkout → orders | `RETAIL_CHECKOUT_PERSISTENCE_REDIS_URL`, replication-group config | high |
| orders → Aurora PostgreSQL 15.10 and RabbitMQ 3.13 on Amazon MQ (AMQPS 5671, single instance) | `RETAIL_ORDERS_PERSISTENCE_PROVIDER=postgres`, `RETAIL_ORDERS_MESSAGING_PROVIDER=rabbitmq` | high |
| Database, broker and search credentials come from Secrets Manager, scoped per execution role | `secrets[].valueFrom`, execution-role policies | high |
| Data tier is single-AZ (Aurora writers in 1c; Redis, MQ, OpenSearch in 1a) | instance placement | high |
| One NAT Gateway (1a) for the private subnets of all three Availability Zones; no VPC endpoints for AWS services | route table `rtb-013112e10818c1489` → `nat-03d1c11b310995aba` | high |
| Deployments are rolling 100/200 with circuit breaker **off** | `deploymentConfiguration` | high |
| No alarms, dashboards, auto scaling, flow logs, CloudTrail, GuardDuty | evidence packs | high |
| The environment is a demonstration, not production | upstream "educational purposes only"; small instance sizes | **medium — confirm with ST-1** |
| Response-time / availability targets | none found anywhere (no SLO, no alarm thresholds) | none — targets in the drivers are proposals |

## Draft drivers (all *derived — confirm*)

Handed to [`/drivers`](drivers/README.md), which holds them as the register:

1. **Business goals**: BG-1 (stated upstream purpose), BG-2 (functional purpose), BG-3 and BG-4
   (inferred — need ST-1).
2. **Use cases**: UC-1 to UC-7 — from the five services' wiring plus the operator paths (deploy, diagnose).
3. **Constraints**: CON-1 to CON-6 — platform, region/account, upstream images, provider set, upstream
   disclaimer, Terraform.
4. **Quality attribute scenarios**: 13, one per tactic family found or conspicuously absent; measures are
   proposals.
5. **Architectural concerns**: AC-1 to AC-5.
6. **As-built views**: the first draft of the [Views and Beyond package](docs/README.md).

## Gap list (as-built vs. as-intended, and absent tactics) → ATAM input

| # | Gap / absent tactic | Evidence | Scenario affected |
|---|---------------------|----------|-------------------|
| G-1 | No redundancy: 1 task per service | `desiredCount 1` × 5 | AQA-1 |
| G-2 | Single-AZ data tier and single NAT Gateway | placement, route table | AQA-2 |
| G-3 | No TLS on the public listener and on internal hops (Redis, Aurora, Service Connect) | listener, parameter groups | SQA-1 |
| G-4 | Task security groups open 8080 to `0.0.0.0/0`; checkout role has DynamoDB access it doesn't need | security groups, IAM | SQA-2 |
| G-5 | No CloudTrail, GuardDuty, Config, Security Hub, Flow Logs, ALB access logs | security scan | SQA-3 |
| G-6 | No alarms or dashboards; task logs never expire; MQ logs off | evidence pack | OQA-1 |
| G-7 | No auto scaling | no scalable targets | SCQA-1 |
| G-8 | Circuit breaker off | deployment configuration | DQA-1 |
| G-9 | DynamoDB point-in-time recovery off; no Redis snapshots; no AWS Backup; deletion protection off | data-store config | RQA-1 |
| G-10 | Redis at rest unencrypted; Redis 4.0.10 old major | replication group | SQA-1, AC-4 |
| G-11 | Images pulled from a public registry without scanning or mirroring | image URIs | DQA-1, SQA-2 |
| G-12 | Cost of the workload not visible (tag not activated) | Cost Explorer returns USD 0 | PQA-2 |

## Questions for the stakeholders

1. ST-1: Is this environment demo-only, a training lab, or a candidate for production? (decides BG-4 priority)
2. ST-1: Where are the Terraform configuration and state? (AC-2)
3. ST-1 / ST-3: Who operates it, and what availability and recovery targets are acceptable? (AQA-1, AQA-2, RQA-1)
4. ST-4: Is the shared account an accepted risk? (AC-1, CON-1)

---

**Navigation**: [architecture package](README.md) · [drivers](drivers/README.md)
