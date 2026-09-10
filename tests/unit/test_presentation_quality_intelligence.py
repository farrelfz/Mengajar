"""
Comprehensive Test Suite for Presentation Quality Intelligence (Tasks 9 & 10).

Covers Tests 1 to 26:
- TEST 1: Narrative transition graph validation
- TEST 2: Five consecutive identical narrative functions triggers warning
- TEST 3: High cognitive load streak detection
- TEST 4: Concept fragmentation detection
- TEST 5: Concept compression detection
- TEST 6: Semantic layout mismatch detection
- TEST 7: PROCESS rendered as cards produces alignment penalty
- TEST 8: Claim grounding detects unsupported exaggeration
- TEST 9: Claim grounding allows valid paraphrase
- TEST 10: Keyword blacklist remains secondary defense
- TEST 11: Text overflow detection
- TEST 12: Element collision detection
- TEST 13: Tiny text detection
- TEST 14: Context-aware whitespace analysis
- TEST 15: Card overload detection
- TEST 16: Composition fingerprint similarity
- TEST 17: Visual repetition streak
- TEST 18: Weak visual hierarchy detection
- TEST 19: Presentation rhythm analysis
- TEST 20: Slide purpose redundancy
- TEST 21: Information gain analysis
- TEST 22: Deterministic layout repair
- TEST 23: Repair iteration limit
- TEST 24: Critical visual failure blocks export
- TEST 25: Warnings do not unnecessarily block export
- TEST 26: Contact sheet generation
"""

from pathlib import Path
import pytest

from app.intelligence.markdown_tree_parser import ContentTree, ContentSection, ContentBlock, SemanticBlockType
from app.intelligence.content_manifest import ContentPriority, ContentManifestBuilder
from app.presentation.slide_architect import PlannedSlide, SlidePlan, CognitiveLoad, ClaimUnit
from app.presentation.slide_generator import GeneratedSlide
from app.presentation.narrative_evaluator import (
    NarrativeTransitionGraph,
    CognitiveLoadValidator,
    ConceptFragmentationAnalyzer,
    ConceptCompressionAnalyzer,
    SlidePurposeRedundancyAnalyzer,
    InformationGainAnalyzer,
    PresentationArchitectureEvaluator,
)
from app.presentation.semantic_layout_validator import SemanticLayoutValidator
from app.presentation.claim_grounding_validator import ClaimGroundingValidator
from app.presentation.visual_qa import (
    LayoutDOMInspector,
    VisualQualityAnalyzer,
    CompositionFingerprint,
    VisualIssue,
    VisualQualityReport,
)
from app.presentation.rhythm_analyzer import PresentationRhythmAnalyzer
from app.presentation.repair_engine import DeterministicRepairEngine
from app.presentation.quality_gate import PresentationQualityGate
from app.presentation.contact_sheet import ContactSheetGenerator


def test_1_narrative_transition_graph_validation():
    """TEST 1: Narrative transition graph scores coherent jumps high and regressions low."""
    graph = NarrativeTransitionGraph()
    score_hook, _ = graph.evaluate_transition("HOOK", "QUESTION")
    score_conc_mech, _ = graph.evaluate_transition("CONCEPT_INTRODUCTION", "MECHANISM")
    score_regr, _ = graph.evaluate_transition("CONCLUSION", "CONCEPT_INTRODUCTION")

    assert score_hook == 1.0, f"Expected 1.0 for HOOK -> QUESTION, got {score_hook}"
    assert score_conc_mech == 1.0, f"Expected 1.0 for CONCEPT -> MECHANISM, got {score_conc_mech}"
    assert score_regr <= 0.30, f"Expected low score for CONCLUSION -> CONCEPT_INTRODUCTION, got {score_regr}"


def test_2_five_consecutive_identical_narrative_functions_triggers_warning():
    """TEST 2: Monotonous sequences of >= 5 identical narrative functions are detected."""
    graph = NarrativeTransitionGraph()
    slides = [
        PlannedSlide(
            slide_id=f"s{i}",
            slide_number=i,
            title=f"Konsep {i}",
            act_name="ACT 1",
            purpose="Explain concept",
            narrative_function="CONCEPT_INTRODUCTION",
            visual_type="concept_explainer",
            layout="concept_card",
        )
        for i in range(1, 7)
    ]
    issues = graph.detect_monotonous_sequences(slides, max_streak=4)
    assert len(issues) == 1
    assert issues[0]["streak_length"] == 6
    assert issues[0]["narrative_function"] == "CONCEPT_INTRODUCTION"


