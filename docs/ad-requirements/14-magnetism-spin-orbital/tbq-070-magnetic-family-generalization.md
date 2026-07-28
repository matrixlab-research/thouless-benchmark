---
id: AD-TBQ-070
tbq_id: TBQ-070
suite: 14-magnetism-spin-orbital
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-070 — Magnetic-family generalization

## Scientific anchor

This companion is derived from [TBQ-070 — Magnetic-family generalization](../../problems/14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- shared magnetic-texture and material parameters

Scientific outputs:

- held-out texture-family observables

## Differentiable formulation

Differentiate a multi-texture loss and validate on unseen skyrmion, spiral, or domain-wall families.

No-AD control: Refit and forward-evaluate each texture family.

## Validity and failure semantics

Texture topology and lattice graph are held-out categorical variables.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of held-out texture-family observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `multiscale-inference` — Multiscale mapping and inference
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: geometry-strain-defects, heldout-generality, multiscale-inference.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
