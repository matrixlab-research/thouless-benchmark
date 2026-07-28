---
id: AD-TBQ-053
tbq_id: TBQ-053
suite: 11-floquet-dynamics
ad_role: helpful
ad_status: missing_forward_physics
forward_status: not_applicable
---

# AD-TBQ-053 — Sambe, direct-propagation, and high-frequency agreement

## Scientific anchor

This companion is derived from [TBQ-053 — Sambe, direct-propagation, and high-frequency agreement](../../problems/11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- drive frequency and amplitude
- time step
- harmonic cutoff

Scientific outputs:

- Sambe-propagator-high-frequency discrepancy

## Differentiable formulation

Differentiate physical controls within each representation and forward-test representation convergence.

No-AD control: Rerun all three methods for every perturbation.

## Validity and failure semantics

Time step and harmonic cutoff remain discrete convergence variables.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of Sambe-propagator-high-frequency discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `time-floquet-adjoints` — Time evolution and Floquet adjoints
- `multiscale-inference` — Multiscale mapping and inference
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
