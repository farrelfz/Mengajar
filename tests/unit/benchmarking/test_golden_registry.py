"""
Tests for Phase 2 Golden Corpus Registry, Loader, Validator, and Versioning.
"""

import os
import json
import pytest
from pathlib import Path

from app.benchmarking.golden_contracts import (
    GoldenCorpus,
    GoldenCorpusVersion,
    GoldenCase,
    GoldenArtifactReference,
    CertificationStatus,
)
from app.benchmarking.golden_registry import (
    GoldenCorpusRegistry,
    GoldenCorpusLoader,
    GoldenCorpusValidator,
    GoldenCorpusVersionManager,
)

@pytest.fixture
def sample_corpus():
    v1 = GoldenCorpusVersion(
        version="1.0.0",
        change_summary="Initial version"
    )
    
    ref = GoldenArtifactReference(
        artifact_id="art-1",
        artifact_type="PRESENTATION",
        source_case_id="case-1",
        artifact_file_reference="dummy.pdf",
        review_status=CertificationStatus.CERTIFIED
    )
    
    case = GoldenCase(
        case_id="case-1",
        source_path="source.md",
        source_hash="abcd",
        corpus_category="CONCEPT",
        difficulty_level="INTERMEDIATE",
        references={"art-1": ref}
    )
    
    return GoldenCorpus(
        corpus_id="corpus-physics",
        current_version=v1,
        cases={"case-1": case}
    )

def test_registry_registration(sample_corpus):
    registry = GoldenCorpusRegistry()
    registry.register(sample_corpus)
    
    retrieved = registry.get("corpus-physics")
    assert retrieved is not None
    assert retrieved.corpus_id == "corpus-physics"
    assert "corpus-physics" in registry.list_corpora()

def test_registry_singleton():
    GoldenCorpusRegistry.reset_default()
    r1 = GoldenCorpusRegistry.get_default()
    r2 = GoldenCorpusRegistry.get_default()
    assert r1 is r2

def test_loader_save_and_load(tmp_path, sample_corpus):
    file_path = tmp_path / "test_corpus.json"
    
    # Save
    GoldenCorpusLoader.save_to_file(sample_corpus, file_path)
    assert file_path.exists()
    
    # Load
    loaded_corpus = GoldenCorpusLoader.load_from_file(file_path)
    assert loaded_corpus.corpus_id == sample_corpus.corpus_id
    assert "case-1" in loaded_corpus.cases

def test_validator_valid_corpus(sample_corpus):
    is_valid, issues = GoldenCorpusValidator.validate(sample_corpus)
    assert is_valid is True
    assert len(issues) == 0

def test_validator_detects_draft(sample_corpus):
    # Mutate to DRAFT
    corpus_dict = sample_corpus.model_dump()
    corpus_dict["cases"]["case-1"]["references"]["art-1"]["review_status"] = CertificationStatus.DRAFT.value
    draft_corpus = GoldenCorpus(**corpus_dict)
    
    is_valid, issues = GoldenCorpusValidator.validate(draft_corpus)
    # It still passes validation conceptually, but raises an issue warning
    assert is_valid is False
    assert any("DRAFT status" in issue for issue in issues)

def test_validator_detects_mismatch(sample_corpus):
    corpus_dict = sample_corpus.model_dump()
    # Create a mismatch in source_case_id
    corpus_dict["cases"]["case-1"]["references"]["art-1"]["source_case_id"] = "wrong-case-id"
    broken_corpus = GoldenCorpus(**corpus_dict)
    
    is_valid, issues = GoldenCorpusValidator.validate(broken_corpus)
    assert is_valid is False
    assert any("not matching" in issue for issue in issues)

def test_version_manager_bump(sample_corpus):
    new_corpus = GoldenCorpusVersionManager.create_new_version(
        corpus=sample_corpus,
        new_version_str="1.1.0",
        change_summary="Added Handout",
        created_by="Admin"
    )
    
    assert new_corpus.current_version.version == "1.1.0"
    assert new_corpus.current_version.parent_version == "1.0.0"
    assert new_corpus.current_version.change_summary == "Added Handout"
    assert new_corpus.current_version.created_by == "Admin"
    
def test_version_manager_same_version_fails(sample_corpus):
    with pytest.raises(ValueError):
        GoldenCorpusVersionManager.create_new_version(
            corpus=sample_corpus,
            new_version_str="1.0.0",
            change_summary="Duplicate version bump"
        )
