# Phase 3A.1 Forensic Architecture Audit: Quality Authority & Overlap Mapping
## Universal Document Intelligence System V5
### Quality Authority Unification & Component Classification Report

---

## 1. Executive Summary & Forensic Context

This forensic audit maps all existing quality evaluation, validation, taxonomy, scoring, and decision-making components across the repository. The Universal Document Intelligence System has evolved through:
- **Phase 1A–1D**: Universal Architecture & Semantic Blueprint Bridge
- **Phase 2A–2B**: Controlled Renderer Execution & Artifact Fidelity
- **Phase 2C**: Adversarial Artifact Quality Calibration
- **Phase 3A**: Independent Rendered Output Physical Quality

Over these iterations, multiple independent evaluators, failure taxonomies, scoring models, and decision gates were introduced. This created **Quality Authority Fragmentation**:
- `CalibratedDecisionEngine` (Phase 2C) inspects semantic intermediate models and issues export decisions without checking rendered output.
- `MasterRenderedQualityEngine` (Phase 3A) inspects physical PDFs and rasters and issues separate export decisions without awareness of semantic grounding.
- `PresentationQualityGate` (Legacy) evaluates presentation slides with an independent 25-gate rule set.
- `UnifiedQualityAuthority` (Phase 3A.1/3A.2/3B) was prototyped to unify these systems.

This audit establishes the definitive baseline inventory to unify all specialized signal providers under **ONE Authoritative Final Decision Architecture** without deleting useful evaluators.

---

## 2. Comprehensive Forensic Quality Component Audit Table

The table below audits all quality systems across `app/quality/`, `app/presentation/`, `app/integration/`, `app/orchestration/`, and `app/rendering/` according to the required schema:

