# CLAIM EXTRACTION ARCHITECTURE
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Heuristic Claim Extractor (`app/grounding/claims.py`)
Deterministic parser identifying atomic assertions across semantic materials:
- `DEFINITIONAL`: Concept formal definitions ($X \text{ is defined as } Y$).
- `QUANTITATIVE`: Equations, formulas, and numeric values ($\tau = rF\sin\theta$).
- `CAUSAL`: Cause-effect and functional dependencies ($X \text{ increases when } Y \text{ increases}$).
- `FACTUAL`: Empirical statements and observations.
- `PEDAGOGICAL`: Decorative rhetorical prompts (flagged `requires_grounding=False`).
