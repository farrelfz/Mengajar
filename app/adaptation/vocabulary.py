"""
Domain Vocabulary & Mathematical Formalism Transformer.
"""

from __future__ import annotations

from app.adaptation.contracts import ComplexityLevel


VOCABULARY_REGISTRY: dict[str, dict[ComplexityLevel, str]] = {
    # Physics Terms
    "torque": {
        ComplexityLevel.FOUNDATIONAL: "Gaya Putar (Efek Memutar Benda)",
        ComplexityLevel.INTRODUCTORY: "Momen Gaya",
        ComplexityLevel.INTERMEDIATE: "Momen Gaya (Torsi)",
        ComplexityLevel.ADVANCED: "Vektor Momen Gaya (Torque Vector)",
        ComplexityLevel.EXPERT: "Rotational Torque Tensor & Cross Product",
    },
    "lever_arm": {
        ComplexityLevel.FOUNDATIONAL: "Jarak Lengan Putar",
        ComplexityLevel.INTRODUCTORY: "Lengan Momen",
        ComplexityLevel.INTERMEDIATE: "Lengan Beban Tegak Lurus (Lever Arm)",
        ComplexityLevel.ADVANCED: "Vektor Posisi Relatif Pivot (r)",
        ComplexityLevel.EXPERT: "Radial Displacement Vector",
    },
    # Research Methodology Terms
    "research_gap": {
        ComplexityLevel.FOUNDATIONAL: "Hal yang Belum Diketahui",
        ComplexityLevel.INTRODUCTORY: "Kesenjangan Informasi",
        ComplexityLevel.INTERMEDIATE: "Celah Riset (Research Gap)",
        ComplexityLevel.ADVANCED: "State-of-the-Art Epistemic Gap",
        ComplexityLevel.EXPERT: "Theoretical & Empirical Void in Literature",
    },
    "hypothesis": {
        ComplexityLevel.FOUNDATIONAL: "Dugaan Awal",
        ComplexityLevel.INTRODUCTORY: "Hipotesis Kerja",
        ComplexityLevel.INTERMEDIATE: "Hipotesis Teruji (Testable Hypothesis)",
        ComplexityLevel.ADVANCED: "Falsifiable Scientific Hypothesis",
        ComplexityLevel.EXPERT: "Operational Null/Alternative Hypothesis (H0 vs H1)",
    },
}

FORMULA_REGISTRY: dict[str, dict[ComplexityLevel, str]] = {
    "torque_formula": {
        ComplexityLevel.FOUNDATIONAL: "tau = F * d  (Gaya x Jarak)",
        ComplexityLevel.INTRODUCTORY: "tau = F * r  (Gaya x Jarak ke Pivot)",
        ComplexityLevel.INTERMEDIATE: "tau = r * F * sin(theta)",
        ComplexityLevel.ADVANCED: "\\vec{\\tau} = \\vec{r} \\times \\vec{F} = I \\vec{\\alpha}",
        ComplexityLevel.EXPERT: "\\tau_i = \\epsilon_{ijk} r_j F_k",
    },
    "newton_third_law": {
        ComplexityLevel.FOUNDATIONAL: "Aksi = Reaksi (Kekuatan sama, arah berlawanan)",
        ComplexityLevel.INTRODUCTORY: "F_aksi = -F_reaksi",
        ComplexityLevel.INTERMEDIATE: "F_AB = -F_BA  (Bekerja pada dua benda terpisah)",
        ComplexityLevel.ADVANCED: "\\frac{d\\vec{p}_{system}}{dt} = \\vec{0} \\implies \\vec{F}_{12} + \\vec{F}_{21} = \\vec{0}",
        ComplexityLevel.EXPERT: "\\nabla \\cdot \\mathbf{T} = 0  (Conservation of Momentum Tensor)",
    },
}


class VocabularyTransformer:
    """Adapts domain terminology and mathematical equations to target complexity level."""

    @staticmethod
    def transform_term(term_key: str, level: ComplexityLevel) -> str:
        key = term_key.lower().strip()
        if key in VOCABULARY_REGISTRY:
            return VOCABULARY_REGISTRY[key].get(level, VOCABULARY_REGISTRY[key][ComplexityLevel.INTERMEDIATE])
        return term_key

    @staticmethod
    def transform_formula(formula_key: str, level: ComplexityLevel) -> str:
        key = formula_key.lower().strip()
        if key in FORMULA_REGISTRY:
            return FORMULA_REGISTRY[key].get(level, FORMULA_REGISTRY[key][ComplexityLevel.INTERMEDIATE])
        return formula_key
