---
id: TBQ-064
suite: 13-moire-strain-supercells
source_requirement: TB-REQ-064
status: proposed
acceptance_class: scaling
lkm_snapshot: 2026-07-27
---

# TBQ-064 — Sparse observables in giant supercells

## Scientific question

Can physically useful spectra and local observables be obtained when full
diagonalization is impossible?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Commensurate and approximant bilayer or strained monolayer lattices with registry- and
geometry-dependent hopping, plus matched continuum descriptions.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `theta` | twist angle | 0.8 to 5.0 | degree |
| `epsilon` | strain amplitude | -0.05 to 0.05 | fraction |
| `u/a` | relaxation displacement | 0 to 0.15 | lattice constants |
| `r0/a` | hopping decay length | 0.1 to 1.0 | lattice constants |
| `N_orb` | supercell orbitals | 1e3 to 1e7 | count |

## Required computation

Compute target eigenpairs, DOS, and local density across N_orb up to the largest
feasible sparse case.

## Expected result

Sparse results reproduce small dense references and retain fixed accuracy with memory
proportional to nonzero Hamiltonian entries.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `scaling`

Small-case error below tolerance and no dense N_orb squared allocation on large cases.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the largest cell and a less sparse coupling cutoff.

Suite-wide isolation rule: Hold out twist angle, relaxation model, material pair, strain texture, and commensurate
index.

## Evidence

- LKM seeds: `gcn_01a4701e71284ca0`, `gcn_20c39b6a194e48e5`, and reasoning chain `928713876365640298_1`.
- Representative source: [Strain induced flat-band superconductivity and symmetry breaking](https://doi.org/10.48550/arXiv.2311.02824).
- Source requirement: [`TB-REQ-064`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
