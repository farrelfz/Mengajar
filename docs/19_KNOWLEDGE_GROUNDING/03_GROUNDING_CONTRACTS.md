# GROUNDING CONTRACTS & DATA MODELS
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Authoritative Enums (`app/grounding/contracts.py`)
- `KnowledgeSourceType`: `LOCAL_DOCUMENT`, `STRUCTURED_DATASET`, `ACADEMIC_PAPER`, `TEXTBOOK`, `INTERNAL_KNOWLEDGE`, `VECTOR_STORE`, `WEB_SOURCE`.
- `SourceAuthority`: `PRIMARY`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.
- `EvidenceType`: `DIRECT_STATEMENT`, `DEFINITION`, `EXPLANATION`, `DATA_POINT`, `EXPERIMENT_RESULT`, `DERIVATION`, `EXAMPLE`, `STATISTICAL_RESULT`, `METHODOLOGY`, `THEORETICAL_MODEL`.
- `ClaimType`: `FACTUAL`, `DEFINITIONAL`, `CAUSAL`, `QUANTITATIVE`, `PROCEDURAL`, `INTERPRETIVE`, `PEDAGOGICAL`, `COMPARATIVE`.
- `SupportRelation`: `SUPPORTS`, `PARTIALLY_SUPPORTS`, `CONTRADICTS`, `RELATED`, `INSUFFICIENT`, `UNKNOWN`.
- `GroundingStatus`: `GROUNDED`, `PARTIALLY_GROUNDED`, `UNGROUNDED`, `CONTRADICTED`, `NOT_REQUIRED`.
- `FreshnessStatus`: `CURRENT`, `STALE`, `UNKNOWN`, `TIME_INSENSITIVE`.

---

### 2. Primary Data Models
- `Evidence`: Atomic snippet with `evidence_id`, `source_id`, `authority`, `relevance_score`, and `freshness`.
- `Claim`: Asserted statement with `claim_id`, `content`, `claim_type`, `importance`, and `grounding_status`.
- `ClaimEvidenceLink`: Relation, support score, similarity, and explanation.
- `CitationProvenance`: Machine-readable path (Claim $\to$ Evidence $\to$ Chunk $\to$ Source).
- `GroundingScore`: Multidimensional score (`coverage`, `support_strength`, `authority`, `freshness`, `consistency`, `overall`).
- `GroundingReport`: Full diagnostic output.
