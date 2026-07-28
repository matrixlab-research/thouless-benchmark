---
id: AD-TBQ-083
tbq_id: TBQ-083
suite: 17-defects-interfaces
ad_role: helpful
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-083 — Embedding and supercell agreement

## Scientific anchor

This companion is derived from [TBQ-083 — Embedding and supercell agreement](../../problems/17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- defect and embedding parameters

Scientific outputs:

- embedding-versus-supercell Green function and spectrum discrepancy

## Differentiable formulation

Differentiate both representations through a shared defect model.

No-AD control: Finite-difference independent embedding and supercell calculations.

## Validity and failure semantics

Supercell size and embedding boundary are convergence variables.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of embedding-versus-supercell Green function and spectrum discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `multiscale-inference` — Multiscale mapping and inference
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
