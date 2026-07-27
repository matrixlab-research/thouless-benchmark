---
id: TBQ-047
suite: 10-non-hermitian
source_requirement: TB-REQ-047
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-047 — Exceptional-point order and sensitivity

## Scientific question

Can exceptional points be distinguished from ordinary degeneracies?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Nonreciprocal SSH and two-dimensional gain-loss lattice families with point gaps, line
gaps, exceptional points, and skin localization.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `t_R/t_L` | hopping nonreciprocity | 0.2 to 5 | dimensionless |
| `gamma/t` | gain or loss strength | 0 to 3 | dimensionless |
| `m/t` | gap control | -2 to 2 | dimensionless |
| `L/a` | open-system size | 20 to 512 | cells |
| `W/t` | complex or real disorder | 0 to 4 | dimensionless |

## Required computation

Sweep around analytic second- and higher-order exceptional points and measure eigenvalue
branching, rank loss, and condition or pseudospectral growth.

## Expected result

Eigenvalues exhibit the expected root branching, eigenvectors coalesce, and sensitivity
diverges with the predicted exponent.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Branching exponent within 5 percent and correct geometric multiplicity.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide the exceptional-point order and perturbation direction.

Suite-wide isolation rule: Hold out boundary orientation, gain-loss pattern, exceptional-point order, and disorder
type.

## Evidence

- LKM seeds: `gcn_130f99edf2fc49a5`, `gcn_61de6af0dab44776`, and reasoning chain `867752662542582493_2`.
- Representative source: [Dissipative two-dimensional Raman lattice](https://doi.org/10.48550/arXiv.2211.00424).
- Source requirement: [`TB-REQ-047`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
