# Phase 3B: Failure Correlation & Causal Attribution Engine
## Universal Document Intelligence System V5
### Forensic Architectural Specification & Calibration Report

---

## 1. Executive Summary

Phase 3B introduces the **Failure Correlation & Causal Attribution Engine** for the Universal Document Intelligence System V5. Operating directly on normalized, detection-only `QualitySignal` instances emitted during Phase 3A/3A.2 inspection, Phase 3B transforms isolated physical and structural symptoms into deterministic failure clusters, formulates competing root cause hypotheses, evaluates multi-dimensional evidence, and issues authoritative repair readiness assessments without mutating artifacts or executing automated repairs.

The engine guarantees:
1. **100% Deterministic & Offline Execution**: Zero reliance on external heuristics, LLMs, or non-reproducible stochastic models.
2. **Multi-Dimensional Correlation**: Measures spatial, structural, semantic, lineage, and failure pattern proximity.
3. **Lineage Consistency**: Enforces directional causality (downstream render symptoms cannot cause upstream blueprint or source defects).
4. **Ambiguity Preservation**: Retains competing hypotheses and detects causal ties ($\Delta \le 0.10$), strictly preventing premature automated misrepairs.
5. **Universal Cross-Artifact Coverage**: Tailored causal attribution across all four canonical formats:
   - `PRESENTATION` (16:9 Slide Deck)
   - `HANDOUT` (A4 Reading Material)
   - `WORKSHEET` (LKS Inquiry Progression)
   - `SCIENTIFIC_DOCUMENT` (KTI Rigor & Evidence Discipline)

---

## 2. Architectural Context & Placement

Within the Universal Document Intelligence System pipeline, Phase 3B occupies the critical analytical bridge between physical detection and targeted strategic repair:

```
+-------------------------------------------------------------------------------+
| PHASE 3A / 3A.2: DETECTION & NORMALIZATION                                    |
| Raw Render & Structural Inspectors -> QualitySignalNormalizer -> QualitySignal |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 3B: CAUSAL ATTRIBUTION & REPAIR READINESS ENGINE (THIS PHASE)           |
| 1. Correlation Engine: 5D Proximity Scoring -> CorrelationGraph               |
| 2. Cluster Builder: Connected Components -> FailureClusters                   |
| 3. Symptom Classifier: Symptoms vs Root Cause Candidates                      |
| 4. Rule Catalog & Evidence Scorer: Competing Hypotheses & Invariant Proofs    |
| 5. Competing Analyzer & Anomaly Detector: Ambiguity & Validator Defect Checks |
| 6. Repair Readiness Assessor: Authority & Blast Radius Gating                 |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| PHASE 3C / 3D: TARGETED REPAIR STRATEGY & TRANSACTION EXECUTION (DEFERRED)    |
| Deterministic Blueprint & Layout Patching -> Atomic Rollbacks -> Revalidation |
+-------------------------------------------------------------------------------+
```

---

## 3. System Principles & Strict Boundaries

### Strict Invariants Enforced in Phase 3B:
1. **Zero Repair Execution**: Phase 3B is strictly read-only and analytical. It proposes repair authority levels and repair classes, but never modifies blueprints, ASTs, HTML/CSS, or PDFs.
2. **Immutability of Inputs**: `QualitySignal` instances remain frozen and immutable throughout the pipeline.
3. **Explicit Distinction between Observations, Inferences, and Causes**:
   - *Observations*: Direct, empirically measured physical coordinates, font sizes, bounding boxes.
   - *Inferences*: Mathematical correlation edges, cluster boundaries, candidate hypotheses, blast radius estimates.
   - *Confirmed Causes*: Hypotheses backed by proven lineage consistency, explanatory coverage, and absence of contradiction.
4. **No Presentation-Only Bias**: All four artifact formats are first-class citizens with dedicated causal rules and scope thresholds.

---

## 4. Failure Correlation Engine: 5-Dimensional Proximity Model

The `FailureCorrelationEngine` measures multi-dimensional proximity between candidate signal pairs $(s_a, s_b)$ using five normalized dimensions ($w_i \in [0, 1]$, $\sum w_i = 1.0$):

$$\text{Total Score}(s_a, s_b) = w_{\text{spa}} S_{\text{spa}} + w_{\text{str}} S_{\text{str}} + w_{\text{sem}} S_{\text{sem}} + w_{\text{lin}} S_{\text{lin}} + w_{\text{pat}} S_{\text{pat}}$$

