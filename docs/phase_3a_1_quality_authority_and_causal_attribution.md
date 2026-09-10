# Phase 3A.1: Quality Authority Consolidation & Causal Failure Attribution
**Universal Document Intelligence System V5**
*Status: Complete & Formally Verified*
*Timestamp: September 2026*

---

## 1. Executive Summary

Phase 3A.1 closes a critical architectural gap in the Universal Document Intelligence System V5.

While Phase 3A successfully established physical rendered-output inspection (detecting clipping, tiny fonts, element collisions, and blank pages directly from PDF display lists and pixel rasters), it exposed an existential danger: **the system could detect that something went wrong, but did not know what caused the failure or which architectural layer was authorized to repair it.**

Treating physical symptoms as root causes leads to catastrophic automated repairs:
- Naively enlarging a `TEXT_TOO_SMALL` font causes immediate `ELEMENT_COLLISION` and `TEXT_CLIPPING` when the underlying cause was an overloaded blueprint packing 8 items onto a single slide.
- Naively padding CSS when `WORKSHEET_QUIZ_COLLAPSE` is detected fails to fix the transformation strategy that selected 12 quiz questions without inquiry scaffolding.
- Naively rewriting claims when `SCIENTIFIC_CITATION_INVISIBLE` is detected fails to address the renderer omission that suppressed bibliographic anchors already present in the source metadata.

Phase 3A.1 creates a deterministic, evidence-based, AI-free causal attribution layer that:
1. **Consolidates Quality Authority**: Establishes `UnifiedQualityAuthority` as the single canonical decision-maker, reconciling semantic, structural, and physical rendered signals.
2. **Standardizes Failure Taxonomy**: Replaces fragmented enum definitions with a unified 7-category taxonomy (`CanonicalFailureCode`).
3. **Disentangles Symptoms from Root Causes**: Differentiates observed physical defects from underlying architectural origins across 10 pipeline layers.
4. **Clusters Correlated Failures**: Combines co-occurring defects on shared pages into unified `FailureCluster` instances.
5. **Models Structural Scope**: Evaluates defect spread across `LOCAL`, `CLUSTER`, `SYSTEMIC`, and `ARTIFACT_WIDE` tiers.
6. **Quantifies Causal Confidence**: Calibrates certainty into `HIGH`, `MEDIUM`, `LOW`, and `AMBIGUOUS` levels, strictly forbidding automatic repair when confidence is inconclusive.
7. **Enforces Repair Authority**: Dictates allowed repair classes (Classes A through G) and explicit forbidden repairs to protect document integrity.

---

## 2. Architectural Problem: Fragmented Quality Authorities

Prior to Phase 3A.1, quality evaluation was fragmented across three separate subsystems:
1. **Phase 2C (`CalibratedDecisionEngine`)**: Evaluated semantic completeness and blueprint quality against AST models, issuing `CalibratedQualityDecision`. Unaware of physical rendering bugs.
2. **Phase 3A (`MasterRenderedQualityEngine`)**: Inspected physical PDF display lists and pixel rasters, issuing `RenderedQualityDecision`. Unaware of semantic selection intent or blueprint constraints.
3. **Legacy Presentation QA (`PresentationQualityGate`)**: Validated slide DOM trees and narrative flows, issuing `GateStatus`.

```
[OLD MODEL: FRAGMENTED & BLIND]
Phase 2C Semantic Engine  ---> CalibratedQualityDecision (PASS)   \
Phase 3A Rendered Engine  ---> RenderedQualityDecision (BLOCKED)  ---> Conflicting Decisions!
Presentation Gate         ---> GateStatus (WARNING)               /
                                      │
                                      ▼
                               Naive Fix: Symptom -> Blind Repair (Causing Cascading Flaws)
```

Phase 3A.1 resolves this by funneling all upstream and downstream signals through a unified pipeline:

