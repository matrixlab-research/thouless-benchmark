---
id: TBQ-072
suite: 15-optical-thermoelectric
source_requirement: TB-REQ-072
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-072 — Optical spectral-sum and time-domain agreement

## Scientific question

Do independent Kubo formulations produce the same optical conductivity?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Clean and disordered multi-band lattices evaluated by spectral-sum and time-domain Kubo
formulations, with charge and heat currents derived from the model.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `omega/t` | probe frequency | 0 to 10 | dimensionless |
| `eta/t` | spectral broadening | 0.001 to 0.20 | dimensionless |
| `kBT/t` | temperature | 0.001 to 0.50 | dimensionless |
| `mu/t` | chemical potential | -4 to 4 | dimensionless |
| `N_t` | time-propagation steps | 1e3 to 1e6 | count |

## Required computation

Compute sigma(omega) by eigenstate sums and real-time propagation for sizes where both
are feasible.

## Expected result

Peak positions, integrated weight, and complex conductivity agree after matching
broadening and finite-time resolution.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Integrated spectral-weight mismatch below 1 percent and peak error below the stated
resolution.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a multiband interband transition.

Suite-wide isolation rule: Hold out a lattice family, disorder regime, and a system size requiring a non-
diagonalization method.

## Evidence

- LKM seeds: `gcn_372abc282cf6400a`, `gcn_b74a9f94ce394173`, and `gcn_da7d99ec9d9c470d`.
- Representative source: [TBPLaS: a Tight-Binding Package for Large-scale Simulation](https://doi.org/10.48550/arXiv.2209.00806).
- Source requirement: [`TB-REQ-072`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
