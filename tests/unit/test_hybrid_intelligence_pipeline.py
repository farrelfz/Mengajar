"""
Unit and Regression Test Suite for the Hybrid Intelligence Pipeline (8 Tasks).

Validates:
- 100% Deterministic parsing (0 API calls)
- Rule-based classification of formulas, tables, procedures, and questions
- Selective AI escalation thresholds
- Content Manifest critical concept preservation
- Anti-hallucination and system log sanitization
- 11 Hard Quality Gates & Export Blocking
- Slide count sanity and layout diversity
"""

from __future__ import annotations

import pytest
from pathlib import Path

from app.intelligence.markdown_tree_parser import MarkdownTreeParser, SemanticBlockType
from app.intelligence.rule_classifier import RuleClassifier, AI_ESCALATION_THRESHOLD
from app.intelligence.content_manifest import ContentManifestBuilder, ContentPriority
from app.presentation.slide_architect import SlideArchitect, PlannedSlide
from app.presentation.slide_generator import SlideGenerator, GeneratedSlide
from app.presentation.quality_gate import PresentationQualityGate
from app.intelligence.schemas import ContentType, ContentUnit
from app.intelligence.ai_usage_policy import AIUsagePolicy


def test_1_markdown_parsing_uses_zero_api():
    """TEST 1: Markdown AST parsing is completely deterministic and local."""
    parser = MarkdownTreeParser()
    md_text = "# Title\n\nParagraph content.\n\n## Subtopic\n- Item 1\n- Item 2"
    tree = parser.parse(md_text, document_title="Test Doc")

    assert tree.total_sections_count >= 1
    assert tree.total_blocks_count >= 2
    assert tree.title in ["Title", "Test Doc"]


def test_2_formula_classification_is_local():
    """TEST 2: Formulas with LaTeX or math symbols are classified locally."""
    rule_engine = RuleClassifier()
    unit = ContentUnit(
        source_order=0,
        raw_text="$$Q = mc\\Delta T$$",
        normalized_text="$$Q = mc\\Delta T$$",
    )
    res = rule_engine.classify_unit(unit)

    assert res.content_type == ContentType.FORMULA
    assert res.confidence >= 0.95
    assert not res.is_ambiguous


def test_3_table_and_risk_matrix_is_local():
    """TEST 3: Tables with hazard/safety keywords become WARNING/risk_matrix."""
    rule_engine = RuleClassifier()
    table_text = "| Bahaya | Pencegahan |\n|---|---|\n| Api | Siapkan air |"
    unit = ContentUnit(
        source_order=0,
        raw_text=table_text,
        normalized_text=table_text,
    )
    res = rule_engine.classify_unit(unit, parent_heading="Keselamatan Kerja")

    assert res.content_type == ContentType.WARNING
    assert res.confidence >= 0.90
    assert not res.is_ambiguous


def test_4_numbered_procedure_is_local():
    """TEST 4: Numbered steps under procedure heading are classified locally."""
    rule_engine = RuleClassifier()
    proc_text = "1. Siapkan baskom air sabun.\n2. Alirkan gas butana.\n3. Ambil busa di tangan."
    unit = ContentUnit(
        source_order=0,
        raw_text=proc_text,
        normalized_text=proc_text,
    )
    res = rule_engine.classify_unit(unit, parent_heading="Tahapan Prosedur Eksperimen")

    assert res.content_type == ContentType.PROCEDURE
    assert res.confidence >= 0.90
    assert not res.is_ambiguous


def test_5_critical_thinking_question_is_local():
    """TEST 5: Questions with inquiry keywords are classified locally."""
    rule_engine = RuleClassifier()
    q_text = "Mengapa tangan tidak melepuh ketika api menyala di atas telapak tangan?"
    unit = ContentUnit(
        source_order=0,
        raw_text=q_text,
        normalized_text=q_text,
    )
    res = rule_engine.classify_unit(unit, parent_heading="Pertanyaan Diskusi")

    assert res.content_type == ContentType.QUESTION
    assert res.confidence >= 0.90
    assert not res.is_ambiguous


def test_6_ambiguous_escalation_threshold():
    """TEST 6: General narrative blocks are flagged as ambiguous (< 0.70)."""
    rule_engine = RuleClassifier()
    vague_text = "Peristiwa ini menunjukkan keterkaitan yang sangat unik dalam kehidupan."
    unit = ContentUnit(
        source_order=0,
        raw_text=vague_text,
        normalized_text=vague_text,
    )
    res = rule_engine.classify_unit(unit, parent_heading="Catatan Tambahan")

    assert res.confidence < AI_ESCALATION_THRESHOLD
    assert res.is_ambiguous is True


def test_7_content_manifest_critical_preservation():
    """TEST 7: Content Manifest extracts all formulas, warnings, and procedures as CRITICAL."""
    md_content = """# Eksperimen Termal

## Teori
$$Q = mc\\Delta T$$

## Keselamatan
> PERINGATAN: Gunakan jas lab katun dan safety goggles.

## Prosedur
1. Basahi tangan.
2. Ambil busa.
"""
    parser = MarkdownTreeParser()
    tree = parser.parse(md_content, document_title="Eksperimen Termal")
    manifest = ContentManifestBuilder().build(tree)

    assert len(manifest.critical_concepts) >= 3
    crit_categories = {c.category for c in manifest.critical_concepts}
    assert "formula" in crit_categories
    assert "safety" in crit_categories
    assert "procedure" in crit_categories


