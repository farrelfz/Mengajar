# 05 — Deterministic Capability Registration

## Registration Pipeline

The default registration sequence is coordinated deterministically in `app/libraries/__init__.py`:

```python
def register_all_default_capabilities(registry: CapabilityRegistry | None = None) -> CapabilityRegistry:
    """Register all standard built-in capabilities and domain packs into registry."""
    reg = registry or CapabilityRegistry.get_instance()

    # 1. Research Education Baseline Capabilities
    ...

    # 2. Universal Pedagogy & Scaffolding Baseline
    ...

    # 3. Physics Mechanics & Mathematics Baseline
    ...

    # 4. Domain Packs (Batch 10 Massive Expansion)
    register_universal_pack(reg)
    register_pedagogy_pack(reg)
    register_scientific_thinking_pack(reg)
    register_research_education_pack(reg)
    register_academic_writing_pack(reg)
    register_experiment_pack(reg)
    register_data_literacy_pack(reg)
    register_presentation_pack(reg)

    return reg
```

---

## Idempotency & Overwrite Guarantees
- Calling `register_all_default_capabilities()` multiple times is idempotent.
- Capabilities registered with `overwrite=True` update existing entries cleanly without creating duplicate registration records in multi-axis taxonomy index tables.
- In-memory lookups remain sub-millisecond even with 100+ capabilities.
