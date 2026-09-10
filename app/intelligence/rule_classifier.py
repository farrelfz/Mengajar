"""
Deterministic Rule-Based Semantic Classifier.

Classifies ContentUnit or raw text blocks into standard ContentType / SemanticBlockType
using structural syntax, mathematical patterns, table structure, list formats,
and lexical signals. Assigns confidence scores and flags ambiguous blocks for selective AI.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, Field

from app.intelligence.schemas import (
    AIClassificationOutput,
    ConfidenceLevel,
    ContentType,
    ContentUnit,
    KtiBab,
)

AI_ESCALATION_THRESHOLD = 0.70


class LocalClassificationResult(BaseModel):
    """Result of local rule-based classification."""
    unit_id: str
    content_type: ContentType
    confidence: float
    is_ambiguous: bool
    reasons: list[str] = Field(default_factory=list)
    research_role: ContentType | None = None
    kti_bab: KtiBab | None = None
    is_core_component: bool = False


class RuleClassifier:
    """Fast, 100% deterministic local semantic classifier."""

    # Mathematical / Formula patterns
    _MATH_SYMBOLS_RE = re.compile(
        r"(=|\+|-|×|/|\\times|\\frac|\\Delta|\\Sigma|\\sqrt|\^|\\approx|\\le|\\ge|\\rightarrow|->|Q\s*=|mc\\Delta T)",
        re.IGNORECASE,
    )
    _LATEX_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)

    # Table patterns
    _TABLE_RE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)
    _RISK_KEYWORDS = ["bahaya", "risiko", "pencegahan", "mitigasi", "k3", "hazard", "safety", "peringatan", "prevention"]
    _OBS_KEYWORDS = ["pengamatan", "observasi", "ulangan", "triplo", "tinggi gelembung", "hasil pengamatan", "tabel data"]

    # Procedure / Process patterns
    _PROCEDURE_KEYWORDS = ["prosedur", "langkah", "tahapan", "cara kerja", "metode", "aktivitas", "step"]
    _NUMBERED_STEP_RE = re.compile(r"^\s*\d+[\.\)]\s+", re.MULTILINE)

    # Question / Discussion patterns
    _CRITICAL_KEYWORDS = ["mengapa", "bagaimana jika", "menurutmu", "prediksi", "apakah", "kenapa", "why", "what if"]

    # Section-based keywords
    _SECTION_MAP: list[tuple[list[str], ContentType, float]] = [
        (["kesimpulan", "conclusion", "rangkuman", "sintesis"], ContentType.CONCLUSION, 0.95),
        (["latar belakang", "pendahuluan", "overview"], ContentType.BACKGROUND, 0.90),
        (["tujuan", "objective", "indikator"], ContentType.OBJECTIVE, 0.95),
        (["rumusan masalah", "problem", "masalah"], ContentType.PROBLEM, 0.95),
        (["hipotesis", "hypothesis"], ContentType.HYPOTHESIS, 0.95),
        (["alat", "reagen", "materials", "aparatus"], ContentType.MATERIAL, 0.95),
        (["diskusi", "pembahasan", "discussion"], ContentType.DISCUSSION, 0.90),
        (["pertanyaan", "inquiry", "evaluasi"], ContentType.QUESTION, 0.90),
        (["definisi", "pengertian", "definition"], ContentType.DEFINITION, 0.95),
        (["teori", "landasan", "hukum newton", "termodinamika"], ContentType.THEORY, 0.85),
        (["paradigma", "dogma", "konsep dasar", "prinsip dasar", "fenomena"], ContentType.CONCEPT, 0.85),
        (["kontradiksi", "logika", "argumen", "eksperimen pikiran", "gedankenexperiment"], ContentType.ARGUMENT, 0.85),
        (["metodologi", "metode penelitian", "metodologi ilmiah"], ContentType.METHOD, 0.90),
    ]

    def classify_unit(
        self,
        unit: ContentUnit,
        parent_heading: str = "",
        context_before: str = "",
        context_after: str = "",
    ) -> LocalClassificationResult:
        """Classify a ContentUnit using deterministic rule heuristics."""
        text = (unit.normalized_text or unit.raw_text or "").strip()
        text_lower = text.lower()
        parent_lower = (parent_heading or unit.title or "").lower()
        combined_text = f"{parent_lower}\n{text_lower}"

        reasons: list[str] = []
        c_type = ContentType.EXPLANATION
        confidence = 0.50

        # 1. Structural Title Check
        if unit.content_type == ContentType.TITLE or text.startswith("#"):
            return LocalClassificationResult(
                unit_id=unit.unit_id,
                content_type=ContentType.TITLE,
                confidence=1.0,
                is_ambiguous=False,
                reasons=["Structural markdown heading"],
            )

        # 2. Mathematical Formula Check
        if self._LATEX_BLOCK_RE.search(text) or text.startswith("$$") or (
            ("=" in text) and any(sym in text for sym in ["\\Delta", "\\rightarrow", "->", "+", "\\times", "Q ="])
        ):
            return LocalClassificationResult(
                unit_id=unit.unit_id,
                content_type=ContentType.FORMULA,
                confidence=0.98,
                is_ambiguous=False,
                reasons=["Mathematical formula syntax and LaTeX detected"],
            )

        # 3. Table / Risk Matrix / Data Check
        if self._TABLE_RE.search(text) or "|" in text:
            if any(k in combined_text for k in self._RISK_KEYWORDS):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.WARNING,
                    confidence=0.95,
                    is_ambiguous=False,
                    reasons=["Table with hazard/safety/risk columns detected"],
                )
            elif any(k in combined_text for k in self._OBS_KEYWORDS):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.DATA,
                    confidence=0.95,
                    is_ambiguous=False,
                    reasons=["Table with observation/experimental data detected"],
                )
            else:
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.DATA,
                    confidence=0.90,
                    is_ambiguous=False,
                    reasons=["Structured markdown table detected"],
                )

        # 4. Procedure / Process Check
        if self._NUMBERED_STEP_RE.search(text) or any(k in parent_lower for k in self._PROCEDURE_KEYWORDS):
            if any(k in parent_lower for k in self._PROCEDURE_KEYWORDS):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.PROCEDURE,
                    confidence=0.95,
                    is_ambiguous=False,
                    reasons=["Sequential numbered steps under procedure heading"],
                )
            elif self._NUMBERED_STEP_RE.search(text):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.PROCESS,
                    confidence=0.85,
                    is_ambiguous=False,
                    reasons=["Numbered sequential list pattern"],
                )

        # 5. Warning / Blockquote Check
        if text.startswith(">") or any(w in text_lower for w in ["peringatan", "warning", "hati-hati", "hazard", "safety"]):
            return LocalClassificationResult(
                unit_id=unit.unit_id,
                content_type=ContentType.WARNING,
                confidence=0.92,
                is_ambiguous=False,
                reasons=["Callout warning / blockquote syntax"],
            )

        # 6. Question / Critical Thinking Check
        if "?" in text:
            if any(q in text_lower for q in self._CRITICAL_KEYWORDS):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.QUESTION,
                    confidence=0.94,
                    is_ambiguous=False,
                    reasons=["Investigative / critical thinking question pattern"],
                )
            else:
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=ContentType.QUESTION,
                    confidence=0.90,
                    is_ambiguous=False,
                    reasons=["Question punctuation mark detected"],
                )

        # 7. Section Heading-guided Classification
        for keywords, target_type, conf in self._SECTION_MAP:
            if any(kw in parent_lower for kw in keywords):
                return LocalClassificationResult(
                    unit_id=unit.unit_id,
                    content_type=target_type,
                    confidence=conf,
                    is_ambiguous=False,
                    reasons=[f"Contextual section keyword match: {parent_heading}"],
                )

        # 8. Definition Lexical Signals
        if any(w in text_lower for w in [" adalah ", " merupakan ", " didefinisikan sebagai ", " yaitu "]):
            return LocalClassificationResult(
                unit_id=unit.unit_id,
                content_type=ContentType.DEFINITION,
                confidence=0.82,
                is_ambiguous=False,
                reasons=["Definitional copula phrase detected"],
            )

        # 9. Fallback ambiguous paragraph
        is_ambiguous = confidence < AI_ESCALATION_THRESHOLD
        return LocalClassificationResult(
            unit_id=unit.unit_id,
            content_type=ContentType.EXPLANATION,
            confidence=0.60,
            is_ambiguous=True,
            reasons=["General explanatory narrative block"],
        )

    def to_ai_output(self, res: LocalClassificationResult) -> AIClassificationOutput:
        """Convert a LocalClassificationResult into AIClassificationOutput schema."""
        return AIClassificationOutput(
            unit_id=res.unit_id,
            content_type=res.content_type,
            research_role=res.research_role,
            kti_bab=res.kti_bab,
            is_core_component=res.is_core_component,
            confidence=ConfidenceLevel.HIGH if res.confidence >= 0.80 else (ConfidenceLevel.MEDIUM if res.confidence >= 0.60 else ConfidenceLevel.LOW),
            reasons=res.reasons,
            source_fidelity_flags=[],
        )
