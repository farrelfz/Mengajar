# 05 — Domain Scalability & Isolation Audit

## 1. Hypothetical Plugin Experiment: Adding a New Domain Pack

We traced what is required to introduce a completely new domain capability, e.g.:
`chemistry.titration_curve` or `experiment.controlled_variable_matrix`.

### Steps Required:
1. **Define Capability Contract & Renderer:** Create `app/libraries/chemistry/titration.py` defining `TitrationCurveSpec` and `TitrationCurveRenderer`.
2. **Register into Registry:** Call `registry.register(titration_curve_capability)` in `app/libraries/__init__.py`.
3. **Intent Matching:** `LibraryResolver` automatically matches tags (`"titration"`, `"chemistry"`, `"acid_base"`) without code changes.
4. **Execution & Rendering:** `CompositionBridge` executes `cap.renderer.render(spec)` and outputs SVG/HTML seamlessly.

---

## 2. Identified Domain Leakage & Bottlenecks

### Finding 1: `CompositionBridge._infer_spec_params` Heuristic Ladder
In [`app/composition/bridge.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/composition/bridge.py#L174-L263), when automated pipeline execution bridges Level A content into capability specs without explicit AI parameter generation, it relies on an `if-elif` ladder matching string capability IDs:
```python
if "hero" in cap_id: ...
elif "concept" in cap_id: ...
elif "worked_example" in cap_id: ...
elif "problem.funnel" in cap_id: ...
```
- **Architectural Risk:** Any new domain capability added to the repository will receive an empty dictionary `{}` unless a corresponding branch is added to `_infer_spec_params` or the AI Content Intelligence layer outputs explicit parameters for the capability spec.
- **Classification:** **YELLOW (Minor architectural coupling before massive scaling)**.

### Finding 2: Component Family Mapping
In `CompositionBridge` (line 77):
```python
if "physics" in cap_id or "diagram" in cap_id or "funnel" in cap_id or "pathway" in cap_id:
    comp_family = ComponentFamily.DIAGRAM_PLACEHOLDER
```
- **Architectural Risk:** Uses substring matching to determine `ComponentFamily` rather than deriving it directly from `cap.metadata.category` or metadata field.

---

## 3. Domain Scalability Score & Recommendation
- **Current Scalability Grade:** **YELLOW (Functional with minor configuration friction)**.
- **Remediation Target for Next Batch:**
  1. Add `default_spec_adapter` or parameter mapper directly on `Capability` object so capabilities own their own parameter extraction logic from `ContentBlueprint`.
  2. Map `ComponentFamily` from `CapabilityMetadata.category` instead of substring matching.
