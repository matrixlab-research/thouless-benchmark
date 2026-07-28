---
id: AD-TBQ-001
tbq_id: TBQ-001
suite: 01-model-construction
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-001 — Basis and generalized-Hermiticity fidelity

## Scientific anchor

This companion is derived from [TBQ-001 — Basis and generalized-Hermiticity fidelity](../../problems/01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- onsite and hopping coefficients
- overlap-matrix elements

Scientific outputs:

- generalized eigenvalues
- Hermiticity and residual losses

## Differentiable formulation

Differentiate a basis-covariant loss built from H, S, and separated spectral subspaces.

No-AD control: Rebuild each perturbed H and S and use central finite differences.

## Validity and failure semantics

S must remain positive definite and the selected subspace must stay separated.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of generalized eigenvalues, Hermiticity and residual losses against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `physical-parameter-spaces` — Physical parameter spaces
- `complex-generalized-basis` — Complex and generalized-basis differentiation
- `hermitian-subspaces` — Hermitian spectral-subspace rules

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: physical-parameter-spaces, complex-generalized-basis.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
