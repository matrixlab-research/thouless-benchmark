---
id: AD-TBQ-094
tbq_id: TBQ-094
suite: 19-scientific-scale-numerics
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-094 — Accuracy-preserving time and memory scaling

## Scientific anchor

This companion is derived from [TBQ-094 — Accuracy-preserving time and memory scaling](../../problems/19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- physical parameters at increasing size

Scientific outputs:

- time, memory, value, and gradient accuracy

## Differentiable formulation

Use sparse adjoints or checkpointing and measure accuracy-preserving scaling.

No-AD control: Finite-difference two full forward solves per direction at every size.

## Validity and failure semantics

Hardware, warmed execution, and accuracy must be matched.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of time, memory, value, and gradient accuracy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_sparse_adjoint_scaling`, `ad_robust_kpm_design`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
