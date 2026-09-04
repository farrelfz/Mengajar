# 08 — Test Truth Audit & Coverage Reality

## 1. Test Suite Taxonomy (92 Passing Tests)

| Category | Test Count | Scope & Focus | What It Proves | What It Does NOT Prove |
|---|---|---|---|---|
| **Intelligence Unit Tests** | 20 | Normalization, Segmentation, Classification, Scoring | Input cleaning, heading extraction, keyword tagging | Does not test multi-page LLM hallucinations |
| **KTI Domain Model Tests** | 15 | BAB 1–5 separation, traceability, orphan detection | Research report semantics are strictly categorized | Does not test end-to-end multi-page layout |
| **Design System Tests** | 6 | Theme registry, density tokens, typography | Tokens exist and are distinct | Does not render visual HTML |
| **Format Contract Tests** | 10 | Presets, registry, geometry, multi-format override | Authoritative format contracts and resolution logic | Does not test custom un-registered paper sizes |
| **File Discovery Safety Tests** | 6 | Directory pruning, deterministic ordering, exclusions | Prunes `venv`, `.git`, `node_modules` before traversal | N/A |
| **Agent & Fallback Tests** | 7 | Orchestration, fallback switching, JSON auto-repair | LLM failure triggers fallback and repair | Does not test network latency / timeout edge cases |
| **Rendering Integration Tests** | 6 | `MasterRenderEngine`, `PDFValidator`, screenshots | Hybrid engine generates valid PDF with assets | N/A |
| **True Production Pipeline Tests** | 4 | `MaterialProductionPipeline` from raw text to PDF | Full intelligence $\rightarrow$ composition $\rightarrow$ PDF $\rightarrow$ validation | Uses mock LLM provider for deterministic offline testing |
| **Visual Acceptance Tests** | 2 | End-to-end PDF generation + screenshot inspection | Real visual outputs for Physics and Research domains | Uses automated heuristic validation rather than human eyes |

---

## 2. Test-Only Glue vs Production Truth
- **Production Truth Verified:** 4 integration tests (`test_true_production_pipeline_research_problem`, `test_e2e_torque_presentation_production`, `test_multiformat_rendering_same_semantic_content`) execute the complete production chain without manual blueprint assembly.
- **Mocking Boundary:** Production integration tests use `MockPipelineAI` to guarantee fast (<10s), deterministic, offline test execution without requiring a live Ollama/OpenAI API key.
- **Coverage Verdict:** The 92 tests provide solid, genuine architectural coverage.