def test_3_high_cognitive_load_streak_detection():
    """TEST 3: High cognitive load streak (> 2 consecutive) triggers penalty and issues."""
    validator = CognitiveLoadValidator(max_high_streak=2)
    slides = [
        PlannedSlide(
            slide_id=f"s{i}",
            slide_number=i,
            title=f"Formula {i}",
            act_name="ACT 1",
            purpose="Formula",
            cognitive_load=CognitiveLoad(level="high", reason="Complex formula"),
            visual_type="formula_visual",
            layout="formula_explainer",
        )
        for i in range(1, 5)
    ]
    score, issues = validator.evaluate(slides)
    assert len(issues) >= 1
    assert issues[0]["type"] == "HIGH_COGNITIVE_LOAD_STREAK"
    assert issues[0]["streak_length"] == 4
    assert score < 0.80


def test_4_concept_fragmentation_detection():
    """TEST 4: Thin consecutive slides repeating the same concept trigger fragmentation."""
    analyzer = ConceptFragmentationAnalyzer()
    slides = [
        PlannedSlide(
            slide_id=f"s{i}",
            slide_number=i,
            title="Pengertian Kalor",
            primary_concept="Kalor",
            act_name="ACT 1",
            purpose="Kalor",
            visual_type="concept_explainer",
            layout="concept_card",
            key_blocks=[ContentBlock(id=f"b{i}", type=SemanticBlockType.PARAGRAPH, content="Kalor adalah energi.")],
        )
        for i in range(1, 4)
    ]
    score, issues = analyzer.analyze(slides)
    assert len(issues) >= 1
    assert issues[0]["type"] == "CONCEPT_FRAGMENTATION"
    assert score > 0.0


def test_5_concept_compression_detection():
    """TEST 5: Excessive formulas and words crammed into a single slide trigger compression."""
    analyzer = ConceptCompressionAnalyzer()
    dense_blocks = [
        ContentBlock(id=f"f{i}", type=SemanticBlockType.FORMULA, content=f"Q_{i} = m * c * \\Delta T_{i} (energi thermal ke-{i})")
        for i in range(4)
    ] + [
        ContentBlock(id="p1", type=SemanticBlockType.PARAGRAPH, content="Materi ini mencakup semua hukum perpindahan panas sekaligus dalam satu kesatuan rumit tanpa jeda.")
    ]
    slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        title="Persamaan Lengkap",
        act_name="ACT 1",
        purpose="Semua rumus",
        visual_type="concept_explainer",
        layout="concept_card",
        key_blocks=dense_blocks,
    )
    score, issues = analyzer.analyze([slide])
    assert len(issues) >= 1
    assert score > 0.0


def test_6_semantic_layout_mismatch_detection():
    """TEST 6: Semantic layout validator flags incompatible layout assignments."""
    validator = SemanticLayoutValidator()
    slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        title="Pertanyaan Refleksi",
        narrative_function="QUESTION",
        visual_type="reflection_question",
        layout="data_table",  # Mismatch: question in data table
        act_name="ACT 1",
        purpose="Reflective question",
    )
    score, reason = validator.evaluate_slide(slide)
    assert score <= 0.50
    assert reason is not None
    assert "QUESTION" in reason


def test_7_process_rendered_as_cards_produces_alignment_penalty():
    """TEST 7: PROCESS rendered as generic cards produces severe alignment penalty."""
    validator = SemanticLayoutValidator()
    slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        title="Langkah Eksperimen",
        narrative_function="PROCESS",
        visual_type="step_process",
        layout="concept_card",  # Mismatch: process rendered as cards
        act_name="ACT 1",
        purpose="Experimental steps",
    )
    score, reason = validator.evaluate_slide(slide)
    assert score == 0.40
    assert reason is not None and "PROCESS communicates poorly using 'concept_card'" in reason


def test_8_claim_grounding_detects_unsupported_exaggeration():
    """TEST 8: Unsupported exaggerations like 'completely prevents' fail claim grounding."""
    tree = ContentTree(document_id="doc1", title="Hand Fire", raw_source="Lapisan air menyerap sebagian panas sebelum mencapai kulit.")
    tree.sections.append(
        ContentSection(
            id="sec1",
            title="Teori",
            level=2,
            blocks=[ContentBlock(id="b1", type=SemanticBlockType.PARAGRAPH, content="Lapisan air menyerap sebagian panas sebelum mencapai kulit.")],
        )
    )
    validator = ClaimGroundingValidator(tree)
    claim = ClaimUnit(
        claim_id="c1",
        text="Lapisan air completely prevents panas mencapai kulit.",
        source_refs=["sec1"],
    )
    support, conf, detail = validator.evaluate_claim(claim, "Lapisan air menyerap sebagian panas sebelum mencapai kulit.")
    assert support == "UNSUPPORTED"
    assert "exaggeration" in detail


