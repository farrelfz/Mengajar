# TEST AND BENCHMARK RESULTS
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Test Suite Results
- **Focused Quality Tests (`tests/quality/`)**:
  - `test_quality_contracts.py` (3 tests) — **PASSED**
  - `test_density_and_redundancy.py` (2 tests) — **PASSED**
  - `test_determinism_and_false_positives.py` (2 tests) — **PASSED**
  - `test_pedagogical_and_format_evaluators.py` (2 tests) — **PASSED**
  - `test_quality_engine_and_gate.py` (3 tests) — **PASSED**
  - `test_quality_pipeline_integration.py` (1 test) — **PASSED**
  - `test_structural_quality.py` (2 tests) — **PASSED**
  - **Subsystem Total**: 15 / 15 PASSED (100%)

- **Full Repository Regression Gate**:
  - Total Tests: **169 / 169 PASSED (100% Green)**
  - Zero failures, zero skips, zero regressions.

---

### 2. Multi-Domain Physical PDF Benchmark
Generated via [`scripts/generate_quality_evaluation_benchmark.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/scripts/generate_quality_evaluation_benchmark.py):

| Domain | Format | Pages | Geometry (pt) | Quality Score | Quality Level | Gate Decision |
|---|---|---|---|---|---|---|
| **Physics** | `presentation_16_9` | 3 | $960.0 \times 540.0$ | **0.968** | EXCELLENT | `PASS_WITH_WARNINGS` |
| **Research Methodology** | `a4_portrait` | 4 | $595.0 \times 841.9$ | **0.937** | GOOD | `PASS_WITH_WARNINGS` |
| **Academic Writing** | `a4_portrait` | 4 | $595.0 \times 841.9$ | **0.937** | GOOD | `PASS_WITH_WARNINGS` |
| **Experiment Design** | `a4_landscape` | 4 | $841.9 \times 595.0$ | **0.968** | EXCELLENT | `PASS_WITH_WARNINGS` |
| **Data Literacy** | `presentation_16_9` | 3 | $960.0 \times 540.0$ | **0.968** | EXCELLENT | `PASS_WITH_WARNINGS` |

All benchmark manifests and individual `quality_report.json` artifacts verified in `outputs/quality_evaluation_benchmark/`.
