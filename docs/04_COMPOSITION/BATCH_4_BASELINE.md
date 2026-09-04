# BATCH 4 BASELINE

## 1. Repository State
The repository contains completed implementations of Batch 1 (Foundation), Batch 2 (Intelligence), and Batch 3 (Design System). All tests from batches 1, 2, and 3 are passing (57 total tests).

## 2. Existing Architecture
The current architecture pipeline translates source content as follows:
- **Batch 1 & 2:** Raw Markdown → `AnalysisResult` (Semantic properties) → `BlueprintProposal` (Content grouped semantically without design intent).
- **Batch 3:** `BlueprintProposal` → `VisualBlueprint` (Assigns abstract UI components, hierarchy levels, tokens, and basic page assignments).

## 3. Existing Contracts
- `BlueprintProposal`: Grouped content units with primary visual intent.
- `VisualBlueprint`: Contains abstract design constraints (colors, typography, hierarchy, global warnings, and a basic sequence of `PageComposition`).
- **Conflict Risk**: The Batch 3 `VisualBlueprint` currently emits a basic `PageComposition` list. Batch 4 must either consume these basic pages and re-evaluate them, or Batch 4 re-segments the original `BlueprintProposal` guided by `VisualBlueprint` constraints. Based on the prompt: `VisualBlueprint` -> `Composition Planning` -> `Page Segmentation` -> ... -> `DocumentComposition`. Batch 4 will define its own `DocumentComposition` schema with a much richer `PageComposition` (containing semantic `RegionRole` like HEADER, PRIMARY).

## 4. Test Baseline
- **Total Tests:** 57
- **Passed:** 57
- **Failed:** 0
- **Skipped:** 0

## 5. Integration Boundaries
Batch 4 must take `VisualBlueprint` as input and produce `DocumentComposition`.
- **Input:** `app.design.schemas.VisualBlueprint`
- **Output:** `app.composition.schemas.DocumentComposition`

## 6. Risks
- Splitting KTI structures across pages might break traceability if not handled correctly.
- Over-segmentation (creating too many pages) in A4 Landscape mode.
- Density engine mismatch: Batch 4's explicit segmentation logic might override or conflict with the earlier density estimations.

## 7. Scope for Batch 4
- Implement `app/composition/schemas.py` for `DocumentComposition`, `PageComposition`, `RegionAllocation`.
- Develop `DocumentComposer` capable of splitting, grouping, and organizing content into regions.
- Build mode-specific resolvers (`A4CompositionResolver`, `PresentationCompositionResolver`).
- Support KTI progression (BAB 1–5).
- Build continuation handling.
- Produce no HTML, CSS, or PDF generation logic.