### Weight Configuration:
- $w_{\text{spatial}} = 0.30$: Physical proximity on canvas (same element, same page, adjacent pages, bounding box overlap).
- $w_{\text{structural}} = 0.25$: Structural hierarchy (shared blueprint slot, parent container, layout template).
- $w_{\text{semantic}} = 0.15$: Conceptual lineage (shared knowledge unit IDs, shared semantic role).
- $w_{\text{lineage}} = 0.15$: Pipeline stage relationships (co-located component transformations).
- $w_{\text{pattern}} = 0.15$: Empirical co-occurrence compatibility (calibrated affinity table).

### Thresholds:
- $\tau_{\text{min}} = 0.60$: Minimum score required to establish a valid `CorrelationEdge`.
- $\tau_{\text{strong}} = 0.80$: Strong correlation indicating tightly coupled failure mechanisms.

---

## 5. Correlation Graph Architecture

The `CorrelationGraph` model maintains nodes (signals) and undirected edges (`CorrelationEdge`). Each edge contains:
- `signal_a_id`, `signal_b_id`: Lexicographically sorted identifiers.
- `score`: Composite float $\in [0.0, 1.0]$.
- `breakdown`: Component scores across the 5 dimensions.
- `relationship_type`: Controlled enumeration:
  - `CO_LOCATED`: Co-located on canvas or element.
  - `STRUCTURALLY_RELATED`: Linked by shared blueprint card or layout container.
  - `SEMANTICALLY_RELATED`: Linked by source knowledge concepts.
  - `LINEAGE_RELATED`: Linked by pipeline transformation steps.
  - `PATTERN_COMPATIBLE`: High co-occurrence affinity.
- `evidence`: Machine-readable textual justifications.

---

## 6. Connected Component Clustering & Deterministic Partitioning

The `FailureClusterBuilder` constructs deterministic `FailureCluster` instances from the `CorrelationGraph`:
1. **Connected Components**: Traverses the graph edges where $\text{score} \ge \tau_{\text{min}}$ using breadth-first search in sorted node order.
2. **Deterministic Cluster ID**: Cryptographically hashed using SHA-256 over sorted member signal IDs:
   $$\text{cluster\_id} = \text{"clust\_"} + \text{SHA256}(\text{"s1::s2::s3"})[:8]$$
3. **Singleton Clusters**: Signals with no edges $\ge \tau_{\text{min}}$ are safely retained as singleton clusters, ensuring 100% signal recall.
4. **Dominant Failure Patterns**: Extracted by sorting defect codes by frequency within the cluster.

---

## 7. Scope Policy Integration

Cluster scope is derived via `ScopePolicy` with multiformat thresholds:
- **`LOCAL`**: Flaws confined to 1–2 pages ($\le 15\%$ of total pages).
- **`CLUSTER`**: Consecutive streaks of affected pages (e.g. 3–5 slides).
- **`SYSTEMIC`**: Defects spanning $> 50\%$ of the document pages.
- **`ARTIFACT_WIDE`**: Document-level structural defects or global invariant violations (`SCIENTIFIC_CITATION_INVISIBLE`, `WORKSHEET_SPOILING_FAILURE`, `METADATA_CORRUPTION`, etc.) unconditionally resolve to `ARTIFACT_WIDE`.

---

## 8. Symptom vs. Cause Classification

The `SymptomCauseClassifier` assigns each signal a functional role within its cluster using architectural stage ordering:

| Architectural Stage | Stage Rank | Example Defect Codes | Assigned Role |
| :--- | :--- | :--- | :--- |
| `SOURCE` / `SEMANTIC` | 1–2 | `SOURCE_GROUNDING_FAILURE`, `UNSUPPORTED_CLAIM` | `ROOT_CAUSE_CANDIDATE` |
| `TRANSFORMATION` | 3 | `WORKSHEET_SPOILING_FAILURE`, `WORKSHEET_QUIZ_COLLAPSE` | `ROOT_CAUSE_CANDIDATE` |
| `BLUEPRINT` | 4 | `BLUEPRINT_CAPACITY_MISMATCH`, `NARRATIVE_FRAGMENTATION` | `ROOT_CAUSE_CANDIDATE` |
| `LAYOUT` / `COMPOSITION` | 5–6 | `DENSITY_OVERLOAD`, `WALL_OF_TEXT`, `LAYOUT_MONOTONY` | `POSSIBLE_CAUSE` |
| `RENDER` | 7 | `TEXT_CLIPPING`, `ELEMENT_COLLISION`, `TEXT_TOO_SMALL` | `PRIMARY_SYMPTOM` |

