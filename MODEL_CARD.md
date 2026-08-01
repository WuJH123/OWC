# OWC XGBoost efficiency surrogate

This repository stores a callable trained XGBoost surrogate for OWC conversion efficiency and separately records the validation of the full research model used for the published `Topt` table.

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

Full research model used for the 1,500-condition optimal-period table:

- Clean training/evaluation pool: 26,187 rows
- Independent-test R²: **0.983908**
- RMSE: **0.029945**
- MAE: **0.018448**

Portable GitHub deployment model:

- 50 loss-guided XGBoost trees, maximum 64 leaves per tree
- Independent-test R²: **0.967798**
- RMSE: **0.042360**
- MAE: **0.029520**

The compact deployment model is deliberately smaller so the trained artifact can be distributed directly with this repository without Git LFS. It uses the same cleaned data and exactly the same eight-factor input contract, but it does **not** replace the full research model as the source of the committed `Topt` evidence table.

## Model persistence

The underlying trained booster is serialized in XGBoost JSON format. For repository portability the JSON bytes are gzip-compressed and base64-split into package-data chunks; `owc_surrogate` reconstructs and loads the booster automatically on first use.

## Scientific-use warning

The callable API validates that inputs remain inside the observed training-domain bounds by default. Predictions inside those rectangular bounds can still be weakly supported when a particular multivariate combination was rare. Hydrodynamic validation is required before interpreting a statistical optimum as a general physical law.
