---
id: TBQ-063
suite: 13-moire-strain-supercells
source_requirement: TB-REQ-063
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-063 — Continuum-atomistic correspondence

## Scientific question

Over which angle and energy window do continuum and atomistic descriptions agree?

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

Compare bandwidths, gaps, layer weights, velocities, and selected topology on matched
structures.

## Expected result

Agreement holds inside a declared low-energy window and degrades systematically when
lattice-scale processes become important.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Below 5 percent error in the declared shared regime with an explicit breakdown boundary.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide an angle near the edge of continuum validity.

Suite-wide isolation rule: Hold out twist angle, relaxation model, material pair, strain texture, and commensurate
index.

## Evidence

- LKM seeds: `gcn_01a4701e71284ca0`, `gcn_20c39b6a194e48e5`, and reasoning chain `928713876365640298_1`.
- Representative source: [Strain induced flat-band superconductivity and symmetry breaking](https://doi.org/10.48550/arXiv.2311.02824).
- Source requirement: [`TB-REQ-063`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
