"""
Universal Document Intelligence System V5 — Quality Regression Baselines.

Phase 2C: Provides structured baseline configurations for testing regression limits.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

BASELINE_FILE = Path(__file__).parent / "quality_regression_baseline.json"


def load_quality_baselines() -> Dict[str, Any]:
    return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))["baselines"]
