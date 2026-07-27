import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_domain_cases_and_implementations_are_consistent() -> None:
    cases = json.loads((ROOT / "benchmark" / "domain_cases.json").read_text())["cases"]
    implementations = json.loads(
        (ROOT / "benchmark" / "domain_implementation.json").read_text()
    )["implemented"]
    by_id = {case["id"]: case for case in cases}
    assert len(cases) == len(by_id) == 5
    assert set(implementations) == {"thouless", "pythtb", "kwant"}
    for backend, case_ids in implementations.items():
        assert len(case_ids) == len(set(case_ids))
        for case_id in case_ids:
            assert case_id in by_id
            assert backend in by_id[case_id]["backends"]


def test_problem_audit_is_complete_and_witnessed() -> None:
    baseline = json.loads((ROOT / "benchmark" / "cases.json").read_text())["cases"]
    domain = json.loads((ROOT / "benchmark" / "domain_cases.json").read_text())["cases"]
    known_cases = {case["id"] for case in baseline + domain}
    audit = json.loads((ROOT / "benchmark" / "problem_coverage.json").read_text())
    problems = audit["problems"]
    assert len(problems) == 100
    assert [problem["id"] for problem in problems] == [
        f"TBQ-{index:03d}" for index in range(1, 101)
    ]
    assert len({problem["id"] for problem in problems}) == 100
    for problem in problems:
        assert set(problem["backends"]) == {"thouless", "pythtb", "kwant"}
        for record in problem["backends"].values():
            assert record["status"] in {
                "implemented",
                "partial",
                "not_applicable",
            }
            if record["status"] == "implemented":
                assert record["witness_cases"]
                assert set(record["witness_cases"]) <= known_cases
            else:
                assert record["witness_cases"] == []


def test_strict_whole_problem_coverage_counts() -> None:
    summary = json.loads(
        (ROOT / "benchmark" / "problem_coverage.json").read_text()
    )["summary"]
    assert summary["thouless"]["implemented"] == 13
    assert summary["pythtb"]["implemented"] == 12
    assert summary["kwant"]["implemented"] == 13
    for item in summary.values():
        assert (
            item["implemented"] + item["partial"] + item["not_applicable"] == 100
        )