```
[NEW MODEL: UNIFIED CAUSAL ARCHITECTURE]
Raw Quality Signals (Fidelity, Semantic, Physical Display Lists, Pixels)
                               │
                               ▼
                   QualitySignalNormalizer
                               │
                               ▼
                      FailureNormalizer
                               │
                               ▼
                   CausalEvidenceCollector (Multi-Layer AST & Render Geometry)
                               │
                               ▼
                   CausalAttributionEngine
                   ├── ScopeAnalyzer (LOCAL, CLUSTER, SYSTEMIC, ARTIFACT_WIDE)
                   ├── FailureCorrelationEngine (Shared-page clustering)
                   ├── CausalConfidenceEstimator (HIGH, MEDIUM, LOW, AMBIGUOUS)
                   └── RepairAuthorityMatrix (Allowed vs Forbidden repairs)
                               │
                               ▼
                   UnifiedQualityAuthority (Single Canonical Decision Gate)
                               │
                               ▼
                   CausalQualityReporter (Actionable JSON & MD Reports)
```

---

## 3. Why Detection Is Not Causation

A quality detector answers: *"What symptom is physically broken?"*
A causal intelligence system answers: *"Why is it broken, who owns it, and what repair is safe?"*

### Case Study: `TEXT_TOO_SMALL` (Slide 14 has 7.7pt font)
| Causal Hypothesis | Supporting Multi-Layer Evidence | Owning Layer | Safe Repair Class | Strictly Forbidden Repair |
| :--- | :--- | :---: | :---: | :---: |
| **Hypothesis A: Blueprint Capacity Mismatch** | Max blocks = 8 (capacity = 5); font reduction isolated only to dense page. | `BLUEPRINT` | `CLASS_D_BLUEPRINT_REGROUPING` (Split slide) | `GLOBAL_FONT_SHRINK` |
| **Hypothesis B: Typography Config Failure** | All 14 slides have $<8.5\text{ pt}$ font despite sparse 2-bullet content. | `TYPOGRAPHY` | `CLASS_B_TYPOGRAPHY` (Increase base font) | `SPLIT_CONTENT_GROUP` |
| **Hypothesis C: Layout Template Mismatch** | Card grid container overlaps flex children; block count normal. | `LAYOUT` | `CLASS_C_LAYOUT_REMAPPING` (Switch to timeline) | `TEXT_CLIPPING_SUPPRESSION` |
| **Hypothesis D: Ambiguous Evidence** | Evidence delta $<0.15$ or confidence $<0.50$. | `ARTIFACT_POLICY` | `CLASS_G_MANUAL_REVIEW` (Human review) | `ANY_AUTOMATIC_REPAIR` |

---

## 4. Forensic Audit Findings

As documented in `docs/phase_3a_1_quality_authority_forensic_audit.md`, 18 core components across Phase 2B, 2C, 3A, and legacy presentation QA were audited:
- **Canonical Components Retained**: `PDFGeometryInspector`, `RasterImageInspector`, `WhitespaceIntentModel`, `UnifiedFidelityValidator`.
- **Reusable Signal Providers**: `MasterQualityScoringEngine` (Phase 2C), `ArtifactDegeneracyDetector`, `PresentationRenderedQualityEvaluator`, `HandoutRenderedQualityEvaluator`, `WorksheetRenderedQualityEvaluator`, `ScientificRenderedQualityEvaluator`.
- **Conflicting Decision Engines Consolidated**: `CalibratedDecisionEngine` and `MasterRenderedQualityEngine` decision methods are subsumed under `UnifiedQualityAuthority`.
- **Duplicate Taxonomies Merged**: `FailureCategory` (Phase 2C) and `RenderedFailureCode` (Phase 3A) normalized into `CanonicalFailureCode` in `app/quality/causal/taxonomy.py`.

---

## 5. Quality Authority Consolidation

`UnifiedQualityAuthority` (`app/quality/causal/quality_authority.py`) is the sole canonical arbiter.
Its public method `evaluate_artifact(...)`:
- Ingests `RenderedArtifactInspection` (Phase 3A), `ArtifactQualityReport` (Phase 2C), and `ArtifactFidelityReport` (Phase 2B).
- Normalizes signals into `CanonicalFailure` instances.
- Performs causal clustering and attribution.
- Outputs `CanonicalQualityAssessment` with a single definitive decision: `PASS`, `PASS_WITH_WARNINGS`, `NEEDS_REPAIR`, or `BLOCKED`.

