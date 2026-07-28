---
id: AD-TBQ-026
tbq_id: TBQ-026
suite: 06-quantum-geometry-response
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-026 — Gauge covariance of geometric tensors

## Scientific anchor

This companion is derived from [TBQ-026 — Gauge covariance of geometric tensors](../../problems/06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- Hamiltonian and overlap parameters
- momentum

Scientific outputs:

- quantum metric
- Berry curvature
- covariance residual

## Differentiable formulation

Differentiate gauge-invariant projector tensors with respect to physical controls.

No-AD control: Central-difference tensors after independent eigensystem reconstruction.

## Validity and failure semantics

Subspace gaps and momentum-mesh convergence are mandatory.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of quantum metric, Berry curvature, covariance residual against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_quantum_metric`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
