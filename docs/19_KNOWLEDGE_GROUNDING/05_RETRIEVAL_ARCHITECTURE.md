# RETRIEVAL ARCHITECTURE & DEDUPLICATION
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Retrieval Engine (`app/grounding/retrieval.py`)
Federates queries across registered providers:
1. Queries each provider with `KnowledgeQuery`.
2. Deduplicates candidates by source and normalized content.
3. Normalizes candidate relevance scores.
4. Deterministically sorts and returns top-K `RetrievedEvidence` items.