---

## 6. Canonical Quality Signals

Implemented in `app/quality/causal/contracts.py`, `QualitySignal` represents raw, unaggregated diagnostic observation:
- `signal_id`: UUID
- `source_engine`: e.g. `rendered_geometry_inspector`, `phase_2c_calibration_engine`
- `source_phase`: e.g. `PHASE_3A`, `PHASE_2C`, `PHASE_2B`
- `artifact_type`: `PRESENTATION`, `HANDOUT`, `WORKSHEET`, `SCIENTIFIC_DOCUMENT`
- `page_indices`: Tuple of affected 1-indexed pages
- `dimension`: `visual_geometry`, `readability`, `density_balance`, `composition_rhythm`, `pedagogy`, `academic_rigor`
- `metric_name`: e.g. `TEXT_TOO_SMALL`, `ELEMENT_COLLISION`
- `metric_value`: Scalar or boolean evidence
- `severity`: `CanonicalFailureSeverity` (`CRITICAL`, `MAJOR`, `MINOR`, `INFO`)

---

## 7. Canonical Failure Taxonomy

Implemented in `app/quality/causal/taxonomy.py`, every defect maps to an immutable code within 7 categories:
1. **SOURCE_SEMANTIC**: `SOURCE_GROUNDING_FAILURE`, `UNSUPPORTED_CLAIM`, `TRACEABILITY_BREAK`, `EVIDENCE_DISCIPLINE_FAILURE`.
2. **TRANSFORMATION**: `CONTENT_SELECTION_FAILURE`, `SEMANTIC_GROUPING_FAILURE`, `ARTIFACT_DIFFERENTIATION_FAILURE`, `COMPRESSION_FAILURE`, `SEQUENCING_FAILURE`.
3. **BLUEPRINT**: `BLUEPRINT_CAPACITY_MISMATCH`, `COGNITIVE_LOAD_OVERFLOW`, `NARRATIVE_FRAGMENTATION`, `INQUIRY_FLOW_BREAK`, `ARGUMENT_STRUCTURE_BREAK`.
4. **LAYOUT**: `LAYOUT_SEMANTIC_MISMATCH`, `LAYOUT_CAPACITY_MISMATCH`, `LAYOUT_MONOTONY`, `CARD_OVERLOAD`, `VISUAL_HIERARCHY_FAILURE`, `DUPLICATE_COMPOSITION`, `REPETITION_STREAK`.
5. **RENDER**: `TEXT_CLIPPING`, `ELEMENT_COLLISION`, `TEXT_TOO_SMALL`, `PAGE_BOUNDARY_VIOLATION`, `RENDER_SCALE_FAILURE`, `BLANK_PAGE`, `MARGIN_INCONSISTENCY`.
6. **DENSITY**: `DENSITY_OVERLOAD`, `DENSITY_UNDERFLOW`, `WALL_OF_TEXT`, `SUSPICIOUS_VOID`, `DENSITY_IMBALANCE`.
7. **ARTIFACT_SPECIFIC**:
   - Presentation: `PRESENTATION_HANDOUT_COLLAPSE`, `PRESENTATION_RHYTHM_FAILURE`, `PRESENTATION_DUPLICATE_SEQUENCE`.
   - Handout: `HANDOUT_READING_FLOW_FAILURE`, `HANDOUT_FRAGMENTATION`, `HANDOUT_PAGE_BALANCE_FAILURE`, `ORPHAN_HEADING`.
   - Worksheet: `WORKSHEET_QUIZ_COLLAPSE`, `WORKSHEET_WORKSPACE_FAILURE`, `WORKSHEET_WORKSPACE_INSUFFICIENT`, `WORKSHEET_INQUIRY_FLOW_FAILURE`, `WORKSHEET_SPOILING_FAILURE`.
   - Scientific: `SCIENTIFIC_HIERARCHY_FAILURE`, `SCIENTIFIC_EVIDENCE_VISIBILITY_FAILURE`, `SCIENTIFIC_EVIDENCE_DETACHED`, `SCIENTIFIC_CITATION_INVISIBLE`, `SCIENTIFIC_ARGUMENT_IMBALANCE`, `SCIENTIFIC_CHAPTER_IMBALANCE`.

