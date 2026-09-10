"""
Universal Document Intelligence System V5 — Benchmark Generalization Reports Generator.

Phase 4.1: Persists machine-readable JSON and human-readable Markdown reports detailing
corpus convergence, operator applicability envelopes, generalization metrics, and integrity audits.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Sequence

from app.benchmarking.contracts import (
    BenchmarkExecutionOutcome,
    BenchmarkIntegrityReport,
    GeneralizationMetrics,
    OperatorApplicabilityEnvelope,
)

logger = logging.getLogger("benchmarking.reports")


class BenchmarkReportGenerator:
    """Generates structured benchmark artifacts, reports, and operator matrices."""

    @classmethod
    def generate_all_reports(
        cls,
        outcomes: Sequence[BenchmarkExecutionOutcome],
        metrics: GeneralizationMetrics,
        envelopes: Dict[str, OperatorApplicabilityEnvelope],
        integrity: BenchmarkIntegrityReport,
        output_dir: Path | str,
    ) -> Dict[str, Path]:
        """Generates and writes all canonical benchmark deliverables."""
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, Path] = {}

        # 1. generalization_report.json
        gen_json_path = out_p / "generalization_report.json"
        gen_data = {
            "metrics": metrics.model_dump(),
            "integrity": integrity.model_dump(),
            "outcomes_count": len(outcomes),
            "outcomes": [o.model_dump() for o in outcomes],
        }
        gen_json_path.write_text(json.dumps(gen_data, indent=2), encoding="utf-8")
        paths["generalization_json"] = gen_json_path

        # 2. generalization_report.md
        gen_md_path = out_p / "generalization_report.md"
        gen_md_content = cls._build_generalization_markdown(outcomes, metrics, integrity)
        gen_md_path.write_text(gen_md_content, encoding="utf-8")
        paths["generalization_md"] = gen_md_path

        # 3. operator_matrix.json
        op_json_path = out_p / "operator_matrix.json"
        op_data = {k: v.model_dump() for k, v in envelopes.items()}
        op_json_path.write_text(json.dumps(op_data, indent=2), encoding="utf-8")
        paths["operator_json"] = op_json_path

        # 4. operator_matrix.md
        op_md_path = out_p / "operator_matrix.md"
        op_md_content = cls._build_operator_markdown(envelopes)
        op_md_path.write_text(op_md_content, encoding="utf-8")
        paths["operator_md"] = op_md_path

        logger.info("Successfully generated all Phase 4.1 reports in %s", out_p)
        return paths

    @classmethod
    def _build_generalization_markdown(
        cls,
        outcomes: Sequence[BenchmarkExecutionOutcome],
        metrics: GeneralizationMetrics,
        integrity: BenchmarkIntegrityReport,
    ) -> str:
        rows = []
        for o in outcomes:
            comm = ", ".join(o.operators_committed) if o.operators_committed else "None"
            rows.append(
                f"| `{o.fixture_id}` | `{o.artifact_type}` | `{o.corpus_category.value}` | `{o.split.value}` | `{o.final_state}` | {o.overall_quality_score:.3f} | {o.hard_blockers_count} | {o.total_iterations} | {comm} |"
            )
        rows_str = "\n".join(rows)

        warning_badge = "**CRITICAL WARNING: GENERALIZATION DEFICIT DETECTED**" if metrics.generalization_warning else "**PASSED: GENERALIZATION VALIDATED**"
        immutability_str = "VERIFIED (100% untouched)" if integrity.fixtures_immutable else "FAILED: Fixtures Mutated"
        leakage_str = "VERIFIED (Zero unseen contamination)" if not integrity.leakage_detected else "FAILED: Leakage Detected"
        repro_str = "VERIFIED (Deterministic hashes match)" if integrity.reproducibility_verified else "FAILED"

        return f"""# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 4.1 — BENCHMARK GENERALIZATION VALIDATION REPORT

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}  
**Status:** {warning_badge}  

---

## 1. Corpus Generalization Summary Metrics

