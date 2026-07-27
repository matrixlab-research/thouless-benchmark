---
id: TBQ-053
suite: 11-floquet-dynamics
source_requirement: TB-REQ-053
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-053 — Sambe, direct-propagation, and high-frequency agreement

## Scientific question

Where do independent Floquet formulations agree, and where does the high-frequency
approximation fail?

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

Compare Sambe diagonalization, direct one-period propagation, and successive Magnus or
van Vleck orders over omega.

## Expected result

All routes agree at high frequency; direct and Sambe remain consistent near resonance
while truncated high-frequency expansions deviate visibly.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Below 1 percent quasienergy error in the declared common regime and correct breakdown
detection.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide a multiphoton resonance.

Suite-wide isolation rule: Hold out waveform family, frequency ratio, resonance order, and switching protocol.

## Evidence

- LKM seeds: `gcn_7d5c22f3ec22410d`, `gcn_da29fc093cae4f5e`, and `gcn_69c35496847846eb`.
- Representative source: [Topological Frequency Conversion in Strongly Driven Quantum Systems](https://doi.org/10.1103/physrevx.7.041008).
- Source requirement: [`TB-REQ-053`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any
backend currently passes it. No current executable case is asserted to cover this full problem.
