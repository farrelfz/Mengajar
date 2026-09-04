# Artifact Lifecycle

This document details output references, metadata tracking, and state lifecycles.

## Lifecycle States
Generated files progress through the following states:
```text
DECLARED -> GENERATED -> VALIDATED -> APPROVED -> PUBLISHED / REJECTED / FAILED
```

- **DECLARED**: Proposed specs.
- **GENERATED**: Output file written by renderers.
- **VALIDATED**: QA checks passed (e.g. PyMuPDF integrity check).
- **APPROVED**: Final quality gate evaluation checks passed.
- **PUBLISHED**: Distributed to output folder.

## Artifact Registry
The `ArtifactRegistry` stores `ArtifactRecord` metadata (id, type, paths, producer_stage, created_at, checksums). This ensures files are registered and tracked cleanly without duplicating huge binaries in memory.
