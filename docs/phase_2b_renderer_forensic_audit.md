# Phase 2B — Renderer Forensic Pre-Execution Audit Report
## Universal Knowledge Intelligence Core V5

**Author:** Universal Document Intelligence Architecture Team  
**Date:** September 5, 2026  
**Status:** Audit Complete & Verified

---

## 1. Executive Summary

This forensic audit inspects all existing rendering components across the four target artifact formats (Presentation, Handout, Worksheet, Scientific Document). The goal is to document actual input models, fields consumed vs. silently ignored, hidden assumptions, fallback behaviors, and content flattening risks before connecting controlled renderer execution.

---

## 2. Presentation Renderer Audit

- **Files:** `app/presentation/slide_generator.py` (`SlideGenerator`), `app/rendering/engine.py` (`MasterRenderEngine`), `app/rendering/html/assembler.py` (`HTMLAssembler`), `app/rendering/playwright/pdf_exporter.py` (`PlaywrightRenderer`).
- **Input Model Consumed:** `PlannedSlide` via `SlideGenerator.generate_slide(planned: PlannedSlide) -> GeneratedSlide`.
- **Fields Actually Read:**
  - `planned.layout`: Directs template branch (`hero_composition`, `formula_explainer`, `three_column_comparison`, `triangle_relationship`, `data_table`, `risk_matrix`, `timeline_horizontal`, `minimal_question`, `synthesis`, `concept_card`).
  - `planned.title`: Escaped and rendered as slide header.
  - `planned.subtitle`: Rendered when layout supports secondary title.
  - `planned.key_blocks`: Content blocks containing text, lists, or tables.
  - `planned.source_refs`: Preserved on `GeneratedSlide.source_refs`.
- **Fields Silently Ignored:**
  - `planned.cognitive_load`: Cognitive load target is not checked or displayed by `SlideGenerator`.
  - `planned.narrative_function`: Not directly used by layout methods; only layout string determines rendering.
  - `planned.pedagogical_function`: Ignored.
  - `planned.why_this_slide_exists`, `unique_information_gain`, `audience_takeaway`, `transition_logic`: Internal planning metadata ignored during HTML assembly.
- **Hidden Assumptions:**
  - Assumes `planned.layout` matches one of the explicit `if/elif` branches in `generate_slide`.
  - Assumes `13.333in x 7.5in` viewport (`page-presentation` CSS class).
  - Assumes content within `key_blocks` fits within 7.5in vertical height without vertical scrolling.
- **Default Fallback Behavior:**
  - If `layout` does not match known branches, falls back to `_render_concept(planned, title_esc, blocks)` which outputs standard concept card.
- **Content Flattening Risk:**
  - If multiple beats are grouped into one slide, `SlideGenerator` requires them to be supplied as `key_blocks` or formatted content; otherwise only the primary block is rendered.
- **Contract Mismatch & Mitigation:**
  - Adapter emits `SlideBlueprint` with `bullet_points` and `content`. Executor must map `SlideBlueprint` to `PlannedSlide` wrapping bullet points and content into `ContentBlock`s so `SlideGenerator` renders them faithfully.

---

## 3. Handout Renderer Audit

- **Files:** `app/rendering/engine.py` (`MasterRenderEngine`), `app/rendering/html/assembler.py` (`HTMLAssembler`), `app/rendering/html/templates/document.html`.
- **Input Model Consumed:** `DocumentComposition` with `pages: list[PageComposition]`.
- **Fields Actually Read:**
  - `composition.metadata.title`: Document header.
  - `page.page_number`: Slide/page counter.
  - `region.blocks`: Iterates over blocks.
  - `block.rendered_html`: Injected as `{{ block.rendered_html | safe }}`.
  - `block.raw_content`: Fallback `<div class="content-paragraph">{{ block.raw_content }}</div>`.
- **Fields Silently Ignored:**
  - `block.typography`: Typography scale ignored by HTML template (uses stylesheet classes).
  - `block.color_role`: Color role ignored unless baked into `rendered_html`.
  - `page.density_estimate`: Density ignored during rendering.
- **Hidden Assumptions:**
  - Assumes page content fits within `210mm x 297mm` (A4 Portrait).
  - Assumes `overflow: hidden` on `.page` prevents spillover, but causes silent clipping if content overflows!
- **Default Fallback Behavior:**
  - If `rendered_html` is absent, wraps `raw_content` in `.content-paragraph`.
