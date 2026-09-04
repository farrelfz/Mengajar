# Pipeline Stage Contracts

This document details the interface and requirements protocols for stages.

## Stage Protocol
Each execution node is defined by a class implementing `ProductionStage` or the stage protocol:
* `stage_id`: Unique string tag.
* `stage_type`: Categorical identifier.
* `should_execute(context)`: Skips stage run dynamically if not required.
* `validate_input(context)`: Explicit checks for upstream data prerequisites.
* `run(context)`: Executed logic.

## Stage Taxonomy
1. **RequestValidationStage**: Evaluates parameters.
2. **KnowledgeGroundingStage**: Detects fact unsupported claims.
3. **MaterialDirectingStage**: Plans narrative progression.
4. **PersonalizationStage**: Applies learner profiling adaptation.
5. **CompositionStage**: Generates layout block parameters.
6. **RenderingStage**: Invokes master rendering engine to write PDF.
7. **QualityEvaluationStage**: Evaluates layout scoring.
8. **GenerativeCriticStage**: Proposes visual/pedagogical correction patches.
9. **RefinementStage**: Commits localized changes to composition.
10. **ArtifactValidationStage**: Checks PDF geometry and integrity.
11. **FinalizationStage**: Registers metadata and final publication status.
