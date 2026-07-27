---
id: TBQ-100
suite: 20-inference-inverse-design
source_requirement: TB-REQ-100
status: proposed
acceptance_class: reference
lkm_snapshot: 2026-07-27
---

# TBQ-100 — Out-of-family inference holdout

## Scientific question

Does an inference or design workflow generalize beyond the model family and noise
pattern used during development?

## Benchmark adaptation

This is a benchmark adaptation motivated by the cited research. It is not a claim to
reproduce the source paper. The benchmark family is:

Synthetic and material-like tight-binding spectra or transport generated from known
parameters, followed by constrained inference and forward-validated design.

## Parameters

`t` or another explicitly named scale is the reference energy when a row is
dimensionless. A concrete case must freeze exact values, conventions, and random seeds
inside the public or held-out evaluator.

| Name | Meaning | Public development range | Unit |
| --- | --- | --- | --- |
| `N_theta` | unknown model parameters | 2 to 100 | count |
| `sigma_y` | observation noise | 0 to 0.10 | observable scale |
| `N_obs` | measured observables | 10 to 10000 | count |
| `lambda_reg` | regularization weight | 0 to 10 | dimensionless |
| `N_start` | optimization restarts | 1 to 100 | count |

## Required computation

Freeze code, priors, losses, and tolerances before exposing a hidden lattice or device
family and target observable.

## Expected result

The workflow either meets calibrated predictive gates or reports out-of-distribution
uncertainty; it does not retune on hidden outputs.

The expected result is a scientific relation, invariant, trend, or independently
generated reference. Cross-package agreement alone is not ground truth.

## Acceptance and convergence

**Class:** `reference`

Predeclared hidden score and calibration gate with immutable evaluation artifacts.

Any numerical tolerance must be fixed before held-out evaluation and justified by the
reference uncertainty, conditioning, and refinement study.

## Held-out variants

Isolate all hidden forward outputs and model-family labels until scoring.

Suite-wide isolation rule: Hold out lattice or device family, target observable, noise model, and parameter regime;
hidden forward outputs remain unavailable during fitting.

## Evidence

- LKM seeds: `gcn_f5b9878833c94b63`, `gcn_5a24091ab6c34b61`, and `gcn_17339133dbf44624`.
- Representative source: [Inverse magnetoconductance design by automatic differentiation](https://doi.org/10.1103/physrevb.110.214201).
- Source requirement: [`TB-REQ-100`](../../tight-binding-domain-benchmark-requirements.md)
  in the domain-requirements derivation.
- LKM retrieval rank is not a confidence or correctness probability.

## Implementation status

`proposed`: this document specifies a scientific problem but does not claim that any backend currently passes it. No current executable case is asserted to cover this full problem.
