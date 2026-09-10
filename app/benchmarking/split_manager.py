"""
Universal Document Intelligence System V5 — Corpus Split Manager.

Phase 4.1: Deterministically partitions the benchmark corpus into Training Reference,
Validation Reference, Unseen Generalization, and Adversarial sets, and persists the corpus manifest.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.benchmarking.contracts import BenchmarkFixtureMetadata
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit

logger = logging.getLogger("benchmarking.split_manager")

DEFAULT_CANONICAL_SPLITS: Dict[str, CorpusSplit] = {
    # Golden Training / Validation References (Known)
    "oobleck_experiment": CorpusSplit.TRAINING_REFERENCE,
    "hand_fire_full": CorpusSplit.TRAINING_REFERENCE,
    "experiment_oobleck": CorpusSplit.TRAINING_REFERENCE,
    "experiment_hand_fire": CorpusSplit.TRAINING_REFERENCE,
    "01_oobleck_experiment": CorpusSplit.TRAINING_REFERENCE,
    "04_hand_fire": CorpusSplit.VALIDATION_REFERENCE,
    "02_dinamika_rotasi": CorpusSplit.VALIDATION_REFERENCE,
    "03_gerak_melingkar": CorpusSplit.VALIDATION_REFERENCE,
    "05_short_concept": CorpusSplit.VALIDATION_REFERENCE,
    "06_long_material": CorpusSplit.VALIDATION_REFERENCE,
    "07_data_heavy_research": CorpusSplit.VALIDATION_REFERENCE,


    # New Unseen Generalization Fixtures
    "concept_rotational_dynamics": CorpusSplit.UNSEEN_GENERALIZATION,
    "concept_harmonic_motion": CorpusSplit.UNSEEN_GENERALIZATION,
    "concept_thermodynamics_carnot": CorpusSplit.UNSEEN_GENERALIZATION,
    "experiment_pendulum_investigation": CorpusSplit.UNSEEN_GENERALIZATION,
    "experiment_inclined_plane": CorpusSplit.UNSEEN_GENERALIZATION,
    "narrative_galileo_falling_bodies": CorpusSplit.UNSEEN_GENERALIZATION,
    "narrative_penicillin_discovery": CorpusSplit.UNSEEN_GENERALIZATION,
    "scientific_kti_climate_microalgae": CorpusSplit.UNSEEN_GENERALIZATION,
    "scientific_superconductivity": CorpusSplit.UNSEEN_GENERALIZATION,

    # Adversarial Pathological Fixtures
    "path_dense_cluster": CorpusSplit.ADVERSARIAL,
    "path_sparse_stub": CorpusSplit.ADVERSARIAL,
    "path_deep_hierarchy": CorpusSplit.ADVERSARIAL,
    "path_repetition_loop": CorpusSplit.ADVERSARIAL,
    "path_formula_heavy": CorpusSplit.ADVERSARIAL,
}


class CorpusSplitManager:
    """Manages deterministic dataset splitting and corpus manifest generation."""

    def __init__(self, registry: Optional[BenchmarkCorpusRegistry] = None) -> None:
        self.registry = registry or BenchmarkCorpusRegistry.get_default()

    def assign_canonical_splits(self) -> None:
        """Applies deterministic canonical split assignments to all registered fixtures."""
        for fid, meta in list(self.registry._fixtures.items()):
            target_split = DEFAULT_CANONICAL_SPLITS.get(fid)
            if target_split is None:
                if meta.corpus_category == CorpusCategory.PATHOLOGICAL:
                    target_split = CorpusSplit.ADVERSARIAL
                else:
                    target_split = CorpusSplit.UNSEEN_GENERALIZATION
            
            # Re-create frozen model with updated split
            updated = meta.model_copy(update={"split": target_split})
            self.registry.register(updated)

    def generate_manifest(self, output_path: Optional[Path | str] = None) -> Dict[str, Any]:
        """Generates a comprehensive corpus manifest dictionary and optionally persists it."""
        all_fixtures = self.registry.get_all()
        by_split: Dict[str, List[Dict[str, Any]]] = {
            split.value: [] for split in CorpusSplit
        }
        by_category: Dict[str, List[str]] = {
            cat.value: [] for cat in CorpusCategory
        }

        for f in all_fixtures:
            dumped = f.model_dump()
            by_split[f.split.value].append(dumped)
            by_category[f.corpus_category.value].append(f.fixture_id)

        manifest = {
            "total_fixtures": len(all_fixtures),
            "distribution_by_split": {k: len(v) for k, v in by_split.items()},
            "distribution_by_category": {k: len(v) for k, v in by_category.items()},
            "fixtures_by_split": by_split,
            "fixtures_by_category": by_category,
        }

        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            logger.info("Saved corpus manifest to %s", p)

        return manifest
