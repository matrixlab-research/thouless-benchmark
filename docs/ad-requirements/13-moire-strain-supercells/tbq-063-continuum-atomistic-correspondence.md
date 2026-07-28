---
id: AD-TBQ-063
tbq_id: TBQ-063
suite: 13-moire-strain-supercells
ad_role: essential
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-063 — Continuum-atomistic correspondence

## Scientific anchor

This companion is derived from [TBQ-063 — Continuum-atomistic correspondence](../../problems/13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- shared continuum and atomistic parameters

Scientific outputs:

- band, subspace, and response discrepancy

## Differentiable formulation

Differentiate an explicit representation map and cross-scale observable loss.

No-AD control: Refit and finite-difference both models separately.

## Validity and failure semantics

The mapping, gauge, and energy window must be declared.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of band, subspace, and response discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `multiscale-inference` — Multiscale mapping and inference
- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `hermitian-subspaces` — Hermitian spectral-subspace rules

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
