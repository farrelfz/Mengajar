# SCORING MODEL & EXPLAINABILITY TRACE
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Dimension Weighting Architecture
The composite score is computed by weighted aggregation of dimensional averages:

$$\text{Overall Score} = \frac{\sum_{d \in D} S_d \cdot W_d}{\sum_{d \in D} W_d}$$

- `SEMANTIC_CORRECTNESS`: $W = 1.5$
- `PEDAGOGICAL_ALIGNMENT`: $W = 1.5$
- `STRUCTURAL_COHERENCE`: $W = 1.3$
- `INFORMATION_DENSITY`: $W = 1.2$
- `FORMAT_INTEGRITY`: $W = 1.4$
- `REDUNDANCY`: $W = 1.0$
- `VISUAL_APPROPRIATENESS`: $W = 1.0$

### 2. Quality Gate Arbitration Matrix
| Condition | QualityGateDecision | can_proceed |
|---|---|---|
| Critical Finding present | `FAIL` | `False` |
| Error Finding present OR score $< 0.70$ | `NEEDS_REFINEMENT` | `False` |
| Warning Finding present OR score $< 0.85$ | `PASS_WITH_WARNINGS` | `True` |
| 0 warnings/errors AND score $\ge 0.85$ | `PASS` | `True` |

### 3. EvaluationTrace
Every `QualityReport` includes an `EvaluationTrace` containing:
- Execution records of every evaluator
- Progressive lifecycle stage evaluation status
- Human-readable score computation logs