---

## 9. Causal Rule Base & Domain-Specific Rules

The `CausalRuleCatalog` maintains calibrated, deterministic causal attribution rules:

### Presentation Rules:
- `RULE_PRES_DENSITY_CAPACITY`: `TEXT_TOO_SMALL` + `DENSITY_OVERLOAD` $\to$ `LAYOUT_CAPACITY_EXCEEDED` (Composition Layer)
- `RULE_PRES_BLUEPRINT_OVERLOAD`: `COGNITIVE_LOAD_OVERFLOW` $\to$ `EXCESSIVE_COMPRESSION` (Blueprint Layer)
- `RULE_PRES_TYPOGRAPHY_SCALE`: `TEXT_TOO_SMALL` without density overload $\to$ `TYPOGRAPHY_SCALE_FAILURE` (Composition Layer)
- `RULE_PRES_HANDOUT_COLLAPSE`: `PRESENTATION_HANDOUT_COLLAPSE` $\to$ `SEMANTIC_LAYOUT_MISMATCH` (Transformation Layer)
- `RULE_PRES_MONOTONY_STREAK`: `LAYOUT_MONOTONY` + `REPETITION_STREAK` $\to$ `INVALID_GROUPING` (Blueprint Layer)

### Handout Rules:
- `RULE_HAND_CONTENT_OVERDENSITY`: `WALL_OF_TEXT` + `DENSITY_OVERLOAD` $\to$ `CONTENT_OVERDENSITY` (Source Layer)
- `RULE_HAND_STRUCTURE_FRAGMENTATION`: `HANDOUT_FRAGMENTATION` + `ORPHAN_HEADING` $\to$ `DOCUMENT_STRUCTURE_FAILURE` (Blueprint Layer)
- `RULE_HAND_LAYOUT_CAPACITY`: `PAGE_BOUNDARY_VIOLATION` + `ELEMENT_COLLISION` $\to$ `LAYOUT_CAPACITY_EXCEEDED` (Composition Layer)
- `RULE_HAND_PAGE_BALANCE`: `HANDOUT_PAGE_BALANCE_FAILURE` $\to$ `LAYOUT_CAPACITY_EXCEEDED` (Composition Layer)

### Worksheet Rules:
- `RULE_WORK_QUIZ_COLLAPSE`: `WORKSHEET_QUIZ_COLLAPSE` $\to$ `WORKSHEET_ANTI_INQUIRY_FAILURE` (Transformation Layer)
- `RULE_WORK_SPOILING`: `WORKSHEET_SPOILING_FAILURE` $\to$ `WORKSHEET_ANSWER_LEAKAGE` (Transformation Layer, Artifact Policy)
- `RULE_WORK_WORKSPACE_DEFICIT`: `WORKSHEET_WORKSPACE_INSUFFICIENT` $\to$ `LAYOUT_CAPACITY_EXCEEDED` (Composition Layer)

### Scientific Document Rules:
- `RULE_SCI_UNSUPPORTED_CLAIM`: `UNSUPPORTED_CLAIM` $\to$ `SOURCE_GROUNDING_FAILURE` (Source Layer)
- `RULE_SCI_CITATION_INVISIBLE`: `SCIENTIFIC_CITATION_INVISIBLE` $\to$ `CITATION_STRUCTURE_FAILURE` (Knowledge Model Layer)
- `RULE_SCI_BAB_INVERSION`: `SCIENTIFIC_ARGUMENT_IMBALANCE` $\to$ `SCIENTIFIC_ARGUMENT_FAILURE` (Blueprint Layer)

---

## 10. Multi-Hypothesis Generation & Non-Destructive Alternatives

When multiple rules match a failure cluster, the engine generates distinct `RootCauseHypothesis` candidates. Lower-ranked hypotheses are **never discarded**; they are retained as `alternative_hypotheses` with explicit rankings and score deltas.

---

## 11. Causal Evidence Scorer & Mathematical Model

Each hypothesis $H$ is scored via:

