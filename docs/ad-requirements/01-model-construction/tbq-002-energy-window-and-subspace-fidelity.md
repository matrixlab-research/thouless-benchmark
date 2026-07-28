---
id: AD-TBQ-002
tbq_id: TBQ-002
suite: 01-model-construction
ad_role: essential
ad_status: implementable_unverified
forward_status: implemented
---

# AD-TBQ-002 — Energy-window and subspace fidelity

## Scientific anchor

This companion is derived from [TBQ-002 — Energy-window and subspace fidelity](../../problems/01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- energy-window weights
- disentanglement and hopping parameters

Scientific outputs:

- out-of-window prediction error
- subspace distance

## Differentiable formulation

Differentiate the fitted subspace and held-out band error with respect to model parameters.

No-AD control: Repeat the fit for every parameter perturbation and compare excluded energies.

## Validity and failure semantics

Window membership must be frozen or replaced by smooth weights.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of out-of-window prediction error, subspace distance against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `physical-parameter-spaces` — Physical parameter spaces
- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `multiscale-inference` — Multiscale mapping and inference
- `heldout-generality` — Held-out generality

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `implementable_unverified`.
- Reason: All specialized primitives needed by this companion already exist; the remaining work is orchestration, a frozen oracle, a recorded result, and CI.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
