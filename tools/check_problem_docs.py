#!/usr/bin/env python3
"""Validate the domain-first scientific problem documentation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBLEM_ROOT = ROOT / "docs" / "problems"
LKM_ROOT = ROOT / "evidence" / "lkm" / "2026-07-27-tight-binding-domain" / "raw"
EXPECTED_HEADINGS = [
    "## Scientific question",
    "## Benchmark adaptation",
    "## Parameters",
    "## Required computation",
    "## Expected result",
    "## Acceptance and convergence",
    "## Held-out variants",
    "## Evidence",
    "## Implementation status",
]
FRONTMATTER_KEYS = {
    "id",
    "suite",
    "source_requirement",
    "status",
    "acceptance_class",
    "lkm_snapshot",
}
ACCEPTANCE_CLASSES = {"exact", "reference", "convergence", "scaling"}


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing opening frontmatter delimiter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError as error:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from error
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        if ": " not in line:
            raise ValueError(f"{path}: malformed frontmatter line {line!r}")
        key, value = line.split(": ", 1)
        if key in metadata:
            raise ValueError(f"{path}: duplicate frontmatter key {key}")
        metadata[key] = value
    if set(metadata) != FRONTMATTER_KEYS:
        raise ValueError(
            f"{path}: frontmatter keys are {sorted(metadata)}, "
            f"expected {sorted(FRONTMATTER_KEYS)}"
        )
    return metadata, body


def extract_section(body: str, heading: str) -> str:
    start = body.index(heading) + len(heading)
    later = [
        body.find(other, start)
        for other in EXPECTED_HEADINGS
        if body.find(other, start) != -1
    ]
    end = min(later) if later else len(body)
    return body[start:end].strip()


def validate_problem(path: Path, expected_number: int, expected_status: str) -> str:
    text = path.read_text()
    metadata, body = parse_frontmatter(text, path)
    qid = f"TBQ-{expected_number:03d}"
    requirement = f"TB-REQ-{expected_number:03d}"
    suite = path.parent.name

    if metadata["id"] != qid:
        raise ValueError(f"{path}: id {metadata['id']} does not match {qid}")
    if metadata["source_requirement"] != requirement:
        raise ValueError(
            f"{path}: source requirement {metadata['source_requirement']} "
            f"does not match {requirement}"
        )
    if metadata["suite"] != suite:
        raise ValueError(f"{path}: suite {metadata['suite']} does not match {suite}")
    if metadata["status"] != expected_status:
        raise ValueError(
            f"{path}: status {metadata['status']} does not match {expected_status}"
        )
    if metadata["acceptance_class"] not in ACCEPTANCE_CLASSES:
        raise ValueError(
            f"{path}: invalid acceptance class {metadata['acceptance_class']}"
        )
    if metadata["lkm_snapshot"] != "2026-07-27":
        raise ValueError(f"{path}: unexpected LKM snapshot {metadata['lkm_snapshot']}")
    if not path.name.startswith(f"tbq-{expected_number:03d}-"):
        raise ValueError(f"{path}: filename does not match {qid}")
    if not re.search(rf"^# {qid} — .+$", body, flags=re.MULTILINE):
        raise ValueError(f"{path}: missing title for {qid}")

    positions = []
    for heading in EXPECTED_HEADINGS:
        count = body.count(heading)
        if count != 1:
            raise ValueError(f"{path}: {heading!r} occurs {count} times")
        positions.append(body.index(heading))
        section = extract_section(body, heading)
        if len(section) < 40:
            raise ValueError(f"{path}: {heading!r} is too short")
    if positions != sorted(positions):
        raise ValueError(f"{path}: required sections are out of order")

    parameter_section = extract_section(body, "## Parameters")
    parameter_rows = [
        line
        for line in parameter_section.splitlines()
        if line.startswith("| `") and line.endswith(" |")
    ]
    if len(parameter_rows) < 3:
        raise ValueError(f"{path}: expected at least three documented parameters")

    evidence = extract_section(body, "## Evidence")
    if not re.search(r"`gcn_[0-9a-f]{16}`", evidence):
        raise ValueError(f"{path}: missing a public LKM GCN identifier")
    if "https://doi.org/" not in evidence:
        raise ValueError(f"{path}: missing DOI link")
    if not re.search(
        r"not a\s+confidence or correctness probability", evidence
    ):
        raise ValueError(f"{path}: missing LKM score interpretation")

    implementation = extract_section(body, "## Implementation status")
    if expected_status == "proposed":
        if not re.search(
            r"does not claim that any\s+backend currently passes it", implementation
        ):
            raise ValueError(f"{path}: proposed status is not explained honestly")
    else:
        if "`executable`" not in implementation:
            raise ValueError(f"{path}: executable status is not stated")
        if "benchmark/problem_coverage.json" not in implementation:
            raise ValueError(f"{path}: executable status does not link the audit")
    if "TBD" in text or "TODO" in text:
        raise ValueError(f"{path}: unresolved placeholder")
    return path.relative_to(PROBLEM_ROOT).as_posix()


def validate() -> int:
    paths = sorted(PROBLEM_ROOT.glob("[0-9][0-9]-*/tbq-[0-9][0-9][0-9]-*.md"))
    if len(paths) != 100:
        raise ValueError(f"expected 100 problem files, found {len(paths)}")

    coverage = json.loads((ROOT / "benchmark" / "problem_coverage.json").read_text())
    coverage_by_id = {problem["id"]: problem for problem in coverage["problems"]}
    if len(coverage_by_id) != 100:
        raise ValueError("problem coverage audit does not contain 100 unique ids")
    executable_ids = {
        qid
        for qid, problem in coverage_by_id.items()
        if any(
            record["status"] == "implemented"
            for record in problem["backends"].values()
        )
    }

    seen_ids = []
    relative_paths = []
    for expected_number, path in enumerate(paths, start=1):
        qid = f"TBQ-{expected_number:03d}"
        expected_status = "executable" if qid in executable_ids else "proposed"
        relative_paths.append(
            validate_problem(path, expected_number, expected_status)
        )
        seen_ids.append(qid)
    if len(set(seen_ids)) != 100:
        raise ValueError("problem identifiers are not unique")

    index = (PROBLEM_ROOT / "README.md").read_text()
    index_ids = re.findall(r"\| (TBQ-[0-9]{3}) \|", index)
    if index_ids != seen_ids:
        raise ValueError("catalog identifiers are missing, duplicated, or out of order")
    linked_paths = re.findall(r"\]\(([^)]+/tbq-[0-9]{3}-[^)]+\.md)\)", index)
    if linked_paths != relative_paths:
        raise ValueError("catalog links do not exactly match the problem files")
    index_statuses = re.findall(
        r"\| TBQ-[0-9]{3} \|.+\| TB-REQ-[0-9]{3} \| (proposed|executable) \|",
        index,
    )
    expected_statuses = [
        "executable" if qid in executable_ids else "proposed" for qid in seen_ids
    ]
    if index_statuses != expected_statuses:
        raise ValueError("catalog statuses do not match the backend audit")

    discovery_paths = sorted(LKM_ROOT.glob("[0-9][0-9]-*.json"))
    reasoning_paths = sorted((LKM_ROOT / "reasoning").glob("[0-9][0-9]-*.json"))
    if len(discovery_paths) != 21 or len(reasoning_paths) != 11:
        raise ValueError(
            "LKM snapshot must contain 21 discovery and 11 reasoning responses"
        )

    node_ids: set[str] = set()
    discovery_papers: set[str] = set()
    reasoning_papers: set[str] = set()
    paper_dois: set[str] = set()
    chain_ids: set[str] = set()
    reasoning_chain_count = 0
    for path in discovery_paths + reasoning_paths:
        response = json.loads(path.read_text())
        data = response.get("data", {})
        node_ids.update(
            variable["id"]
            for variable in data.get("variables", [])
            if "id" in variable
        )
        papers = data.get("papers", {})
        target = discovery_papers if path in discovery_paths else reasoning_papers
        target.update(key.removeprefix("paper:") for key in papers)
        paper_dois.update(
            paper["doi"].lower()
            for paper in papers.values()
            if paper.get("doi")
        )
        chains = data.get("reasoning_chains", [])
        reasoning_chain_count += len(chains)
        chain_ids.update(
            chain["chain_id"] for chain in chains if chain.get("chain_id")
        )

    if len(node_ids) != 846:
        raise ValueError(f"LKM snapshot has {len(node_ids)} nodes, expected 846")
    if len(discovery_papers) != 835:
        raise ValueError(
            f"LKM discovery has {len(discovery_papers)} papers, expected 835"
        )
    if reasoning_chain_count != 250:
        raise ValueError(
            f"LKM snapshot has {reasoning_chain_count} chains, expected 250"
        )
    if len(discovery_papers | reasoning_papers) != 1048:
        raise ValueError(
            "LKM discovery and reasoning union does not contain 1,048 papers"
        )

    all_problem_text = "\n".join(path.read_text() for path in paths)
    cited_gcns = set(re.findall(r"`(gcn_[0-9a-f]{16})`", all_problem_text))
    cited_chains = set(re.findall(r"`([0-9]+_[0-9]+)`", all_problem_text))
    cited_dois = set(
        doi.lower()
        for doi in re.findall(r"https://doi\.org/([^)]+)", all_problem_text)
    )
    if cited_gcns - node_ids:
        raise ValueError(f"problem docs cite unknown GCN ids: {cited_gcns - node_ids}")
    if cited_chains - chain_ids:
        raise ValueError(
            f"problem docs cite unknown reasoning chains: {cited_chains - chain_ids}"
        )
    if cited_dois - paper_dois:
        raise ValueError(f"problem docs cite unknown paper DOIs: {cited_dois - paper_dois}")

    failed_lookup = json.loads(
        (
            LKM_ROOT / "reasoning" / "11-zero-chern-nonlinear-boundary.json"
        ).read_text()
    )
    if failed_lookup.get("code") != 290004:
        raise ValueError("the retained failed LKM lookup no longer has code 290004")
    return len(executable_ids)


def main() -> int:
    try:
        executable_count = validate()
    except (OSError, ValueError) as error:
        print(f"problem documentation validation failed: {error}", file=sys.stderr)
        return 1
    print(
        "problem documentation validation passed: "
        f"100 unique questions in 20 suites, {executable_count} executable; "
        "846 LKM nodes, 1,048 papers, and 250 reasoning chains verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
