# 10 — Director Diagnostics

## Machine-Readable Diagnostics

Every execution of `IntelligentMaterialDirector` emits structured telemetry:

```python
DirectorDiagnostics(
    strategy_selected=MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    strategy_score=0.95,
    domain_policy="physics",
    stage_count=5,
    warnings=[],
    density_budget="low",
    alternative_strategies=[
        ("misconception_correction", 0.90),
        ("worked_example_progressive", 0.85),
    ],
)
```
