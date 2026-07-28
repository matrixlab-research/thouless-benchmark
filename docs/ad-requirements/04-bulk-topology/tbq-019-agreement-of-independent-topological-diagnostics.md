---
id: AD-TBQ-019
tbq_id: TBQ-019
suite: 04-bulk-topology
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-019 — Agreement of independent topological diagnostics

## Scientific anchor

This companion is derived from [TBQ-019 — Agreement of independent topological diagnostics](../../problems/04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- model parameters

Scientific outputs:

- discrepancy among Chern, Wilson, parity, and real-space diagnostics

## Differentiable formulation

Differentiate continuous discrepancy measures to diagnose which representation causes disagreement.

No-AD control: Recompute every diagnostic for each perturbed model.

## Validity and failure semantics

Diagnostics with discrete outputs remain forward gates.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of discrepancy among Chern, Wilson, parity, and real-space diagnostics against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `boundary-localization` — Boundary and localization composition
- `multiscale-inference` — Multiscale mapping and inference

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
