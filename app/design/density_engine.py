"""
KIR AI Document Intelligence — Content Density Engine.

Calculates the visual density of content groups and emits warnings if thresholds are exceeded.
"""

from app.intelligence.schemas import ContentDensity, DocumentMode
from app.design.schemas import DesignWarning, DesignWarningCode

# Max safe word counts before triggering warnings
DENSITY_LIMITS = {
    DocumentMode.A4_PORTRAIT: {
        "sparse": 80,
        "light": 150,
        "balanced": 350,
        "dense": 550,
        "max_safe": 650
    },
    DocumentMode.A4_LANDSCAPE: {
        "sparse": 50,
        "light": 100,
        "balanced": 250,
        "dense": 400,
        "max_safe": 500
    },
    DocumentMode.A4_TUTORIAL: {
        "sparse": 50,
        "light": 100,
        "balanced": 250,
        "dense": 400,
        "max_safe": 500  # Beyond this is overflow risk
    },
    DocumentMode.PRESENTATION_16_9: {
        "sparse": 20,
        "light": 40,
        "balanced": 80,
        "dense": 120,
        "max_safe": 150  # Presentations must be concise
    }
}


def evaluate_density(total_words: int, mode: DocumentMode, unit_count: int = 1) -> tuple[ContentDensity, DesignWarning | None]:
    """
    Evaluates density based on word count and document mode.
    Returns the visual density class and an optional warning if overloaded.
    """
    limits = DENSITY_LIMITS.get(mode, DENSITY_LIMITS[DocumentMode.A4_PORTRAIT])
    
    # Calculate base density
    if total_words <= limits["sparse"]:
        density = ContentDensity.LOW
    elif total_words <= limits["balanced"]:
        density = ContentDensity.MEDIUM
    elif total_words <= limits["dense"]:
        density = ContentDensity.HIGH
    else:
        density = ContentDensity.OVERLOADED
        
    warning = None
    if total_words > limits["max_safe"]:
        strategy = "CONTENT_SPLIT_REQUIRED"
        if mode == DocumentMode.PRESENTATION_16_9:
            strategy = "Switch to A4 Mode or split into multiple slides"
            
        warning = DesignWarning(
            code=DesignWarningCode.OVERFLOW_RISK,
            severity="error",
            reason=f"Content exceeds maximum safe word count for {mode.value} (Words: {total_words}, Max: {limits['max_safe']})",
            suggested_strategy=strategy
        )
    elif density == ContentDensity.OVERLOADED:
        warning = DesignWarning(
            code=DesignWarningCode.EXCESSIVE_DENSITY,
            severity="warning",
            reason=f"Content density is extremely high for {mode.value}. Readability may suffer.",
            suggested_strategy="Increase whitespace, use lists, or summarize."
        )
        
    return density, warning
