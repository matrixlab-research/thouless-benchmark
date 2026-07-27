#!/usr/bin/env python3
"""Build or verify the explicit 100-question, three-backend capability audit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "benchmark" / "problem_coverage.json"
MARKDOWN_OUTPUT = ROOT / "docs" / "problem-coverage.md"
BACKENDS = ("thouless", "pythtb", "kwant")
STATUSES = (
    "implemented",
    "implementable_unverified",
    "missing_capability",
    "not_applicable",
)

# Only whole-problem witnesses belong here. A related model or one matching
# observable is not enough.
COMMON_IMPLEMENTED = {
    "TBQ-006": ["domain_spectral_reliability"],
    "TBQ-007": ["domain_spectral_reliability"],
    "TBQ-010": ["domain_spectral_reliability"],
    "TBQ-011": ["domain_magnetic_hofstadter"],
    "TBQ-012": ["domain_magnetic_hofstadter"],
    "TBQ-013": ["domain_magnetic_hofstadter"],
    "TBQ-019": [
        "bulk_haldane_chern_transition",
        "boundary_haldane_ribbon_flow",
    ],
    "TBQ-022": ["boundary_ssh_edge_localization"],
    "TBQ-041": ["domain_bdg_majorana"],
    "TBQ-042": ["domain_bdg_majorana"],
    "TBQ-043": ["domain_bdg_majorana"],
    "TBQ-066": ["domain_spin_texture_covariance"],
}
BACKEND_IMPLEMENTED = {
    "thouless": {
        "TBQ-001": ["domain_model_fidelity"],
        "TBQ-002": ["domain_model_fidelity"],
        "TBQ-003": ["domain_model_fidelity"],
        "TBQ-004": ["domain_model_fidelity"],
        "TBQ-005": ["domain_model_fidelity"],
        "TBQ-008": ["domain_fermiology"],
        "TBQ-009": ["domain_fermiology"],
        "TBQ-014": ["domain_magnetic_convergence"],
        "TBQ-015": ["domain_magnetic_convergence"],
        "TBQ-016": ["domain_bulk_topology_controls"],
        "TBQ-017": ["domain_bulk_topology_controls"],
        "TBQ-018": ["domain_bulk_topology_controls"],
        "TBQ-020": ["domain_bulk_topology_controls"],
        "TBQ-021": ["domain_boundary_families"],
        "TBQ-023": ["domain_boundary_families"],
        "TBQ-024": ["domain_boundary_families"],
        "TBQ-025": ["domain_boundary_families"],
        "TBQ-026": ["domain_quantum_geometry_nonlinear"],
        "TBQ-027": ["domain_quantum_geometry_nonlinear"],
        "TBQ-028": ["domain_quantum_geometry_nonlinear"],
        "TBQ-030": ["domain_quantum_geometry_nonlinear"],
        "TBQ-031": ["domain_disorder_reproducibility"],
        "TBQ-036": ["domain_lead_calibration"],
        "TBQ-037": ["domain_transport_consistency"],
        "TBQ-038": ["domain_transport_consistency"],
        "TBQ-039": ["domain_transport_consistency"],
        "TBQ-040": ["domain_transport_consistency"],
        "TBQ-045": ["domain_bdg_discretization"],
        "TBQ-046": ["domain_nonhermitian_static"],
        "TBQ-047": ["domain_nonhermitian_static"],
        "TBQ-049": ["domain_nonhermitian_static"],
        "TBQ-050": ["domain_nonhermitian_static"],
        "TBQ-061": ["domain_moire_geometry"],
        "TBQ-062": ["domain_moire_geometry"],
        "TBQ-067": ["domain_spin_transport"],
        "TBQ-068": ["domain_spin_transport"],
        "TBQ-069": ["domain_spin_transport"],
        "TBQ-070": ["domain_spin_transport"],
        "TBQ-071": ["domain_response_thermoelectric"],
        "TBQ-073": ["domain_response_thermoelectric"],
        "TBQ-075": ["domain_response_thermoelectric"],
        "TBQ-076": ["domain_arbitrary_graphs"],
        "TBQ-081": ["domain_defect_workflows"],
        "TBQ-082": ["domain_defect_workflows"],
        "TBQ-083": ["domain_defect_workflows"],
        "TBQ-084": ["domain_defect_workflows"],
        "TBQ-085": ["domain_defect_workflows"],
        "TBQ-086": ["domain_multiscale_validation"],
        "TBQ-087": ["domain_multiscale_validation"],
        "TBQ-088": ["domain_multiscale_validation"],
        "TBQ-089": ["domain_multiscale_validation"],
        "TBQ-090": ["domain_multiscale_validation"],
        "TBQ-093": ["domain_sparse_numerics"],
        "TBQ-094": ["domain_sparse_numerics"],
        "TBQ-095": ["domain_sparse_numerics"],
    },
    "pythtb": {},
    "kwant": {"TBQ-036": ["domain_lead_calibration"]},
}

# A capability is included only when the pinned package exposes the relevant
# reusable primitive. Model definitions, parameter loops, statistics, and
# gauge-invariant postprocessing may be benchmark code, but the named backend
# must construct the Hamiltonian and perform every specialized solver step.
CAPABILITY_LABELS = {
    "generalized_eigensystem": "generalized H psi = E S psi eigensystem",
    "periodic_model": "periodic tight-binding Hamiltonian construction",
    "finite_model": "finite tight-binding Hamiltonian construction",
    "dense_spectrum": "dense eigensystem and eigenvectors",
    "parameterized_models": "parameterized model reconstruction",
    "topological_inputs": "eigenframes and positions for topological diagnostics",
    "quantum_geometry": "Hamiltonian derivatives or overlaps for quantum geometry",
    "analytic_hamiltonian_derivatives": (
        "analytic momentum derivatives of the Hamiltonian"
    ),
    "magnetic_models": "complex Peierls hoppings and magnetic cells",
    "surface_green_function": "semi-infinite surface Green function",
    "sparse_operators": "sparse Hamiltonian and operator path",
    "kernel_polynomial": "kernel-polynomial spectral and response solver",
    "steady_state_transport": "lead-attached steady-state transport",
    "local_continuity": "local density, current, and source operators",
    "transport_noise": "scattering amplitudes for noise correlations",
    "long_device_solver": "stable sparse long-device transport solver",
    "static_bdg": "static BdG Hamiltonian and particle-hole analysis",
    "nonhermitian_spectrum": "non-Hermitian left and right eigensystem",
    "sparse_nonhermitian_solver": (
        "sparse non-Hermitian spectral and localization solver"
    ),
    "non_bloch_topology": (
        "point-gap, line-gap, and generalized-Brillouin-zone topology"
    ),
    "real_time_propagation": "real-time state or operator propagation",
    "self_consistent_interactions": "interacting mean-field self-consistency",
    "continuum_discretization": "continuum-to-lattice discretization",
    "large_sparse_geometry": "large sparse supercell or graph construction",
    "targeted_sparse_eigenpairs": "interior or targeted sparse eigenpairs",
    "spin_observables": "spinful local observables and torque inputs",
    "response_operators": (
        "Hamiltonian-consistent velocity, charge-current, and heat-current operators"
    ),
    "frequency_response": "frequency-domain spectral response",
    "thermoelectric_response": "energy-resolved thermoelectric inputs",
    "arbitrary_graphs": "translation-free finite graph representation",
    "sparse_real_space_topology": (
        "sparse real-space topology at production-scale system sizes"
    ),
    "embedding_green_function": "defect embedding Green function",
    "iterative_linear_solver": "iterative sparse linear solve",
    "model_inference": "constrained parameter inference or inverse design",
    "automatic_differentiation": "automatic or adjoint spectral derivatives",
}

BACKEND_CAPABILITIES = {
    "thouless": {
        "version": "git 0d87773278183ddc7c254438dccbda1face04fb2",
        "source": (
            "https://github.com/matrixlab-research/thouless/tree/"
            "0d87773278183ddc7c254438dccbda1face04fb2"
        ),
        "declared_scope": (
            "Rust-native tight binding, topology, intrinsic response, sparse "
            "spectral methods, steady-state quantum transport, and dense "
            "non-Hermitian eigensystems."
        ),
        "capabilities": {
            "generalized_eigensystem": (
                "thouless::decomposition::{generalized_schur,"
                "eigenvectors_from_generalized_schur}"
            ),
            "periodic_model": (
                "thouless::model::TightBindingModel::{hamiltonian,eigensystem,"
                "momentum_derivatives}"
            ),
            "finite_model": (
                "thouless::transform::{make_finite_geometry,make_finite_cluster,"
                "make_supercell}"
            ),
            "dense_spectrum": "thouless::spectrum::hermitian_eigensystem",
            "parameterized_models": (
                "thouless::model::{ModelBuilder,TightBindingModel}"
            ),
            "topological_inputs": (
                "thouless::topology::{chern_numbers_on_uniform_grid,"
                "wilson_loop_eigenphases,local_chern_marker_from_hamiltonian}"
            ),
            "quantum_geometry": (
                "thouless::topology::quantum_geometric_tensor_from_"
                "hamiltonian_derivatives"
            ),
            "analytic_hamiltonian_derivatives": (
                "thouless::model::TightBindingModel::{"
                "reduced_momentum_derivatives,cartesian_momentum_derivatives}"
            ),
            "magnetic_models": (
                "thouless::gauge::{uniform_field_peierls_phase,"
                "peierls_phases_from_fluxes}"
            ),
            "surface_green_function": (
                "thouless::transport::surface_green_function"
            ),
            "sparse_operators": (
                "thouless::linear_operator::{CsrMatrix,LinearOperator}"
            ),
            "kernel_polynomial": "thouless::kpm",
            "steady_state_transport": (
                "thouless::transport::{solve_open_system,ScatteringMatrix}"
            ),
            "local_continuity": (
                "thouless::observables::{local_densities,bond_currents,"
                "local_sources}"
            ),
            "transport_noise": "thouless::transport::partition_shot_noise",
            "long_device_solver": (
                "thouless::transport::SparseOpenSystem with ILU0-GMRES"
            ),
            "static_bdg": (
                "thouless::model plus thouless::symmetry::"
                "particle_hole_symmetric_basis"
            ),
            "nonhermitian_spectrum": (
                "thouless::decomposition::{schur,eigenvectors_from_schur}"
            ),
            "continuum_discretization": (
                "thouless::continuum::finite_difference_stencil"
            ),
            "large_sparse_geometry": (
                "thouless::block_system::assemble_block_csr and "
                "thouless::graph::CompressedGraph"
            ),
            "spin_observables": (
                "thouless::observables::{bond_currents,local_sources,"
                "pauli_coefficients}"
            ),
            "response_operators": (
                "thouless::model::TightBindingModel::momentum_derivatives plus "
                "thouless::observables::{bond_currents,local_sources}"
            ),
            "frequency_response": (
                "thouless::kpm::correlation_response and "
                "thouless::response"
            ),
            "thermoelectric_response": (
                "thouless::transport::ScatteringMatrix plus "
                "thouless::response::FermiDistribution"
            ),
            "arbitrary_graphs": (
                "thouless::graph::{DirectedGraphBuilder,CompressedGraph}"
            ),
            "embedding_green_function": (
                "thouless::transport::solve_open_system_from_self_energies"
            ),
            "iterative_linear_solver": (
                "thouless::linear_operator::{gmres,"
                "gmres_with_right_preconditioner}"
            ),
        },
    },
    "pythtb": {
        "version": (
            "2.0.0; source commit "
            "0f3bb0b8588101cafbdf428c70fb43c9302fe7cf"
        ),
        "source": (
            "https://github.com/pythtb/pythtb/tree/"
            "0f3bb0b8588101cafbdf428c70fb43c9302fe7cf"
        ),
        "declared_scope": (
            "Construction and analysis of static Hermitian tight-binding "
            "models for topological band theory."
        ),
        "capabilities": {
            "periodic_model": "pythtb.TBModel.hamiltonian",
            "finite_model": (
                "pythtb.TBModel::{cut_piece,make_finite,make_supercell}"
            ),
            "dense_spectrum": (
                "pythtb.TBModel::{solve_one,solve_all,solve_ham}"
            ),
            "parameterized_models": (
                "pythtb.TBModel::{with_parameters,set_parameters}"
            ),
            "topological_inputs": (
                "pythtb.WFArray plus TBModel::{chern_number,"
                "local_chern_marker}"
            ),
            "quantum_geometry": (
                "pythtb.TBModel::{quantum_geometric_tensor,"
                "berry_curvature,quantum_metric}"
            ),
            "analytic_hamiltonian_derivatives": (
                "pythtb.TBModel.velocity analytic k derivatives"
            ),
            "magnetic_models": (
                "pythtb.TBModel.set_hop with complex hopping amplitudes"
            ),
            "static_bdg": (
                "pythtb.TBModel spinful Hermitian block Hamiltonians"
            ),
            "spin_observables": (
                "pythtb.TBModel spinful eigenvectors, velocity, and "
                "position operators"
            ),
            "response_operators": (
                "pythtb.TBModel::{velocity,position_matrix}"
            ),
            "frequency_response": (
                "pythtb.TBModel::{velocity,solve_all} for eigenstate sums"
            ),
            "thermoelectric_response": (
                "pythtb.TBModel::{velocity,solve_all} for band integrals"
            ),
            "arbitrary_graphs": (
                "pythtb.Lattice and finite TBModel orbital/hopping tables"
            ),
        },
    },
    "kwant": {
        "version": (
            "1.5.0; source commit "
            "de315f171270d62ee2412c4084260c912cc4d58f"
        ),
        "source": (
            "https://gitlab.kwant-project.org/kwant/kwant/-/tree/"
            "de315f171270d62ee2412c4084260c912cc4d58f"
        ),
        "declared_scope": (
            "Static Hermitian tight-binding systems with a strong focus on "
            "sparse steady-state quantum transport."
        ),
        "capabilities": {
            "periodic_model": (
                "kwant.physics.Bands and kwant.wraparound.wraparound"
            ),
            "finite_model": "kwant.Builder and kwant.system.FiniteSystem",
            "dense_spectrum": (
                "kwant.system.System.hamiltonian_submatrix with SciPy "
                "eigensolvers"
            ),
            "parameterized_models": (
                "kwant.Builder value functions and params binding"
            ),
            "topological_inputs": (
                "kwant.wraparound plus hamiltonian_submatrix for shared "
                "eigenframe postprocessing"
            ),
            "quantum_geometry": (
                "kwant.wraparound parameterized Bloch Hamiltonians for "
                "derivative or overlap postprocessing"
            ),
            "magnetic_models": (
                "kwant.builder::{add_peierls_phase,magnetic_gauge}"
            ),
            "surface_green_function": (
                "kwant.system.InfiniteSystem.selfenergy and "
                "kwant.solvers.default.greens_function"
            ),
            "sparse_operators": (
                "kwant.system.System.hamiltonian_submatrix(sparse=True)"
            ),
            "kernel_polynomial": (
                "kwant.kpm::{SpectralDensity,Correlator,conductivity}"
            ),
            "steady_state_transport": (
                "kwant.solvers.default::{smatrix,greens_function,wave_function}"
            ),
            "local_continuity": (
                "kwant.operator::{Density,Current,Source}"
            ),
            "transport_noise": "kwant.physics.two_terminal_shotnoise",
            "long_device_solver": (
                "kwant stabilized lead modes plus sparse solver interface"
            ),
            "static_bdg": (
                "kwant.Builder matrix-valued onsite and hopping blocks"
            ),
            "continuum_discretization": "kwant.continuum.discretize",
            "large_sparse_geometry": (
                "kwant.Builder finalized to a sparse graph Hamiltonian"
            ),
            "targeted_sparse_eigenpairs": (
                "sparse Hamiltonian output plus declared SciPy eigsh dependency"
            ),
            "spin_observables": (
                "kwant.operator::{Density,Current,Source} with matrix onsite"
            ),
            "response_operators": (
                "kwant.operator::Current plus kwant.kpm::conductivity"
            ),
            "frequency_response": (
                "kwant.kpm::{Correlator,conductivity}"
            ),
            "thermoelectric_response": (
                "energy-resolved kwant.smatrix and transmission eigenvalues"
            ),
            "arbitrary_graphs": "kwant.Builder and kwant.graph",
            "embedding_green_function": (
                "kwant.builder.SelfEnergyLead and "
                "kwant.solvers.default.greens_function"
            ),
            "iterative_linear_solver": (
                "sparse Hamiltonian output plus declared SciPy sparse solvers"
            ),
        },
    },
}

# These are whole-problem requirements, not an API wish list. A requirement
# names only a specialized primitive that cannot be replaced by case-specific
# answer logic. General parameter sweeps, model definitions, statistics, and
# invariant postprocessing are shared benchmark orchestration.
PROBLEM_REQUIREMENTS = {
    1: ("periodic_model", "generalized_eigensystem"),
    2: (
        "periodic_model",
        "generalized_eigensystem",
        "dense_spectrum",
        "topological_inputs",
    ),
    3: (
        "periodic_model",
        "generalized_eigensystem",
        "dense_spectrum",
        "frequency_response",
    ),
    4: (
        "periodic_model",
        "generalized_eigensystem",
        "dense_spectrum",
        "parameterized_models",
    ),
    5: (
        "periodic_model",
        "generalized_eigensystem",
        "dense_spectrum",
        "parameterized_models",
    ),
    6: ("periodic_model", "dense_spectrum", "topological_inputs"),
    7: ("periodic_model", "finite_model", "dense_spectrum"),
    8: ("periodic_model", "dense_spectrum"),
    9: ("periodic_model", "dense_spectrum"),
    10: ("periodic_model", "finite_model", "dense_spectrum"),
    11: ("finite_model", "magnetic_models", "dense_spectrum"),
    12: ("periodic_model", "magnetic_models", "dense_spectrum"),
    13: ("periodic_model", "magnetic_models", "topological_inputs"),
    14: ("periodic_model", "magnetic_models", "dense_spectrum"),
    15: (
        "periodic_model",
        "finite_model",
        "magnetic_models",
        "topological_inputs",
    ),
    16: ("periodic_model", "dense_spectrum", "topological_inputs"),
    17: (
        "periodic_model",
        "dense_spectrum",
        "topological_inputs",
        "parameterized_models",
    ),
    18: ("periodic_model", "dense_spectrum", "topological_inputs"),
    19: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "topological_inputs",
    ),
    20: (
        "periodic_model",
        "dense_spectrum",
        "topological_inputs",
        "parameterized_models",
    ),
    21: ("periodic_model", "finite_model"),
    22: ("finite_model", "dense_spectrum"),
    23: ("finite_model", "dense_spectrum", "surface_green_function"),
    24: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "topological_inputs",
    ),
    25: ("periodic_model", "finite_model", "dense_spectrum"),
    26: (
        "periodic_model",
        "dense_spectrum",
        "quantum_geometry",
        "analytic_hamiltonian_derivatives",
    ),
    27: ("periodic_model", "quantum_geometry", "frequency_response"),
    28: ("periodic_model", "quantum_geometry", "frequency_response"),
    29: (
        "periodic_model",
        "quantum_geometry",
        "frequency_response",
        "parameterized_models",
        "automatic_differentiation",
    ),
    30: (
        "periodic_model",
        "finite_model",
        "quantum_geometry",
        "steady_state_transport",
    ),
    31: ("finite_model", "parameterized_models", "nonhermitian_spectrum"),
    32: (
        "finite_model",
        "sparse_operators",
        "kernel_polynomial",
        "steady_state_transport",
        "sparse_nonhermitian_solver",
    ),
    33: (
        "finite_model",
        "sparse_operators",
        "steady_state_transport",
        "sparse_nonhermitian_solver",
    ),
    34: (
        "finite_model",
        "sparse_operators",
        "topological_inputs",
        "steady_state_transport",
        "sparse_nonhermitian_solver",
    ),
    35: (
        "finite_model",
        "sparse_operators",
        "parameterized_models",
        "sparse_nonhermitian_solver",
    ),
    36: ("surface_green_function", "steady_state_transport"),
    37: (
        "steady_state_transport",
        "local_continuity",
        "transport_noise",
    ),
    38: (
        "steady_state_transport",
        "local_continuity",
        "transport_noise",
    ),
    39: ("steady_state_transport", "long_device_solver"),
    40: (
        "steady_state_transport",
        "surface_green_function",
        "parameterized_models",
    ),
    41: ("finite_model", "dense_spectrum", "static_bdg"),
    42: ("finite_model", "dense_spectrum", "static_bdg"),
    43: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "static_bdg",
        "topological_inputs",
    ),
    44: ("finite_model", "static_bdg", "real_time_propagation"),
    45: (
        "finite_model",
        "dense_spectrum",
        "static_bdg",
        "parameterized_models",
        "continuum_discretization",
    ),
    46: ("nonhermitian_spectrum",),
    47: ("nonhermitian_spectrum", "parameterized_models"),
    48: (
        "nonhermitian_spectrum",
        "topological_inputs",
        "non_bloch_topology",
    ),
    49: ("nonhermitian_spectrum", "finite_model", "periodic_model"),
    50: ("nonhermitian_spectrum", "finite_model", "parameterized_models"),
    51: ("real_time_propagation", "parameterized_models"),
    52: ("real_time_propagation", "dense_spectrum"),
    53: ("real_time_propagation", "dense_spectrum"),
    54: (
        "real_time_propagation",
        "local_continuity",
        "topological_inputs",
    ),
    55: ("real_time_propagation", "parameterized_models"),
    56: ("self_consistent_interactions",),
    57: ("self_consistent_interactions", "parameterized_models"),
    58: ("self_consistent_interactions", "dense_spectrum"),
    59: ("self_consistent_interactions", "local_continuity"),
    60: ("self_consistent_interactions", "dense_spectrum"),
    61: ("large_sparse_geometry",),
    62: ("large_sparse_geometry", "parameterized_models"),
    63: (
        "large_sparse_geometry",
        "continuum_discretization",
        "sparse_operators",
        "targeted_sparse_eigenpairs",
        "topological_inputs",
    ),
    64: (
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
    ),
    65: (
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
        "parameterized_models",
    ),
    66: ("finite_model", "dense_spectrum", "spin_observables"),
    67: ("finite_model", "spin_observables", "local_continuity"),
    68: ("periodic_model", "spin_observables", "frequency_response"),
    69: (
        "finite_model",
        "spin_observables",
        "steady_state_transport",
    ),
    70: (
        "finite_model",
        "spin_observables",
        "steady_state_transport",
        "parameterized_models",
    ),
    71: (
        "generalized_eigensystem",
        "sparse_operators",
        "response_operators",
    ),
    72: ("frequency_response", "real_time_propagation"),
    73: (
        "thermoelectric_response",
        "sparse_operators",
        "parameterized_models",
    ),
    74: (
        "frequency_response",
        "kernel_polynomial",
        "real_time_propagation",
    ),
    75: ("frequency_response", "kernel_polynomial", "sparse_operators"),
    76: ("arbitrary_graphs", "finite_model", "large_sparse_geometry"),
    77: (
        "arbitrary_graphs",
        "finite_model",
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
    ),
    78: (
        "arbitrary_graphs",
        "finite_model",
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "topological_inputs",
        "sparse_real_space_topology",
    ),
    79: (
        "arbitrary_graphs",
        "finite_model",
        "large_sparse_geometry",
        "sparse_operators",
        "targeted_sparse_eigenpairs",
    ),
    80: (
        "arbitrary_graphs",
        "finite_model",
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
        "sparse_real_space_topology",
        "parameterized_models",
    ),
    81: ("arbitrary_graphs", "finite_model"),
    82: (
        "arbitrary_graphs",
        "finite_model",
        "dense_spectrum",
        "embedding_green_function",
    ),
    83: (
        "finite_model",
        "dense_spectrum",
        "embedding_green_function",
    ),
    84: (
        "finite_model",
        "dense_spectrum",
        "steady_state_transport",
    ),
    85: (
        "arbitrary_graphs",
        "finite_model",
        "sparse_operators",
        "kernel_polynomial",
        "parameterized_models",
    ),
    86: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "sparse_operators",
        "continuum_discretization",
        "parameterized_models",
    ),
    87: (
        "periodic_model",
        "finite_model",
        "generalized_eigensystem",
        "dense_spectrum",
        "topological_inputs",
    ),
    88: (
        "periodic_model",
        "finite_model",
        "sparse_operators",
        "topological_inputs",
        "steady_state_transport",
        "frequency_response",
    ),
    89: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "sparse_operators",
        "parameterized_models",
    ),
    90: (
        "periodic_model",
        "finite_model",
        "dense_spectrum",
        "sparse_operators",
        "parameterized_models",
    ),
    91: (
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
        "iterative_linear_solver",
        "real_time_propagation",
    ),
    92: (
        "sparse_operators",
        "kernel_polynomial",
        "targeted_sparse_eigenpairs",
        "iterative_linear_solver",
        "real_time_propagation",
    ),
    93: (
        "sparse_operators",
        "kernel_polynomial",
        "iterative_linear_solver",
    ),
    94: ("sparse_operators", "kernel_polynomial"),
    95: (
        "large_sparse_geometry",
        "sparse_operators",
        "kernel_polynomial",
        "parameterized_models",
    ),
    96: ("model_inference", "parameterized_models"),
    97: (
        "model_inference",
        "automatic_differentiation",
        "parameterized_models",
    ),
    98: ("model_inference", "parameterized_models"),
    99: (
        "model_inference",
        "parameterized_models",
        "finite_model",
        "steady_state_transport",
    ),
    100: ("model_inference", "parameterized_models"),
}

# not_applicable is a declared-scope judgment, not a synonym for a missing
# feature. Mixed-domain questions remain missing_capability when the package
# handles the rest of the workflow but lacks one essential primitive.
OUT_OF_SCOPE = {
    "thouless": set(range(51, 61)) | set(range(96, 101)),
    "pythtb": (
        set(range(36, 41))
        | set(range(46, 61))
        | set(range(91, 101))
    ),
    "kwant": set(range(46, 61)) | set(range(96, 101)),
}

OUT_OF_SCOPE_REASON = {
    "thouless": {
        "51-55": "The pinned Thouless scope is static and steady-state; Floquet propagation is outside that declared scope.",
        "56-60": "Interacting mean-field self-consistency is outside the pinned noninteracting Thouless scope.",
        "96-100": "Parameter inference and inverse design are outside the pinned Thouless solver scope.",
    },
    "pythtb": {
        "36-40": "Semi-infinite leads and open-system scattering are outside PythTB's declared static band-theory scope.",
        "46-50": "Non-Hermitian lattice models are outside PythTB's Hermitian model contract.",
        "51-55": "Floquet propagation is outside PythTB's declared static band-theory scope.",
        "56-60": "Interacting mean-field self-consistency is outside PythTB's noninteracting model scope.",
        "91-95": "Sparse production-scale solver engineering is outside PythTB's dense band-theory scope.",
        "96-100": "Parameter inference and inverse design are outside PythTB's declared scope.",
    },
    "kwant": {
        "46-50": "Non-Hermitian lattice models are outside Kwant Builder's Hermitian system contract.",
        "51-55": "Floquet propagation is outside Kwant 1.5's static steady-state transport scope.",
        "56-60": "Interacting mean-field self-consistency is outside Kwant 1.5's noninteracting transport scope.",
        "96-100": "Parameter inference and inverse design are outside Kwant 1.5's declared scope.",
    },
}


def problem_rows() -> list[tuple[str, str, str, str]]:
    rows = []
    paths = sorted(
        (ROOT / "docs" / "problems").glob("[0-9][0-9]-*/tbq-[0-9][0-9][0-9]-*.md")
    )
    for path in paths:
        text = path.read_text()
        qid = re.search(r"^id: (TBQ-[0-9]{3})$", text, re.MULTILINE)
        title = re.search(r"^# TBQ-[0-9]{3} — (.+)$", text, re.MULTILINE)
        if qid is None or title is None:
            raise ValueError(f"cannot parse {path}")
        rows.append(
            (
                qid.group(1),
                title.group(1),
                path.parent.name,
                path.relative_to(ROOT / "docs").as_posix(),
            )
        )
    if len(rows) != 100:
        raise ValueError(f"expected 100 problems, found {len(rows)}")
    expected_requirements = set(range(1, 101))
    if set(PROBLEM_REQUIREMENTS) != expected_requirements:
        raise ValueError("problem capability requirements do not cover 1..100 exactly")
    for number, capabilities in PROBLEM_REQUIREMENTS.items():
        if len(capabilities) != len(set(capabilities)):
            raise ValueError(f"duplicate capability in TBQ-{number:03d}")
        unknown = set(capabilities) - set(CAPABILITY_LABELS)
        if unknown:
            raise ValueError(
                f"unknown capabilities in TBQ-{number:03d}: {sorted(unknown)}"
            )
    return rows


def scope_reason(backend: str, number: int) -> str:
    for interval, reason in OUT_OF_SCOPE_REASON[backend].items():
        lower, upper = (int(part) for part in interval.split("-"))
        if lower <= number <= upper:
            return reason
    raise ValueError(f"missing scope reason for {backend} TBQ-{number:03d}")


def audit_entry(qid: str, backend: str) -> dict:
    number = int(qid.split("-")[1])
    required = list(PROBLEM_REQUIREMENTS[number])
    witnesses = COMMON_IMPLEMENTED.get(qid) or BACKEND_IMPLEMENTED[backend].get(qid)
    supported = BACKEND_CAPABILITIES[backend]["capabilities"]
    available = [capability for capability in required if capability in supported]
    missing = [capability for capability in required if capability not in supported]
    evidence = {
        capability: supported[capability]
        for capability in available
    }

    if witnesses is not None:
        if missing:
            raise ValueError(
                f"{backend} {qid} is marked implemented but lacks {missing}"
            )
        return {
            "status": "implemented",
            "witness_cases": witnesses,
            "required_capabilities": required,
            "available_capabilities": available,
            "missing_capabilities": [],
            "capability_evidence": evidence,
            "reason": (
                "Every required claim is exercised by package-backed code, an "
                "independent analytic or invariant-based gate, a recorded "
                "result, and CI."
            ),
        }
    if number in OUT_OF_SCOPE[backend]:
        return {
            "status": "not_applicable",
            "witness_cases": [],
            "required_capabilities": required,
            "available_capabilities": available,
            "missing_capabilities": missing,
            "capability_evidence": evidence,
            "reason": scope_reason(backend, number),
        }
    if not missing:
        return {
            "status": "implementable_unverified",
            "witness_cases": [],
            "required_capabilities": required,
            "available_capabilities": available,
            "missing_capabilities": [],
            "capability_evidence": evidence,
            "reason": (
                "The pinned package has source-level evidence for every "
                "specialized primitive required by this problem. Only model "
                "orchestration, acceptance gates, result recording, and CI "
                "remain; no complete evaluator has yet verified the claim."
            ),
        }
    missing_labels = ", ".join(CAPABILITY_LABELS[item] for item in missing)
    return {
        "status": "missing_capability",
        "witness_cases": [],
        "required_capabilities": required,
        "available_capabilities": available,
        "missing_capabilities": missing,
        "capability_evidence": evidence,
        "reason": (
            "The complete workflow requires unsupported reusable primitives: "
            f"{missing_labels}. Implementing the problem therefore requires "
            "new general package capability, not only benchmark orchestration."
        ),
    }


def build() -> dict:
    problems = []
    for qid, title, suite, document in problem_rows():
        problems.append(
            {
                "id": qid,
                "title": title,
                "suite": suite,
                "document": document,
                "backends": {
                    backend: audit_entry(qid, backend) for backend in BACKENDS
                },
            }
        )
    summary = {}
    for backend in BACKENDS:
        counts = {
            status: sum(
                problem["backends"][backend]["status"] == status
                for problem in problems
            )
            for status in STATUSES
        }
        summary[backend] = {
            **counts,
            "total_questions": 100,
            "verified_coverage_percent": counts["implemented"],
        }
    return {
        "schema_version": 2,
        "policy": {
            "unit": "whole scientific problem",
            "implemented": (
                "all required claims have executable package-backed witnesses, "
                "independent gates, recorded results, and CI"
            ),
            "implementable_unverified": (
                "the pinned package has every required specialized primitive, "
                "but the end-to-end evaluator or verification evidence is missing"
            ),
            "missing_capability": (
                "at least one required reusable solver or representation is "
                "absent, so test orchestration alone cannot complete the problem"
            ),
            "not_applicable": (
                "the core scientific workflow lies outside the package's "
                "declared scope; this is not inferred merely from a missing API"
            ),
            "shared_postprocessing": (
                "model definitions, parameter loops, statistics, and "
                "gauge-invariant postprocessing may be shared only after the "
                "named backend constructs the Hamiltonian; a documented package "
                "dependency may supply a numerical kernel only when that is the "
                "package's normal exposed workflow and the dependency is named; "
                "unrelated hidden NumPy or SciPy solvers do not count"
            ),
            "scientific_scale": (
                "the documented parameter range is part of the problem; a "
                "dense toy-size route does not establish availability of a "
                "required sparse or production-scale capability"
            ),
            "public_is_not_held_out": True,
        },
        "backend_capabilities": BACKEND_CAPABILITIES,
        "capability_labels": CAPABILITY_LABELS,
        "summary": summary,
        "problems": problems,
    }


def format_capabilities(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) or "none"


def render_markdown(payload: dict) -> str:
    labels = {
        "implemented": "implemented",
        "implementable_unverified": "implementable, unverified",
        "missing_capability": "missing capability",
        "not_applicable": "not applicable",
    }
    lines = [
        "# Whole-problem backend capability assessment",
        "",
        "This is the human-readable view of",
        "[`benchmark/problem_coverage.json`](../benchmark/problem_coverage.json).",
        "The assessment unit is one complete scientific problem, not an API name.",
        "",
        "## Status definitions",
        "",
        "- **Implemented:** a package-backed evaluator, independent gate, recorded",
        "  result, and CI witness every required claim.",
        "- **Implementable, unverified:** source evidence shows that every specialized",
        "  primitive already exists; only end-to-end orchestration and verification",
        "  remain. This is not counted as coverage.",
        "- **Missing capability:** at least one reusable solver or representation is",
        "  absent, so writing test glue alone cannot complete the workflow.",
        "- **Not applicable:** the core workflow lies outside the package's declared",
        "  scope. A missing API by itself is not enough for this label.",
        "",
        "Shared model definitions, parameter loops, statistics, and gauge-invariant",
        "postprocessing are allowed only after the named backend constructs the",
        "Hamiltonian. A specialized solver cannot be hidden in NumPy or SciPy and",
        "then attributed to the backend. A documented dependency counts only when",
        "the package exposes the required representation as its normal workflow,",
        "and the dependency is named in the evidence.",
        "",
        "The documented parameter range is part of each assessment. A dense",
        "toy-size route does not establish a sparse or production-scale capability.",
        "",
        "## Summary",
        "",
        "| Backend | Implemented | Implementable, unverified | Missing capability | Not applicable | Verified coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for backend in BACKENDS:
        item = payload["summary"][backend]
        lines.append(
            f"| {backend} | {item['implemented']} | "
            f"{item['implementable_unverified']} | "
            f"{item['missing_capability']} | {item['not_applicable']} | "
            f"{item['verified_coverage_percent']}% |"
        )
    lines.extend(
        [
            "",
            "## Package evidence boundary",
            "",
            "| Backend | Pinned version | Source | Declared scope |",
            "| --- | --- | --- | --- |",
        ]
    )
    for backend in BACKENDS:
        profile = payload["backend_capabilities"][backend]
        lines.append(
            f"| {backend} | {profile['version']} | "
            f"[pinned source]({profile['source']}) | "
            f"{profile['declared_scope']} |"
        )
    lines.extend(
        [
            "",
            "The machine-readable audit records the exact package API evidence used",
            "for every required capability. The principal inspected sources were the",
            "pinned Thouless Rust source and coverage manifests, the installed",
            "PythTB 2.0 package source and metadata, and the installed Kwant 1.5",
            "package source and metadata.",
            "",
            "## All questions",
            "",
            "| ID | Scientific problem | Thouless | PythTB | Kwant | Witnesses |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for problem in payload["problems"]:
        witnesses = sorted(
            {
                witness
                for record in problem["backends"].values()
                for witness in record["witness_cases"]
            }
        )
        link = f"[{problem['title']}]({problem['document']})"
        lines.append(
            f"| {problem['id']} | {link} | "
            f"{labels[problem['backends']['thouless']['status']]} | "
            f"{labels[problem['backends']['pythtb']['status']]} | "
            f"{labels[problem['backends']['kwant']['status']]} | "
            f"{', '.join(f'`{item}`' for item in witnesses) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Detailed 300-way assessment",
            "",
            "| ID | Backend | Status | Required capabilities | Missing capabilities |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for problem in payload["problems"]:
        for backend in BACKENDS:
            record = problem["backends"][backend]
            lines.append(
                f"| {problem['id']} | {backend} | {labels[record['status']]} | "
                f"{format_capabilities(record['required_capabilities'])} | "
                f"{format_capabilities(record['missing_capabilities'])} |"
            )
    lines.extend(
        [
            "",
            "`Implementable, unverified` is an engineering queue, not verified",
            "scientific coverage. Public witnesses are not held-out validation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown = render_markdown(payload)
    if args.check:
        if (
            not OUTPUT.exists()
            or OUTPUT.read_text() != encoded
            or not MARKDOWN_OUTPUT.exists()
            or MARKDOWN_OUTPUT.read_text() != markdown
        ):
            print(
                "problem capability audit is missing or stale; run "
                "python tools/build_problem_coverage.py",
                file=sys.stderr,
            )
            return 1
        print("problem capability audit passed: 100 questions x 3 backends")
        return 0
    OUTPUT.write_text(encoded)
    MARKDOWN_OUTPUT.write_text(markdown)
    print(f"wrote {OUTPUT} and {MARKDOWN_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