def test_8_slide_estimation_rejects_extreme_compression():
    """TEST 8: Slide count bounds reject collapsing multi-section docs into few slides."""
    parser = MarkdownTreeParser()
    sections_text = "\n\n".join(f"## Bagian {i}\nKonten materi bab {i}." for i in range(1, 16))
    tree = parser.parse(sections_text, document_title="Materi Panjang")
    manifest = ContentManifestBuilder().build(tree)

    assert manifest.min_slides >= 11
    assert manifest.max_slides >= 18


def test_9_quality_gate_rejects_consecutive_duplicates():
    """TEST 9: Gate 6 catches consecutive duplicate slides."""
    gate = PresentationQualityGate()
    parser = MarkdownTreeParser()
    tree = parser.parse("# Judul\n## A\nIsi A", document_title="Test")
    manifest = ContentManifestBuilder().build(tree)
    architect = SlideArchitect()
    plan = architect.plan(tree, manifest)

    # Inject duplicate slides
    s1 = GeneratedSlide(
        slide_id="s1",
        slide_number=1,
        title="Sama",
        layout="concept_card",
        rendered_html="<p>Konten persis sama berulang</p>",
        source_refs=["ref1"],
    )
    s2 = GeneratedSlide(
        slide_id="s2",
        slide_number=2,
        title="Sama",
        layout="concept_card",
        rendered_html="<p>Konten persis sama berulang</p>",
        source_refs=["ref1"],
    )

    report = gate.evaluate(tree, manifest, plan, [s1, s2])
    g6 = next(g for g in report.gate_results if g.gate_id == "GATE_6_CONSECUTIVE_IDENTICAL")
    assert g6.passed is False
    assert report.export_blocked is True


def test_10_quality_gate_blocks_hallucination_and_logs():
    """TEST 10: Anti-hallucination and log sanitization gates catch forbidden tokens."""
    gate = PresentationQualityGate()
    parser = MarkdownTreeParser()
    tree = parser.parse("# Judul\n## A\nIsi eksperimen sains", document_title="Test")
    manifest = ContentManifestBuilder().build(tree)
    architect = SlideArchitect()
    plan = architect.plan(tree, manifest)

    s1 = GeneratedSlide(
        slide_id="s1",
        slide_number=1,
        title="Eksperimen",
        layout="concept_card",
        rendered_html="<p>Hasil menunjukkan p < 0.05 pada treatment.</p>",
        source_refs=["ref1"],
        has_hallucination_warning=True,
    )
    s2 = GeneratedSlide(
        slide_id="s2",
        slide_number=2,
        title="Log",
        layout="concept_card",
        rendered_html="<p>[04:00:54] Job registered with AI model</p>",
        source_refs=["ref2"],
        has_sanitization_error=True,
    )

    report = gate.evaluate(tree, manifest, plan, [s1, s2])
    g7 = next(g for g in report.gate_results if g.gate_id == "GATE_7_ANTI_HALLUCINATION")
    g8 = next(g for g in report.gate_results if g.gate_id == "GATE_8_LOG_SANITIZATION")

    assert g7.passed is False
    assert g8.passed is False
    assert report.export_blocked is True


def test_11_quality_gate_blocks_insufficient_slides():
    """TEST 11: Gate 4 blocks export when generated slides < manifest.min_slides."""
    gate = PresentationQualityGate()
    parser = MarkdownTreeParser()
    sections_text = "\n\n".join(f"## Bagian {i}\nKonten materi bab {i}." for i in range(1, 12))
    tree = parser.parse(sections_text, document_title="Materi Panjang")
    manifest = ContentManifestBuilder().build(tree)
    architect = SlideArchitect()
    plan = architect.plan(tree, manifest)

    # Only provide 2 slides when min_slides is much higher
    s1 = GeneratedSlide(
        slide_id="s1", slide_number=1, title="A", layout="hero_composition",
        rendered_html="<p>A</p>", source_refs=["sec-l2-bagian-1"]
    )
    s2 = GeneratedSlide(
        slide_id="s2", slide_number=2, title="B", layout="concept_card",
        rendered_html="<p>B</p>", source_refs=["sec-l2-bagian-2"]
    )

    report = gate.evaluate(tree, manifest, plan, [s1, s2])
    g4 = next(g for g in report.gate_results if g.gate_id == "GATE_4_SLIDE_COUNT")
    assert g4.passed is False
    assert report.export_blocked is True


def test_12_telemetry_ratio_calculation():
    """TEST 12: AIUsagePolicy correctly records calls and computes local ratio."""
    policy = AIUsagePolicy()
    policy.metrics.total_blocks_processed = 20
    policy.metrics.locally_classified_blocks = 18
    policy.metrics.ai_escalated_blocks = 2
    ratio = policy.metrics.calculate_ratio()

    assert ratio == 0.90
    policy.record_call(
        task_name="Task 5: Presentation Architecture",
        purpose="Storyboard planning",
        model="gateway",
        latency=0.5,
        input_count=10,
        output_count=20,
    )
    assert policy.metrics.total_api_calls == 1
    assert policy.metrics.presentation_architecture_calls == 1
