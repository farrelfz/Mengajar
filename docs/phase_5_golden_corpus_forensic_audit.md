# Phase 5 — Golden Artifact Corpus & Benchmark Certification: Forensic Architecture Audit

---

## 1. Executive Summary & Objective

Universal Document Intelligence System V5 requires a governed, reproducible, deterministic, versioned, and adversarial **Golden Artifact Corpus & Benchmark Certification** layer.
This audit forensically surveys the existing repository to establish exact symbols, interfaces, contracts, and integration points to build upon—without duplicating existing engines, without bypassing `UnifiedQualityAuthority`, and without creating parallel quality or certification authorities.

---

## 2. Answers to Explicit Forensic Audit Questions (A – O)

### A. Where does the existing benchmark infrastructure live?
The benchmark infrastructure resides in two complementary modules under `app/benchmarking/`:
1. **`app/benchmarking/` (Core & Generalization)**:
   - `contracts.py`: `BenchmarkFixtureMetadata`, `BenchmarkExecutionOutcome`, `GeneralizationMetrics`, `BenchmarkIntegrityReport`
   - `corpus_registry.py`: `BenchmarkCorpusRegistry`
   - `split_manager.py`: `CorpusSplitManager` (partitions fixtures into Training, Validation, Unseen Generalization, Adversarial)
   - `benchmark_runner.py`: `BenchmarkRunner` (orchestrates target execution with leakage protection)
   - `leakage_guard.py`: `BenchmarkLeakageGuard` (enforces anti-leakage during unseen/adversarial runs)
   - `metrics.py`: `GeneralizationMetricEngine`
   - `reports.py`: `BenchmarkReportGenerator`
2. **`app/benchmarking/golden_contracts.py` & `golden_registry.py`**:
   - `golden_contracts.py`: `GoldenCorpus`, `GoldenCase`, `GoldenArtifactReference`, `GoldenCorpusVersion`, `DimensionResult`, `BenchmarkEvaluation`, `ExpectedInvariants`, `VariationPolicy`, `CertificationDecision`, `CertificationStatus`
   - `golden_registry.py`: `GoldenCorpusRegistry`, `GoldenCorpusLoader`, `GoldenCorpusValidator`, `GoldenCorpusVersionManager`
3. **`app/benchmarking/comparison/`**:
   - `base.py`, `semantic.py`, `structural.py`, `visual.py`, `artifact_specific.py`
4. **`app/benchmarking/certification/`**:
   - `engine.py`: `CertificationEngine`
   - `policy.py`: `CertificationPolicy`
   - `regression_detector.py`: `RegressionDetector`

---

### B. What is the actual CertificationEngine API?
`CertificationEngine.certify(...)` in `app/benchmarking/certification/engine.py`:
```python
@classmethod
def certify(
    cls,
    artifact_id: str,
    golden_reference: GoldenArtifactReference,
    corpus_version: str,
    dimension_results: Dict[str, DimensionResult],
    hard_invariant_results: Dict[str, bool],
    historical_baseline: Optional[Dict[str, float]] = None
) -> BenchmarkEvaluation:
    ...
```
It returns an immutable `BenchmarkEvaluation` containing:
- `evaluation_id`, `artifact_id`, `golden_reference_id`, `corpus_version`, `benchmark_protocol_version`
- `dimension_results: Dict[str, DimensionResult]`
- `hard_invariant_results: Dict[str, bool]`
- `variation_interpretations: Dict[str, str]`
- `reference_alignment: float` (0.0 to 1.0)
- `regression_analysis: Dict[str, Any]` (`is_regression: bool`, dimension drop breakdown)
- `certification_decision: CertificationDecision`
- `reproducibility_metadata: Dict[str, Any]`

---

### C. What contracts already exist?
- **Benchmark Evaluation**: `BenchmarkEvaluation` (`app/benchmarking/golden_contracts.py`), `BenchmarkExecutionOutcome` (`app/benchmarking/contracts.py`).
- **Regression Detection**: `RegressionDetector` (`app/benchmarking/certification/regression_detector.py`), detecting drops exceeding `NOISE_THRESHOLD` (0.05) with `MIN_CONFIDENCE_FOR_REGRESSION` (0.80).
- **Certification Policy**: `CertificationPolicy` (`app/benchmarking/certification/policy.py`), evaluating hard invariant blockers, regressions, and threshold intervals (`EXCELLENT_THRESHOLD=0.90`, `ACCEPTABLE_THRESHOLD=0.70`, `MIN_DIMENSION_SCORE=0.50`).
- **Quality Reports**: `UnifiedQualityReport` (`app/quality/contracts/reports.py`), containing `domain_scores`, `dimension_scores`, `findings`, `finding_clusters`, `hard_blockers`, `warnings`, `decision`, `can_export`.
- **Provenance**: `QualityProvenanceGraph` (`app/quality/contracts/provenance.py`), tracking signal IDs, cluster links, findings, and decision lineage.
- **Artifact Identity**: `ArtifactType` enum in `app/intelligence/transformation/intent.py` (`PRESENTATION`, `HANDOUT`, `WORKSHEET`, `SCIENTIFIC_DOCUMENT`).

