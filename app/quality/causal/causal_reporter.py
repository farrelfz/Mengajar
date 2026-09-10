"""
Universal Document Intelligence System V5 — Causal Intelligence Reporter.

Phase 3B: Generates forensic diagnostic reports in JSON and Markdown formats,
strictly separating OBSERVATIONS, INFERENCES, and CONFIRMED CAUSES.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.quality.causal.causal_engine import CausalAnalysisResult
from app.quality.causal.causal_taxonomy import CausalDecision
from app.quality.causal.contracts import FailureCluster, RootCauseHypothesis


class CausalReporter:
    """Generates structured machine-readable and human-readable causal quality reports."""

    @classmethod
    def to_dict(cls, result: CausalAnalysisResult) -> Dict[str, Any]:
        """Builds a structured dictionary strictly categorizing observations, inferences, and conclusions."""
        # 1. OBSERVATIONS (Direct physical & structural measurements)
        observations: List[Dict[str, Any]] = []
        for cluster in result.clusters:
            for s in cluster.signals:
                observations.append({
                    "signal_id": s.signal_id,
                    "failure_code": s.failure_code.value,
                    "failure_domain": s.failure_domain.value,
                    "severity": s.severity.value,
                    "detection_confidence": s.detection_confidence.value,
                    "location": {
                        "artifact_type": s.location.artifact_type,
                        "page_indices": list(s.location.page_indices),
                        "element_id": s.location.element_id,
                        "bounding_box": list(s.location.bounding_box) if s.location.bounding_box else None,
                    },
                    "description": s.description,
                    "source_engine": s.source_engine,
                })

        # 2. INFERENCES (Correlation links, clusters, and competing alternatives)
        inferences: List[Dict[str, Any]] = []
        for cluster in result.clusters:
            competing = result.competing_results.get(cluster.cluster_id)
            readiness = result.readiness_assessments.get(cluster.cluster_id)

            alternatives_data = []
            if competing and competing.alternative_hypotheses:
                for alt in competing.alternative_hypotheses:
                    alternatives_data.append({
                        "cause_code": alt.cause_code,
                        "cause_layer": alt.cause_layer if isinstance(alt.cause_layer, str) else alt.cause_layer.value if hasattr(alt.cause_layer, "value") else str(alt.cause_layer),
                        "confidence_score": alt.confidence_score,
                        "confidence_level": alt.confidence_level if isinstance(alt.confidence_level, str) else alt.confidence_level.value if hasattr(alt.confidence_level, "value") else str(alt.confidence_level),
                        "causal_path": alt.causal_path,
                    })

            inferences.append({
                "cluster_id": cluster.cluster_id,
                "scope": cluster.scope.value,
                "affected_pages": list(cluster.affected_pages),
                "correlation_strength": cluster.correlation_strength,
                "symptoms": [sym.value for sym in cluster.symptoms],
                "competing_alternatives_count": len(alternatives_data),
                "competing_alternatives": alternatives_data,
                "is_ambiguous": competing.is_ambiguous if competing else False,
                "readiness": {
                    "blast_radius": readiness.blast_radius if readiness else 0.0,
                    "reversibility": readiness.reversibility if readiness else 0.0,
                    "determinism": readiness.determinism if readiness else 0.0,
                    "alternative_ambiguity": readiness.alternative_ambiguity if readiness else 0.0,
                    "recommended_authority": readiness.recommended_authority.value if readiness else "UNKNOWN",
                    "blocking_reasons": readiness.blocking_reasons if readiness else [],
                } if readiness else None,
            })

        # 3. CONFIRMED CAUSES (Validated root cause attributions)
        confirmed_causes: List[Dict[str, Any]] = []
        for cluster in result.clusters:
            competing = result.competing_results.get(cluster.cluster_id)
            primary = cluster.primary_root_cause
            if not primary:
                continue

            decision = competing.decision if competing else CausalDecision.UNKNOWN
            confirmed_causes.append({
                "cluster_id": cluster.cluster_id,
                "causal_decision": decision.value if hasattr(decision, "value") else str(decision),
                "root_cause_code": primary.cause_code,
                "origin_layer": primary.cause_layer if isinstance(primary.cause_layer, str) else primary.cause_layer.value if hasattr(primary.cause_layer, "value") else str(primary.cause_layer),
                "confidence_score": primary.confidence_score,
                "confidence_level": primary.confidence_level if isinstance(primary.confidence_level, str) else primary.confidence_level.value if hasattr(primary.confidence_level, "value") else str(primary.confidence_level),
                "causal_path": primary.causal_path,
                "explains_signals": list(primary.explains_signal_ids),
                "confidence_components": primary.confidence_components,
                "supporting_evidence": list(primary.supporting_evidence),
                "recommended_repair_class": cluster.recommended_repair_class.value,
            })

        return {
            "summary": result.summary,
            "total_signals": result.total_signals,
            "correlated_pairs_count": result.correlated_pairs_count,
            "clusters_count": result.clusters_count,
            "unattributed_signals": list(result.unattributed_signals),
            "observations": observations,
            "inferences": inferences,
            "confirmed_causes": confirmed_causes,
        }

    @classmethod
    def generate_json(cls, result: CausalAnalysisResult, indent: int = 2) -> str:
        """Serializes the causal analysis report to formatted JSON."""
        return json.dumps(cls.to_dict(result), indent=indent)

    @classmethod
    def generate_markdown(cls, result: CausalAnalysisResult) -> str:
        """Generates a human-readable forensic report in Markdown with distinct sections."""
        data = cls.to_dict(result)

        lines: List[str] = [
            "# Universal Document Intelligence System V5",
            "## Phase 3B: Failure Correlation & Causal Attribution Report",
            "",
            f"**Summary**: {data['summary']}",
            f"- **Total Signals Observed**: {data['total_signals']}",
            f"- **Correlated Signal Pairs**: {data['correlated_pairs_count']}",
            f"- **Failure Clusters Formed**: {data['clusters_count']}",
            "",
            "---",
            "",
            "### SECTION 1: OBSERVATIONS (Physical & Structural Symptoms)",
            "",
            "| Signal ID | Failure Code | Domain | Severity | Location | Source Engine |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        if not data["observations"]:
            lines.append("| *None* | *Clean Artifact* | - | - | - | - |")
        else:
            for obs in data["observations"]:
                loc_str = f"Pages: {obs['location']['page_indices']}"
                if obs['location']['element_id']:
                    loc_str += f" ({obs['location']['element_id']})"
                lines.append(
                    f"| `{obs['signal_id']}` | `{obs['failure_code']}` | {obs['failure_domain']} | "
                    f"**{obs['severity']}** | {loc_str} | {obs['source_engine']} |"
                )

        lines.extend([
            "",
            "---",
            "",
            "### SECTION 2: INFERENCES (Failure Clusters, Correlations & Competing Hypotheses)",
            "",
        ])

        if not data["inferences"]:
            lines.append("*No failure clusters inferred.*")
        else:
            for inf in data["inferences"]:
                lines.extend([
                    f"#### Cluster `{inf['cluster_id']}`",
                    f"- **Scope**: `{inf['scope']}` | **Pages**: {inf['affected_pages']} | **Correlation Strength**: {inf['correlation_strength']:.2f}",
                    f"- **Symptoms**: {', '.join(f'`{s}`' for s in inf['symptoms'])}",
                ])

                readiness = inf.get("readiness")
                if readiness:
                    lines.extend([
                        f"- **Repair Readiness Assessment**:",
                        f"  - Recommended Authority: **{readiness['recommended_authority']}**",
                        f"  - Blast Radius: {readiness['blast_radius']:.2f} | Reversibility: {readiness['reversibility']:.2f} | Determinism: {readiness['determinism']:.2f}",
                    ])
                    if readiness['blocking_reasons']:
                        lines.append(f"  - Blocking Reasons: {'; '.join(readiness['blocking_reasons'])}")

                if inf["competing_alternatives"]:
                    lines.append("- **Competing Root Cause Hypotheses**:")
                    for alt in inf["competing_alternatives"]:
                        lines.append(
                            f"  - `{alt['cause_code']}` ({alt['cause_layer']}): Score {alt['confidence_score']:.2f} ({alt['confidence_level']})"
                        )
                lines.append("")

        lines.extend([
            "---",
            "",
            "### SECTION 3: CONFIRMED CAUSES (Authoritative Causal Attribution)",
            "",
        ])

        if not data["confirmed_causes"]:
            lines.append("*No confirmed root causes found.*")
        else:
            for cause in data["confirmed_causes"]:
                lines.extend([
                    f"#### Cluster `{cause['cluster_id']}` -> `{cause['root_cause_code']}`",
                    f"- **Decision**: **{cause['causal_decision']}**",
                    f"- **Origin Layer**: `{cause['origin_layer']}`",
                    f"- **Causal Confidence**: **{cause['confidence_score']:.2f}** ({cause['confidence_level']})",
                    f"- **Causal Path**: `{cause['causal_path']}`",
                    f"- **Recommended Repair Class**: `{cause['recommended_repair_class']}`",
                    f"- **Signals Explained**: {', '.join(f'`{s}`' for s in cause['explains_signals'])}",
                    "- **Evidence & Proof**:",
                ])
                for ev in cause["supporting_evidence"]:
                    lines.append(f"  - {ev}")
                lines.append("")

        lines.extend([
            "---",
            "",
            "> [!NOTE]",
            "> **Phase 3B Invariant**: Causal attribution and repair readiness are analytical advisory outputs.",
            "> Automated repairs are strictly deferred to Phase 3C/3D.",
        ])

        return "\n".join(lines)

    @classmethod
    def write_reports(cls, result: CausalAnalysisResult, output_dir: Path | str) -> Tuple[Path, Path]:
        """Writes causal_analysis.json and causal_analysis.md to the target directory."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / "causal_analysis.json"
        md_file = out_path / "causal_analysis.md"

        json_file.write_text(cls.generate_json(result), encoding="utf-8")
        md_file.write_text(cls.generate_markdown(result), encoding="utf-8")

        return json_file, md_file
