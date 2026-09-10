# CANONICAL ARCHITECTURE ROADMAP
## Universal Document Intelligence System V5

This document establishes the canonical phase naming, semantic ownership, and boundaries across the document intelligence, quality, design, and repair subsystems.

---

## 1. Canonical Phase Ownership

```
PHASE 1: UNIVERSAL KNOWLEDGE INTELLIGENCE
├── Phase 1A: Universal Knowledge Extraction & Semantic Core
├── Phase 1B: Semantic Integrity & Adversarial Validation
├── Phase 1C: Artifact Transformation Contracts (Presentation, Handout, Worksheet, Scientific)
├── Phase 1C.1: Cross-Artifact Adversarial Validation
└── Phase 1D: Transformation Integration & Blueprint Bridge

PHASE 2: RENDERER CONTRACT ADAPTERS & FIDELITY
├── Phase 2A: Renderer Adapter Contracts (Legacy preservation)
├── Phase 2B: Controlled Renderer Execution (4 executor paths)
└── Phase 2C: Adversarial Artifact Quality Calibration

PHASE 3: QUALITY, DESIGN, ATTRIBUTION & REPAIR
├── Phase 3A: Rendered Output Physical Quality Intelligence
├── Phase 3A.1 / 3A.2: Unified Quality Authority & Canonical Quality Signal Contracts
├── Phase 3B: Failure Correlation & Root Cause Attribution (`app/quality/causal/`)
├── Phase 3B.0: Universal Design System & Asset Library (`app/design_system/`)
├── Phase 3C: Targeted Repair Strategy Engine (`app/quality/repair/`)
└── Phase 3C.1: Adversarial Repair Safety & Design System Integration Hardening (`app/quality/repair/`, THIS PHASE)

PHASE 3D (FUTURE): CONVERGENCE ORCHESTRATION & PRODUCTION REPAIR LIFECYCLE
└── Master production orchestrator closed-loop automated repair wiring.
```

---

## 2. Canonical Subsystem Ownership

| Subsystem | Primary Path | Authority / Role |
| :--- | :--- | :--- |
| **Knowledge Core** | `app/intelligence/` | Source grounding, extraction, semantic blueprints |
| **Quality Authority** | `app/quality/authority/` | **SOLE Level-0 Export Decision Authority** |
| **Causal Attribution** | `app/quality/causal/` | Correlating failure signals into root causes |
| **Design System** | `app/design_system/` | **SOLE Visual & Physical Parameter Authority** |
| **Repair Engine** | `app/quality/repair/` | Proposing & executing minimal transactional repairs |
| **Executors** | `app/integration/render_execution/` | Controlled physical rendering via Playwright & ReportLab |

---

## 3. Strict Boundary Rules

1. **Quality Authority Primacy**: Only `UnifiedQualityAuthority` makes export decisions (`EXPORT_APPROVED`, `REPAIR_REQUIRED`, `MANUAL_REVIEW_REQUIRED`, `REJECTED`).
2. **Design Authority Primacy**: No renderer or repair module may define independent visual constants; all must resolve through `DesignTokenResolver` and `DesignAwareRepairResolver`.
3. **Repair Subordination**: Repair strategies can only propose mutations; mutations are gated by `RepairMutationBudget`, `ArtifactDriftAnalyzer`, and `SafetyInvariants`.
4. **Offline Determinism**: 100% offline, reproducible, zero AI calls in quality, design, and repair kernels.
