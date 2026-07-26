from pathlib import Path

from thouless_benchmark.manifest import load_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_has_expected_shape() -> None:
    cases = load_manifest(ROOT / "benchmark" / "cases.json")
    assert len(cases) == 20
    assert sum(case.track == "bulk" for case in cases) == 12
    assert sum(case.track == "boundary" for case in cases) == 4
    assert sum(case.track == "transport" for case in cases) == 4
    assert all("thouless" in case.backends for case in cases)
