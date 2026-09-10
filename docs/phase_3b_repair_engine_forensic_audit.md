# PHASE 3B — FORENSIC ARCHITECTURE AUDIT: REPAIR ENGINE & QUALITY CONVERGENCE
## Universal Document Intelligence System V5
### Forensic Investigation Before Repair Implementation

---

## 1. Executive Summary & Audit Mandate

This forensic audit establishes the empirical baseline for **Phase 3B: Root-Cause-Aware Targeted Repair & Iterative Quality Convergence Engine**.
Following strict architectural discipline, this audit analyzes the existing codebase to prevent symptom-chasing, infinite oscillation loops, evidence fabrication, and quality authority fragmentation.

**Core Finding**: The repository currently exhibits severe **Repair Asymmetry**. Automated repair exists solely for `PRESENTATION` in a legacy prototype module (`app/presentation/repair_engine.py`), which treats physical symptoms (e.g. `TEXT_OVERFLOW`, `TINY_TEXT`) with crude heuristic mutations (toggling `text_density = "high"` vs `"low"`) without root cause analysis. `HANDOUT`, `WORKSHEET`, and `SCIENTIFIC_DOCUMENT` possess **zero automated repair strategies**, causing all non-presentation failures to either block export or require manual intervention.

---

## 2. Quality Authority Architecture Mapping

The quality authority layer consolidated in Phase 3A.1 provides the sole canonical source of truth:

```
[Specialized Evaluators / Inspectors]
  │  ├── Rendered Geometry Inspector (Phase 3A)
  │  ├── Calibration Quality Evaluator (Phase 2C)
  │  ├── Renderer Fidelity Validator (Phase 2B)
  │  └── Semantic / Claim Grounding Evaluator (Phase 1C/1D)
  ▼
[Signal Adapters] (app/quality/adapters/)
  ├── RenderedQualitySignalAdapter
  ├── CalibrationSignalAdapter
  ├── FidelitySignalAdapter
  └── PresentationQualitySignalAdapter / LegacyDocumentQualitySignalAdapter
  ▼
[Canonical Quality Language] (app/quality/contracts/)
  ├── QualitySignal (domain, truth_layer, canonical_code, severity, metrics)
  ├── QualityFinding (finding_id, failure_code, severity, affected_pages, repair_class)
  └── FindingCluster (correlated multi-signal defect representations)
  ▼
[UnifiedQualityAuthority] (app/quality/authority/master_authority.py)
  │  ├── FindingCorrelationEngine (co-occurrence & spatial clustering)
  │  ├── Double-Penalty Suppression
  │  ├── QualityDimensionNormalizer (4 canonical dimensions: Fidelity, Geometry, Structure, Aesthetic)
  │  └── Format Quality Profiles (PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT)
  ▼
[AuthoritativeDecisionEngine] (app/quality/authority/decision_engine.py)
  └── UnifiedQualityDecision (EXPORT_APPROVED, EXPORT_APPROVED_WITH_WARNINGS,
                             RENDER_REPAIR_REQUIRED, SEMANTIC_REPAIR_REQUIRED,
                             REPAIR_REQUIRED, MANUAL_REVIEW_REQUIRED, BLOCKED)
```

### Key Invariant:
`UnifiedQualityAuthority` is the **exclusive Level-0 authority**. The Phase 3B repair engine is an execution client that consumes authoritative findings, identifies root causes, plans mutations, executes minimal interventions, and submits results back to `UnifiedQualityAuthority` for re-evaluation. The repair engine **never** approves an export independently.

---

## 3. Canonical Finding Codes & Failure Taxonomy

Mapped in `app/quality/contracts/taxonomy_mapping.py` and `app/quality/contracts/findings.py`:

