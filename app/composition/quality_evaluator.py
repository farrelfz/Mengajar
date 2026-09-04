"""
KIR AI Document Intelligence — Composition Quality Evaluator.
"""
from app.composition.schemas import DocumentComposition, CompositionQualityReport
from app.composition.page_sequence import evaluate_page_sequence
from app.composition.completeness_validator import validate_completeness

def evaluate_composition_quality(source_unit_ids: list[str], composition: DocumentComposition) -> CompositionQualityReport:
    """Evaluates the semantic and structural quality of the document composition."""
    report = CompositionQualityReport()
    
    # 1. Sequence Validation
    seq_warnings = evaluate_page_sequence(composition.pages)
    report.warnings.extend(seq_warnings)
    
    # 2. Completeness Validation
    comp_warnings = validate_completeness(source_unit_ids, composition)
    report.warnings.extend(comp_warnings)
    
    for w in comp_warnings:
        if w.severity == "error":
            report.critical_issues.append(w.reason)
            report.score = 0.0
            
    if report.score > 0.0:
        if seq_warnings:
            report.score = 0.8
        else:
            report.score = 1.0
            
    return report
