---
id: TBQ-038
suite: 08-open-transport
source_requirement: TB-REQ-038
status: executable
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-038 — Transmission, local density, and finite-temperature noise

## Scientific question

Can one calculation consistently predict conductance, transmission eigenvalues, local
states, and current fluctuations?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Finite one- and two-dimensional devices attached to periodic multi-orbital leads,
including propagating and evanescent modes, disorder, and magnetic flux.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `E/t` | transport energy | -2.5 to 2.5 | dimensionless |
| `L/a` | device length | 1 to 100000 | cells |
| `N_ch` | open lead channels | 1 to 64 | count |
| `tau_c/t` | contact coupling | 0.1 to 1.2 | dimensionless |
| `kBT/t` | temperature | 0 to 0.20 | dimensionless |

## Required computation

Evaluate resonant and multiterminal devices, including finite-temperature auto- and
cross-correlated noise.

## Expected result

Symmetric resonances reach unit transmission, thermal noise obeys fluctuation-
dissipation at equilibrium, and zero-temperature shot noise follows transmission
eigenvalues.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Analytic scalar limits within 1e-7 and covariance matrices positive semidefinite within
1e-10.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide asymmetric contacts and a three-terminal geometry.

Suite-wide isolation rule: Hold out lead orientation, cross-section, orbital matching, contact transparency, and
terminal count.

## Evidence

- LKM seeds: `gcn_da2e995d149b4da4`, `gcn_8d5107693c024b90`, and reasoning chain `811903549792321536_1`.
- Representative source: [Modeling of Nanoscale Devices](https://doi.org/10.1109/jproc.2008.927355).
- Source requirement: [`TB-REQ-038`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`: the package-backed evaluator, independent gates, recorded result, and CI are present for thouless: domain_transport_consistency. See the machine-readable [backend audit](../../../benchmark/problem_coverage.json). This public result is not held-out validation.
