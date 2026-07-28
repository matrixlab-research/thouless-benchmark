# Native AD versus no-AD baseline

This benchmark compares native Thouless automatic differentiation with a
central finite-difference baseline on the same ten research workflows. It does
not compare isolated derivative APIs.

The no-AD path calls only the Rust forward objective. For a scalar objective
with \(P\) parameters, one complete finite-difference gradient requires the
center value and \(2P\) displaced forward evaluations. Native AD returns the
same complete gradient through the corresponding analytic JVP or VJP rule.

## Fairness contract

Both methods use:

- the same Rust physical model and objective;
- the same physical parameter coordinates;
- the same requested scientific product;
- the same initial parameters, stopping conditions, maximum iterations, and
  forward-only backtracking line search for optimization workflows; and
- the same process and machine for each paired measurement.

Four cases compare complete end-to-end optimizations. Five compare a complete
physical-coordinate gradient, and the identifiability case compares the full
five-observable Jacobian and its Fisher spectrum. The finite-difference step is
fixed at \(10^{-6}\).

Correctness and scientific equivalence are CI gates. Relative speed is
descriptive and is never a CI gate.

## Verified result

The
[seven-repetition paired snapshot](../results/verified/2026-07-28-ad-vs-finite-difference.json)
was measured on the recorded arm64 macOS machine. Times below are medians of
the method-specific workload measured inside the same Rust process. “Speedup”
is finite-difference time divided by native-AD time, so a value greater than
one favors AD.

| Scientific workflow | Native AD | No AD | Speedup |
|---|---:|---:|---:|
| Rice-Mele spectral recovery | 2.634 ms | 10.044 ms | 3.81× |
| BHZ degenerate projector gradient | 0.003 ms | 0.012 ms | 4.66× |
| SSH identifiability Jacobian | 0.006 ms | 0.023 ms | 4.23× |
| Rice-Mele quantum-metric gradient | 0.109 ms | 0.482 ms | 4.44× |
| QWZ topological design | 18.535 ms | 35.796 ms | 1.93× |
| Implicit surface Green-function gradient | 0.006 ms | 0.030 ms | 4.72× |
| Double-dot inverse transport | 2.746 ms | 8.150 ms | 2.97× |
| Whole device-lead sensitivity | 0.014 ms | 0.364 ms | 26.76× |
| Anderson sparse-adjoint scaling | 0.236 ms | 8.604 ms | 36.50× |
| Disorder-robust SSH KPM design | 1,184.933 ms | 1,794.567 ms | 1.51× |

Native AD is faster in all ten recorded warmed workloads, with a median
speedup of 4.33×. The advantage becomes large when one reverse solve replaces
parameter-wise repeated solves. In the Anderson workflow, the complete 8-,
32-, and 64-parameter sweep uses six native linear systems versus 211 forward
finite-difference systems. The one-parameter QWZ design and four-parameter KPM
design show the smaller gains expected when parameter-wise differencing needs
only a few additional forward passes.

The KPM speedup is more modest because it has four parameters and the
checkpointed reverse pass intentionally recomputes part of the recurrence to
bound memory. Its measured end-to-end optimization executes 1,057,960 native
operator applications versus 1,668,520 without AD.

All ten complete gradients or Jacobians agree within their declared
tolerances, and both methods produce equivalent scientific results. The
largest recorded full-gradient relative error is \(1.55\times10^{-5}\) in the
64-parameter iterative sparse solve; the paired scientific outputs remain
equal at the recorded tolerance. The speed ordering is reported rather than
required, so a future workload where finite differences win will remain a
valid benchmark result.

## Reproduce

```bash
cargo build --release --manifest-path backends/thouless/Cargo.toml
python tools/run_thouless_cases.py --track ad-comparison
python tools/collect_ad_comparison.py
python tools/check_ad_comparison.py \
  results/local/ad-vs-finite-difference.json
```

The machine-readable workload definitions and fairness contract are in
[`benchmark/ad_comparison.json`](../benchmark/ad_comparison.json).