| Component | File | Phase Origin | Input | Output | Quality Domain | Authority Level | Duplicate? | Reuse / Adapt / Deprecate | Migration Action |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `UnifiedQualityAuthority` | `app/quality/causal/quality_authority.py` | 3A.1 | Normalized Signals, MultiLayerEvidence | `CanonicalQualityAssessment` | CROSS_DOMAIN | **CANONICAL** | NO | Reuse & Harden | Sole authoritative final decision engine. |
| `MasterRenderedQualityEngine` | `app/quality/rendered/quality_engine.py` | 3A | Rendered PDF, HTML metadata | `RenderedArtifactInspection` | PHYSICAL_RENDER | **SPECIALIZED_PROVIDER** | NO | Adapt via Adapter | Wrap as signal provider for physical rendered canvas. |
| `PDFGeometryInspector` | `app/quality/rendered/pdf_inspector.py` | 3A | PyMuPDF Document / Page | `GeometryMetrics`, `PageGeometryAnalysis` | PHYSICAL_RENDER | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Primary display list geometry inspector (clipping, fonts). |
| `RasterQualityInspector` | `app/quality/rendered/raster_inspector.py` | 3A | PyMuPDF Pixmaps | `RasterMetrics`, `PageRasterAnalysis` | PHYSICAL_RENDER | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Primary visual/raster vision inspector (blank pages, blur). |
| `CompositionFingerprintEngine` | `app/quality/rendered/composition_fingerprint.py` | 3A | Rendered Page Geometry | `CompositionMetrics`, `RepetitionStreak` | STYLE_DESIGN | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Spatial layout similarity & repetition streak provider. |
| `WhitespaceDistributionModel` | `app/quality/rendered/whitespace_model.py` | 3A | Page occupancy, element bbox | `WhitespaceEvaluation` | COGNITIVE_LOAD | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Contextual whitespace vs student workspace classifier. |
| `TypographyDensityModel` | `app/quality/rendered/typography_density.py` | 3A | Text token counts, line count | `DensityMetrics` | COGNITIVE_LOAD | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Wall-of-text and paragraph density analyzer. |
| `CalibratedQualityEngine` | `app/quality/calibration/calibration_engine.py` | 2C | Semantic Blueprint, Metrics | `ArtifactQualityReport` | SEMANTIC / ARTIFACT | **SPECIALIZED_PROVIDER** | NO | Adapt via Adapter | Upstream semantic & pedagogical quality provider. |
| `MasterQualityScoringEngine` | `app/quality/calibration/quality_scoring.py` | 2C | Intermediate models | `ArtifactQualityReport` | SEMANTIC / ARTIFACT | **SPECIALIZED_PROVIDER** | NO | Adapt via Adapter | Provides calibrated dimension scores. |
| `CalibratedDecisionEngine` | `app/quality/calibration/decision_engine.py` | 2C | FidelityReport, QualityReport | `CalibratedQualityDecision` | SEMANTIC_DECISION | **CONFLICTING** | YES | Deprecate Authority, Retain as Adapter | Subsume export authority under UnifiedQualityAuthority. |
| `ArtifactDegeneracyDetector` | `app/quality/calibration/degeneracy_detector.py` | 2C | Intermediate models | `DegeneracyViolation` | SEMANTIC_INTEGRITY | **SPECIALIZED_PROVIDER** | NO | Reuse directly | Feeds anti-perfection and collapse signals into authority. |
| `UnifiedFidelityValidator` | `app/quality/artifact_fidelity/unified_fidelity_validator.py` | 2B | RenderArtifact, LegacyModel | `ArtifactFidelityReport` | ARTIFACT_FIDELITY | **SPECIALIZED_PROVIDER** | NO | Adapt via Adapter | Authoritative validator for semantic blueprint survival. |
| `PresentationFidelityValidator` | `app/quality/artifact_fidelity/presentation_fidelity.py` | 2B | PresentationBlueprint, RenderArtifact | `ArtifactFidelityReport` | ARTIFACT_FIDELITY | **SPECIALIZED_PROVIDER** | NO | Reuse via UnifiedFidelity | Presentation-specific fidelity validator. |
| `HandoutFidelityValidator` | `app/quality/artifact_fidelity/handout_fidelity.py` | 2B | HandoutBlueprint, RenderArtifact | `ArtifactFidelityReport` | ARTIFACT_FIDELITY | **SPECIALIZED_PROVIDER** | NO | Reuse via UnifiedFidelity | Handout-specific fidelity validator. |
| `WorksheetFidelityValidator` | `app/quality/artifact_fidelity/worksheet_fidelity.py` | 2B | WorksheetBlueprint, RenderArtifact | `ArtifactFidelityReport` | ARTIFACT_FIDELITY | **SPECIALIZED_PROVIDER** | NO | Reuse via UnifiedFidelity | Worksheet-specific fidelity validator. |
| `ScientificDocumentFidelityValidator` | `app/quality/artifact_fidelity/scientific_fidelity.py` | 2B | ScientificBlueprint, RenderArtifact | `ArtifactFidelityReport` | ARTIFACT_FIDELITY | **SPECIALIZED_PROVIDER** | NO | Reuse via UnifiedFidelity | Scientific document-specific fidelity validator. |
| `PresentationQualityGate` | `app/presentation/quality_gate.py` | Legacy | `SlidePlan`, `GeneratedSlide` | `GateResult`, `QualityRound` | PRESENTATION_GATE | **CONFLICTING** | YES | Adapt via Adapter | Subsume gate decisions; wrap outputs into QualitySignal. |
| `VisualQA` | `app/presentation/visual_qa.py` | Legacy | Slide DOM / Rendered bbox | `VisualQAResult` | PRESENTATION_VISUAL | **LEGACY_COMPATIBILITY** | YES | Adapt via Adapter | Wrap DOM inspection outputs into canonical signals. |
| `NarrativeFlowEvaluator` | `app/presentation/narrative_evaluator.py` | Legacy | Slide Sequence, Blueprint | Narrative Score | PEDAGOGICAL | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds narrative progression metrics. |
| `RhythmAnalyzer` | `app/presentation/rhythm_analyzer.py` | Legacy | Slide layouts, element counts | Rhythm Score | STYLE_DESIGN | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds composition variation metrics. |
| `SemanticLayoutValidator` | `app/presentation/semantic_layout_validator.py` | Legacy | Layout card types, content units | Validation status | BLUEPRINT_INTEGRITY | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds layout-semantic compatibility signals. |
| `ClaimGroundingValidator` | `app/presentation/claim_grounding_validator.py` | Legacy | Slide claims, SourceUnits | Grounding status | SEMANTIC_TRACEABILITY| **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds source grounding signals. |
| `PresentationDecisionEngine` | `app/presentation/decision_engine.py` | Legacy | Gate results, visual QA | Slide decision | PRESENTATION_DECISION| **DEPRECATED** | YES | Deprecate Authority | Replaced by UnifiedQualityAuthority. |
| `QualityEvaluationEngine` | `app/quality/engine.py` | Phase 1 | Markdown/Raw AST | Legacy `QualityReport` | GENERIC_QUALITY | **LEGACY_COMPATIBILITY** | YES | Adapt via Adapter | Legacy fallback evaluator; wrapped by adapter. |
| `SemanticEvaluator` | `app/quality/semantic_evaluator.py` | Phase 1 | Content AST | Semantic metrics | SEMANTIC_INTEGRITY | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds raw semantic metrics. |
| `StructuralEvaluator` | `app/quality/structural_evaluator.py` | Phase 1 | Content AST | Structural metrics | BLUEPRINT_INTEGRITY | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds document structure metrics. |
| `PedagogicalEvaluator` | `app/quality/pedagogical_evaluator.py` | Phase 1 | Content AST | Pedagogical metrics | PEDAGOGICAL | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds pedagogical structure metrics. |
| `FormatEvaluator` | `app/quality/format_evaluator.py` | Phase 1 | Content AST | Format metrics | FORMAT_COMPLIANCE | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds format conformance metrics. |
| `DensityEvaluator` | `app/quality/density_evaluator.py` | Phase 1 | Content AST | Density metrics | COGNITIVE_LOAD | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds AST text density metrics. |
| `RedundancyEvaluator` | `app/quality/redundancy_evaluator.py` | Phase 1 | Content AST | Redundancy metrics | COGNITIVE_LOAD | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Feeds AST repetition metrics. |
| `ContentChecker` | `app/quality/content_checker.py` | Phase 1 | Text tokens | Keyword checks | CONTENT_CHECK | **LEGACY_COMPATIBILITY** | NO | Reuse as Provider | Basic content checks. |
| `LayoutChecker` | `app/quality/layout_checker.py` | Phase 1 | HTML layout | Layout checks | LAYOUT_CHECK | **LEGACY_COMPATIBILITY** | NO | Reuse as Provider | HTML DOM sanity checks. |
| `PDFChecker` | `app/quality/pdf_checker.py` | Phase 1 | PDF bytes | PDF syntax checks | PDF_VALIDATION | **LEGACY_COMPATIBILITY** | NO | Reuse as Provider | Basic PDF syntax checks. |
| `PDFValidator` | `app/rendering/validation/pdf_validator.py` | Phase 2B | PDF path, page count | `ValidationResult` | PDF_CONFORMANCE | **SPECIALIZED_PROVIDER** | NO | Reuse as Provider | Checks basic page count and PDF header conformance. |
| `FailureCorrelationEngine` | `app/quality/causal/failure_correlation.py` | 3A.1 | `CanonicalFailure`s, Evidence | `FailureCluster`s | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Correlates co-occurring findings on shared pages. |
| `CausalAttributionEngine` | `app/quality/causal/attribution_engine.py` | 3A.1 | `CanonicalFailure`s, Evidence | `RootCauseHypothesis` | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Attributes root cause layer and hypotheses. |
| `RepairAuthorityMatrix` | `app/quality/causal/repair_authority.py` | 3A.1 | Root causes, target layers | Allowed repair classes | REPAIR_POLICY | **CANONICAL** | NO | Reuse & Harden | Restricts repair authorization per layer. |
| `ProgressionAwareRepetitionAnalyzer` | `app/quality/causal/repetition_analyzer.py` | 3A.1 | Slide fingerprints, information gain | Adjusted monotony penalty | STYLE_DESIGN | **CANONICAL** | NO | Reuse & Harden | Distinguishes progressive reveal from monotony. |
| `ScopePolicy` / `ScopeAnalyzer` | `app/quality/causal/scope.py` | 3A.1/3A.2 | Affected pages, total pages | `FailureScope` | QUALITY_SCOPE | **CANONICAL** | NO | Reuse & Harden | Derives LOCAL, CLUSTER, SYSTEMIC, ARTIFACT_WIDE. |
| `SignalLifecycleStateMachine` | `app/quality/causal/lifecycle.py` | 3A.2 | Lifecycle records | Transitioned record | LIFECYCLE_AUDIT | **CANONICAL** | NO | Reuse & Harden | Validates state progression and audit history. |
| `QualitySignalNormalizer` | `app/quality/causal/signal_normalization.py` | 3A.2 | Adapter inputs | `QualitySignal`s | SIGNAL_NORMALIZATION | **CANONICAL** | NO | Reuse & Harden | Converts raw provider outputs into canonical signals. |
| `FindingCorrelationEngine` | `app/quality/causal/correlation_engine.py` | 3B | `QualitySignal`s | `CorrelationGraph`, `CorrelationResult` | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | 5D multi-index proximity correlation. |
| `FailureClusterBuilder` | `app/quality/causal/cluster_builder.py` | 3B | `CorrelationResult` | `FailureCluster`s | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Deterministic SHA-256 connected components clustering. |
| `SymptomCauseClassifier` | `app/quality/causal/symptom_classifier.py` | 3B | `FailureCluster` | `FailureRoleAssignment`s | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Separates physical symptoms from root causes. |
| `CausalRuleCatalog` | `app/quality/causal/rules.py` | 3B | `FailureCluster` | `CausalRuleMatch`es | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Deterministic rule base for 4 artifact formats. |
| `CausalEvidenceScorer` | `app/quality/causal/evidence_scorer.py` | 3B | Rule matches, Cluster | Causal confidence & breakdown | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Calculates confidence, enforces lineage direction. |
| `CompetingHypothesisAnalyzer` | `app/quality/causal/competing_analysis.py` | 3B | Hypotheses list | `CompetingAnalysisResult` | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Evaluates competing causes and ambiguity margin ($\le 0.10$). |
| `ValidatorAnomalyDetector` | `app/quality/causal/validator_anomaly.py` | 3B | `FailureCluster` | `RootCauseHypothesis` | CAUSAL_DIAGNOSIS | **CANONICAL** | NO | Reuse & Harden | Flags inspector contradiction (`VALIDATOR_FALSE_POSITIVE`). |
| `RepairReadinessAssessor` | `app/quality/causal/repair_readiness.py` | 3B | Cluster, CompetingResult | `RepairReadinessAssessment` | REPAIR_POLICY | **CANONICAL** | NO | Reuse & Harden | Recommends authority (`DETERMINISTIC_REPAIR_CANDIDATE`, etc.). |
| `QualityStage` | `app/orchestration/stages/quality.py` | Orchestration | Artifact payload | Stage result | PIPELINE_STAGE | **LEGACY_COMPATIBILITY** | NO | Adapt to Authority | Orchestrator pipeline stage executing quality authority. |
| `ArtifactValidationStage` | `app/orchestration/stages/artifact_validation.py` | Orchestration | Artifact payload | Stage result | PIPELINE_STAGE | **LEGACY_COMPATIBILITY** | NO | Adapt to Authority | Orchestrator pipeline stage executing validation. |

