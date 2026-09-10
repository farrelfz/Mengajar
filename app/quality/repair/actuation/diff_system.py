"""
Universal Document Intelligence System V5 — Transformation Diff System.

Phase 4: Forensics engine generating machine-readable (JSON) and human-readable (Markdown)
before/after diff reports capturing all structural, textual, and spatial mutations.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.actuation.contracts import RepairActuationResult
from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprinter


class TransformationDiffReport(BaseModel):
    """Authoritative representation of physical artifact differences caused by actuation."""
    model_config = ConfigDict(frozen=True)

    actuator_id: str
    artifact_type: str
    iteration: int
    changed_layers: Tuple[str, ...]
    added_elements: Tuple[str, ...]
    modified_elements: Tuple[str, ...]
    removed_elements: Tuple[str, ...]
    unified_diff: str
    fingerprint_delta: Dict[str, Any]
    mutation_cost: float
    rationale: str


class TransformationDiffSystem:
    """Generates comprehensive structural and textual diffs for repair actuations."""

    @classmethod
    def generate_diff(
        cls,
        actuator_result: RepairActuationResult,
        artifact_type: str,
        before_blueprint: Any,
        after_blueprint: Any,
        iteration: int = 1,
    ) -> TransformationDiffReport:
        # String representations
        str_before = json.dumps(
            cls._serialize_bp(before_blueprint), indent=2, sort_keys=True
        )
        str_after = json.dumps(
            cls._serialize_bp(after_blueprint), indent=2, sort_keys=True
        )

        diff_lines = difflib.unified_diff(
            str_before.splitlines(keepends=True),
            str_after.splitlines(keepends=True),
            fromfile=f"blueprint_before_iter_{iteration}.json",
            tofile=f"blueprint_after_iter_{iteration}.json",
        )
        unified_diff_str = "".join(diff_lines)

        # Detect element delta
        before_ids = cls._extract_element_ids(before_blueprint)
        after_ids = cls._extract_element_ids(after_blueprint)

        added = tuple(sorted(set(after_ids) - set(before_ids)))
        removed = tuple(sorted(set(before_ids) - set(after_ids)))
        modified = tuple(sorted(set(actuator_result.changed_element_ids) & set(after_ids)))

        fp_delta: Dict[str, Any] = {}
        if actuator_result.before_fingerprint and actuator_result.after_fingerprint:
            b_fp = actuator_result.before_fingerprint
            a_fp = actuator_result.after_fingerprint
            b_hash = getattr(b_fp, "composite_hash", getattr(b_fp, "fingerprint_hash", ""))
            a_hash = getattr(a_fp, "composite_hash", getattr(a_fp, "fingerprint_hash", ""))
            b_count = len(getattr(b_fp, "component_signatures", {})) or getattr(b_fp, "element_count", 0)
            a_count = len(getattr(a_fp, "component_signatures", {})) or getattr(a_fp, "element_count", 0)
            fp_delta = {
                "hash_changed": b_hash != a_hash,
                "before_hash": b_hash,
                "after_hash": a_hash,
                "elements_count_delta": a_count - b_count,
            }

        return TransformationDiffReport(
            actuator_id=actuator_result.actuator_id,
            artifact_type=artifact_type,
            iteration=iteration,
            changed_layers=tuple(l.name for l in actuator_result.changed_artifact_layers),
            added_elements=added,
            modified_elements=modified,
            removed_elements=removed,
            unified_diff=unified_diff_str,
            fingerprint_delta=fp_delta,
            mutation_cost=actuator_result.mutation_cost,
            rationale=actuator_result.rationale,
        )

    @classmethod
    def write_diff_artifacts(
        cls,
        diff_report: TransformationDiffReport,
        output_dir: Path,
    ) -> Tuple[Path, Path]:
        """Writes transformation_diff.json and transformation_diff.md to output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "transformation_diff.json"
        md_path = output_dir / "transformation_diff.md"

        json_path.write_text(json.dumps(diff_report.model_dump(), indent=2), encoding="utf-8")

        md_content = f"""# Transformation Diff Report — Iteration {diff_report.iteration}

- **Actuator**: `{diff_report.actuator_id}`
- **Artifact Type**: `{diff_report.artifact_type}`
- **Mutation Cost**: `{diff_report.mutation_cost}`
- **Changed Layers**: `{', '.join(diff_report.changed_layers) or 'None'}`
- **Rationale**: {diff_report.rationale}

## Element Modifications
- **Added Elements** ({len(diff_report.added_elements)}): {list(diff_report.added_elements)}
- **Modified Elements** ({len(diff_report.modified_elements)}): {list(diff_report.modified_elements)}
- **Removed Elements** ({len(diff_report.removed_elements)}): {list(diff_report.removed_elements)}

## Domain Fingerprint Delta
```json
{json.dumps(diff_report.fingerprint_delta, indent=2)}
```

## Unified Blueprint Diff
```diff
{diff_report.unified_diff or "No text changes detected."}
```
"""
        md_path.write_text(md_content, encoding="utf-8")

        return json_path, md_path

    @classmethod
    def _extract_element_ids(cls, bp: Any) -> List[str]:
        if hasattr(bp, "beats") and bp.beats:
            return [b.beat_id for b in bp.beats]
        if hasattr(bp, "activities") and bp.activities:
            return [a.activity_id for a in bp.activities]
        if hasattr(bp, "slides") and bp.slides:
            return [getattr(s, "slide_id", str(i)) for i, s in enumerate(bp.slides)]
        if hasattr(bp, "sections") and bp.sections:
            return [getattr(s, "section_id", str(i)) for i, s in enumerate(bp.sections)]
        return []

    @classmethod
    def _serialize_bp(cls, bp: Any) -> Dict[str, Any]:
        if hasattr(bp, "model_dump"):
            try:
                return bp.model_dump()
            except Exception:
                pass
        return {"repr": repr(bp)}
