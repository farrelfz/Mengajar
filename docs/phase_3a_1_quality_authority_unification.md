# Phase 3A.1 — Quality Authority Unification & Forensic Consolidation
## Universal Document Intelligence System V5

---

## 1. Executive Summary

Phase 3A.1 establishes the **UnifiedQualityAuthority** as the single canonical arbiter of document quality, failure normalization, causal attribution, and export decisions across all four supported document formats:
1. **PRESENTATION** (16:9 widescreen classroom slide decks)
2. **HANDOUT** (A4 continuous educational reading materials)
3. **WORKSHEET / LKS** (A4 student activity and scientific investigation sheets)
4. **SCIENTIFIC_DOCUMENT / KTI** (A4 Indonesian KTI / academic research papers)

Prior to this phase, quality evaluation was fragmented across disconnected evaluators:
- Legacy heuristics in `app/quality/` (`DensityEvaluator`, `PedagogicalEvaluator`, `StructuralEvaluator`, `FormatEvaluator`, `RedundancyEvaluator`, `SemanticEvaluator`)
- Presentation-specific gates in `app/presentation/quality/presentation_quality_gate.py` and `app/presentation/visual_qa.py`
- Phase 2B structural fidelity checks in `app/quality/artifact_fidelity/`
- Phase 2C adversarial calibration scoring in `app/quality/calibration/`
- Phase 3A physical rendered PDF geometry checking in `app/quality/rendered/`

Phase 3A.1 unifies these diagnostic engines under a single authoritative decision hierarchy without destroying specialized domain evaluators. Evaluators are transitioned into **Signal Providers**, emitting canonical `QualitySignal` instances that are normalized, correlated, deduplicated, and arbitrated exclusively by the `UnifiedQualityAuthority`.

---

## 2. Four Orthogonal Truth Layers

The system's quality model is structured into four non-overlapping, strictly orthogonal layers of truth:

```
+-----------------------------------------------------------------------------------+
|                           UnifiedQualityAuthority                                 |
+-----------------------------------------------------------------------------------+
       ▲                           ▲                         ▲                    ▲
       │                           │                         │                    │
+---------------+         +-----------------+       +----------------+    +---------------+
|    Layer 1    |         |     Layer 2     |       |    Layer 3     |    |    Layer 4    |
|   SEMANTIC    |         |    ARTIFACT     |       |    ARTIFACT    |    |   PHYSICAL    |
|  INTEGRITY    |         |    FIDELITY     |       |    QUALITY     |    |RENDERED QUAL. |
+---------------+         +-----------------+       +----------------+    +---------------+
| - Knowledge   |         | - Retention     |       | - Density      |    | - Geometry    |
|   Grounding   |         | - Blueprint     |       | - Narrative    |    | - Text Bounds |
| - Veracity    |         |   Mapping       |       | - Pedagogy     |    | - Collisions  |
| - Non-        |         | - Slot          |       | - Inquiry Arc  |    | - Font Sizes  |
|   Fabrication |         |   Resolution    |       | - Rigor        |    | - Viewport    |
+---------------+         +-----------------+       +----------------+    +---------------+
```

### Orthogonality Invariants:
1. **High Fidelity $\neq$ High Quality**: An artifact that retains 100% of source elements can still suffer severe physical text collisions or cognitive overload.
2. **Clean Render $\neq$ Truthful Semantics**: A visually flawless document with perfect typographic spacing can still contain completely unsupported claims or fabricated citations.
3. **Flawless Layout $\neq$ Valid Pedagogy**: A worksheet with ideal bounding box coordinates can leak the solution inside the hypothesis question, violating anti-spoiling invariants.
4. **Authority Separation**: Individual evaluators only report symptoms; only `UnifiedQualityAuthority` issues lifecycle verdicts (`EXPORT_APPROVED`, `EXPORT_APPROVED_WITH_WARNINGS`, `REPAIR_REQUIRED`, `RENDER_REPAIR_REQUIRED`, `SEMANTIC_REPAIR_REQUIRED`, `MANUAL_REVIEW_REQUIRED`, `BLOCKED`).

