# Results and interpretation

## 1. Data audit

The uploaded merged file contains 26,313 simulations, not ~10,000. All runs are recorded as successful and the selected inputs plus `result_efficiencyOWC` are complete.

There are 125 duplicated points in the eight-factor design space. They have identical target values and are removed before model splitting so that identical design points cannot occur on both sides of the train/test boundary.

The target distribution contains one isolated value of 5.1498. Because it lies far above the rest of the efficiency distribution and beyond the Tukey upper fence (~1.238), it is excluded from the primary analysis. Values only slightly above 1 are retained and disclosed rather than clipped, because their interpretation depends on the exact numerical definition of `result_efficiencyOWC`.

## 2. Surrogate accuracy

XGBoost clearly outperforms both a linear model and ExtraTrees on the independent test set:

| Model | Test R² | Test RMSE | Test MAE |
|---|---:|---:|---:|
| Linear | 0.433 | 0.178 | 0.142 |
| ExtraTrees | 0.966 | 0.0436 | 0.0275 |
| XGBoost | **0.9839** | **0.0299** | **0.0184** |

Five-fold XGBoost validation gives R² = 0.9853 ± 0.0008, supporting the use of the surrogate for post-hoc interpretation within the sampled design domain.

## 3. SHAP ranking

Mean absolute SHAP values are approximately:

| Rank | Variable | Mean |SHAP| |
|---:|---|---:|
| 1 | wave period, T | 0.1067 |
| 2 | draft, d | 0.0713 |
| 3 | artificial damping, Ca | 0.0634 |
| 4 | chamber width, b | 0.0517 |
| 5 | opening ratio, a | 0.0351 |
| 6 | wave amplitude, A | 0.0150 |
| 7 | front-wall thickness, tw | 0.0110 |
| 8 | quadratic damping, Cq | 0.0110 |

This confirms that the requested `T–d–b–a` system contains four of the five most influential variables.

The SHAP beeswarm also shows why single-factor conclusions would be misleading: high draft values are often associated with negative global SHAP contributions, yet the ALE analysis below shows that this effect reverses with wave period. Therefore, “larger draft is worse” is not a defensible general conclusion.

## 4. Second-order ALE: period–geometry coupling

Among all 28 pairwise interactions, the strongest are:

1. `T × d`: RMS second-order ALE ≈ **0.093**
2. `T × b`: ≈ **0.074**
3. `b × a`: ≈ 0.033
4. `A × a`: ≈ 0.030
5. `a × Ca`: ≈ 0.023

`T × a` is weaker, ≈ **0.020**.

### T × d

At high draft (`d ≈ 0.56`), the interaction changes sign across the period range. Around `T ≈ 1.42`, the centred interaction is strongly negative (~−0.26), while around `T ≈ 2.41` it becomes strongly positive (~+0.18). This is a pronounced crossover interaction: larger draft is unfavourable at short periods but becomes increasingly compatible with long-period operation.

### T × b

Small chamber width (`b ≈ 0.24`) shows positive interaction at short period (`T ≈ 1.05`, ~+0.18) but strongly negative interaction at longer period (`T ≈ 2.24`, ~−0.22). Thus, the favourable chamber width shifts upward as period increases.

### T × a

The `T × a` interaction is materially weaker. A very small opening ratio can be favourable at short period, whereas very large opening ratios at the longest periods become mildly unfavourable. This supports treating `a` as a secondary tuning parameter after the main `T–d–b` geometry matching.

## 5. High-efficiency period–geometry envelope

Within each wave-period decile, the median geometry of the top 10% efficiency cases changes systematically:

- At `T ≈ 1.11–1.63`, high-performing cases cluster near `d ≈ 0.14`, `b ≈ 0.55` and `a ≈ 0.0066–0.0072`.
- At `T ≈ 1.77`, the high-efficiency median shifts to approximately `d ≈ 0.22`, `b ≈ 0.70`, `a ≈ 0.0106`.
- At `T ≈ 1.90–2.06`, it moves to `d ≈ 0.33–0.37`, `b ≈ 0.70–0.78`, `a ≈ 0.0130–0.0136`.
- At `T ≈ 2.24–2.40`, it reaches approximately `d ≈ 0.44–0.46`, `b ≈ 0.81–0.86`, while `a` settles around `0.0124–0.0125` rather than continuing to increase.

The 90th-percentile efficiency rises from ~0.64 at the shortest-period bin to ~0.94 around `T ≈ 2.06–2.24`, then decreases toward ~0.92 at the longest-period bin. This is consistent with a finite high-performance band, but it should be described as a **data-supported optimum region**, not labelled a resonance mechanism until confirmed against hydrodynamic quantities such as free-surface phase, pressure, radiation/damping balance or eigenfrequency.

## 6. What can be stated in a paper

A defensible result statement is:

> OWC efficiency is governed by strong period-dependent geometry matching rather than separable one-factor effects. Wave period is the most influential predictor, while period–draft and period–chamber-width interactions are the dominant pairwise couplings. High-efficiency designs require progressively larger draft and chamber width as the incident period increases, whereas the opening ratio exhibits a weaker, saturating adjustment.

Avoid causal wording such as “wave period causes draft to increase efficiency” unless the trends are subsequently verified with targeted controlled simulations.

## 7. Recommended hydrodynamic verification

For the final paper, select representative short-, intermediate- and long-period conditions from the ALE crossover regions and run a small controlled simulation matrix around the inferred ridge. Compare pressure amplitude/phase, chamber free-surface response, pneumatic power and incident-wave power. This converts the ML explanation from a statistical design rule into a mechanism-supported energy-conversion result.
