---
id: AD-TBQ-033
tbq_id: TBQ-033
suite: 07-disorder-localization
ad_role: essential
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-033 — Finite-size scaling of mobility edges

## Scientific anchor

This companion is derived from [TBQ-033 — Finite-size scaling of mobility edges](../../problems/07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- disorder strength
- energy
- continuous scaling parameters

Scientific outputs:

- mobility-edge location
- critical exponent
- collapse loss

## Differentiable formulation

Differentiate a smooth finite-size-scaling collapse and validate the extracted crossing independently.

No-AD control: Grid-search scaling parameters and rerun all sizes.

## Validity and failure semantics

Critical branches and finite-size corrections must be reported.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of mobility-edge location, critical exponent, collapse loss against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `disorder-ensembles` — Disorder and ensemble differentiation
- `boundary-localization` — Boundary and localization composition
- `identifiability-higher-order` — Identifiability and higher-order products

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
