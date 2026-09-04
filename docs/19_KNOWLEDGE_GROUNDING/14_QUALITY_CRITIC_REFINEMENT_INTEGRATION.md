# QUALITY, CRITIC & REFINEMENT INTEGRATION
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Inter-Subsystem Compatibility
- **Quality Engine (Batch 15)**: Receives `grounding_report.score` and unsupported claim counts as external signals.
- **Generative Critic (Batch 16)**: Surfaces warnings for claims lacking authoritative grounding.
- **Iterative Refinement (Batch 17)**: Prioritizes localized patches to replace contradicted claims or soften unsupported assertions.
