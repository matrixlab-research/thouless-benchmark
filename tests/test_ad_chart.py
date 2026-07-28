from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from render_ad_comparison_chart import CASE_ORDER, load_chart_data, render_svg


RESULT = (
    ROOT
    / "results"
    / "verified"
    / "2026-07-28-ad-vs-finite-difference.json"
)
CHART = ROOT / "docs" / "ad-vs-finite-difference.svg"


def test_committed_ad_chart_matches_verified_snapshot() -> None:
    data = load_chart_data(RESULT)
    rendered = render_svg(data)
    assert CHART.read_text() == rendered
    assert len(data.pairs) == 10
    assert data.native_ad_faster == 10
    assert data.repetitions == 7
    assert rendered.count('class="native-ad-bar"') == 10
    assert rendered.count('class="finite-difference-bar"') == 10
    assert rendered.count('class="speedup-label"') == 10
    assert rendered.count('class="timing-label"') == 10
    assert "logarithmic time axis" in rendered
    assert "AD faster in 10/10 workflows" in rendered
    assert "AD 36.50× faster" in rendered
    assert "Disorder-robust KPM design" in rendered
    assert all(f'data-case-id="{case_id}"' in rendered for case_id in CASE_ORDER)
    root = ET.fromstring(rendered)
    assert root.tag.endswith("svg")
    assert root.attrib["role"] == "img"


def test_chart_loader_rejects_missing_workflow(tmp_path: Path) -> None:
    payload = json.loads(RESULT.read_text())
    payload["records"].pop()
    path = tmp_path / "missing.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="does not match the chart catalog"):
        load_chart_data(path)


def test_chart_loader_rejects_inconsistent_speedup(tmp_path: Path) -> None:
    payload = json.loads(RESULT.read_text())
    payload["records"][0]["speedup_finite_difference_over_ad"] = 999.0
    path = tmp_path / "inconsistent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="speedup is inconsistent"):
        load_chart_data(path)
