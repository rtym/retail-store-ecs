# Architecture package — retail-store-ecs

- **Date**: 2026-10-09
- **Owner**: workload owner (ST-1) — to confirm; reconstructed by ST-2
- **Design purpose**: brownfield — as-built architecture recovery and assessment of an existing deployment
- **Stakeholders**: [drivers/stakeholders.md](drivers/stakeholders.md)
- **Diagram notation**: UML throughout (PlantUML) — legend: [diagrams/legend.png](diagrams/legend.png)

> The index of `architecture/`. Every SEI activity registers its output here.
> Evidence base: read-only AWS evidence in [`../aws/`](../aws/README.md); the reconstruction started
> with the [brownfield intake](brownfield-intake.md). Everything derived from the deployment rather
> than from people is marked **derived — confirm**.

## Start here

| If you want… | Read |
|--------------|------|
| What the system is and how it is built | [docs/README.md](docs/README.md) → [system overview](docs/system-overview.md) |
| What it must achieve (as far as can be reconstructed) | [drivers/README.md](drivers/README.md), [utility tree](drivers/quality-attributes/utility-tree.md) |
| Whether it achieves it — risks and what to do | [atam/atam-report.md](atam/atam-report.md) |
| How it was reconstructed, and what is still unknown | [brownfield-intake.md](brownfield-intake.md) |

## Activities and outputs

| Activity | Command | Output | Status |
|----------|---------|--------|--------|
| Brownfield intake | `/sei` (router) | [brownfield-intake.md](brownfield-intake.md) | done 2026-10-09 |
| Architectural drivers | `/drivers` | [drivers/README.md](drivers/README.md) | done 2026-10-09 (all derived — confirm) |
| Quality attribute scenarios | `/quality-attributes` | in the drivers register (register mode): [drivers/quality-attributes/](drivers/quality-attributes/README.md) | done 2026-10-09 |
| Quality Attribute Workshop | `/qaw` | `qaw/qaw-report.md` | not run — needs stakeholders in the room |
| ADD 3.0 design | `/add` | `add/<slug>-Architecture.md` + `add/adr/` | not run — recommended for risk themes RT-1–RT-4 |
| ATAM evaluation | `/atam` | [atam/atam-report.md](atam/atam-report.md) | done 2026-10-09 (Lightweight) |
| Views and Beyond documentation | `/architecture-docs` | [docs/README.md](docs/README.md) | done 2026-10-09 (v0.1 as-built) |
| Deliverable reports | `build-report.sh` | [reports/](reports/architecture-description.html) | done 2026-10-09 (HTML) |

## Change log

| Date | Activity | Change |
|------|----------|--------|
| 2026-10-09 | intake | brownfield intake from AWS evidence (read-only) |
| 2026-10-09 | `/drivers` | package created; initial driver set: 4 BG, 7 UC, 6 CON, 5 AC, 13 QA scenarios, 7 stakeholders |
| 2026-10-09 | `/architecture-docs` | V&B package v0.1: system overview; module, C&C, deployment, security, observability views; mapping; rationale; directory |
| 2026-10-09 | `/atam` | lightweight evaluation: 12 approaches, 14 risks, 9 non-risks, 7 sensitivity points, 5 tradeoff points, 4 risk themes; write-back: 9 scenarios + BG-2, BG-4 at risk; MQA-1, INQA-1 addressed |
| 2026-10-09 | all | diagrams converted to UML (PlantUML) at the owner's request: use case, component, deployment and sequence diagrams; scenario diagrams in the PlantUML six-part pattern |
| 2026-10-09 | reports | HTML deliverables built in `reports/` |
