"""
Universal Document Intelligence System V5 — Static Review Bundle Generator.

Phase 6: Generates self-contained, read-only forensic inspection bundles
including static_review.html, evidence.json, and case manifests.
The static HTML is strictly a visual inspection tool, NEVER an export authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.review.contracts.evidence import ReviewEvidencePackage
from app.review.contracts.review_case import ReviewCase
from app.review.evidence.evidence_package import EvidencePackageBuilder


class StaticReviewBundleGenerator:
    """Creates file-backed inspection packages in artifacts/review_queue/cases/{case_id}/."""

    @classmethod
    def generate_bundle(
        cls,
        case: ReviewCase,
        evidence_pkg: ReviewEvidencePackage,
        output_dir: Optional[Path] = None,
    ) -> Path:
        base = output_dir or Path("artifacts/review_queue/cases") / case.case_id
        base.mkdir(parents=True, exist_ok=True)

        # 1. Case manifest
        with open(base / "case_manifest.json", "w", encoding="utf-8") as fp:
            fp.write(case.model_dump_json(indent=2))

        # 2. Evidence JSON & Markdown
        with open(base / "evidence.json", "w", encoding="utf-8") as fp:
            fp.write(evidence_pkg.model_dump_json(indent=2))

        with open(base / "evidence.md", "w", encoding="utf-8") as fp:
            fp.write(EvidencePackageBuilder.generate_markdown_summary(evidence_pkg))

        # 3. Quality report & repair history
        with open(base / "quality_report.json", "w", encoding="utf-8") as fp:
            json.dump({"findings": list(evidence_pkg.findings), "hard_blockers": list(evidence_pkg.hard_blockers)}, fp, indent=2)

        with open(base / "repair_history.json", "w", encoding="utf-8") as fp:
            json.dump(list(evidence_pkg.repair_history), fp, indent=2)

        # 4. Review decision template
        template = {
            "case_id": case.case_id,
            "reviewer_id": case.assigned_reviewer_id or "reviewer_id_placeholder",
            "decision_type": "CONFIRM_DEFECT",
            "confidence": "HIGH",
            "epistemic_status": "VERIFIED",
            "rationale": "Provide detailed pedagogical, visual, or scientific justification (min 20 chars).",
            "observations": [
                {
                    "statement": "Defect observation description.",
                    "target_element": "element_id",
                    "page_or_slide": 1,
                    "epistemic_status": "VERIFIED",
                }
            ],
            "directives": [],
        }
        with open(base / "review_template.json", "w", encoding="utf-8") as fp:
            json.dump(template, fp, indent=2)

        # 5. Static read-only HTML bundle
        html_content = cls._build_static_html(case, evidence_pkg)
        with open(base / "static_review.html", "w", encoding="utf-8") as fp:
            fp.write(html_content)

        return base

    @classmethod
    def _build_static_html(cls, case: ReviewCase, pkg: ReviewEvidencePackage) -> str:
        findings_li = "".join(
            f"<li><b>[{f.get('severity', 'INFO')}] {f.get('failure_code', '')}:</b> {f.get('message', '')}</li>"
            for f in pkg.findings[:10]
        ) or "<li>No findings recorded.</li>"

        blockers_li = "".join(f"<li><code>{b}</code></li>" for b in pkg.hard_blockers) or "<li>None</li>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Review Case {case.case_id} — Universal Document Intelligence V5</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; background: #0f172a; color: #f8fafc; }}
    .header {{ border-bottom: 2px solid #334155; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
    .badge {{ display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; background: #dc2626; color: white; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem; }}
    h1, h2, h3 {{ color: #38bdf8; }}
    code {{ background: #334155; padding: 0.2rem 0.4rem; border-radius: 4px; color: #facc15; }}
    ul {{ line-height: 1.6; }}
    .notice {{ background: #451a03; border-left: 4px solid #f59e0b; padding: 0.75rem; margin-top: 1rem; color: #fef3c7; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Human Review Studio — Forensic Case Inspection</h1>
    <div><b>Case ID:</b> <code>{case.case_id}</code> | <b>Artifact Type:</b> <code>{case.artifact_type}</code> | <span class="badge">{case.current_state.value}</span></div>
  </div>

  <div class="card">
    <h2>1. Case Overview</h2>
    <p><b>Trigger Source:</b> <code>{case.trigger.value}</code></p>
    <p><b>Priority Score:</b> <code>{case.priority_score:.3f}</code></p>
    <p><b>Evidence Sufficiency:</b> <code>{pkg.sufficiency.overall_sufficiency.value}</code> ({pkg.sufficiency.explanation})</p>
  </div>

  <div class="card">
    <h2>2. Hard Blockers Remaining</h2>
    <ul>{blockers_li}</ul>
  </div>

  <div class="card">
    <h2>3. Diagnostic Findings</h2>
    <ul>{findings_li}</ul>
  </div>

  <div class="notice">
    <b>READ-ONLY FORENSIC VIEW:</b> This inspection artifact is rendered for human evidence review only. Export clearance can strictly be granted by <code>AuthorizedExportGate</code> upon re-evaluation by <code>UnifiedQualityAuthority</code>.
  </div>
</body>
</html>
"""
