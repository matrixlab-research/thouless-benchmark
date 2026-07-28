---
id: AD-TBQ-059
tbq_id: TBQ-059
suite: 12-interactions-self-consistency
ad_role: helpful
ad_status: missing_forward_physics
forward_status: not_applicable
---

# AD-TBQ-059 — Conservation and unbroken-symmetry checks

## Scientific anchor

This companion is derived from [TBQ-059 — Conservation and unbroken-symmetry checks](../../problems/12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- physical interaction and model parameters

Scientific outputs:

- conservation, Ward-like, and unbroken-symmetry residuals

## Differentiable formulation

Differentiate the physical observable while using conservation residual gradients as diagnostics.

No-AD control: Finite-difference converged observables and residuals.

## Validity and failure semantics

The declared approximation determines which conservation laws apply.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of conservation, Ward-like, and unbroken-symmetry residuals against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `interaction-self-consistency` — Interacting self-consistency
- `implicit-stationarity` — Implicit fixed-point and stationarity rules
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
