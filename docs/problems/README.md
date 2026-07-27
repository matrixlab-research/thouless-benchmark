# Tight-Binding Scientific Problem Catalog

This catalog contains 100 domain-first benchmark problem specifications. Each
problem is defined before choosing a Rust API or source-package compatibility
surface. The original twenty workflows remain in
[`benchmark/cases.json`](../../benchmark/cases.json); additional whole-problem
witnesses are in
[`benchmark/domain_cases.json`](../../benchmark/domain_cases.json), with the
three-backend audit in
[`benchmark/problem_coverage.json`](../../benchmark/problem_coverage.json).

The upstream derivation is retained in
[`docs/tight-binding-domain-benchmark-requirements.md`](../tight-binding-domain-benchmark-requirements.md),
and the verbatim LKM snapshot is documented in
[`evidence/lkm/2026-07-27-tight-binding-domain`](../../evidence/lkm/2026-07-27-tight-binding-domain/README.md).

Every problem file contains a scientific question, model family, parameter
ranges and units, required computation, expected result, acceptance and
convergence conditions, held-out variants, provenance, and implementation
status.

The per-document status below says only whether an executable benchmark exists.
The separate [three-backend capability assessment](../problem-coverage.md)
classifies every problem for Thouless, PythTB, and Kwant as `implemented`,
`implementable_unverified`, `missing_capability`, or `not_applicable`.
That assessment includes the documented parameter range: a dense small-system
path does not satisfy a problem that requires sparse production-scale methods.

## Status vocabulary

- `proposed`: domain specification only; no backend pass is claimed.
- `executable`: a package-backed evaluator, independent oracle, result record,
  and CI job are present.
- `held-out-validated`: reserved for evaluator-owned isolated validation.

## Catalog

### Suite 01 — Low-energy model construction and provenance

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-001 | [Basis and generalized-Hermiticity fidelity](01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md) | TB-REQ-001 | proposed |
| TBQ-002 | [Energy-window and subspace fidelity](01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md) | TB-REQ-002 | proposed |
| TBQ-003 | [Controlled hopping truncation](01-model-construction/tbq-003-controlled-hopping-truncation.md) | TB-REQ-003 | proposed |
| TBQ-004 | [Symmetry preservation and negative controls](01-model-construction/tbq-004-symmetry-preservation-and-negative-controls.md) | TB-REQ-004 | proposed |
| TBQ-005 | [Transfer beyond fitted structures](01-model-construction/tbq-005-transfer-beyond-fitted-structures.md) | TB-REQ-005 | proposed |

### Suite 02 — Bands, density of states, and Fermiology

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-006 | [Degeneracy-safe band projectors](02-bands-dos-fermiology/tbq-006-degeneracy-safe-band-projectors.md) | TB-REQ-006 | executable |
| TBQ-007 | [Density-of-states state counting](02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md) | TB-REQ-007 | executable |
| TBQ-008 | [Van Hove and flat-band feature resolution](02-bands-dos-fermiology/tbq-008-van-hove-and-flat-band-feature-resolution.md) | TB-REQ-008 | proposed |
| TBQ-009 | [Fermi-surface topology and Lifshitz transitions](02-bands-dos-fermiology/tbq-009-fermi-surface-topology-and-lifshitz-transitions.md) | TB-REQ-009 | proposed |
| TBQ-010 | [Bloch and finite-real-space spectral agreement](02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md) | TB-REQ-010 | executable |

### Suite 03 — Magnetic fields, Landau fans, and Hofstadter physics

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-011 | [Gauge-covariant Peierls substitution](03-magnetic-flux-hofstadter/tbq-011-gauge-covariant-peierls-substitution.md) | TB-REQ-011 | executable |
| TBQ-012 | [Magnetic translation and minimal unit cell](03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md) | TB-REQ-012 | executable |
| TBQ-013 | [Hofstadter gap topology and Streda consistency](03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md) | TB-REQ-013 | executable |
| TBQ-014 | [Low-field Landau-level correspondence](03-magnetic-flux-hofstadter/tbq-014-low-field-landau-level-correspondence.md) | TB-REQ-014 | proposed |
| TBQ-015 | [Rational-approximant convergence](03-magnetic-flux-hofstadter/tbq-015-rational-approximant-convergence.md) | TB-REQ-015 | proposed |