$$\text{Confidence}(H) = 0.30 \cdot C_{\text{cov}} + 0.25 \cdot E_{\text{str}} + 0.25 \cdot L_{\text{dir}} + 0.20 \cdot P_{\text{match}} - P_{\text{contra}} - P_{\text{comp}}$$

Where:
- $C_{\text{cov}}$: Explanatory coverage ($\frac{\text{signals explained}}{\text{total cluster signals}}$).
- $E_{\text{str}}$: Evidence strength from cluster correlation and physical inspection proofs.
- $L_{\text{dir}}$: Lineage consistency score ($1.0$ if upstream, $0.10$ if downstream violation).
- $P_{\text{match}}$: Pattern compatibility from rule match score.
- $P_{\text{contra}}$: Contradiction penalty ($0.40$ if contradictory measurements exist).
- $P_{\text{comp}}$: Competition penalty ($0.15 \times \text{number of competing hypotheses}$).

---

## 12. Lineage Consistency Invariant & Directional Enforcement

Downstream layers can never cause upstream defects. If a hypothesis proposes that a `RENDERING` layer issue caused a `BLUEPRINT` or `SOURCE_CONTENT` flaw, the engine applies an immediate $90\%$ lineage penalty ($L_{\text{dir}} = 0.10$), preventing spurious attributions.

---

## 13. Contradiction Penalty & Falsification Model

If diagnostic metadata indicates contradictory physical evidence (e.g. DOM declares large font but bounding box heuristic reports clipping), the hypothesis receives a severe contradiction penalty ($P_{\text{contra}} = 0.40$). Furthermore, hypotheses with contradictions are strictly barred from achieving `VERY_HIGH` confidence.

---

## 14. Competing Hypothesis Analyzer & Ambiguity Margin Policy

The `CompetingHypothesisAnalyzer` compares the top two hypotheses $H_1$ and $H_2$:
- If $\text{Score}(H_1) - \text{Score}(H_2) \le 0.10$ ($\text{Ambiguity Margin}$), the engine marks:
  $$\text{CausalDecision} = \text{MULTIPLE\_PLAUSIBLE\_CAUSES}, \quad \text{is\_ambiguous} = \text{True}$$
  This triggers a strict block against automated repair.

---

## 15. Authoritative Causal Decisions

The engine issues one of six authoritative causal decision states:
1. `ROOT_CAUSE_CONFIRMED`: Single dominant cause with score $\ge 0.85$ and clear margin.
2. `ROOT_CAUSE_LIKELY`: Single cause with score $\ge 0.75$.
3. `MULTIPLE_PLAUSIBLE_CAUSES`: Top hypotheses score within $0.10$ margin.
4. `INSUFFICIENT_EVIDENCE`: Top hypothesis score $< 0.35$.
5. `VALIDATOR_ANOMALY_SUSPECTED`: Conflicting measurements indicate tool defect.
6. `NO_CAUSAL_LINK`: Uncorrelated or spurious events.

---

## 16. Explainable Causal Path Construction & Lineage Chains

Each hypothesis formats a human-readable and machine-verifiable ASCII causal path illustrating the pipeline transmission:

```
[TRANSFORMATION] Excessive concept grouping into single beat
  --(CAUSES)--> [BLUEPRINT] Cognitive load capacity overflow
  --(CAUSES)--> [COMPOSITION] Container geometry overflow
  --(CAUSES)--> [RENDERING] Font scale reduced and text clipped
```

---

## 17. Validator False-Positive & Anomaly Detection

The `ValidatorAnomalyDetector` monitors for discrepancies where physical inspectors produce conflicting measurements (e.g. PyMuPDF reports text clipping, but DOM declared explicit bounding dimensions, or raster OCR is legible). When detected, the engine generates a `VALIDATOR_FALSE_POSITIVE` hypothesis and issues `CausalDecision.VALIDATOR_ANOMALY_SUSPECTED`.

---

## 18. Repair Readiness Assessment Model & Gating Criteria

The `RepairReadinessAssessor` evaluates whether a defect is safe for repair planning.

