# CLAIM-EVIDENCE LINKING
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Linking Logic (`app/grounding/linker.py`)
For each extracted claim:
1. Candidate evidences are ranked.
2. Contradiction and semantic overlap checks determine the `SupportRelation` (`SUPPORTS`, `PARTIALLY_SUPPORTS`, `CONTRADICTS`, `INSUFFICIENT`).
3. `ClaimEvidenceLink` records the formal link with machine-readable explanation.
