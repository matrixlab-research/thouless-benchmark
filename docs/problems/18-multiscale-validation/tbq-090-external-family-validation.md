---
id: TBQ-090
suite: 18-multiscale-validation
source_requirement: TB-REQ-090
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-090 — External-family validation

## Scientific question

Does a calibrated tight-binding workflow predict a material or geometry family never
used in construction?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Matched analytic, continuum, lattice, first-principles, or experiment-like descriptions
of the same physical system and observable.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `a/L` | lattice-to-device scale ratio | 1e-4 to 0.2 | dimensionless |
| `k_max*a` | continuum fitting window | 0.01 to 1.0 | dimensionless |
| `epsilon_ref` | reference uncertainty | 1e-5 to 0.10 | observable units |
| `N_band` | retained low-energy bands | 1 to 32 | count |
| `L/a` | finite sample size | 20 to 10000 | lattice constants |

## Required computation

Freeze model-selection rules and tolerances, then evaluate the held-out external family.

## Expected result

Predictions are accompanied by calibrated uncertainty and no hidden-family data are used
to retune parameters.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Predeclared acceptance gate passes or failure is reported without tolerance changes.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

The complete external family is isolated until final scoring.

Suite-wide isolation rule: Hold out a material, device geometry, scale ratio, or experimental condition from model
selection and tolerance tuning.

## Evidence

- LKM seeds: `gcn_c9883ef775314033`, `gcn_d2c6245554f04bd1`, and `gcn_3226df8d95374015`.
- Representative source: [Transparent Graphene-Superconductor Interfaces: Quantum Hall and Zero Field Regimes](https://doi.org/10.48550/arXiv.2502.13307).
- Source requirement: [`TB-REQ-090`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