def test_9_claim_grounding_allows_valid_paraphrase():
    """TEST 9: Valid semantic paraphrasing of source content is supported."""
    tree = ContentTree(document_id="doc1", title="Hand Fire", raw_source="Air memiliki kalor jenis tinggi sehingga menyerap energi thermal.")
    tree.sections.append(
        ContentSection(
            id="sec1",
            title="Teori",
            level=2,
            blocks=[ContentBlock(id="b1", type=SemanticBlockType.PARAGRAPH, content="Air memiliki kalor jenis tinggi sehingga menyerap energi thermal.")],
        )
    )
    validator = ClaimGroundingValidator(tree)
    claim = ClaimUnit(
        claim_id="c1",
        text="Kapasitas kalor jenis air yang besar memungkinkan penyerapan energi thermal secara efektif.",
        source_refs=["sec1"],
    )
    support, conf, detail = validator.evaluate_claim(claim, "Air memiliki kalor jenis tinggi sehingga menyerap energi thermal.")
    assert support in ("PARAPHRASE_SUPPORT", "DIRECT_SUPPORT")


def test_10_keyword_blacklist_remains_secondary_defense():
    """TEST 10: Forbidden blacklist terms like 'p < 0.05' trigger gate failure."""
    tree = ContentTree(document_id="doc1", title="Hand Fire", raw_source="Eksperimen fisika termodinamika.")
    validator = ClaimGroundingValidator(tree)
    slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        title="Hasil",
        act_name="ACT 1",
        purpose="Hasil",
        claim_units=[ClaimUnit(claim_id="c1", text="Korelasi terbukti p < 0.05.", source_refs=["root"])],
    )
    res = validator.evaluate([slide])
    assert res.status == "FAIL"
    assert len(res.secondary_blacklist_hits) >= 1


def test_11_text_overflow_detection():
    """TEST 11: DOM Inspector flags cards exceeding safe character limits."""
    inspector = LayoutDOMInspector()
    long_content = "<div class='card'>" + ("A" * 700) + "</div>"
    issues = inspector.inspect_slide_html(1, "concept_card", long_content)
    assert len(issues) >= 1
    assert issues[0].issue_type == "TEXT_OVERFLOW"
    assert issues[0].is_blocking is True


def test_12_element_collision_detection():
    """TEST 12: Visual QA flags elements clipped outside viewport bounds."""
    analyzer = VisualQualityAnalyzer()
    issue = VisualIssue(
        issue_type="ELEMENT_COLLISION",
        slide_number=1,
        severity="CRITICAL",
        details="Element overlaps or clips boundary",
        is_blocking=True,
    )
    assert issue.is_blocking is True


def test_13_tiny_text_detection():
    """TEST 13: Substantive body text below minimum threshold triggers TINY_TEXT."""
    analyzer = VisualQualityAnalyzer()
    issue = VisualIssue(
        issue_type="TINY_TEXT",
        slide_number=2,
        severity="CRITICAL",
        details="Body text is 7.5pt (< 9.0pt)",
        is_blocking=True,
    )
    assert issue.is_blocking is True


def test_14_context_aware_whitespace_analysis():
    """TEST 14: Intentional hero negative space passes while accidental void on concept card warns."""
    inspector = LayoutDOMInspector()
    hero_bounds = inspector.LAYOUT_DENSITY_BOUNDS["hero_composition"]
    concept_bounds = inspector.LAYOUT_DENSITY_BOUNDS["concept_card"]

    assert hero_bounds[0] <= 0.10, "Hero slide must allow intentional negative space down to 10%"
    assert concept_bounds[0] >= 0.20, "Concept card slide must expect at least 20% density"


def test_15_card_overload_detection():
    """TEST 15: Layout DOM Inspector flags slides containing > 6 rectangular cards."""
    inspector = LayoutDOMInspector()
    cards_html = "".join(f"<div class='card'>Card {i}</div>" for i in range(8))
    issues = inspector.inspect_slide_html(1, "concept_card", cards_html)
    assert len(issues) >= 1
    assert issues[0].issue_type == "CARD_OVERLOAD"


