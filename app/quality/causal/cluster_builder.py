"""
Universal Document Intelligence System V5 — Failure Cluster Builder.

Phase 3B: Constructs explainable, deterministic FailureCluster instances from
the CorrelationGraph connected components.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.contracts import FailureCluster, QualityLocation, QualitySignal
from app.quality.causal.correlation_engine import CorrelationResult
from app.quality.causal.scope import ScopePolicy
from app.quality.causal.taxonomy import CanonicalFailureCode, FailureScope


class FailureClusterBuilder:
    """Builds deterministic, explainable FailureCluster objects from correlation results."""

    def __init__(
        self,
        config: Optional[CausalIntelligenceConfig] = None,
        scope_policy: Optional[ScopePolicy] = None,
    ):
        self.config = config or DEFAULT_CAUSAL_CONFIG
        self.scope_policy = scope_policy or ScopePolicy()

    def build_clusters(
        self,
        correlation_result: CorrelationResult,
        total_pages: int = 1,
        artifact_type: str = "UNKNOWN",
    ) -> List[FailureCluster]:
        """Transforms correlated signal groups into rich, immutable FailureCluster instances."""
        clusters: List[FailureCluster] = []
        graph = correlation_result.graph
        policy = ScopePolicy.for_artifact(artifact_type) if artifact_type != "UNKNOWN" else self.scope_policy

        all_groups = list(correlation_result.correlated_groups)
        for iso in correlation_result.isolated_signals:
            all_groups.append([iso])

        for group in all_groups:
            if not group:
                continue

            signals: List[QualitySignal] = [
                graph.nodes[sid] for sid in sorted(group) if sid in graph.nodes
            ]
            if not signals:
                continue

            # Deterministic cluster ID from sorted member signal IDs
            group_hash = hashlib.sha256("::".join(sorted(group)).encode("utf-8")).hexdigest()[:8]
            cluster_id = f"clust_{group_hash}"

            # Aggregate affected pages
            pages_set: Set[int] = set()
            locations: List[QualityLocation] = []
            for s in signals:
                locations.append(s.location)
                for p in s.location.page_indices:
                    pages_set.add(p)
            affected_pages = tuple(sorted(pages_set))

            # Aggregate symptoms and dominant failure patterns
            code_counts = Counter(s.failure_code for s in signals)
            dominant_patterns = tuple(c.value for c, _ in code_counts.most_common())
            symptoms = tuple(sorted(code_counts.keys(), key=lambda c: c.value))

            # Calculate average correlation strength within the cluster
            relevant_edges = [
                e for e in correlation_result.correlation_edges
                if e.signal_a_id in group and e.signal_b_id in group
            ]
            avg_strength = (
                sum(e.score for e in relevant_edges) / len(relevant_edges)
                if relevant_edges else 0.0
            )

            # Determine cluster scope
            is_doc_level = any(
                ScopePolicy.is_global_invariant_code(s.failure_code) for s in signals
            )
            dominant_code = symptoms[0] if symptoms else None
            scope = policy.determine_scope(
                affected_pages=affected_pages,
                total_pages=total_pages,
                is_document_level=is_doc_level,
                failure_code=dominant_code,
                artifact_type=artifact_type,
            )

            # Extract shared context
            shared_ctx: Dict[str, Any] = {
                "artifact_type": artifact_type,
                "signal_count": len(signals),
                "affected_pages": list(affected_pages),
                "dominant_code": dominant_code.value if dominant_code else None,
            }

            # Collect edge evidence
            cluster_evidence_list: List[str] = []
            for e in relevant_edges:
                for ev in e.evidence:
                    if ev not in cluster_evidence_list:
                        cluster_evidence_list.append(ev)

            summary = (
                f"Cluster {cluster_id}: {len(signals)} correlated defects on pages {list(affected_pages)} "
                f"with dominant symptoms: {', '.join(dominant_patterns[:3])}"
            )

            cluster = FailureCluster(
                cluster_id=cluster_id,
                affected_pages=affected_pages,
                symptoms=symptoms,
                signals=tuple(signals),
                scope=scope,
                dominant_failure_patterns=dominant_patterns,
                affected_locations=tuple(locations),
                shared_context=shared_ctx,
                correlation_strength=round(avg_strength, 4),
                cluster_summary=summary,
                cluster_evidence=tuple(cluster_evidence_list),
            )
            clusters.append(cluster)

        # Sort clusters deterministically by cluster_id
        clusters.sort(key=lambda c: c.cluster_id)
        return clusters