### Suite 04 — Bulk topology and phase diagrams

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-016 | [Gauge-invariant bulk indices](04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md) | TB-REQ-016 | proposed |
| TBQ-017 | [Topological phase-boundary localization](04-bulk-topology/tbq-017-topological-phase-boundary-localization.md) | TB-REQ-017 | proposed |
| TBQ-018 | [Degeneracy-safe Wilson and nested Wilson flow](04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md) | TB-REQ-018 | proposed |
| TBQ-019 | [Agreement of independent topological diagnostics](04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md) | TB-REQ-019 | executable |
| TBQ-020 | [Trivial, nearly gapless, and basis-adversarial controls](04-bulk-topology/tbq-020-trivial-nearly-gapless-and-basis-adversarial-controls.md) | TB-REQ-020 | proposed |

### Suite 05 — Boundaries, higher-order topology, and bulk-boundary relations

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-021 | [Termination families from one bulk model](05-boundaries-bulk-boundary/tbq-021-termination-families-from-one-bulk-model.md) | TB-REQ-021 | proposed |
| TBQ-022 | [Boundary-state localization and finite-size splitting](05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md) | TB-REQ-022 | executable |
| TBQ-023 | [Finite-spectrum and surface-Green-function agreement](05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md) | TB-REQ-023 | proposed |
| TBQ-024 | [Conditional bulk-boundary correspondence](05-boundaries-bulk-boundary/tbq-024-conditional-bulk-boundary-correspondence.md) | TB-REQ-024 | proposed |
| TBQ-025 | [Geometry-family generalization](05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md) | TB-REQ-025 | proposed |

### Suite 06 — Quantum geometry and nonlinear response

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-026 | [Gauge covariance of geometric tensors](06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md) | TB-REQ-026 | proposed |
| TBQ-027 | [Competing nonlinear Hall mechanisms](06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md) | TB-REQ-027 | proposed |
| TBQ-028 | [Symmetry-forbidden nonlinear tensor components](06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md) | TB-REQ-028 | proposed |
| TBQ-029 | [Fermi-surface and derivative convergence](06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md) | TB-REQ-029 | proposed |
| TBQ-030 | [Zero-Chern nonlinear bulk-boundary workflow](06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md) | TB-REQ-030 | proposed |

### Suite 07 — Disorder, localization, and mobility edges

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-031 | [Reproducible disorder ensembles](07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md) | TB-REQ-031 | proposed |
| TBQ-032 | [Cross-observable localization diagnosis](07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md) | TB-REQ-032 | proposed |
| TBQ-033 | [Finite-size scaling of mobility edges](07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md) | TB-REQ-033 | proposed |
| TBQ-034 | [Topological mobility gap](07-disorder-localization/tbq-034-topological-mobility-gap.md) | TB-REQ-034 | proposed |
| TBQ-035 | [Statistical generalization across disorder families](07-disorder-localization/tbq-035-statistical-generalization-across-disorder-families.md) | TB-REQ-035 | proposed |

### Suite 08 — Open-system transport and scattering

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-036 | [Lead modes and self-energy calibration](08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md) | TB-REQ-036 | executable |
| TBQ-037 | [Scattering conservation and local continuity](08-open-transport/tbq-037-scattering-conservation-and-local-continuity.md) | TB-REQ-037 | proposed |
| TBQ-038 | [Transmission, local density, and finite-temperature noise](08-open-transport/tbq-038-transmission-local-density-and-finite-temperature-noise.md) | TB-REQ-038 | proposed |
| TBQ-039 | [Numerical stability for long evanescent devices](08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md) | TB-REQ-039 | proposed |
| TBQ-040 | [Generalization across contact families](08-open-transport/tbq-040-generalization-across-contact-families.md) | TB-REQ-040 | proposed |

### Suite 09 — Superconducting BdG and Majorana systems

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-041 | [Nambu convention and particle-hole symmetry](09-superconducting-bdg/tbq-041-nambu-convention-and-particle-hole-symmetry.md) | TB-REQ-041 | executable |
| TBQ-042 | [Phase-resolved Andreev spectrum and Josephson current](09-superconducting-bdg/tbq-042-phase-resolved-andreev-spectrum-and-josephson-current.md) | TB-REQ-042 | executable |
| TBQ-043 | [Majorana versus trivial near-zero modes](09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md) | TB-REQ-043 | executable |
| TBQ-044 | [Fragility of four-pi Josephson response](09-superconducting-bdg/tbq-044-fragility-of-four-pi-josephson-response.md) | TB-REQ-044 | proposed |
| TBQ-045 | [Continuum-to-lattice BdG convergence](09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md) | TB-REQ-045 | proposed |

