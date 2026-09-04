# 02 — RISK-02: Capability Parameter Decentralization

## 1. The Coupling Problem

Prior to Batch 7.9, `CompositionBridge._infer_spec_params` contained an 88-line `if-elif` ladder matching string capability IDs (`if "hero" in cap_id: ... elif "concept" in cap_id: ... elif "worked_example" in cap_id: ...`).

This created tight, centralized coupling:
- `CompositionBridge` had to know every domain parameter (torque radius, hypothesis variables, gap matrix fields, worked example calculations).
- Adding a new capability required modifying `CompositionBridge` or the capability would receive an empty `{}` spec parameter dictionary.

---

## 2. The Decentralized Architecture

We extended the `Capability` contract:
```python
class Capability(BaseModel, Generic[SpecT]):
    metadata: CapabilityMetadata
    spec_model: type[SpecT]
    renderer: CapabilityRenderer[SpecT]
    parameter_extractor: Callable[[Any, Any], dict[str, Any]] | None = None

    def extract_parameters(self, step: Any, material: Any) -> dict[str, Any]:
        if self.parameter_extractor:
            try:
                return self.parameter_extractor(step, material)
            except Exception:
                return {}
        return {}
```

Furthermore, `ComponentFamily` and `RenderTarget` are derived directly from `CapabilityMetadata.component_family` and `CapabilityMetadata.render_target`.

---

## 3. Bridge Simplification

`CompositionBridge` is now a pure orchestrator:
```python
# Derive component family & render target directly from capability metadata
comp_family = cap.metadata.component_family
render_target = cap.metadata.render_target

# Auto-extract parameters via decentralized capability extractor
if not spec_params or len(spec_params) <= 1:
    spec_params = cap.extract_parameters(step, material)

spec_instance = cap.spec_model(**spec_params)
cap_output = cap.renderer.render(spec_instance)
```

- **Domain branches in `CompositionBridge` before:** **9 branches (88 lines of hardcoded inference)**
- **Domain branches in `CompositionBridge` after:** **0 branches (0 lines)**
- **Extensibility:** Any new capability can be registered and rendered without touching `bridge.py`.
