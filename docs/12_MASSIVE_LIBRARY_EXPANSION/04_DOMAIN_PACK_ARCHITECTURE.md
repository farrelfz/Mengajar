# 04 — Domain Pack Architecture

## Modular, Pluggable Capability Packs

Batch 10 establishes the **Domain Pack Architecture** in `app/libraries/packs/`:

```
app/libraries/
├── __init__.py                # Main registration entry point
├── catalog.py                 # Machine-readable discovery & filter API
├── packs/
│   ├── __init__.py            # Domain pack exports
│   ├── universal_pack.py      # General structure, comparison, collection
│   ├── pedagogy_pack.py       # Scaffolding, misconception, practice, assessment
│   ├── scientific_thinking_pack.py # Hypothesis, observation, causality, CER
│   ├── research_education_pack.py  # Methodology, literature, results, novelty
│   ├── academic_writing_pack.py    # Paragraph anatomy, thesis map, outline
│   ├── experiment_pack.py     # Controls, protocols, safety, apparatus
│   ├── data_literacy_pack.py  # Chart reading, correlations, distributions
│   └── presentation_pack.py   # Hooks, big ideas, narrative arcs, summaries
```

---

## Design Principles of Domain Packs

1. **Zero Core Modifications**: Adding a new domain pack (e.g. `register_chemistry_pack()`, `register_economics_pack()`) requires **0 changes** to:
   - `CompositionBridge`
   - `MasterRenderEngine`
   - `HTMLAssembler`
   - `FormatRegistry`
   - `PDFValidator`
2. **Factory Driven**: Over 95% of domain pack capabilities are generated directly via `register_family_capability()`.
3. **Decentralized Parameter Extraction**: Domain packs can optionally attach specialized parameter extraction functions without modifying core pipeline solvers.
4. **Rich Metadata & Multi-Axis Taxonomy**: Every capability carries domain, category, semantic tags, supported artifact types, and a full `TaxonomySignature`.
