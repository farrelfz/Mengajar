"""
Universal Document Intelligence System V5 — Artifact Snapshot Manager.

Phase 6: Stores immutable, read-only references and snapshots of visual renders,
blueprints, and manifests for safe reviewer inspection.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


class ArtifactSnapshotManager:
    """Manages frozen snapshot storage for review cases."""

    @classmethod
    def capture_snapshot(
        cls,
        case_dir: Path,
        render_paths: Optional[List[Path]] = None,
        blueprint_data: Optional[Dict[str, Any]] = None,
        manifest_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Copies or links artifacts into case folder."""
        rendered_dir = case_dir / "rendered"
        artifact_dir = case_dir / "artifact"
        rendered_dir.mkdir(parents=True, exist_ok=True)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        copied_renders: List[str] = []
        if render_paths:
            for rp in render_paths:
                if rp.exists():
                    dest = rendered_dir / rp.name
                    if rp.is_file():
                        shutil.copy2(rp, dest)
                        copied_renders.append(str(dest))

        if blueprint_data:
            bp_dest = artifact_dir / "blueprint.json"
            with open(bp_dest, "w", encoding="utf-8") as fp:
                json.dump(blueprint_data, fp, indent=2)

        if manifest_data:
            mf_dest = artifact_dir / "manifest.json"
            with open(mf_dest, "w", encoding="utf-8") as fp:
                json.dump(manifest_data, fp, indent=2)

        return {
            "rendered_dir": str(rendered_dir),
            "artifact_dir": str(artifact_dir),
            "renders": copied_renders,
            "has_blueprint": blueprint_data is not None,
            "has_manifest": manifest_data is not None,
        }
