---
id: AD-TBQ-039
tbq_id: TBQ-039
suite: 08-open-transport
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-039 — Numerical stability for long evanescent devices

## Scientific anchor

This companion is derived from [TBQ-039 — Numerical stability for long evanescent devices](../../problems/08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- device length
- barrier and hopping parameters

Scientific outputs:

- transmission
- residual
- condition and iteration counts

## Differentiable formulation

Differentiate the sparse solve while treating solver diagnostics as acceptance evidence.

No-AD control: Finite-difference repeated long-device solves under a fixed solver.

## Validity and failure semantics

Solver switching and preconditioner rebuilding are discrete events.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of transmission, residual, condition and iteration counts against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `scale-error-diagnostics` — Scale and error diagnostics
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
