# Native automatic-differentiation benchmarks

This track turns LKM-discovered research workflows and the AD requirements in
[issue #6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)
into ten executable Rust-native benchmarks. Each case now names a physical
system, a source paper, and a compact adaptation boundary; the selection is
not ten variations of a scalar derivative test.

The correctness track uses native Thouless JVPs and VJPs. Central finite
differences are independent validators only in that track. A separate
[paired method comparison](ad-method-comparison.md) runs complete central
finite-difference gradients and optimizations as an explicit no-AD baseline.
Optimizers and loss composition remain a thin benchmark layer outside the
physics kernels.

## Selection

| Case | Scientific problem type | Motivating questions | Native AD gates | Independent evidence |
|---|---|---|---|---|
| `ad_spectral_recovery` | Rice-Mele parameter inference | TBQ-096, TBQ-099 | AD-G01, AD-G11 | Known parameters and excluded momenta |
| `ad_degenerate_projector` | BHZ Kramers subspace | TBQ-006, TBQ-097 | AD-G04 | Basis rotation and exact-degeneracy negative control |
| `ad_identifiability` | SSH hopping identifiability | TBQ-098 | AD-G14 | Analytic hopping-swap nullspace and a local marker |
| `ad_quantum_metric` | Rice-Mele quantum geometry | TBQ-026, TBQ-029 | AD-G01, AD-G02, AD-G15 | Basis covariance and mesh refinement |
| `ad_topological_design` | QWZ Chern inverse design | TBQ-017, TBQ-030 | AD-G16 | Independent Chern calculation and resolved gap closing |
| `ad_surface_green_implicit` | SSH boundary Green function | TBQ-023, TBQ-036 | AD-G02, AD-G09, AD-G10 | Adjoint identity, retarded branch, and tolerance stability |
| `ad_inverse_transport` | Double-quantum-dot inference | TBQ-040, TBQ-099 | AD-G12, AD-G13 | Non-AD forward solve at excluded energies |
| `ad_lead_device_sensitivity` | Resonant-level contact sensitivity | TBQ-036, TBQ-040 | AD-G09, AD-G12 | Device, lead, interface, energy, and broadening contributions |
| `ad_sparse_adjoint_scaling` | Anderson sparse adjoint | TBQ-094, TBQ-097 | AD-G07, AD-G08 | Residuals, derivative agreement, and solve counts |
| `ad_robust_kpm_design` | Disordered SSH KPM design | TBQ-094, TBQ-100 | AD-G08, AD-G17 | Training disorder and public unseen seeds |

The canonical machine-readable definitions, including physical systems,
source papers, LKM node identifiers, parameters, oracles, and required checks,
are in
[`benchmark/ad_cases.json`](../benchmark/ad_cases.json).
The raw discovery and reasoning responses are in
[`evidence/lkm/2026-07-28-ad-research-workflows`](../evidence/lkm/2026-07-28-ad-research-workflows/README.md).

## What is actually tested

Every case must pass three scientific checks:

- **Derivative truth:** a directional finite difference, an adjoint identity,
  an analytic nullspace, or another independently defined relation.
- **Workflow result:** parameter recovery, loss reduction, an invariant change,
  or a converged sensitivity result.
- **Generalization or failure semantics:** excluded momenta or energies, unseen
  public disorder seeds, basis covariance, mesh/tolerance refinement, or an
  explicit nonsmooth negative control.

The topological case never differentiates a Chern number. It optimizes a smooth
projector objective, then recomputes the integer invariant through a separate
forward path and verifies that the phase change crosses a resolved gap closing.

The surface-Green-function case differentiates the converged fixed-point
equation. Its acceptance is therefore based on the physical retarded solution,
JVP/VJP duality, finite differences, and solver-tolerance stability rather than
agreement with an unrolled iteration trace.

The sparse cases report numerical cost as well as correctness. At 64
parameters, the adjoint linear-solve case uses two linear systems while a
central parameter-wise difference would require 128. The checkpointed KPM case
reports 824 native operator applications versus 2,240 for the declared
finite-difference baseline, while storing 19 vectors instead of the full
36-vector recurrence.

## Verified snapshot

The
[`2026-07-28 research-workflow result`](../results/verified/2026-07-28-ad-research-workflows.json)
contains seven same-machine repetitions for all ten cases. All 30 required
scientific checks pass against Thouless commit
`237f544c497e89cd99dedd68f16e399bc9980987`.

Median native-kernel times on the recorded arm64 macOS machine are:

| Case | Median kernel time |
|---|---:|
| Rice-Mele spectral recovery | 3.555 ms |
| BHZ degenerate projector | 0.094 ms |
| SSH identifiability | 0.081 ms |
| Rice-Mele quantum metric | 0.867 ms |
| QWZ topological design | 37.723 ms |
| Implicit surface Green function | 0.060 ms |
| Double-dot inverse transport | 2.990 ms |
| Resonant-level sensitivity | 0.101 ms |
| Anderson sparse adjoint | 0.809 ms |
| Disordered SSH KPM design | 3,085.887 ms |

These timings describe complete benchmark workflows and are not cross-package
speed claims. The KPM workflow includes 360 optimization iterations across
eight disorder realizations; its longer runtime is therefore not comparable
to a single gradient evaluation.

## Generality boundary

The public excluded momenta, energies, and disorder seeds catch elementary
overfitting during development. They are visible to implementations and
therefore do **not** satisfy AD-G18. Isolated held-out evaluation remains the
responsibility of [issue #3](https://github.com/matrixlab-research/thouless-benchmark/issues/3).

Likewise, a case's `question_ids` record which domain requirements motivated
it. An AD witness does not mark the complete TBQ problem as implemented unless
all of that problem's forward physics, scale, convergence, and held-out gates
are separately satisfied.

## Run

```bash
cargo build --release --manifest-path backends/thouless/Cargo.toml
python tools/run_thouless_cases.py --track ad
python tools/collect_ad_results.py
python tools/check_ad_results.py --current results/local/ad.json
python tools/run_thouless_cases.py --track ad-comparison
python tools/collect_ad_comparison.py
python tools/check_ad_comparison.py \
  results/local/ad-vs-finite-difference.json
```