---

## 3. Classification of Quality Authority Levels

1. **CANONICAL (Single Source of Truth)**:
   - `UnifiedQualityAuthority` (`app/quality/causal/quality_authority.py`)
   - `ScopePolicy` (`app/quality/causal/scope.py`)
   - `SignalLifecycleStateMachine` (`app/quality/causal/lifecycle.py`)
   - `FindingCorrelationEngine` / `FailureCorrelationEngine` (`app/quality/causal/correlation_engine.py`, `failure_correlation.py`)
   - `CausalAttributionEngine` / `CausalRuleCatalog` (`app/quality/causal/attribution_engine.py`, `rules.py`)
   - `RepairAuthorityMatrix` / `RepairReadinessAssessor` (`app/quality/causal/repair_authority.py`, `repair_readiness.py`)
   - `CompetingHypothesisAnalyzer` (`app/quality/causal/competing_analysis.py`)

2. **SPECIALIZED_PROVIDER (Specialized Evaluators to be Wrapped)**:
   - `MasterRenderedQualityEngine`, `PDFGeometryInspector`, `RasterQualityInspector` (Phase 3A)
   - `UnifiedFidelityValidator` and 4 format fidelity validators (Phase 2B)
   - `CalibratedQualityEngine`, `MasterQualityScoringEngine` (Phase 2C)
   - `ArtifactDegeneracyDetector` (Phase 2C)
   - `WhitespaceDistributionModel`, `TypographyDensityModel`, `CompositionFingerprintEngine` (Phase 3A)
   - `NarrativeFlowEvaluator`, `RhythmAnalyzer`, `SemanticLayoutValidator`, `ClaimGroundingValidator` (Presentation)
   - `SemanticEvaluator`, `StructuralEvaluator`, `PedagogicalEvaluator` (Phase 1)

