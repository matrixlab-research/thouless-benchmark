---
id: AD-TBQ-012
tbq_id: TBQ-012
suite: 03-magnetic-flux-hofstadter
ad_role: not_central
ad_status: ad_not_central
forward_status: implemented
---

# AD-TBQ-012 — Magnetic translation and minimal unit cell

## Scientific anchor

This companion is derived from [TBQ-012 — Magnetic translation and minimal unit cell](../../problems/03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `not_central`.

The core acceptance target is a discrete or forward classification; AD is limited to a continuous inner loop.

## Controls and outputs

Continuous controls:

- hopping and onsite parameters at fixed rational flux

Scientific outputs:

- magnetic-cell residual
- band observables

## Differentiable formulation

Use AD only inside a preselected magnetic cell to tune continuous parameters.

No-AD control: Enumerate rational cells and solve each candidate forward.

## Validity and failure semantics

Minimal-cell selection and flux rationalization are discrete.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of magnetic-cell residual, band observables against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `nonsmooth-failure-semantics` — Nonsmooth and discrete failure semantics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_not_central`.
- Reason: AD is not the scientific acceptance target for this companion; continuous inner-loop sensitivities may still be useful.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