### Suite 10 — Non-Hermitian spectra and topology

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-046 | [Biorthogonal eigenvectors and residuals](10-non-hermitian/tbq-046-biorthogonal-eigenvectors-and-residuals.md) | TB-REQ-046 | proposed |
| TBQ-047 | [Exceptional-point order and sensitivity](10-non-hermitian/tbq-047-exceptional-point-order-and-sensitivity.md) | TB-REQ-047 | proposed |
| TBQ-048 | [Point-gap, line-gap, and non-Bloch invariants](10-non-hermitian/tbq-048-point-gap-line-gap-and-non-bloch-invariants.md) | TB-REQ-048 | proposed |
| TBQ-049 | [Periodic-open mismatch and skin localization](10-non-hermitian/tbq-049-periodic-open-mismatch-and-skin-localization.md) | TB-REQ-049 | proposed |
| TBQ-050 | [Non-Hermitian family generalization](10-non-hermitian/tbq-050-non-hermitian-family-generalization.md) | TB-REQ-050 | proposed |

### Suite 11 — Floquet and time-dependent dynamics

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-051 | [Equivalent representations of a drive](11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md) | TB-REQ-051 | proposed |
| TBQ-052 | [Quasienergy branch and time-origin consistency](11-floquet-dynamics/tbq-052-quasienergy-branch-and-time-origin-consistency.md) | TB-REQ-052 | proposed |
| TBQ-053 | [Sambe, direct-propagation, and high-frequency agreement](11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md) | TB-REQ-053 | proposed |
| TBQ-054 | [Dynamical pumping and frequency conversion](11-floquet-dynamics/tbq-054-dynamical-pumping-and-frequency-conversion.md) | TB-REQ-054 | proposed |
| TBQ-055 | [Time-step and harmonic-cutoff holdout](11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md) | TB-REQ-055 | proposed |

### Suite 12 — Interactions and self-consistent lattice approximations

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-056 | [Interaction and double-counting declaration](12-interactions-self-consistency/tbq-056-interaction-and-double-counting-declaration.md) | TB-REQ-056 | proposed |
| TBQ-057 | [Self-consistency robustness and metastability](12-interactions-self-consistency/tbq-057-self-consistency-robustness-and-metastability.md) | TB-REQ-057 | proposed |
| TBQ-058 | [Thermodynamic comparison of competing orders](12-interactions-self-consistency/tbq-058-thermodynamic-comparison-of-competing-orders.md) | TB-REQ-058 | proposed |
| TBQ-059 | [Conservation and unbroken-symmetry checks](12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md) | TB-REQ-059 | proposed |
| TBQ-060 | [Validation against small exact systems](12-interactions-self-consistency/tbq-060-validation-against-small-exact-systems.md) | TB-REQ-060 | proposed |

### Suite 13 — Moiré, strain, and large reconstructed supercells

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-061 | [Commensurate and reconstructed geometry](13-moire-strain-supercells/tbq-061-commensurate-and-reconstructed-geometry.md) | TB-REQ-061 | proposed |
| TBQ-062 | [Geometry-dependent coupling laws](13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md) | TB-REQ-062 | proposed |
| TBQ-063 | [Continuum-atomistic correspondence](13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md) | TB-REQ-063 | proposed |
| TBQ-064 | [Sparse observables in giant supercells](13-moire-strain-supercells/tbq-064-sparse-observables-in-giant-supercells.md) | TB-REQ-064 | proposed |
| TBQ-065 | [Structural-family transfer](13-moire-strain-supercells/tbq-065-structural-family-transfer.md) | TB-REQ-065 | proposed |

### Suite 14 — Magnetism, textures, and spin-orbital transport

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-066 | [Spinor texture construction and covariance](14-magnetism-spin-orbital/tbq-066-spinor-texture-construction-and-covariance.md) | TB-REQ-066 | executable |
| TBQ-067 | [Charge, spin, orbital-current, and torque continuity](14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md) | TB-REQ-067 | proposed |
| TBQ-068 | [Mechanism-resolved Hall response](14-magnetism-spin-orbital/tbq-068-mechanism-resolved-hall-response.md) | TB-REQ-068 | proposed |
| TBQ-069 | [Texture-resolution and adiabatic convergence](14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md) | TB-REQ-069 | proposed |
| TBQ-070 | [Magnetic-family generalization](14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md) | TB-REQ-070 | proposed |

### Suite 15 — Optical and thermoelectric response

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-071 | [Hamiltonian-consistent response operators](15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md) | TB-REQ-071 | proposed |
| TBQ-072 | [Optical spectral-sum and time-domain agreement](15-optical-thermoelectric/tbq-072-optical-spectral-sum-and-time-domain-agreement.md) | TB-REQ-072 | proposed |
| TBQ-073 | [Thermoelectric and Onsager relations](15-optical-thermoelectric/tbq-073-thermoelectric-and-onsager-relations.md) | TB-REQ-073 | proposed |
| TBQ-074 | [Broadening and integration convergence](15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md) | TB-REQ-074 | proposed |
| TBQ-075 | [Method transfer from exact to large sparse systems](15-optical-thermoelectric/tbq-075-method-transfer-from-exact-to-large-sparse-systems.md) | TB-REQ-075 | proposed |