---

### D. Where are fixtures currently located?
1. `tests/fixtures/`:
   - Raw markdown inputs: `oobleck_experiment.md`, `hand_fire_full.md`, `experiment.md`, `simple_physics.md`, `mixed_semantics.md`, `tutorial_sample.md`, `kti_bab1.md` through `kti_bab5.md`.
2. `tests/fixtures/benchmark/`:
   - `01_oobleck_experiment.md` through `07_data_heavy_research.md`.
3. `tests/fixtures/benchmark_corpus/`:
   - Curated suite of 16 markdown documents + `.meta.json` companion metadata files covering experiments, concepts, narratives, scientific papers, and pathological cases.
4. `tests/fixtures/adversarial/`:
   - Subdirectories: `presentation/dense_slide.json`, `handout/hierarchy_inversion.json`, `worksheet/answer_leak.json`, `scientific/unsupported_claim.json`.

---

### E. How are fixtures currently loaded?
1. `FixtureMetadataAnalyzer.load_or_infer_metadata(md_file)` parses markdown frontmatter/structure and companion `.meta.json` files.
2. `BenchmarkCorpusRegistry.scan_directory(corpus_dir)` iterates through directory files and registers them.
3. `GoldenCorpusLoader.load_from_file(filepath)` loads the complete serialized `GoldenCorpus` JSON.

---

### F. Does the repository already have registries, metadata, versioning, snapshots, reports?
- **Fixture Registry**: Yes, `BenchmarkCorpusRegistry` (`app/benchmarking/corpus_registry.py`) and `GoldenCorpusRegistry` (`app/benchmarking/golden_registry.py`).
- **Corpus Metadata**: Yes, `BenchmarkFixtureMetadata` (`app/benchmarking/contracts.py`) and `GoldenCase` (`app/benchmarking/golden_contracts.py`).
- **Baseline Versioning**: Yes, `GoldenCorpusVersionManager` and `GoldenCorpusVersion` (`app/benchmarking/golden_contracts.py`).
- **Artifact Snapshots**: Raw state dictionaries captured during execution and stored in `references` within `GoldenCase`.
- **Historical Benchmark Reports**: Yes, `BenchmarkReportGenerator` (`app/benchmarking/reports.py`) outputs `generalization_report.json`, `generalization_report.md`, and `operator_matrix.json`.

---

### G. How does `UnifiedQualityAuthority` expose quality signals?
`UnifiedQualityAuthority.assess(...)` executes 4 truth layers (Semantic, Fidelity, Artifact Quality, Rendered Quality). It aggregates raw signals into `UnifiedQualityReport` containing:
- `overall_quality_score: float` (0.0 to 1.0)
- `domain_scores: Dict[str, float]` (`semantic_integrity`, `artifact_fidelity`, `artifact_quality`, `rendered_quality`)
- `dimension_scores: Dict[str, DimensionScore]`
- `hard_blockers: Tuple[str, ...]`
- `findings: Tuple[QualityFinding, ...]`
- `decision: ExportDecision` (`APPROVED`, `APPROVED_WITH_WARNINGS`, `REPAIR_REQUIRED`, `BLOCKED`, `MANUAL_REVIEW_REQUIRED`)
- `can_export: bool`

---

### H. How can Phase 5 consume quality reports WITHOUT creating another quality authority?
Phase 5 treats `UnifiedQualityAuthority` as the **sole Level-0 source of truth** for artifact quality.
1. The production pipeline or test harness invokes `ProductionOrchestrator.produce(...)` or `UnifiedQualityAuthority.assess(...)`.
2. The resulting `UnifiedQualityReport` is ingested by the benchmark evaluation adapters.
3. Benchmark dimensions (`SEMANTIC`, `STRUCTURAL`, `VISUAL`, `PEDAGOGICAL`, `SCIENTIFIC`) extract measurements directly from `UnifiedQualityReport.domain_scores`, `dimension_scores`, and `hard_blockers`.
4. `CertificationEngine` compares these measurements to the `GoldenArtifactReference` and historical baseline.
5. **Separation of Concerns**: `UnifiedQualityAuthority` decides *Can this artifact be exported right now?* while `CertificationEngine` decides *Has the system's generator improved, remained stable, or regressed over time?*

---

