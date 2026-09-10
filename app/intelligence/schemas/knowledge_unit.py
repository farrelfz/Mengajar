"""
Universal Knowledge Core — KnowledgeUnit & Stable ID Hashing.
"""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.intelligence.schemas.content_type import ContentType
from app.intelligence.schemas.payloads import KnowledgePayloadUnion
from app.intelligence.schemas.provenance import KnowledgeProvenance


class KnowledgeCategory(str, Enum):
    CORE_CONCEPT = "core_concept"
    PROCEDURAL = "procedural"
    EMPIRICAL = "empirical"
    FORMAL = "formal"
    EVALUATIVE = "evaluative"
    STIMULUS = "stimulus"


class IntrinsicImportance(str, Enum):
    FOUNDATIONAL = "foundational"  # Fundamental law or core definition
    CENTRAL = "central"            # Primary mechanism or main topic
    SUPPORTING = "supporting"      # Illustrative example or secondary detail
    CONTEXTUAL = "contextual"      # Historical background or optional trivia


class ResolutionStatus(str, Enum):
    LOCAL_CONFIDENT = "LOCAL_CONFIDENT"        # High-confidence local rule classification (bypasses AI)
    AI_RESOLVED = "AI_RESOLVED"                # Ambiguous unit successfully resolved via selective AI
    UNRESOLVED_OFFLINE = "UNRESOLVED_OFFLINE"  # Ambiguous unit compiled in offline mode (local confidence preserved)
    DEFERRED = "DEFERRED"                      # Ambiguous unit with AI failure / queued for retry


def normalize_content_for_identity(raw_content: str) -> str:
    """Normalizes raw content for stable semantic identity hashing.
    
    Normalizes:
    - Leading Markdown heading syntax (# Title -> Title, ## Title -> Title)
    - Cosmetic Markdown bold/italic wrappers (**text** -> text, _text_ -> text)
    - Whitespace and line breaks
    
    Preserves:
    - Mathematical and scientific operators (=, ≠, ≤, ≥, +, -, /, *, ^, Δ, °, %, →)
    - Chemical formulas (H₂O, Na+, pH)
    - Exact numeric precision and decimal values (10.5, 3.14)
    """
    text = raw_content.strip()
    # 1. Strip leading Markdown heading syntax
    text = re.sub(r"^#{1,6}\s+", "", text)
    # 2. Strip cosmetic Markdown bold/italic markers (**text**, __text__, *text*, _text_)
    text = re.sub(r"(\*\*|__|^\*|^_|\*$|_$)", "", text)
    # 3. Collapse whitespace (preserve casing for scientific and identity preservation)
    normalized = re.sub(r"\s+", " ", text.strip())
    return normalized


def generate_stable_knowledge_id(
    source_fingerprint: str,
    raw_content: str,
    content_type: str | ContentType,
) -> str:
    """Generates a cryptographic deterministic stable ID for a KnowledgeUnit.
    
    Formula: SHA256(source_fingerprint + normalized_content + content_type)[:12]
    Result format: ku_<12-char-hex-hash>
    """
    c_type_str = content_type.value if isinstance(content_type, ContentType) else str(content_type)
    normalized_content = normalize_content_for_identity(raw_content)
    
    seed = f"{source_fingerprint}:{normalized_content.lower()}:{c_type_str}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"ku_{digest}"


class KnowledgeUnit(BaseModel):
    """Atomic unit of extracted domain knowledge.
    
    Contains NO physical canvas/layout fields (no slide numbers, page numbers,
    CSS, font sizes, or presentation assumptions).
    """
    id: str = Field(description="Deterministic stable ID in format ku_<12-char-hex>")
    title: str = ""
    content_type: ContentType
    category: KnowledgeCategory
    intrinsic_importance: IntrinsicImportance = IntrinsicImportance.CENTRAL
    raw_content: Optional[str] = None
    normalized_content: Optional[str] = None
    provenance: KnowledgeProvenance
    secondary_provenances: List[KnowledgeProvenance] = Field(default_factory=list)
    payload: KnowledgePayloadUnion = Field(discriminator="kind")
    classification_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    resolution_status: ResolutionStatus = Field(default=ResolutionStatus.LOCAL_CONFIDENT)
    tags: List[str] = Field(default_factory=list)

    def __init__(self, **data: Any) -> None:
        if "confidence" in data and "classification_confidence" not in data:
            data["classification_confidence"] = data["confidence"]
        super().__init__(**data)

    @property
    def confidence(self) -> float:
        return self.classification_confidence

    @confidence.setter
    def confidence(self, val: float) -> None:
        self.classification_confidence = val

    @property
    def all_provenances(self) -> List[KnowledgeProvenance]:
        """Returns all provenance anchors associated with this semantic KnowledgeUnit."""
        return [self.provenance] + self.secondary_provenances

