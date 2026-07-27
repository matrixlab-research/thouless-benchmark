---
id: TBQ-015
suite: 03-magnetic-flux-hofstadter
source_requirement: TB-REQ-015
status: proposed
acceptance_class: convergence
lkm_snapshot: 2026-07-27
---

# TBQ-015 — Rational-approximant convergence

## Scientific question

Which magnetic observables converge as an irrational target flux is approached by
rational sequences?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Square, triangular, and honeycomb lattices with Peierls phases, including next-neighbour
hoppings and rational flux p/q per primitive plaquette.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `phi/phi0` | flux per plaquette | p/q with q=3 to 61 | flux quanta |
| `t2/t` | long-range hopping | 0 to 0.25 | dimensionless |
| `q` | magnetic denominator | 3 to 61 | integer |
| `L/a` | real-space linear size | 24 to 256 | lattice constants |
| `eta/t` | spectral broadening | 0.002 to 0.05 | dimensionless |

## Required computation

Evaluate integrated DOS, robust gaps, and local Chern markers along two continued-
fraction or alternative approximant sequences.

## Expected result

Stable gaps and integrated observables converge sequence-independently; nonconvergent
fine spectral structure is reported rather than forced to a scalar answer.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `convergence`

Agreement of stable integrated observables within 1 percent between the final two
sequence levels.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the irrational target and approximant sequence.

Suite-wide isolation rule: Hold out flux denominators, a gauge family, and one lattice with non-nearest-neighbour
loops.

## Evidence

- LKM seeds: `gcn_7ad8b68bedaa49b5`, `gcn_75ecf3d114d74c69`, and `gcn_7cc10d3d9e354922`.
- Representative source: [Hofstadter Topology with Real Space Invariants and Reentrant Projective Symmetries](https://doi.org/10.48550/arXiv.2209.10559).
- Source requirement: [`TB-REQ-015`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
