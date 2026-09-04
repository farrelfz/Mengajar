# TEST AND BENCHMARK RESULTS
## BATCH 19 — KNOWLEDGE GROUNDING & EVIDENCE INTELLIGENCE

### 1. Test Suite Verification
- **Knowledge Grounding Unit Tests (`tests/grounding/`)**: 17 / 17 PASSED (100%)
- **Full Repository Regression Gate**: **249 / 249 PASSED (100% Green)** across 61 test files in 20.47s.

---

### 2. Cross-Domain Grounding Benchmark
Executed via [`scripts/generate_knowledge_grounding_benchmark.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/scripts/generate_knowledge_grounding_benchmark.py) (manifest saved to [`outputs/knowledge_grounding_benchmark/master_grounding_benchmark_manifest.json`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/outputs/knowledge_grounding_benchmark/master_grounding_benchmark_manifest.json)):

| Case ID | Domain | Claims Total | Grounded | Partial | Unsupported | Contradicted | Coverage | Consistency | Overall Score |
|---|---|---|---|---|---|---|---|---|---|
| **Case 1: Physics** | `physics` | 3 | 3 | 0 | 0 | 0 | 1.00 | 1.00 | 0.948 |
| **Case 2: Research** | `research_methodology` | 3 | 2 | 1 | 0 | 0 | 1.00 | 1.00 | 0.947 |
| **Case 3: Pedagogy** | `education` | 2 | 2 | 0 | 0 | 0 | 1.00 | 1.00 | 0.971 |
| **Case 4: Writing** | `research_methodology` | 1 | 1 | 0 | 0 | 0 | 1.00 | 1.00 | 0.985 |
| **Case 5: Data Literacy** | `general` | 1 | 0 | 0 | 1 | 0 | 0.00 | 1.00 | 0.450 |
| **Case 6: Mixed Failure** | `physics` | 3 | 1 | 0 | 1 | 1 | 0.33 | 0.50 | 0.670 |