- **Content Flattening Risk:**
  - Definitions and examples will be flattened into plain paragraphs unless explicitly styled with `.card`, `.badge`, or definition list HTML tags.
- **Contract Mismatch & Mitigation:**
  - `DocumentContent` from `HandoutContractAdapter` contains `DocumentContentSection`s with explicit `definitions` and `examples`. Handout Executor must compose these sections into `PageComposition` with structured HTML callouts for definitions and examples.

---

## 4. Worksheet Renderer Audit

- **Files:** `app/rendering/engine.py` (`MasterRenderEngine`), `app/rendering/html/templates/document.html`.
- **Input Model Consumed:** `DocumentComposition` (mode: `DocumentMode.A4_PORTRAIT`, format: `student_worksheet`).
- **Fields Actually Read:**
  - `block.rendered_html`, `page.regions`.
- **Fields Silently Ignored:**
  - `withhold_explanation`: The renderer has NO concept of withholding answers! If explanation text reaches the renderer, it will be displayed. Withholding MUST be guaranteed at the adapter/composition level.
  - `requires_student_workspace`: Ignored unless explicit workspace HTML (`<div class="workspace-box">`) is included in `rendered_html`.
  - `inquiry_activity_type`: Ignored unless rendered as badge/heading.
- **Hidden Assumptions:**
  - Assumes each page contains 2–4 activities with dedicated student response areas.
  - Assumes answers are NOT included in the prompt text.
- **Default Fallback Behavior:**
  - Renders blocks sequentially without student workspace if not supplied in HTML.
- **Content Flattening Risk:**
  - High risk of converting inquiry activities into generic textbook reading paragraphs if activity type badges and response boxes are omitted.
- **Contract Mismatch & Mitigation:**
  - Worksheet Executor must render each `LegacyWorksheetActivity` with:
    1. Activity type badge (`[PHENOMENON]`, `[PREDICTION]`, `[INVESTIGATION]`, etc.).
    2. Explicit inquiry prompt text.
    3. Dedicated student response workspace (`<div class="student-workspace">`).
    4. Verified absence of explanatory answers.

---

## 5. Scientific Document (KTI) Renderer Audit

- **Files:** `app/rendering/engine.py` (`MasterRenderEngine`), `app/composition/kti_integrator.py`, `app/rendering/html/templates/document.html`.
- **Input Model Consumed:** `DocumentComposition` with `metadata["kti_bab"]` or `PageComposition.metadata["kti_bab"]`.
- **Fields Actually Read:**
  - `block.rendered_html`, `composition.metadata.title`.
- **Fields Silently Ignored:**
  - `evidence_id`, `relationship_id`: Completely ignored by HTML template unless embedded into text/citations.
  - `confidence_score`: Ignored.
  - `counter_considerations`: Ignored unless formatted into subsections.
- **Hidden Assumptions:**
  - Assumes 5 formal chapters (BAB I - V).
  - Assumes formal academic typography (Times New Roman / serif, 1.5 line spacing, indented paragraphs).
- **Default Fallback Behavior:**
  - Renders raw text blocks.
- **Content Flattening Risk:**
  - Critical risk: Evidence relationships flattened into anonymous prose; citations dropped.
- **Contract Mismatch & Mitigation:**
  - Scientific Document Executor must format each `LegacyKtiBabSection` and `LegacyScientificSubsection` with:
    1. Formal Chapter Header (e.g. `BAB IV: HASIL DAN PEMBAHASAN`).
    2. Numbered Subsections (`Subbab 4.1`, `Subbab 4.2`).
    3. Explicit evidence citations with callout references (`[BUKTI: ...]`).
    4. Explicit limitation callout boxes in Bab V.

---

## 6. Pre-Render Audit Matrix Summary

| Artifact | Consumed Model | Renderer Engine | Key Fields Read | Key Fields Ignored | Critical Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Presentation** | `PlannedSlide` | `SlideGenerator` + Playwright | `layout`, `title`, `key_blocks` | `cognitive_load`, `narrative_function` | Fallback to generic card |
| **Handout** | `DocumentComposition` | `MasterRenderEngine` | `rendered_html`, `title` | `reading_depth`, `color_role` | Definition/example flattening |
| **Worksheet** | `DocumentComposition` | `MasterRenderEngine` | `rendered_html`, `regions` | `withhold_explanation`, `workspace` | Answer leakage / loss of workspace |
| **Scientific Doc**| `DocumentComposition` | `MasterRenderEngine` | `rendered_html`, `regions` | `evidence_id`, `relationship_id` | Evidence link flattening into prose |
