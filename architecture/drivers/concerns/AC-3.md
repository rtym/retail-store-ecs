# AC-3: Missing account security baseline

- **Concern**: CloudTrail, GuardDuty, AWS Config and Security Hub are not enabled in the account/region; 2 console users lack MFA; no password policy.
- **Kind**: general (technology mandate)
- **Raised by**: ST-2 (architecture reconstruction)
- **Priority**: high
- **Status**: open

## Why it matters

The workload inherits a baseline with no audit trail and no threat detection (see SQA-3).

## Related drivers

[BG-4](../business-goals/BG-4.md), [SQA-3](../quality-attributes/SQA-3.md), [CON-1](../constraints/CON-1.md)
