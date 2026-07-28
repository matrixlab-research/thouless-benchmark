---
id: AD-TBQ-022
tbq_id: TBQ-022
suite: 05-boundaries-bulk-boundary
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-022 — Boundary-state localization and finite-size splitting

## Scientific anchor

This companion is derived from [TBQ-022 — Boundary-state localization and finite-size splitting](../../problems/05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- bulk and boundary couplings
- system length

Scientific outputs:

- edge-state energy
- localization length
- splitting

## Differentiable formulation

Differentiate localization and splitting at fixed finite size, then perform a forward size sequence.

No-AD control: Rerun diagonalization for each parameter and system size.

## Validity and failure semantics

State mixing and exact zero-mode crossings require projector treatment.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of edge-state energy, localization length, splitting against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `boundary-localization` — Boundary and localization composition
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
