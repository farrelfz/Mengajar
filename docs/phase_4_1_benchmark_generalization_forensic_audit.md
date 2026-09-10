# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 4.1 — BENCHMARK GENERALIZATION FORENSIC AUDIT
## Architectural Investigation of Corpus Representation, Operator Generalization, and Evaluation Biases

---

## 1. Executive Summary & Audit Purpose

Phase 4 established true physical repair actuation across five mutation layers, achieving 100% blocker elimination on the canonical 8-job production benchmark suite. However, forensic analysis reveals a fundamental architectural risk: **the Phase 4 benchmark corpus is heavily overfitted to two experiment-heavy physics fixtures (`oobleck_experiment.md` and `hand_fire_full.md`)**.

This forensic audit maps existing fixtures, actuators, performance registries, quality scoring routines, and orchestration harnesses to determine:
1. Exact locations of implicit benchmark and content-type assumptions.
2. The degree to which repair operators generalize to non-experimental, highly dense, narrative, or pathological structures.
3. Vulnerabilities where evaluation scripts or scoring functions contain fixture-specific heuristics.
4. Structural gaps in reporting infrastructure preventing corpus-level aggregation and generalization gap measurement.

---

## 2. Current Benchmark Corpus Mapping

### 2.1 Existing Repository Fixtures
- **Production Golden Benchmarks** (`tests/fixtures/`):
  - `oobleck_experiment.md` (38.6 KB): High-density fluid mechanics experiment with hypothesis, variable tables, procedures, and calculations.
  - `hand_fire_full.md` (13.5 KB): Combustion experiment with heat capacity, butane stoichiometry, and safety protocols.
- **Phase 2C Cross-Fixture Calibration Corpus** (`tests/fixtures/benchmark/`):
  - `01_oobleck_experiment.md` (Experiment)
  - `02_dinamika_rotasi.md` (3.2 KB, Concept-heavy physics)
  - `03_gerak_melingkar.md` (3.1 KB, Concept-heavy physics)
  - `04_hand_fire.md` (Experiment)
  - `05_short_concept.md` (0.5 KB, Sparse conceptual stub)
  - `06_long_material.md` (15.9 KB, Multi-chapter thermodynamics)
  - `07_data_heavy_research.md` (3.5 KB, Data table / numerical evidence)
- **Modular Academic Fixtures** (`tests/fixtures/`):
  - `kti_bab1.md` through `kti_bab5.md`: Fragmented chapters of an Indonesian scientific paper.
  - `tutorial_sample.md`: Pedagogical walkthrough.
  - `simple_physics.md`: Minimal 500-byte concept stub.

### 2.2 Forensic Finding: The Experiment-Heavy Bias
Currently, 100% of production convergence testing in Phase 3D, Phase 3D.1, and Phase 4 was executed exclusively on `oobleck_experiment` and `hand_fire_full`. Both fixtures share a nearly identical epistemic profile:
- Both describe physical lab experiments with hands-on mixtures/combustion.
- Both contain formal hypothesis statements, controlled variable lists, and step-by-step apparatus setups.
- Neither tests pure narrative history, abstract mathematical axiomatization, formal legal/policy analysis, or intentionally broken/pathological layouts (e.g. deeply nested headings, extreme token density, formula-only clusters).

---

## 3. Operator Generalization & Content-Type Assumptions

| Operator | Owning Layer | Implicit Structural Assumptions | Vulnerability on Non-Experiment Inputs |
| :--- | :--- | :--- | :--- |
| `TypographyConstraintSolver` | Layer 1 (Token) | Linear box model height estimation based on average character width and line height. | Robust to content types; however, extreme formula density with non-standard glyph heights may skew height estimates. |
| `PresentationComponentReflowActuator` | Layer 2 (Component) | Card layout with standard text and bullet items. | Assumes card components can be reflowed by adjusting flex basis and padding without altering semantic order. |
| `PresentationFormulaRecompositionActuator` | Layer 2 (Component) | Math expressions enclosed in LaTeX `$$` or KaTeX markup. | Fails silently or provides zero effect if formula strings use plain text Unicode (e.g. `x² + y² = z²`) instead of LaTeX markup. |
| `PresentationCompositionActuator` | Layer 3 (Composition) | Horizontal slide overflows can be resolved by converting to 2-column or 3-column CSS grid layouts. | Assumes number of cards on slide is factorable (e.g. 2, 4, 6). For prime numbers of cards (e.g. 5 or 7 cards), creates unbalanced grid orphans. |
| `PresentationSlideSplitActuator` | Layer 4 (Blueprint) | Slide contains atomic `key_blocks` or `cards` that can be partitioned across continuation slides. | If a single giant card exceeds 540pt by itself (e.g. monolithic table or unbroken paragraph), split actuator cannot partition internal card content. |
| `WorksheetInquiryRecompositionActuator` | Layer 5 (Semantic) | Restructures activities into a 7-stage scientific inquiry arc (`PHENOMENON` -> `PREDICTION` -> `OBSERVATION` -> `INVESTIGATION` -> `DATA_ANALYSIS` -> `REFLECTION`). | **High Vulnerability**: Prompts explicitly reference experimental observation (`Tabel observasi`, `Langkah investigasi`). When applied to non-experimental topics (e.g. philosophical ethics, pure algebra, historical analysis), these prompts produce semantically incongruous exercises. |
| `ScientificCitationActuator` | Layer 5 (Semantic) | Injects formal bibliography and links citations to argument claims. | Assumes academic citation format and availability of concept claims in source manifest. |
| `ScientificEvidenceActuator` | Layer 5 (Semantic) | Grounds ungrounded claims with empirical observation text. | If source document contains zero empirical observations (e.g. purely normative or conceptual claims), actuator cannot manufacture evidence ($D_{\\text{trace}} = 0$). |