---

## 8. Symptom vs Root Cause

| Observed Physical Symptom | Underlying Architectural Root Cause | Why They Differ |
| :--- | :--- | :--- |
| `TEXT_TOO_SMALL` | `BLUEPRINT_CAPACITY_MISMATCH` | Too many beats packed onto page forced font scaling down. |
| `TEXT_TOO_SMALL` | `TYPOGRAPHY_CONFIGURATION_FAILURE` | CSS base scale was misconfigured globally. |
| `ELEMENT_COLLISION` | `LAYOUT_CAPACITY_MISMATCH` | Template slots cannot support 4 multi-line cards side-by-side. |
| `BLANK_PAGE` | `BLANK_PAGE_INJECTION` | Spurious page-break CSS injected into continuous flow. |
| `WORKSHEET_QUIZ_COLLAPSE` | `TRANSFORMATION_SELECTION_FAILURE` | Transformer repeatedly picked questions without inquiry context. |
| `SCIENTIFIC_CITATION_INVISIBLE` | `CITATION_RENDER_SUPPRESSION` | Citations exist semantically in source/blueprint but omitted by renderer. |
| `ORPHAN_HEADING` | `PAGINATION_BREAK_PLACEMENT_FAILURE` | Heading placed $<70\text{ pt}$ from page edge without room for body. |

---

## 9. Root Cause Hypothesis Model

Implemented in `app/quality/causal/contracts.py`, `RootCauseHypothesis`:
- `cause_code`: Normalized cause string from catalog
- `cause_layer`: `ArchitectureLayer`
- `confidence_score`: Float between $0.0$ and $1.0$
- `confidence_level`: `HIGH`, `MEDIUM`, `LOW`, `AMBIGUOUS`
- `supporting_evidence`: Verifiable multi-layer proof points
- `contradicting_evidence`: Conflicting evidence items
- `affected_scope`: `LOCAL`, `CLUSTER`, `SYSTEMIC`, `ARTIFACT_WIDE`
- `repair_authority`: Architecture layer authorized to execute repair
- `allowed_repair_classes`: Tuple of permitted `CanonicalRepairClass`
- `forbidden_repairs`: Prohibited repair actions

---

## 10. Multi-Layer Evidence Collection

Implemented in `app/quality/causal/evidence_collector.py`, `CausalEvidenceCollector` extracts:
1. **Source Layer**: Entity count, word density.
2. **Transformation Layer**: Selected units, compression ratio.
3. **Blueprint Layer**: Planned blocks per slide/page, cognitive load index, capacity threshold comparisons.
4. **Layout Layer**: Template family, card counts, slot capacities.
5. **Render Layer**: Display list bounding boxes, font distributions, clipping count, collision count, raster densities.
6. **Font Distribution Isolation**: Computes whether font reduction is globally uniform or isolated exclusively to overloaded pages.

---

## 11. Failure Correlation & Clustering

Implemented in `app/quality/causal/failure_correlation.py`:
- Maps failures by affected pages and calculates connected components.
- Co-occurring defects on shared pages (e.g. `TEXT_TOO_SMALL` + `ELEMENT_COLLISION` + `DENSITY_OVERLOAD` on Slide 5) are unified into a single `FailureCluster`.
- **Architectural Value**: Prevents the repair engine from attempting three separate, competing repairs on the same container. A single root cause (`BLUEPRINT_CAPACITY_MISMATCH`) is addressed by `CLASS_D_BLUEPRINT_REGROUPING`.

---

## 12. Scope-Aware Failure Analysis

Implemented in `app/quality/causal/scope_analyzer.py`:
- `LOCAL`: 1–2 pages ($\le 15\%$ of pages).
- `CLUSTER`: 3+ consecutive pages with repetitive failure.
- `SYSTEMIC`: $> 50\%$ of pages exhibit the flaw.
- `ARTIFACT_WIDE`: Structural flaws affecting the whole artifact (citations, BAB ordering, quiz collapse).

