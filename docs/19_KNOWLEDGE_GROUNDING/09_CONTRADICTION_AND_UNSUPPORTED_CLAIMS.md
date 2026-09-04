# CONTRADICTION & UNSUPPORTED CLAIM DETECTION
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Conservative Contradiction Detection (`ContradictionDetector`)
Detects factual collisions:
- **Numeric Collisions**: Value clashes in physical constants or variables (e.g. $g = 9.8\text{ m/s}^2$ vs $12\text{ m/s}^2$).
- **Direct Negations**: "Causes" vs "does not cause", "depends on" vs "does not depend on".
- Conservative rule: Missing evidence produces `INSUFFICIENT`, not false contradiction.

### 2. Unsupported Claim Detector (`UnsupportedClaimDetector`)
Flags foundational claims that lack evidence support while exempting decorative rhetorical sentences.
