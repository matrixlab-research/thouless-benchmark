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
    baseline_results = json.loads(
        (ROOT / "results" / "verified" / "2026-07-26-implemented.json").read_text()
    )["results"]
    domain_records = json.loads(
        (ROOT / "results" / "verified" / "2026-07-27-domain.json").read_text()
    )["records"]
    verified = {
        (record["case_id"], record["backend"])
        for record in baseline_results
        if record["status"] == "passed"
    } | {
        (record["case_id"], record["backend"])
        for record in domain_records
        if record["representative_result"]["status"] == "passed"
    }
    audit = json.loads((ROOT / "benchmark" / "problem_coverage.json").read_text())
    problems = audit["problems"]
    assert len(problems) == 100
    assert [problem["id"] for problem in problems] == [
        f"TBQ-{index:03d}" for index in range(1, 101)
    ]
    assert len({problem["id"] for problem in problems}) == 100
    assert audit["schema_version"] == 2
    capability_labels = audit["capability_labels"]
    assert capability_labels
    assert "scientific_scale" in audit["policy"]
    assert set(audit["backend_capabilities"]) == {"thouless", "pythtb", "kwant"}
    for profile in audit["backend_capabilities"].values():
        assert profile["version"]
        assert profile["source"].startswith("https://")
        assert profile["declared_scope"]
    for problem in problems:
        assert set(problem["backends"]) == {"thouless", "pythtb", "kwant"}
        for backend, record in problem["backends"].items():
            assert record["status"] in {
                "implemented",
                "implementable_unverified",
                "missing_capability",
                "not_applicable",
            }
            assert record["required_capabilities"]
            assert len(record["required_capabilities"]) == len(
                set(record["required_capabilities"])
            )
            assert set(record["required_capabilities"]) <= set(capability_labels)
            assert set(record["available_capabilities"]) <= set(
                record["required_capabilities"]
            )
            assert set(record["missing_capabilities"]) <= set(
                record["required_capabilities"]
            )
            assert set(record["available_capabilities"]).isdisjoint(
                record["missing_capabilities"]
            )
            assert set(record["available_capabilities"]) | set(
                record["missing_capabilities"]
            ) == set(record["required_capabilities"])
            assert set(record["capability_evidence"]) == set(
                record["available_capabilities"]
            )
            assert all(record["capability_evidence"].values())
            supported = audit["backend_capabilities"][backend]["capabilities"]
            assert set(record["available_capabilities"]) <= set(supported)
            assert set(record["missing_capabilities"]).isdisjoint(supported)
            if record["status"] == "implemented":
                assert record["witness_cases"]
                assert set(record["witness_cases"]) <= known_cases
                assert all(
                    (case_id, backend) in verified
                    for case_id in record["witness_cases"]
                )
                assert record["missing_capabilities"] == []
            else:
                assert record["witness_cases"] == []
            if record["status"] == "implementable_unverified":
                assert record["missing_capabilities"] == []
            if record["status"] == "missing_capability":
                assert record["missing_capabilities"]
            assert record["reason"]


def test_strict_whole_problem_coverage_counts() -> None:
    summary = json.loads(
        (ROOT / "benchmark" / "problem_coverage.json").read_text()
    )["summary"]
    expected = {
        "thouless": {
            "implemented": 13,
            "implementable_unverified": 54,
            "missing_capability": 18,
            "not_applicable": 15,
        },
        "pythtb": {
            "implemented": 12,
            "implementable_unverified": 16,
            "missing_capability": 42,
            "not_applicable": 30,
        },
        "kwant": {
            "implemented": 13,
            "implementable_unverified": 46,
            "missing_capability": 21,
            "not_applicable": 20,
        },
    }
    for backend, counts in expected.items():
        for status, count in counts.items():
            assert summary[backend][status] == count
    for item in summary.values():
        assert (
            item["implemented"]
            + item["implementable_unverified"]
            + item["missing_capability"]
            + item["not_applicable"]
            == 100
        )
        assert item["verified_coverage_percent"] == item["implemented"]


