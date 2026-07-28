---
id: AD-TBQ-030
tbq_id: TBQ-030
suite: 06-quantum-geometry-response
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-030 — Zero-Chern nonlinear bulk-boundary workflow

## Scientific anchor

This companion is derived from [TBQ-030 — Zero-Chern nonlinear bulk-boundary workflow](../../problems/06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- bulk couplings
- boundary potential
- chemical potential

Scientific outputs:

- nonlinear bulk response
- boundary accumulation
- zero Chern number

## Differentiable formulation

Differentiate the nonlinear response and boundary observable while forward-validating the zero-Chern condition.

No-AD control: Parameter-scan bulk and boundary calculations independently.

## Validity and failure semantics

The bulk gap, symmetry class, and boundary definition must remain declared.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of nonlinear bulk response, boundary accumulation, zero Chern number against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `boundary-localization` — Boundary and localization composition
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_topological_design`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
