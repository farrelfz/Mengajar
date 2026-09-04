"""
Tests for Density adaptation, Format adaptation, and Determinism across Capability Families.
"""

from app.capabilities.families.contracts import ComparisonItem, ComparisonSpec, ProcessSpec, ProcessStage
from app.capabilities.families.templates import LinearProcessTemplate, MatrixComparisonTemplate
from app.capabilities.taxonomy import DensityProfile


def test_process_template_density_adaptation():
    template = LinearProcessTemplate()

    # 1. Minimal density
    spec_min = ProcessSpec(
        title="Compact Process",
        density=DensityProfile.MINIMAL,
        stages=[
            ProcessStage(id="1", label="Phase One", description="Extensive description not shown"),
            ProcessStage(id="2", label="Phase Two", description="Another description"),
        ],
    )
    html_min = template.render_html(spec_min)
    assert "Phase One" in html_min
    assert "Extensive description not shown" not in html_min  # Minimal density trims description

    # 2. Dense reference density
    spec_dense = ProcessSpec(
        title="Detailed Protocol",
        density=DensityProfile.DENSE_REFERENCE,
        stages=[
            ProcessStage(
                id="1",
                label="Centrifuge Sample",
                description="Spin at 4000 rpm for 10 min",
                meta_info={"Reagent": "Buffer A", "Temp": "4C"},
            ),
        ],
    )
    html_dense = template.render_html(spec_dense)
    assert "Centrifuge Sample" in html_dense
    assert "Spin at 4000 rpm for 10 min" in html_dense
    assert "Reagent:" in html_dense
    assert "Buffer A" in html_dense


def test_comparison_template_highlight_and_attributes():
    template = MatrixComparisonTemplate()
    spec = ComparisonSpec(
        title="Framework Comparison",
        highlight_dimension="Cost",
        items=[
            ComparisonItem(
                id="opt_a",
                name="Solution A",
                tag="Open Source",
                highlight=True,
                attributes={"Cost": "Free", "Support": "Community"},
            ),
            ComparisonItem(
                id="opt_b",
                name="Solution B",
                tag="Enterprise",
                highlight=False,
                attributes={"Cost": "$$$", "Support": "24/7 SLA"},
            ),
        ],
    )
    rendered = template.render_html(spec)
    assert "Solution A" in rendered
    assert "Solution B" in rendered
    assert "Open Source" in rendered
    assert "Enterprise" in rendered
    assert "ring-indigo-500" in rendered  # Highlight class


def test_family_rendering_determinism():
    template = LinearProcessTemplate()
    spec = ProcessSpec(
        title="Deterministic Flow",
        stages=[
            ProcessStage(id="1", label="Step 1", description="Description 1"),
            ProcessStage(id="2", label="Step 2", description="Description 2"),
            ProcessStage(id="3", label="Step 3", description="Description 3"),
        ],
    )

    out1 = template.render_html(spec)
    out2 = template.render_html(spec)
    out3 = template.render_html(spec)

    assert out1 == out2
    assert out2 == out3
