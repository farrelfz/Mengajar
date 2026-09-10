# Presentation Quality Plan: V2 to V3 Architecture Evolution

## Executive Summary
This document establishes the architectural blueprint for transitioning the Markdown → AI Presentation → HTML → PDF system from a **"Valid Presentation Pipeline"** to a **"Presentation Intelligence System with Visual Quality Assurance"**.

While V2 solved API explosion, per-block classification, static compression, and basic traceability, V2 metrics (100% coverage, 0 duplicates, high layout entropy) proved that a deck can be technically valid while remaining pedagogically monotonous, visually repetitive, text-overcrowded, or semantically misaligned.

---

## 1. Current Pipeline Status (V2 Audit)

| Component | Current Implementation | Status / Limitation |
|---|---|---|
| **Structural Parsing** | `MarkdownTreeParser` -> `ContentTree`, `ContentSection`, `ContentBlock` | Solid. Extracts 100% of sections, formulas, tables, warnings. |
| **Local Classification** | `RuleClassifier` with regex & semantic rules | Fast & deterministic. Local ratio ~98%. |
| **Selective AI Reasoning** | Escalation only for high-entropy ambiguous blocks | High cost-efficiency. |
| **Content Manifest** | `ContentManifestBuilder` -> Critical/Important/Supporting | Accurate priority tags, calculates min/target/max slide bounds. |
| **Presentation Blueprint** | `SlideArchitect` -> `PlannedSlide`, `SlidePlan` | **Weakness**: Lacks narrative function, pedagogical function, cognitive load, transition logic, claim units, and information gain models. |
| **Visual Intent Mapping** | `VisualDirector` with 12 layouts | **Weakness**: Relies on layout entropy rather than semantic appropriateness. A process could be rendered as cards and pass entropy. |
| **HTML Composition** | `SlideGenerator` with hardcoded layout methods | Good styling, but lacks deterministic overflow/density auto-repair mechanisms. |
| **Rendering** | `MasterRenderEngine` (Playwright + PyMuPDF validator) | Produces valid PDF. Checks page count and non-empty text, but lacks raster visual QA. |
| **Quality Validation** | `PresentationQualityGate` (11 hard gates) | Validates parsing, coverage, duplicates, layout entropy, log errors, and regex blacklist (`p < 0.05`). Lacks raster visual inspection, claim grounding, cognitive load, and rhythm checks. |
| **Repair Loop** | None | Fails or passes in one shot. No deterministic repair or refinement loop. |

---

## 2. Missing Quality & Visual QA Signals

### 2.1 Missing Presentation Intelligence Signals
1. **Narrative Progression**: No transition compatibility graph. Consecutive identical narrative states (e.g. 5 CONCEPT slides) are unpenalized.
2. **Pedagogical Progression**: No explicit sequence tracking (Hook -> Inquiry -> Concept -> Mechanism -> Application -> Synthesis).
3. **Cognitive Load Balance**: No tracking of cumulative cognitive load streaks (e.g. 4 HIGH load slides in a row).
4. **Concept Fragmentation**: No detection when a single simple concept is needlessly stretched over 4 consecutive thin slides.
5. **Concept Compression**: No detection when a single slide tries to pack 6 dense concepts and formulas without breathing room.
6. **Slide Purpose Redundancy**: No detection of consecutive slides having high lexical overlap and identical functions.
7. **Information Gain**: No metric measuring whether slide $N+1$ actually introduces new concepts/mechanisms relative to slide $N$.
8. **Semantic Layout Appropriateness**: No matrix penalizing semantically mismatched layouts (e.g. a step-by-step experiment procedure rendered as disconnected cards).

