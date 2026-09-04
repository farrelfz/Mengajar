# QUALITY EVALUATION CONTRACTS & DATA MODELS
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Enumerations
- **`QualityDimension`**:
  - `SEMANTIC_CORRECTNESS`: Objective coverage and clear concept formalization.
  - `PEDAGOGICAL_ALIGNMENT`: Learning journey sequencing, prerequisite ordering, scaffolding.
  - `STRUCTURAL_COHERENCE`: Non-empty sections, page allocations, and logical progression.
  - `INFORMATION_DENSITY`: Character volume per page/slide, text-to-visual ratio.
  - `FORMAT_INTEGRITY`: Rendered PDF point geometry and page count conformance.
  - `REDUNDANCY`: Non-trivial duplicate text blocks across pages.
- **`QualitySeverity`**: `INFO`, `LOW`, `WARNING`, `ERROR`, `CRITICAL`.
- **`QualityLevel`**: `EXCELLENT` ($\ge 0.95$), `GOOD` ($\ge 0.85$), `ACCEPTABLE` ($\ge 0.75$), `NEEDS_IMPROVEMENT` ($\ge 0.60$), `POOR` ($\ge 0.40$), `CRITICAL` ($< 0.40$).
- **`QualityGateDecision`**:
  - `PASS`: High composite score ($\ge 0.85$) with 0 warnings/errors.
  - `PASS_WITH_WARNINGS`: Meets acceptable quality standard with non-blocking warnings.
  - `NEEDS_REFINEMENT`: Contains functional errors or low score requiring refinement.
  - `FAIL`: Critical rendering or structural invariant violation.

---

### 2. Core Diagnostic Models
- **`QualityFinding`**: Contains `dimension`, `severity`, `finding`, `evidence` dict, `affected_artifact`, `affected_section`, `score_impact`, and actionable `recommendation`.
- **`QualityMetric`**: Contains `name`, `dimension`, `score` (0.0 to 1.0), `weight`, and `raw_value`.
- **`EvaluationTrace`**: Machine-readable audit trace logging per-evaluator metrics, stage status, and scoring rationale.
- **`QualityReport`**: Master artifact container encapsulating overall score, quality level, gate result, findings, metrics, and execution trace.
