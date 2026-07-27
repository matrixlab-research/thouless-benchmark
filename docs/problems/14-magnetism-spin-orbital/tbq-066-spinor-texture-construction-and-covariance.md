---
id: TBQ-066
suite: 14-magnetism-spin-orbital
source_requirement: TB-REQ-066
status: executable
acceptance_class: exact
lkm_snapshot: 2026-07-27
---

# TBQ-066 — Spinor texture construction and covariance

## Scientific question

Does a site-resolved exchange texture have the intended winding and transform correctly
under global spin rotation?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Spinful square or triangular lattices coupled to ferromagnetic, antiferromagnetic,
spiral, domain-wall, and skyrmion exchange textures.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `J/t` | exchange coupling | 0.1 to 10 | dimensionless |
| `lambda_SO/t` | spin-orbit coupling | 0 to 1 | dimensionless |
| `R_sk/a` | skyrmion or texture radius | 2 to 64 | lattice constants |
| `q` | spiral wavevector | 0 to pi | inverse lattice constant |
| `E_F/t` | Fermi energy | -4 to 4 | dimensionless |

## Required computation

Build analytic textures, compute discrete topological charge, rotate both texture and
spin basis, and compare spectra.

## Expected result

Topological charge converges to the prescribed value and global spin rotations leave
spectra invariant without spin-orbit coupling.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `exact`

Charge error below 1 percent at final resolution and spectral error below 1e-10.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Hide an antiferromagnetic skyrmion and noncoplanar spiral.

Suite-wide isolation rule: Hold out texture topology, chirality, sublattice structure, spin-orbit strength, and
contacts.

## Evidence

- LKM seeds: `gcn_24b0aa946f4346b7`, `gcn_a572d7be0648498e`, and `gcn_9897d0405aaa497b`.
- Representative source: [Topological orbital Hall effect caused by skyrmions and antiferromagnetic skyrmions](https://doi.org/10.48550/arXiv.2410.00820).
- Source requirement: [`TB-REQ-066`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`executable`:
[`domain_spin_texture_covariance`](../../../benchmark/domain_cases.json) passes with
native Thouless, original PythTB, and original Kwant. The backend-level witnesses
and remaining gaps are recorded in
[`benchmark/problem_coverage.json`](../../../benchmark/problem_coverage.json).
