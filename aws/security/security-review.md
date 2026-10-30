# AWS Security Review

_GuardDuty, Security Hub, IAM, and network exposure findings_

Generated: 2026-10-09T15:52:28+00:00

## CloudTrail

- **Multi-region trail configured:** NO -- gap
- **A trail is actively logging:** NO -- gap
- **Log file validation enabled:** no
- **Trails found:** 0

## IAM Hygiene

- **Console users without MFA:** 2
- **Access keys to review (active, rotation age tracked):** 3
- **Root account risks:** none detected
- **Account password policy set:** no

## S3 Exposure

| Bucket | Issue |
| --- | --- |
| quiz-scanner-ui-111122223333-eu-central-1 | Public access not fully blocked |

## Regional Coverage

| Region | GuardDuty | Security Hub | Config recorder | GuardDuty findings | Security Hub findings | Open security groups |
| --- | --- | --- | --- | --- | --- | --- |
| eu-central-1 | NOT enabled | NOT enabled | NOT recording | 0 | 0 | 10 |

## Wide-Open Security Group Rules

| Region | Group | Port range | Protocol | Open to |
| --- | --- | --- | --- | --- |
| eu-central-1 | sg-089fe6fbd4d9a9033 | 80-80 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0acded8061f612a60 | 3389-3389 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0ad6c494b0abe97dd | 3389-3389 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-01179a77728a504c6 | 22-22 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-040b3a46ff959179a | 8080-8080 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-07200dd8c1cd91664 | 8080-8080 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0da8eca938cda3bab | 8080-8080 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0ca08510903503c64 | 80-80 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0e0e2272b9ea01935 | 8080-8080 | tcp | 0.0.0.0/0 |
| eu-central-1 | sg-0095c5c4e962d6d3c | 8080-8080 | tcp | 0.0.0.0/0 |

## Load Balancer Listeners Without TLS

| Region | Load balancer | Port | Protocol |
| --- | --- | --- | --- |
| eu-central-1 | retail-store-ecs-ui | 80 | HTTP |
