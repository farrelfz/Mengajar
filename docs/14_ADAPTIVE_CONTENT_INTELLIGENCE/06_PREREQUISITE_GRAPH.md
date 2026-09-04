# 06 — Concept Prerequisite Graph

## Dependency Modeling & Missing Knowledge Detection

The `ConceptPrerequisiteGraph` models structural concept relationships:

```
[TORQUE]
   ├── [scalar_force]
   ├── [lever_distance]
   ├── [vector_components]
   └── [rotational_pivot]
```

### Remediation Workflow
When `check_missing_prerequisites()` identifies unmastered concepts (e.g. `vector_components` for a middle school student), the system avoids immediate formalization and flags micro-remediation requirements.
