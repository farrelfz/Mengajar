"""
Claim Extraction: Heuristic and rule-based extraction of atomic semantic claims from blueprints and text.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any
from app.blueprints.content import ContentBlueprint
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.grounding.contracts import Claim, ClaimType, GroundingStatus


class ClaimExtractor(ABC):
    @abstractmethod
    def extract_claims(self, blueprint: SemanticMaterialBlueprint | ContentBlueprint | str, domain: str = "general") -> list[Claim]:
        pass


class HeuristicClaimExtractor(ClaimExtractor):
    """Deterministic extractor parsing concepts, formulas, facts, and assertions into typed claims."""

    def extract_claims(self, blueprint: SemanticMaterialBlueprint | ContentBlueprint | str, domain: str = "general") -> list[Claim]:
        claims: list[Claim] = []

        if isinstance(blueprint, SemanticMaterialBlueprint):
            content = blueprint.content
            return self._extract_from_content_blueprint(content, domain)
        elif isinstance(blueprint, ContentBlueprint):
            return self._extract_from_content_blueprint(blueprint, domain)
        elif isinstance(blueprint, str):
            return self._extract_from_text(blueprint, domain)

        return claims

    def _extract_from_content_blueprint(self, content: ContentBlueprint, domain: str) -> list[Claim]:
        claims: list[Claim] = []
        dom = content.metadata.domain.value if hasattr(content.metadata.domain, "value") else str(content.metadata.domain)

        # 1. Extract definitions & concepts
        for c in content.concepts:
            claims.append(
                Claim(
                    claim_id=f"claim_concept_{c.id}",
                    content=f"{c.name}: {c.formal_definition}",
                    claim_type=ClaimType.DEFINITIONAL,
                    importance=1.0,
                    source_location=f"concept_{c.id}",
                    domain=dom,
                    requires_grounding=True,
                    grounding_status=GroundingStatus.UNGROUNDED,
                )
            )
            if c.formula:
                claims.append(
                    Claim(
                        claim_id=f"claim_formula_{c.id}",
                        content=f"Equation for {c.name}: {c.formula}",
                        claim_type=ClaimType.QUANTITATIVE,
                        importance=1.0,
                        source_location=f"concept_{c.id}",
                        domain=dom,
                        requires_grounding=True,
                        grounding_status=GroundingStatus.UNGROUNDED,
                    )
                )

        # 2. Extract facts
        for f in content.facts:
            claims.append(
                Claim(
                    claim_id=f"claim_fact_{f.id}",
                    content=f.statement,
                    claim_type=ClaimType.FACTUAL,
                    importance=0.8,
                    source_location=f"fact_{f.id}",
                    domain=dom,
                    requires_grounding=True,
                    grounding_status=GroundingStatus.UNGROUNDED,
                )
            )

        # 3. Extract worked examples / principles
        for we in content.worked_examples:
            for pr in we.principles_used:
                claims.append(
                    Claim(
                        claim_id=f"claim_we_{we.id}_{hash(pr) % 10000}",
                        content=pr,
                        claim_type=ClaimType.CAUSAL if "cause" in pr.lower() or "depends" in pr.lower() else ClaimType.FACTUAL,
                        importance=0.7,
                        source_location=f"we_{we.id}",
                        domain=dom,
                        requires_grounding=True,
                        grounding_status=GroundingStatus.UNGROUNDED,
                    )
                )

        return claims

    def _extract_from_text(self, text: str, domain: str) -> list[Claim]:
        claims: list[Claim] = []
        sentences = [s.strip() for s in re.split(r"[.\n]+", text) if len(s.strip()) > 5]

        for idx, s in enumerate(sentences):
            s_lower = s.lower()
            # Check if decorative statement
            if s_lower.startswith("let's") or s_lower.startswith("welcome") or s_lower.startswith("hello") or "explore" in s_lower and len(s.split()) < 5:
                claims.append(
                    Claim(
                        claim_id=f"claim_text_{idx}",
                        content=s,
                        claim_type=ClaimType.PEDAGOGICAL,
                        importance=0.1,
                        domain=domain,
                        requires_grounding=False,
                        grounding_status=GroundingStatus.NOT_REQUIRED,
                    )
                )
                continue

            # Classify type
            if "=" in s or "tau" in s_lower or "sin(" in s_lower or re.search(r"\d+\s*(m/s|kg|n|n\*m)", s_lower):
                c_type = ClaimType.QUANTITATIVE
            elif "is defined as" in s_lower or "refers to" in s_lower or "means" in s_lower or ":" in s:
                c_type = ClaimType.DEFINITIONAL
            elif "because" in s_lower or "causes" in s_lower or "increases when" in s_lower or "depends on" in s_lower:
                c_type = ClaimType.CAUSAL
            else:
                c_type = ClaimType.FACTUAL

            claims.append(
                Claim(
                    claim_id=f"claim_text_{idx}",
                    content=s,
                    claim_type=c_type,
                    importance=0.9 if c_type in [ClaimType.DEFINITIONAL, ClaimType.QUANTITATIVE] else 0.7,
                    domain=domain,
                    requires_grounding=True,
                    grounding_status=GroundingStatus.UNGROUNDED,
                )
            )

        return claims