### I. How can the existing `ProductionOrchestrator` be invoked reproducibly?
Via `ProductionOrchestrator.produce(request)` with `ProductionRequest`:
```python
req = ProductionRequest(
    raw_input=raw_source,
    artifact_type=artifact_type,
    output_dir=job_out_dir,
    output_filename=fixture_id,
    source_filename=f"{fixture_id}.md",
    max_repair_iterations=max_repair_iterations,
)
outcome: ProductionOutcome = await orchestrator.produce(req)
```
Inside `BenchmarkRunner.run_target(...)`, execution is wrapped in `BenchmarkLeakageGuard(metadata.split)` ensuring zero mutation of persistent operator registries during unseen or adversarial evaluation.

---

### J. Where should Golden Corpus metadata live?
In a dedicated governed directory:
`golden_corpus/`
  ├── `corpus_manifest.json`
  ├── `corpus_version.json`
  ├── `cases/`
  │     ├── `case_oobleck/`
  │     │     ├── `source.md`
  │     │     ├── `case_metadata.json`
  │     │     ├── `references/` (presentation, handout, worksheet, scientific_document references)
  │     │     └── `adversarial/` (twin variants)
  │     └── `case_hand_fire/` ...
  └── `baselines/`
        ├── `v1.0.0_baseline.json`
        └── `lineage.json`

---

### K. How should corpus artifacts be versioned?
Using `GoldenCorpusVersionManager`:
Each version is an immutable `GoldenCorpusVersion` record containing:
- `version: str` (semantic versioning, e.g. "1.0.0")
- `parent_version: Optional[str]`
- `change_summary: str`
- `created_at: float`
- `created_by: str`
- `review_provenance: str`
- Content SHA-256 digests of all constituent fixture sources and reference files.

---

### L. What currently prevents benchmark baselines from being silently replaced?
1. Content hashing (`BenchmarkFixtureMetadata.compute_hash`) detects source file tampering (`verify_immutability()`).
2. Phase 5 will add **Anti-Benchmark-Laundering Governance**: A validation check rejecting any baseline update that lacks:
   - explicit `change_reason`,
   - `expected_quality_impact`,
   - `previous_baseline_reference`,
   - `change_classification` (e.g. `LEGITIMATE_CORRECTION`, `FIXTURE_ERROR`, `POLICY_EVOLUTION`).
3. If baseline scores are lowered without classification as a breaking/policy change, the system flags `BENCHMARK_LAUNDERING_ATTEMPT`.

---

### M. Which existing provenance mechanisms can be reused?
1. `QualityProvenanceGraph` (`app/quality/contracts/provenance.py`): tracks signal-to-cluster-to-finding-to-decision graphs.
2. `TransformationTraceabilityEngine` (`app/intelligence/transformation/traceability.py`): tracks knowledge unit mappings from source manifest into blueprint elements.
3. `reproducibility_metadata` in `BenchmarkEvaluation`: stores execution timestamp, environment parameters, and commit/version tags.

---

### N. What is the safest integration point for full corpus replay?
Extending `BenchmarkRunner` (`app/benchmarking/benchmark_runner.py`) and providing a dedicated CLI/script harness `scripts/replay_golden_corpus.py` (and an equivalent Python module API in `app/benchmarking/replay_harness.py`).
This harness:
- reads `GoldenCorpusRegistry`,
- wraps execution in `BenchmarkLeakageGuard`,
- invokes `ProductionOrchestrator` or offline transformers,
- evaluates outputs via `ComparisonEngine` against `GoldenArtifactReference`,
- certifies via `CertificationEngine`,
- reports via `BenchmarkReportGenerator`.

---

### O. Can benchmark generation be executed deterministically offline?
Yes!
The compilation and transformation pipeline supports:
- `KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())` (runs offline without LLM calls),
- Deterministic heuristic transformers: `PresentationTransformer`, `HandoutTransformer`, `WorksheetTransformer`, `ScientificDocumentTransformer`,
- Offline comparison models (`SemanticComparison`, `StructuralComparison`, `VisualComparison`, `create_pedagogical_comparison`),
- Deterministic quality authority scoring via `MasterQualityScoringEngine` and `UnifiedQualityAuthority`.

---

## 3. Repository Architecture Map

