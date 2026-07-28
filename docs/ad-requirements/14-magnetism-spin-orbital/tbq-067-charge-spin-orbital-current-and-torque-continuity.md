---
id: AD-TBQ-067
tbq_id: TBQ-067
suite: 14-magnetism-spin-orbital
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-067 — Charge, spin, orbital-current, and torque continuity

## Scientific anchor

This companion is derived from [TBQ-067 — Charge, spin, orbital-current, and torque continuity](../../problems/14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- texture and spin-orbital parameters

Scientific outputs:

- charge, spin, orbital currents
- torque and continuity residual

## Differentiable formulation

Differentiate all local observables through one Hamiltonian-consistent operator construction.

No-AD control: Finite-difference states and every current operator.

## Validity and failure semantics

The current and torque conventions must be explicit.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of charge, spin, orbital currents, torque and continuity residual against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `topology-geometry-response` — Topology, quantum geometry, and response composition

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: complex-generalized-basis, topology-geometry-response.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