def test_four_way_boundary_judgments_are_frozen() -> None:
    problems = json.loads(
        (ROOT / "benchmark" / "problem_coverage.json").read_text()
    )["problems"]
    by_id = {problem["id"]: problem["backends"] for problem in problems}

    # Generalized overlap is present in the pinned Thouless algebra layer, but
    # absent from the Hermitian PythTB and Kwant model contracts.
    assert by_id["TBQ-001"]["thouless"]["status"] == "implementable_unverified"
    assert by_id["TBQ-001"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-001"]["kwant"]["status"] == "missing_capability"
    for qid in ("TBQ-002", "TBQ-003", "TBQ-004", "TBQ-005"):
        assert by_id[qid]["thouless"]["status"] == "implementable_unverified"
        assert by_id[qid]["pythtb"]["status"] == "missing_capability"
        assert by_id[qid]["kwant"]["status"] == "missing_capability"

    # PythTB can do finite spectra but lacks the surface Green-function
    # primitive required by this otherwise in-scope boundary problem.
    assert by_id["TBQ-023"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-023"]["kwant"]["status"] == "implementable_unverified"

    # Requiring analytic, automatic, and finite-difference derivatives exposes
    # the lack of an automatic/adjoint differentiation path in all three.
    assert {
        record["status"] for record in by_id["TBQ-029"].values()
    } == {"missing_capability"}

    # The disorder suite explicitly includes non-Hermitian systems. Dense
    # non-Hermitian eigensystems suffice for ensemble construction, but the
    # large localization workflows need a sparse non-Hermitian solver.
    assert by_id["TBQ-031"]["thouless"]["status"] == "implementable_unverified"
    assert by_id["TBQ-031"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-031"]["kwant"]["status"] == "missing_capability"
    for qid in ("TBQ-032", "TBQ-033", "TBQ-034", "TBQ-035"):
        assert {
            record["status"] for record in by_id[qid].values()
        } == {"missing_capability"}

    # Open transport is outside PythTB's declared static band-theory scope.
    assert by_id["TBQ-036"]["pythtb"]["status"] == "not_applicable"

    # Mixed static/dynamic questions expose a missing propagator instead of
    # being hidden as out of scope.
    for qid in ("TBQ-044", "TBQ-072", "TBQ-074"):
        assert {
            record["status"] for record in by_id[qid].values()
        } == {"missing_capability"}

    # Thouless has general left/right eigensystems; PythTB and Kwant retain
    # Hermitian model contracts.
    assert by_id["TBQ-046"]["thouless"]["status"] == "implementable_unverified"
    assert by_id["TBQ-046"]["pythtb"]["status"] == "not_applicable"
    assert by_id["TBQ-046"]["kwant"]["status"] == "not_applicable"
    assert by_id["TBQ-048"]["thouless"]["status"] == "missing_capability"

    # Continuum-to-lattice BdG refinement needs a reusable discretizer.
    assert by_id["TBQ-045"]["thouless"]["status"] == "implementable_unverified"
    assert by_id["TBQ-045"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-045"]["kwant"]["status"] == "implementable_unverified"

    # The giant-supercell problem requires target sparse eigenpairs, which the
    # pinned Thouless revision does not yet provide.
    assert by_id["TBQ-064"]["thouless"]["status"] == "missing_capability"
    assert by_id["TBQ-064"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-064"]["kwant"]["status"] == "implementable_unverified"
    for qid in ("TBQ-063", "TBQ-065"):
        assert by_id[qid]["thouless"]["status"] == "missing_capability"
        assert by_id[qid]["pythtb"]["status"] == "missing_capability"
        assert by_id[qid]["kwant"]["status"] == "implementable_unverified"

    # The aperiodic suite reaches N=10^7. PythTB's dense model path therefore
    # cannot be called implementable merely because small graphs are possible.
    for qid in ("TBQ-076", "TBQ-077", "TBQ-078", "TBQ-079", "TBQ-080"):
        assert by_id[qid]["pythtb"]["status"] == "missing_capability"
    for qid in ("TBQ-078", "TBQ-080"):
        assert {
            record["status"] for record in by_id[qid].values()
        } == {"missing_capability"}

    # The optical and multiscale documents explicitly include non-orthogonal
    # and large sparse holdouts.
    assert by_id["TBQ-071"]["thouless"]["status"] == "implementable_unverified"
    assert by_id["TBQ-071"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-071"]["kwant"]["status"] == "missing_capability"
    assert by_id["TBQ-073"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-087"]["pythtb"]["status"] == "missing_capability"
    assert by_id["TBQ-087"]["kwant"]["status"] == "missing_capability"

    # The production solver portfolio includes a propagation task. Neither
    # applicable pinned backend exposes a real-time propagator.
    assert by_id["TBQ-091"]["thouless"]["status"] == "missing_capability"
    assert by_id["TBQ-091"]["pythtb"]["status"] == "not_applicable"
    assert by_id["TBQ-091"]["kwant"]["status"] == "missing_capability"

    # Inference is outside all three packages' declared solver scopes.
    assert {
        record["status"] for record in by_id["TBQ-096"].values()
    } == {"not_applicable"}
