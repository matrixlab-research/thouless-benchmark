---
id: AD-TBQ-018
tbq_id: TBQ-018
suite: 04-bulk-topology
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-018 — Degeneracy-safe Wilson and nested Wilson flow

## Scientific anchor

This companion is derived from [TBQ-018 — Degeneracy-safe Wilson and nested Wilson flow](../../problems/04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- Hamiltonian parameters
- loop base point

Scientific outputs:

- Wilson and nested-Wilson subspace spectra

## Differentiable formulation

Differentiate gauge-covariant holonomy subspaces under a maintained spectral separation.

No-AD control: Finite-difference complete loop constructions with parallel-transport rematching.

## Validity and failure semantics

Wilson-sector gaps and occupied gaps must remain open.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of Wilson and nested-Wilson subspace spectra against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: topology-geometry-response, nonsmooth-failure-semantics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