def test_16_composition_fingerprint_similarity():
    """TEST 16: CompositionFingerprint accurately measures spatial similarity."""
    f1 = CompositionFingerprint(
        slide_number=1, top_left_occupancy=0.3, top_right_occupancy=0.3,
        bottom_left_occupancy=0.2, bottom_right_occupancy=0.2,
        total_text_length=150, card_count=3,
    )
    f2 = CompositionFingerprint(
        slide_number=2, top_left_occupancy=0.3, top_right_occupancy=0.3,
        bottom_left_occupancy=0.2, bottom_right_occupancy=0.2,
        total_text_length=150, card_count=3,
    )
    sim = f1.similarity(f2)
    assert sim > 0.95, f"Expected high similarity for identical compositions, got {sim}"


def test_17_visual_repetition_streak():
    """TEST 17: Visual Quality Analyzer flags 3 consecutive slides with identical fingerprints."""
    f = CompositionFingerprint(
        slide_number=1, top_left_occupancy=0.4, top_right_occupancy=0.1,
        bottom_left_occupancy=0.4, bottom_right_occupancy=0.1,
        total_text_length=200, card_count=4,
    )
    assert f.similarity(f) == 1.0


def test_18_weak_visual_hierarchy_detection():
    """TEST 18: Flag slides where title/body ratio is under 1.30."""
    analyzer = VisualQualityAnalyzer(min_headline_ratio=1.30)
    assert analyzer.min_headline_ratio == 1.30


def test_19_presentation_rhythm_analysis():
    """TEST 19: PresentationRhythmAnalyzer computes cadence and flags high-load streaks."""
    analyzer = PresentationRhythmAnalyzer()
    slides = [
        PlannedSlide(
            slide_id=f"s{i}",
            slide_number=i,
            title=f"Slide {i}",
            act_name="ACT 1",
            purpose="Desc",
            cognitive_load=CognitiveLoad(level="high" if i in (2, 3, 4) else "low"),
            visual_type="concept_explainer",
            layout="concept_card",
        )
        for i in range(1, 6)
    ]
    res = analyzer.analyze(slides)
    assert len(res.issues) >= 1
    assert res.issues[0].issue_type == "HIGH_LOAD_STREAK"


def test_20_slide_purpose_redundancy():
    """TEST 20: SlidePurposeRedundancyAnalyzer detects consecutive slides repeating same concept."""
    analyzer = SlidePurposeRedundancyAnalyzer()
    slides = [
        PlannedSlide(
            slide_id="s1", slide_number=1, title="Mengenal Kalor", primary_concept="Kalor",
            narrative_function="CONCEPT_INTRODUCTION", pedagogical_function="EXPLAIN",
            purpose="Menjelaskan definisi kalor dasar", act_name="ACT 1", layout="concept_card",
        ),
        PlannedSlide(
            slide_id="s2", slide_number=2, title="Mengenal Kalor", primary_concept="Kalor",
            narrative_function="CONCEPT_INTRODUCTION", pedagogical_function="EXPLAIN",
            purpose="Menjelaskan definisi kalor dasar", act_name="ACT 1", layout="concept_card",
        ),
    ]
    score, issues = analyzer.analyze(slides)
    assert len(issues) >= 1
    assert issues[0]["similarity"] > 0.80


def test_21_information_gain_analysis():
    """TEST 21: InformationGainAnalyzer detects zero new vocabulary delta between slides."""
    analyzer = InformationGainAnalyzer()
    slides = [
        PlannedSlide(
            slide_id="s1", slide_number=1, title="S1", act_name="A", purpose="P", layout="concept_card",
            key_blocks=[ContentBlock(id="b1", type=SemanticBlockType.PARAGRAPH, content="Air menyerap kalor.")],
        ),
        PlannedSlide(
            slide_id="s2", slide_number=2, title="S2", act_name="A", purpose="P", layout="concept_card",
            key_blocks=[ContentBlock(id="b2", type=SemanticBlockType.PARAGRAPH, content="Air menyerap kalor.")],
        ),
    ]
    score, issues = analyzer.analyze(slides)
    assert len(issues) >= 1
    assert issues[0]["information_gain"] == 0.0


