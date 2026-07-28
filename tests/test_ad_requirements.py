import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ad_requirements_are_one_to_one_and_semantically_valid() -> None:
    subprocess.run(
        [sys.executable, "tools/check_ad_requirements.py"],
        cwd=ROOT,
        check=True,
    )


def test_generated_ad_requirement_artifacts_are_current() -> None:
    subprocess.run(
        [sys.executable, "tools/build_ad_requirements.py", "--check"],
        cwd=ROOT,
        check=True,
    )


def test_ad_requirement_statuses_do_not_overstate_full_tbq_coverage() -> None:
    payload = json.loads((ROOT / "benchmark" / "ad_requirements.json").read_text())
    assert len(payload["problems"]) == 100
    assert payload["summary"]["questions_with_existing_witnesses"] == 14
    assert payload["summary"]["status_counts"]["ad_native_verified"] == 14
    assert payload["summary"]["status_counts"]["implementable_unverified"] > 0
    assert (
        "source TBQ"
        in payload["status_vocabulary"]["ad_native_verified"]
    )


def test_tbq_073_distinguishes_thermopower_and_finite_bias_derivatives() -> None:
    problems = {
        problem["tbq_id"]: problem
        for problem in json.loads(
            (ROOT / "benchmark" / "ad_requirements.json").read_text()
        )["problems"]
    }
    requirement = problems["TBQ-073"]
    text = " ".join(
        requirement["continuous_controls"]
        + requirement["scientific_outputs"]
        + [requirement["differentiable_formulation"], requirement["validity_boundary"]]
    ).lower()
    assert "energy" in text and "seebeck" in text
    assert "bias" in text and "differential conductance" in text
