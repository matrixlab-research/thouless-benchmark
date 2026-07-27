---
id: TBQ-094
suite: 19-scientific-scale-numerics
source_requirement: TB-REQ-094
status: executable
acceptance_class: scaling
lkm_snapshot: 2026-07-27
---

# TBQ-094 — Accuracy-preserving time and memory scaling

## Scientific question

How do runtime and peak memory grow when scientific error, rather than iteration count,
is held fixed?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Sparse short-range lattice families scaled from exactly solvable small systems to
millions of orbitals for spectra, Green functions, propagation, and response.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `N` | Hamiltonian dimension | 1e2 to 1e7 | orbitals |
| `z` | mean nonzeros per row | 3 to 100 | count |
| `N_ev` | requested eigenpairs | 1 to 256 | count |
| `M` | polynomial or Krylov order | 50 to 20000 | count |
| `epsilon` | target observable error | 1e-2 to 1e-10 | dimensionless |

## Required computation

Choose M, tolerances, and samples adaptively to maintain epsilon across an N ladder and
record hardware and solver metadata.

## Expected result

Accuracy remains fixed while measured scaling reflects the intended algorithm; a faster
but inaccurate run does not pass.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `scaling`

All sizes meet epsilon and fitted exponents include confidence intervals and raw
measurements.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a more difficult spectral condition at large N.

Suite-wide isolation rule: Hold out the largest size, sparsity pattern, spectral condition, and required
observable.

## Evidence

- LKM seeds: `gcn_61cc01e25fae41d8`, `gcn_e6394f2f69bb47a8`, and reasoning chain `811267572279279617_2`.
- Representative source: [Efficient Multiscale Lattice Simulations of Strained and Disordered Graphene](https://doi.org/10.1016/bs.semsem.2016.04.002).
- Source requirement: [`TB-REQ-094`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_sparse_numerics. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
