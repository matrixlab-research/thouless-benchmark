---
id: AD-TBQ-055
tbq_id: TBQ-055
suite: 11-floquet-dynamics
ad_role: conditional
ad_status: conditionally_differentiable
forward_status: not_applicable
---

# AD-TBQ-055 — Time-step and harmonic-cutoff holdout

## Scientific anchor

This companion is derived from [TBQ-055 — Time-step and harmonic-cutoff holdout](../../problems/11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `conditional`.

A derivative is meaningful only after the relevant branch, graph, solver, or representation has been fixed.

## Controls and outputs

Continuous controls:

- physical drive controls at fixed numerical resolution

Scientific outputs:

- value and gradient convergence across time steps and cutoffs

## Differentiable formulation

Differentiate only within a fixed discretization, then require an external value-gradient convergence ladder.

No-AD control: Rerun finite differences at every time step and cutoff.

## Validity and failure semantics

Time-step and harmonic-count changes are not differentiated.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of value and gradient convergence across time steps and cutoffs against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `time-floquet-adjoints` — Time evolution and Floquet adjoints
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `not_applicable`.
- AD companion status: `conditionally_differentiable`.
- Reason: A local derivative is meaningful only inside the declared fixed branch or representation; the discrete event remains a forward gate.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