---

## 3. Evaluator Classification & Provider Architecture

All existing evaluators in the repository are classified into the following architectural roles:

| Component | Historical Location | Phase 3A.1 Classification | Canonical Ingest Adapter |
|---|---|---|---|
| `MasterRenderedQualityEngine` | `app/quality/rendered/` | SPECIALIZED_PROVIDER (Layer 4) | `RenderedQualitySignalAdapter` |
| `PDFGeometryInspector` | `app/quality/rendered/` | SPECIALIZED_PROVIDER (Layer 4) | `RenderedQualitySignalAdapter` |
| `CalibratedQualityEngine` | `app/quality/calibration/` | SPECIALIZED_PROVIDER (Layer 3) | `CalibrationSignalAdapter` |
| `MasterQualityScoringEngine` | `app/quality/calibration/` | SPECIALIZED_PROVIDER (Layer 3) | `CalibrationSignalAdapter` |
| `UnifiedFidelityValidator` | `app/quality/artifact_fidelity/` | SPECIALIZED_PROVIDER (Layer 2) | `FidelitySignalAdapter` |
| `PresentationQualityGate` | `app/presentation/quality/` | SPECIALIZED_PROVIDER (Layer 3) | `PresentationQualitySignalAdapter` |
| `VisualQA` | `app/presentation/` | SPECIALIZED_PROVIDER (Layer 4) | `PresentationQualitySignalAdapter` |
| `QualityEvaluationEngine` | `app/quality/engine.py` | LEGACY_COMPATIBILITY | `LegacyDocumentQualitySignalAdapter` |
| Legacy Heuristic Evaluators (6) | `app/quality/*_evaluator.py` | SPECIALIZED_PROVIDER | `LegacyDocumentQualitySignalAdapter` |
| `UnifiedQualityAuthority` | `app/quality/authority/` | **CANONICAL_AUTHORITY** | Single Master Arbiter |

---

## 4. Canonical Quality Contracts

All contracts are defined as immutable Pydantic v2 models in `app/quality/contracts/`:

### 4.1. `QualitySignal` (`signals.py`)
Standardized symptom emitted by any evaluator:
- `signal_id: str`: Unique identifier (`sig_xxxxxxxx`)
- `artifact_type: str`: Target document type
- `domain: QualityDomain`: `SEMANTIC`, `FIDELITY`, `ARTIFACT`, or `RENDERED`
- `dimension: str`: Target quality dimension
- `metric_name / canonical_code: str`: Normalized failure code
- `raw_value: Any`: Empirical measurement (e.g. `6.5` pt, `3400` chars, `0.42`)
- `normalized_value: float`: Calibrated score in $[0.0, 1.0]$
- `threshold: Optional[float]`: Expected boundary threshold
- `measurement: Optional[str]`: Measurement name or unit
- `severity: SignalSeverity`: `INFO`, `WARNING`, `MINOR`, `MAJOR`, `ERROR`, `CRITICAL`, `BLOCKING`
- `confidence: SignalConfidence`: `DEFINITIVE`, `HIGH`, `MEDIUM`, `LOW`
- `location: QualityLocation`: Spatial coordinates (`slide_index`, `page_index`, `element_id`, `bounding_box`)
- `evidence: Tuple[EvidenceReference, ...]`: Empirical evidence references
- `provenance: Dict[str, Any]`: Original raw evaluator metadata

### 4.2. `QualityFinding` & `FindingCluster` (`findings.py`)
Normalized actionable defect representation:
- `QualityFinding`: Backward-compatible with legacy fields (`id`, `finding`, `affected_artifact`, `score_impact`, `evidence`) and canonical fields (`finding_id`, `failure_code`, `domain`, `severity`, `is_blocking()`).
- `FindingCluster`: Correlated group of co-occurring defects at the same page/element, designating a primary `canonical_finding`, list of `correlated_findings`, and contributing signals to suppress double-counting.

