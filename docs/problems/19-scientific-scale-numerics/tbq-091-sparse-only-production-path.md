---
id: TBQ-091
suite: 19-scientific-scale-numerics
source_requirement: TB-REQ-091
status: proposed
acceptance_class: scaling
lkm_snapshot: 2026-07-27
---

# TBQ-091 — Sparse-only production path

## Scientific question

Can large cases run without constructing an N by N dense Hamiltonian or dense
intermediate?

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

Instrument assembly and each production solver across N and z while checking storage
objects and peak memory.

## Expected result

Memory follows O(N z) plus solver workspace and the large case completes without dense
allocation.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `scaling`

Peak memory fits a declared linear-in-nonzeros envelope with less than 20 percent
unexplained growth.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a less regular sparsity pattern and largest N.

Suite-wide isolation rule: Hold out the largest size, sparsity pattern, spectral condition, and required
observable.

## Evidence

- LKM seeds: `gcn_61cc01e25fae41d8`, `gcn_e6394f2f69bb47a8`, and reasoning chain `811267572279279617_2`.
- Representative source: [Efficient Multiscale Lattice Simulations of Strained and Disordered Graphene](https://doi.org/10.1016/bs.semsem.2016.04.002).
- Source requirement: [`TB-REQ-091`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
