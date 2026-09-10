"""
Universal Document Intelligence System V5 — Golden Corpus Registry & Versioning.

Phase 5: Golden Corpus Registry handling loading, validation, and versioning
of the objective reference artifacts used for benchmarking.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import ValidationError

from app.benchmarking.golden_contracts import (
    GoldenCorpus,
    GoldenCorpusVersion,
    CertificationStatus,
)

logger = logging.getLogger("benchmarking.golden_registry")

class GoldenCorpusRegistry:
    """Authoritative registry for managing and versioning the Golden Corpus."""

    _default_instance: Optional[GoldenCorpusRegistry] = None

    def __init__(self) -> None:
        self._corpora: Dict[str, GoldenCorpus] = {}

    @classmethod
    def get_default(cls) -> GoldenCorpusRegistry:
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    @classmethod
    def reset_default(cls) -> None:
        cls._default_instance = None

    def register(self, corpus: GoldenCorpus) -> None:
        """Registers a Golden Corpus in memory."""
        self._corpora[corpus.corpus_id] = corpus

    def get(self, corpus_id: str) -> Optional[GoldenCorpus]:
        return self._corpora.get(corpus_id)

    def list_corpora(self) -> List[str]:
        return list(self._corpora.keys())

class GoldenCorpusLoader:
    """Loads and serializes the Golden Corpus to and from disk."""
    
    @classmethod
    def load_from_file(cls, filepath: Path | str) -> GoldenCorpus:
        """Loads a Golden Corpus from a JSON file."""
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"Golden Corpus file not found: {p}")
        
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return GoldenCorpus(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {p}: {e}")
        except ValidationError as e:
            raise ValueError(f"Golden Corpus validation failed for {p}: {e}")
            
    @classmethod
    def save_to_file(cls, corpus: GoldenCorpus, filepath: Path | str) -> None:
        """Saves a Golden Corpus to a JSON file."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(corpus.model_dump_json(indent=2), encoding="utf-8")

class GoldenCorpusValidator:
    """Validates the logical consistency of a Golden Corpus."""
    
    @classmethod
    def validate(cls, corpus: GoldenCorpus) -> Tuple[bool, List[str]]:
        """
        Validates internal consistency:
        - Ensures reference cases point to existing case IDs.
        - Checks for draft references in certified corpora.
        - Verifies versioning structure.
        """
        issues = []
        
        if not corpus.corpus_id:
            issues.append("Corpus is missing corpus_id.")
            
        if not corpus.current_version or not corpus.current_version.version:
            issues.append("Corpus is missing a valid current_version.")
            
        for case_id, case in corpus.cases.items():
            if case.case_id != case_id:
                issues.append(f"Case ID mismatch: dictionary key {case_id} != case_id {case.case_id}")
                
            for ref_id, ref in case.references.items():
                if ref.source_case_id != case_id:
                    issues.append(f"Reference {ref_id} has source_case_id {ref.source_case_id} not matching {case_id}")
                if ref.review_status == CertificationStatus.DRAFT:
                    issues.append(f"Reference {ref_id} is in DRAFT status, which may be uncertified for production benchmarks.")
                    
        return len(issues) == 0, issues

class GoldenCorpusVersionManager:
    """Handles the immutable versioning of the Golden Corpus."""
    
    @classmethod
    def create_new_version(
        cls, 
        corpus: GoldenCorpus, 
        new_version_str: str, 
        change_summary: str,
        created_by: str = "System"
    ) -> GoldenCorpus:
        """
        Creates a new version of the Golden Corpus.
        The parent version points to the corpus's current version.
        """
        if new_version_str == corpus.current_version.version:
            raise ValueError(f"New version {new_version_str} must differ from current version.")
            
        new_version = GoldenCorpusVersion(
            version=new_version_str,
            parent_version=corpus.current_version.version,
            change_summary=change_summary,
            created_by=created_by
        )
        
        # We model a shallow copy/rebuild to enforce immutability of the outer record
        updated_dict = corpus.model_dump()
        updated_dict["current_version"] = new_version.model_dump()
        
        return GoldenCorpus(**updated_dict)
