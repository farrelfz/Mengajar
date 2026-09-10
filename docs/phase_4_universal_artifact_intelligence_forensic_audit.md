# Phase 4 Universal Artifact Intelligence - Forensic Audit

## 1. Existing Presentation Quality Intelligence Components
- **Duplicate Slide Analyzer:** Analyzes slide duplication by stripping HTML/CSS, currently coupled to `PresentationQualityGate`.
- **Claim Grounding Validator:** Verifies slide claims against source text.
- **Semantic Layout Validation:** Enforces `VISUAL_GRAMMAR_MATRIX` for presentation slide layouts based on role.
- **Narrative Evaluator:** Evaluates transition graph, progression, and cognitive load for presentation.
- **Cognitive Load Analysis:** Tracks presentation cognitive streaks and fatigue.
- **Visual QA Analyzer:** PyMuPDF integration for bounding box, text overflow, and font size checking, currently hard-coded mostly for 16:9 slides.
- **Contact Sheet Generator:** Renders a 4-column presentation thumbnail layout.

## 2. Measurement vs. Conceptual Implementation
- **Visual QA Analyzer** conceptually handles text overflow and collisions, but is currently implemented heavily towards Presentation (16:9 bounding boxes, "card" tracking, etc.).
- **Narrative Evaluator** conceptually measures flow, but implements it as slide-to-slide progression instead of a universal section-to-section progression metric.
- **Claim Grounding** specifically looks for slide claims instead of generalized assertion grounding.
- **Cognitive Load Analysis** assumes slides as the primary pagination barrier, ignoring A4 continuous reading rhythms (Handout).

## 3. Overlap with Unified Quality Authority (UQA)
UQA currently holds 4 layers of truth:
1. Semantic Integrity
2. Artifact Fidelity
3. Artifact Quality
4. Physical Rendered Quality

The proposed Universal Taxonomy (Information Density, Structural Coherence, Narrative Flow, etc.) maps smoothly to Level 3 (Artifact Quality) and Level 4 (Physical Rendered Quality). The UQA evaluates these levels via artifact-specific "quality gates," meaning the UQA can consume the generalized Universal Dimensions without redefining its authority.

## 4. Components to Generalize (Not Rewrite)
- **PyMuPDF bounding box & collision checker:** Must be generalized in `RenderedArtifactInspector` for arbitrary PDF geometry (A4 vs 16:9).
- **RuleClassifier & SequenceMatcher:** Generalize into `RepetitionPatternAnalyzer` instead of keeping it in `DuplicateSlideAnalyzer`.
- **Lexical/Semantic overlap logic:** Abstract from `ClaimGroundingValidator` into `AssertionGroundingAnalyzer` handling arbitrary Knowledge Units.
- **Contact Sheet Logic:** Abstract `Pillow` rendering for arbitrary dimensions and aspect ratios (`ArtifactVisualEvidenceGenerator`).

## 5. Duplication Risks in Phase 4
- Creating `HandoutQualityGate`, `WorksheetQualityGate`, `ScientificQualityGate` which completely mirror `PresentationQualityGate`.
- Creating `HandoutVisualQA`, `WorksheetVisualQA`, etc., duplicating PyMuPDF parsing logic.
- Building separate metrics calculation engines for each artifact type instead of utilizing the `QualityMetric(Protocol)` design.
- Decoupling quality intelligence from the central `UnifiedQualityAuthority`, creating competing rejection rules.

## 6. Repair Strategy Consumption
- **`grid_reflow_and_compression` / `card_restructure` (Class A):** Can consume generalized `TEXT_OVERFLOW` and `CARD_OVERLOAD` findings from `RenderedArtifactInspector`.
- **`layout_remap` (Class B):** Can consume `SEMANTIC_LAYOUT_MISMATCH` from `SemanticLayoutValidator`.
- **`ClaimProvenanceRepairer` (Class B):** Can consume `UNSUPPORTED` claims from `AssertionGroundingAnalyzer`.
- Generalized structural findings (like `REPETITION_STREAK` or `COGNITIVE_OVERLOAD`) can trigger Class C/D/E refactoring routines.

## 7. Findings Lacking Root Cause Mapping
- **Rhythmic Monotony:** Currently detected but lacks a specific repair actuator.
- **Information Gain / Cross-Artifact Terminology Inconsistency:** Will be newly introduced but lack immediate deterministic repair hooks (might require regeneration or manual review).
- **Pedagogical/Anti-Spoiling leaks:** In worksheets, detected but currently requires strict halt rather than auto-repair, as it often means the blueprint failed deeply.

## 8. Existing Benchmark Infrastructure
- Existing fixtures: `hand_fire_full.md`, `oobleck_experiment.md` (implied from Phase 4 doc).
- The infrastructure mostly relies on unit tests (`pytest tests/unit/`) currently.

## 9. Benchmark Infrastructure Location
- Belonging to `app/benchmarking/` or similar. Since it evaluates end-to-end truth against golden standards, it should not live inside `app/quality/` (which handles dynamic export authority) but strictly in its own domain.

## 10. Architectural Duplication
- **Fake Universalization:** Creating universal dimensions that only apply to one artifact type anyway.
- **Competing Scoring:** Having `UnifiedQualityAuthority.score` AND `UniversalIntelligence.score`. UQA must consume signals and remain the singular score and decision maker.
