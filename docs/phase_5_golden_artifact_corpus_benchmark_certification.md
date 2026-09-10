# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 5 — GOLDEN ARTIFACT CORPUS & BENCHMARK CERTIFICATION
# ARCHITECTURAL SPECIFICATION & CERTIFICATION REPORT

---

## 1. Problem Statement & Historical Context
In complex multi-format document synthesis pipelines, adding arbitrary test fixtures produces an illusion of coverage. Without governed references and regression boundaries, systems suffer from:
1. **Silent Quality Erosion**: Subtle degradation in layout density, explanation depth, or inquiry integrity goes unnoticed if tests only assert exit codes.
2. **Benchmark Laundering**: Developers faced with failing tests quietly lower baseline thresholds or substitute easier fixtures, wiping out historical standard memory.
3. **Artifact Homogenization**: Under high source knowledge overlap, different document targets (slides, reading texts, inquiry worksheets, formal papers) silently collapse into the same cosmetic structure with different CSS.
4. **Authority Conflation**: Overriding or duplicating production quality gates with ad-hoc benchmark formulas.

Phase 5 addresses these risks by establishing a **governed, immutable, reproducible, multi-dimensional Golden Artifact Corpus & Benchmark Certification System**.

---

## 2. Why Fixtures Alone Are Insufficient
A raw Markdown fixture (e.g. `oobleck_experiment.md`) only specifies *what raw knowledge exists*. It does not declare:
- What *good* looks like for each specific target format.
- What variations are permissible (e.g., color palette vs. structural hierarchy).
- What failures are strictly forbidden (e.g., answer leaks on worksheets).
- Whether an observed score difference reflects random measurement noise or a genuine architectural regression.

The Golden Corpus solves this by pairing raw source knowledge with **governed reference contracts, expected characteristics, forbidden failure taxonomies, and adversarial mutant twins**.

---

## 3. Golden Corpus Philosophy & Absolute Invariants
- **INVARIANT 1 (Level-0 Authority)**: `UnifiedQualityAuthority` remains the sole arbiter of production export safety. Benchmarks are observers, never controllers.
- **INVARIANT 2 (No Parallel Systems)**: Reuses and extends `GoldenCorpusRegistry`, `CertificationEngine`, `CertificationPolicy`, and `RegressionDetector`.
- **INVARIANT 3 (Immutability by Default)**: Every corpus version is locked with content SHA-256 digests and explicit parent lineage.
- **INVARIANT 4 (Zero Benchmark Laundering)**: Baseline score adjustments require substantive reasons, impact declarations, and governed classifications (`POLICY_EVOLUTION`, `LEGITIMATE_CORRECTION`). Silent score reductions raise `BENCHMARK_LAUNDERING_ATTEMPT`.
- **INVARIANT 5 (Unseen Isolation)**: Wrapped in `BenchmarkLeakageGuard` to ensure unseen benchmarks never mutate adaptive operator memory.
- **INVARIANT 6 (Offline Determinism)**: 100% executable offline without runtime LLM or web dependencies.

---

## 4. Architecture Overview

```
SOURCE FIXTURE (e.g., oobleck_experiment.md)
      │
      ▼
GOVERNED GOLDEN CASE (GOLDEN_OOBLECK)
      │
      ├─────────────────────────────────────────┐
      ▼                                         ▼
PRODUCTION ORCHESTRATION / HARNESS       GOLDEN ARTIFACT REFERENCE
      │                                         │
      ▼                                         ├─ Expected Characteristics
UNIFIED QUALITY AUTHORITY (Level-0)             ├─ Forbidden Failures
      │                                         ├─ Hard Invariants
      ▼                                         └─ Acceptable Variations
BENCHMARK DIMENSION EXTRACTOR                   │
      │                                         │
      ▼                                         ▼
MULTI-DIMENSION COMPARISON (Semantic, Structural, Visual, Pedagogical, Scientific)
      │
      ▼
CROSS-ARTIFACT DIVERGENCE BENCHMARK (Detects Collapse & Homogenization)
      │
      ▼
REGRESSION DETECTOR (Noise Filtered: Δ > 0.05, Conf ≥ 0.80)
      │
      ▼
CERTIFICATION POLICY (Hard Invariants & Multi-Tier Thresholds)
      │
      ▼
CERTIFICATION DECISION (EXCELLENT, ACCEPTABLE, WARNINGS, REGRESSION, INSUFFICIENT, REVIEW)
      │
      ▼
IMMUTABLE REPLAY REPORT (benchmark_evaluation.json & benchmark_evaluation.md)
```

---

