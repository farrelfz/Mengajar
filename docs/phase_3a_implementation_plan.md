# PHASE 3A — IMPLEMENTATION PLAN
## INDEPENDENT, ADVERSARIAL, RENDERED-OUTPUT QUALITY INTELLIGENCE LAYER
### UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5

---

## 1. ARCHITECTURAL OBJECTIVE
Construct an independent, post-render quality inspection layer in `app/quality/rendered/` that evaluates rendered PDFs and raster images across all four artifact formats (Presentation, Handout, Worksheet, Scientific Document). This layer operates downstream of `MasterRenderEngine` without modifying legacy renderers, templates, or CSS, adhering strictly to:
$$\text{Contract Fidelity} \neq \text{Source Traceability} \neq \text{Rendered Visual Quality} \neq \text{Pedagogical Quality} \neq \text{Artifact-Specific Quality} \neq \text{Real-World Usability}$$

---

## 2. DETAILED IMPLEMENTATION PHASES

```
STEP 0: Forensic Architecture Audit (Complete - docs/phase_3a_forensic_audit.md)
  │
STEP 1: Implementation Plan (This document)
  │
STEP 2: Universal Rendered Quality Contracts & Failure Taxonomy
  ├── app/quality/rendered/contracts.py
  └── app/quality/rendered/failure_taxonomy.py
  │
STEP 3: PDF Geometry Inspection Engine
  └── app/quality/rendered/pdf_inspector.py (PyMuPDF: clipping, margin, font size, collisions)
  │
STEP 4: Raster / Image Quality Inspection Engine
  └── app/quality/rendered/raster_inspector.py (Pillow: visual density, blank ratio, visual balance)
  │
STEP 5: Composition Fingerprinting Engine
  └── app/quality/rendered/composition_fingerprint.py (Quadrant spatial vectors & layout streaks)
  │
STEP 6: Context-Aware Whitespace Model
  └── app/quality/rendered/whitespace_model.py (WhitespaceIntentModel: intentional vs accidental void)
  │
STEP 7: Typography & Content Density Analysis
  └── app/quality/rendered/typography_density.py (Typographic scale ratios, density bounds)
  │
STEP 8: Presentation Rendered Quality Evaluator
  └── app/quality/rendered/presentation_quality.py (16:9 slide ergonomics, cards, rhythm, monotony)
  │
STEP 9: Handout Rendered Quality Evaluator
  └── app/quality/rendered/handout_quality.py (A4 reading flow, heading hierarchy, orphan headings, chunking)
  │
STEP 10: Worksheet Rendered Quality Evaluator
  └── app/quality/rendered/worksheet_quality.py (Inquiry progression, student workspace adequacy, anti-spoiling, quiz collapse)
  │
STEP 11: Scientific Document Rendered Quality Evaluator
  └── app/quality/rendered/scientific_quality.py (IMRAD/BAB hierarchy, claim-evidence proximity, citation visibility)
  │
STEP 12: Unified Rendered Quality Engine
  └── app/quality/rendered/quality_engine.py (MasterRenderedQualityEngine)
  │
STEP 13: Quality Reporting Layer
  └── app/quality/rendered/quality_reporter.py (JSON and Markdown reports)
  │
STEP 14: Contact Sheet Intelligence Upgrade
  └── Enhanced diagnostic contact sheet annotations
  │
STEP 15: Adversarial Fixtures & Automated Test Suite (35+ tests)
  ├── tests/unit/quality/rendered/test_rendered_contracts.py
  ├── tests/unit/quality/rendered/test_pdf_geometry_inspector.py
  ├── tests/unit/quality/rendered/test_raster_inspector.py
  ├── tests/unit/quality/rendered/test_presentation_rendered_quality.py
  ├── tests/unit/quality/rendered/test_handout_rendered_quality.py
  ├── tests/unit/quality/rendered/test_worksheet_rendered_quality.py
  ├── tests/unit/quality/rendered/test_scientific_rendered_quality.py
  └── tests/integration/test_rendered_quality_golden_benchmark.py
  │
STEP 16: Golden Fixture Execution (Oobleck + Benchmark Corpus)
  └── Persist outputs to outputs/benchmark/phase_3a/
  │
STEP 17: Full Regression Verification
  └── pytest tests/unit/ and pytest tests/integration/
  │
STEP 18: Master Architectural Documentation
  └── docs/phase_3a_rendered_quality_intelligence.md (All 21 required sections)
```

---

## 3. STRICT BOUNDARIES & CONSTRAINTS
- **Zero Renderer Redesign**: Legacy CSS, Jinja templates, and Python renderers remain completely untouched.
- **Zero Automatic Repair**: Phase 3A reports diagnostics and classifies failures into future repair classes; no automated repair loops are connected.
- **Zero Score Inflation**: If an artifact has weak visual layout or excessive text density, report the truth. A truthful score of 62% is vastly superior to an artificial 100%.
- **Zero AI / Zero LLM**: Strictly deterministic AST, DOM, box geometry, and statistical algorithms.
