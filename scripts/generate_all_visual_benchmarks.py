"""
Generate all visual benchmarks (Presentation 16:9, Handout A4 Portrait, Research Education)
with HTML, SVGs, PDF, and high-resolution PNG page screenshots.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from app.rendering.validation.screenshot_exporter import PDFScreenshotExporter
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


async def generate_benchmark(
    name: str,
    raw_text: str,
    domain: KnowledgeDomain,
    target_artifact: TargetArtifactType,
    output_base: Path,
):
    out_dir = output_base / name
    out_dir.mkdir(parents=True, exist_ok=True)

    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    result = await pipeline.produce_artifact(
        raw_input=raw_text,
        source_hint=f"{name}.md",
        domain=domain,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=target_artifact,
        output_dir=out_dir,
        output_filename=name,
    )

    print(f"[{name}] Success: {result.success} | Pages: {len(result.composition.pages)} | PDF: {result.pdf_path}")
    if result.pdf_path:
        exporter = PDFScreenshotExporter()
        screenshots = exporter.export_pages(result.pdf_path, out_dir / "screenshots")
        print(f"[{name}] Exported {len(screenshots)} screenshots to {out_dir / 'screenshots'}")


async def main():
    base_dir = Path("outputs/visual_benchmark")

    # 1. Research Education Presentation
    research_text = """
    # Mengubah Fenomena Menjadi Masalah Penelitian

    ## 1. Fenomena Sampah Plastik di Lingkungan Sekolah
    Volume sampah plastik kemasan sekali pakai di kantin meningkat signifikan selama jam istirahat.
    Meskipun fasilitas pembuangan telah disediakan, kepatuhan pemilahan sampah oleh siswa masih rendah.

    ## 2. Identifikasi dan Pembatasan Masalah
    Kesenjangan utama adalah belum optimalnya literasi lingkungan dan ketersediaan sarana tempat sampah tematik.
    Penelitian ini dibatasi pada siswa SMA kelas X dan XI dengan fokus pada intervensi penataan fasilitas tempat sampah.

    ## 3. Rumusan Masalah dan Hipotesis
    Bagaimana efektivitas penataan tempat sampah tematik terhadap peningkatan kepatuhan pembuangan sampah siswa?
    Jika tempat sampah tematik diletakkan di dekat area istirahat, maka kepatuhan pembuangan sampah akan meningkat secara signifikan.
    """
    await generate_benchmark(
        name="research_education",
        raw_text=research_text,
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_base=base_dir,
    )

    # 2. Presentation 16:9 (Physics Torque)
    physics_text = """
    # Physics of Rotational Motion: Understanding Torque

    ## 1. Door Handle Phenomenon
    Why is a door handle positioned as far as possible from the hinges?
    Opening a door by pushing directly on the hinges requires immense force, while pushing at the edge requires minimal effort.

    ## 2. Formal Concept & Definition
    Torque (tau) is the rotational analog of force, measuring the effectiveness of a force in causing rotational acceleration.
    Formula: tau = r * F * sin(theta).

    ## 3. Rotational Equilibrium
    For a body to be in static rotational equilibrium, the net torque acting about any arbitrary pivot point must equal zero.
    """
    await generate_benchmark(
        name="presentation_16_9",
        raw_text=physics_text,
        domain=KnowledgeDomain.PHYSICS,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_base=base_dir,
    )

    # 3. Tutorial A4 (Educational Document / Handout A4 Portrait)
    tutorial_text = """
    # Panduan Metodologi Penelitian Eksperimen untuk Siswa

    ## 1. Konsep Dasar Desain Eksperimen
    Penelitian eksperimen bertujuan menguji hubungan sebab-akibat antara variabel bebas dan variabel terikat
    dengan mengontrol variabel pengganggu secara ketat.

    ## 2. Matriks Operasional Variabel
    Variabel bebas adalah perlakuan yang dimanipulasi, variabel terikat adalah respon terukur,
    dan variabel kontrol adalah kondisi yang dijaga konstan selama periode pengujian.

    ## 3. Prosedur dan Analisis Data
    Langkah pengujian mencakup pemberian pretest, pelaksanaan perlakuan selama 6 pekan, dan pemberian posttest
    yang dianalisis menggunakan uji-t berpasangan atau ANCOVA.
    """
    await generate_benchmark(
        name="tutorial_a4",
        raw_text=tutorial_text,
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        target_artifact=TargetArtifactType.DETAILED_HANDOUT,
        output_base=base_dir,
    )


if __name__ == "__main__":
    asyncio.run(main())