### Gating Conditions:
- If ambiguous $\to$ `MANUAL_REVIEW`.
- If validator anomaly $\to$ `MANUAL_REVIEW`.
- If confidence $< 0.55 \to$ `OBSERVE`.
- If blast radius $\ge 0.70$ or systemic scope $\to$ `HIGH_RISK_REPAIR`.
- If reversibility $< 0.50$ or determinism $< 0.60 \to$ `HIGH_RISK_REPAIR`.
- If confirmed/likely, confidence $\ge 0.70$, bounded blast radius, high reversibility & determinism $\to$ `DETERMINISTIC_REPAIR_CANDIDATE`.

---

## 19. Blast Radius, Reversibility, and Determinism Scoring

- **Blast Radius**:
  - `LOCAL`: $0.15$
  - `CLUSTER`: $0.40$
  - `SYSTEMIC`: $0.75$
  - `ARTIFACT_WIDE`: $0.95$
  Adjusted by exact page coverage ratio: $\text{Radius} = 0.60 \cdot \text{Base} + 0.40 \cdot \frac{\text{affected pages}}{\text{total pages}}$.
- **Reversibility**:
  - CSS / Typography / Geometry: $0.90$
  - Blueprint Regrouping: $0.60$
  - Transformation / Knowledge Model: $0.35$
  - Source Content: $0.20$
- **Determinism**:
  - Rendering / Composition: $0.85$
  - Semantic Layout: $0.80$
  - Blueprint: $0.70$
  - Ambiguous / Multi-hypothesis: $0.25$

---

## 20. Repair Authority Classification Matrix

| Recommended Authority | Criteria | Automated Repair Allowed? |
| :--- | :--- | :--- |
| `NO_ACTION` | Informational signals only, zero defect impact | No (Not Needed) |
| `OBSERVE` | Low confidence ($< 0.55$) or minor unconfirmed flaw | No (Monitor) |
| `MANUAL_REVIEW` | Ambiguous causes, validator anomaly, or safety-critical | **FORBIDDEN** |
| `HIGH_RISK_REPAIR` | Systemic/artifact-wide scope, blast radius $\ge 0.70$ | High-Risk Protocol Only |
| `DETERMINISTIC_REPAIR_CANDIDATE` | Confirmed cause, confidence $\ge 0.70$, low blast radius | **ALLOWED (Phase 3C)** |

---

## 21. Signal Lifecycle State Machine & Transition Audit Trail

Signals progress through strictly validated states:
`RAW_DETECTION` $\to$ `NORMALIZED` $\to$ `CORRELATED` $\to$ `CLUSTERED` $\to$ `CAUSAL_HYPOTHESIS`.
Every transition records timestamp, next state, and explicit rationale in `QualitySignalLifecycleRecord`.

---

## 22. Forensic Reporting Engine

The `CausalReporter` generates two output artifacts:
1. `causal_analysis.json`: Machine-readable forensic record.
2. `causal_analysis.md`: Markdown report strictly divided into:
   - **SECTION 1: OBSERVATIONS** (Empirical signals)
   - **SECTION 2: INFERENCES** (Clusters, competing hypotheses, readiness)
   - **SECTION 3: CONFIRMED CAUSES** (Authoritative attributions and evidence)

---

## 23. Presentation Artifact Causal Blueprint

- **Format**: 16:9 Presentation Slide Deck.
- **Common Defect Trajectory**: Dense source concepts allocated to single slide $\to$ Card slot geometry exceeded $\to$ Font size reduced below readability threshold ($6\text{pt}$) and text clipped.
- **Causal Attribution**: Root cause attributed to `LAYOUT_CAPACITY_EXCEEDED` at the `COMPOSITION` layer (with upstream pressure from `BLUEPRINT`).
- **Recommended Repair**: `CLASS_C_LAYOUT_REMAPPING` or `CLASS_D_BLUEPRINT_REGROUPING`.

---

## 24. Handout Artifact Causal Blueprint

- **Format**: A4 Multi-Page Comprehensive Reading Material.
- **Common Defect Trajectory**: Uncompressed academic paragraphs mapped directly to handout $\to$ `WALL_OF_TEXT` and `DENSITY_OVERLOAD` $\to$ Reading flow collapse.
- **Causal Attribution**: `CONTENT_OVERDENSITY` at the `SOURCE_CONTENT` layer.
- **Recommended Repair**: `CLASS_D_BLUEPRINT_REGROUPING` or `CLASS_E_TRANSFORMATION_STRATEGY`.

---

## 25. Worksheet Artifact Causal Blueprint

