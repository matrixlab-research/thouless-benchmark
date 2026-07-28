---
id: AD-TBQ-031
tbq_id: TBQ-031
suite: 07-disorder-localization
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-031 — Reproducible disorder ensembles

## Scientific anchor

This companion is derived from [TBQ-031 — Reproducible disorder ensembles](../../problems/07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- disorder strength
- differentiable noise amplitudes

Scientific outputs:

- ensemble DOS
- localization and transport statistics

## Differentiable formulation

Use fixed seeds or reparameterized noise to differentiate ensemble estimators.

No-AD control: Repeat large ensembles for every parameter perturbation.

## Validity and failure semantics

Seed policy and confidence intervals are part of the result.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of ensemble DOS, localization and transport statistics against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `disorder-ensembles` — Disorder and ensemble differentiation
- `kpm-stochastic-adjoints` — KPM and stochastic adjoints
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: disorder-ensembles, scale-error-diagnostics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
