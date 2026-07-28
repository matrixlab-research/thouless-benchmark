---
id: AD-TBQ-051
tbq_id: TBQ-051
suite: 11-floquet-dynamics
ad_role: helpful
ad_status: missing_forward_physics
forward_status: not_applicable
---

# AD-TBQ-051 — Equivalent representations of a drive

## Scientific anchor

This companion is derived from [TBQ-051 — Equivalent representations of a drive](../../problems/11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- drive amplitude, phase, frequency, and waveform coefficients

Scientific outputs:

- propagator and Floquet-observable discrepancy

## Differentiable formulation

Differentiate a common drive representation and compare gauge-equivalent encodings.

No-AD control: Finite-difference full time evolution for each encoding.

## Validity and failure semantics

Time-origin and gauge transformations must be handled covariantly.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of propagator and Floquet-observable discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `gauge-fields-drives` — Gauge fields and drive parameterization
- `time-floquet-adjoints` — Time evolution and Floquet adjoints

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
