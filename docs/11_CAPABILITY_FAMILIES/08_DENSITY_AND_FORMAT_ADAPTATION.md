# 08 — Density & Format Adaptation

## Structural Adaptation (Not Just CSS Font Shrinking)

Capability Families adapt structurally based on `DensityProfile` and `ArtifactFormat`:

### Density Adaptation Rules

| Density Profile | Process Family | Comparison Family | Quantitative Family |
|---|---|---|---|
| `MINIMAL` | Renders stage labels and icons only (hides detailed descriptions). | 2-column compact contrast with key differences. | Governing formula + Final result only. |
| `FOCUSED` | Standard stage card with title and concise explanatory paragraph. | Multi-column card grid with tagged badges and bullet attributes. | Initial formula, 2-3 key transformation steps, final result. |
| `ANALYTICAL` | Step cards + detailed procedure + validation checkpoints. | Full comparison matrix with multi-dimensional criteria rows. | Full step-by-step mathematical proof with intermediate comments. |
| `DENSE_REFERENCE` | Step cards + parameters table + equipment/reagent metadata. | Comprehensive tabular matrix with definitions and trade-offs. | Comprehensive variable mapping table + dimensional units. |

---

## Physical Format Adaptation Rules

- **A4 Portrait (`210 x 297 mm`)**:
  - Vertical flex flows (`flex-col space-y-3`) or 2-column grid arrangements.
  - Generates top-to-bottom reading rhythm.
- **A4 Landscape (`297 x 210 mm`)**:
  - Horizontal flex flows (`flex-row flex-wrap gap-3`) or 3-column card layouts.
- **16:9 Presentation (`338.7 x 190.5 mm`)**:
  - Horizontal pipeline flows with generous stage padding and high visual contrast for projection.
