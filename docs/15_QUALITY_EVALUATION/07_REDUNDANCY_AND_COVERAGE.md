# REDUNDANCY EVALUATION & CONCEPT COVERAGE
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Redundancy Evaluator (`app/quality/redundancy_evaluator.py`)
Detects accidental verbatim duplicate blocks across pages while respecting intentional pedagogical reinforcement.

### 2. Evaluated Signals & Thresholds
- **Substantial Text Blocks**: Only text spans $> 50$ characters are evaluated to avoid flagging short labels (e.g. "Figure 1", "Example").
- **Cross-Page Deduplication**: Identifies identical text blocks appearing on subsequent pages.
- **Intentional Reinforcement Distinction**: Short summary recaps and retrieval questions are treated as valid pedagogical recurrence when tagged as distinct semantic roles in `PedagogicalBlueprint`.
