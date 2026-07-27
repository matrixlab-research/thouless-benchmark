# Thouless benchmark

Twenty-five LKM-motivated, executable tight-binding workflows comparing native
[Thouless](https://github.com/matrixlab-research/thouless) Rust with the
original PythTB 2.0 and Kwant 1.5 packages.

The benchmark asks scientific questions rather than timing isolated kernels.
Each case defines a model, an observable, an analytic or invariant-based gate,
and its public LKM question and paper provenance. The source papers motivate
the questions; the compact lattice cases are explicitly benchmark adaptations,
not claims to reproduce those papers.

## Tracks

| Track | Cases | Backends |
|---|---:|---|
| Bulk bands and topology | 12 | Thouless, PythTB, and Kwant where applicable |
| Finite boundaries | 4 | Thouless, PythTB, and Kwant |
| Open-system transport | 4 | Thouless and Kwant; PythTB is not a transport solver |
| Whole-problem domain witnesses | 5 | Backend applicability is explicit |

The original manifest is [`benchmark/cases.json`](benchmark/cases.json).
Whole-problem witnesses are frozen in
[`benchmark/domain_cases.json`](benchmark/domain_cases.json).

## Domain problem catalog

The documentation system also contains
[100 domain-first scientific problem specifications](docs/problems/README.md),
organized into twenty research suites. Each problem has its own Markdown file
with:

- a scientific question and benchmark adaptation;
- parameter ranges, meanings, and units;
- the required calculation and expected result;
- acceptance, convergence, and held-out-family rules; and
- LKM and paper provenance.

These documents define benchmark problems before API design. Thirteen are now
marked `executable`; eighty-seven remain `proposed`. The canonical
[100-question by three-backend audit](benchmark/problem_coverage.json)
distinguishes complete implementation, partial capability, and scientific
non-applicability. A related model or single observable is not counted as a
whole-problem implementation.

## Comparison policy

- Correctness is primary. Analytic spectra, quantized invariants, symmetry
  transformations, bulk-boundary correspondence, and exact transport limits
  are the reference gates.
- Cross-backend agreement is reported but is never the sole source of truth.
- `not_applicable` is explicit and unscored.
- The original PythTB and Kwant packages are installed in an isolated Python
  environment. The repository rejects imports from a Thouless compatibility
  tree.
- Thouless is executed as a Rust binary pinned to an exact Git commit.
- Timing measurements are descriptive. CI does not assert that one backend
  must be faster.

## Status

The original twenty-case seed remains fully implemented:

| Backend | Implemented | Applicable | Remaining |
|---|---:|---:|---:|
| Thouless native Rust | 20 | 20 | 0 |
| Original PythTB 2.0.0 | 16 | 16 | 0 |
| Original Kwant 1.5.0 | 19 | 19 | 0 |

The [verified result set](results/verified/2026-07-26-implemented.json) contains
all twenty end-to-end workflows. The finite-boundary track includes SSH and
Haldane spectral flow, graphene termination signatures, and BBH corner modes.
The open-system track includes ballistic and resonant transport,
Aharonov-Bohm interference, and a disordered Hofstadter strip with
edge-localized bond current. All fifty-five applicable backend-case executions
pass their analytic or invariant-based checks. See
[`benchmark/implementation.json`](benchmark/implementation.json) and
`python tools/coverage_report.py`.

Strict whole-problem coverage of the 100-question catalog is:

| Backend | Implemented | Partial | Not applicable | Raw coverage |
|---|---:|---:|---:|---:|
| Thouless native Rust | 13 | 71 | 16 | 13% |
| Original PythTB 2.0.0 | 12 | 44 | 44 | 12% |
| Original Kwant 1.5.0 | 13 | 61 | 26 | 13% |

The five domain witnesses cover degeneracy-safe projectors and DOS state
counting, Bloch-to-finite spectral convergence, Peierls gauge covariance and
Hofstadter topology, BdG/Andreev/Majorana physics, analytic lead calibration,
and spin-texture covariance. `Partial` is a recorded gap, not coverage.

## Same-machine timing

The verified domain result contains seven repetitions per backend-case on one
arm64 macOS machine. Kernel time excludes import and process startup; process
wall time includes both. The table reports median kernel milliseconds:

| Workflow | PythTB | Kwant | Thouless |
|---|---:|---:|---:|
| Spectral reliability | 716.10 | 207.42 | 20.96 |
| Magnetic Hofstadter | 78.99 | 162.71 | 1.42 |
| BdG and Majorana | 14.50 | 40.21 | 1.52 |
| Lead calibration | not applicable | 10.89 | 0.14 |
| Spin-texture covariance | 11.60 | 10.06 | 4.48 |

Median process-wall ranges are 294–991 ms for PythTB, 524–735 ms for Kwant,
and 2.6–24.3 ms for Thouless. These numbers describe these complete adapters,
including their model-assembly choices; they are not isolated eigensolver
microbenchmarks. The local Kwant environment used SciPy's solver because MUMPS
was unavailable. See the
[raw repeated result](results/verified/2026-07-27-domain.json).

PythTB 2.0 requires NumPy 2, while Kwant 1.5 currently builds against NumPy
1.26. They therefore run in separate environments. Combining both into one
Python environment is not a supported benchmark configuration.

Local setup and execution:

```bash
uv sync --python 3.12 --extra pythtb --extra test
uv venv --python 3.12 .venv-kwant
uv pip install --python .venv-kwant/bin/python \
  -r requirements/kwant-build.txt
uv pip install --python .venv-kwant/bin/python --no-build-isolation \
  tinyarray==1.2.5 kwant==1.5.0
uv pip install --python .venv-kwant/bin/python --no-deps -e .
python tools/collect_seed.py
python tools/collect_domain_results.py
python tools/build_problem_coverage.py --check
python tools/check_problem_docs.py
```

Every completed workflow must satisfy
[`instructions/benchmark-implementation.md`](instructions/benchmark-implementation.md).

This is a public benchmark, not the isolated held-out evaluator for Thouless.
