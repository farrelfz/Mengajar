# EXPLAINABILITY MODEL & AUDIT TRACE
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Six-Part Explainability Invariant
Every `CritiqueFinding` emitted by any critic must answer:
1. **WHAT** was observed (`observation`)
2. **WHY** is it a weakness (`diagnosis`)
3. **WHY DOES IT MATTER** (`why_it_matters`)
4. **WHAT EVIDENCE SUPPORTS THIS** (`evidence` list with source and data)
5. **WHERE IS IT LOCATED** (`affected_locations`)
6. **HOW TO IMPROVE IT** (`improvement_direction`)

### 2. Execution Audit Trace (`CritiqueTrace`)
Records:
- `critics_executed`, `critics_skipped`, `critics_failed`
- `evidence_sources` consumed
- `reasoning_steps` executed
- `synthesis_steps` performed
- `conflicts_detected` and `agreements_detected` counts