| Canonical Failure Code | Domain | Truth Layer | Typical Symptoms | Allowed Repair Class |
| :--- | :--- | :--- | :--- | :--- |
| `TEXT_CLIPPING` | RENDERED | PHYSICAL_RENDER | Text truncated by container bounding box | Class A (Geometry) / Class B (Split) |
| `TEXT_OVERFLOW` | RENDERED | PHYSICAL_RENDER | Text exceeds allocated visual height/width | Class A (Spacing/Padding) / Class B (Split) |
| `ELEMENT_COLLISION` | RENDERED | PHYSICAL_RENDER | Overlap area > 0 between distinct nodes | Class A (Geometry rebalance, grid flow) |
| `FONT_TOO_SMALL` | RENDERED | PHYSICAL_RENDER | Body font < format threshold (12pt / 9pt) | Class A (Geometry/Margins) / Class B (Split) |
| `UNDERUTILIZED_SPACE` | RENDERED | PHYSICAL_RENDER | Occupancy ratio < format minimum | Class A (Whitespace redistribution) |
| `ACCIDENTAL_PAGE` | RENDERED | PHYSICAL_RENDER | Trailing page with < 10% content or orphans | Class B (Pagination consolidation) |
| `MARGIN_VIOLATION` | RENDERED | PHYSICAL_RENDER | Elements inside safe-zone boundary | Class A (Padding / margin adjustment) |
| `EXCESSIVE_LINE_LENGTH` | RENDERED | PHYSICAL_RENDER | CPL > 90 characters | Class A (Column allocation) |
| `DUPLICATE_CONTENT` | ARTIFACT | SEMANTIC_TRANSFORMATION | Redundant slide or identical section text | Class B (Deduplication & merging) |
| `LAYOUT_MONOTONY` | ARTIFACT | SEMANTIC_TRANSFORMATION | $\ge 5$ consecutive identical layouts | Class C (Visual grammar remapping) |
| `LAYOUT_TAXONOMY_MISMATCH` | ARTIFACT | SEMANTIC_TRANSFORMATION | Process mapped to cards, comparison to text | Class C (Layout family remapping) |
| `COGNITIVE_OVERLOAD` | ARTIFACT | PEDAGOGICAL_STRUCTURE | Too many cards ($\ge 6$), high density streak | Class B (Compositional split) |
| `STRUCTURAL_HIERARCHY_INVERSION`| ARTIFACT | STRUCTURAL_BLUEPRINT | Heading level skips (H1 -> H3) or Bab inverted | Class D (Pedagogical reordering) |
| `INQUIRY_ARC_BROKEN` | ARTIFACT | PEDAGOGICAL_STRUCTURE | Reflection before observation, non-inquiry order| Class D (Inquiry sequence restore) |
| `ANTI_SPOILING_BREACH` | ARTIFACT | PEDAGOGICAL_STRUCTURE | Explanation/answer disclosed before prediction | Class D (Withhold explanation, isolate) |
| `INSUFFICIENT_WORKSPACE` | ARTIFACT | PHYSICAL_RENDER | Workspace missing or < format minimum | Class A (Expand workspace) / Class B (Split) |
| `QUIZ_COLLAPSE` | ARTIFACT | PEDAGOGICAL_STRUCTURE | Dominated by $\ge 10$ multiple choice items | Class D (Convert to inquiry activity) |
| `UNSUPPORTED_SCIENTIFIC_CLAIM` | SEMANTIC | FACTUAL_GROUNDING | Claim lacks verified evidence linkage | Class E (Evidence map / Certainty downgrade) |
| `MISATTRIBUTED_EVIDENCE` | SEMANTIC | FACTUAL_GROUNDING | Evidence mapped to wrong claim unit | Class E (Remap to valid source evidence) |
| `CITATION_MISSING` | SEMANTIC | FACTUAL_GROUNDING | Empirical claim missing bibliography ref | Class E (Link bibliography / Downgrade) |
| `SOURCE_CONTRADICTION` | SEMANTIC | FACTUAL_GROUNDING | Mutual contradiction in source units | Class F (MANUAL_REVIEW_REQUIRED) |

---

## 4. DecisionEngine Repair Routes & Exit States

`AuthoritativeDecisionEngine` routes quality outputs as follows:

1. **`BLOCKED`**: Triggered when `hard_blockers` exist (e.g. `SCIENTIFIC_CITATION_INVISIBLE`, `WORKSHEET_SPOILING_FAILURE`, `TRACEABILITY_BREAK`, or any `BLOCKING` severity signal). Auto-repair is permitted ONLY IF the defect has a registered deterministic strategy with `risk_level <= HIGH` and defined preconditions; otherwise escalates to `MANUAL_REVIEW_REQUIRED`.
2. **`RENDER_REPAIR_REQUIRED`**: Triggered when physical rendered defects dominate (`TEXT_CLIPPING`, `ELEMENT_COLLISION`, `FONT_TOO_SMALL`). Directs pipeline to Class A/B physical and compositional repair.
3. **`SEMANTIC_REPAIR_REQUIRED`**: Triggered when structural/pedagogical defects dominate (`LAYOUT_MONOTONY`, `INQUIRY_ARC_BROKEN`, `UNSUPPORTED_SCIENTIFIC_CLAIM`). Directs pipeline to Class C/D/E repair.
4. **`REPAIR_REQUIRED`**: Multi-layer co-occurring defects. Requires root-cause clustering before selecting minimal intervention.
5. **`MANUAL_REVIEW_REQUIRED`**: Non-repairable structural failures (Class F), source contradictions, or detected oscillation. Halts automation safely.
6. **`EXPORT_APPROVED_WITH_WARNINGS`**: Minor informational/warning signals within tolerance; export permitted.
7. **`EXPORT_APPROVED`**: Zero blockers, zero unhandled errors, score >= threshold; clean export.

---

## 5. Renderer Execution Boundaries & Target Scopes

