"""
KIR AI Document Intelligence — Visual Quality Gate.

Evaluates a fully formed VisualBlueprint before it's passed to Rendering.
"""

from app.design.schemas import VisualBlueprint, BalanceStatus


def run_quality_gate(blueprint: VisualBlueprint) -> str:
    """
    VISUAL QUALITY GATE
    
    Returns:
    - PASS
    - PASS_WITH_WARNINGS
    - FAIL
    """
    has_warnings = False
    
    if blueprint.global_warnings:
        has_warnings = True
        # If any global warning is an error, fail immediately
        if any(w.severity == "error" for w in blueprint.global_warnings):
            return "FAIL"
            
    for page in blueprint.pages:
        if page.balance_report:
            if page.balance_report.status == BalanceStatus.FAIL:
                return "FAIL"
            if page.balance_report.status == BalanceStatus.WARNING:
                has_warnings = True
                
    if has_warnings:
        return "PASS_WITH_WARNINGS"
        
    return "PASS"
