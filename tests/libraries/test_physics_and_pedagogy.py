"""
Unit tests for deterministic Physics and Pedagogical capabilities rendering.
"""

from app.libraries.physics import torque_diagram_capability, free_body_diagram_capability, TorqueDiagramSpec
from app.libraries.pedagogy import worked_example_capability, misconception_capability, WorkedExampleSpec, MisconceptionSpec


def test_torque_diagram_svg_rendering():
    spec = TorqueDiagramSpec(
        lever_length_m=2.5,
        force_newtons=40.0,
        force_angle_deg=90.0,
        rotation_direction="counterclockwise",
    )
    
    assert torque_diagram_capability.renderer.validate_spec(spec) is True
    output = torque_diagram_capability.renderer.render(spec)

    assert output.output_format == "svg"
    assert "<svg" in output.rendered_content
    assert "</svg>" in output.rendered_content
    # Check torque math in metadata
    assert output.metadata["tau_newton_meters"] == 100.0  # 2.5 * 40 * sin(90) = 100
    assert "τ = 100.0 N·m" in output.rendered_content


def test_worked_example_html_rendering():
    spec = WorkedExampleSpec(
        problem="Calculate the torque exerted by a 50 N force at a distance of 0.8 m perpendicular to the pivot.",
        knowns={"r": "0.8 m", "F": "50 N", "θ": "90°"},
        principles=["τ = r · F · sin(θ)"],
        final_answer="τ = 40 N·m",
        interpretation="The door opens easily because torque is maximized at 90 degrees.",
    )

    assert worked_example_capability.renderer.validate_spec(spec) is True
    output = worked_example_capability.renderer.render(spec)

    assert output.output_format == "html"
    assert "Worked Example" in output.rendered_content
    assert "τ = 40 N·m" in output.rendered_content
    assert "50 N" in output.rendered_content


def test_misconception_correction_rendering():
    spec = MisconceptionSpec(
        common_belief="Pushing harder always produces more rotation regardless of position.",
        why_it_seems_true="Effort feels directly correlated with result.",
        counterexample="Pushing directly on the door hinges produces zero rotation regardless of force.",
        correct_explanation="Torque depends on both force AND the lever arm distance (r).",
        topic="Torque & Rotation",
    )

    assert misconception_capability.renderer.validate_spec(spec) is True
    output = misconception_capability.renderer.render(spec)

    assert output.output_format == "html"
    assert "Common Misconception" in output.rendered_content
    assert "Scientific Reality" in output.rendered_content
