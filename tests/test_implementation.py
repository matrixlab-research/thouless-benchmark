import json
from pathlib import Path

from thouless_benchmark.manifest import load_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_implementation_claims_are_applicable_and_known() -> None:
    cases = load_manifest(ROOT / "benchmark" / "cases.json")
    by_id = {case.id: case for case in cases}
    status = json.loads((ROOT / "benchmark" / "implementation.json").read_text())
    for backend, implemented in status["implemented"].items():
        assert len(implemented) == len(set(implemented))
        for case_id in implemented:
            assert case_id in by_id
            assert backend in by_id[case_id].backends


def test_seed_has_one_common_case_per_scientific_track() -> None:
    cases = load_manifest(ROOT / "benchmark" / "cases.json")
    by_id = {case.id: case for case in cases}
    status = json.loads((ROOT / "benchmark" / "implementation.json").read_text())
    common = set.intersection(*(set(items) for items in status["implemented"].values()))
    assert {by_id[case_id].track for case_id in common} == {"bulk", "boundary"}
    assert any(
        by_id[case_id].track == "transport"
        for case_id in set(status["implemented"]["thouless"])
        & set(status["implemented"]["kwant"])
    )