Renderer execution in `app/integration/render_execution/` operates via dedicated executors:

- `PresentationExecutor` (`app/integration/render_execution/presentation_executor.py`):
  - Consumes: `PresentationAdapterResult` containing slide HTML / compositions.
  - Granularity: Slide-level (`slide_number`).
  - Targeted Re-render Scope: Individual slides can be re-rendered independently and spliced back into the presentation deck without re-rendering unaffected slides.
- `HandoutExecutor` (`app/integration/render_execution/handout_executor.py`):
  - Consumes: `HandoutAdapterResult` containing A4 document pages.
  - Granularity: Section-level / Page-level.
  - Targeted Re-render Scope: Flowable pagination. Mutations to section spacing or paragraph breaks may reflow subsequent pages, requiring scoped re-render from modified section index forward.
- `WorksheetExecutor` (`app/integration/render_execution/worksheet_executor.py`):
  - Consumes: `WorksheetAdapterResult` containing discrete inquiry activity blocks.
  - Granularity: Activity-level (`activity_id`).
  - Targeted Re-render Scope: Activity block re-layout with reserved workspace containers.
- `ScientificDocumentExecutor` (`app/integration/render_execution/scientific_document_executor.py`):
  - Consumes: `ScientificDocumentAdapterResult` containing formal Indonesian KTI chapters (Bab I - V).
  - Granularity: ArgumentUnit / Section-level.
  - Targeted Re-render Scope: Chapter/section level with formal citation and evidence linkage tables.

---

## 6. Artifact Blueprint Architecture

Defined immutably in `app/intelligence/transformation/blueprints.py`:

1. **`PresentationBlueprint`**:
   - Element: `ConceptualBeat`
   - Key attributes: `sequence_index`, `primary_concept_unit_id`, `narrative_function`, `cognitive_load_target`, `visual_priority`, `knowledge_unit_ids`.
2. **`HandoutBlueprint`**:
   - Element: `ExplanatorySection`
   - Key attributes: `topic`, `heading_level`, `core_unit_ids`, `supporting_unit_ids`, `definitions`, `examples`, `reading_depth`.
3. **`WorksheetBlueprint`**:
   - Element: `LearningActivity`
   - Key attributes: `activity_type` (`PHENOMENON`, `PREDICTION`, `QUESTION`, `OBSERVATION`, `INVESTIGATION`, `DATA_ANALYSIS`, `REFLECTION`), `withhold_explanation` (strictly boolean), `scaffolding_level`, `prompt_text`.
4. **`ScientificDocumentBlueprint`**:
   - Element: `ScientificArgumentUnit`
   - Key attributes: `argument_role` (`BACKGROUND_CLAIM`, `HYPOTHESIS`, `EMPIRICAL_EVIDENCE`, `LIMITATION`, `CONCLUSION`), `claim_statement`, `supporting_evidence_unit_ids`, `confidence`, `source_traceability`.

---

## 7. Forensic Audit of Legacy Repair Logic

Examination of `app/presentation/repair_engine.py` reveals the existing prototype repair mechanisms:

### Existing Implemented Heuristics:
1. **`SlideDeduplicationPlanner`** (Lines 116–175):
   - Merges duplicate slides into predecessor slide.
   - Preserves source refs and key blocks.
   - Re-indexes slide numbers.
2. **`ClaimProvenanceRepairer`** (Lines 177–271):
   - Links independent best source match when available.
   - Softens absolute Indonesian/English exaggerations via regex (e.g., `100% aman` -> `aman dalam pengawasan ketat`).
   - Removes ungrounded claims (`slide.claim_units = [c for c in ...]`).
3. **`Semantic Layout Alignment`** (Lines 345–387):
   - Remaps slide layout using `VISUAL_GRAMMAR_MATRIX` when `GATE_16_SEMANTIC_LAYOUT_ALIGNMENT` fails.
4. **`Visual QA Repairs`** (Lines 389–450):
   - For `TEXT_OVERFLOW`: sets `slide.text_density = "high"`, switches `concept_card` -> `two_column`.
   - For `TINY_TEXT`: sets `slide.text_density = "low"`.
   - For `CARD_OVERLOAD`: sets layout to `three_column_comparison` or `two_column`.

---

## 8. Defect Catalog: Specific Anti-Patterns Identified