3. **LEGACY_COMPATIBILITY (Preserved Without Breaking Legacy Callers)**:
   - `QualityEvaluationEngine` (`app/quality/engine.py`)
   - `VisualQA` (`app/presentation/visual_qa.py`)
   - `ContentChecker`, `LayoutChecker`, `PDFChecker`
   - `QualityStage`, `ArtifactValidationStage`

4. **CONFLICTING (Deprecate Direct Decision Authority; Subsume Under Unified Authority)**:
   - `CalibratedDecisionEngine`: Currently issues independent `PASS`/`BLOCKED` based on Phase 2C only. Must be subsumed; its pairwise comparison logic is preserved.
   - `PresentationQualityGate`: Currently issues independent slide-level `GateStatus`. Its checks are adapted into `QualitySignal`s.

5. **DEPRECATED**:
   - `PresentationDecisionEngine` (`app/presentation/decision_engine.py`): Legacy ad-hoc decision engine superseded by `UnifiedQualityAuthority`.

---

## 4. The Four Orthogonal Truth Layers

The unified authority explicitly consolidates four independent, orthogonal truth layers:

```
+-------------------------------------------------------------------------------+
|                      TRUTH LAYER 1: SEMANTIC INTEGRITY                         |
| Question: "Is the knowledge transformation semantically correct?"             |
| Evaluators: CalibratedQualityEngine, SemanticEvaluator, ClaimGroundingValidator |
| Failure Modes: UNSUPPORTED_CLAIM, FABRICATED_KNOWLEDGE, ANSWER_LEAKAGE         |
+-------------------------------------------------------------------------------+
                                      ▲
                                      │
+-------------------------------------------------------------------------------+
|                      TRUTH LAYER 2: ARTIFACT FIDELITY                          |
| Question: "Did the artifact-specific semantic blueprint survive execution?"    |
| Evaluators: UnifiedFidelityValidator (Presentation, Handout, Worksheet, Sci)  |
| Failure Modes: SOURCE_ELEMENT_DROPPED, BLUEPRINT_ELEMENT_DROPPED, UNRESOLVED   |
+-------------------------------------------------------------------------------+
                                      ▲
                                      │
+-------------------------------------------------------------------------------+
|                      TRUTH LAYER 3: ARTIFACT QUALITY                           |
| Question: "Is the artifact pedagogically and structurally good?"              |
| Evaluators: Format Rendered Evaluators, NarrativeEvaluator, RhythmAnalyzer     |
| Failure Modes: COGNITIVE_LOAD_OVERFLOW, INQUIRY_FLOW_BREAK, MONOTONY_STREAK    |
+-------------------------------------------------------------------------------+
                                      ▲
                                      │
+-------------------------------------------------------------------------------+
|                   TRUTH LAYER 4: PHYSICAL RENDERED QUALITY                     |
| Question: "Did the actual rendered PDF physically render correctly?"           |
| Evaluators: PDFGeometryInspector (PyMuPDF), RasterQualityInspector (Pillow)    |
| Failure Modes: TEXT_CLIPPING, ELEMENT_COLLISION, TEXT_TOO_SMALL, BLANK_PAGE   |
+-------------------------------------------------------------------------------+
```

---

## 5. Decision Authority & Double-Counting Prevention Strategy

1. **Sole Decision Authority**:
   Only `UnifiedQualityAuthority` produces the final `CanonicalQualityAssessment` (`PASS`, `PASS_WITH_WARNINGS`, `NEEDS_REPAIR`, `BLOCKED`). No specialized evaluator may independently block or approve export.
2. **Double-Counting Elimination**:
   `FindingCorrelationEngine` clusters co-occurring symptoms detected by multiple inspectors (e.g. PyMuPDF tiny font + legacy visual QA readability penalty) on the same element/page into a single `FailureCluster` with unified severity, preserving all contributing evidence references.
3. **Lineage-Consistent Causal Attribution**:
   Physical symptoms on canvas are separated from root causes. `TEXT_TOO_SMALL` in the presence of `DENSITY_OVERLOAD` attributes to `LAYOUT_CAPACITY_EXCEEDED` at the `COMPOSITION` layer, rather than a naive font resizing rule.
4. **Zero AI Guarantee**:
   All 4 truth layers, adapters, correlation engines, and decision matrices are 100% deterministic, offline Python standard library and Pydantic models.

---
*End of Phase 3A.1 Forensic Architecture Audit.*
