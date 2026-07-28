---
id: AD-TBQ-062
tbq_id: TBQ-062
suite: 13-moire-strain-supercells
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-062 — Geometry-dependent coupling laws

## Scientific anchor

This companion is derived from [TBQ-062 — Geometry-dependent coupling laws](../../problems/13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- atomic coordinates
- strain tensor
- coupling-law parameters

Scientific outputs:

- hoppings
- bands
- response and force-like sensitivities

## Differentiable formulation

Differentiate geometry-dependent onsite and hopping laws from coordinates to observables.

No-AD control: Finite-difference every coordinate or coupling parameter.

## Validity and failure semantics

Connectivity cutoffs require smoothing or explicit event handling.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of hoppings, bands, response and force-like sensitivities against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `physical-parameter-spaces` — Physical parameter spaces
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: geometry-strain-defects, physical-parameter-spaces, scale-error-diagnostics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
