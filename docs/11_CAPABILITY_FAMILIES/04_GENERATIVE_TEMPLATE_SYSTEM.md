# 04 — Generative Template System

## Contract & Pipeline

The Generative Template System implements the layout and markup generation logic for capability families.

### The Template Protocol (`FamilyTemplate`)

```python
class FamilyTemplate(ABC, Generic[TSpec]):
    template_id: str
    family: CapabilityFamily
    spec_model: type[TSpec]
    preferred_render_target: RenderTarget = RenderTarget.HTML

    def validate_spec(self, spec: TSpec) -> bool:
        return isinstance(spec, self.spec_model)

    @abstractmethod
    def render_html(self, spec: TSpec, context: dict[str, Any] | None = None) -> str:
        """Render structural responsive HTML."""
        pass

    def render_svg(self, spec: TSpec, context: dict[str, Any] | None = None) -> str:
        """Render raw SVG if supported."""
        raise NotImplementedError(...)

    def render(self, spec: TSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        """Execute template rendering pipeline."""
        ...
```

---

## Canonical Templates Implemented in Batch 9

1. **`LinearProcessTemplate` (`process.linear`)**:
   - Supports horizontal and vertical stage flows with step numbering, status pills, and responsive connector chevrons.
   - Dynamic density adaptation: Trims descriptions in `MINIMAL` density; expands metadata grids in `DENSE_REFERENCE`.

2. **`MatrixComparisonTemplate` (`comparison.matrix`)**:
   - Renders multi-item, multi-axis comparison cards with badge tags, attribute lists, and highlight styling.

3. **`HierarchyTreeTemplate` (`hierarchy.tree`)**:
   - Renders multi-tiered conceptual hierarchies and taxonomies with automatic circular reference detection.

4. **`EvidenceChainTemplate` (`reasoning.evidence_chain`)**:
   - Renders structured claim-evidence-warrant-conclusion cards with citation and empirical data callouts.

5. **`ProgressionLadderTemplate` (`progression.ladder`)**:
   - Formats Bloom's cognitive scaffolding ladders with level badges and pedagogical focus callouts.

6. **`QuantitativeDerivationTemplate` (`quantitative.derivation`)**:
   - Formats step-by-step mathematical derivations, formula boxes, and variable definition bars.

7. **`RelationshipMapTemplate` (`relationship.network`)**:
   - Renders directed causal networks and factor links with node/edge validation.

8. **`CardCollectionTemplate` (`collection.grid`)**:
   - Generates responsive definition and concept card grids.
