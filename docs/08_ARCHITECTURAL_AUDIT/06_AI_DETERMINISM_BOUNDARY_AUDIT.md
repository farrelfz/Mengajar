# 06 — AI vs Deterministic Boundary Audit

## 1. Boundary Verification Matrix

We audited all AI prompt schemas, agent classes, and output data models to verify strict separation between AI reasoning and deterministic rendering.

| Responsibility Area | AI Owned | Deterministic Code Owned | Boundary Status | Evidence |
|---|---|---|---|---|
| **Semantic Ingestion & Segmentation** | No | **YES** | **CLEAN** | Deterministic regex/AST splitting in `normalizer.py` and `segmenter.py` |
| **Concept & Entity Extraction** | **YES** | Schema Validation | **CLEAN** | LLM extracts concepts, facts, misconceptions into typed Pydantic models |
| **Narrative / Pedagogical Sequence** | **YES** | Schema Validation | **CLEAN** | AI plans sequence of steps (`step.purpose`, `semantic_type`) |
| **Layout Coordinates (x, y, margins)** | **NO** | **YES** | **CLEAN** | Zero layout coordinates in AI prompts or schemas |
| **Page Dimensions & Aspect Ratio** | **NO** | **YES** | **CLEAN** | Owned by `app/formats/` (`ArtifactFormat`) |
| **CSS Rules & HTML Rendering** | **NO** | **YES** | **CLEAN** | AI never generates CSS or page HTML; generated via Jinja2 & CSS Design System |
| **SVG Vector Geometry & Trig** | **NO** | **YES** | **CLEAN** | Vector geometry (`math.sin`, SVG path, viewBox) computed in Python capability renderers |
| **PDF Export & Validation** | **NO** | **YES** | **CLEAN** | Headless Chromium + PyMuPDF |

---

## 2. LLM Output Validation & Auto-Repair Loop
- The system includes `OutputValidator` (`app/contracts/output_validator.py`) with an automated repair loop:
  1. Strips markdown fences (` ```json ... ``` `).
  2. Validates JSON payload against target Pydantic schema.
  3. On schema violation, captures exact Pydantic error details and re-prompts the LLM with error context (up to `max_attempts=3`).
  4. If unrepairable, raises `SchemaValidationError` and triggers fallback chain.

---

## 3. Verdict
The AI vs Deterministic boundary is **exceptionally clean (Grade: GREEN)**. There is zero leakage of coordinates, pixel dimensions, or raw CSS/HTML into the AI prompt and generation layer.