```
app/benchmarking/
├── contracts.py                  # Generalization contracts & execution outcomes
├── taxonomy.py                   # CorpusSplit, CorpusCategory, FailureTaxonomy
├── golden_contracts.py           # GoldenCorpus, GoldenCase, Reference, Evaluation
├── golden_registry.py            # GoldenCorpusRegistry, Loader, Validator, VersionManager
├── comparison/                   # Multi-dimension comparison engines
│   ├── base.py
│   ├── semantic.py
│   ├── structural.py
│   ├── visual.py
│   └── artifact_specific.py
├── certification/                # Certification engine & regression detection
│   ├── engine.py                 # CertificationEngine.certify(...)
│   ├── policy.py                 # CertificationPolicy.evaluate(...)
│   └── regression_detector.py    # RegressionDetector.detect(...)
├── corpus_registry.py            # BenchmarkCorpusRegistry
├── split_manager.py              # CorpusSplitManager
├── leakage_guard.py              # BenchmarkLeakageGuard (anti-leakage)
├── benchmark_runner.py           # BenchmarkRunner
├── metrics.py                    # GeneralizationMetricEngine
└── reports.py                    # BenchmarkReportGenerator

tests/fixtures/
├── oobleck_experiment.md         # Canonical source 1 (Experimental non-Newtonian)
├── hand_fire_full.md             # Canonical source 2 (Experimental thermodynamics)
├── benchmark_corpus/             # 16 domain fixtures
└── adversarial/                  # Adversarial twins (dense, leak, unsupported, inversion)
```

---

## 4. Key Extension Points vs. Duplication Guards

| Requirement | Existing Component to Extend | Duplication Guard (DO NOT CREATE) |
|---|---|---|
| **Corpus Data Model** | `app/benchmarking/golden_contracts.py` | Do not create parallel corpus models |
| **Corpus Storage/Load** | `app/benchmarking/golden_registry.py` | Do not create secondary file loaders |
| **Scoring / Comparison** | `app/benchmarking/comparison/` | Do not create independent scoring authority |
| **Certification Decision** | `app/benchmarking/certification/engine.py` | Do not create competing certification engine |
| **Policy Thresholds** | `app/benchmarking/certification/policy.py` | Do not hardcode ad-hoc thresholds in tests |
| **Regression Checking** | `app/benchmarking/certification/regression_detector.py` | Do not compute ad-hoc diffs without noise filter |
| **Leakage Protection** | `app/benchmarking/leakage_guard.py` | Always wrap test runs in `BenchmarkLeakageGuard` |
| **Export Decisions** | `UnifiedQualityAuthority` | Never let benchmark engine grant export approval |

---

## 5. Detailed Implementation Plan for Phase 5

1. **Step 5.1: Golden Corpus Taxonomy & Governance Contracts**
   - Formalize taxonomy in `app/benchmarking/taxonomy.py` and `golden_contracts.py` (Categories: `EXPERIMENTAL_PHENOMENA`, `TEACHING_CONCEPTS`, `SCIENTIFIC_RESEARCH`, `DENSE_CURRICULUM`).
   - Add `GovernanceMetadata` and `AntiLaunderingPolicy` in `app/benchmarking/governance.py`.
2. **Step 5.2: Expected Characteristics & Forbidden Failures Contracts**
   - Create `ExpectedCharacteristicsContract` and `ForbiddenFailuresContract` in `app/benchmarking/golden_contracts.py`.
   - Formalize `MUST_HAVE`, `MUST_NOT_HAVE`, `ACCEPTABLE_VARIATION`, and `HARD_INVARIANTS` per artifact type.
3. **Step 5.3: Canonical Golden Corpus Fixtures**
   - Create governed `golden_corpus/` directory structure.
   - Populate Case 1: `oobleck_experiment` (Non-Newtonian Fluid) across all 4 artifact references.
   - Populate Case 2: `hand_fire_full` (Thermodynamics & Heat Transfer) across all 4 artifact references.
   - Attach explicit expected contracts, forbidden failures, and blueprints for each artifact.
4. **Step 5.4: Adversarial Twin Corpus**
   - Populate adversarial variants for each case (e.g. wall-of-text presentation, answer-leaked worksheet, unsupported-claim scientific document, slide-fragmented handout).
5. **Step 5.5: Cross-Artifact Divergence Benchmark**
   - Implement `CrossArtifactDivergenceBenchmark` in `app/benchmarking/divergence.py` calculating semantic divergence scores and verifying that high source overlap does NOT cause structural homogenization.
6. **Step 5.6: Anti-Benchmark-Laundering Governance Guard**
   - Implement `AntiLaunderingGuard` in `app/benchmarking/governance.py` enforcing immutable lineage, change reasons, and regression protection.
7. **Step 5.7: Full Corpus Replay Harness & Reporting**
   - Implement `CorpusReplayHarness` (`app/benchmarking/replay_harness.py`) and `scripts/replay_golden_corpus.py`.
   - Support machine-readable `benchmark_report.json` and human-readable `benchmark_report.md`.
8. **Step 5.8: Comprehensive Testing & Verification**
   - Unit tests for governance, expected characteristics, forbidden failures, divergence benchmark, and adversarial twins.
   - Integration tests executing full replay on the golden corpus.
   - Full regression suite verification.
