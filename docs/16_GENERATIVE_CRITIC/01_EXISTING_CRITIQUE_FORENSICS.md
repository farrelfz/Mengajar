# EXISTING CRITIQUE FORENSICS & REUSABLE INFRASTRUCTURE AUDIT
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Architectural Audit of Existing Systems
Before constructing `app/critic/`, a forensic audit of all existing subsystems in the repository was completed:

| Existing Layer | Responsibility | Batch 16 Reuse Opportunity | Duplication Risk | Decision |
|---|---|---|---|---|
| **Quality Engine (`app/quality/`)** | Numerical rule evaluation, geometric bounds, density limits, pass/fail gating | Diagnostic evidence source for critic context (`QualityReport`) | High if critic re-implements raw metric calculations | **Consume `QualityReport` as optional context; do not duplicate evaluators** |
| **Material Director (`app/director/`)** | Pedagogical choreography, learning journey stage sequencing | Instructional intent reference (`LearningJourney`) | Low | **Compare intended journey with actual composition** |
| **Capability Resolver (`app/capabilities/`)** | Resolution and selection of UI components from taxonomy | Component choice evaluation (`ResolutionTrace`) | Low | **Critique appropriateness of selected capability family** |
| **Blueprint System (`app/blueprints/`)** | Level A/B/C source semantic and instructional truth | Primary semantic and structural context | None | **Use `SemanticMaterialBlueprint` as primary context** |
| **Hybrid Renderer (`app/rendering/`)** | Physical PDF compilation via Playwright & headless browser | Physical artifact evidence (page count, render success) | None | **Optional visual render context** |
| **Format Engine (`app/formats/`)** | Geometric contracts and canvas specifications | Format constraint context (`ArtifactFormat`) | None | **Use format contracts as baseline for layout critique** |

---

### 2. Core Architectural Distinction: Quality Evaluation vs Generative Critic
- **Quality Engine (Batch 15)** answers: *"Does this artifact pass hard rules and measurable metrics?"* (Score: 0.0 to 1.0, Gate: PASS / FAIL).
- **Generative Critic (Batch 16)** answers: *"What is weak, WHY is it weak, what evidence supports that, and what actionable direction would make it better?"* (Explainable qualitative diagnostics across 10 perspectives).
