# AC-4: Version currency of managed engines and images

- **Concern**: ElastiCache runs Redis 4.0.10, images are pinned to 1.6.3, Aurora MySQL 3.10.3 and Aurora PostgreSQL 15.10; Amazon MQ auto-minor-upgrade is on.
- **Kind**: quality of the design
- **Raised by**: ST-2 (architecture reconstruction)
- **Priority**: medium
- **Status**: open

## Why it matters

Old engine majors lose support and carry known issues; upgrades need a planned path (and Redis 4 → 7 requires replacing the cluster).

## Related drivers

[BG-4](../business-goals/BG-4.md), [DQA-1](../quality-attributes/DQA-1.md)
