#!/usr/bin/env python3
"""Validate the one-to-one domain-first AD companion catalog."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "ad_requirements.json"
DOC_ROOT = ROOT / "docs" / "ad-requirements"
ROLES = {"essential", "helpful", "conditional", "not_central"}
STATUSES = {
    "ad_native_verified",
    "implementable_unverified",
    "missing_ad_rule",
    "missing_forward_physics",
    "conditionally_differentiable",
    "ad_not_central",
}
REQUIRED_FIELDS = {
    "id",
    "tbq_id",
    "title",
    "suite",
    "source_problem",
    "ad_role",
    "continuous_controls",
    "scientific_outputs",
    "differentiable_formulation",
    "no_ad_baseline",
    "validity_boundary",
    "required_capabilities",
    "acceptance",
    "forward_status",
    "ad_status",
    "status_reason",
    "existing_witnesses",
    "issue",
}
ACCEPTANCE_FIELDS = {
    "derivative_oracle",
    "scientific_gate",
    "generalization_gate",
}


def validate() -> dict[str, object]:
    payload = json.loads(MANIFEST.read_text())
    if payload["schema_version"] != 1:
        raise ValueError("AD requirement schema_version must be 1")
    problems = payload["problems"]
    expected_qids = [f"TBQ-{number:03d}" for number in range(1, 101)]
    if [problem["tbq_id"] for problem in problems] != expected_qids:
        raise ValueError("AD companions must map in order to TBQ-001..TBQ-100")
    if len({problem["id"] for problem in problems}) != 100:
        raise ValueError("AD companion identifiers must be unique")
    if set(payload["status_vocabulary"]) != STATUSES:
        raise ValueError("AD status vocabulary is incomplete or contains extra states")
    if set(payload["role_vocabulary"]) != ROLES:
        raise ValueError("AD role vocabulary is incomplete or contains extra roles")

    capability_ids = set(payload["capabilities"])
    if not capability_ids:
        raise ValueError("AD capability catalog is empty")
    forward_payload = json.loads(
        (ROOT / "benchmark" / "problem_coverage.json").read_text()
    )
    forward = {
        problem["id"]: problem["backends"]["thouless"]["status"]
        for problem in forward_payload["problems"]
    }
    cases = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())["cases"]
    witnesses = {case["id"]: set(case["question_ids"]) for case in cases}

    expected_docs: set[Path] = set()
    for problem in problems:
        if set(problem) != REQUIRED_FIELDS:
            raise ValueError(
                f"{problem.get('tbq_id', 'unknown')}: unexpected problem fields"
            )
        qid = problem["tbq_id"]
        if problem["id"] != f"AD-{qid}":
            raise ValueError(f"{qid}: AD companion id does not match")
        if problem["ad_role"] not in ROLES or problem["ad_status"] not in STATUSES:
            raise ValueError(f"{qid}: invalid role or status")
        if problem["forward_status"] != forward[qid]:
            raise ValueError(f"{qid}: forward status drifted from the domain audit")
        if not problem["continuous_controls"] or not all(problem["continuous_controls"]):
            raise ValueError(f"{qid}: continuous controls are empty")
        if not problem["scientific_outputs"] or not all(problem["scientific_outputs"]):
            raise ValueError(f"{qid}: scientific outputs are empty")
        if not problem["differentiable_formulation"].strip():
            raise ValueError(f"{qid}: differentiable formulation is empty")
        if not problem["no_ad_baseline"].strip():
            raise ValueError(f"{qid}: no-AD baseline is empty")
        if not problem["validity_boundary"].strip():
            raise ValueError(f"{qid}: validity boundary is empty")
        if set(problem["acceptance"]) != ACCEPTANCE_FIELDS:
            raise ValueError(f"{qid}: acceptance gates are incomplete")
        if not set(problem["required_capabilities"]) <= capability_ids:
            raise ValueError(f"{qid}: cites an unknown AD capability")
        if not (ROOT / problem["source_problem"]).is_file():
            raise ValueError(f"{qid}: source problem does not exist")
        if not problem["issue"].startswith("https://github.com/"):
            raise ValueError(f"{qid}: unresolved work lacks a GitHub issue")
        if problem["ad_role"] == "conditional" and (
            problem["ad_status"] != "conditionally_differentiable"
        ):
            raise ValueError(f"{qid}: conditional role must retain conditional status")
        if problem["ad_role"] == "not_central" and (
            problem["ad_status"] != "ad_not_central"
        ):
            raise ValueError(f"{qid}: non-central role must retain non-central status")
        if problem["ad_status"] == "ad_native_verified" and not problem[
            "existing_witnesses"
        ]:
            raise ValueError(f"{qid}: verified companion lacks a native witness")
        for witness in problem["existing_witnesses"]:
            if witness not in witnesses or qid not in witnesses[witness]:
                raise ValueError(f"{qid}: invalid witness mapping {witness}")

        doc = (
            DOC_ROOT
            / problem["suite"]
            / Path(problem["source_problem"]).name
        )
        expected_docs.add(doc)
        if not doc.is_file():
            raise ValueError(f"{qid}: companion document is missing")
        text = doc.read_text()
        for heading in (
            "## Scientific anchor",
            "## Why differentiation matters",
            "## Controls and outputs",
            "## Differentiable formulation",
            "## Validity and failure semantics",
            "## Acceptance",
            "## Required Rust-native capabilities",
            "## Current evidence and gap",
            "## Provenance",
        ):
            if text.count(heading) != 1:
                raise ValueError(f"{qid}: missing or duplicated heading {heading}")
        if "No-AD control:" not in text:
            raise ValueError(f"{qid}: companion lacks a no-AD control")

    actual_docs = set(DOC_ROOT.glob("[0-9][0-9]-*/tbq-*.md"))
    if actual_docs != expected_docs:
        raise ValueError("AD companion documents are not one-to-one with the manifest")

    seebeck = problems[72]
    seebeck_text = " ".join(
        seebeck["continuous_controls"]
        + seebeck["scientific_outputs"]
        + [seebeck["differentiable_formulation"]]
    ).lower()
    for required in ("energy", "bias", "seebeck", "differential conductance"):
        if required not in seebeck_text:
            raise ValueError(f"TBQ-073 omits the derivative target {required}")

    summary = payload["summary"]
    if summary["problems"] != 100:
        raise ValueError("AD summary problem count is not 100")
    if summary["status_counts"] != dict(
        sorted(Counter(problem["ad_status"] for problem in problems).items())
    ):
        raise ValueError("AD summary status counts are stale")
    if summary["role_counts"] != dict(
        sorted(Counter(problem["ad_role"] for problem in problems).items())
    ):
        raise ValueError("AD summary role counts are stale")
    return payload


def main() -> int:
    try:
        payload = validate()
    except (KeyError, TypeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "validated 100 domain-first AD companions, "
        f"{len(payload['capabilities'])} reusable capabilities, and one-to-one docs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
