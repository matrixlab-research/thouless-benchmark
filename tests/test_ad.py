import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ad_case_catalog_is_diverse_and_complete() -> None:
    payload = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())
    assert payload["schema_version"] == 1
    assert payload["source_issue"].endswith("/thouless-benchmark/issues/6")
    cases = payload["cases"]
    by_id = {case["id"]: case for case in cases}
    assert len(cases) == len(by_id) == 10
    assert len({case["problem_type"] for case in cases}) == 10
    assert all(case["track"] == "ad" for case in cases)
    assert all(case["question_ids"] for case in cases)
    assert all(case["ad_gates"] for case in cases)
    assert all(case["lkm_nodes"] for case in cases)
    assert all(len(case["required_checks"]) == 3 for case in cases)
    assert all(
        node.startswith("gcn_")
        for case in cases
        for node in case["lkm_nodes"]
    )
    for case in cases:
        document = ROOT / case["document"]
        assert document.is_file()
        text = document.read_text()
        for heading in (
            "## Scientific question",
            "## Parameters",
            "## Required computation",
            "## Expected result",
            "## Acceptance",
            "## Evidence and boundary",
        ):
            assert heading in text

    implemented = json.loads(
        (ROOT / "benchmark" / "ad_implementation.json").read_text()
    )["implemented"]
    assert set(implemented) == {"thouless"}
    assert len(implemented["thouless"]) == len(set(implemented["thouless"])) == 10
    assert set(implemented["thouless"]) == set(by_id)


def test_ad_question_references_belong_to_the_domain_catalog() -> None:
    known = {
        problem["id"]
        for problem in json.loads(
            (ROOT / "benchmark" / "problem_coverage.json").read_text()
        )["problems"]
    }
    cases = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())["cases"]
    assert {
        question_id
        for case in cases
        for question_id in case["question_ids"]
    } <= known


def test_verified_ad_snapshot_matches_manifest() -> None:
    result_path = (
        ROOT / "results" / "verified" / "2026-07-28-ad.json"
    )
    payload = json.loads(result_path.read_text())
    records = payload["records"]
    expected = set(
        json.loads(
            (ROOT / "benchmark" / "ad_implementation.json").read_text()
        )["implemented"]["thouless"]
    )
    assert {record["case_id"] for record in records} == expected
    assert all(record["backend"] == "thouless" for record in records)
    assert all(
        record["representative_result"]["status"] == "passed"
        for record in records
    )
    assert payload["policy"]["public_validation_is_not_isolated_held_out_evaluation"]
    assert payload["policy"]["whole_tbq_coverage_is_not_inferred_from_ad_witnesses"]
