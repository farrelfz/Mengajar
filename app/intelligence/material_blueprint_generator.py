"""
KIR AI Document Intelligence — Material Blueprint Generator.

Automatically transforms an AnalysisResult (from ContentIntelligenceAgent)
or raw text into a valid 3-level SemanticMaterialBlueprint (Levels A, B, C)
without requiring manual blueprint assembly.
"""

from __future__ import annotations

import logging
from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    FactStatement,
    KnowledgeDomain,
    LearningObjective,
    MisconceptionItem,
)
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    SemanticIntentSpec,
    TargetArtifactType,
)
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.intelligence.schemas import AnalysisResult, ContentType

log = logging.getLogger(__name__)


class MaterialBlueprintGenerator:
    """Automates transformation of classified analysis into a SemanticMaterialBlueprint."""

    def generate_from_analysis(
        self,
        analysis: AnalysisResult,
        title_override: str | None = None,
        domain: KnowledgeDomain = KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience: AudienceLevel = AudienceLevel.HIGH_SCHOOL,
        target_artifact: TargetArtifactType = TargetArtifactType.TEACHING_PRESENTATION,
    ) -> SemanticMaterialBlueprint:
        """Generate a complete SemanticMaterialBlueprint from an AnalysisResult."""
        units = analysis.content_units

        # 1. Level A — Content Blueprint
        title = title_override or (units[0].normalized_text if units else "Research Education Guide")
        if len(title) > 60:
            title = title[:57] + "..."

        meta = ContentMetadata(
            title=title,
            domain=domain,
            audience=audience,
            purpose="teaching",
        )

        concepts: list[ConceptDefinition] = []
        facts: list[FactStatement] = []
        objectives: list[LearningObjective] = []

        for u in units:
            if u.title:
                objectives.append(LearningObjective(objective=f"Understand {u.title}"))
            elif u.content_type in [ContentType.DEFINITION, ContentType.CONCEPT] or "defin" in u.normalized_text.lower():
                concepts.append(ConceptDefinition(
                    name=u.normalized_text[:30],
                    formal_definition=u.normalized_text,
                ))
            elif u.content_type in [ContentType.EXPLANATION, ContentType.BACKGROUND, ContentType.CONTEXT]:
                facts.append(FactStatement(statement=u.normalized_text))
            else:
                facts.append(FactStatement(statement=u.normalized_text))

        content_bp = ContentBlueprint(
            metadata=meta,
            objectives=objectives or [LearningObjective(objective="Understand scientific inquiry")],
            concepts=concepts or [ConceptDefinition(name=title, formal_definition=title)],
            facts=facts,
        )

        # 2. Level B — Pedagogical Blueprint
        pedagogical_steps: list[PedagogicalStep] = []
        
        if domain == KnowledgeDomain.EXPERIMENT_KIR:
            # Standar Pakem Eksperimen KIR:
            # 1. Pendahuluan, Fenomena & Tujuan Eksperimen
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.HOOK,
                purpose="Pendahuluan: Latar belakang fenomena sains, konsep dasar & tujuan eksperimen",
            ))

            # 2. Hipotesis & Variabel Penelitian (Bebas, Terikat, Kontrol)
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.MATHEMATICAL_MODEL,
                purpose="Formulasi hipotesis ilmiah & matriks variabel penelitian (bebas, terikat, kontrol)",
                visual_intent="hypothesis_testing",
            ))

            # 3. Alat, Bahan & Protokol Keselamatan Kerja Laboratorium
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.VISUALIZATION,
                purpose="Spesifikasi alat, takaran bahan/reagen & protokol keselamatan kerja (K3/Safety)",
                visual_intent="research_problem_funnel",
            ))

            # 4. Tahapan Prosedur Kerja Eksperimen (Step-by-Step)
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.WORKED_EXAMPLE,
                purpose="Prosedur kerja sistematis berurutan dan teknik replikasi pengulangan (triplo)",
            ))

            # 5. Tabel Matriks Data Pengamatan & Lembar Observasi
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.PRACTICE,
                purpose="Matriks tabel hasil pengamatan, pencatatan data kuantitatif/kualitatif & grafik",
            ))

            # 6. Analisis Hasil, Pembahasan Ilmiah & Kesimpulan
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.SUMMARY,
                purpose="Analisis data, pembahasan perbandingan teori vs fakta eksperimen & kesimpulan",
            ))

            pedagogy_bp = PedagogicalBlueprint(
                primary_pattern=PedagogicalPattern.SCIENTIFIC_REASONING,
                narrative_rationale="Pendahuluan & Tujuan -> Hipotesis & Variabel -> Alat/Bahan & K3 -> Prosedur Kerja -> Data Pengamatan -> Pembahasan & Kesimpulan",
                sequence=pedagogical_steps,
            )
        else:
            # Opening Hook
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.HOOK,
                purpose="Engage learners with the central question or real-world phenomenon",
            ))

            # Check if research problem or hypothesis is present
            has_research_problem = any(
                "problem" in u.normalized_text.lower() or "phenomenon" in u.normalized_text.lower() or "rumusan" in u.normalized_text.lower()
                for u in units
            )
            has_hypothesis = any(
                "hypothes" in u.normalized_text.lower() or "variable" in u.normalized_text.lower()
                for u in units
            )

            if has_research_problem:
                pedagogical_steps.append(PedagogicalStep(
                    semantic_type=SemanticStepType.VISUALIZATION,
                    purpose="Formulate the research question using problem funnel",
                    visual_intent="research_problem_funnel",
                ))

            if has_hypothesis:
                pedagogical_steps.append(PedagogicalStep(
                    semantic_type=SemanticStepType.MATHEMATICAL_MODEL,
                    purpose="Operationalize hypothesis and variable matrix",
                    visual_intent="hypothesis_testing",
                ))

            # Add Concept & Summary steps
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.CONCEPT,
                purpose="Explain the core underlying scientific concepts",
            ))
            pedagogical_steps.append(PedagogicalStep(
                semantic_type=SemanticStepType.SUMMARY,
                purpose="Summarize key takeaways and practical guidance",
            ))

            pedagogy_bp = PedagogicalBlueprint(
                primary_pattern=PedagogicalPattern.SCIENTIFIC_REASONING if has_research_problem else PedagogicalPattern.CONCRETE_TO_ABSTRACT,
                narrative_rationale="Phenomenon -> Problem Structuring -> Concept Understanding -> Synthesis",
                sequence=pedagogical_steps,
            )

        # 3. Level C — Production Blueprint
        prod_requirements: list[ProductionRequirement] = []
        for step in pedagogical_steps:
            if step.semantic_type == SemanticStepType.HOOK:
                req = ProductionRequirement(
                    step_id=step.id,
                    semantic_type="hook",
                    required_capability_id="presentation.hero_statement",
                )
            elif step.visual_intent == "research_problem_funnel":
                req = ProductionRequirement(
                    step_id=step.id,
                    semantic_type="visualization",
                    semantic_intent=SemanticIntentSpec(
                        semantic_intent="research_problem_funnel",
                        domain="research_education",
                        parameters={"topic": title},
                    ),
                )
            elif step.visual_intent == "hypothesis_testing":
                req = ProductionRequirement(
                    step_id=step.id,
                    semantic_type="visualization",
                    semantic_intent=SemanticIntentSpec(
                        semantic_intent="hypothesis_testing",
                        domain="research_education",
                    ),
                )
            elif step.semantic_type == SemanticStepType.CONCEPT:
                req = ProductionRequirement(
                    step_id=step.id,
                    semantic_type="concept",
                    required_capability_id="presentation.concept_introduction",
                )
            else:
                req = ProductionRequirement(
                    step_id=step.id,
                    semantic_type="summary",
                    required_capability_id="presentation.concept_introduction",
                )
            prod_requirements.append(req)

        production_bp = ProductionBlueprint(
            target_artifact=target_artifact,
            requirements=prod_requirements,
        )

        material = SemanticMaterialBlueprint(
            content=content_bp,
            pedagogy=pedagogy_bp,
            production=production_bp,
        )
        return material
