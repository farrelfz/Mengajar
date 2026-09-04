# 05 — Full Regression & Benchmark Results

## 1. Test Suite Growth & Pass Rate

- **Baseline before Batch 7.9:** 92 / 92 passed
- **New Tests Added:**
  1. `tests/formats/test_format_geometry_invariants.py::test_format_geometry_invariants_css_rules`
  2. `tests/formats/test_format_geometry_invariants.py::test_format_geometry_invariants_point_dimensions`
  3. `tests/formats/test_format_geometry_invariants.py::test_html_assembler_injects_matching_page_class`
  4. `tests/capabilities/test_capability_parameter_extraction.py::test_decentralized_parameter_extraction_pedagogy`
  5. `tests/capabilities/test_capability_parameter_extraction.py::test_decentralized_parameter_extraction_physics`
  6. `tests/capabilities/test_capability_parameter_extraction.py::test_decentralized_parameter_extraction_research_problem`
  7. `tests/capabilities/test_capability_parameter_extraction.py::test_capability_without_extractor_returns_empty_dict`
  8. `tests/integration/test_decoupled_capability_pipeline.py::test_extensible_plugin_without_core_modification`
  9. `tests/regression/test_landscape_pagination_regression.py::test_a4_landscape_produces_exact_page_count`
- **Final Test Suite:** **101 / 101 PASSED in 11.63s (0 regressions)**.

---

## 2. Multi-Format Physical PDF Benchmark

Generated via `scripts/generate_preflight_benchmark.py`:

| Target Format | Composition Steps | PDF Pages | Width (mm) | Height (mm) | Deterministic? | Status |
|---|---|---|---|---|---|---|
| **A4 Portrait** | 3 | 3 | 209.89 mm | 297.01 mm | Yes (3/3 identical) | **PERFECT** |
| **A4 Landscape** | 3 | 3 (Fixed from 8) | 297.01 mm | 209.89 mm | Yes (3/3 identical) | **PERFECT** |
| **Presentation 16:9** | 3 | 3 | 338.67 mm | 190.50 mm | Yes (3/3 identical) | **PERFECT** |

---

## 3. Physical Inspection Summary
- No empty pages generated across any format.
- No unexpected page breaks in landscape.
- Determinism check: 3 repeated runs produced 3 identical PDFs with identical page and asset counts.
