"""Post-ATAM overlay for gen_drivers.py: statuses, 'Addressed in' cells and change-log lines.

Kept separate from the derived driver data so the evaluation's write-back is visible as one diff.
"""
STATUS = {
    "AQA-1": "at risk", "AQA-2": "at risk", "RQA-1": "at risk", "SQA-1": "at risk",
    "SQA-2": "at risk", "SQA-3": "at risk", "OQA-1": "at risk", "SCQA-1": "at risk",
    "DQA-1": "at risk",
    "MQA-1": "addressed", "INQA-1": "addressed",
    "BG-2": "at risk", "BG-4": "at risk",
}

ADDRESSED = {
    "AQA-1": "ATAM R-1 (RT-1)", "AQA-2": "ATAM R-2, R-3 (RT-1)", "RQA-1": "ATAM R-4 (RT-4)",
    "SQA-1": "ATAM R-5, R-6 (RT-2)", "SQA-2": "ATAM R-6–R-9 (RT-2)", "SQA-3": "ATAM R-9, R-10 (RT-3)",
    "OQA-1": "ATAM R-11 (RT-3)", "SCQA-1": "ATAM R-12 (RT-1)", "DQA-1": "ATAM R-13, N-5 (RT-3)",
    "MQA-1": "as-built AA-9; ATAM N-3", "INQA-1": "as-built AA-3; ATAM N-4",
    "PQA-1": "not analysed — no load data", "PQA-2": "not analysed — no utilisation data",
}

CHANGELOG = [
    "| 2026-10-09 | `/atam` (lightweight) write-back: AQA-1, AQA-2, RQA-1, SQA-1, SQA-2, SQA-3, OQA-1, SCQA-1, DQA-1 → at risk (R-1–R-13); MQA-1, INQA-1 → addressed (N-3, N-4); BG-2, BG-4 → at risk (RT-1–RT-4) |",
    "| 2026-10-09 | scenario diagrams redrawn in PlantUML (UML palette); Mermaid sources removed |",
]

NAV_EXTRA = " · [ATAM report](../atam/atam-report.md) · [docs](../docs/README.md)"