## 5. Corpus Taxonomy
Standardized categorical partitions (`app/benchmarking/taxonomy.py`):
1. **EXPERIMENTAL_PHENOMENA (`EXPERIMENT_HEAVY`)**: Observable events, variables, procedures, predictions, and empirical observations (e.g. Oobleck, Hand Fire).
2. **TEACHING_CONCEPTS (`CONCEPT_HEAVY`)**: Conceptual hierarchies, definitions, misconceptions, worked examples, and formal laws (e.g. Rotational Dynamics, Harmonic Motion).
3. **SCIENTIFIC_RESEARCH (`SCIENTIFIC_HEAVY`)**: Formal research questions, Claim-Evidence-Reasoning, empirical data, limitations, and citations (e.g. Microalgae Climate Mitigation, Perovskite Photovoltaics).
4. **DENSE_CURRICULUM**: Heavy multi-concept domains designed to stress cognitive load, compression, and layout pacing (e.g. Thermodynamics, Electromagnetism).

---

## 6. Fixture Contract & Governed Directory Structure
Located at `golden_corpus/`:
```
golden_corpus/
├── corpus_manifest.json          # Root GoldenCorpus specification
├── corpus_version.json           # Active version metadata & digest
├── cases/                        # Governed Case definitions
│   ├── oobleck/
│   │   └── references/           # 4 artifact references & expectations
│   └── hand_fire/
│       └── references/           # 4 artifact references & expectations
├── baselines/                    # Historical score baselines & lineage records
│   ├── v1.0.0_baseline.json
│   └── lineage.json
└── governance/                   # Policy records & mutation audits
```

Each Golden Case declares:
- `case_id`: Unique identifier (e.g., `GOLDEN_OOBLECK`, `GOLDEN_HAND_FIRE`).
- `source_path` & `source_hash`: Cryptographic binding to immutable source text.
- `references`: Dictionary of format-specific `GoldenArtifactReference` instances across the 4 artifact targets.

---

## 7. Expected Characteristics System
Instead of fragile pixel-perfect matching, `ExpectedCharacteristics` declares functional and cognitive invariants:
- **`must_have`**: Mandatory structural and pedagogical traits (e.g. `progressive_disclosure` on slides, `5_layer_explanation` on handouts, `withheld_answers` on worksheets).
- **`must_not_have`**: Absolute negative traits (e.g. `wall_of_text`, `answer_leak`, `quiz_collapse`, `unsupported_claims`).
- **`preferred`**: Quality differentiators (e.g. `worked_examples`, `diagram_focal_point`).
- **`acceptable_variation`**: Explicitly permitted degrees of freedom (e.g. `color_palette`, `table_dimension`, `callout_styling`).

---

## 8. Forbidden Failure System
Standardized failure codes mapped to each artifact format (`ForbiddenFailures`):
- **PRESENTATION**: `WALL_OF_TEXT`, `PRESENTATION_HANDOUT_COLLAPSE`, `COGNITIVE_OVERLOAD`.
- **HANDOUT**: `SLIDE_FRAGMENTATION`, `WALL_OF_TEXT`, `READING_FLOW_BREAK`.
- **WORKSHEET**: `ANSWER_LEAK`, `QUIZ_COLLAPSE`, `INQUIRY_ARC_BROKEN`.
- **SCIENTIFIC_DOCUMENT**: `UNSUPPORTED_CLAIM`, `FABRICATED_CITATION`, `CER_BREAK`.

---

## 9. Adversarial Twin Corpus
Every golden case is accompanied by paired adversarial mutant fixtures (`AdversarialVariant`) that verify validator sensitivity:
1. **Worksheet with Answer Leak**: Injects the discovery conclusion directly into the observation prompt.
2. **Worksheet with Quiz Collapse**: Strips all inquiry/experiment steps, reducing the sheet to pure factual recall.
3. **Presentation with Wall of Text**: Inundates slides with >85 words per card.
4. **Handout with Hierarchy Inversion**: Abruptly skips from H1 to H3 without intermediate context.
5. **Scientific Document with Unsupported Claim**: Asserts causal claims without supporting empirical or literature evidence.

---

## 10. Cross-Artifact Divergence Benchmark
Located in `app/benchmarking/divergence.py`:
- **Core Principle**: High knowledge overlap from a shared source is expected, but structural and pedagogical divergence must remain $\ge 0.50$.
- **Detection**:
  - Computes pairwise sequence matcher divergence across native structural containers (`slides`, `sections`, `activities`, `arguments`).
  - Penalizes specific collapse modes (`PRESENTATION_TO_HANDOUT_COLLAPSE`, `WORKSHEET_TO_ANSWER_LEAK`, `WORKSHEET_TO_QUIZ_COLLAPSE`, `SCIENTIFIC_TO_GENERIC_ESSAY_COLLAPSE`).
  - Flags `CROSS_ARTIFACT_HOMOGENIZATION` if two different artifact formats share $>80\%$ structural identity.

---

