"""
Master Generative Critic Engine.

Orchestrates multi-perspective critique panels, context assembly,
finding synthesis, conflict/agreement detection, prioritization, and report assembly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.critic.audience import AudienceCritic
from app.critic.capability_selection import CapabilitySelectionCritic
from app.critic.cognitive_load import CognitiveLoadCritic
from app.critic.context import CritiqueContext, CritiqueContextBuilder
from app.critic.contracts import CritiqueReport, CritiqueTrace
from app.critic.narrative import NarrativeCritic
from app.critic.panel import CriticPanel
from app.critic.pedagogical import PedagogicalCritic
from app.critic.prioritization import CritiquePrioritizer
from app.critic.recommendations import RecommendationGenerator
from app.critic.redundancy import RedundancyCritic
from app.critic.registry import CriticRegistry
from app.critic.scientific import ScientificRigorCritic
from app.critic.semantic import SemanticCritic
from app.critic.structural import StructuralCritic
from app.critic.synthesis import CritiqueSynthesizer
from app.critic.visual import VisualCommunicationCritic
from app.director.contracts import LearningJourney
from app.formats.contracts import ArtifactFormat
from app.quality.contracts import QualityReport


class GenerativeCriticEngine:
    """Master orchestrator for explainable multi-perspective material critique."""

    def __init__(self, registry: CriticRegistry | None = None) -> None:
        if registry is None:
            registry = CriticRegistry()
            # Register all 10 default built-in perspective critics
            registry.register(StructuralCritic())
            registry.register(SemanticCritic())
            registry.register(PedagogicalCritic())
            registry.register(CognitiveLoadCritic())
            registry.register(NarrativeCritic())
            registry.register(VisualCommunicationCritic())
            registry.register(ScientificRigorCritic())
            registry.register(AudienceCritic())
            registry.register(CapabilitySelectionCritic())
            registry.register(RedundancyCritic())

        self.registry = registry
        self.panel = CriticPanel(registry=self.registry)

    def critique(
        self,
        artifact_id: str = "artifact_critique",
        blueprint: SemanticMaterialBlueprint | None = None,
        composition: DocumentComposition | None = None,
        journey: LearningJourney | None = None,
        quality_report: QualityReport | None = None,
        resolution_trace: dict[str, Any] | None = None,
        format_contract: ArtifactFormat | None = None,
        pdf_path: str | Path | None = None,
        target_format: str = "a4_portrait",
        audience_level: str = "undergraduate",
        document_genre: str = "educational",
        selected_critics: list[str] | None = None,
    ) -> CritiqueReport:
        # 1. Build Context
        context = (
            CritiqueContextBuilder(artifact_id)
            .with_blueprint(blueprint)
            .with_composition(composition)
            .with_journey(journey)
            .with_quality_report(quality_report)
            .with_resolution_trace(resolution_trace)
            .with_format(target_format, contract=format_contract)
            .with_pdf_path(pdf_path)
            .with_audience(audience_level)
            .with_genre(document_genre)
            .build()
        )

        # 2. Execute Critic Panel
        raw_findings, initial_trace = self.panel.execute_critique(context, selected_critics=selected_critics)

        # 3. Synthesize Findings (Deduplicate, Agreements, Conflicts)
        merged_findings, agreements, conflicts, synthesis_steps = CritiqueSynthesizer.synthesize(raw_findings)

        # 4. Prioritize Findings
        priority_queue = CritiquePrioritizer.prioritize(merged_findings, agreements)

        # 5. Generate Non-Destructive Recommendations
        recommendations = RecommendationGenerator.generate_recommendations(merged_findings, agreements)

        # 6. Construct Overall Assessment Summary
        if not merged_findings:
            assessment = f"Artifact '{artifact_id}' satisfies all multi-perspective qualitative criteria with 0 identified weaknesses."
        else:
            crit_count = sum(1 for f in merged_findings if f.severity.value == "critical")
            high_count = sum(1 for f in merged_findings if f.severity.value == "high")
            med_count = sum(1 for f in merged_findings if f.severity.value == "medium")
            assessment = (
                f"Critique identified {len(merged_findings)} qualitative findings "
                f"({crit_count} critical, {high_count} high, {med_count} medium). "
                f"{len(agreements)} consensus agreements and {len(conflicts)} design trade-off conflicts detected."
            )

        # 7. Build Complete Trace
        trace = CritiqueTrace(
            critics_executed=initial_trace.critics_executed,
            critics_skipped=initial_trace.critics_skipped,
            critics_failed=initial_trace.critics_failed,
            evidence_sources=context.available_evidence_sources(),
            reasoning_steps=initial_trace.reasoning_steps,
            synthesis_steps=synthesis_steps,
            conflicts_detected=len(conflicts),
            agreements_detected=len(agreements),
        )

        return CritiqueReport(
            artifact_id=artifact_id,
            overall_assessment=assessment,
            findings=merged_findings,
            recommendations=recommendations,
            conflicts=conflicts,
            agreements=agreements,
            priority_queue=priority_queue,
            trace=trace,
            metadata={"target_format": target_format, "audience_level": audience_level, "genre": document_genre},
        )
