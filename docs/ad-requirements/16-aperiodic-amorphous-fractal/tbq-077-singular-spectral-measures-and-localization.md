---
id: AD-TBQ-077
tbq_id: TBQ-077
suite: 16-aperiodic-amorphous-fractal
ad_role: helpful
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-077 — Singular spectral measures and localization

## Scientific anchor

This companion is derived from [TBQ-077 — Singular spectral measures and localization](../../problems/16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- model and geometry parameters

Scientific outputs:

- spectral-measure moments
- localization observables

## Differentiable formulation

Differentiate smoothed measures and KPM moments with common random vectors.

No-AD control: Finite-difference repeated KPM and exact approximant calculations.

## Validity and failure semantics

Singular measures require resolution and kernel convergence.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of spectral-measure moments, localization observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `boundary-localization` — Boundary and localization composition
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