### 2.2 Missing Visual QA Signals
1. **Text Overflow & Clipping**: No check if rendered text exceeds the viewport or gets clipped by `overflow: hidden`.
2. **Tiny Text**: No check for body fonts shrinking below readable thresholds (e.g. < 14pt in 16:9).
3. **Density Imbalance**: No check whether occupied bounding box area is too sparse (< 10% on content slides) or overcrowded (> 85%).
4. **Context-Aware Whitespace**: Treating all whitespace identically instead of distinguishing intentional hero negative space from accidental void.
5. **Card Overload**: No check for AI decks overusing generic card grids (> 6 cards on a single slide).
6. **Composition Repetition Fingerprint**: Two slides with different layout names can have the exact same 3-box visual composition. No spatial fingerprint comparison exists.
7. **Weak Visual Hierarchy**: No ratio check between headline, subtitle, and body text prominence.
8. **Slide-to-Slide Visual Rhythm**: No sequence analysis of density and visual type flow across the entire deck.

### 2.3 Hallucination Detection Weaknesses
- Currently relies strictly on a static blacklist of strings (`p < 0.05`, `Primary Factor / Treatment`).
- Does not verify if generated claims are actually grounded in source block text.
- Cannot catch unsupported exaggerations (e.g. "completely prevents heat") or fabricated constants ("safe duration is exactly 10s").

---

## 3. Proposed V3 Architecture (10-Task Flow)

```
[Markdown Source]
      │
      ▼
TASK 1: Structural Parsing (MarkdownTreeParser)
      │
      ▼
TASK 2: Local Semantic Classification (RuleClassifier)
      │
      ▼
TASK 3: Selective AI Reasoning (SelectiveReasoner)
      │
      ▼
TASK 4: Content Manifest & Coverage Planning (ContentManifestBuilder)
      │
      ▼
TASK 5: Multi-Dimensional Presentation Architecture (SlideArchitect & PresentationArchitectureEvaluator)
      ├─ Narrative Functions & Transitions
      ├─ Pedagogical Roles & Cognitive Load
      ├─ Claim Unit Extraction
      └─ Information Gain & Allocation Intelligence
      │
      ▼
TASK 6: Visual Grammar & Semantic Layout Assignment (SemanticLayoutValidator)
      └─ Visual Grammar Matrix (Role <-> Layout Compatibility)
      │
      ▼
TASK 7: Deterministic Composition (SlideGenerator)
      │
      ▼
TASK 8: Rendering (MasterRenderEngine - Playwright + PDF)
      │
      ▼
TASK 9: Semantic + Visual Quality Assurance (PresentationQualityEngine)
      ├─ Claim Grounding Validator (Primary Defense)
      ├─ Layout DOM & PyMuPDF Visual QA Analyzer (Overflow, Tiny Text, Density, Repetition)
      ├─ Presentation Rhythm Analyzer
      └─ 25 Hard Quality Gates Matrix
      │
      ▼
TASK 10: Deterministic Repair & Refinement Loop (RepairEngine)
      ├─ Class A: Deterministic Layout & Typography Repair (No AI)
      ├─ Class B: Semantic Layout Re-mapping (No AI)
      ├─ Class C/D/E: Structural/Narrative Refinement (Max 2 Iterations)
      └─ Re-render & Re-verify
      │
      ▼
[Export & QA Artifacts Generation]
      ├─ final_presentation.pdf
      ├─ generation_report.json
      ├─ generation_report.md
      ├─ presentation_quality_report.md
      └─ presentation_contact_sheet.png
```

---

## 4. Proposed Modules & Responsibilities

### 4.1 Upgraded Presentation Blueprint (`app/presentation/slide_architect.py`)
- Upgrade `PlannedSlide` schema with:
  - `narrative_function`: `HOOK`, `QUESTION`, `CONTEXT`, `CONCEPT_INTRODUCTION`, `MECHANISM`, `COMPARISON`, `PROCESS`, `APPLICATION`, `EXPERIMENT`, `OBSERVATION`, `ANALYSIS`, `REFLECTION`, `SYNTHESIS`, `CONCLUSION`
  - `pedagogical_function`: `ENGAGE`, `EXPLAIN`, `VISUALIZE`, `COMPARE`, `BREAK_DOWN`, `APPLY`, `ANALYZE`, `SYNTHESIZE`
  - `information_role`: `NEW_INFORMATION`, `ELABORATION`, `CONNECTION`, `EVIDENCE`, `SUMMARY`
  - `cognitive_load`: `{"level": "low"|"medium"|"high", "reason": "..."}`
  - `visual_priority`: `HIGH`, `MEDIUM`, `LOW`
  - `transition_from_previous`, `transition_to_next`
  - `claim_units`: list of `ClaimUnit`
  - Internal metadata: `why_this_slide_exists`, `audience_takeaway`, `unique_information_gain`, `why_not_merge_with_previous`

