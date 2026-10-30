# Mapping between views — retail-store-ecs

- **Date**: 2026-10-09

This file proves the views are consistent: every module has a runtime component and a deployment
location, and every element maps to the drivers it serves.

## Module → runtime component → deployment

| Module ([view-module-decomposition](view-module-decomposition.md)) | Runtime component ([view-cnc-runtime](view-cnc-runtime.md)) | Deployment ([view-allocation-deployment](view-allocation-deployment.md)) | Security controls ([view-security](view-security.md)) |
|---|---|---|---|
| ui | ECS service `ui`, Service Connect name `ui`, target of load balancer | 1 Fargate task, private subnet (1c on 2026-10-09) | task SG `sg-0e0e2272b9ea01935`; roles `retail-store-ecs-ui-task` / `-ui-te` |
| catalog | ECS service `catalog` (`catalog:80`) | 1 Fargate task (1a) | task SG `sg-040b3a46ff959179a`; roles `-catalog-task` / `-catalog-te` (2 secrets) |
| carts | ECS service `carts` (`carts:80`) | 1 Fargate task (1c) | task SG `sg-0da8eca938cda3bab`; roles `-carts-task` / `-carts-te` |
| checkout | ECS service `checkout` (`checkout:80`) | 1 Fargate task (1a) | task SG `sg-0095c5c4e962d6d3c`; roles `-checkout-task` / `-checkout-te` |
| orders | ECS service `orders` (`orders:80`) | 1 Fargate task (1a) | task SG `sg-07200dd8c1cd91664`; roles `-orders-task` / `-orders-te` (2 secrets) |

## Data store ownership → runtime connector → placement

| Element | Owner module | Connector | Placement | Store security group |
|---------|--------------|-----------|-----------|----------------------|
| Aurora MySQL `retail-store-ecs-catalog` | catalog | MySQL TCP 3306 | writer in 1c | `sg-09c7a14effce5b90a` ← catalog-task |
| OpenSearch `retail-store-ecs-catalog` | catalog | HTTPS 443 | 1 node, 1a | `sg-0f311a84fbd640ebb` ← catalog-task |
| DynamoDB `retail-store-ecs-carts` | carts | HTTPS 443 via NAT | regional | IAM only (`retail-store-ecs-carts-dynamo`) |
| ElastiCache `retail-store-ecs-checkout` | checkout | Redis TCP 6379 | 1 node, 1a | `sg-0f71c87c4e6803b4d` ← checkout-task |
| Aurora PostgreSQL `retail-store-ecs-orders` | orders | PostgreSQL TCP 5432 | writer in 1c | `sg-0d699b165b0fd5d62` ← orders-task |
| Amazon MQ `retail-store-ecs-orders-broker` | orders | AMQPS 5671 | single instance, 1a | `sg-065189381aa8e7c39` ← orders-task |

## Element → driver

| Element | Drivers served | Drivers put at risk |
|---------|----------------|---------------------|
| Application Load Balancer (3 AZ) | UC-1–UC-4, BG-2 | SQA-1 (HTTP only), SQA-3 (no access logs) |
| Service Connect | UC-1–UC-5, MQA-1 | SQA-1 (no TLS) |
| 1 task per service | BG-3, PQA-2 | AQA-1, SCQA-1 |
| Single NAT Gateway | BG-3 | AQA-2, UC-3, UC-6 |
| Single-AZ data stores | BG-3 | AQA-2, RQA-1 |
| Per-store security groups + scoped secrets | SQA-2, BG-4 | — |
| Task security groups 8080 from 0.0.0.0/0 | — | SQA-2 |
| Amazon MQ publish-subscribe | INQA-1, UC-5 | AQA-2 (single instance) |
| Provider environment variables | MQA-1, CON-4 | — |
| Rolling deployment, circuit breaker off | UC-6 | DQA-1 |
| Container Insights + task log group | UC-7 | OQA-1 (no alarms), PQA-2 (1-day retention) |

## Use case → views that show it

| Use case | Behaviour | Structure | Placement |
|----------|-----------|-----------|-----------|
| UC-1 / UC-2 | [seq-uc1-browse](view-cnc-runtime.md#uc-1--uc-2--browse-and-search-the-catalogue) | view-cnc-runtime 1a, 1b | view-allocation-deployment 1a, 1b |
| UC-3 | [seq-uc3-cart](view-cnc-runtime.md#uc-3--manage-shopping-cart) | view-cnc-runtime 1b | view-allocation-deployment 1a (NAT) |
| UC-4 / UC-5 | [seq-uc4-checkout](view-cnc-runtime.md#uc-4--uc-5--check-out-and-place-order) | view-cnc-runtime 1c | view-allocation-deployment 1b |
| UC-6 | [seq-uc6-deploy](view-cnc-runtime.md#uc-6--deploy-a-new-service-version) | view-module-decomposition 1b | view-allocation-deployment 1a |
| UC-7 | [view-observability](view-observability.md) §2.4 | view-observability | — |

---

**Navigation**: [docs roadmap](README.md) · [architecture package](../README.md)
