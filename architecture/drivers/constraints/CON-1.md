# CON-1: AWS eu-central-1 in a shared account

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: technical
- **Constraint**: The workload runs in AWS region eu-central-1, account 111122223333, which also hosts unrelated workloads (happy-nmt, TMG, sklad-kontrol, Terra, quiz-scanner, …).
- **Source**: Deployment evidence (`aws/discovery/architecture-inventory.json`); owner to confirm whether intentional.
- **Nature**: negotiable
- **Priority**: high
- **Status**: open

## Rationale

Region and account are where the environment was deployed; no landing-zone or Organizations structure isolates it.

## Impact on the architecture

Account-level controls (CloudTrail, GuardDuty, Config, IAM users) are shared with neighbours; quotas are shared; cost must be separated by tag.

## Conflicts

BG-4 (isolation and detection are weaker in a shared account).

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md), [BG-3](../business-goals/BG-3.md)