- **Format**: Inquiry-Based Worksheet / LKS.
- **Common Defect Trajectory**: Observation activity leaks scientific conclusion before student experiment $\to$ Anti-spoiling rule breached.
- **Causal Attribution**: `WORKSHEET_ANSWER_LEAKAGE` at `TRANSFORMATION` layer.
- **Scope & Gating**: `ARTIFACT_WIDE` scope, `CRITICAL` severity $\to$ Mandates `HIGH_RISK_REPAIR` or `CLASS_F_ARTIFACT_POLICY`.

---

## 26. Scientific Document Causal Blueprint

- **Format**: Academic Paper / KTI.
- **Common Defect Trajectory**: Inline citation callout `[12]` lacks matching reference entry $\to$ `SCIENTIFIC_CITATION_INVISIBLE`.
- **Causal Attribution**: `CITATION_STRUCTURE_FAILURE` at `KNOWLEDGE_MODEL` layer (distinguished from physical rendering clipping).
- **Scope & Gating**: `ARTIFACT_WIDE` scope $\to$ `CLASS_F_ARTIFACT_POLICY`.

---

## 27. Offline Determinism & Zero AI/LLM Dependency Guarantee

Phase 3B has zero runtime network calls, zero external API keys, and zero LLM dependencies. All calculations (hashing, connected components, 5D scoring, evidence weights, rule matching, ambiguity margins) are 100% deterministic Python standard library and Pydantic models.

---

## 28. Comprehensive Test Suite Accounting & Verification Results

### Truthful Test Accounting:
- **Prior Baseline Tests**: 68 tests (Phase 3A.2 contracts, scope policies, lifecycle transitions, Phase 3A.1 backward compatibility).
- **Phase 3B New Dedicated Tests**: 47 tests across 7 test files.
- **Total Active Test Suite**: **115 tests passed (100% Green, 0 Failures, 0 Regressions)** in 4.02 seconds.

### Test Breakdown by Module:
1. `tests/unit/quality/causal/test_phase_3b_correlation.py`: **10 passed** (Tests 1–10: 5D proximity, composite scoring, candidate indexing, determinism).
2. `tests/unit/quality/causal/test_phase_3b_clustering.py`: **8 passed** (Tests 11–18: connected components, deterministic IDs, singleton clusters, scope derivation).
3. `tests/unit/quality/causal/test_phase_3b_causality.py`: **10 passed** (Tests 19–28: symptom/cause separation, rule matching, competing hypotheses, lineage consistency, ambiguity).
4. `tests/unit/quality/causal/test_phase_3b_validator_anomaly.py`: **3 passed** (Tests 29–31: conflicting inspectors, fair competition, manual review gating).
5. `tests/unit/quality/causal/test_phase_3b_repair_readiness.py`: **5 passed** (Tests 32–36: authority levels, blast radius, determinism, zero repair execution).
6. `tests/unit/quality/causal/test_phase_3b_cross_artifact.py`: **7 passed** (Tests 37–43: Presentation, Handout, Worksheet, Scientific causal chains).
7. `tests/integration/test_phase_3b_golden_benchmark.py`: **4 passed** (End-to-end multi-artifact pipeline, clean artifact verification, JSON/MD reporting).

---

## 29. Known Edge Cases, Limitations & Hardening Guardrails

1. **Disconnected Multipage Cascades**: When a layout overflow on page 2 pushes headings onto page 3 and cards onto page 4, spatial proximity alone may fail; structural blueprint indexing bridges these signals into a unified cluster.
2. **Ambiguity Preservation Over Aggressive Decisions**: The engine purposefully blocks automated repair when $\Delta \le 0.10$, preferring `MANUAL_REVIEW` over an incorrect repair.
3. **Sparse Signals vs Dense Failure Fields**: Single-signal failures are handled as singleton clusters with appropriate conservative bounds.

---

## 30. Phase 3C Integration Contract & Forward Roadmap

Phase 3B formally delivers:
1. `CausalAnalysisResult`: Immutable container holding correlated clusters, competing hypotheses, and repair readiness assessments.
2. `causal_analysis.json` & `causal_analysis.md`: Authoritative forensic artifacts.
3. Explicit Gating: Phase 3C will ingest clusters marked `DETERMINISTIC_REPAIR_CANDIDATE` and generate `RepairProposal` transactions according to the recommended `CanonicalRepairClass`.

---
*End of Phase 3B Specification.*