| Metric Description | Canonical Symbol | Value | Certified Threshold |
| :--- | :---: | :---: | :---: |
| **Total Benchmark Jobs** | $N$ | {metrics.total_jobs} | $\\ge 40$ |
| **Known Reference Jobs** | $N_{{\\text{{known}}}}$ | {metrics.known_jobs} | $\\ge 8$ |
| **Unseen Generalization Jobs** | $N_{{\\text{{unseen}}}}$ | {metrics.unseen_jobs} | $\\ge 20$ |
| **Pathological Stress Jobs** | $N_{{\\text{{path}}}}$ | {metrics.pathological_jobs} | $\\ge 12$ |
| **Repair Generalization Rate** | $\\text{{RGR}}$ | **{metrics.repair_generalization_rate * 100:.1f}%** | $\\ge 80.0\\%$ |
| **Repair Regression Rate** | $\\text{{RRG}}$ | **{metrics.repair_regression_rate * 100:.1f}%** | $\\le 5.0\\%$ |
| **False Repair Rate** | $\\text{{FRR}}$ | **{metrics.false_repair_rate * 100:.1f}%** | $\\le 5.0\\%$ |
| **Causal Resolution Rate** | $\\text{{CRR}}$ | **{metrics.causal_resolution_rate * 100:.1f}%** | $\\ge 85.0\\%$ |
| **Zero-Effect Rate** | $\\text{{ZER}}$ | **{metrics.zero_effect_rate * 100:.1f}%** | $\\le 10.0\\%$ |
| **Known Corpus Mean Score** | $\\bar{{S}}_{{\\text{{known}}}}$ | **{metrics.known_corpus_mean_score:.3f}** | $\\ge 0.950$ |
| **Unseen Corpus Mean Score** | $\\bar{{S}}_{{\\text{{unseen}}}}$ | **{metrics.unseen_corpus_mean_score:.3f}** | $\\ge 0.900$ |
| **Generalization Gap** | $\\Delta G$ | **{metrics.generalization_gap:.3f}** | $\\le 0.080$ |
| **Worst-Case Score** | $\\min(S)$ | **{metrics.worst_case_score:.3f}** | $\\ge 0.750$ |
| **Unseen Blocker Retention Rate** | $\\text{{BRR}}$ | **{metrics.unseen_blocker_retention_rate * 100:.1f}%** | $0.0\\%$ |
| **Mean Iterations to Convergence** | $\\bar{{I}}$ | **{metrics.mean_iterations_to_convergence:.2f}** | $\\le 2.50$ |

---

## 2. Integrity & Anti-Leakage Verification
- **Fixture Immutability**: {immutability_str}
- **Anti-Leakage Guard**: {leakage_str}
- **Reproducibility**: {repro_str}

---

## 3. Comprehensive Benchmark Matrix

| Fixture ID | Artifact Type | Category | Split | Final State | Quality | Blockers | Iters | Primary Committed Repair |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
{rows_str}
"""

    @classmethod
    def _build_operator_markdown(
        cls,
        envelopes: Dict[str, OperatorApplicabilityEnvelope],
    ) -> str:
        rows = []
        for op_id, env in sorted(envelopes.items()):
            arts = ", ".join(env.supported_artifact_types)
            rcs = ", ".join(env.supported_root_causes)
            rows.append(
                f"| `{op_id}` | `{env.evidence_strength.value}` | `{arts}` | `{rcs}` | {env.unseen_success_rate * 100:.1f}% | {env.regression_rate * 100:.1f}% | {env.fixture_diversity_count} |"
            )
        rows_str = "\n".join(rows)

        return f"""# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# OPERATOR APPLICABILITY ENVELOPE MATRIX

---

## 1. Certified Repair Operator Performance & Applicability Envelopes

| Operator Identifier | Evidence Strength | Supported Formats | Supported Root Causes | Unseen Win-Rate | Regression Rate | Fixture Diversity |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: |
{rows_str}

---

## 2. Evidence Strength Classification Rules
- **STRONG**: Validated across unseen fixtures across multiple structural signatures, with zero regressive outcomes and >= 6 fixtures.
- **MODERATE**: Validated across at least 2 structural signatures, >= 5 fixtures.
- **LIMITED**: 3 to 5 fixtures or limited to single artifact type.
- **INSUFFICIENT**: Fewer than 3 distinct fixtures or single success. Operators marked `INSUFFICIENT` must NOT be scheduled as primary automated repairs on high-stakes pipelines without manual review escalation.
"""
