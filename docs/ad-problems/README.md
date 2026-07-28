# Automatic-differentiation problem set

These ten specifications turn LKM-discovered AD and AD-helpful research
workflows into executable Rust-native benchmarks. Each case names a physical
system and source paper, while clearly marking the compact executable model as
an adaptation:

1. [Rice-Mele spectral and Wannier-sector inference](ad-spectral-recovery.md)
2. [BHZ Kramers-subspace differentiation](ad-degenerate-projector.md)
3. [SSH hopping identifiability with a local marker](ad-identifiability.md)
4. [Rice-Mele quantum-metric sensitivity](ad-quantum-metric.md)
5. [QWZ topological inverse design with independent invariants](ad-topological-design.md)
6. [SSH boundary Green-function differentiation](ad-surface-green-implicit.md)
7. [Double-quantum-dot transmission inference](ad-inverse-transport.md)
8. [Resonant-level device-and-contact sensitivity](ad-lead-device-sensitivity.md)
9. [Many-parameter Anderson sparse adjoint](ad-sparse-adjoint-scaling.md)
10. [Robust KPM design of a disordered SSH chain](ad-robust-kpm-design.md)

Each file defines the scientific question, parameters, computation, expected
result, acceptance gates, and generalization boundary before referring to an
API. LKM nodes record discovery provenance; the linked primary papers remain
the scientific sources. The raw discovery and reasoning responses are
preserved in
[`evidence/lkm/2026-07-28-ad-research-workflows`](../../evidence/lkm/2026-07-28-ad-research-workflows/README.md).
