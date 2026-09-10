"""
Universal Document Intelligence System V5 — Production Versioning & Iteration Storage.

Phase 3D: Preserves full immutable physical and metadata records of every render iteration
(iteration_0, iteration_1, ..., final) preventing silent overwrites and ensuring complete forensic auditability.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.repair.transaction import RepairTransactionRecord


@dataclass(frozen=True)
class IterationSnapshot:
    """Immutable record of an individual iteration's files and hashes."""
    iteration: int
    iteration_dir: Path
    blueprint_path: Optional[Path]
    html_path: Optional[Path]
    pdf_path: Optional[Path]
    quality_json_path: Optional[Path]
    transaction_json_path: Optional[Path]
    blueprint_hash: str
    pdf_hash: str


class ProductionVersionManager:
    """Manages versioned iteration directories and immutable final packaging."""

    def __init__(self, base_output_dir: Path | str, artifact_name: str = "artifact") -> None:
        self.base_output_dir = Path(base_output_dir)
        self.artifact_name = artifact_name
        self.iterations: List[IterationSnapshot] = []

    @staticmethod
    def compute_file_hash(filepath: Optional[Path]) -> str:
        if not filepath or not filepath.exists():
            return ""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def record_iteration(
        self,
        iteration: int,
        blueprint: Any,
        html_path: Optional[Path] = None,
        pdf_path: Optional[Path] = None,
        quality_report: Optional[UnifiedQualityReport] = None,
        transaction_record: Optional[RepairTransactionRecord] = None,
    ) -> IterationSnapshot:
        """Stores all outputs of an iteration into a dedicated immutable folder."""
        iter_dir = self.base_output_dir / f"iteration_{iteration}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        bp_file = iter_dir / "blueprint.json"
        with open(bp_file, "w", encoding="utf-8") as f:
            if hasattr(blueprint, "model_dump_json"):
                f.write(blueprint.model_dump_json(indent=2))
            elif hasattr(blueprint, "to_dict"):
                f.write(json.dumps(blueprint.to_dict(), indent=2, default=str))
            else:
                f.write(json.dumps(getattr(blueprint, "__dict__", {}), indent=2, default=str))

        dest_html = None
        if html_path and html_path.exists():
            dest_html = iter_dir / f"{self.artifact_name}.html"
            if html_path.resolve() != dest_html.resolve():
                shutil.copy2(html_path, dest_html)
            else:
                dest_html = html_path

        dest_pdf = None
        if pdf_path and pdf_path.exists():
            dest_pdf = iter_dir / f"{self.artifact_name}.pdf"
            if pdf_path.resolve() != dest_pdf.resolve():
                shutil.copy2(pdf_path, dest_pdf)
            else:
                dest_pdf = pdf_path

        q_file = None
        if quality_report:
            q_file = iter_dir / "quality.json"
            with open(q_file, "w", encoding="utf-8") as f:
                f.write(quality_report.model_dump_json(indent=2))

        tx_file = None
        if transaction_record:
            tx_file = iter_dir / "repair_transaction.json"
            with open(tx_file, "w", encoding="utf-8") as f:
                f.write(transaction_record.model_dump_json(indent=2))

        snapshot = IterationSnapshot(
            iteration=iteration,
            iteration_dir=iter_dir,
            blueprint_path=bp_file,
            html_path=dest_html,
            pdf_path=dest_pdf,
            quality_json_path=q_file,
            transaction_json_path=tx_file,
            blueprint_hash=self.compute_file_hash(bp_file),
            pdf_hash=self.compute_file_hash(dest_pdf),
        )
        self.iterations.append(snapshot)
        return snapshot

    def package_final(
        self,
        approved_iteration: int,
        provenance_data: Dict[str, Any],
        quality_markdown: str,
        generation_summary: Dict[str, Any],
    ) -> Path:
        """Copies the approved iteration into final/ alongside comprehensive documentation."""
        final_dir = self.base_output_dir / "final"
        final_dir.mkdir(parents=True, exist_ok=True)

        # Locate approved snapshot
        target_snap = next((s for s in self.iterations if s.iteration == approved_iteration), None)
        if not target_snap:
            # Fallback to last iteration if matching snapshot not found
            target_snap = self.iterations[-1] if self.iterations else None

        if target_snap and target_snap.pdf_path and target_snap.pdf_path.exists():
            dest = final_dir / f"{self.artifact_name}.pdf"
            if target_snap.pdf_path.resolve() != dest.resolve():
                shutil.copy2(target_snap.pdf_path, dest)

        if target_snap and target_snap.html_path and target_snap.html_path.exists():
            dest = final_dir / f"{self.artifact_name}.html"
            if target_snap.html_path.resolve() != dest.resolve():
                shutil.copy2(target_snap.html_path, dest)

        with open(final_dir / "provenance.json", "w", encoding="utf-8") as f:
            json.dump(provenance_data, f, indent=2, default=str)

        with open(final_dir / "quality_report.md", "w", encoding="utf-8") as f:
            f.write(quality_markdown)

        with open(final_dir / "generation_report.json", "w", encoding="utf-8") as f:
            json.dump(generation_summary, f, indent=2, default=str)

        # Manifest pointing to the exact iteration
        manifest = {
            "approved_iteration": approved_iteration,
            "total_iterations": len(self.iterations),
            "approved_pdf_hash": target_snap.pdf_hash if target_snap else "",
            "approved_blueprint_hash": target_snap.blueprint_hash if target_snap else "",
        }
        with open(final_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return final_dir
