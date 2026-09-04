"""
KIR AI Document Intelligence — Balance Evaluator.

Analyzes proposed page layouts for risks such as monotony, overcrowding,
or missing hierarchy, outputting a BalanceReport.
"""

from app.design.schemas import PageComposition, BalanceReport, BalanceStatus, DesignWarning, DesignWarningCode, VisualWeight


def evaluate_balance(page: PageComposition) -> BalanceReport:
    """
    Evaluates the visual balance of a composed page.
    Returns a BalanceReport indicating PASS, WARNING, or FAIL.
    """
    warnings = []
    reasons = []
    strategies = []
    
    # 1. Check for missing focus (no strong elements)
    dominant_count = sum(1 for c in page.components if c.visual_weight == VisualWeight.DOMINANT)
    strong_count = sum(1 for c in page.components if c.visual_weight == VisualWeight.STRONG)
    
    if dominant_count == 0 and strong_count == 0:
        warnings.append(
            DesignWarning(
                code=DesignWarningCode.MISSING_PRIMARY_FOCUS,
                severity="warning",
                reason="Page has no dominant or strong elements. It may appear flat.",
                suggested_strategy="Elevate a key sentence or title to a higher hierarchy level."
            )
        )
        reasons.append("Lacks clear focal point.")
        
    # 2. Check for overcrowding (too many components)
    if len(page.components) > 7:
        warnings.append(
            DesignWarning(
                code=DesignWarningCode.UNBALANCED_COMPOSITION,
                severity="warning",
                reason=f"Page has {len(page.components)} distinct visual components. Too fragmented.",
                suggested_strategy="Group related items into a single text block or split the page."
            )
        )
        strategies.append("Reduce component fragmentation.")
        
    # 3. Multiple dominant elements (competing focus)
    if dominant_count > 1:
        warnings.append(
            DesignWarning(
                code=DesignWarningCode.WEAK_HIERARCHY,
                severity="warning",
                reason="Multiple dominant elements compete for attention.",
                suggested_strategy="Demote one dominant element to strong."
            )
        )
        reasons.append("Competing primary elements.")
        
    status = BalanceStatus.PASS
    if len(warnings) >= 2:
        status = BalanceStatus.FAIL
    elif len(warnings) == 1:
        status = BalanceStatus.WARNING
        
    return BalanceReport(
        status=status,
        warnings=warnings,
        reasons=reasons,
        suggested_strategies=strategies
    )
