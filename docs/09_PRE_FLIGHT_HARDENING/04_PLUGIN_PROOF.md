# 04 — Plugin Extensibility Proof

## 1. Objective

Prove that a completely new capability can be created, registered, resolved, parameterized, and rendered end-to-end **without editing any file in `app/composition/`, `app/rendering/`, or core infrastructure**.

---

## 2. The Test Capability: `test.experimental.variable_matrix`

In `tests/integration/test_decoupled_capability_pipeline.py`, we defined:

```python
class CustomPluginSpec(CapabilitySpec):
    sample_size: int = 50
    independent_factor: str = "Light Intensity"
    metric: str = "Photosynthesis Rate"

class CustomPluginRenderer(CapabilityRenderer[CustomPluginSpec]):
    def validate_spec(self, spec: CustomPluginSpec) -> bool:
        return spec.sample_size > 0
    def measure(self, spec: CustomPluginSpec, context=None):
        return {"height_px": 250}
    def render(self, spec: CustomPluginSpec, context=None) -> CapabilityOutput:
        html = f"""
        <div class="plugin-custom-matrix">
            <h3>Experimental Matrix: {spec.independent_factor} vs {spec.metric}</h3>
            <p>Sample Size: N={spec.sample_size}</p>
        </div>
        """
        return CapabilityOutput(
            capability_id="test.experimental.variable_matrix",
            output_format="html",
            rendered_content=html,
        )

def _custom_plugin_extractor(step, material):
    return {
        "sample_size": 120,
        "independent_factor": f"Custom Factor for {material.content.metadata.title}",
        "metric": "Yield Performance",
    }
```

---

## 3. End-to-End Execution Trace

1. **Registration:** `custom_registry.register(test_capability)`
2. **Semantic Blueprint:** `SemanticMaterialBlueprint` created with title `"Agricultural Lighting Experiment"`.
3. **Bridge Execution:** `bridge = CompositionBridge(registry=custom_registry)`
4. **Rendering Output:**
   - Page count: 1
   - Rendered HTML: `<div class="plugin-custom-matrix">...<h3>Experimental Matrix: Custom Factor for Agricultural Lighting Experiment vs Yield Performance</h3><p>Sample Size: N=120</p>...`
   - Core files modified: **0**

---

## 4. Verdict
The plugin architecture is **100% decentralized and verified**.
