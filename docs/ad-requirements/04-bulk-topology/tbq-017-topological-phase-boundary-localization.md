---
id: AD-TBQ-017
tbq_id: TBQ-017
suite: 04-bulk-topology
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-017 — Topological phase-boundary localization

## Scientific anchor

This companion is derived from [TBQ-017 — Topological phase-boundary localization](../../problems/04-bulk-topology/tbq-017-topological-phase-boundary-localization.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- mass, hopping, spin-orbit, or strain parameters

Scientific outputs:

- smooth phase proxy
- gap
- independently recomputed index

## Differentiable formulation

Optimize a smooth occupied-subspace objective and locate the forward gap closing.

No-AD control: Grid-search parameters and recompute gaps and invariants.

## Validity and failure semantics

The topological transition is validated forward, never by differentiating the integer.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/04-bulk-topology/tbq-017-topological-phase-boundary-localization.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of smooth phase proxy, gap, independently recomputed index against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_topological_design`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/04-bulk-topology/tbq-017-topological-phase-boundary-localization.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
