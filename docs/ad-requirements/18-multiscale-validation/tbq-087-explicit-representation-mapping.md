---
id: AD-TBQ-087
tbq_id: TBQ-087
suite: 18-multiscale-validation
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-087 — Explicit representation mapping

## Scientific anchor

This companion is derived from [TBQ-087 — Explicit representation mapping](../../problems/18-multiscale-validation/tbq-087-explicit-representation-mapping.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- representation-map and physical parameters

Scientific outputs:

- mapped Hamiltonian, subspace, and observable residuals

## Differentiable formulation

Differentiate an explicit map rather than comparing unnamed matrices.

No-AD control: Finite-difference map construction and both endpoint solvers.

## Validity and failure semantics

Map gauge, basis, window, and normalization must be explicit.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/18-multiscale-validation/tbq-087-explicit-representation-mapping.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of mapped Hamiltonian, subspace, and observable residuals against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `multiscale-inference` — Multiscale mapping and inference
- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `hermitian-subspaces` — Hermitian spectral-subspace rules

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: multiscale-inference, complex-generalized-basis.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/18-multiscale-validation/tbq-087-explicit-representation-mapping.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
