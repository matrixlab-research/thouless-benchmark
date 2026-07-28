---
id: AD-TBQ-082
tbq_id: TBQ-082
suite: 17-defects-interfaces
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-082 — Defect-specific local chemistry

## Scientific anchor

This companion is derived from [TBQ-082 — Defect-specific local chemistry](../../problems/17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- defect onsite, charge-state, and local hopping parameters

Scientific outputs:

- local levels
- charge and spin observables

## Differentiable formulation

Differentiate a localized chemistry parameterization and its embedded observables.

No-AD control: Finite-difference each local chemistry parameter.

## Validity and failure semantics

Charge-state or bonding changes require separate branches.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of local levels, charge and spin observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `physical-parameter-spaces` — Physical parameter spaces

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: geometry-strain-defects, physical-parameter-spaces.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
