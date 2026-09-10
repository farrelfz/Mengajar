"""
Universal Document Intelligence System V5 — Benchmark Fixture Metadata Parser.

Phase 4.1: Analyzes and validates machine-readable fixture metadata and computes
structural signatures directly from raw Markdown content.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

from app.benchmarking.contracts import (
    BenchmarkFixtureMetadata,
    StructuralSignature,
)
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit

logger = logging.getLogger("benchmarking.metadata")


class FixtureMetadataAnalyzer:
    """Extracts structural signatures from raw markdown and validates metadata descriptors."""

    @classmethod
    def analyze_source_structure(cls, raw_content: str) -> StructuralSignature:
        """Extracts quantifiable structural metrics from raw markdown."""
        lines = raw_content.splitlines()
        token_count = len(re.findall(r"\w+", raw_content))
        character_count = len(raw_content)

        # Headings
        headings = [line for line in lines if line.strip().startswith("#")]
        max_depth = 1
        for h in headings:
            match = re.match(r"^(#+)", h.strip())
            if match:
                max_depth = max(max_depth, len(match.group(1)))
        section_count = max(1, len(headings))

        # Tables (markdown table delimiter line)
        table_count = sum(1 for line in lines if re.match(r"^\|?\s*[-:]{3,}\s*\|", line.strip()))

        # Formulas ($...$ or $$...$$)
        formula_matches = re.findall(r"\$\$?[^\$]+\$\$?", raw_content)
        formula_count = len(formula_matches)

        # Code blocks
        has_code_blocks = "```" in raw_content

        # Mixed languages (simple heuristic for common Indonesian + English physics terms)
        id_terms = {"adalah", "dengan", "dan", "untuk", "pada", "oleh", "suhu", "kecepatan"}
        en_terms = {"the", "and", "with", "velocity", "temperature", "equation", "setup"}
        words_lower = set(re.findall(r"\b[a-z]{3,}\b", raw_content.lower()))
        has_mixed = bool((words_lower & id_terms) and (words_lower & en_terms))

        # Card estimate: roughly sections or bold bullet clusters
        card_est = max(section_count, len(re.findall(r"^\s*[-*]\s+\*\*", raw_content, re.M)))

        return StructuralSignature(
            token_count=token_count,
            character_count=character_count,
            section_count=section_count,
            max_heading_depth=min(6, max_depth),
            table_count=table_count,
            formula_count=formula_count,
            has_code_blocks=has_code_blocks,
            has_mixed_languages=has_mixed,
            card_estimate=card_est,
        )

    @classmethod
    def load_or_infer_metadata(
        cls,
        source_path: Path | str,
        default_category: CorpusCategory = CorpusCategory.CONCEPT_HEAVY,
        default_split: CorpusSplit = CorpusSplit.UNSEEN_GENERALIZATION,
    ) -> BenchmarkFixtureMetadata:
        """Loads existing .meta.json or infers metadata from source structure."""
        p = Path(source_path)
        meta_path = p.with_suffix(".meta.json")
        raw_text = p.read_text(encoding="utf-8") if p.exists() else ""
        content_hash = BenchmarkFixtureMetadata.compute_hash(raw_text)

        if meta_path.exists():
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                # Ensure path and hash are synchronized
                data["source_path"] = str(p.resolve())
                data["content_hash"] = content_hash
                return BenchmarkFixtureMetadata(**data)
            except Exception as ex:
                logger.warning("Failed parsing %s: %s. Falling back to inference.", meta_path, ex)

        # Inference fallback
        sig = cls.analyze_source_structure(raw_text)
        return BenchmarkFixtureMetadata(
            fixture_id=p.stem,
            source_path=str(p.resolve()),
            corpus_category=default_category,
            domain="General Physics / Education",
            difficulty_level="INTERMEDIATE",
            structural_signature=sig,
            semantic_density=min(1.0, sig.token_count / 1500.0),
            formula_density=min(1.0, sig.formula_count / 10.0),
            table_density=min(1.0, sig.table_count / 5.0),
            narrative_complexity=0.5,
            inquiry_complexity=0.5,
            evidence_complexity=0.5,
            expected_artifact_types=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"),
            split=default_split,
            provenance="Inferred by FixtureMetadataAnalyzer",
            content_hash=content_hash,
        )

    @classmethod
    def save_metadata(cls, meta: BenchmarkFixtureMetadata, output_path: Path | str) -> None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(meta.model_dump_json(indent=2), encoding="utf-8")