### 4.2 Presentation Architecture Evaluator (`app/presentation/narrative_evaluator.py`)
- `NarrativeTransitionGraph`: Directed compatibility graph and penalty scoring.
- `CognitiveLoadValidator`: Enforces max consecutive high cognitive load streak <= 2.
- `ConceptFragmentationAnalyzer`: Flags simple concepts spread over multiple redundant slides.
- `ConceptCompressionAnalyzer`: Flags overcrowded concepts per slide.
- `SlidePurposeRedundancyAnalyzer`: Flags identical concepts, narrative functions, and high text similarity.
- `InformationGainAnalyzer`: Measures new concept/mechanism delta between consecutive slides.

### 4.3 Semantic Layout Validator (`app/presentation/semantic_layout_validator.py`)
- Enforces Visual Grammar Matrix:
  - `PROCESS` -> requires sequence/timeline layouts; penalizes cards.
  - `QUESTION` -> requires minimal_question/hero; penalizes dense tables.
  - `FORMULA` -> requires formula_explainer/derivation; penalizes card grids.
  - `COMPARISON` -> requires comparison_split/3-col/matrix; penalizes random timelines.
  - `SAFETY` -> requires hazard/risk_matrix.

### 4.4 Claim Grounding Validator (`app/presentation/claim_grounding_validator.py`)
- Extracts key factual claims from slides.
- Compares claims against source block text using lexical and semantic overlap.
- Categorizes support level: `DIRECT_SUPPORT`, `PARAPHRASE_SUPPORT`, `INFERRED_SUPPORT`, `UNSUPPORTED`.
- Detects unsupported exaggerations and fabricated figures.
- Retains regex blacklist (`p < 0.05`, log timestamps) as secondary safety defense.

### 4.5 Visual Quality Analyzer (`app/presentation/visual_qa.py`)
- **PyMuPDF & DOM raster inspection**:
  - `check_text_overflow`: detects text length exceeding container limits and bounding boxes outside page rectangle `[0, 0, width, height]`.
  - `check_tiny_text`: parses text span font sizes in PDF; flags body text below 14pt.
  - `check_density_balance`: computes bounding box area ratio; layout-aware thresholds (hero: 0.10–0.45, concept: 0.30–0.70, diagram: 0.25–0.80, table: 0.45–0.85).
  - `check_card_overload`: flags > 6 generic cards per slide (unless comparison/matrix).
  - `check_visual_hierarchy`: verifies title font size > subtitle font size > body font size.
  - `check_whitespace_quality`: distinguishes intentional hero space from accidental void.
- `CompositionFingerprint`: Quadrant/spatial zone occupancy vector; detects visual repetition streaks where consecutive slides look identical despite different titles.

### 4.6 Presentation Rhythm Analyzer (`app/presentation/rhythm_analyzer.py`)
- Analyzes slide-to-slide progression of cognitive load, visual density, and component types.
- Computes overall `rhythm_score` (0.0 to 1.0).

### 4.7 Deterministic Repair Engine (`app/presentation/repair_engine.py`)
- **Class A**: Deterministic layout repairs (font-size adjustment, card reflow, padding reduction).
- **Class B**: Semantic layout re-mapping (e.g. remap PROCESS from cards to `timeline_horizontal`).
- **Class C/D/E**: Selective restructuring with hard limit `MAX_REPAIR_ITERATIONS = 2`.
- Full repair traceability log logged into reports.

### 4.8 QA Contact Sheet Generator (`app/presentation/contact_sheet.py`)
- Uses PyMuPDF `page.get_pixmap()` and Pillow `Image` to render all slide pages into a 4-column thumbnail contact sheet (`presentation_contact_sheet.png`) with slide labels and borders.

