# PHASE 3C.1 — FORENSIC ARCHITECTURE AUDIT: ADVERSARIAL REPAIR SAFETY & HARDENING
## Universal Document Intelligence System V5
### Forensic Investigation of Repair Mutation Surfaces, Hardcoded Primitives, and Safety Invariants

---

## 1. Executive Summary

Phase 3C.1 establishes rigorous safety boundaries around the automated repair engine implemented in Phase 3C (`app/quality/repair/`).
While the repair engine is capable of mitigating defects across all 4 artifact formats, it introduces a critical hazard: **numerical quality improvement accompanied by silent semantic degradation, excessive structural churn, or broken traceability**.

This forensic audit analyzes:
1. Canonical Phase Ownership and Naming Normalization.
2. The complete Mutation Surface across all 4 artifact types.
3. The distribution of visual literals and design system integration points.
4. The call graphs linking Quality Authority, Causal Attribution, Repair Engine, Design System, and Renderers.

---

## 2. Canonical Phase Ownership & Naming Normalization

- **Phase 3B**: Failure Correlation & Root Cause Attribution (`app/quality/causal/` and `app/quality/repair/root_cause.py`).
- **Phase 3B.0**: Universal Design System & Asset Library (`app/design_system/`).
- **Phase 3C**: Targeted Repair Strategy Engine (`app/quality/repair/`).
- **Phase 3C.1 (THIS PHASE)**: Adversarial Repair Safety & Design System Integration Hardening.
- **Phase 3D (FUTURE)**: Production Pipeline Convergence Orchestration.

Roadmap documented in `docs/canonical_architecture_roadmap.md`.

---

## 3. Mutation Surface Audit

| Mutation Surface | Mutating Module | Allowed Repair Strategies | Risk Level | Rollback Mechanism | Traceability Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Slide Count / Granularity** | `presentation.py` | `PresentationDensitySplitStrategy` | MEDIUM | `SnapshotManager` deepcopy | Preserved: source refs split across slides |
| **Slide Layout Family** | `presentation.py` | `PresentationLayoutRemapStrategy` | LOW | `SnapshotManager` deepcopy | None: source refs unchanged |
| **Slide Container Padding** | `presentation.py` | `PresentationPaddingAdjustmentStrategy` | LOW | `SnapshotManager` deepcopy | None: layout density token update |
| **Handout Section Distribution** | `handout.py` | `HandoutPaginationStrategy` | LOW | `SnapshotManager` deepcopy | None: sections redistributed across pages |
| **Handout Section Level** | `handout.py` | `HandoutHierarchyRepairStrategy` | LOW | `SnapshotManager` deepcopy | None: heading levels normalized monotonically |
| **Worksheet Answer Withholding** | `worksheet.py` | `WorksheetAntiSpoilingRepairStrategy` | CRITICAL | `SnapshotManager` deepcopy | Must preserve source IDs while purging leaked answer text |
| **Worksheet Inquiry Flow** | `worksheet.py` | `WorksheetInquirySequenceStrategy` | HIGH | `SnapshotManager` deepcopy | Phase order re-aligned to inquiry standard |
| **Worksheet Response Space** | `worksheet.py` | `WorksheetWorkspaceExpansionStrategy` | LOW | `SnapshotManager` deepcopy | None: height parameter increased |
| **Scientific Claim Downgrade** | `scientific.py` | `ScientificClaimDowngradeStrategy` | HIGH | `SnapshotManager` deepcopy | Preserved: unproven assertion hedged; **ZERO fabrication** |
| **Scientific BAB Chapter Order** | `scientific.py` | `ScientificMethodologyOrderStrategy` | MEDIUM | `SnapshotManager` deepcopy | Chapter order aligned to BAB I–V standard |
| **Scientific Evidence Linking** | `scientific.py` | `ScientificEvidenceMappingStrategy` | HIGH | `SnapshotManager` deepcopy | Grounded linking to verified evidence IDs only |

---

## 4. Hardcoded Visual Values Audit

| Subsystem / File | Literal Example | Classification | Remediation Strategy |
| :--- | :--- | :--- | :--- |
| `app/rendering/html/templates/document.html` | `13.333in`, `210mm`, `#0f172a`, `32pt` | **3. Design System Violation** | Bind via `var(--ds-*, fallback)` using `HtmlDesignAdapter` |
| `app/rendering/reportlab/renderer.py` | `#34495e`, `#3498db`, `#e74c3c` | **3. Design System Violation** | Bind via `DesignAwareStyleFactory` using `ReportLabDesignAdapter` |
| `app/integration/render_execution/worksheet_executor.py` | `INQUIRY_BADGE_COLORS` hex dict | **3. Design System Violation** | Resolve via `RepairDesignContext` from educational theme tokens |
| `app/design_system/contracts/geometry.py` | `72.0 pt/in`, `25.4 mm/in` | **4. Unavoidable Physical Conversion** | Retain in canonical unit conversion utility |
| `app/design_system/contracts/tokens.py` | Level 1 raw constants | **1. Legitimate Renderer Primitive** | Foundational raw token definitions |
| `app/integration/render_execution/handout_executor.py` | `sections_per_page = 2` | **2. Legacy Compatibility Value** | Safe layout pagination heuristic |

---

## 5. Complete Subsystem Call Graph

```
UnifiedQualityDecision (from UnifiedQualityAuthority)
  ↓
FailureCorrelationEngine (clusters signals)
  ↓
DeterministicRootCauseAnalyzer (hypothesizes root causes)
  ↓
MinimalInterventionRepairPlanner (evaluates mutation scope & utility)
  ↓ (Gated by RepairMutationBudget)
RepairDesignContext (resolves canonical tokens exclusively)
  ↓
SnapshotManager (records SHA-256 pre-state snapshot)
  ↓
RepairStrategy.apply_repair() (executes atomic mutation)
  ↓
ArtifactDriftAnalyzer (measures semantic, structural, traceability drift)
  ↓
SafetyInvariants.check_all() (checks non-negotiable invariants)
  ↓
RegressionGuard (evaluates score delta & new blockers)
  ↓
Commit (advance state) OR Rollback (restore snapshot)
  ↓
UnifiedQualityAuthority Re-evaluation
```

---

## 6. Required Phase 3C.1 Implementations

1. `app/quality/repair/mutation_contract.py`: `RepairMutationScope` (Levels 0-6), `RepairMutationRisk`, `RepairMutation`.
2. `app/quality/repair/mutation_budget.py`: Artifact-specific `RepairMutationBudget` preventing over-mutation.
3. `app/quality/repair/drift_analyzer.py`: `ArtifactDriftAnalyzer` and `ArtifactDriftReport`.
4. `app/quality/repair/planner.py`: `MinimalInterventionRepairPlanner` with utility ranking formula.
5. `app/quality/repair/repair_design_context.py`: `RepairDesignContext` bridging design tokens.
6. `app/design_system/validation/parity_validator.py`: `CrossRendererParityValidator`.
7. `app/quality/repair/safety_invariants.py`: Global and format-specific non-negotiable safety rules.
8. `app/quality/repair/transaction.py`: `RepairTransactionManager` and `RepairTransactionRecord`.
9. Adversarial test suite covering Scenarios A through J.
