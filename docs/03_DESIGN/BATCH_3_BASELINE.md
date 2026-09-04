# BATCH 3 BASELINE AUDIT

> **File:** `docs/03_DESIGN/BATCH_3_BASELINE.md`
> **Date:** 2026-08-23
> **Status:** Initial Audit before BATCH 3 Execution

## 1. Existing design-related files
- `app/design/__init__.py` (Empty stub)
- `app/design/color_system.py` (Empty stub)
- `app/design/layout_engine.py` (Empty stub)
- `app/design/spacing.py` (Empty stub)
- `app/design/theme_manager.py` (Empty stub)
- `app/design/typography.py` (Empty stub)
- `app/intelligence/schemas.py` (Contains upstream definitions like `VisualIntent`, `BlueprintCandidateType`, `ContentDensity`, but NO actual design artifacts).

## 2. Existing color system
None exists. `color_system.py` is empty. No design tokens or palettes are defined.

## 3. Existing typography system
None exists. `typography.py` is empty. No scales are defined for different document modes.

## 4. Existing spacing system
None exists. `spacing.py` is empty.

## 5. Existing layout engine
None exists. `layout_engine.py` is empty. There are no grids or safe area calculations.

## 6. Existing theme manager
None exists. `theme_manager.py` is empty.

## 7. Existing template structure
`templates/` directory exists conceptually in architecture but no semantic-to-template mapping logic exists yet.

## 8. Existing domain schemas
Batch 2 defined semantic schemas (`ContentUnit`, `ContentGroup`, `BlueprintProposal`), which stop just short of design logic. There are no schemas for `VisualBlueprint` or `PageType`.

## 9. Existing BlueprintProposal fields relevant to design
- `document_genre`: Affects KTI vs Tutorial.
- `recommended_mode`: `A4_TUTORIAL` vs `PRESENTATION_16_9`.
- `content_groups`: Array of semantically grouped content.
  - `blueprint_candidate`: e.g. `TITLE_BLOCK`, `DATA_EVIDENCE_BLOCK`.
  - `primary_visual_intent`: e.g. `PROCESS_FLOW`, `DATA_TREND`.
  - `density`: e.g. `LOW`, `HIGH`.
  - `importance_rank`: Determines visual hierarchy.
  - `kti_bab`: Used for KTI-specific treatment.

## 10. Current architectural boundaries
The line is firmly drawn at `BlueprintProposal`. Intelligence produces the semantic blueprint; Design must consume it.
- `app/intelligence/` must NOT contain design logic.
- `app/design/` must NOT contain HTML/CSS/Playwright code.

## 11. Design risks
- Risk of polluting `VisualBlueprint` with HTML/CSS instead of abstract tokens.
- Risk of miscalculating density and causing overflow without emitting warnings.
- Risk of visual monotony if the engine defaults to the same page type continuously.
- Risk of breaking semantic traceability during pagination or composition.

## 12. Missing abstractions
- `VisualBlueprint`, `PageType`, `CompositionPattern`, `DesignWarning`, `BalanceReport`.
- Token management system.
- Density Engine.
- Balance Evaluator.

## 13. Existing code that should be preserved
- `app/intelligence/schemas.py` must NOT be altered to add design attributes. All design artifacts must live in `app/design/schemas.py` to maintain boundary integrity.
- `app/config/settings.py` structure should be preserved.
