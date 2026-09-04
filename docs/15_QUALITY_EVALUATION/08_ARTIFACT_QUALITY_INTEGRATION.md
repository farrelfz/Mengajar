# ARTIFACT QUALITY & GEOMETRY INTEGRATION
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Format Evaluator (`app/quality/format_evaluator.py`)
Directly inspects rendered physical PDF binaries using PyMuPDF (`fitz`).

### 2. Physical Point Geometry Verification
- **A4 Portrait**: Expected $595.0 \times 841.9\text{ pt}$ ($210 \times 297\text{ mm}$).
- **A4 Landscape**: Expected $841.9 \times 595.0\text{ pt}$ ($297 \times 210\text{ mm}$).
- **Presentation 16:9**: Expected $960.0 \times 540.0\text{ pt}$ ($338.7 \times 190.5\text{ mm}$).

### 3. Safety Invariants
- **Missing PDF Path**: Triggers `QualitySeverity.CRITICAL` and score $0.0$.
- **0-Page / Corrupted PDF**: Triggers `QualitySeverity.CRITICAL`.
- **Dimensional Deviation $> 2.0\text{ pt}$**: Triggers `QualitySeverity.ERROR`.
