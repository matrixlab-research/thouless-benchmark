---
id: AD-TBQ-097
tbq_id: TBQ-097
suite: 20-inference-inverse-design
ad_role: essential
ad_status: ad_native_verified
forward_status: not_applicable
---

# AD-TBQ-097 — Gradient verification through spectral calculations

## Scientific anchor

This companion is derived from [TBQ-097 — Gradient verification through spectral calculations](../../problems/20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- model parameters
- arbitrary tangent and cotangent directions

Scientific outputs:

- JVP and VJP products through spectral calculations

## Differentiable formulation

Compare native products with independent directional finite differences and adjoint identities.

No-AD control: Compute central differences for each tested direction.

## Validity and failure semantics

Degenerate states require projector-based objectives.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of JVP and VJP products through spectral calculations against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `identifiability-higher-order` — Identifiability and higher-order products
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_degenerate_projector`, `ad_sparse_adjoint_scaling`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
