# 12 — Pipeline Integration & Backward Compatibility

## Seamless Integration in `MaterialProductionPipeline`

```python
pipeline = MaterialProductionPipeline()

# Standard production with Intelligent Direction enabled
result = await pipeline.produce_artifact(
    raw_input=text,
    source_hint="physics_torque.md",
    domain=KnowledgeDomain.PHYSICS,
    audience=AudienceLevel.HIGH_SCHOOL,
    target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
    target_format="presentation_16_9",
    director_enabled=True,
    preferred_strategy=MaterialStrategyType.CONCRETE_TO_ABSTRACT,
)
```

- **Backward Compatibility**: `director_enabled=False` by default maintains 100% regression compatibility for legacy test cases.
- **Pipeline Result**: `MaterialJobResult.material_direction` carries the full `MaterialDirection` (journey, choreography, trace, diagnostics).
