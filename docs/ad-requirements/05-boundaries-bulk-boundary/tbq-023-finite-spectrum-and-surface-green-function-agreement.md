---
id: AD-TBQ-023
tbq_id: TBQ-023
suite: 05-boundaries-bulk-boundary
ad_role: essential
ad_status: ad_native_verified
forward_status: implemented
---

# AD-TBQ-023 — Finite-spectrum and surface-Green-function agreement

## Scientific anchor

This companion is derived from [TBQ-023 — Finite-spectrum and surface-Green-function agreement](../../problems/05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- bulk and surface couplings
- energy
- broadening

Scientific outputs:

- surface Green function
- spectral density
- finite-slab discrepancy

## Differentiable formulation

Apply an implicit adjoint to the retarded surface fixed point and compare with finite spectra.

No-AD control: Unroll or rerun the surface solver for every perturbation.

## Validity and failure semantics

The retarded branch and solver residual must remain stable.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of surface Green function, spectral density, finite-slab discrepancy against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `linear-resolvent-adjoints` — Dense and sparse linear-resolvent adjoints
- `implicit-stationarity` — Implicit fixed-point and stationarity rules
- `boundary-localization` — Boundary and localization composition

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `ad_native_verified`.
- Reason: A current Rust-native AD witness exercises the stated companion formulation; this does not claim completion of the full source TBQ.
- Existing Rust-native witnesses: `ad_surface_green_implicit`
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