### 4.3. `CanonicalQualityDimension` (`dimensions.py`)
The 15 canonical quality dimensions spanning all four layers:
- **Semantic Integrity**: `SEMANTIC_GROUNDING`, `CLAIM_VERACITY`, `KNOWLEDGE_TRACEABILITY`
- **Artifact Fidelity**: `BLUEPRINT_FIDELITY`, `ELEMENT_SURVIVAL`, `CONTRACT_COMPLIANCE`
- **Artifact Quality**: `NARRATIVE_FLOW`, `COGNITIVE_LOAD`, `INQUIRY_STRUCTURE`, `SCIENTIFIC_RIGOR`, `STYLE_DESIGN`
- **Physical Rendered Quality**: `READABILITY`, `PHYSICAL_GEOMETRY`, `VISUAL_DENSITY`, `PAGE_BALANCE`

### 4.4. `UnifiedQualityDecision` & `ExportDecision` (`decisions.py`)
Authoritative lifecycle verdict:
- `ExportDecision.EXPORT_APPROVED`
- `ExportDecision.EXPORT_APPROVED_WITH_WARNINGS`
- `ExportDecision.REPAIR_REQUIRED`
- `ExportDecision.RENDER_REPAIR_REQUIRED`
- `ExportDecision.SEMANTIC_REPAIR_REQUIRED`
- `ExportDecision.MANUAL_REVIEW_REQUIRED`
- `ExportDecision.BLOCKED`

### 4.5. `UnifiedQualityReport` (`authority.py`)
Master diagnostic report encapsulating:
- `decision: ExportDecision`
- `can_export: bool`
- `repair_required: bool`
- `overall_quality_score: float`
- `domain_scores: Dict[str, float]` (scores for each of the 4 truth layers)
- `semantic_integrity`, `artifact_fidelity`, `artifact_quality`, `rendered_quality` (layer breakdowns)
- `dimension_scores: Dict[str, QualityDimensionScore]`
- `findings: Tuple[QualityFinding, ...]`
- `finding_clusters: Tuple[FindingCluster, ...]`
- `causal_diagnoses: Tuple[Dict[str, Any], ...]`
- `provenance: QualityProvenanceGraph`
- `hard_blockers: Tuple[str, ...]`
- `warnings: Tuple[str, ...]`, `summary: str`

---

## 5. Failure Taxonomy Mapping

The taxonomy mapping module (`app/quality/contracts/taxonomy_mapping.py`) bridges legacy, rendered, calibration, and fidelity codes to canonical codes:

