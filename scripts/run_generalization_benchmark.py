"""
Universal Document Intelligence System V5 — Generalization Benchmark Runner Script.

Phase 4.1: Executes the extended benchmark corpus across Training Reference,
Validation Reference, Unseen Generalization, and Adversarial splits.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
import sys

from app.benchmarking.benchmark_runner import BenchmarkGeneralizationRunner
from app.benchmarking.corpus_registry import BenchmarkCorpusRegistry
from app.benchmarking.split_manager import CorpusSplitManager
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("benchmark.script")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 4.1 Generalization Benchmark Runner")
    parser.add_argument("--unseen-only", action="store_true", help="Run only unseen generalization fixtures")
    parser.add_argument("--pathological-only", action="store_true", help="Run only pathological stress fixtures")
    parser.add_argument("--category", choices=[c.value for c in CorpusCategory], help="Filter by corpus category")
    parser.add_argument("--artifact-type", choices=["PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"], help="Filter by format")
    parser.add_argument("--output-dir", default="outputs/benchmarks/phase_4_1", help="Output directory")

    args = parser.parse_args()

    reg = BenchmarkCorpusRegistry.get_default()
    reg.scan_directory("tests/fixtures/benchmark_corpus")
    sm = CorpusSplitManager(reg)
    sm.assign_canonical_splits()
    sm.generate_manifest(Path(args.output_dir) / "corpus_manifest.json")

    splits = None
    if args.unseen_only:
        splits = [CorpusSplit.UNSEEN_GENERALIZATION]
    elif args.pathological_only:
        splits = [CorpusSplit.ADVERSARIAL]

    categories = None
    if args.category:
        categories = [CorpusCategory(args.category)]

    artifact_types = [args.artifact_type] if args.artifact_type else None

    runner = BenchmarkGeneralizationRunner(registry=reg, output_dir=args.output_dir)
    outcomes, metrics, envelopes = await runner.run_suite(
        splits=splits,
        categories=categories,
        artifact_types=artifact_types,
    )

    logger.info("==================================================")
    logger.info("BENCHMARK GENERALIZATION RUN COMPLETE")
    logger.info("Total Jobs: %d", metrics.total_jobs)
    logger.info("Known Mean Score: %.3f | Unseen Mean Score: %.3f", metrics.known_corpus_mean_score, metrics.unseen_corpus_mean_score)
    logger.info("Generalization Gap: %.3f", metrics.generalization_gap)
    logger.info("Repair Generalization Rate (RGR): %.1f%%", metrics.repair_generalization_rate * 100)
    logger.info("Generalization Warning: %s", metrics.generalization_warning)
    logger.info("==================================================")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
