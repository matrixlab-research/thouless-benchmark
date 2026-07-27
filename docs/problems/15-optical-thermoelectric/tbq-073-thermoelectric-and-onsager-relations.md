---
id: TBQ-073
suite: 15-optical-thermoelectric
source_requirement: TB-REQ-073
status: executable
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-073 — Thermoelectric and Onsager relations

## Scientific question

Do electrical, thermoelectric, and thermal coefficients satisfy reciprocity and known
low-temperature limits?

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

Compute the linear-response matrix versus mu, T, and magnetic-field reversal.

## Expected result

Onsager-Casimir relations hold, thermopower vanishes at particle-hole symmetry, and the
low-T Mott or Wiedemann-Franz limit is recovered where applicable.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Reciprocity residual below 1e-6 and low-T relative error below 2 percent.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide weak particle-hole asymmetry and reversed field.

Suite-wide isolation rule: Hold out a lattice family, disorder regime, and a system size requiring a non-
diagonalization method.

## Evidence

- LKM seeds: `gcn_372abc282cf6400a`, `gcn_b74a9f94ce394173`, and `gcn_da7d99ec9d9c470d`.
- Representative source: [TBPLaS: a Tight-Binding Package for Large-scale Simulation](https://doi.org/10.48550/arXiv.2209.00806).
- Source requirement: [`TB-REQ-073`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_response_thermoelectric. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
