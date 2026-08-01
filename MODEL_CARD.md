# OWC XGBoost efficiency surrogate

This repository stores the trained XGBoost model used for OWC efficiency analysis.

## Inputs

The model requires eight inputs, in this order:

1. `wave_period`
2. `wave_amplitude`
3. `draft`
4. `front_wall_thickness`
5. `chamber_width`
6. `opening_ratio`
7. `quadratic_damping`
8. `artificial_damping`

Output: `result_efficiencyOWC`.

## Validation

- Clean training/evaluation pool: 26,187 rows
- Full research model independent-test R²: 0.983908
- RMSE: 0.029945
- MAE: 0.018448

The GitHub deployment model is serialized with XGBoost JSON model IO. It uses 150 loss-guided trees (max 96 leaves) and retains independent-test R² ≈ 0.9801. The full 1600-tree research model used to generate the 1500-row Topt table achieved R² = 0.9839. The deployment model is intentionally compact enough for direct GitHub distribution.

## Scientific-use warning

The callable API validates that inputs remain inside the observed training-domain bounds by default. Predictions inside the rectangular bounds can still be weakly supported if a particular multivariate combination was rare; use hydrodynamic validation before interpreting an optimum as a physical law.
