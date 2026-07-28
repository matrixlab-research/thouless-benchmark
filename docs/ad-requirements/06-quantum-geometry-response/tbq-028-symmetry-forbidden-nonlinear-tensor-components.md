---
id: AD-TBQ-028
tbq_id: TBQ-028
suite: 06-quantum-geometry-response
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-028 — Symmetry-forbidden nonlinear tensor components

## Scientific anchor

This companion is derived from [TBQ-028 — Symmetry-forbidden nonlinear tensor components](../../problems/06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- symmetry-allowed perturbations
- model parameters

Scientific outputs:

- allowed and forbidden tensor components

## Differentiable formulation

Pull back response gradients through symmetry-constrained parameters and test zero directions.

No-AD control: Perturb each parameter and recompute the tensor.

## Validity and failure semantics

Forbidden-component tests require exact declared symmetries.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of allowed and forbidden tensor components against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `physical-parameter-spaces` — Physical parameter spaces
- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `complex-generalized-basis` — Complex and generalized-basis differentiation

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: physical-parameter-spaces, topology-geometry-response, complex-generalized-basis.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
