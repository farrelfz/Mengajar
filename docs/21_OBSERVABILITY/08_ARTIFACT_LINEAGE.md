# Artifact Lineage

This document explains artifact tracking, parent-child relationships, and search interfaces.

## Artifact Lineage Model
- **ArtifactLineageRecord**: Stores artifact ID, path, type, source run ID, trace ID, format configurations, page counts, parents, and metadata.
- Workspace-relative path formatting ensures that JSON manifests generated across different filesystems remain deterministic.

## Graph Traversal
- **ArtifactLineageGraph**: Compiles records into an adjacency graph.
- **get_ancestors(artifact_id)**: Recursively crawls upstream dependencies.
- **get_descendants(artifact_id)**: Recursively crawls downstream dependents.
