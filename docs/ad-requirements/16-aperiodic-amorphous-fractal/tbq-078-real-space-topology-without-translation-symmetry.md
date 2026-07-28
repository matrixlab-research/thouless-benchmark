---
id: AD-TBQ-078
tbq_id: TBQ-078
suite: 16-aperiodic-amorphous-fractal
ad_role: helpful
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-078 — Real-space topology without translation symmetry

## Scientific anchor

This companion is derived from [TBQ-078 — Real-space topology without translation symmetry](../../problems/16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- model and coordinate parameters

Scientific outputs:

- local Chern or Bott proxies
- mobility gap

## Differentiable formulation

Differentiate smooth real-space projector objectives and independently recompute discrete markers.

No-AD control: Finite-difference sparse projectors and marker calculations.

## Validity and failure semantics

Mobility gap and projector approximation must remain controlled.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of local Chern or Bott proxies, mobility gap against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `boundary-localization` — Boundary and localization composition

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
