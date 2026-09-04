# Execution Context

This document details the single, structured `ProductionJobContext` passed across workflow stages.

## Data Schema

* **job_id**: Unique context identifier.
* **request**: Immutable request spec containing raw inputs and configurations.
* **stage_results**: Historical map of completed execution results.
* **shared_data**: Typed namespace for intermediate artifacts:
  - `material_blueprint`: Proposed pedagogical blueprint.
  - `material_direction`: Narrative strategy.
  - `composition`: Page-by-page block layouts.
  - `quality_report`: Scoring metrics.
  - `refinement_history`: Iterate patch tracking.
* **gate_results**: List of gate decisions.
* **artifacts**: Output files registered.
* **refinement_iterations**: Count of refinement cycles.
* **retries_count**: Map of retry count metrics.
