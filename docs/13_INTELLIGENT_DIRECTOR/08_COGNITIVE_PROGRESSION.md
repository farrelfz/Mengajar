# 08 — Cognitive Progression & Misconceptions

## Bloom's Cognitive Progression Model

```
RECOGNIZE (Rank 1)
  ↓
UNDERSTAND (Rank 2)
  ↓
APPLY (Rank 3)
  ↓
ANALYZE (Rank 4)
  ↓
EVALUATE (Rank 5)
  ↓
CREATE (Rank 6)
```

`CognitiveProgressionPolicy` guards against cognitive overload:
- For `NOVICE` learners, immediate entry into `EVALUATE` or `CREATE` without scaffolding triggers a diagnostic warning.
- Abrupt jumps (>3 levels between adjacent stages) are flagged.

---

## Misconception Engine
- Evaluates topics for high-value student fallacies (e.g. Torque, Gravity, Correlation vs Causation).
- Integrates counterexample contrast payloads when `MISCONCEPTION_CORRECTION` strategy is active.
