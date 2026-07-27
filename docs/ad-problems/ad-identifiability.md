# Identifiability and predictive ambiguity

**Case:** `ad_identifiability`  
**Motivating requirement:** TBQ-098  
**AD gate:** AD-G14

## Scientific question

Can automatic sensitivities distinguish parameter recovery from genuine
identifiability, and can an additional local observable lift a known spectral
ambiguity?

## Benchmark adaptation

A two-parameter spectrum is constructed to depend only on one linear
combination. Its sensitivity matrix therefore has one known null direction.
A local perturbation observable responds to the orthogonal combination and is
then appended to the information matrix.

## Parameters

- Model parameters: `2`.
- Spectral observations: `5`.
- Local perturbation observations: `1`.
- Fisher analysis: exact symmetric `2 x 2` eigenproblem.

## Required computation

Build spectral gradients with native eigenderivatives, form the Fisher matrix,
compare its smallest-eigenvector direction with the analytic nullspace, and
repeat after adding the local observable.

## Expected result

The spectral Fisher matrix is rank deficient in the planted direction. The
local measurement gives nonzero sensitivity along that direction and removes
the degeneracy. Predictions that depend on the null direction remain visibly
ambiguous before the extra measurement.

## Acceptance

- Spectral null eigenvalue and eigenvector match the analytic construction.
- Augmented minimum Fisher eigenvalue is strictly positive.
- Two spectrally equivalent parameter sets give distinct local predictions.

## Evidence and boundary

LKM node `gcn_f3c1234ae1284fbd` motivated the local-perturbation constraint.
Primary source:
[Burgarth and Ajoy (2017)](https://arxiv.org/abs/1705.07725).
This deterministic case establishes structural identifiability, not a complete
noise-calibrated posterior.
