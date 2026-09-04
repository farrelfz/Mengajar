"""
Critique Context & Context Builder supporting progressive evidence assembly and graceful degradation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.director.contracts import LearningJourney
from app.formats.contracts import ArtifactFormat
from app.quality.contracts import QualityReport


class CritiqueContext(BaseModel):
    """Encapsulates all observable evidence available to the Generative Critic."""

    artifact_id: str = Field(description="Unique artifact/job identifier")
    blueprint: SemanticMaterialBlueprint | None = Field(default=None, description="Level A/B/C Semantic Blueprint")
    composition: DocumentComposition | None = Field(default=None, description="Abstract layout & page composition")
    journey: LearningJourney | None = Field(default=None, description="Director pedagogical learning journey")
    quality_report: QualityReport | None = Field(default=None, description="Batch 15 Quality Evaluation Report")
    resolution_trace: dict[str, Any] | None = Field(default=None, description="Capability resolution trace")
    format_contract: ArtifactFormat | None = Field(default=None, description="Target physical format contract")
    pdf_path: str | Path | None = Field(default=None, description="Path to rendered PDF file")
    target_format: str = Field(default="a4_portrait", description="Format identifier string")
    audience_level: str = Field(default="undergraduate", description="Target learner grade/level")
    document_genre: str = Field(default="educational", description="Document genre/purpose")

    def available_evidence_sources(self) -> list[str]:
        sources = []
        if self.blueprint is not None:
            sources.append("blueprint")
        if self.composition is not None:
            sources.append("composition")
        if self.journey is not None:
            sources.append("director_journey")
        if self.quality_report is not None:
            sources.append("quality_report")
        if self.resolution_trace is not None:
            sources.append("resolution_trace")
        if self.pdf_path is not None:
            sources.append("physical_pdf")
        return sources


class CritiqueContextBuilder:
    """Builder supporting progressive context construction."""

    def __init__(self, artifact_id: str):
        self._artifact_id = artifact_id
        self._blueprint: SemanticMaterialBlueprint | None = None
        self._composition: DocumentComposition | None = None
        self._journey: LearningJourney | None = None
        self._quality_report: QualityReport | None = None
        self._resolution_trace: dict[str, Any] | None = None
        self._format_contract: ArtifactFormat | None = None
        self._pdf_path: str | Path | None = None
        self._target_format: str = "a4_portrait"
        self._audience_level: str = "undergraduate"
        self._document_genre: str = "educational"

    def with_blueprint(self, blueprint: SemanticMaterialBlueprint | None) -> CritiqueContextBuilder:
        self._blueprint = blueprint
        if blueprint and blueprint.content and blueprint.content.metadata:
            if hasattr(blueprint.content.metadata, "audience") and blueprint.content.metadata.audience:
                self._audience_level = str(blueprint.content.metadata.audience.value if hasattr(blueprint.content.metadata.audience, "value") else blueprint.content.metadata.audience)
        return self

    def with_composition(self, composition: DocumentComposition | None) -> CritiqueContextBuilder:
        self._composition = composition
        return self

    def with_journey(self, journey: LearningJourney | None) -> CritiqueContextBuilder:
        self._journey = journey
        return self

    def with_quality_report(self, quality_report: QualityReport | None) -> CritiqueContextBuilder:
        self._quality_report = quality_report
        return self

    def with_resolution_trace(self, trace: dict[str, Any] | None) -> CritiqueContextBuilder:
        self._resolution_trace = trace
        return self

    def with_format(self, target_format: str, contract: ArtifactFormat | None = None) -> CritiqueContextBuilder:
        self._target_format = target_format
        self._format_contract = contract
        return self

    def with_pdf_path(self, pdf_path: str | Path | None) -> CritiqueContextBuilder:
        self._pdf_path = pdf_path
        return self

    def with_audience(self, audience_level: str) -> CritiqueContextBuilder:
        self._audience_level = audience_level
        return self

    def with_genre(self, genre: str) -> CritiqueContextBuilder:
        self._document_genre = genre
        return self

    def build(self) -> CritiqueContext:
        return CritiqueContext(
            artifact_id=self._artifact_id,
            blueprint=self._blueprint,
            composition=self._composition,
            journey=self._journey,
            quality_report=self._quality_report,
            resolution_trace=self._resolution_trace,
            format_contract=self._format_contract,
            pdf_path=self._pdf_path,
            target_format=self._target_format,
            audience_level=self._audience_level,
            document_genre=self._document_genre,
        )
