---
id: AD-TBQ-095
tbq_id: TBQ-095
suite: 19-scientific-scale-numerics
ad_role: conditional
ad_status: conditionally_differentiable
forward_status: implemented
---

# AD-TBQ-095 — Reproducible transition from exact to production scale

## Scientific anchor

This companion is derived from [TBQ-095 — Reproducible transition from exact to production scale](../../problems/19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `conditional`.

A derivative is meaningful only after the relevant branch, graph, solver, or representation has been fixed.

## Controls and outputs

Continuous controls:

- physical parameters at fixed exact or production method

Scientific outputs:

- exact-to-production value and gradient discrepancy

## Differentiable formulation

Differentiate both methods on their overlap and forward-validate the transition policy.

No-AD control: Finite-difference both methods over the size ladder.

## Validity and failure semantics

Method switching and size are discrete.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of exact-to-production value and gradient discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics
- `multiscale-inference` — Multiscale mapping and inference
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `conditionally_differentiable`.
- Reason: A local derivative is meaningful only inside the declared fixed branch or representation; the discrete event remains a forward gate.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
