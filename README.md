# Thouless benchmark

Twenty LKM-motivated, executable tight-binding workflows comparing native
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

The manifest is [`benchmark/cases.json`](benchmark/cases.json). It is the
canonical list of questions, parameters, applicability, observables,
tolerances, and provenance.

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
- Wall-clock and memory measurements are descriptive. CI does not assert that
  one backend must be faster.

## Status

The repository deliberately reports specification and implementation coverage
separately:

| Backend | Implemented | Applicable | Remaining |
|---|---:|---:|---:|
| Thouless native Rust | 9 | 20 | 11 |
| Original PythTB 2.0.0 | 8 | 16 | 8 |
| Original Kwant 1.5.0 | 8 | 19 | 11 |

The [verified result set](results/verified/2026-07-26-implemented.json) contains
nine end-to-end workflows: graphene Dirac cones, SSH polarization, Rice-Mele
pumping, the QWZ phase diagram, Weyl-node chirality, nodal-line Berry phase,
finite Fourier-Wannier interpolation, SSH end-state localization, and
ballistic-chain transmission. All twenty-five applicable backend-case
executions pass their analytic checks. The other eleven scientific questions
are specified but are not yet implemented; see [`benchmark/implementation.json`](benchmark/implementation.json)
and `python tools/coverage_report.py`.

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
```

Every completed workflow must satisfy
[`instructions/benchmark-implementation.md`](instructions/benchmark-implementation.md).

This is a public benchmark, not the isolated held-out evaluator for Thouless.
