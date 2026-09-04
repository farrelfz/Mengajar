"""
KIR AI Document Intelligence — Design System Tests.
"""
from app.design.schemas import ColorRole, TypographyScale, ComponentFamily, CompositionPattern, VisualWeight
from app.design.theme_manager import theme_registry
from app.design.visual_hierarchy import determine_hierarchy, map_hierarchy_to_typography
from app.intelligence.schemas import ContentUnit, ContentType, DocumentMode, VisualIntent, ContentDensity
from app.design.density_engine import evaluate_density
from app.design.kti_visual_mapping import get_kti_component_family
from app.design.visual_rules import evaluate_sequence
from app.design.schemas import PageComposition, DesignWarningCode
import app.design.presets.editorial
import app.design.presets.educational
import app.design.presets.presentation

def test_theme_registry():
    theme = theme_registry.get_theme("editorial_hybrid")
    assert theme.colors[ColorRole.BACKGROUND] is not None
    assert theme.is_dark_mode is False

def test_typography_mode_distinction():
    a4_scale = map_hierarchy_to_typography(1, DocumentMode.A4_TUTORIAL)
    pres_scale = map_hierarchy_to_typography(1, DocumentMode.PRESENTATION_16_9)
    assert a4_scale == TypographyScale.TITLE
    assert pres_scale == TypographyScale.HERO
    
def test_density_engine():
    density, warning = evaluate_density(10, DocumentMode.A4_TUTORIAL)
    assert density == ContentDensity.LOW
    assert warning is None
    
    density, warning = evaluate_density(160, DocumentMode.PRESENTATION_16_9)
    assert density == ContentDensity.OVERLOADED
    assert warning is not None
    assert warning.code == DesignWarningCode.OVERFLOW_RISK
    
def test_kti_bab4_distinctions():
    f_data, w_data = get_kti_component_family(ContentType.DATA)
    f_finding, w_finding = get_kti_component_family(ContentType.FINDING)
    f_interp, w_interp = get_kti_component_family(ContentType.INTERPRETATION)
    
    assert f_data == ComponentFamily.DATA_BLOCK
    assert f_finding == ComponentFamily.KEY_STATEMENT
    assert w_finding == VisualWeight.DOMINANT
    assert f_interp == ComponentFamily.TEXT_BLOCK

def test_kti_bab5_distinctions():
    f_conc, _ = get_kti_component_family(ContentType.CONCLUSION)
    f_lim, _ = get_kti_component_family(ContentType.LIMITATION)
    assert f_conc == ComponentFamily.SUMMARY_BLOCK
    assert f_lim == ComponentFamily.WARNING_BLOCK

def test_visual_monotony_prevention():
    page1 = PageComposition(page_type="GENERIC_CONTENT", composition_pattern=CompositionPattern.SEQUENTIAL)
    page2 = PageComposition(page_type="GENERIC_CONTENT", composition_pattern=CompositionPattern.SEQUENTIAL)
    page3 = PageComposition(page_type="GENERIC_CONTENT", composition_pattern=CompositionPattern.SEQUENTIAL)
    
    warnings = evaluate_sequence([page1, page2, page3])
    assert len(warnings) == 1
    assert warnings[0].code == DesignWarningCode.VISUAL_MONOTONY
