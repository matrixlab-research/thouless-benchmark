---
id: AD-TBQ-043
tbq_id: TBQ-043
suite: 09-superconducting-bdg
ad_role: helpful
ad_status: missing_ad_rule
forward_status: implemented
---

# AD-TBQ-043 — Majorana versus trivial near-zero modes

## Scientific anchor

This companion is derived from [TBQ-043 — Majorana versus trivial near-zero modes](../../problems/09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md). It does not change the source scientific question and does not by itself complete the source TBQ.

## Why differentiation matters

AD role: `helpful`.

Differentiation improves attribution or efficiency, while the accepted forward scientific result remains independently obtainable.

## Controls and outputs

Continuous controls:

- chemical potential
- pairing
- Zeeman and disorder parameters

Scientific outputs:

- near-zero projector
- localization
- topological and trivial diagnostics

## Differentiable formulation

Differentiate projector-based robustness metrics and validate against independent diagnostics.

No-AD control: Scan all parameters and classify modes from repeated spectra.

## Validity and failure semantics

Individual Majorana labels are invalid at degeneracy.

The implementation must reject or explicitly flag derivatives outside this domain; it must not silently return a plausible number across a branch, rank, graph, or solver discontinuity.

## Acceptance

1. **Forward science:** The scientific acceptance and convergence conditions in docs/problems/09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md remain authoritative; the AD path must reproduce the accepted forward observable before any derivative or speed claim.
2. **Derivative oracle:** Compare at least one predeclared directional derivative of near-zero projector, localization, topological and trivial diagnostics against an independent central finite difference, analytic identity, or adjoint identity.
3. **Generality:** Repeat the value-and-derivative check on a held-out variant declared by the source TBQ. Public examples are not held-out evidence.

No universal tolerance is introduced here. The benchmark must freeze a tolerance justified by the source problem's scale and convergence study; unresolved failures stay linked to an issue rather than widening that tolerance.

## Required Rust-native capabilities

- `hermitian-subspaces` — Hermitian spectral-subspace rules
- `boundary-localization` — Boundary and localization composition
- `topology-geometry-response` — Topology, quantum geometry, and response composition

## Current evidence and gap

- Source forward status for Thouless: `implemented`.
- AD companion status: `missing_ad_rule`.
- Reason: The forward workflow exists, but reusable native AD support is incomplete for: boundary-localization, topology-geometry-response.
- Existing Rust-native witnesses: None. Related public examples must not be treated as a held-out result.
- Tracking issue: [https://github.com/matrixlab-research/thouless/issues/13](https://github.com/matrixlab-research/thouless/issues/13)

## Provenance

Scientific provenance, parameter ranges, expected results, LKM identifiers, and paper citations are inherited from the [source problem](../../problems/09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md). The LKM score remains a retrieval ranking signal, not a confidence or correctness probability.
