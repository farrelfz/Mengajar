"""
Universal Document Intelligence System V5 — Quality Calibration Profiles & Metrics.

Phase 2C: Empirical calibration curves and detection performance tracking.
Calibrates metrics against excellent, acceptable, warning, and failure intervals
and evaluates quality detectors via precision, recall, FPR, and FNR.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class QualityCalibrationProfile(BaseModel):
    """Calibrated empirical operating ranges for a specific quality metric."""
    model_config = ConfigDict(frozen=True)

    metric: str
    artifact_type: str
    excellent_range: Tuple[float, float]
    acceptable_range: Tuple[float, float]
    warning_range: Tuple[float, float]
    failure_range: Tuple[float, float]
    rationale: str

    def evaluate_metric(self, value: float) -> Tuple[str, float]:
        """Evaluates a raw value against the profile ranges.
        
        Returns:
            (status, score_factor) where status is 'EXCELLENT', 'ACCEPTABLE', 'WARNING', 'FAILURE'.
        """
        # Lower bound of failure or upper bound depending on polarity
        # Assuming higher is better unless failure_range[1] < excellent_range[0]
        is_higher_better = self.excellent_range[0] >= self.failure_range[1]
        
        if is_higher_better:
            if value >= self.excellent_range[0]:
                return "EXCELLENT", 1.0
            elif value >= self.acceptable_range[0]:
                return "ACCEPTABLE", 0.85
            elif value >= self.warning_range[0]:
                return "WARNING", 0.65
            else:
                return "FAILURE", 0.30
        else:
            # Lower is better (e.g. duplicate rate, collision count)
            if value <= self.excellent_range[1]:
                return "EXCELLENT", 1.0
            elif value <= self.acceptable_range[1]:
                return "ACCEPTABLE", 0.85
            elif value <= self.warning_range[1]:
                return "WARNING", 0.65
            else:
                return "FAILURE", 0.30


class QualityDetectionMetrics(BaseModel):
    """Classifier performance metrics evaluating quality detection accuracy."""
    model_config = ConfigDict(frozen=True)

    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0

    @property
    def total_evaluations(self) -> int:
        return self.true_positives + self.false_positives + self.true_negatives + self.false_negatives

    @property
    def precision(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        denom = self.true_positives + self.false_positives
        return round(self.true_positives / denom, 3) if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        denom = self.true_positives + self.false_negatives
        return round(self.true_positives / denom, 3) if denom > 0 else 0.0

    @property
    def false_positive_rate(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        denom = self.false_positives + self.true_negatives
        return round(self.false_positives / denom, 3) if denom > 0 else 0.0

    @property
    def false_negative_rate(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        denom = self.false_negatives + self.true_positives
        return round(self.false_negatives / denom, 3) if denom > 0 else 0.0

    @property
    def detection_confidence(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        p = self.precision
        r = self.recall
        return round(2 * (p * r) / max(p + r, 1e-6), 3) if (p + r) > 0 else 0.0


# Standard calibrated profiles across artifact types
CALIBRATION_PROFILES: Dict[str, List[QualityCalibrationProfile]] = {
    "PRESENTATION": [
        QualityCalibrationProfile(
            metric="duplicate_rate",
            artifact_type="PRESENTATION",
            excellent_range=(0.0, 0.0),
            acceptable_range=(0.0, 0.05),
            warning_range=(0.05, 0.15),
            failure_range=(0.15, 1.0),
            rationale="Slides must communicate progressive ideas. Duplication >15% severely degrades engagement.",
        ),
        QualityCalibrationProfile(
            metric="visual_hierarchy_ratio",
            artifact_type="PRESENTATION",
            excellent_range=(1.6, 3.0),
            acceptable_range=(1.3, 1.6),
            warning_range=(1.15, 1.3),
            failure_range=(0.0, 1.15),
            rationale="Major Third/Golden Ratio typography provides distinct visual scanability.",
        ),
        QualityCalibrationProfile(
            metric="min_body_font_size",
            artifact_type="PRESENTATION",
            excellent_range=(12.0, 24.0),
            acceptable_range=(10.0, 12.0),
            warning_range=(8.5, 10.0),
            failure_range=(0.0, 8.5),
            rationale="Presentation slides viewed from distance require minimum readable font size.",
        ),
    ],
    "HANDOUT": [
        QualityCalibrationProfile(
            metric="page_character_density",
            artifact_type="HANDOUT",
            excellent_range=(1000.0, 2500.0),
            acceptable_range=(800.0, 3200.0),
            warning_range=(500.0, 4000.0),
            failure_range=(4000.0, 10000.0),
            rationale="Continuous reading handouts require balanced text density to prevent fatigue.",
        ),
    ],
    "WORKSHEET": [
        QualityCalibrationProfile(
            metric="workspace_adequacy_height",
            artifact_type="WORKSHEET",
            excellent_range=(60.0, 300.0),
            acceptable_range=(40.0, 60.0),
            warning_range=(25.0, 40.0),
            failure_range=(0.0, 25.0),
            rationale="Student active writing requires at least 40pt height for legible response.",
        ),
        QualityCalibrationProfile(
            metric="quiz_collapse_ratio",
            artifact_type="WORKSHEET",
            excellent_range=(0.0, 0.15),
            acceptable_range=(0.15, 0.35),
            warning_range=(0.35, 0.60),
            failure_range=(0.60, 1.0),
            rationale="Inquiry worksheets must emphasize active investigation over passive MCQ trivia.",
        ),
    ],
    "SCIENTIFIC_DOCUMENT": [
        QualityCalibrationProfile(
            metric="evidence_grounding_ratio",
            artifact_type="SCIENTIFIC_DOCUMENT",
            excellent_range=(0.85, 1.0),
            acceptable_range=(0.70, 0.85),
            warning_range=(0.50, 0.70),
            failure_range=(0.0, 0.50),
            rationale="Scientific claims must be supported by empirical evidence citations.",
        ),
    ],
}
