---
id: AD-TBQ-016
tbq_id: TBQ-016
suite: 04-bulk-topology
ad_role: not_central
ad_status: ad_not_central
forward_status: implemented
---

# AD-TBQ-016 — Gauge-invariant bulk indices

## Scientific anchor

This companion is derived from [TBQ-016 — Gauge-invariant bulk indices](../../problems/04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `not_central`.

The core acceptance target is a discrete or forward classification; AD is limited to a continuous inner loop.

## Controls and outputs

Continuous controls:

- continuous Hamiltonian parameters

Scientific outputs:

- smooth projector geometry
- independently recomputed bulk index

## Differentiable formulation

Use AD for smooth projector observables but not for the integer index itself.

No-AD control: Parameter-scan and recompute the invariant on every model.

## Validity and failure semantics

The index derivative is zero away from transitions and undefined at gap closing.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of smooth projector geometry, independently recomputed bulk index against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_not_central`.
- Reason: AD is not the scientific acceptance target for this companion; continuous inner-loop sensitivities may still be useful.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
