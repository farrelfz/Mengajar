# EVIDENCE RANKING
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Weighted Ranking Function (`app/grounding/evidence_ranker.py`)
$$\text{Score} = 0.40 \cdot \text{Relevance} + 0.25 \cdot \text{Authority} + 0.15 \cdot \text{Specificity} + 0.10 \cdot \text{Domain} + 0.10 \cdot \text{Freshness}$$

### 2. Properties
- Configurable, transparent weights without magic numbers.
- Authority boosts Primary and High-authority literature over lower tiers.
