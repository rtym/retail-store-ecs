# retail-store-ecs — architecture reconstruction

Read-only architecture reconstruction of the `retail-store-ecs` workload, an Amazon ECS (Fargate)
deployment in AWS region eu-central-1. Collected on 2026-10-09 with the
`aws-well-architected-and-analysis` and `sei-architecture-methodology` plugins for Claude Code.

| Folder | Contents |
|--------|----------|
| [`aws/`](aws/README.md) | Read-only AWS evidence: discovery inventory, scoped workload evidence, Well-Architected review, security review |
| [`architecture/`](architecture/README.md) | SEI architecture package: brownfield intake, drivers, Views and Beyond documentation, lightweight ATAM, HTML reports |
| [`REPLICATION.md`](REPLICATION.md) | Process replication package: how to repeat the reconstruction on another deployment (setup, `CLAUDE.md`, prompts) |
| [`diagrams/`](diagrams/) | UML figures of the reconstruction toolchain (PlantUML source, PNG, SVG, PDF) |

## Redaction

This public copy is redacted. The AWS account ID is replaced with `111122223333`, IAM user names
with `iam-user-N`, access key IDs with `AKIAREDACTED…`, live endpoint hostnames with placeholders,
and public IP addresses with RFC 5737 documentation addresses. No secret values were ever collected.
