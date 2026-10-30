# Directory — index, glossary, acronyms

- **Date**: 2026-10-09

## Element index

| Element | Defined in |
|---------|-----------|
| ui, catalog, carts, checkout, orders | [module view](view-module-decomposition.md), [C&C view](view-cnc-runtime.md) |
| Application Load Balancer `retail-store-ecs-ui` | [C&C view](view-cnc-runtime.md), [security view](view-security.md) |
| Aurora MySQL / PostgreSQL, DynamoDB, ElastiCache, Amazon MQ, OpenSearch | [C&C view](view-cnc-runtime.md) §2.1, [deployment view](view-allocation-deployment.md) |
| VPC, subnets, NAT Gateway, route tables | [deployment view](view-allocation-deployment.md) |
| Security groups, IAM roles, secrets | [security view](view-security.md) |
| Log groups, Container Insights | [observability view](view-observability.md) |

## Glossary

| Term | Meaning |
|------|---------|
| As-built | What is actually deployed, as opposed to what was intended |
| Availability Zone (AZ) | One isolated location within an AWS region (here eu-central-1a/b/c) |
| Service Connect | ECS feature that gives services short DNS names and routes calls through a proxy sidecar |
| Fargate | ECS launch type in which AWS runs the tasks; no servers to manage |
| Task | A running instance of an ECS task definition (one or more containers) |
| Derived — confirm | A driver or rationale reconstructed from evidence that a stakeholder has not yet confirmed |
| View packet | One view's documentation: primary presentation, element catalog, context, variability, rationale |

## Acronyms

| Acronym | Expansion |
|---------|-----------|
| ACM | AWS Certificate Manager |
| ALB | Application Load Balancer |
| AMQP(S) | Advanced Message Queuing Protocol (over TLS) |
| ATAM | Architecture Tradeoff Analysis Method |
| C&C | Component-and-Connector |
| ECR | Elastic Container Registry |
| ECS | Elastic Container Service |
| ENI | Elastic Network Interface |
| IAM | Identity and Access Management |
| KMS | Key Management Service |
| NAT | Network Address Translation |
| PII | Personally Identifiable Information |
| RPO / RTO | Recovery Point / Recovery Time Objective |
| SG | Security group |
| TLS | Transport Layer Security |
| V&B | Views and Beyond |
| VPC | Virtual Private Cloud |

---

**Navigation**: [docs roadmap](README.md) · [architecture package](../README.md)
