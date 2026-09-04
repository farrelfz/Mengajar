"""
Pipeline Profiles: Declarative factory for configuring workflow definitions according to quality/speed tiers.
"""

from __future__ import annotations

from enum import Enum
from app.orchestration.contracts import WorkflowStageType
from app.orchestration.workflow import WorkflowDefinition, WorkflowNode


class PipelineProfileType(str, Enum):
    FAST_PREVIEW = "fast_preview"
    STANDARD = "standard"
    STRICT = "strict"
    RESEARCH_GRADE = "research_grade"


class PipelineProfileRegistry:
    """Creates declarative WorkflowDefinitions based on requested profile."""

    @classmethod
    def get_workflow(cls, profile: PipelineProfileType | str = PipelineProfileType.STANDARD) -> WorkflowDefinition:
        p_enum = PipelineProfileType(profile) if isinstance(profile, str) else profile

        wf = WorkflowDefinition(workflow_id=f"wf_{p_enum.value}", name=f"{p_enum.value.title()} Profile Workflow")

        # 1. Base stage: Validation
        wf.add_node(WorkflowNode(stage_id="request_validation", stage_type=WorkflowStageType.VALIDATION, dependencies=[]))

        if p_enum == PipelineProfileType.FAST_PREVIEW:
            # Fast Preview: Validation -> Blueprint -> Composition -> Rendering -> Finalization
            wf.add_node(WorkflowNode(stage_id="blueprint_generation", stage_type=WorkflowStageType.BLUEPRINT_GENERATION, dependencies=["request_validation"]))
            wf.add_node(WorkflowNode(stage_id="composition", stage_type=WorkflowStageType.COMPOSITION, dependencies=["blueprint_generation"]))
            wf.add_node(WorkflowNode(stage_id="rendering", stage_type=WorkflowStageType.RENDERING, dependencies=["composition"]))
            wf.add_node(WorkflowNode(stage_id="finalization", stage_type=WorkflowStageType.FINALIZATION, dependencies=["rendering"]))

        elif p_enum == PipelineProfileType.STANDARD:
            # Standard: Validation -> Director -> Blueprint -> Composition -> Quality -> Rendering -> Artifact Validation -> Finalization
            wf.add_node(WorkflowNode(stage_id="directing", stage_type=WorkflowStageType.DIRECTING, dependencies=["request_validation"]))
            wf.add_node(WorkflowNode(stage_id="blueprint_generation", stage_type=WorkflowStageType.BLUEPRINT_GENERATION, dependencies=["directing"]))
            wf.add_node(WorkflowNode(stage_id="composition", stage_type=WorkflowStageType.COMPOSITION, dependencies=["blueprint_generation"]))
            wf.add_node(WorkflowNode(stage_id="pre_render_quality", stage_type=WorkflowStageType.PRE_RENDER_QUALITY, dependencies=["composition"]))
            wf.add_node(WorkflowNode(stage_id="rendering", stage_type=WorkflowStageType.RENDERING, dependencies=["pre_render_quality"]))
            wf.add_node(WorkflowNode(stage_id="artifact_validation", stage_type=WorkflowStageType.ARTIFACT_VALIDATION, dependencies=["rendering"]))
            wf.add_node(WorkflowNode(stage_id="finalization", stage_type=WorkflowStageType.FINALIZATION, dependencies=["artifact_validation"]))

        elif p_enum in [PipelineProfileType.STRICT, PipelineProfileType.RESEARCH_GRADE]:
            # Strict / Research Grade: Validation -> Grounding -> Director -> Blueprint -> Personalization -> Composition -> Quality -> Rendering -> Artifact Validation -> Finalization
            wf.add_node(WorkflowNode(stage_id="grounding", stage_type=WorkflowStageType.GROUNDING, dependencies=["request_validation"]))
            wf.add_node(WorkflowNode(stage_id="directing", stage_type=WorkflowStageType.DIRECTING, dependencies=["grounding"]))
            wf.add_node(WorkflowNode(stage_id="blueprint_generation", stage_type=WorkflowStageType.BLUEPRINT_GENERATION, dependencies=["directing"]))
            wf.add_node(WorkflowNode(stage_id="personalization", stage_type=WorkflowStageType.PERSONALIZATION, dependencies=["blueprint_generation"], optional=True))
            wf.add_node(WorkflowNode(stage_id="composition", stage_type=WorkflowStageType.COMPOSITION, dependencies=["personalization"]))
            wf.add_node(WorkflowNode(stage_id="pre_render_quality", stage_type=WorkflowStageType.PRE_RENDER_QUALITY, dependencies=["composition"]))
            wf.add_node(WorkflowNode(stage_id="rendering", stage_type=WorkflowStageType.RENDERING, dependencies=["pre_render_quality"]))
            wf.add_node(WorkflowNode(stage_id="artifact_validation", stage_type=WorkflowStageType.ARTIFACT_VALIDATION, dependencies=["rendering"]))
            wf.add_node(WorkflowNode(stage_id="finalization", stage_type=WorkflowStageType.FINALIZATION, dependencies=["artifact_validation"]))

        return wf
