"""
Presentation Rhythm Analyzer.

Evaluates slide-to-slide rhythm, pacing, and cognitive cadence:
- High cognitive load streaks
- High density clusters
- Monotonous visual type repetition
- Dynamism score across narrative acts
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.presentation.slide_architect import PlannedSlide
from app.presentation.visual_qa import VisualSlideReport


class RhythmIssue(BaseModel):
    issue_type: str  # HIGH_LOAD_STREAK, HIGH_DENSITY_STREAK, MONOTONOUS_PACING
    slides: list[int]
    severity: str  # WARNING, INFO
    details: str


class RhythmAnalysisResult(BaseModel):
    rhythm_score: float
    status: str  # "PASS", "WARNING"
    load_sequence: list[str] = Field(default_factory=list)
    density_sequence: list[float] = Field(default_factory=list)
    issues: list[RhythmIssue] = Field(default_factory=list)


class PresentationRhythmAnalyzer:
    """Analyzes dynamic slide-to-slide progression and pacing."""

    def analyze(
        self,
        slides: list[PlannedSlide],
        visual_reports: list[VisualSlideReport] | None = None,
    ) -> RhythmAnalysisResult:
        """Evaluates pacing rhythm across planned slides and optional visual reports."""
        if not slides:
            return RhythmAnalysisResult(rhythm_score=1.0, status="PASS")

        load_seq = [(s.cognitive_load.level if hasattr(s.cognitive_load, "level") else "medium").lower() for s in slides]
        density_map = {vr.slide_number: vr.density for vr in (visual_reports or [])}
        density_seq = [density_map.get(s.slide_number, 0.45) for s in slides]

        issues: list[RhythmIssue] = []
        penalties = 0.0

        # 1. High Cognitive Load Streaks (>= 3 consecutive high load slides)
        high_load_streak: list[int] = []
        for s in slides:
            lvl = (s.cognitive_load.level if hasattr(s.cognitive_load, "level") else "medium").lower()
            if lvl == "high":
                high_load_streak.append(s.slide_number)
            else:
                if len(high_load_streak) >= 3:
                    penalties += 0.15 * (len(high_load_streak) - 2)
                    issues.append(
                        RhythmIssue(
                            issue_type="HIGH_LOAD_STREAK",
                            slides=list(high_load_streak),
                            severity="WARNING",
                            details=f"High cognitive load streak on slides {high_load_streak} causes cognitive fatigue",
                        )
                    )
                high_load_streak = []

        if len(high_load_streak) >= 3:
            penalties += 0.15 * (len(high_load_streak) - 2)
            issues.append(
                RhythmIssue(
                    issue_type="HIGH_LOAD_STREAK",
                    slides=list(high_load_streak),
                    severity="WARNING",
                    details=f"High cognitive load streak on slides {high_load_streak} causes cognitive fatigue",
                )
            )

        # 2. High Density Clusters (>= 3 consecutive slides with density > 0.65)
        high_density_streak: list[int] = []
        for i, dens in enumerate(density_seq):
            s_num = slides[i].slide_number
            if dens > 0.65:
                high_density_streak.append(s_num)
            else:
                if len(high_density_streak) >= 3:
                    penalties += 0.10 * (len(high_density_streak) - 2)
                    issues.append(
                        RhythmIssue(
                            issue_type="HIGH_DENSITY_STREAK",
                            slides=list(high_density_streak),
                            severity="WARNING",
                            details=f"High density streak on slides {high_density_streak} exceeds 65% area occupancy",
                        )
                    )
                high_density_streak = []

        if len(high_density_streak) >= 3:
            penalties += 0.10 * (len(high_density_streak) - 2)
            issues.append(
                RhythmIssue(
                    issue_type="HIGH_DENSITY_STREAK",
                    slides=list(high_density_streak),
                    severity="WARNING",
                    details=f"High density streak on slides {high_density_streak} exceeds 65% area occupancy",
                )
            )

        # 3. Monotonous Layout Pacing (same layout >= 4 slides)
        monotonous_layout_streak: list[int] = []
        cur_layout = slides[0].layout
        for s in slides:
            if s.layout == cur_layout:
                monotonous_layout_streak.append(s.slide_number)
            else:
                if len(monotonous_layout_streak) >= 4:
                    penalties += 0.10
                    issues.append(
                        RhythmIssue(
                            issue_type="MONOTONOUS_PACING",
                            slides=list(monotonous_layout_streak),
                            severity="WARNING",
                            details=f"Monotonous layout '{cur_layout}' repeated across slides {monotonous_layout_streak}",
                        )
                    )
                cur_layout = s.layout
                monotonous_layout_streak = [s.slide_number]

        if len(monotonous_layout_streak) >= 4:
            penalties += 0.10
            issues.append(
                RhythmIssue(
                    issue_type="MONOTONOUS_PACING",
                    slides=list(monotonous_layout_streak),
                    severity="WARNING",
                    details=f"Monotonous layout '{cur_layout}' repeated across slides {monotonous_layout_streak}",
                )
            )

        final_score = max(0.0, min(1.0, 1.0 - penalties))
        status = "PASS" if not issues else "WARNING"

        return RhythmAnalysisResult(
            rhythm_score=round(final_score, 3),
            status=status,
            load_sequence=load_seq,
            density_sequence=[round(d, 2) for d in density_seq],
            issues=issues,
        )
