"""
Universal Document Intelligence System V5 — Corpus Coverage & Representativeness Analyzer.

Phase 5: Analyzes Golden Corpus domain diversity, pedagogical modes, content structures,
difficulty distributions, and artifact coverage. Flags representation gaps without fabricating content.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set
from pydantic import BaseModel, ConfigDict, Field

from app.benchmarking.golden_contracts import GoldenCorpus


class CorpusCoverageReport(BaseModel):
    """Detailed diagnostic report on corpus domain and difficulty distribution."""
    model_config = ConfigDict(frozen=True)

    corpus_id: str
    total_cases: int
    total_artifact_references: int
    domain_distribution: Dict[str, int] = Field(default_factory=dict)
    difficulty_distribution: Dict[str, int] = Field(default_factory=dict)
    artifact_coverage: Dict[str, int] = Field(default_factory=dict)
    underrepresented_domains: List[str] = Field(default_factory=list)
    missing_difficulties: List[str] = Field(default_factory=list)
    missing_artifact_types: List[str] = Field(default_factory=list)
    concentration_risk: bool = False
    concentration_warning: str = ""
    coverage_score: float = Field(ge=0.0, le=1.0)


class CorpusCoverageAnalyzer:
    """Evaluates the epistemic representativeness and balance of the Golden Benchmark Corpus."""

    CANONICAL_DOMAINS: Set[str] = {
        "EXPERIMENTAL_PHENOMENA",
        "TEACHING_CONCEPTS",
        "SCIENTIFIC_RESEARCH",
        "DENSE_CURRICULUM",
    }

    CANONICAL_DIFFICULTIES: Set[str] = {
        "BASIC",
        "INTERMEDIATE",
        "ADVANCED",
        "ADVERSARIAL",
    }

    CANONICAL_ARTIFACT_TYPES: Set[str] = {
        "PRESENTATION",
        "HANDOUT",
        "WORKSHEET",
        "SCIENTIFIC_DOCUMENT",
    }

    @classmethod
    def analyze(cls, corpus: GoldenCorpus) -> CorpusCoverageReport:
        """Analyzes coverage across all dimensions of the given GoldenCorpus."""
        cases = list(corpus.cases.values())
        total_cases = len(cases)

        domain_dist: Dict[str, int] = {}
        diff_dist: Dict[str, int] = {}
        art_dist: Dict[str, int] = {at: 0 for at in cls.CANONICAL_ARTIFACT_TYPES}

        total_refs = 0

        for c in cases:
            dom = getattr(c, "taxonomy_category", None) or c.corpus_category
            domain_dist[dom] = domain_dist.get(dom, 0) + 1

            diff = c.difficulty_level.upper()
            diff_dist[diff] = diff_dist.get(diff, 0) + 1

            for at in c.references.keys():
                art_dist[at] = art_dist.get(at, 0) + 1
                total_refs += 1

        underrepresented = [
            dom for dom in cls.CANONICAL_DOMAINS if domain_dist.get(dom, 0) < 1
        ]
        missing_diffs = [
            diff for diff in cls.CANONICAL_DIFFICULTIES if diff_dist.get(diff, 0) < 1
        ]
        missing_arts = [
            at for at in cls.CANONICAL_ARTIFACT_TYPES if art_dist.get(at, 0) < 1
        ]

        # Concentration Risk: if > 70% of cases are in one domain
        concentration_risk = False
        concentration_warning = ""
        if total_cases > 0:
            max_dom_count = max(domain_dist.values()) if domain_dist else 0
            if (max_dom_count / total_cases) > 0.70 and total_cases >= 3:
                concentration_risk = True
                dominant_dom = [d for d, cnt in domain_dist.items() if cnt == max_dom_count][0]
                concentration_warning = (
                    f"Concentration risk: {dominant_dom} represents "
                    f"{(max_dom_count/total_cases)*100:.1f}% of all corpus cases."
                )

        # Coverage Score calculation
        domain_coverage = (len(cls.CANONICAL_DOMAINS) - len(underrepresented)) / max(1, len(cls.CANONICAL_DOMAINS))
        artifact_coverage = (len(cls.CANONICAL_ARTIFACT_TYPES) - len(missing_arts)) / max(1, len(cls.CANONICAL_ARTIFACT_TYPES))
        difficulty_coverage = (len(cls.CANONICAL_DIFFICULTIES) - len(missing_diffs)) / max(1, len(cls.CANONICAL_DIFFICULTIES))

        coverage_score = round(
            (domain_coverage * 0.4) + (artifact_coverage * 0.4) + (difficulty_coverage * 0.2), 3
        )

        return CorpusCoverageReport(
            corpus_id=corpus.corpus_id,
            total_cases=total_cases,
            total_artifact_references=total_refs,
            domain_distribution=domain_dist,
            difficulty_distribution=diff_dist,
            artifact_coverage=art_dist,
            underrepresented_domains=underrepresented,
            missing_difficulties=missing_diffs,
            missing_artifact_types=missing_arts,
            concentration_risk=concentration_risk,
            concentration_warning=concentration_warning,
            coverage_score=coverage_score,
        )