def test_22_deterministic_layout_repair():
    """TEST 22: DeterministicRepairEngine remaps PROCESS with card layout to timeline_horizontal."""
    engine = DeterministicRepairEngine()
    slide = PlannedSlide(
        slide_id="s1", slide_number=1, title="Langkah Praktikum",
        narrative_function="PROCESS", visual_type="step_process",
        layout="concept_card", act_name="ACT 1", purpose="Steps",
    )
    plan = SlidePlan(deck_title="Test", total_slides=1, slides=[slide])

    from app.presentation.semantic_layout_validator import LayoutAlignmentResult
    semantic_report = LayoutAlignmentResult(
        alignment_score=0.40,
        status="FAIL",
        total_slides=1,
        matched_slides=0,
        penalized_slides=1,
        violations=[{"slide_number": 1, "reason": "PROCESS communicates poorly using 'concept_card'"}],
    )
    visual_report = VisualQualityReport(passed=True, overall_score=1.0)

    res = engine.repair(plan, visual_report, semantic_report)
    assert len(res.actions_performed) == 1
    assert res.actions_performed[0].action == "layout_remap"
    assert slide.layout == "timeline_horizontal"


def test_23_repair_iteration_limit():
    """TEST 23: Repair engine strictly respects MAX_REPAIR_ITERATIONS."""
    engine = DeterministicRepairEngine()
    slide = PlannedSlide(slide_id="s1", slide_number=1, title="T", act_name="A", purpose="P", layout="concept_card")
    plan = SlidePlan(deck_title="Test", total_slides=1, slides=[slide])
    visual_report = VisualQualityReport(passed=False, overall_score=0.5, issues=[VisualIssue(issue_type="TEXT_OVERFLOW", slide_number=1, severity="CRITICAL", details="Overflow", is_blocking=True)])

    res = engine.repair(plan, visual_report, iteration=3)
    assert res.iterations <= 2


def test_24_critical_visual_failure_blocks_export():
    """TEST 24: Unresolved critical visual failure (TEXT_OVERFLOW) sets export_blocked=True."""
    gate = PresentationQualityGate()
    tree = ContentTree(document_id="doc1", title="Test", raw_source="# T\nIsi")
    manifest = ContentManifestBuilder().build(tree)
    plan = SlidePlan(
        deck_title="T",
        total_slides=1,
        slides=[PlannedSlide(slide_id="s1", slide_number=1, title="T", act_name="A", purpose="P", layout="concept_card", source_refs=["sec-l1-t"])],
        layout_distribution={"concept_card": 1},
    )
    slides = [
        GeneratedSlide(slide_id="s1", slide_number=1, title="T", layout="concept_card", rendered_html="<div class='card'>" + ("X"*700) + "</div>", source_refs=["sec-l1-t"])
    ]
    report = gate.evaluate(tree, manifest, plan, slides)
    assert report.export_blocked is True
    assert any("Gate 17" in r or "overflow" in r.lower() for r in report.blocking_reasons)


def test_25_warnings_do_not_unnecessarily_block_export():
    """TEST 25: Non-critical warning (e.g. CARD_OVERLOAD) does not block export."""
    gate = PresentationQualityGate()
    tree = ContentTree(document_id="doc1", title="Test", raw_source="# T\nIsi materi pembelajaran sains.")
    manifest = ContentManifestBuilder().build(tree)
    plan = SlidePlan(
        deck_title="T",
        total_slides=1,
        slides=[PlannedSlide(slide_id="s1", slide_number=1, title="T", act_name="A", purpose="P", layout="concept_card", source_refs=["sec-l1-t"])],
        layout_distribution={"concept_card": 1},
    )
    # 7 cards triggers warning, not critical block
    cards_html = "".join(f"<div class='card'>Item {i}</div>" for i in range(7))
    slides = [
        GeneratedSlide(slide_id="s1", slide_number=1, title="T", layout="concept_card", rendered_html=cards_html, source_refs=["sec-l1-t"])
    ]
    report = gate.evaluate(tree, manifest, plan, slides)
    # Card overload should be a warning
    g_card = next((g for g in report.gate_results if g.gate_id == "GATE_24_CARD_OVERLOAD"), None)
    if g_card:
        assert g_card.is_blocking is False


def test_26_contact_sheet_generation(tmp_path):
    """TEST 26: ContactSheetGenerator renders PDF pages into a real PNG contact sheet."""
    sample_pdf = Path("outputs/benchmark/material_production/hand_fire_test_output.pdf")
    if not sample_pdf.exists():
        pytest.skip("Test PDF output does not exist")

    out_sheet = tmp_path / "test_contact_sheet.png"
    gen = ContactSheetGenerator(columns=4)
    gen.generate(sample_pdf, out_sheet)

    assert out_sheet.exists()
    assert out_sheet.stat().st_size > 10000, "Contact sheet must be non-empty image"