### 4.9 Unified Export Quality Gate (`app/presentation/quality_gate.py`)
- Expands from 11 gates to the complete 25-Gate Matrix.

---

## 5. 25-Gate Quality Matrix

| Gate | Name | Category | Critical? | Method |
|---|---|---|---|---|
| **GATE 1** | Source Parsing Integrity | Semantic | Yes | Local Structural Check |
| **GATE 2** | Critical Content Coverage >= 95% | Semantic | Yes | Manifest Source Matching |
| **GATE 3** | Important Content Coverage >= 85% | Semantic | Yes | Manifest Source Matching |
| **GATE 4** | Claim-Level Source Grounding | Semantic | Yes | Claim Support Validator |
| **GATE 5** | Presentation Narrative Quality | Semantic | No (Warning) | Narrative Transition Graph |
| **GATE 6** | Cognitive Load Balance | Semantic | No (Warning) | Max Load Streak Check |
| **GATE 7** | Concept Fragmentation | Semantic | No (Warning) | Fragmentation Analyzer |
| **GATE 8** | Concept Compression | Semantic | No (Warning) | Compression Analyzer |
| **GATE 9** | Semantic Layout Alignment | Semantic | Yes | Visual Grammar Matrix |
| **GATE 10** | Text Overflow & Boundary Violation | Visual | Yes | DOM / PyMuPDF BBox |
| **GATE 11** | Element Collision & Severe Overlap | Visual | Yes | PyMuPDF BBox Intersection |
| **GATE 12** | Tiny Text Minimum Threshold | Visual | Yes | PyMuPDF Span Font Size |
| **GATE 13** | Density Balance | Visual | No (Warning) | Area Occupancy Thresholds |
| **GATE 14** | Intentional Whitespace Quality | Visual | No (Warning) | Void vs Structure Analysis |
| **GATE 15** | Visual Hierarchy | Visual | No (Warning) | Headline/Body Size Ratio |
| **GATE 16** | Composition Repetition Streak | Visual | No (Warning) | Spatial Fingerprint Distance |
| **GATE 17** | Diagram Readability | Visual | No (Warning) | SVG/Node Density Check |
| **GATE 18** | Card Overload (Max 6 generic) | Visual | No (Warning) | Card Component Counter |
| **GATE 19** | Presentation Rhythm | Presentation | No (Warning) | Rhythm Analyzer |
| **GATE 20** | Slide Purpose Redundancy | Presentation | No (Warning) | Purpose Similarity Check |
| **GATE 21** | Information Gain Between Slides | Presentation | No (Warning) | Information Gain Delta |
| **GATE 22** | Slide Allocation Sanity | Presentation | Yes | Min/Max Slide Budget |
| **GATE 23** | System Log Sanitization | Safety | Yes | Regex Pattern Scan |
| **GATE 24** | Duplicate Slide Rate (< 10%) | Safety | Yes | Sequence Matcher |
| **GATE 25** | Anti-Hallucination Blacklist | Safety | Yes | Forbidden Terms Scan |

---

## 6. Implementation Steps & Verification Plan
1. **Audit complete** (this document).
2. Upgrade `PlannedSlide` schema in `slide_architect.py`.
3. Implement `narrative_evaluator.py`, `semantic_layout_validator.py`, `claim_grounding_validator.py`.
4. Implement `visual_qa.py`, `rhythm_analyzer.py`, `contact_sheet.py`.
5. Implement `repair_engine.py`.
6. Upgrade `quality_gate.py` with the 25-Gate Matrix and `generation_reporter.py` with `presentation_quality_report.md`.
7. Integrate Tasks 9 and 10 into `MaterialProductionPipeline` in `production_pipeline.py`.
8. Write comprehensive automated tests in `tests/unit/test_presentation_quality_intelligence.py` covering all 28 required test cases.
9. Execute Hand Fire regression end-to-end, verify generated PDF, contact sheet, and reports.
