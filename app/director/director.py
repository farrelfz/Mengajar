"""
Intelligent Material Director Engine.

Plans pedagogical and narrative learning journeys above the capability layer,
orchestrating domain policies, cognitive progression, stage transition grammar,
density budgeting, and capability choreography.
"""

from __future__ import annotations

from typing import Any

from app.capabilities.taxonomy import DensityProfile
from app.director.choreography import PedagogicalChoreographer
from app.director.cognition import CognitiveProgressionPolicy
from app.director.contracts import (
    AudienceProfile,
    CapabilityRequirement,
    DensityBudget,
    DirectorDiagnostics,
    DirectorTrace,
    InstructionalIntent,
    KnowledgeState,
    LearningGoal,
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialDirection,
    MaterialStrategyType,
)
from app.director.diagnostics import DiagnosticsCollector
from app.director.journey import LearningJourneyBuilder
from app.director.misconceptions import MisconceptionDetector
from app.director.policies import DomainPolicyRegistry, get_default_policy_registry
from app.director.strategies import STRATEGY_REGISTRY, get_strategy_definition
from app.director.trace import DirectorTraceBuilder
from app.director.validators import StageTransitionPolicy


class IntelligentMaterialDirector:
    """Master pedagogical and narrative director orchestrating learning journeys."""

    def __init__(self, policy_registry: DomainPolicyRegistry | None = None) -> None:
        self.policies = policy_registry or get_default_policy_registry()
        self.journey_builder = LearningJourneyBuilder()
        self.choreographer = PedagogicalChoreographer()
        self.trace_builder = DirectorTraceBuilder()

    def direct(
        self,
        goal: LearningGoal,
        audience: AudienceProfile | None = None,
        intent: InstructionalIntent = InstructionalIntent.TEACH,
        format_id: str = "a4_portrait",
        preferred_strategy: MaterialStrategyType | None = None,
    ) -> MaterialDirection:
        """Execute full material direction pipeline."""
        aud = audience or AudienceProfile()
        diag_collector = DiagnosticsCollector()

        # 1. Fetch domain policy
        domain_policy = self.policies.get(goal.domain)

        # 2. Select strategy
        strategy_reasons: list[str] = []
        if preferred_strategy is not None:
            selected_strategy = preferred_strategy
            fit_score = domain_policy.evaluate_strategy_fit(selected_strategy, goal, aud, intent, format_id)
            strategy_reasons.append(f"Manual override: Explicitly selected '{selected_strategy.value}'")
            if fit_score < 0.5:
                diag_collector.add_warning(
                    f"Manual strategy override '{selected_strategy.value}' has low compatibility ({fit_score:.2f}) with domain '{goal.domain}' and intent '{intent.value}'."
                )
        else:
            # Score all registered strategies
            scored_strategies: list[tuple[MaterialStrategyType, float]] = []
            for strat_type in STRATEGY_REGISTRY.keys():
                score = domain_policy.evaluate_strategy_fit(strat_type, goal, aud, intent, format_id)
                scored_strategies.append((strat_type, score))

            scored_strategies.sort(key=lambda x: x[1], reverse=True)
            diag_collector.record_alternatives(scored_strategies[1:4])
            selected_strategy, fit_score = scored_strategies[0]
            strategy_reasons.append(f"Domain policy '{domain_policy.domain_name}' scored highest ({fit_score:.2f}) for '{selected_strategy.value}'.")
            strategy_reasons.append(f"Audience knowledge state is '{aud.prior_knowledge.value}'.")
            strategy_reasons.append(f"Instructional intent is '{intent.value}'.")

        # 3. Density Budgeting (semantic, not pixel-based)
        if format_id == "presentation_16_9":
            budget = DensityBudget(
                level="low",
                max_concepts_per_stage=1,
                max_derivation_steps=2,
                preferred_density_profile=DensityProfile.MINIMAL,
            )
            density_reason = "16:9 Presentation format requires high visual contrast and low information density per slide."
        else:
            budget = DensityBudget(
                level="medium",
                max_concepts_per_stage=3,
                max_derivation_steps=5,
                preferred_density_profile=DensityProfile.FOCUSED,
            )
            density_reason = f"Document format '{format_id}' supports focused reading density."

        # 4. Build Learning Journey
        journey = self.journey_builder.build_journey(
            strategy=selected_strategy,
            goal=goal,
            audience=aud,
            density_budget=budget,
            format_id=format_id,
        )

        # 5. Misconception Opportunity Integration
        misc_opp = MisconceptionDetector.detect_for_topic(goal.concept)
        if misc_opp and selected_strategy == MaterialStrategyType.MISCONCEPTION_CORRECTION:
            for s in journey.stages:
                if s.stage_type == LearningStageType.MISCONCEPTION:
                    s.content_payload["misconception_statement"] = misc_opp.misconception_statement
                    s.purpose = f"Elicit common student fallacy: {misc_opp.misconception_statement}"

        # 6. Validate Stage Transition Grammar
        stage_types = [s.stage_type for s in journey.stages]
        is_journey_valid, journey_warnings = StageTransitionPolicy.validate_journey(stage_types, selected_strategy)
        for w in journey_warnings:
            diag_collector.add_warning(w)

        # 7. Validate Cognitive Progression
        is_cog_valid, cog_warnings = CognitiveProgressionPolicy.validate_progression(journey.stages, aud)
        for w in cog_warnings:
            diag_collector.add_warning(w)

        # 8. Choreograph to CapabilityRequirements
        choreography = self.choreographer.choreograph(journey, budget)

        # 9. Build Diagnostics and Explainable Trace
        diagnostics = diag_collector.build_diagnostics(
            strategy_selected=selected_strategy,
            strategy_score=fit_score,
            domain_policy=domain_policy.domain_name,
            stage_count=len(journey.stages),
            density_budget=budget.level,
        )

        trace = self.trace_builder.build_trace(
            strategy=selected_strategy,
            strategy_reasons=strategy_reasons,
            journey=journey,
            domain_policy=domain_policy.domain_name,
            density_reason=density_reason,
        )

        return MaterialDirection(
            goal=goal,
            audience=aud,
            intent=intent,
            strategy=selected_strategy,
            journey=journey,
            choreography=choreography,
            diagnostics=diagnostics,
            trace=trace,
        )
