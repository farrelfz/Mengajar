"""
Unit tests for Pipeline Profiles and Workflow Definition generation.
"""

import pytest
from app.orchestration.profiles import PipelineProfileRegistry, PipelineProfileType


def test_profile_registry_generates_correct_workflows():
    wf_fast = PipelineProfileRegistry.get_workflow(PipelineProfileType.FAST_PREVIEW)
    assert "rendering" in wf_fast.nodes
    assert "grounding" not in wf_fast.nodes

    wf_strict = PipelineProfileRegistry.get_workflow(PipelineProfileType.STRICT)
    assert "grounding" in wf_strict.nodes
    assert "pre_render_quality" in wf_strict.nodes
    assert "artifact_validation" in wf_strict.nodes
