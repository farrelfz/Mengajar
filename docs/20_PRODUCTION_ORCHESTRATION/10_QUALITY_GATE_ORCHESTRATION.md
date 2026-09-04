# Quality Gate Orchestration

This document details Quality Gates, evaluation rules, and decisions.

## Gate Integration
The orchestrator checks gates after Grounding and Quality Evaluation stages:
- **Grounding Gate**: Checks for factual contradictions. Emits `BLOCK` (pipeline failure) if claims are contradicted. Emits `PASS` if grounding score >= 0.70, else `PASS_WITH_WARNINGS`.
- **Structural Quality Gate**: Evaluates page layouts. Emits `PASS` if layout score >= 0.75, else `REFINE` (diverts execution to critic and refinement loop).
- **Pedagogical Gate**: Evaluates instructional flow.

## Routing Logic
```text
                       Quality Stage
                             │
                             ▼
                    [ Gate Evaluation ]
                             ├── Score >= 0.75 ──► [ Render Stage ]
                             └── Score < 0.75  ──► [ Critic Stage ]
```