---

## 4. Codebase Audit: Hardcoded Heuristics & Leakage Risks

### 4.1 Keyword Contamination in Quality Scoring
- Located in `app/quality/calibration/quality_scoring.py` (Line 612):
  ```python
  if any(k in prompt_lower for k in ["jawaban:", "karena oobleck berubah menjadi padat", "kesimpulan sudah terbukti"]):
  ```
  - **Forensic Diagnosis**: The literal string `"karena oobleck berubah menjadi padat"` was hardcoded directly inside the generic anti-spoiling scoring logic to detect a specific fixture leak.
  - **Architectural Impact**: This constitutes a fixture-specific leakage contamination. If an unseen fixture has a similar leak with different text (e.g. `"karena es meleleh saat dipanaskan"`), it would bypass this specific check unless matched by generic rules.

### 4.2 Benchmark Replay Script Hardcoding
- Located in `scripts/replay_convergence_benchmark.py`:
  - Fixtures are hardcoded to a 2-element list:
    ```python
    benchmarks = [
        ("oobleck_experiment", Path("tests/fixtures/oobleck_experiment.md")),
        ("hand_fire_full", Path("tests/fixtures/hand_fire_full.md")),
    ]
    ```
  - Output is saved directly to `outputs/benchmarks/phase_3d_1/` without corpus partitioning or split management.

### 4.3 Adaptive Learning & Benchmark Leakage
- In `app/quality/repair/actuation/learning.py`:
  - `RepairOperatorPerformanceRegistry` records every execution into a singleton dictionary `self._records`.
  - **Leakage Risk**: If an unseen benchmark fixture executes a repair during validation, `RepairOperatorPerformanceRegistry.record_execution()` modifies the singleton operator weights. Subsequent fixtures evaluated in the same process would experience state leakage from the held-out test fixture!

---

## 5. Required Architectural Subsystems for Phase 4.1

To transform the benchmark infrastructure into a scientifically sound generalization testbed, the following canonical subsystems must be constructed:

1. **Benchmark Taxonomy & Contracts (`app/benchmarking/`)**:
   - Explicit categorization: `CONCEPT_HEAVY`, `EXPERIMENT_HEAVY`, `NARRATIVE_HEAVY`, `SCIENTIFIC_HEAVY`, `PATHOLOGICAL`.
   - Machine-readable metadata schema (`BenchmarkFixtureMetadata`).
   - Formal failure taxonomy (`GeneralizationFailureType`).
2. **Deterministic Split Manager (`split_manager.py`)**:
   - Partitioning into `TRAINING_REFERENCE`, `VALIDATION_REFERENCE`, `UNSEEN_GENERALIZATION`, and `ADVERSARIAL`.
   - Explicit, persisted split manifest with cryptographic hashing of source content.
   - Anti-leakage isolation: In `UNSEEN_GENERALIZATION` mode, the operator performance registry is placed in read-only / isolated mode so evaluation outcomes do not contaminate operator weights.
3. **Generalization Metric Engine (`metrics.py`)**:
   - Repair Generalization Rate (RGR), Repair Regression Rate (RRG), False Repair Rate (FRR), Causal Resolution Rate (CRR), Zero-Effect Rate (ZER).
   - Known vs. Unseen Generalization Gap ($\\Delta G = \\text{Score}_{\\text{known}} - \\text{Score}_{\\text{unseen}}$).
   - Distribution metrics: worst-case performance, blocker percentiles, entropy preservation.
4. **Operator Applicability Envelope (`operator_analysis.py`)**:
   - Evidence-based mapping of supported vs. unsupported structural signatures, root causes, and artifact types.
   - Categorization of evidence strength: `INSUFFICIENT`, `LIMITED`, `MODERATE`, `STRONG`.
5. **Diverse Benchmark Corpus Expansion (16–20 Fixtures)**:
   - Creating rich, realistic fixtures across all 5 corpus categories in `tests/fixtures/benchmark_corpus/` with companion `.meta.json` files.
6. **Unified Generalization Replay Harness (`benchmark_runner.py`)**:
   - Flexible CLI and programmatic execution across splits, categories, formats, and operators.
   - Comprehensive reporting in `outputs/benchmarks/phase_4_1/`.

---

## 6. Audit Sign-Off
Forensic audit complete. No implementation should proceed without adhering to the invariants outlined herein.