---

## 13. Causal Confidence Model

Implemented in `app/quality/causal/confidence.py`:
$$\text{Raw Confidence} = \left(\frac{N_{\text{supporting}}}{N_{\text{supporting}} + 1}\right) \times W_{\text{evidence}}$$
- If $N_{\text{contradicting}} > 0$: Confidence capped at $0.40$ (`LOW`).
- If $\Delta(\text{Hyp}_1, \text{Hyp}_2) < 0.15$: Reclassified as `AMBIGUOUS`.
- **Invariant**: If confidence is `LOW` or `AMBIGUOUS`, automatic repair is forbidden (`requires_manual_review = True`, allowed repair = `CLASS_G_MANUAL_REVIEW`).

---

## 14. Architectural Layer Ownership

The 10 layers:
1. `SOURCE`: Factual grounding, source integrity.
2. `SEMANTIC`: Knowledge manifest, entity boundaries.
3. `TRANSFORMATION`: Cross-artifact intent, compression, sequencing.
4. `SELECTION`: Entity filtering.
5. `BLUEPRINT`: Cognitive load, beat grouping, section capacities.
6. `LAYOUT`: Template selection, card allocation, slot counts.
7. `COMPOSITION`: Multi-column flow, page break pagination, visual rhythm.
8. `TYPOGRAPHY`: Type scale, font family, line leading.
9. `RENDER`: Browser viewport, PDF display lists, vector geometry.
10. `ARTIFACT_POLICY`: Anti-spoiling, scientific academic conventions, pedagogical rules.

---

## 15. Repair Authority Matrix

Implemented in `app/quality/causal/repair_authority.py`:

| Root Cause | Owning Layer | Allowed Repair Classes | Strictly Forbidden Repairs |
| :--- | :---: | :--- | :--- |
| `BLUEPRINT_CAPACITY_MISMATCH` | `BLUEPRINT` | `CLASS_D_BLUEPRINT_REGROUPING`, `CLASS_C_LAYOUT_REMAPPING` | `GLOBAL_FONT_SHRINK`, `TEXT_CLIPPING_SUPPRESSION` |
| `TYPOGRAPHY_CONFIGURATION_FAILURE`| `TYPOGRAPHY` | `CLASS_B_TYPOGRAPHY` | `SPLIT_CONTENT_GROUP`, `REGENERATE_BLUEPRINT` |
| `LAYOUT_CAPACITY_MISMATCH` | `LAYOUT` | `CLASS_C_LAYOUT_REMAPPING`, `CLASS_A_GEOMETRY` | `TEXT_CLIPPING_SUPPRESSION` |
| `RENDER_SCALE_FAILURE` | `RENDER` | `CLASS_A_GEOMETRY` | `CONTENT_DELETION` |
| `TRANSFORMATION_SELECTION_FAILURE`| `TRANSFORMATION` | `CLASS_E_TRANSFORMATION_STRATEGY` | `LAYOUT_CSS_PATCH` |
| `ANTI_SPOILING_POLICY_BREACH` | `ARTIFACT_POLICY` | `CLASS_F_ARTIFACT_POLICY`, `CLASS_E_TRANSFORMATION_STRATEGY`| `CSS_OPACITY_ZERO` |
| `CITATION_RENDER_SUPPRESSION` | `COMPOSITION` | `CLASS_F_ARTIFACT_POLICY`, `CLASS_C_LAYOUT_REMAPPING` | `REWRITE_SOURCE_CLAIMS` |
| `BLANK_PAGE_INJECTION` | `COMPOSITION` | `CLASS_A_GEOMETRY` | `FILL_WITH_LOREM_IPSUM` |
| `CAUSE_AMBIGUOUS` / `LOW` | `ARTIFACT_POLICY` | `CLASS_G_MANUAL_REVIEW` | `ANY_AUTOMATIC_REPAIR` |

---

## 16. Artifact-Specific Causal Rules

