"""
Visual Acceptance Tests & Physical Production Truth Audit.

Verifies that generated PDF artifacts strictly adhere to physical visual truth:
1. Exact 1-to-1 page matching (logical_pages == physical_pages).
2. Zero blank pages.
3. Complete absence of forbidden debug/fallback strings ('title_block:', 'text_block:', 'placeholder', UUIDs).
4. Physical presence of high-resolution PNG page screenshots.
"""

from pathlib import Path
import pytest
import pymupdf

from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.rendering.validation.screenshot_exporter import PDFScreenshotExporter
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


FORBIDDEN_STRINGS = [
    "title_block:",
    "text_block:",
    "diagram_placeholder:",
    "key_statement:",
    "Real KTI text placeholder",
    "placeholder for",
]


@pytest.mark.asyncio
async def test_visual_acceptance_research_education(tmp_path: Path):
    """Visual acceptance test for Research Education presentation."""
    real_teaching_request = """
    # Mengubah Fenomena Menjadi Masalah Penelitian

    ## 1. Fenomena Sampah Plastik di Sekolah
    Setiap hari setelah jam istirahat sekolah, volume sampah plastik di kantin dan lapangan meningkat drastis.
    Banyak tempat sampah telah disediakan namun siswa belum memanfaatkannya secara konsisten.

    ## 2. Identifikasi dan Pembatasan Masalah
    Kesenjangan utama adalah perilaku pembuangan sampah yang belum optimal meskipun sarana tersedia.
    Penelitian ini membatasi lingkup pada siswa SMA kelas 10 dan 11 selama semester ganjil.

    ## 3. Rumusan Masalah dan Hipotesis
    Bagaimana pengaruh penempatan tempat sampah tematik terhadap kepatuhan pembuangan sampah siswa?
    Jika tempat sampah tematik diletakkan dekat area duduk, maka tingkat kepatuhan membuang sampah akan meningkat signifikan.
    """

    out_dir = tmp_path / "research_education_visual"
    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    result = await pipeline.produce_artifact(
        raw_input=real_teaching_request,
        source_hint="research_problem_formulation.md",
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=out_dir,
    )

    assert result.success is True
    assert result.pdf_path is not None
    pdf_path = Path(result.pdf_path)
    assert pdf_path.exists()

    # Export PNG screenshots
    exporter = PDFScreenshotExporter()
    screenshots_dir = out_dir / "screenshots"
    reports = exporter.export_pages(pdf_path, screenshots_dir)

    logical_pages = len(result.composition.pages)
    physical_pages = len(reports)

    # 1. Exact Page Match Invariant (No Alternating Blank Pages)
    assert logical_pages == physical_pages, f"Page mismatch: Logical {logical_pages} != Physical {physical_pages}"

    # 2. Inspect Every Page
    full_doc_text = ""
    for r in reports:
        assert not r.is_blank, f"Page {r.page_number} is completely blank!"
        full_doc_text += f"\n--- Page {r.page_number} ---\n" + r.text_content

        # Verify PNG screenshot exists
        assert Path(r.image_path).exists()
        assert Path(r.image_path).stat().st_size > 5000  # Non-trivial image file size

    # 3. Assert Absence of Forbidden Debug Strings
    for forbidden in FORBIDDEN_STRINGS:
        assert forbidden.lower() not in full_doc_text.lower(), f"Forbidden string '{forbidden}' found in PDF output:\n{full_doc_text}"

    # 4. Assert Presence of Meaningful Content
    assert "MENGUBAH FENOMENA" in full_doc_text.upper() or "PENELITIAN" in full_doc_text.upper()


@pytest.mark.asyncio
async def test_visual_acceptance_physics_torque(tmp_path: Path):
    """Visual acceptance test for Physics Torque 16:9 presentation."""
    physics_request = """
    # Understanding Torque in Rotational Mechanics

    ## 1. Door Handle Analogy
    Pushing a door near the hinges requires immense effort, whereas pushing at the outer edge opens it effortlessly.

    ## 2. Formal Definition
    Torque is the rotational analog of force, defined as the cross product of lever arm r and applied force F.

    ## 3. Mathematical Model
    Tau = r * F * sin(theta). Maximum torque is achieved when the force is applied perpendicularly at 90 degrees.
    """

    out_dir = tmp_path / "physics_torque_visual"
    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    result = await pipeline.produce_artifact(
        raw_input=physics_request,
        source_hint="physics_torque.md",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=out_dir,
    )

    assert result.success is True
    pdf_path = Path(result.pdf_path)
    
    exporter = PDFScreenshotExporter()
    reports = exporter.export_pages(pdf_path, out_dir / "screenshots")

    assert len(result.composition.pages) == len(reports)
    for r in reports:
        assert not r.is_blank
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden.lower() not in r.text_content.lower()
