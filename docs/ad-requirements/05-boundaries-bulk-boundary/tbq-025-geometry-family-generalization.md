---
id: AD-TBQ-025
tbq_id: TBQ-025
suite: 05-boundaries-bulk-boundary
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-025 — Geometry-family generalization

## Scientific anchor

This companion is derived from [TBQ-025 — Geometry-family generalization](../../problems/05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- continuous geometry and termination-family parameters

Scientific outputs:

- held-out boundary spectra and localization

## Differentiable formulation

Differentiate a family-level loss and validate on unseen geometries.

No-AD control: Brute-force calibrate each geometry and evaluate held-out families.

## Validity and failure semantics

Connectivity and termination class remain evaluator-controlled.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of held-out boundary spectra and localization against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `boundary-localization` — Boundary and localization composition
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: geometry-strain-defects, heldout-generality, boundary-localization.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
