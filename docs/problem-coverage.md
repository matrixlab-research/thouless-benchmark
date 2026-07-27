# Whole-problem backend coverage

This is the human-readable view of
[`benchmark/problem_coverage.json`](../benchmark/problem_coverage.json).
Coverage is counted only when every required claim in one domain problem has
package-backed executable evidence and an analytic or invariant-based gate.

## Summary

| Backend | Implemented | Capability gap | Not applicable | Raw coverage |
| --- | ---: | ---: | ---: | ---: |
| thouless | 13 | 71 | 16 | 13% |
| pythtb | 12 | 44 | 44 | 12% |
| kwant | 13 | 61 | 26 | 13% |

## All questions

| ID | Scientific problem | Thouless | PythTB | Kwant | Witnesses |
| --- | --- | --- | --- | --- | --- |
| TBQ-001 | [Basis and generalized-Hermiticity fidelity](problems/01-model-construction/tbq-001-basis-and-generalized-hermiticity-fidelity.md) | not applicable | not applicable | not applicable | none |
| TBQ-002 | [Energy-window and subspace fidelity](problems/01-model-construction/tbq-002-energy-window-and-subspace-fidelity.md) | capability gap | capability gap | not applicable | none |
| TBQ-003 | [Controlled hopping truncation](problems/01-model-construction/tbq-003-controlled-hopping-truncation.md) | capability gap | capability gap | capability gap | none |
| TBQ-004 | [Symmetry preservation and negative controls](problems/01-model-construction/tbq-004-symmetry-preservation-and-negative-controls.md) | capability gap | capability gap | capability gap | none |
| TBQ-005 | [Transfer beyond fitted structures](problems/01-model-construction/tbq-005-transfer-beyond-fitted-structures.md) | capability gap | capability gap | capability gap | none |
| TBQ-006 | [Degeneracy-safe band projectors](problems/02-bands-dos-fermiology/tbq-006-degeneracy-safe-band-projectors.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-007 | [Density-of-states state counting](problems/02-bands-dos-fermiology/tbq-007-density-of-states-state-counting.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-008 | [Van Hove and flat-band feature resolution](problems/02-bands-dos-fermiology/tbq-008-van-hove-and-flat-band-feature-resolution.md) | capability gap | capability gap | capability gap | none |
| TBQ-009 | [Fermi-surface topology and Lifshitz transitions](problems/02-bands-dos-fermiology/tbq-009-fermi-surface-topology-and-lifshitz-transitions.md) | capability gap | capability gap | capability gap | none |
| TBQ-010 | [Bloch and finite-real-space spectral agreement](problems/02-bands-dos-fermiology/tbq-010-bloch-and-finite-real-space-spectral-agreement.md) | implemented | implemented | implemented | `domain_spectral_reliability` |
| TBQ-011 | [Gauge-covariant Peierls substitution](problems/03-magnetic-flux-hofstadter/tbq-011-gauge-covariant-peierls-substitution.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-012 | [Magnetic translation and minimal unit cell](problems/03-magnetic-flux-hofstadter/tbq-012-magnetic-translation-and-minimal-unit-cell.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-013 | [Hofstadter gap topology and Streda consistency](problems/03-magnetic-flux-hofstadter/tbq-013-hofstadter-gap-topology-and-streda-consistency.md) | implemented | implemented | implemented | `domain_magnetic_hofstadter` |
| TBQ-014 | [Low-field Landau-level correspondence](problems/03-magnetic-flux-hofstadter/tbq-014-low-field-landau-level-correspondence.md) | capability gap | capability gap | capability gap | none |
| TBQ-015 | [Rational-approximant convergence](problems/03-magnetic-flux-hofstadter/tbq-015-rational-approximant-convergence.md) | capability gap | capability gap | capability gap | none |
| TBQ-016 | [Gauge-invariant bulk indices](problems/04-bulk-topology/tbq-016-gauge-invariant-bulk-indices.md) | capability gap | capability gap | capability gap | none |
| TBQ-017 | [Topological phase-boundary localization](problems/04-bulk-topology/tbq-017-topological-phase-boundary-localization.md) | capability gap | capability gap | capability gap | none |
| TBQ-018 | [Degeneracy-safe Wilson and nested Wilson flow](problems/04-bulk-topology/tbq-018-degeneracy-safe-wilson-and-nested-wilson-flow.md) | capability gap | capability gap | capability gap | none |
| TBQ-019 | [Agreement of independent topological diagnostics](problems/04-bulk-topology/tbq-019-agreement-of-independent-topological-diagnostics.md) | implemented | implemented | implemented | `boundary_haldane_ribbon_flow`, `bulk_haldane_chern_transition` |
| TBQ-020 | [Trivial, nearly gapless, and basis-adversarial controls](problems/04-bulk-topology/tbq-020-trivial-nearly-gapless-and-basis-adversarial-controls.md) | capability gap | capability gap | capability gap | none |
| TBQ-021 | [Termination families from one bulk model](problems/05-boundaries-bulk-boundary/tbq-021-termination-families-from-one-bulk-model.md) | capability gap | capability gap | capability gap | none |
| TBQ-022 | [Boundary-state localization and finite-size splitting](problems/05-boundaries-bulk-boundary/tbq-022-boundary-state-localization-and-finite-size-splitting.md) | implemented | implemented | implemented | `boundary_ssh_edge_localization` |
| TBQ-023 | [Finite-spectrum and surface-Green-function agreement](problems/05-boundaries-bulk-boundary/tbq-023-finite-spectrum-and-surface-green-function-agreement.md) | capability gap | not applicable | capability gap | none |
| TBQ-024 | [Conditional bulk-boundary correspondence](problems/05-boundaries-bulk-boundary/tbq-024-conditional-bulk-boundary-correspondence.md) | capability gap | capability gap | capability gap | none |
| TBQ-025 | [Geometry-family generalization](problems/05-boundaries-bulk-boundary/tbq-025-geometry-family-generalization.md) | capability gap | capability gap | capability gap | none |
| TBQ-026 | [Gauge covariance of geometric tensors](problems/06-quantum-geometry-response/tbq-026-gauge-covariance-of-geometric-tensors.md) | capability gap | capability gap | capability gap | none |
| TBQ-027 | [Competing nonlinear Hall mechanisms](problems/06-quantum-geometry-response/tbq-027-competing-nonlinear-hall-mechanisms.md) | capability gap | capability gap | capability gap | none |
| TBQ-028 | [Symmetry-forbidden nonlinear tensor components](problems/06-quantum-geometry-response/tbq-028-symmetry-forbidden-nonlinear-tensor-components.md) | capability gap | capability gap | capability gap | none |
| TBQ-029 | [Fermi-surface and derivative convergence](problems/06-quantum-geometry-response/tbq-029-fermi-surface-and-derivative-convergence.md) | capability gap | capability gap | capability gap | none |
| TBQ-030 | [Zero-Chern nonlinear bulk-boundary workflow](problems/06-quantum-geometry-response/tbq-030-zero-chern-nonlinear-bulk-boundary-workflow.md) | capability gap | not applicable | capability gap | none |
| TBQ-031 | [Reproducible disorder ensembles](problems/07-disorder-localization/tbq-031-reproducible-disorder-ensembles.md) | capability gap | capability gap | capability gap | none |
| TBQ-032 | [Cross-observable localization diagnosis](problems/07-disorder-localization/tbq-032-cross-observable-localization-diagnosis.md) | capability gap | capability gap | capability gap | none |
| TBQ-033 | [Finite-size scaling of mobility edges](problems/07-disorder-localization/tbq-033-finite-size-scaling-of-mobility-edges.md) | capability gap | capability gap | capability gap | none |
| TBQ-034 | [Topological mobility gap](problems/07-disorder-localization/tbq-034-topological-mobility-gap.md) | capability gap | capability gap | capability gap | none |
| TBQ-035 | [Statistical generalization across disorder families](problems/07-disorder-localization/tbq-035-statistical-generalization-across-disorder-families.md) | capability gap | capability gap | capability gap | none |
| TBQ-036 | [Lead modes and self-energy calibration](problems/08-open-transport/tbq-036-lead-modes-and-self-energy-calibration.md) | implemented | not applicable | implemented | `domain_lead_calibration` |
| TBQ-037 | [Scattering conservation and local continuity](problems/08-open-transport/tbq-037-scattering-conservation-and-local-continuity.md) | capability gap | not applicable | capability gap | none |
| TBQ-038 | [Transmission, local density, and finite-temperature noise](problems/08-open-transport/tbq-038-transmission-local-density-and-finite-temperature-noise.md) | capability gap | not applicable | capability gap | none |
| TBQ-039 | [Numerical stability for long evanescent devices](problems/08-open-transport/tbq-039-numerical-stability-for-long-evanescent-devices.md) | capability gap | not applicable | capability gap | none |
| TBQ-040 | [Generalization across contact families](problems/08-open-transport/tbq-040-generalization-across-contact-families.md) | capability gap | not applicable | capability gap | none |
| TBQ-041 | [Nambu convention and particle-hole symmetry](problems/09-superconducting-bdg/tbq-041-nambu-convention-and-particle-hole-symmetry.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-042 | [Phase-resolved Andreev spectrum and Josephson current](problems/09-superconducting-bdg/tbq-042-phase-resolved-andreev-spectrum-and-josephson-current.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-043 | [Majorana versus trivial near-zero modes](problems/09-superconducting-bdg/tbq-043-majorana-versus-trivial-near-zero-modes.md) | implemented | implemented | implemented | `domain_bdg_majorana` |
| TBQ-044 | [Fragility of four-pi Josephson response](problems/09-superconducting-bdg/tbq-044-fragility-of-four-pi-josephson-response.md) | capability gap | not applicable | not applicable | none |
| TBQ-045 | [Continuum-to-lattice BdG convergence](problems/09-superconducting-bdg/tbq-045-continuum-to-lattice-bdg-convergence.md) | capability gap | not applicable | not applicable | none |
| TBQ-046 | [Biorthogonal eigenvectors and residuals](problems/10-non-hermitian/tbq-046-biorthogonal-eigenvectors-and-residuals.md) | capability gap | not applicable | not applicable | none |
| TBQ-047 | [Exceptional-point order and sensitivity](problems/10-non-hermitian/tbq-047-exceptional-point-order-and-sensitivity.md) | capability gap | not applicable | not applicable | none |
| TBQ-048 | [Point-gap, line-gap, and non-Bloch invariants](problems/10-non-hermitian/tbq-048-point-gap-line-gap-and-non-bloch-invariants.md) | capability gap | not applicable | not applicable | none |
| TBQ-049 | [Periodic-open mismatch and skin localization](problems/10-non-hermitian/tbq-049-periodic-open-mismatch-and-skin-localization.md) | capability gap | not applicable | not applicable | none |
| TBQ-050 | [Non-Hermitian family generalization](problems/10-non-hermitian/tbq-050-non-hermitian-family-generalization.md) | capability gap | not applicable | not applicable | none |
| TBQ-051 | [Equivalent representations of a drive](problems/11-floquet-dynamics/tbq-051-equivalent-representations-of-a-drive.md) | not applicable | not applicable | not applicable | none |
| TBQ-052 | [Quasienergy branch and time-origin consistency](problems/11-floquet-dynamics/tbq-052-quasienergy-branch-and-time-origin-consistency.md) | not applicable | not applicable | not applicable | none |
| TBQ-053 | [Sambe, direct-propagation, and high-frequency agreement](problems/11-floquet-dynamics/tbq-053-sambe-direct-propagation-and-high-frequency-agreement.md) | not applicable | not applicable | not applicable | none |
| TBQ-054 | [Dynamical pumping and frequency conversion](problems/11-floquet-dynamics/tbq-054-dynamical-pumping-and-frequency-conversion.md) | not applicable | not applicable | not applicable | none |
| TBQ-055 | [Time-step and harmonic-cutoff holdout](problems/11-floquet-dynamics/tbq-055-time-step-and-harmonic-cutoff-holdout.md) | not applicable | not applicable | not applicable | none |
| TBQ-056 | [Interaction and double-counting declaration](problems/12-interactions-self-consistency/tbq-056-interaction-and-double-counting-declaration.md) | not applicable | not applicable | not applicable | none |
| TBQ-057 | [Self-consistency robustness and metastability](problems/12-interactions-self-consistency/tbq-057-self-consistency-robustness-and-metastability.md) | not applicable | not applicable | not applicable | none |
| TBQ-058 | [Thermodynamic comparison of competing orders](problems/12-interactions-self-consistency/tbq-058-thermodynamic-comparison-of-competing-orders.md) | not applicable | not applicable | not applicable | none |
| TBQ-059 | [Conservation and unbroken-symmetry checks](problems/12-interactions-self-consistency/tbq-059-conservation-and-unbroken-symmetry-checks.md) | not applicable | not applicable | not applicable | none |
| TBQ-060 | [Validation against small exact systems](problems/12-interactions-self-consistency/tbq-060-validation-against-small-exact-systems.md) | not applicable | not applicable | not applicable | none |
| TBQ-061 | [Commensurate and reconstructed geometry](problems/13-moire-strain-supercells/tbq-061-commensurate-and-reconstructed-geometry.md) | capability gap | capability gap | capability gap | none |
| TBQ-062 | [Geometry-dependent coupling laws](problems/13-moire-strain-supercells/tbq-062-geometry-dependent-coupling-laws.md) | capability gap | capability gap | capability gap | none |
| TBQ-063 | [Continuum-atomistic correspondence](problems/13-moire-strain-supercells/tbq-063-continuum-atomistic-correspondence.md) | capability gap | capability gap | capability gap | none |
| TBQ-064 | [Sparse observables in giant supercells](problems/13-moire-strain-supercells/tbq-064-sparse-observables-in-giant-supercells.md) | capability gap | not applicable | capability gap | none |
| TBQ-065 | [Structural-family transfer](problems/13-moire-strain-supercells/tbq-065-structural-family-transfer.md) | capability gap | capability gap | capability gap | none |
| TBQ-066 | [Spinor texture construction and covariance](problems/14-magnetism-spin-orbital/tbq-066-spinor-texture-construction-and-covariance.md) | implemented | implemented | implemented | `domain_spin_texture_covariance` |
| TBQ-067 | [Charge, spin, orbital-current, and torque continuity](problems/14-magnetism-spin-orbital/tbq-067-charge-spin-orbital-current-and-torque-continuity.md) | capability gap | not applicable | capability gap | none |
| TBQ-068 | [Mechanism-resolved Hall response](problems/14-magnetism-spin-orbital/tbq-068-mechanism-resolved-hall-response.md) | capability gap | capability gap | capability gap | none |
| TBQ-069 | [Texture-resolution and adiabatic convergence](problems/14-magnetism-spin-orbital/tbq-069-texture-resolution-and-adiabatic-convergence.md) | capability gap | not applicable | capability gap | none |
| TBQ-070 | [Magnetic-family generalization](problems/14-magnetism-spin-orbital/tbq-070-magnetic-family-generalization.md) | capability gap | capability gap | capability gap | none |
| TBQ-071 | [Hamiltonian-consistent response operators](problems/15-optical-thermoelectric/tbq-071-hamiltonian-consistent-response-operators.md) | capability gap | not applicable | capability gap | none |
| TBQ-072 | [Optical spectral-sum and time-domain agreement](problems/15-optical-thermoelectric/tbq-072-optical-spectral-sum-and-time-domain-agreement.md) | capability gap | not applicable | not applicable | none |
| TBQ-073 | [Thermoelectric and Onsager relations](problems/15-optical-thermoelectric/tbq-073-thermoelectric-and-onsager-relations.md) | capability gap | not applicable | not applicable | none |
| TBQ-074 | [Broadening and integration convergence](problems/15-optical-thermoelectric/tbq-074-broadening-and-integration-convergence.md) | capability gap | not applicable | capability gap | none |
| TBQ-075 | [Method transfer from exact to large sparse systems](problems/15-optical-thermoelectric/tbq-075-method-transfer-from-exact-to-large-sparse-systems.md) | capability gap | not applicable | capability gap | none |
| TBQ-076 | [Translation-free geometric construction](problems/16-aperiodic-amorphous-fractal/tbq-076-translation-free-geometric-construction.md) | capability gap | capability gap | capability gap | none |
| TBQ-077 | [Singular spectral measures and localization](problems/16-aperiodic-amorphous-fractal/tbq-077-singular-spectral-measures-and-localization.md) | capability gap | capability gap | capability gap | none |
| TBQ-078 | [Real-space topology without translation symmetry](problems/16-aperiodic-amorphous-fractal/tbq-078-real-space-topology-without-translation-symmetry.md) | capability gap | capability gap | capability gap | none |
| TBQ-079 | [Approximant and multifractal scaling](problems/16-aperiodic-amorphous-fractal/tbq-079-approximant-and-multifractal-scaling.md) | capability gap | capability gap | capability gap | none |
| TBQ-080 | [Geometry-family generalization](problems/16-aperiodic-amorphous-fractal/tbq-080-geometry-family-generalization.md) | capability gap | capability gap | capability gap | none |
| TBQ-081 | [Provenance-preserving structural defects](problems/17-defects-interfaces/tbq-081-provenance-preserving-structural-defects.md) | capability gap | capability gap | capability gap | none |
| TBQ-082 | [Defect-specific local chemistry](problems/17-defects-interfaces/tbq-082-defect-specific-local-chemistry.md) | capability gap | capability gap | capability gap | none |
| TBQ-083 | [Embedding and supercell agreement](problems/17-defects-interfaces/tbq-083-embedding-and-supercell-agreement.md) | capability gap | capability gap | capability gap | none |
| TBQ-084 | [Local-state and transport consequences](problems/17-defects-interfaces/tbq-084-local-state-and-transport-consequences.md) | capability gap | not applicable | capability gap | none |
| TBQ-085 | [Defect-family generalization](problems/17-defects-interfaces/tbq-085-defect-family-generalization.md) | capability gap | capability gap | capability gap | none |
| TBQ-086 | [One physical question across scales](problems/18-multiscale-validation/tbq-086-one-physical-question-across-scales.md) | capability gap | capability gap | capability gap | none |
| TBQ-087 | [Explicit representation mapping](problems/18-multiscale-validation/tbq-087-explicit-representation-mapping.md) | capability gap | capability gap | capability gap | none |
| TBQ-088 | [Gauge-invariant observable comparison](problems/18-multiscale-validation/tbq-088-gauge-invariant-observable-comparison.md) | capability gap | capability gap | capability gap | none |
| TBQ-089 | [Discrepancy decomposition](problems/18-multiscale-validation/tbq-089-discrepancy-decomposition.md) | capability gap | capability gap | capability gap | none |
| TBQ-090 | [External-family validation](problems/18-multiscale-validation/tbq-090-external-family-validation.md) | capability gap | capability gap | capability gap | none |
| TBQ-091 | [Sparse-only production path](problems/19-scientific-scale-numerics/tbq-091-sparse-only-production-path.md) | capability gap | not applicable | capability gap | none |
| TBQ-092 | [Scalable solver portfolio](problems/19-scientific-scale-numerics/tbq-092-scalable-solver-portfolio.md) | capability gap | not applicable | capability gap | none |
| TBQ-093 | [Separated numerical error budget](problems/19-scientific-scale-numerics/tbq-093-separated-numerical-error-budget.md) | capability gap | not applicable | capability gap | none |
| TBQ-094 | [Accuracy-preserving time and memory scaling](problems/19-scientific-scale-numerics/tbq-094-accuracy-preserving-time-and-memory-scaling.md) | capability gap | not applicable | capability gap | none |
| TBQ-095 | [Reproducible transition from exact to production scale](problems/19-scientific-scale-numerics/tbq-095-reproducible-transition-from-exact-to-production-scale.md) | capability gap | not applicable | capability gap | none |
| TBQ-096 | [Constrained multi-observable parameter inference](problems/20-inference-inverse-design/tbq-096-constrained-multi-observable-parameter-inference.md) | not applicable | not applicable | not applicable | none |
| TBQ-097 | [Gradient verification through spectral calculations](problems/20-inference-inverse-design/tbq-097-gradient-verification-through-spectral-calculations.md) | not applicable | not applicable | not applicable | none |
| TBQ-098 | [Identifiability and predictive calibration](problems/20-inference-inverse-design/tbq-098-identifiability-and-predictive-calibration.md) | not applicable | not applicable | not applicable | none |
| TBQ-099 | [Independent forward validation of inverse designs](problems/20-inference-inverse-design/tbq-099-independent-forward-validation-of-inverse-designs.md) | not applicable | not applicable | not applicable | none |
| TBQ-100 | [Out-of-family inference holdout](problems/20-inference-inverse-design/tbq-100-out-of-family-inference-holdout.md) | not applicable | not applicable | not applicable | none |

`Capability gap` means that the backend supplies at least one relevant
component but does not currently solve the complete problem. It is not
included in coverage. Public witnesses are not held-out validation.
