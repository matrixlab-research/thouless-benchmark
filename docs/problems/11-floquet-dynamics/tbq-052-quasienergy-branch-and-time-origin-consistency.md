---
id: TBQ-052
suite: 11-floquet-dynamics
source_requirement: TB-REQ-052
status: proposed
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-052 — Quasienergy branch and time-origin consistency

## Scientific question

Are quasienergies, micromotion, and physical predictions invariant under equivalent time
origins and branch choices?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Driven two-level, SSH, Haldane-like, and quasiperiodically driven lattice models
represented by harmonic, pulsed, or piecewise protocols.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `A/t` | drive amplitude | 0.01 to 5 | dimensionless |
| `omega/t` | drive frequency | 0.2 to 20 | dimensionless |
| `N_h` | Floquet harmonic cutoff | 1 to 31 | harmonics per side |
| `dt*t` | time step | 1e-4 to 5e-2 | dimensionless |
| `N_cycle` | observed drive cycles | 1 to 1000 | count |

## Required computation

Shift the drive origin, reconstruct micromotion, and compare phase spectra modulo omega.

## Expected result

Quasienergy sets agree modulo omega, observables are unchanged, and state matching
accounts for branch crossings.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Phase-set distance below 1e-8 modulo 2 pi.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a shift that crosses the principal branch.

Suite-wide isolation rule: Hold out waveform family, frequency ratio, resonance order, and switching protocol.

## Evidence

- LKM seeds: `gcn_7d5c22f3ec22410d`, `gcn_da29fc093cae4f5e`, and `gcn_69c35496847846eb`.
- Representative source: [Topological Frequency Conversion in Strongly Driven Quantum Systems](https://doi.org/10.1103/physrevx.7.041008).
- Source requirement: [`TB-REQ-052`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
