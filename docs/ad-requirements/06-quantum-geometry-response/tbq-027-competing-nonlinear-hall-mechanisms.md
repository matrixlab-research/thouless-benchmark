---
id: AD-TBQ-027
tbq_id: TBQ-027
suite: 06-quantum-geometry-response
ad_role: essential
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-027 — Competing nonlinear Hall mechanisms

## Scientific anchor

This companion is derived from [TBQ-027 — Competing nonlinear Hall mechanisms](../../problems/06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `essential`.

The requested sensitivity is itself a scientific observable or changes the tractability of calibration, control, or inverse design.

## Controls and outputs

Continuous controls:

- chemical potential
- relaxation time
- band parameters

Scientific outputs:

- intrinsic, Berry-dipole, and extrinsic Hall contributions

## Differentiable formulation

Differentiate mechanism-resolved response integrals instead of a single fitted total.

No-AD control: Finite-difference each mechanism after full Brillouin-zone integration.

## Validity and failure semantics

The chosen scattering model and Fermi-surface smoothing must be explicit.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of intrinsic, Berry-dipole, and extrinsic Hall contributions against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `topology-geometry-response` — Topology, quantum geometry, and response composition
- `physical-parameter-spaces` — Physical parameter spaces
- `scale-error-diagnostics` — Scale and error diagnostics

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: topology-geometry-response, physical-parameter-spaces, scale-error-diagnostics.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
