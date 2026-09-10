"""
Universal Document Intelligence System V5 — Benchmark Corpus Registry.

Phase 4.1: Centralized registry discovering, classifying, and validating
the extended benchmark corpus with immutability verification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from app.benchmarking.contracts import BenchmarkFixtureMetadata
from app.benchmarking.fixture_metadata import FixtureMetadataAnalyzer
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit

logger = logging.getLogger("benchmarking.corpus_registry")


class BenchmarkCorpusRegistry:
    """Authoritative registry for benchmark fixtures across all categories and splits."""

    _default_instance: Optional[BenchmarkCorpusRegistry] = None

    def __init__(self) -> None:
        self._fixtures: Dict[str, BenchmarkFixtureMetadata] = {}

    @classmethod
    def get_default(cls) -> BenchmarkCorpusRegistry:
        if cls._default_instance is None:
            reg = cls()
            cls._default_instance = reg
        return cls._default_instance

    @classmethod
    def reset_default(cls) -> None:
        cls._default_instance = None

    def register(self, metadata: BenchmarkFixtureMetadata) -> None:
        """Registers a benchmark fixture metadata record."""
        self._fixtures[metadata.fixture_id] = metadata

    def get(self, fixture_id: str) -> Optional[BenchmarkFixtureMetadata]:
        return self._fixtures.get(fixture_id)

    def get_all(self) -> List[BenchmarkFixtureMetadata]:
        return list(self._fixtures.values())

    def get_by_category(self, category: CorpusCategory) -> List[BenchmarkFixtureMetadata]:
        return [f for f in self._fixtures.values() if f.corpus_category == category]

    def get_by_split(self, split: CorpusSplit) -> List[BenchmarkFixtureMetadata]:
        return [f for f in self._fixtures.values() if f.split == split]

    def count(self) -> int:
        return len(self._fixtures)

    def scan_directory(self, corpus_dir: Path | str) -> int:
        """Scans a directory for .md fixtures and their companion .meta.json files."""
        p = Path(corpus_dir)
        if not p.exists() or not p.is_dir():
            return 0

        count = 0
        for md_file in sorted(p.glob("*.md")):
            meta = FixtureMetadataAnalyzer.load_or_infer_metadata(md_file)
            self.register(meta)
            count += 1
        return count

    def verify_immutability(self) -> Tuple[bool, List[str]]:
        """Verifies that no benchmark fixture source file has been modified in place."""
        mutated: List[str] = []
        for fid, meta in self._fixtures.items():
            fpath = Path(meta.source_path)
            if not fpath.exists():
                mutated.append(f"{fid} (missing file: {meta.source_path})")
                continue
            curr_hash = BenchmarkFixtureMetadata.compute_hash(fpath.read_text(encoding="utf-8"))
            if meta.content_hash and curr_hash != meta.content_hash:
                mutated.append(f"{fid} (hash mismatch: expected {meta.content_hash}, got {curr_hash})")

        return len(mutated) == 0, mutated
