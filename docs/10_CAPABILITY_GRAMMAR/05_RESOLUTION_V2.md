# 05 — Capability Resolution V2

## Overview

Resolver V2 upgrades capability resolution from brittle string heuristics to an explainable, multi-axis weighted constraint solver.

## Weighted Scoring Formula

For every registered candidate $C$ and pedagogical requirement $R$, the resolution score is calculated deterministically:

$$S(C, R) = w_\text{explicit} + S_\text{intent} + S_\text{structure} + S_\text{role} + S_\text{grammar} + S_\text{domain} + S_\text{format} + S_\text{density} + S_\text{tags}$$

### Dimension Weights
- **Explicit ID Match**: $100.0$ (immediate short-circuit win)
- **Primary Intent Match**: $+30.0$ (Supported intent: $+15.0$)
- **Information Structure Match**: $+25.0$ (Category affinity: $+15.0$)
- **Pedagogical Role Match**: $+20.0$
- **Visual Grammar Match**: $+15.0$
- **Domain Affinity**:
  - Exact domain match: $+20.0$
  - General domain capability match: $+10.0$
  - Cross-domain mismatch: $-15.0$
- **Physical Format Compatibility**: $+10.0$
- **Density Profile Match**: $+5.0$
- **Semantic Tag Matches**: $+15.0$ per tag (max $+30.0$)

## Deterministic Tie-Breaking
When two capabilities have equal score:
1. Higher Domain Specificity (specialized domain wins over `"general"`).
2. Format Affinity (capability explicitly listing target format wins).
3. Lexicographical Capability ID ordering (deterministic reproducible resolution).
