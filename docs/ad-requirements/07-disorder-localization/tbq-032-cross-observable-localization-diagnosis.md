---
id: AD-TBQ-032
tbq_id: TBQ-032
suite: 07-disorder-localization
ad_role: essential
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-032 — Cross-observable localization diagnosis

## Scientific anchor

This companion is derived from [TBQ-032 — Cross-observable localization diagnosis](../../problems/07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- disorder and model parameters

Scientific outputs:

- IPR, transfer, conductance, and local-marker discrepancy

## Differentiable formulation

Differentiate a cross-observable localization objective with common disorder samples.

No-AD control: Finite-difference every observable over matched ensembles.

## Validity and failure semantics

All observables must share samples and resolved finite-size errors.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of IPR, transfer, conductance, and local-marker discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `disorder-ensembles` — Disorder and ensemble differentiation
- `boundary-localization` — Boundary and localization composition
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
