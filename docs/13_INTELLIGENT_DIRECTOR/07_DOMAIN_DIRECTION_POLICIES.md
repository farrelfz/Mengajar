# 07 — Domain Direction Policies

## Pluggable Policy Registry

The system provides pluggable domain direction policies in `app/director/policies/`:

- `PhysicsDomainPolicy`: Phenomenon-first progression, free-body and vector diagrams.
- `MathematicsDomainPolicy`: Proof and derivation sequencing, step-by-step math cards.
- `ResearchEducationDomainPolicy`: Gap analysis, conceptual frameworks, method matrices.
- `AcademicWritingDomainPolicy`: Paragraph anatomy, thesis scaffolding, counterargument refutations.
- `ExperimentDesignDomainPolicy`: Variable controls, observation tables, error analysis.
- `PedagogyDomainPolicy`: Misconception elicitation, guided practice, checkpoint cards.
- `PresentationDomainPolicy`: High visual contrast, dramatic arcs, hero statement hooks.

---

## Extensibility Without Core Modifications
New domains (e.g. `ChemistryDomainPolicy`, `EconomicsDomainPolicy`) can register dynamically via `registry.register(CustomPolicy())` without touching the Director core.
