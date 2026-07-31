# OWC efficiency interpretability analysis

Reproducible analysis of OWC conversion efficiency using eight physical/control factors and `result_efficiencyOWC` as the response.

## Variables used

Response:

- `result_efficiencyOWC`

Predictors:

- `wave_period` (`T`)
- `wave_amplitude` (`A`)
- `draft` (`d`)
- `front_wall_thickness` (`t_w`)
- `chamber_width` (`b`)
- `opening_ratio` (`a`)
- `quadratic_damping` (`C_q`)
- `artificial_damping` (`C_a`)

**Column-letter check for the uploaded merged CSV:** `wave_period` is M, `wave_amplitude` is N, `draft` is Q, `front_wall_thickness` is R, `chamber_width` is S and `opening_ratio` is T. Analyses therefore use column names rather than spreadsheet letters to prevent the draft/wave-amplitude mismatch.

## Workflow

1. Data-quality audit and exact-input deduplication.
2. Extreme-response audit using a Tukey IQR fence; only the isolated efficiency value of 5.1498 is excluded from the primary model.
3. Surrogate benchmarking (linear regression, ExtraTrees and XGBoost).
4. Independent validation plus five-fold cross-validation.
5. Global SHAP ranking and SHAP dependence visualization.
6. Centred second-order accumulated local effects (ALE) for all predictor pairs.
7. Detailed period–geometry analysis for `T × d`, `T × b` and `T × a`.
8. High-efficiency design envelope: median and interquartile range of `d`, `b` and `a` among the top 10% efficiency cases within each wave-period decile.

## Main quantitative findings

- Raw dataset: 26,313 rows × 41 columns; all runs are marked `ok`, all result parses are valid, and the nine selected columns contain no missing values.
- 125 repeated rows in the specified eight-dimensional input space are removed before splitting to prevent train/test leakage.
- One isolated efficiency value (5.1498) lies beyond the Tukey upper fence (~1.238) and is excluded; modest values slightly above 1 are retained and explicitly reported rather than silently clipped.
- XGBoost independent test performance: **R² = 0.9839, RMSE = 0.0299, MAE = 0.0184**.
- Five-fold cross-validation: **R² = 0.9853 ± 0.0008**.
- Mean absolute SHAP ranking: `wave_period` > `draft` > `artificial_damping` > `chamber_width` > `opening_ratio` > `wave_amplitude` > `front_wall_thickness` ≈ `quadratic_damping`.
- The two strongest second-order ALE interactions are **`wave_period × draft` (RMS ≈ 0.093)** and **`wave_period × chamber_width` (RMS ≈ 0.074)**. `wave_period × opening_ratio` is weaker (RMS ≈ 0.020), indicating a secondary tuning role.
- High-efficiency configurations shift from approximately `d ≈ 0.14`, `b ≈ 0.55`, `a ≈ 0.0066` at short periods to larger `d` and `b` at long periods. Around `T ≈ 2.0–2.4`, top-decile cases have approximately `d ≈ 0.37–0.46`, `b ≈ 0.78–0.86`, and `a ≈ 0.012–0.013`.

See [`RESULTS.md`](RESULTS.md) for detailed interpretation and cautions.

## Run

```bash
python analysis/owc_efficiency_interpretability.py \
  --csv training_dataset_merged_deduplicated.csv \
  --out results
```

The script exports CSV summaries, an XGBoost model and publication-ready SVG/PDF/450-dpi PNG figures.

## Figure design

Figures are laid out at ~183 mm double-column width, use editable sans-serif text and 5–8 pt typography, and export vector formats plus 450-dpi PNG. These choices follow the Nature research figure guide recommendations for figure width, font sizing, editability and image resolution.

## Method references

- Chen, T. & Guestrin, C. *XGBoost: A Scalable Tree Boosting System*. KDD (2016). DOI: 10.1145/2939672.2939785.
- Lundberg, S. M. & Lee, S.-I. *A Unified Approach to Interpreting Model Predictions*. NeurIPS 30 (2017).
- Apley, D. W. & Zhu, J. *Visualizing the Effects of Predictor Variables in Black Box Supervised Learning Models*. J. R. Stat. Soc. B 82, 1059–1086 (2020). DOI: 10.1111/rssb.12377.

## Reproducibility note

Second-order ALE maps are interaction effects centred around zero. A positive ALE region means the pair acts more favourably than expected from the two additive main effects; it is **not** the absolute efficiency. The high-efficiency envelope figure is provided alongside ALE to show the practical parameter combinations associated with the best simulated cases.
