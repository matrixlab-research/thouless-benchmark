---
id: AD-TBQ-069
tbq_id: TBQ-069
suite: 14-magnetism-spin-orbital
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-069 — Texture-resolution and adiabatic convergence

## Scientific anchor

This companion is derived from [TBQ-069 — Texture-resolution and adiabatic convergence](../../problems/14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- texture length scale
- mesh spacing
- exchange parameters

Scientific outputs:

- adiabatic error
- current and torque convergence

## Differentiable formulation

Differentiate at fixed resolution and require value-gradient convergence over texture meshes.

No-AD control: Rerun every perturbation for every resolution.

## Validity and failure semantics

Mesh and topology changes remain external convergence choices.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of adiabatic error, current and torque convergence against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `geometry-strain-defects` — Geometry, strain, and defect parameterization
- `scale-error-diagnostics` — Scale and error diagnostics
- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: geometry-strain-defects, scale-error-diagnostics, nonsmooth-failure-semantics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
