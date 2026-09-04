# 02 — Capability Family Architecture

## Architectural Evolution: From Monolithic Capabilities to Generative Families

### The Problem of Individual Capability Architecture
Previously, creating a new capability required writing:
1. A distinct Pydantic `CapabilitySpec` subclass.
2. A dedicated `CapabilityRenderer` subclass containing raw HTML or SVG string generation logic.
3. Custom rendering CSS and layout coordinates.

While modular, scaling this paradigm to 100+ domain capabilities produces severe architectural friction:
- **Renderer Explosion**: Hundreds of separate Python rendering classes doing virtually identical work (e.g. stage pipelines, contrast cards, equation chains).
- **Code Duplication**: Redundant SVG chevron math, HTML card wrappers, and CSS flex grids.
- **Maintenance Fragility**: Design token or styling updates required editing dozens of individual files.

---

## The Solution: The Capability Family Abstraction

```
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Material                        │
│   (Semantic Intent + Pedagogical Step + Source Content)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Library Resolver V2                      │
│       (Matches Taxonomy, Family, Domain, Format)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Capability Metadata                     │
│    (Domain Context, Semantic Tags, Complexity, Taxonomy)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                Capability Family Abstraction                │
│    (PROCESS, COMPARISON, HIERARCHY, REASONING, etc.)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Generative Family Template                 │
│   (LinearProcessTemplate, MatrixComparisonTemplate, etc.)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Master Render Engine & Artifact Format          │
│            (Deterministic HTML / SVG / PDF Output)          │
└─────────────────────────────────────────────────────────────┘
```

### Decoupled Separation of Concerns
1. **Capability**: Owns semantic identity, domain relevance, and decentralized parameter extraction (`extract_parameters()`).
2. **Capability Family**: Defines the abstract structural rendering grammar (e.g., `PROCESS_VISUALIZATION`, `COMPARATIVE_REASONING`).
3. **Family Template**: Owns structural layout generation, markup assembly, and density adaptation (`render_html()`, `render_svg()`).
4. **Artifact Format**: Single source of truth for physical dimensions and geometry (`a4_portrait`, `a4_landscape`, `presentation_16_9`).
5. **Composition Bridge & Master Engine**: Orchestrates pages and renders physical PDFs without any family-specific hardcoded switches.
