# RUNTIME CALL GRAPH AUDIT
## BATCH 15.5 — ACCEPTANCE AUDIT & ADVERSARIAL VALIDATION

### 1. Concrete Runtime Call Graph
```text
MaterialProductionPipeline.produce_artifact(..., evaluate_quality=True)
  │
  ▼
QualityEvaluationEngine.evaluate_artifact(job_id, material_bp, journey, composition, pdf_path, target_format)
  ├── 1. StructuralEvaluator.evaluate(blueprint, composition)
  │       └── Returns (struct_metrics: list[QualityMetric], struct_findings: list[QualityFinding])
  │
  ├── 2. SemanticEvaluator.evaluate(blueprint)
  │       └── Returns (sem_metrics: list[QualityMetric], sem_findings: list[QualityFinding])
  │
  ├── 3. PedagogicalEvaluator.evaluate(journey, blueprint)
  │       └── Returns (ped_metrics: list[QualityMetric], ped_findings: list[QualityFinding])
  │
  ├── 4. DensityEvaluator.evaluate(composition, target_format)
  │       └── Returns (dens_metrics: list[QualityMetric], dens_findings: list[QualityFinding])
  │
  ├── 5. RedundancyEvaluator.evaluate(composition)
  │       └── Returns (red_metrics: list[QualityMetric], red_findings: list[QualityFinding])
  │
  └── 6. FormatEvaluator.evaluate(pdf_path, target_format, expected_page_count)
          └── Returns (fmt_metrics: list[QualityMetric], fmt_findings: list[QualityFinding])
  │
  ▼
QualityEvaluationEngine._compute_quality_score(all_metrics)
  ├── Groups metrics by QualityDimension
  ├── Computes dimensional weighted averages
  ├── Applies DIMENSION_WEIGHTS
  └── Determines QualityLevel (EXCELLENT, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, POOR, CRITICAL)
  │
  ▼
QualityEvaluationEngine._arbitrate_quality_gate(score, all_findings)
  ├── Checks for CRITICAL findings -> FAIL
  ├── Checks for ERROR findings or score < 0.70 -> NEEDS_REFINEMENT
  ├── Checks for WARNING findings or score < 0.85 -> PASS_WITH_WARNINGS
  └── Else (score >= 0.85 and 0 warnings) -> PASS
  │
  ▼
QualityReport(job_id, overall_score, quality_level, gate_result, findings, metrics, trace, metadata)
```

---

### 2. Dead Code & Exception Masking Audit
- **Dead Evaluators**: 0. Every evaluator is directly called in sequence.
- **Exception Swallowing**: None. Python exceptions in evaluators propagate up or raise descriptive diagnostics.
- **Always-Pass Hardcoded Logic**: None. Gate decisions are dynamically arbitrated from findings severity and scores.
