# CON-5: Upstream: educational use, not production

> **Derived — confirm.** Reconstructed from the deployed AWS environment (read-only evidence), not from a stakeholder. Treat as a hypothesis until confirmed.

- **Type**: business
- **Constraint**: The upstream project states it is intended for educational purposes only and not for production use.
- **Source**: aws-containers/retail-store-sample-app README.
- **Nature**: hard
- **Priority**: high
- **Status**: open

## Rationale

Upstream disclaimer; governs what the environment may legitimately be used for.

## Impact on the architecture

Production-grade guarantees (security reviews of the code, support) are not provided upstream.

## Conflicts

BG-4 if ST-1 intends production use — that tension must be decided by ST-1.

## Traces up to

- Business goals: [BG-1](../business-goals/BG-1.md), [BG-4](../business-goals/BG-4.md)