### Suite 16 — Aperiodic, amorphous, and fractal lattices

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-076 | [Translation-free geometric construction](16-aperiodic-amorphous-fractal/tbq-076-translation-free-geometric-construction.md) | TB-REQ-076 | proposed |
| TBQ-077 | [Singular spectral measures and localization](16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md) | TB-REQ-077 | proposed |
| TBQ-078 | [Real-space topology without translation symmetry](16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md) | TB-REQ-078 | proposed |
| TBQ-079 | [Approximant and multifractal scaling](16-aperiodic-amorphous-fractal/tbq-079-approximant-and-multifractal-scaling.md) | TB-REQ-079 | proposed |
| TBQ-080 | [Geometry-family generalization](16-aperiodic-amorphous-fractal/tbq-080-geometry-family-generalization.md) | TB-REQ-080 | proposed |

### Suite 17 — Defects, impurities, and interfaces

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-081 | [Provenance-preserving structural defects](17-defects-interfaces/tbq-081-provenance-preserving-structural-defects.md) | TB-REQ-081 | proposed |
| TBQ-082 | [Defect-specific local chemistry](17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md) | TB-REQ-082 | proposed |
| TBQ-083 | [Embedding and supercell agreement](17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md) | TB-REQ-083 | proposed |
| TBQ-084 | [Local-state and transport consequences](17-defects-interfaces/tbq-084-local-state-and-transport-consequences.md) | TB-REQ-084 | proposed |
| TBQ-085 | [Defect-family generalization](17-defects-interfaces/tbq-085-defect-family-generalization.md) | TB-REQ-085 | proposed |

### Suite 18 — Multiscale and external validation

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-086 | [One physical question across scales](18-multiscale-validation/tbq-086-one-physical-question-across-scales.md) | TB-REQ-086 | proposed |
| TBQ-087 | [Explicit representation mapping](18-multiscale-validation/tbq-087-explicit-representation-mapping.md) | TB-REQ-087 | proposed |
| TBQ-088 | [Gauge-invariant observable comparison](18-multiscale-validation/tbq-088-gauge-invariant-observable-comparison.md) | TB-REQ-088 | proposed |
| TBQ-089 | [Discrepancy decomposition](18-multiscale-validation/tbq-089-discrepancy-decomposition.md) | TB-REQ-089 | proposed |
| TBQ-090 | [External-family validation](18-multiscale-validation/tbq-090-external-family-validation.md) | TB-REQ-090 | proposed |

### Suite 19 — Scientific-scale numerical reliability

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-091 | [Sparse-only production path](19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md) | TB-REQ-091 | proposed |
| TBQ-092 | [Scalable solver portfolio](19-scientific-scale-numerics/tbq-092-scalable-solver-portfolio.md) | TB-REQ-092 | proposed |
| TBQ-093 | [Separated numerical error budget](19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md) | TB-REQ-093 | proposed |
| TBQ-094 | [Accuracy-preserving time and memory scaling](19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md) | TB-REQ-094 | proposed |
| TBQ-095 | [Reproducible transition from exact to production scale](19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md) | TB-REQ-095 | proposed |

### Suite 20 — Parameter inference, inverse design, and uncertainty

| ID | Scientific problem | Source requirement | Status |
| --- | --- | --- | --- |
| TBQ-096 | [Constrained multi-observable parameter inference](20-inference-inverse-design/tbq-096-constrained-multi-observable-parameter-inference.md) | TB-REQ-096 | proposed |
| TBQ-097 | [Gradient verification through spectral calculations](20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md) | TB-REQ-097 | proposed |
| TBQ-098 | [Identifiability and predictive calibration](20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md) | TB-REQ-098 | proposed |
| TBQ-099 | [Independent forward validation of inverse designs](20-inference-inverse-design/tbq-099-independent-forward-validation-of-inverse-designs.md) | TB-REQ-099 | proposed |
| TBQ-100 | [Out-of-family inference holdout](20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md) | TB-REQ-100 | proposed |

## Validation

Run:

```console
python tools/check_problem_docs.py
```

The validator requires exactly 100 unique files, continuous identifiers,
all required sections, parameter rows, evidence identifiers, and honest
status metadata.
