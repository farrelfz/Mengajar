"""
KIR AI Document Intelligence — Safe File Discovery Utility.

Provides deterministic file traversal with early directory pruning before traversal,
preventing unrestricted scans into deep dependency or cache directories like `venv`,
`.git`, and `node_modules`.
"""
from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_SKIP_DIRS: frozenset[str] = frozenset({
    "venv",
    ".venv",
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".idea",
    ".vscode",
})


def find_files(
    base_path: str | Path,
    patterns: str | Sequence[str] | None = None,
    skip_dirs: Iterable[str] | None = None,
    recursive: bool = True,
) -> list[Path]:
    """Find files under `base_path` matching `patterns`, safely pruning excluded directories before entry.

    Parameters
    ----------
    base_path : str | Path
        Root directory to begin searching from.
    patterns : str | Sequence[str] | None
        Glob filename pattern (e.g. '*.pdf') or list of patterns (e.g. ['*.pdf', '*.html']).
        If None, matches all files.
    skip_dirs : Iterable[str] | None
        Directory names to prune before traversal. Defaults to `DEFAULT_SKIP_DIRS`.
    recursive : bool
        Whether to traverse subdirectories. Default True.

    Returns
    -------
    list[Path]
        Deterministically sorted list of matching Path objects.
    """
    root_path = Path(base_path)
    if not root_path.exists():
        return []

    # If base_path points directly to a file
    if root_path.is_file():
        if patterns is None:
            return [root_path]
        pat_list = [patterns] if isinstance(patterns, str) else list(patterns)
        if any(fnmatch.fnmatch(root_path.name, pat) for pat in pat_list):
            return [root_path]
        return []

    if not root_path.is_dir():
        return []

    effective_skip: set[str] = set(DEFAULT_SKIP_DIRS if skip_dirs is None else skip_dirs)

    if patterns is None:
        pattern_list = ["*"]
    elif isinstance(patterns, str):
        pattern_list = [patterns]
    else:
        pattern_list = list(patterns)

    discovered: list[Path] = []

    for root, dirs, files in os.walk(root_path, topdown=True):
        # PRUNING: Mutate dirs in-place before descending into child directories
        dirs[:] = [
            d for d in dirs
            if d not in effective_skip and not d.startswith(".venv")
        ]

        # Match files in current directory
        for f in files:
            for pat in pattern_list:
                if fnmatch.fnmatch(f, pat):
                    discovered.append(Path(root) / f)
                    break

        if not recursive:
            break

    return sorted(discovered)
