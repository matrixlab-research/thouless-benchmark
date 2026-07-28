---
id: AD-TBQ-074
tbq_id: TBQ-074
suite: 15-optical-thermoelectric
ad_role: helpful
ad_status: missing_forward_physics
forward_status: missing_capability
---

# AD-TBQ-074 — Broadening and integration convergence

## Scientific anchor

This companion is derived from [TBQ-074 — Broadening and integration convergence](../../problems/15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- broadening
- integration nodes
- physical model parameters

Scientific outputs:

- response value and derivative convergence

## Differentiable formulation

Differentiate physical parameters at fixed quadrature, then test convergence across broadenings and grids.

No-AD control: Repeat finite differences across the full convergence ladder.

## Validity and failure semantics

Numerical regularizers are convergence variables unless scientifically declared.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of response value and derivative convergence against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `scale-error-diagnostics` — Scale and error diagnostics
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `missing_capability`.
- AD companion status: `missing_forward_physics`.
- Reason: The complete Thouless forward workflow for the source TBQ is not yet implemented, so an end-to-end derivative claim would be premature.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless-benchmark/issues/6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
