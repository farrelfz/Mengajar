"""
Director Diagnostics telemetry recorder.
"""

from __future__ import annotations

from app.director.contracts import DirectorDiagnostics, MaterialStrategyType


class DiagnosticsCollector:
    """Collects and summarizes diagnostic telemetry during direction planning."""

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.alternative_strategies: list[tuple[str, float]] = []

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def record_alternatives(self, ranked_strategies: list[tuple[MaterialStrategyType, float]]) -> None:
        self.alternative_strategies = [(s.value, score) for s, score in ranked_strategies]

    def build_diagnostics(
        self,
        strategy_selected: MaterialStrategyType,
        strategy_score: float,
        domain_policy: str,
        stage_count: int,
        density_budget: str,
    ) -> DirectorDiagnostics:
        return DirectorDiagnostics(
            strategy_selected=strategy_selected,
            strategy_score=strategy_score,
            domain_policy=domain_policy,
            stage_count=stage_count,
            warnings=list(self.warnings),
            density_budget=density_budget,
            alternative_strategies=list(self.alternative_strategies),
        )
