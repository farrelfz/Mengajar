# ACCEPTANCE POLICY & IMPROVEMENT JUDGE
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Decision Matrix (`app/refinement/decision.py`)

| Condition | Decision | Rationale |
|---|---|---|
| Invariant Violation | `REJECT` | Never sacrifice core concepts, objectives, or format. |
| New Regressions | `REJECT` | Patches must not introduce new flaws. |
| Meaningful Gain + 0 Regressions | `ACCEPT` | Proven genuine improvement. |
| $\Delta < 0.005$ & 0 Resolved Findings | `STOP_NO_IMPROVEMENT` | Plateau reached. |
