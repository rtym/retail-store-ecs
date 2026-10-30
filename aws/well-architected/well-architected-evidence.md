# AWS Well-Architected Review -- Evidence Pack

_Pillars: operational-excellence, security, reliability, performance-efficiency, cost-optimization, sustainability_

Generated: 2026-10-09T15:53:31+00:00

## How to use this evidence pack

This report is collected evidence only. Read the matching `references/pillars/<pillar>.md` question catalogue alongside each section below and rate each best-practice question Yes / Partial / No / Not applicable based on the evidence, citing the specific resource IDs found here.

## Operational Excellence

**Region eu-central-1:**

- CloudWatch/Config visibility: 0 Config rule evaluations found, Config recorder NOT recording
- ECS/EKS workloads (deploy automation surface): 1 ECS clusters, 0 EKS clusters
- Lambda functions (event-driven/IaC-friendly compute): 22
- CloudWatch alarms: 0 total, 0 with no notification action, 1 dashboards

## Security

**Region eu-central-1:**

- GuardDuty enabled: False
- Security Hub enabled: False
- Wide-open security group rules: 10
- IAM Access Analyzer active findings: 0
- EC2 instances not enforcing IMDSv2: 0
- Load balancer listeners without TLS: 1
- ACM certificates expired or expiring within 30 days: 0

## Reliability

**Region eu-central-1:**

- Auto Scaling groups: 1
- Load balancers (ALB/NLB + classic): 1
- Multi-AZ signal -- RDS instances: 2, manual snapshots: 0
- NAT gateways (single point of failure risk if 1 per VPC): 1
- CloudWatch alarms monitoring this region: 0 (0 currently in ALARM state)
- AWS Backup plans covering this region: 0 (0 with cross-region copy), 0 recent failed jobs
- Service Quota headroom checked for: Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances, VPCs per Region, Rules per security group, Application Load Balancers per Region, DB instances, Concurrent executions

## Performance Efficiency

**Region eu-central-1:**

- EC2 instances: 2
- VPC endpoints (reduces NAT/internet hairpin latency): 2
- ElastiCache clusters: 1
- DynamoDB tables: 18

## Cost Optimization

**Region eu-central-1:**

- Unattached EBS volumes: 0
- Unassociated Elastic IPs: 0
- Stopped EC2 instances (still billed for EBS): 0

## Sustainability

**Region eu-central-1:**

- Stopped instances retaining attached storage: 0
- Unattached EBS volumes (wasted provisioned capacity): 0
- Manual RDS snapshots retained indefinitely: 0

## Account-wide IAM Evidence (Security + Operational Excellence)

| Signal | Count |
| --- | --- |
| Console users without MFA | 2 |
| Access keys to review | 3 |
| Root account risks | 0 |
| Password policy set | False |

## Account-wide CloudTrail Evidence (Security SEC01/SEC04, Operational Excellence OPS04)

- Multi-region trail configured: False
- A trail is actively logging: False
- Log file validation enabled: False

## Account-wide Budgets Evidence (Cost Optimization COST01/COST03)

1 AWS Budget(s) configured.