## 11. Baseline Versioning & Lineage
Governed by `GoldenCorpusVersionManager`:
- Corpus transitions (e.g. `1.0.0` $\rightarrow$ `1.1.0`) are recorded in an immutable DAG.
- Each transition records `parent_version`, `change_summary`, `created_by`, `timestamp`, and `content_digest`.
- Attempting to update a corpus without version increment raises `ValueError`.

---

## 12. Anti-Benchmark-Laundering Governance
Located in `app/benchmarking/governance.py`:
- **`AntiLaunderingGuard`** actively validates all proposed baseline changes:
  1. Rejects mutations classified as `UNKNOWN_CHANGE`.
  2. Requires substantive `change_reason` ($\ge 15$ characters).
  3. Enforces unbroken `previous_baseline_reference` lineage.
  4. Detects silent baseline lowering: lowering score targets is blocked unless classified as `POLICY_EVOLUTION` or `LEGITIMATE_CORRECTION` with detailed impact documentation.
  5. Any unauthorized attempt raises `BenchmarkLaunderingAttemptError` with code `BENCHMARK_LAUNDERING_ATTEMPT`.

---

## 13. Regression Integration
Integrated with `RegressionDetector` (`app/benchmarking/certification/regression_detector.py`):
- **Dimensional Granularity**: Compares dimension-by-dimension (`SEMANTIC`, `STRUCTURAL`, `VISUAL`, `PEDAGOGICAL`, `SCIENTIFIC`), preventing aggregate scores from masking drops in critical sub-metrics.
- **Noise Filtering**: Ignores variations $\le 0.05$ to eliminate non-deterministic scoring jitter.
- **Confidence Gate**: Requires confidence $\ge 0.80$ before certifying a regression.

---

## 14. Certification Policy & Decisions
Executed by `CertificationEngine` and `CertificationPolicy`:
1. **Hard Invariant Failure** $\rightarrow$ `BENCHMARK_INSUFFICIENT`.
2. **Material Regression** $\rightarrow$ `BENCHMARK_REGRESSION`.
3. **Single Dimension Collapse (< 0.50)** $\rightarrow$ `MANUAL_BENCHMARK_REVIEW_REQUIRED`.
4. **Acceptable Average with Minor Weakness** $\rightarrow$ `CERTIFIED_WITH_WARNINGS`.
5. **Score $\ge 0.90$ across all dimensions** $\rightarrow$ `CERTIFIED_EXCELLENT`.
6. **Score $\ge 0.70$ across all dimensions** $\rightarrow$ `CERTIFIED_ACCEPTABLE`.

---

## 15. Replay Harness & CLI Architecture
- **API**: `CorpusReplayHarness` (`app/benchmarking/replay_harness.py`).
- **CLI**: `scripts/replay_golden_corpus.py` supporting `--full`, `--case`, `--artifact-type`, and `--output-dir`.
- **Leakage Protection**: All replay passes are wrapped in `BenchmarkLeakageGuard(CorpusSplit.VALIDATION_REFERENCE)` to prevent polluting adaptive repair operator registries.

---

## 16. Reporting Deliverables
Replay generates:
1. `output/benchmark_reports/benchmark_evaluation.json`: Machine-readable evaluation dump with full reproducibility metadata.
2. `output/benchmark_reports/benchmark_evaluation.md`: Human-readable certification matrix, divergence summary, and invariant audits.

---

## 17. Determinism Guarantees
- 100% reproducible offline execution.
- Zero network or LLM API calls.
- Purely deterministic AST/heuristic compilation and invariant checking.

---

## 18. Testing & Verification Summary
- `tests/unit/benchmarking/test_golden_corpus_phase5.py`: **26 tests passed**.
- Full benchmarking suite (`tests/unit/benchmarking/`): **69 tests passed**.
- Intelligence & Blueprint hardening suite: **75 tests passed**.
- Total targeted suite: **144 tests passed in 3.53s**.

---

## 19. Known Limitations
- Current initial Golden Corpus contains 2 canonical experimental cases (`GOLDEN_OOBLECK` and `GOLDEN_HAND_FIRE`) across 8 reference targets. Expansion to include additional conceptual and formal KTI cases can proceed under the established `GoldenCorpusVersionManager`.
- Rendering tests currently evaluate structural, visual, and pedagogical metrics; pixel rasterization comparison is deferred to optional visual regression diff tooling.

---

## 20. Future Phase 6 Integration (Human Review Studio)
Phase 5 prepares clean, typed data structures for Phase 6 consumption:
- `BenchmarkEvaluation` (records certification decisions and regression details).
- `CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED` (identifies cases requiring human sign-off).
- `CrossArtifactDivergenceReport` (highlights collapse warnings for human pedagogical inspection).
- No UI or review application logic was built, preserving strict Phase 5 boundaries.
