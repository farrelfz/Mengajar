# GENERATIVE CRITIC SUBSYSTEM ARCHITECTURE
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Conceptual Flow
The Generative Critic (`app/critic/`) acts as an analytical intelligence layer:

```text
INPUT MATERIAL / ARTIFACTS
      │
      ▼
CRITIQUE CONTEXT BUILDER (CritiqueContext)
      ├── Level A/B/C Blueprint Context
      ├── Abstract Layout (DocumentComposition)
      ├── Quality Diagnostics (QualityReport - Optional)
      ├── Director Journey (LearningJourney - Optional)
      └── Target Format & Audience Context
      │
      ▼
MULTI-PERSPECTIVE CRITIC PANEL (CriticPanel)
      ├── Structural Critic
      ├── Semantic Critic
      ├── Pedagogical Critic
      ├── Cognitive Load Critic
      ├── Narrative Critic
      ├── Visual Communication Critic
      ├── Scientific Rigor Critic
      ├── Audience Critic
      ├── Capability Selection Critic
      └── Redundancy Critic
      │
      ▼
CRITIQUE FINDINGS & SYNTHESIS (CritiqueSynthesizer)
      ├── Merges Overlapping Findings
      ├── Detects Multi-Perspective Consensus Agreements
      └── Detects Genuine Pedagogical vs Cognitive Conflicts
      │
      ▼
PRIORITIZATION & RECOMMENDATIONS
      ├── CritiquePrioritizer (BLOCKER, CRITICAL, HIGH, MEDIUM, LOW)
      └── RecommendationGenerator (Actionable, Non-Destructive Directions)
      │
      ▼
EXPLAINABLE CRITIQUE REPORT (CritiqueReport)
```

---

### 2. Core Architectural Invariants
- **Non-Destructive**: Batch 16 never mutates documents; it emits structured findings and directional recommendations for Batch 17 Refinement.
- **Fault-Isolated**: Critic execution in `CriticPanel` isolates exceptions so that individual critic failures do not crash the entire panel.
- **Graceful Context Degradation**: Critics run with partial evidence (e.g. Blueprint only) when full compositions or rendered PDFs are unavailable.