Implemented in `app/quality/causal/artifact_causes.py`:
- **Presentation**: Differentiates `PRESENTATION_HANDOUT_COLLAPSE` (transformation compression failure) from `CARD_OVERLOAD` (blueprint capacity mismatch).
- **Handout**: Differentiates `ORPHAN_HEADING` (pagination composition break) from `WALL_OF_TEXT` (transformation grouping failure).
- **Worksheet**: Differentiates `WORKSHEET_QUIZ_COLLAPSE` (transformation selection) from `WORKSHEET_WORKSPACE_INSUFFICIENT` (blueprint allocation) and `WORKSHEET_SPOILING_FAILURE` (policy breach).
- **Scientific Document**: Differentiates `CITATION_RENDER_SUPPRESSION` (composition omission when source has citations) from `EVIDENCE_DISCIPLINE_FAILURE` (source truly lacking citations), and `SCIENTIFIC_HIERARCHY_FAILURE` (transformation sequencing).

---

## 17. Progressive Reveal Protection

Implemented in `app/quality/causal/repetition_analyzer.py`:
- Solves the false-positive repetition problem where conceptual builds (e.g. Slide 1 problem, Slide 2 equation, Slide 3 derivation) were penalized as layout monotony.
- Analyzes `semantic_information_gain` alongside `visual_similarity`.
- If visual similarity $\ge 0.88$ AND information gain $\ge 0.25$: classified as `INTENTIONAL_CONTINUITY` with **0 penalty**.
- If visual similarity $\ge 0.88$ AND information gain $< 0.20$: classified as `LAYOUT_MONOTONY` with penalty.

---

## 18. Decision Policy & Gatekeeping

`UnifiedQualityAuthority` enforces a deterministic decision rule:
1. If $N_{\text{critical}} > 0$: `decision = BLOCKED`, `can_export = False`, `repair_required = True`.
2. If $N_{\text{major}} > 0$ with `SYSTEMIC`, `CLUSTER`, or `ARTIFACT_WIDE` scope: `decision = NEEDS_REPAIR`, `can_export = False`, `repair_required = True`.
3. If $N_{\text{major}} > 0$ with `LOCAL` scope on an isolated page: `decision = PASS_WITH_WARNINGS`, `can_export = True`.
4. If only $N_{\text{minor}} > 0$ or score $< 0.90$: `decision = PASS_WITH_WARNINGS`, `can_export = True`.
5. If clean: `decision = PASS`, `can_export = True`.
6. If any hypothesis has `LOW` or `AMBIGUOUS` confidence: `manual_review_required = True`.

---

## 19. Adversarial Testing Matrix

`tests/unit/quality/causal/test_causal_quality_intelligence.py` includes 31 comprehensive adversarial tests:
- Duplicate failure code normalization (Tests 1–4)
- Symptom vs root cause separation (Tests 5–8)
- Failure correlation and clustering (Tests 9–11)
- Scope analysis (Tests 12–15)
- Decision policy gatekeeping (Tests 16–19)
- Progressive reveal vs monotony (Tests 20–22)
- Worksheet pedagogical causal attribution (Tests 23–25)
- Scientific document causal attribution (Tests 26–27)
- Cross-phase consolidation and report generation (Tests 28–31)

**Result**: 31 / 31 passed in $0.44\text{ seconds}$.

---

## 20. Golden Fixture Results (`01_oobleck_experiment`)

Executed via `tests/integration/test_causal_quality_golden_benchmark.py`:

| Artifact Type | Unified Decision | Can Export | Score | Top Root Cause | Owning Layer | Clusters | Causal Insight |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **PRESENTATION** | `BLOCKED` | `False` | `0.546` | `TYPOGRAPHY_CONFIGURATION_FAILURE` | `TYPOGRAPHY` | 1 | All 14 slides suffer from global tiny font sizes below presentation readability threshold ($<11.0\text{ pt}$). |
| **HANDOUT** | `PASS_WITH_WARNINGS` | `True` | `0.929` | `GENERAL_RENDER_DEFECT` | `RENDER` | 1 | High overall readability and reading flow. 1 minor whitespace notice on page 1. |
| **WORKSHEET** | `NEEDS_REPAIR` | `False` | `0.805` | `GENERAL_RENDER_DEFECT` | `RENDER` | 1 | High inquiry coverage and 30+ writing boxes. Micro-typography in notes requires Class B adjustment. |
| **SCIENTIFIC_DOCUMENT** | `NEEDS_REPAIR` | `False` | `0.893` | `CITATION_RENDER_SUPPRESSION` | `COMPOSITION` | 1 | Citations exist in source metadata but renderer suppressed bracketed markers in the 10-page text. |

