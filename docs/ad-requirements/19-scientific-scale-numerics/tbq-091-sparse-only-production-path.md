---
id: AD-TBQ-091
tbq_id: TBQ-091
suite: 19-scientific-scale-numerics
ad_role: helpful
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-091 — Sparse-only production path

## Scientific anchor

This companion is derived from [TBQ-091 — Sparse-only production path](../../problems/19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- physical parameters in a fixed sparse representation

Scientific outputs:

- target observables
- memory and sparsity diagnostics

## Differentiable formulation

Differentiate through matrix-free or sparse operators and assert no dense fallback.

No-AD control: Finite-difference repeated sparse forward calculations.

## Validity and failure semantics

Matrix materialization is a hard failure.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of target observables, memory and sparsity diagnostics against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
