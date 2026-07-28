---
id: AD-TBQ-013
tbq_id: TBQ-013
suite: 03-magnetic-flux-hofstadter
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-013 — Hofstadter gap topology and Streda consistency

## Scientific anchor

This companion is derived from [TBQ-013 — Hofstadter gap topology and Streda consistency](../../problems/03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- flux density
- chemical potential
- hopping parameters

Scientific outputs:

- gap proxy
- density derivative
- Chern and Streda discrepancy

## Differentiable formulation

Differentiate density and smooth gap proxies while independently recomputing the integer invariant.

No-AD control: Finite-difference density versus flux and forward-compute Chern numbers.

## Validity and failure semantics

Gap closings and rational-cell changes invalidate a local derivative.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of gap proxy, density derivative, Chern and Streda discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `gauge-fields-drives` — Gauge fields and drive parameterization
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: gauge-fields-drives, topology-geometry-response, nonsmooth-failure-semantics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