*Generated Reports*:
- Master Causal Summary: [`outputs/benchmark/phase_3a_1/phase_3a_1_golden_benchmark_causal_summary.md`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/benchmark/phase_3a_1/phase_3a_1_golden_benchmark_causal_summary.md)
- Presentation: [`outputs/benchmark/phase_3a_1/01_oobleck_experiment/presentation/presentation_causal_report.md`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/benchmark/phase_3a_1/01_oobleck_experiment/presentation/presentation_causal_report.md)
- Handout: [`outputs/benchmark/phase_3a_1/01_oobleck_experiment/handout/handout_causal_report.md`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/benchmark/phase_3a_1/01_oobleck_experiment/handout/handout_causal_report.md)
- Worksheet: [`outputs/benchmark/phase_3a_1/01_oobleck_experiment/worksheet/worksheet_causal_report.md`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/benchmark/phase_3a_1/01_oobleck_experiment/worksheet/worksheet_causal_report.md)
- Scientific: [`outputs/benchmark/phase_3a_1/01_oobleck_experiment/scientific_document/scientific_document_causal_report.md`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/benchmark/phase_3a_1/01_oobleck_experiment/scientific_document/scientific_document_causal_report.md)

---

## 21. Performance & Execution Benchmarks

- **Signal Normalization**: $< 0.2\text{ ms}$ per artifact.
- **Evidence Collection & Analysis**: $< 0.5\text{ ms}$ per artifact.
- **Clustering & Causal Attribution**: $< 1.0\text{ ms}$ per artifact.
- **Full Golden Benchmark Evaluation (4 artifacts, 42 pages)**: $3.90\text{ seconds}$ total.
- **Full Repository Regression (446 tests)**: $22.95\text{ seconds}$ total.

---

## 22. Limitations

1. **Heuristic Blueprint Correlation**: When full upstream AST intermediate models are omitted, the engine falls back to physical render evidence and marks confidence as `MEDIUM` or `LOW`.
2. **Deterministic Thresholds**: Slot capacity and density thresholds are strictly deterministic. Future empirical tuning may refine specific thresholds per custom curriculum.
3. **No Dynamic Code Inspection**: The engine does not parse arbitrary user CSS stylesheets directly; it infers typography configuration failures from the physical font distribution across pages.

---

## 23. Phase 3B Readiness Criteria

Phase 3A.1 successfully provides the contract interface required by Phase 3B (Targeted Repair Strategy Engine):
- `repair(failure)` is strictly **FORBIDDEN**.
- Instead, Phase 3B will receive:
  ```python
  repair_context = {
      "cluster_id": cluster.cluster_id,
      "symptoms": cluster.symptoms,
      "probable_root_cause": cluster.primary_root_cause.cause_code,
      "owning_layer": cluster.primary_root_cause.cause_layer,
      "confidence": cluster.primary_root_cause.confidence_level,
      "allowed_repair_classes": cluster.primary_root_cause.allowed_repair_classes,
      "forbidden_repairs": cluster.primary_root_cause.forbidden_repairs,
  }
  ```
- If `confidence` is `LOW` or `AMBIGUOUS`, Phase 3B is programmatically prohibited from executing automated edits, preserving document safety.

---

## 24. Explicit Architectural Sign-off

- [x] **No renderer redesign occurred.**
- [x] **No CSS beautification occurred.**
- [x] **No automatic repair loops executed.**
- [x] **No LLM or heuristic AI dependencies introduced (100% deterministic).**
- [x] **Quality authority consolidated under `UnifiedQualityAuthority`.**
- [x] **Symptom and root cause strictly separated.**
- [x] **Ambiguous root causes preserved as ambiguous without guessing.**
- [x] **Full regression suite 100% green (446/446 passed).**

