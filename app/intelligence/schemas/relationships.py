"""
Universal Knowledge Core — Knowledge Relationship & Provenance Schemas.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    # Universal Knowledge Graph relations
    PREREQUISITE_OF = "prereq_of"
    EXPLAINED_BY = "explained_by"
    SUPPORTED_BY = "supported_by"
    MEASURED_BY = "measured_by"
    DEMONSTRATED_BY = "demonstrated_by"
    CONTRASTED_WITH = "contrasted_with"
    CAUSES = "causes"
    DERIVES_FROM = "derives_from"
    REFUTES = "refutes"

    # Semantic / Legacy relations
    ADDRESSES = "addresses"
    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"
    PRODUCED_BY = "produced_by"
    ANALYZED_BY = "analyzed_by"
    INTERPRETS = "interprets"
    COMPARES_WITH = "compares_with"
    CONNECTED_TO = "connected_to"
    ANSWERS = "answers"
    CONCLUDES_FROM = "concludes_from"
    BASED_ON = "based_on"
    RECOMMENDS = "recommends"
    EXTENDS = "extends"
    LIMITS = "limits"


class RelationshipOrigin(str, Enum):
    EXPLICIT_SOURCE = "explicit_source"    # Declared directly in source text
    DETERMINISTIC_RULE = "rule_deduced"    # Deduced via deterministic heuristic (e.g. section nesting)
    AI_INFERRED = "ai_inferred"            # Inferred via Selective AI Gateway


class RelationshipEvidence(BaseModel):
    origin: RelationshipOrigin
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_snippet: Optional[str] = None
    rule_name: Optional[str] = None


class KnowledgeRelationship(BaseModel):
    """Directed edge connecting two KnowledgeUnits in the UniversalKnowledgeGraph."""
    source_unit_id: str
    target_unit_id: str
    relationship: RelationshipType = RelationshipType.EXPLAINED_BY
    evidence: RelationshipEvidence = Field(default_factory=lambda: RelationshipEvidence(origin=RelationshipOrigin.DETERMINISTIC_RULE))
    relationship_id: Optional[str] = None
    weight: Optional[float] = None

    def __init__(self, **data: Any) -> None:
        if "relationship_type" in data and "relationship" not in data:
            rt = str(data["relationship_type"]).lower()
            if "explain" in rt:
                data["relationship"] = RelationshipType.EXPLAINED_BY
            elif "support" in rt:
                data["relationship"] = RelationshipType.SUPPORTED_BY
            elif "cause" in rt:
                data["relationship"] = RelationshipType.CAUSES
            else:
                data["relationship"] = RelationshipType.EXPLAINED_BY
        if "evidence" not in data:
            conf = data.get("weight", 1.0)
            data["evidence"] = RelationshipEvidence(origin=RelationshipOrigin.DETERMINISTIC_RULE, confidence=conf)
        super().__init__(**data)
