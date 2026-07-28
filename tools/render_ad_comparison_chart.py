#!/usr/bin/env python3
"""Render the paired native-AD and finite-difference medians as SVG."""

from __future__ import annotations

import argparse
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path


CASE_LABELS = {
    "adcmp_spectral_recovery": "Spectral parameter recovery",
    "adcmp_degenerate_projector": "Degenerate projector gradient",
    "adcmp_identifiability": "SSH identifiability Jacobian",
    "adcmp_quantum_metric": "Quantum-metric gradient",
    "adcmp_topological_design": "Topological inverse design",
    "adcmp_surface_green_implicit": "Surface Green-function gradient",
    "adcmp_inverse_transport": "Inverse transport calibration",
    "adcmp_lead_device_sensitivity": "Whole device-lead sensitivity",
    "adcmp_sparse_adjoint_scaling": "Sparse-adjoint scaling",
    "adcmp_robust_kpm_design": "Disorder-robust KPM design",
}
CASE_ORDER = tuple(CASE_LABELS)


@dataclass(frozen=True)
class TimingPair:
    case_id: str
    label: str
    native_ad_ms: float
    finite_difference_ms: float

    @property
    def speedup(self) -> float:
        return self.finite_difference_ms / self.native_ad_ms


@dataclass(frozen=True)
class ChartData:
    pairs: tuple[TimingPair, ...]
    machine: str
    system: str
    repetitions: int
    native_ad_faster: int
    median_speedup: float


def _positive_finite(value: object, context: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"{context} must be positive and finite, found {number}")
    return number


def load_chart_data(path: Path) -> ChartData:
    payload = json.loads(path.read_text())
    records = payload["records"]
    by_id = {record["case_id"]: record for record in records}
    if len(records) != len(by_id):
        raise ValueError("comparison snapshot contains duplicate case identifiers")
    expected = set(CASE_ORDER)
    missing = expected - by_id.keys()
    extra = by_id.keys() - expected
    if missing or extra:
        raise ValueError(
            "comparison snapshot does not match the chart catalog: "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )

    pairs = []
    for case_id in CASE_ORDER:
        record = by_id[case_id]
        if record["representative_result"]["status"] != "passed":
            raise ValueError(f"{case_id} does not have a passing representative")
        repetitions = int(record["repetitions"])
        if repetitions < 3:
            raise ValueError(f"{case_id} has fewer than three repetitions")
        native_ad_ms = (
            _positive_finite(
                record["native_ad_seconds"]["median"],
                f"{case_id} native-AD median",
            )
            * 1_000
        )
        finite_difference_ms = (
            _positive_finite(
                record["central_finite_difference_seconds"]["median"],
                f"{case_id} finite-difference median",
            )
            * 1_000
        )
        pair = TimingPair(
            case_id=case_id,
            label=CASE_LABELS[case_id],
            native_ad_ms=native_ad_ms,
            finite_difference_ms=finite_difference_ms,
        )
        recorded_speedup = _positive_finite(
            record["speedup_finite_difference_over_ad"],
            f"{case_id} speedup",
        )
        if not math.isclose(pair.speedup, recorded_speedup, rel_tol=1.0e-12):
            raise ValueError(f"{case_id} speedup is inconsistent with its medians")
        pairs.append(pair)

    repetitions = int(payload["summary"]["repetitions_per_record"])
    if any(record["repetitions"] != repetitions for record in records):
        raise ValueError("comparison snapshot mixes repetition counts")
    speedups = sorted(pair.speedup for pair in pairs)
    middle = len(speedups) // 2
    median_speedup = (speedups[middle - 1] + speedups[middle]) / 2.0
    native_ad_faster = sum(pair.speedup > 1.0 for pair in pairs)
    if payload["summary"]["native_ad_faster"] != native_ad_faster:
        raise ValueError("comparison summary has an inconsistent AD win count")
    if not math.isclose(
        payload["summary"]["median_speedup_finite_difference_over_ad"],
        median_speedup,
        rel_tol=1.0e-12,
    ):
        raise ValueError("comparison summary has an inconsistent median speedup")

    platform = payload["platform"]
    return ChartData(
        pairs=tuple(pairs),
        machine=str(platform["machine"]),
        system=str(platform["system"]),
        repetitions=repetitions,
        native_ad_faster=native_ad_faster,
        median_speedup=median_speedup,
    )


