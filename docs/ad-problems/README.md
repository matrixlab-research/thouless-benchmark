# Automatic-differentiation problem set

These ten specifications turn the AD and AD-helpful research directions from
[issue #6](https://github.com/matrixlab-research/thouless-benchmark/issues/6)
into executable scientific benchmarks:

1. [Multi-observable spectral recovery](ad-spectral-recovery.md)
2. [Degeneracy-safe occupied-projector differentiation](ad-degenerate-projector.md)
3. [Identifiability and predictive ambiguity](ad-identifiability.md)
4. [Differentiable quantum metric](ad-quantum-metric.md)
5. [Topological inverse design with independent invariants](ad-topological-design.md)
6. [Implicit differentiation of a surface Green function](ad-surface-green-implicit.md)
7. [Inverse transmission design](ad-inverse-transport.md)
8. [Complete device-and-lead sensitivity](ad-lead-device-sensitivity.md)
9. [Many-parameter sparse adjoint scaling](ad-sparse-adjoint-scaling.md)
10. [Robust checkpointed KPM design](ad-robust-kpm-design.md)

Each file defines the scientific question, parameters, computation, expected
result, acceptance gates, and generalization boundary before referring to an
API. LKM nodes record discovery provenance; the linked primary papers remain
the scientific sources.
