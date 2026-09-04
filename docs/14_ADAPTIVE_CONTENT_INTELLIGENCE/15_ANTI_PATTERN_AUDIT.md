# 15 — Anti-Pattern Audit

| Anti-Pattern ID | Anti-Pattern Description | Architectural Defense in Batch 12 | Status |
|---|---|---|---|
| **ANTI-PATTERN 1** | Grade-based `if` ladders scattered across codebase | Centralized in `ComplexityPolicy` and `AdaptiveContentTransformer` | **PREVENTED** |
| **ANTI-PATTERN 2** | Duration-based `if` ladders | Centralized in `PacingPolicy` and `InstructionalTimeBudget` | **PREVENTED** |
| **ANTI-PATTERN 3** | Artifact type determines capability ID directly | Decoupled via `SemanticIntentSpec` & `ResolverV2` | **PREVENTED** |
| **ANTI-PATTERN 4** | Bundle artifacts duplicate each other | Enforced via `ContentAllocationPolicy` & `BundleCoherenceValidator` | **PREVENTED** |
| **ANTI-PATTERN 5** | Adaptation only changes density / word count | Substantive conceptual, formula, and vocabulary transformations | **PREVENTED** |
| **ANTI-PATTERN 6** | Presentation merely shortened handout | Differentiated roles: `PRESENTATION` (visual hook), `HANDOUT` (reference) | **PREVENTED** |
| **ANTI-PATTERN 7** | Assessment generated without learning objective traceability | Enforced via `SharedLearningObjective` coverage matrix | **PREVENTED** |
| **ANTI-PATTERN 8** | Prerequisite model ignored by director | `ConceptPrerequisiteGraph` flags missing prerequisite mastery | **PREVENTED** |
| **ANTI-PATTERN 9** | Complexity metadata exists but never affects output | Direct formula & vocabulary substitution into blueprints | **PREVENTED** |
| **ANTI-PATTERN 10**| Cross-artifact inconsistency | Shared single semantic source of truth via bundle planner | **PREVENTED** |
