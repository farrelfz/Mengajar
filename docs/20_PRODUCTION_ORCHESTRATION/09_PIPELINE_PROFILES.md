# Pipeline Profiles

This document details Named Pipeline Profiles and their stage execution sequences.

## Named Profiles

### 1. MINIMAL
Includes only request validation, composition, rendering, and delivery:
- `validation` -> `composition` -> `rendering` -> `finalization`

### 2. STANDARD
The default production profile:
- `validation` -> `directing` -> `blueprint_generation` -> `composition` -> `pre_render_quality` -> `rendering` -> `artifact_validation` -> `finalization`

### 3. FULL_PRODUCTION
The complete orchestration chain:
- `validation` -> `grounding` -> `directing` -> `personalization` -> `blueprint_generation` -> `composition` -> `pre_render_quality` -> `rendering` -> `artifact_validation` -> `finalization`

### 4. STRICT
Standard full production chain with strict quality evaluation gates (requires score >= 0.75, grounding contradictions == 0).
- Triggers critic review and refinement loops if gates reject candidate.
- Grounding checks are strictly enforced.