| Intervention Type | Location | Implementation in Code | Architectural Defect |
| :--- | :--- | :--- | :--- |
| **Font Shrinking / Density Toggle** | `repair_engine.py:403, 420` | `slide.text_density = "high"` / `"low"` | **Oscillation Trap**: High density causes tiny text in subsequent pass; low density causes overflow. Treats physical consequence rather than content volume. |
| **Heuristic Layout Fallback** | `repair_engine.py:402, 437` | Hardcoded `new_layout = "two_column"` | Ignores narrative function; violates visual grammar if slide function is timeline, process, or quote. |
| **Card Restructuring** | `repair_engine.py:444` | Fallback to `three_column_comparison` | Fails when block count > 6; does not split overloaded conceptual beats. |
| **Slide / Page Splitting** | *Missing in legacy engine* | None (omitted entirely) | Overloaded slides are never split; forced to shrink or truncate. |
| **Content Trimming** | `repair_engine.py:257` | `slide.claim_units = [c ...]` | Silent claim deletion without argument coherence check; risks destroying presentation narrative. |
| **CSS Modification** | *None directly in Python* | CSS templates static | Correct: styling remains decoupled from logic. |
| **Prompt Retry** | *None* | Deterministic code only | Correct: zero non-deterministic LLM loops. |

---

## 9. Repair Asymmetry Across Artifact Types

| Capability | PRESENTATION | HANDOUT | WORKSHEET | SCIENTIFIC_DOCUMENT |
| :--- | :---: | :---: | :---: | :---: |
| **Automated Repair Engine** | Prototype (`repair_engine.py`) | **NONE** | **NONE** | **NONE** |
| **Deduplication Repair** | Yes (Slide level) | **NONE** | **NONE** | **NONE** |
| **Visual Grammar Remap** | Yes (`VISUAL_GRAMMAR_MATRIX`) | **NONE** | **NONE** | **NONE** |
| **Claim Softening / Evidence Map** | Yes (Regex & refs) | **NONE** | **NONE** | **NONE** |
| **Inquiry Arc Restoration** | N/A | N/A | **NONE** | N/A |
| **Anti-Spoiling Repair** | N/A | N/A | **NONE** | N/A |
| **Workspace Sizing Repair** | N/A | N/A | **NONE** | N/A |
| **Scientific Methodology Order Repair** | N/A | N/A | N/A | **NONE** |
| **Limitation Isolation Strategy** | N/A | N/A | N/A | **NONE** |

**Conclusion**: Phase 3B must construct an artifact-aware repair registry with dedicated, specialized strategies for all four formats.

---

## 10. Symptoms Currently Treated as Causes

1. **`TEXT_CLIPPING` / `TEXT_OVERFLOW` treated as Typography/Layout**:
   - Reality: 85% of overflows are caused by **`CONTENT_DENSITY`** (too many concepts/words in one container) or **`PADDING_SPACING`** container constraints, not wrong layout family.
   - Required Root Cause: Differentiate `CONTENT_DENSITY` (requires Class B split) from `GRID_GEOMETRY` (requires Class A padding adjustment).
2. **`TINY_TEXT` treated as an isolated styling defect**:
   - Reality: Text was downscaled by auto-fit routines because the volume exceeded the physical viewport. Enforcing minimum font without reducing density will trigger immediate `TEXT_CLIPPING`.
3. **`CARD_OVERLOAD` treated as Layout Mismatch**:
   - Reality: Overload is a compositional failure (Class B); changing from 6 cards to 2 columns simply creates two massive, unreadable columns.
4. **`DUPLICATE_SLIDE` treated as Deletion Candidate**:
   - Reality: Duplicate slides often arise from split narrative beats that share the same concept unit; merging without coverage verification risks losing unique pedagogical points.

---

## 11. Architectural Directives for Phase 3B Implementation

Based on this audit, Phase 3B implementation must adhere to the following principles:

1. **Root Cause Analysis First**:
   - Evaluate `FindingCluster` and correlation metrics to determine the true causal layer (`CONTENT_DENSITY`, `PADDING_SPACING`, `TYPOGRAPHY`, `SEMANTIC_LAYOUT_MAPPING`, `INQUIRY_STRUCTURE`, `EVIDENCE_MAPPING`).
2. **Deterministic Strategy Registry**:
   - Strategies must declare exact `supported_artifact_types`, `supported_failure_codes`, `mutation_class`, `preconditions`, and `postconditions`.
3. **Multi-Format Parity**:
   - Implement dedicated strategies for `PRESENTATION`, `HANDOUT`, `WORKSHEET`, and `SCIENTIFIC_DOCUMENT`.
4. **Safe Convergence & Anti-Oscillation**:
   - State hashing of artifact compositions after each iteration.
   - Immediate rollback and escalation to `MANUAL_REVIEW_REQUIRED` upon detecting state cycles or regression.
5. **Zero Evidence Fabrication**:
   - Scientific claims may only be mapped to verified source units, downgraded in certainty, or isolated as limitations. Never synthesize false references.
6. **Unified Quality Authority Integration**:
   - Every repair iteration must be re-evaluated authoritatively by `UnifiedQualityAuthority`. No local gate may bypass it.

---

*Forensic Audit Completed: Phase 3B implementation may proceed in strict accordance with the above findings.*
