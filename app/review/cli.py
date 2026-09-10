"""
Universal Document Intelligence System V5 — Human Review CLI.

Phase 6: Deterministic command-line interface for queue inspection,
leasing, evidence assembly, decision submission, and ledger verification.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from app.review.contracts.directives import ReviewDirective
from app.review.contracts.review_decision import ReviewDecision
from app.review.decisions.review_engine import ReviewDecisionEngine
from app.review.evidence.evidence_package import EvidencePackageBuilder
from app.review.provenance.immutable_ledger import ReviewProvenanceLedger
from app.review.queue.registry import ReviewQueueRegistry
from app.review.safety.directive_safety_validator import DirectiveSafetyValidator
from app.review.static_bundle import StaticReviewBundleGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.review.cli",
        description="Universal Document Intelligence V5 — Review Studio CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List active review cases")

    # show
    show_p = subparsers.add_parser("show", help="Show details for a specific case")
    show_p.add_argument("case_id", help="Review Case ID")

    # lease
    lease_p = subparsers.add_parser("lease", help="Acquire a lease lock on a case")
    lease_p.add_argument("case_id", help="Review Case ID")
    lease_p.add_argument("reviewer_id", help="Reviewer ID")
    lease_p.add_argument("--duration", type=float, default=1800.0, help="Lease duration in seconds")

    # evidence
    ev_p = subparsers.add_parser("evidence", help="Show evidence summary for a case")
    ev_p.add_argument("case_id", help="Review Case ID")

    # decide
    dec_p = subparsers.add_parser("decide", help="Submit an expert decision from a JSON file")
    dec_p.add_argument("case_id", help="Review Case ID")
    dec_p.add_argument("decision_file", help="Path to JSON file containing decision payload")

    # validate-directive
    val_p = subparsers.add_parser("validate-directive", help="Validate a directive JSON file")
    val_p.add_argument("case_id", help="Review Case ID")
    val_p.add_argument("directive_file", help="Path to JSON file containing directive payload")

    # ledger verify
    subparsers.add_parser("ledger-verify", help="Verify cryptographic hash chain of the review ledger")

    # bundle
    bnd_p = subparsers.add_parser("bundle", help="Generate a static HTML/JSON review bundle")
    bnd_p.add_argument("case_id", help="Review Case ID")

    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    registry = ReviewQueueRegistry()

    if args.command == "list":
        cases = registry.list_cases()
        print(f"Total Cases: {len(cases)}")
        print("-" * 80)
        for c in cases:
            print(f"[{c.priority_score:.2f}] {c.case_id} | {c.artifact_type:15} | {c.current_state.value:15} | {c.trigger.value}")
        return 0

    elif args.command == "show":
        case = registry.get_case(args.case_id)
        if not case:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            return 1
        print(case.model_dump_json(indent=2))
        return 0

    elif args.command == "lease":
        ok, updated, msg = registry.lease_case(args.case_id, args.reviewer_id, duration_seconds=args.duration)
        if ok and updated:
            print(f"Success: Case {args.case_id} leased to {args.reviewer_id} until {updated.lease_expires_at}.")
            return 0
        else:
            print(f"Lease failed: {msg}", file=sys.stderr)
            return 1

    elif args.command == "evidence":
        case = registry.get_case(args.case_id)
        if not case:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            return 1
        pkg = EvidencePackageBuilder.assemble(
            case_id=case.case_id,
            artifact_id=case.artifact_id,
            artifact_type=case.artifact_type,
            trigger=case.trigger,
        )
        print(EvidencePackageBuilder.generate_markdown_summary(pkg))
        return 0

    elif args.command == "decide":
        case = registry.get_case(args.case_id)
        if not case:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            return 1
        with open(args.decision_file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        decision = ReviewDecision.model_validate(data)
        ok, updated, errs = ReviewDecisionEngine.apply_decision(case, decision)
        if ok:
            registry.update_case(updated)
            print(f"Decision committed successfully. Case state: {updated.current_state.value}")
            return 0
        else:
            print(f"Decision rejected: {'; '.join(errs)}", file=sys.stderr)
            return 1

    elif args.command == "validate-directive":
        case = registry.get_case(args.case_id)
        if not case:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            return 1
        with open(args.directive_file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        directive = ReviewDirective.model_validate(data)
        res = DirectiveSafetyValidator.validate(directive, artifact_type=case.artifact_type, raise_on_violation=False)
        print(res.model_dump_json(indent=2))
        return 0 if res.is_valid else 1

    elif args.command == "ledger-verify":
        ledger = ReviewProvenanceLedger()
        is_ok, count, err = ledger.verify_ledger_integrity()
        if is_ok:
            print(f"Ledger integrity VERIFIED across {count} records. Hash chain intact.")
            return 0
        else:
            print(f"Ledger verification FAILED: {err}", file=sys.stderr)
            return 1

    elif args.command == "bundle":
        case = registry.get_case(args.case_id)
        if not case:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            return 1
        pkg = EvidencePackageBuilder.assemble(
            case_id=case.case_id,
            artifact_id=case.artifact_id,
            artifact_type=case.artifact_type,
            trigger=case.trigger,
        )
        bundle_path = StaticReviewBundleGenerator.generate_bundle(case, pkg)
        print(f"Static review bundle created at: {bundle_path}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
