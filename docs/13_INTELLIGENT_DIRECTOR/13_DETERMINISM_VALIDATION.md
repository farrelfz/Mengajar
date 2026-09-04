# 13 — Determinism Validation

## 3-Pass Determinism Verification

Running the exact same `MaterialRequest` through the Director 3 consecutive times yields:
- Exact same selected `MaterialStrategyType`.
- Exact same sequence of `LearningStage` elements.
- Exact same sequence of `CapabilityRequirement` items.
- Exact same page count and physical layout in the final PDF artifact.