def _text(value: object) -> str:
    return html.escape(str(value), quote=True)


def _time_label(milliseconds: float) -> str:
    if milliseconds < 0.01:
        return f"{milliseconds:.3f}"
    if milliseconds < 1.0:
        return f"{milliseconds:.3f}"
    if milliseconds < 100.0:
        return f"{milliseconds:.2f}"
    return f"{milliseconds:.1f}"


def _tick_label(milliseconds: float) -> str:
    if milliseconds < 1.0:
        return f"{milliseconds * 1_000:g} μs"
    if milliseconds < 1_000:
        return f"{milliseconds:g} ms"
    return f"{milliseconds / 1_000:g} s"


def render_svg(data: ChartData) -> str:
    if len(data.pairs) != len(CASE_ORDER):
        raise ValueError(
            f"expected {len(CASE_ORDER)} timing pairs, found {len(data.pairs)}"
        )

    width = 1180
    left = 330
    right = 265
    top = 174
    bottom = 80
    row_height = 64
    finite_difference_bar_height = 30
    native_ad_bar_height = 16
    plot_width = width - left - right
    annotation_x = left + plot_width + 18
    height = top + row_height * len(data.pairs) + bottom

    minimum_ms = 10 ** math.floor(
        math.log10(
            min(
                min(pair.native_ad_ms, pair.finite_difference_ms)
                for pair in data.pairs
            )
        )
    )
    maximum_ms = 10 ** math.ceil(
        math.log10(
            max(
                max(pair.native_ad_ms, pair.finite_difference_ms)
                for pair in data.pairs
            )
        )
    )
    logarithmic_span = math.log10(maximum_ms / minimum_ms)

    def x_for(milliseconds: float) -> float:
        fraction = math.log10(milliseconds / minimum_ms) / logarithmic_span
        return left + fraction * plot_width

    subtitle = (
        f"{data.machine} {data.system} · {data.repetitions} warmed repetitions · "
        "median method time, lower is better"
    )
    summary = (
        f"AD faster in {data.native_ad_faster}/{len(data.pairs)} workflows · "
        f"median {data.median_speedup:.2f}×"
    )
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            'aria-labelledby="chart-title chart-desc">'
        ),
        '<title id="chart-title">Native AD versus central finite differences</title>',
        (
            '<desc id="chart-desc">Overlaid horizontal bars compare native '
            'automatic differentiation and central finite differences for ten '
            'scientific workflows on a logarithmic time axis. Each row reports '
            'the same-machine median times and finite-difference over AD speedup.</desc>'
        ),
        '<rect width="100%" height="100%" rx="12" fill="#ffffff"/>',
        (
            '<text class="chart-heading" x="28" y="46" '
            'font-family="system-ui, sans-serif" font-size="28" '
            'font-weight="700" fill="#172033">'
            'Native AD versus central finite differences</text>'
        ),
        (
            '<text class="chart-subtitle" x="28" y="78" '
            'font-family="system-ui, sans-serif" font-size="15" '
            f'fill="#596579">{_text(subtitle)}</text>'
        ),
        (
            '<rect class="summary-badge" x="826" y="24" width="326" '
            'height="42" rx="21" fill="#edf4ff"/>'
        ),
        (
            '<text class="summary-label" x="989" y="51" text-anchor="middle" '
            'font-family="system-ui, sans-serif" font-size="15" '
            f'font-weight="700" fill="#205493">{_text(summary)}</text>'
        ),
        '<rect x="28" y="101" width="24" height="16" rx="3" fill="#377eb8"/>',
        (
            '<text class="legend-label" x="62" y="115" '
            'font-family="system-ui, sans-serif" font-size="15" '
            'fill="#344054">Native AD</text>'
        ),
        '<rect x="171" y="94" width="24" height="30" rx="3" fill="#e7a568"/>',
        (
            '<text class="legend-label" x="205" y="115" '
            'font-family="system-ui, sans-serif" font-size="15" '
            'fill="#344054">Central finite difference</text>'
        ),
        (
            '<text class="scale-note" x="450" y="115" '
            'font-family="system-ui, sans-serif" font-size="14" '
            'fill="#667085">logarithmic time axis</text>'
        ),
    ]

    tick = minimum_ms
    while tick <= maximum_ms * (1.0 + 1.0e-12):
        x = x_for(tick)
        lines.extend(
            [
                (
                    f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" '
                    f'y2="{height - bottom + 4}" stroke="#e6e9ef" '
                    'stroke-width="1"/>'
                ),
                (
                    f'<text class="tick-label" x="{x:.2f}" '
                    f'y="{height - bottom + 30}" text-anchor="middle" '
                    'font-family="system-ui, sans-serif" font-size="13" '
                    f'fill="#667085">{_text(_tick_label(tick))}</text>'
                ),
            ]
        )
        tick *= 10.0
    lines.append(
        (
            f'<text class="axis-label" x="{left + plot_width / 2:.2f}" '
            f'y="{height - 18}" text-anchor="middle" '
            'font-family="system-ui, sans-serif" font-size="15" '
            'fill="#475467">median method time (log scale)</text>'
        )
    )

    for index, pair in enumerate(data.pairs):
        row_top = top + index * row_height
        center = row_top + row_height / 2
        finite_difference_y = center - finite_difference_bar_height / 2
        native_ad_y = center - native_ad_bar_height / 2
        if index % 2:
            lines.append(
                (
                    f'<rect class="row-guide" x="20" y="{row_top + 2:.2f}" '
                    f'width="{width - 40}" height="{row_height - 4}" rx="6" '
                    'fill="#fafbfc" fill-opacity="0.68"/>'
                )
            )
        lines.append(
            (
                f'<text class="workflow-label" x="{left - 16}" '
                f'y="{center + 5:.2f}" text-anchor="end" '
                'font-family="system-ui, sans-serif" font-size="15" '
                f'font-weight="600" fill="#283548">{_text(pair.label)}</text>'
            )
        )
        for method, value, y, bar_height, color, css_class in (
            (
                "Central finite difference",
                pair.finite_difference_ms,
                finite_difference_y,
                finite_difference_bar_height,
                "#e7a568",
                "finite-difference-bar",
            ),
            (
                "Native AD",
                pair.native_ad_ms,
                native_ad_y,
                native_ad_bar_height,
                "#377eb8",
                "native-ad-bar",
            ),
        ):
            bar_width = max(1.5, x_for(value) - left)
            lines.append(
                (
                    f'<rect class="{css_class}" '
                    f'data-case-id="{_text(pair.case_id)}" '
                    f'data-center-y="{center:.2f}" x="{left}" y="{y:.2f}" '
                    f'width="{bar_width:.2f}" height="{bar_height}" rx="4" '
                    f'fill="{color}"><title>{_text(method)}: '
                    f'{value:.6f} ms</title></rect>'
                )
            )
        lines.extend(
            [
                (
                    f'<text class="speedup-label" '
                    f'data-case-id="{_text(pair.case_id)}" '
                    f'x="{annotation_x:.2f}" y="{center - 3:.2f}" '
                    'font-family="system-ui, sans-serif" font-size="15" '
                    f'font-weight="700" fill="#205493">'
                    f'AD {pair.speedup:.2f}× faster</text>'
                ),
                (
                    f'<text class="timing-label" '
                    f'data-case-id="{_text(pair.case_id)}" '
                    f'x="{annotation_x:.2f}" y="{center + 17:.2f}" '
                    'font-family="ui-monospace, SFMono-Regular, monospace" '
                    'font-size="12.5" fill="#667085">'
                    f'AD {_time_label(pair.native_ad_ms)} · '
                    f'FD {_time_label(pair.finite_difference_ms)} ms</text>'
                ),
            ]
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    chart = render_svg(load_chart_data(args.result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(chart)


if __name__ == "__main__":
    main()
