import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ad_case_catalog_is_diverse_and_complete() -> None:
    payload = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())
    assert payload["schema_version"] == 1
    assert payload["source_issue"].endswith("/thouless-benchmark/issues/6")
    assert (ROOT / payload["lkm_evidence"] / "README.md").is_file()
    cases = payload["cases"]
    by_id = {case["id"]: case for case in cases}
    assert len(cases) == len(by_id) == 10
    assert len({case["problem_type"] for case in cases}) == 10
    assert all(case["track"] == "ad" for case in cases)
    assert all(case["question_ids"] for case in cases)
    assert all(case["ad_gates"] for case in cases)
    assert all(case["lkm_nodes"] for case in cases)
    assert all(case["benchmark_kind"] == "research_workflow_adaptation" for case in cases)
    assert all(case["physical_system"] for case in cases)
    assert len({case["physical_system"] for case in cases}) == 9
    assert all(case["source_papers"] for case in cases)
    assert all(
        paper["doi"] and paper["title"] and paper["lkm_paper_id"].isdigit()
        for case in cases
        for paper in case["source_papers"]
    )
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
            "## Benchmark adaptation",
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


def test_ad_lkm_evidence_bundle_is_complete_and_traceable() -> None:
    payload = json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())
    bundle = ROOT / payload["lkm_evidence"]
    searches = sorted((bundle / "raw").glob("[0-9][0-9]-*.json"))
    reasoning = sorted((bundle / "raw" / "reasoning").glob("[0-9][0-9]-*.json"))
    assert len(searches) == len(reasoning) == 10

    discovered_nodes = set()
    for path in searches:
        response = json.loads(path.read_text())
        assert response["code"] == 0
        assert response["trace_id"].startswith("req_")
        assert response["data"]["variables"]
        assert response["data"]["papers"]
        discovered_nodes.update(
            variable["id"] for variable in response["data"]["variables"]
        )

    for path in reasoning:
        response = json.loads(path.read_text())
        assert response["code"] == 0
        assert response["trace_id"].startswith("req_")
        assert response["data"]["papers"]

    manifest_nodes = {
        node for case in payload["cases"] for node in case["lkm_nodes"]
    }
    assert manifest_nodes <= discovered_nodes


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
        ROOT
        / "results"
        / "verified"
        / "2026-07-28-ad-research-workflows.json"
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
    cases = {
        case["id"]: case
        for case in json.loads(
            (ROOT / "benchmark" / "ad_cases.json").read_text()
        )["cases"]
    }
    assert all(
        record["representative_result"]["metrics"]["physical_model"]
        == cases[record["case_id"]]["physical_system"]
        for record in records
    )
    assert payload["policy"]["public_validation_is_not_isolated_held_out_evaluation"]
    assert payload["policy"]["whole_tbq_coverage_is_not_inferred_from_ad_witnesses"]


def test_ad_method_comparison_manifest_is_complete_and_fair() -> None:
    payload = json.loads((ROOT / "benchmark" / "ad_comparison.json").read_text())
    cases = payload["cases"]
    source_cases = {
        case["id"]
        for case in json.loads((ROOT / "benchmark" / "ad_cases.json").read_text())[
            "cases"
        ]
    }
    assert payload["schema_version"] == 1
    assert len(cases) == len({case["id"] for case in cases}) == 10
    assert {case["source_case_id"] for case in cases} == source_cases
    assert all(case["id"].startswith("adcmp_") for case in cases)
    assert all(case["parameter_count"] > 0 for case in cases)
    assert {
        case["workload_kind"] for case in cases
    } == {
        "end_to_end_optimization",
        "full_gradient",
        "full_jacobian",
        "parameter_scaling_full_gradient",
    }
    fairness = payload["fairness_contract"]
    assert fairness["same_rust_forward_model"]
    assert fairness["same_scientific_product"]
    assert fairness["same_initial_state_and_optimizer"]
    assert fairness["finite_difference_uses_forward_only_calls"]
    assert fairness["both_derivative_paths_are_warmed_before_timing"]
    assert fairness["accuracy_is_gated"]
    assert fairness["relative_speed_is_not_a_ci_gate"]
    assert set(payload["required_checks"]) == {
        "ADCMP-G01_full_derivative_agreement",
        "ADCMP-G02_scientific_result_equivalence",
        "ADCMP-G03_paired_timings_are_positive",
    }


def test_verified_ad_method_comparison_matches_manifest() -> None:
    payload = json.loads(
        (
            ROOT
            / "results"
            / "verified"
            / "2026-07-28-ad-vs-finite-difference.json"
        ).read_text()
    )
    expected = {
        case["id"]
        for case in json.loads(
            (ROOT / "benchmark" / "ad_comparison.json").read_text()
        )["cases"]
    }
    records = payload["records"]
    assert {record["case_id"] for record in records} == expected
    assert all(record["repetitions"] >= 3 for record in records)
    assert all(
        record["representative_result"]["status"] == "passed"
        for record in records
    )
    assert (
        payload["summary"]["native_ad_faster"]
        + payload["summary"]["central_finite_difference_faster"]
        <= len(records)
    )
    assert payload["policy"]["relative_speed_is_not_a_ci_gate"]