| Source Code | Originating Layer | Canonical Code | Canonical Domain | Canonical Dimension |
|---|---|---|---|---|
| `TEXT_CLIPPING` | Phase 3A Render | `TEXT_CLIPPING` | `RENDERED` | `PHYSICAL_GEOMETRY` |
| `OVERLAPPING_CONTENT` | Phase 3A Render | `ELEMENT_COLLISION` | `RENDERED` | `PHYSICAL_GEOMETRY` |
| `TINY_TEXT` | Phase 3A Render | `FONT_TOO_SMALL` | `RENDERED` | `READABILITY` |
| `VIEWPORT_BREACH` | Phase 3A Render | `MARGIN_VIOLATION` | `RENDERED` | `PHYSICAL_GEOMETRY` |
| `DROPPED_SOURCE_UNITS` | Phase 2B Fidelity | `TRACEABILITY_BREAK` | `FIDELITY` | `KNOWLEDGE_TRACEABILITY` |
| `UNRESOLVED_SLOTS` | Phase 2B Fidelity | `UNRESOLVED_SLOT` | `FIDELITY` | `BLUEPRINT_FIDELITY` |
| `EXCESSIVE_DENSITY` | Phase 2C Presentation | `COGNITIVE_OVERLOAD` | `ARTIFACT` | `COGNITIVE_LOAD` |
| `FIVE_CONSECUTIVE_IDENTICAL_LAYOUT` | Phase 2C Presentation | `LAYOUT_MONOTONY` | `ARTIFACT` | `STYLE_DESIGN` |
| `EXTREME_DENSE_PAGE` | Phase 2C Handout | `COGNITIVE_OVERLOAD` | `ARTIFACT` | `COGNITIVE_LOAD` |
| `HEADING_HIERARCHY_INVERSION` | Phase 2C Handout | `STRUCTURAL_HIERARCHY_INVERSION` | `ARTIFACT` | `SCIENTIFIC_RIGOR` |
| `ANSWER_LEAKED_INSIDE_QUESTION` | Phase 2C Worksheet | `ANTI_SPOILING_BREACH` | `ARTIFACT` | `INQUIRY_STRUCTURE` |
| `EXPLANATION_LEAKED_BEFORE_PREDICTION` | Phase 2C Worksheet | `ANTI_SPOILING_BREACH` | `ARTIFACT` | `INQUIRY_STRUCTURE` |
| `WORKSPACE_OVERLAPS_CONTENT` | Phase 2C Worksheet | `ELEMENT_COLLISION` | `RENDERED` | `PHYSICAL_GEOMETRY` |
| `CLAIM_WITHOUT_EVIDENCE` | Phase 2C Scientific | `UNSUPPORTED_SCIENTIFIC_CLAIM` | `SEMANTIC` | `CLAIM_VERACITY` |
| `EVIDENCE_ATTACHED_TO_WRONG_CLAIM` | Phase 2C Scientific | `MISATTRIBUTED_EVIDENCE` | `SEMANTIC` | `CLAIM_VERACITY` |
| `FABRICATED_CITATION_MARKER` | Phase 2C Scientific | `FABRICATED_CITATION` | `SEMANTIC` | `SEMANTIC_GROUNDING` |
| `BAB_HIERARCHY_INVERSION` | Phase 2C Scientific | `STRUCTURAL_HIERARCHY_INVERSION` | `ARTIFACT` | `SCIENTIFIC_RIGOR` |

---

## 6. Format-Specific Quality Profiles & Hard Blockers

Each document format has calibrated hard blockers and warning tolerances defined in `app/quality/authority/profiles.py`:

| Artifact Format | Hard Blockers (Zero Tolerance) | Warning Tolerance | Min Score | Dominant Weights |
|---|---|:---:|:---:|---|
| **PRESENTATION** | `TEXT_CLIPPING`, `ELEMENT_COLLISION`, `FONT_TOO_SMALL` (<12pt), `FIVE_CONSECUTIVE_IDENTICAL_LAYOUT`, `COGNITIVE_OVERLOAD`, `TRACEABILITY_BREAK` | 3 | 0.85 | Geometry (1.5), Readability (1.3), Cognitive Load (1.2) |
| **HANDOUT** | `FONT_TOO_SMALL` (<8pt), `EXTREME_DENSE_PAGE` (>3000 chars), `STRUCTURAL_HIERARCHY_INVERSION`, `ACCIDENTAL_PAGE`, `TRACEABILITY_BREAK` | 3 | 0.85 | Readability (1.4), Narrative Flow (1.3), Page Balance (1.2) |
| **WORKSHEET** | `ANTI_SPOILING_BREACH` (Answer Leaks, Observation Prefilled), `ELEMENT_COLLISION` (`WORKSPACE_OVERLAPS_CONTENT`), `INQUIRY_ARC_BROKEN`, `TRACEABILITY_BREAK` | 2 | 0.85 | Inquiry Structure (1.8), Geometry (1.4), Narrative Flow (1.2) |
| **SCIENTIFIC_DOCUMENT** | `UNSUPPORTED_SCIENTIFIC_CLAIM` (`CLAIM_WITHOUT_EVIDENCE`), `MISATTRIBUTED_EVIDENCE`, `FABRICATED_CITATION`, `CONTRADICTORY_CLAIMS`, `BAB_HIERARCHY_INVERSION`, `TRACEABILITY_BREAK` | 2 | 0.88 | Claim Veracity (2.0), Scientific Rigor (1.8), Grounding (1.5) |

