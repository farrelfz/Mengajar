# VISUAL QUALITY & INFORMATION DENSITY EVALUATION
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Density Evaluator (`app/quality/density_evaluator.py`)
Assesses human-readable text volume per page/slide in a strictly format-aware manner.

### 2. Format-Aware Text Budgeting
- **16:9 Presentation (`presentation_16_9`)**:
  - Maximum recommended slide text volume: **1,200 characters**.
  - Moderate slide text volume: 400–800 characters.
  - Exceeding 1,200 characters flags `QualitySeverity.WARNING`.
  - Exceeding 1,800 characters flags `QualitySeverity.ERROR`.
- **A4 Portrait Document (`a4_portrait`)**:
  - Maximum recommended page text volume: **3,500 characters**.
  - Dense document mode supports up to 4,500 characters with 2-column layouts.
- **A4 Landscape Tutorial (`a4_landscape`)**:
  - Maximum recommended page text volume: **2,500 characters**.

### 3. Plain-Text Extraction
Density evaluation strips HTML/SVG structural markup before character counting, ensuring that complex SVG diagrams and CSS styles do not falsely trigger density violations.