---

## 7. Finding Correlation & Double-Counting Prevention

The `FindingCorrelationEngine` (`app/quality/authority/correlation.py`) prevents unfair score degradation when a single defect cascades across multiple layers:
1. **Spatial & Causal Clustering**: Co-occurring signals on the same page or slide (e.g. `COGNITIVE_OVERLOAD` causing `TEXT_CLIPPING`) are grouped into a `FindingCluster`.
2. **Root Cause Selection**: The dominant signal (highest severity or known causal root) is promoted to the canonical finding.
3. **Penalty Deduction**: Rather than summing multiple $-0.40$ penalties for the same physical issue, the cluster deduplicates deductions to avoid double-penalizing both semantic density and physical layout geometry.

---

## 8. Degeneracy Detection Safeguard

The `QualityDimensionNormalizer` includes deterministic anomaly detection to safeguard against corrupt evaluators:
1. **Universal One ($1.0$)**: Flags when an evaluator emits defects, but upstream scoring blindly outputs $1.0$.
2. **Zero Variance**: Flags when all 15 dimensions report identical scores despite active defect findings.
3. **Escalation**: Any detected degeneracy routes the decision directly to `MANUAL_REVIEW_REQUIRED`.

---

## 9. Verification & Test Evidence

The unification architecture is thoroughly verified by 305 passing unit and integration tests with **zero regressions**:

### 9.1. Unit Test Suite (`tests/unit/quality/test_quality_authority_contract.py`)
- **30 / 30 tests PASSED (0.45s)**
- Covers signal validation, raw metric preservation, directional normalization, profile registries, finding clustering, penalty suppression, taxonomy mapping, format-specific hard blockers, degeneracy detection, warning tolerances, provenance graph completeness, JSON round-trip immutability, zero-AI determinism, and all 5 signal provider adapters.

### 9.2. Integration Test Suite (`tests/integration/test_unified_quality_authority.py`)
- **12 / 12 tests PASSED (0.45s)**
- Covers end-to-end evaluation for Presentation, Handout, Worksheet, and Scientific Document.
- Covers Adversarial Conflict Scenarios A through G:
  - **Scenario A (High Fidelity + Low Physical)**: High element retention blocked due to text clipping.
  - **Scenario B (Clean Render + Semantic Fabrication)**: Flawless geometry blocked due to unsupported claim.
  - **Scenario C (Perfect Layout + Worksheet Answer Leak)**: Beautiful activity sheet blocked due to answer spoiling.
  - **Scenario D (Minor Warning Accumulation)**: Clean approval with warnings when within tolerance.
  - **Scenario E (Density + Clipping Correlation)**: Single cluster and suppressed double-penalty.
  - **Scenario F (Missing Rendered Inspection)**: Graceful evaluation using remaining 3 truth layers.
  - **Scenario G (Degeneracy Detection)**: Corrupt flat scoring routed to manual review.

### 9.3. Full Regression Benchmark
- **305 passed in 14.81s** across `tests/unit/quality/` and `tests/integration/`.

---

## 10. Architectural Handoff to Phase 3B

Phase 3A.1 successfully consolidates all quality authority into a unified, deterministic, explainable core. The architecture is fully prepared for Phase 3B (Targeted Repair Strategy Engine):
- `UnifiedQualityReport` provides structured `causal_diagnoses` and `finding_clusters`.
- Every finding specifies `repairability` and targeted `domain`.
- Decision outcomes (`RENDER_REPAIR_REQUIRED`, `SEMANTIC_REPAIR_REQUIRED`, `REPAIR_REQUIRED`) provide clear routing signals for automated repair planners without violating authority boundaries.
