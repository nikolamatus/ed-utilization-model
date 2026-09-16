# Table 4. Sensitivity and diagnostic analyses (not replacements for the primary mixed-age Family A result)

Unless noted, Δ = Full − ED-history on training-only 5×5 CV with
Nadeau–Bengio inference (df = 24). Adult age ablation is exploratory
(No-age − Full within adults).

| Analysis | Sample / change | Metric | Mean Δ | 95% CI | Unadjusted *p* | Primary replacement? |
|---|---|---|---:|---|---:|---|
| Mixed-age primary (Family A) | N = 5,108; train 3,831 | ROC-AUC | +0.0295 | +0.0045 to +0.0546 | 0.0226 | — |
| Adult-only | AGEY3X ≥ 18; train 3,162; holdout 1,048 / 166 events | ROC-AUC | +0.0194 | −0.0050 to +0.0438 | 0.1134 | No |
| Adult-only | same | PR-AUC | +0.0299 | +0.0113 to +0.0486 | 0.0029 | No |
| Adult-only | same | Brier | −0.0014 | −0.0035 to +0.0008 | 0.1958 | No |
| ALL9RDS == 1 | train 3,663; holdout 1,220 / 166 events | ROC-AUC | +0.0311 | +0.0061 to +0.0562 | 0.0168 | No |
| ALL9RDS == 1 | same | PR-AUC | +0.0381 | +0.0112 to +0.0649 | 0.0073 | No |
| ALL9RDS == 1 | same | Brier | −0.0018 | −0.0041 to +0.0005 | 0.1201 | No |
| Exclude ERTOTY2 | same persons as primary; weaker ED-history comparator | ROC-AUC | +0.0460 | +0.0220 to +0.0700 | 0.0006 | No |
| Exclude ERTOTY2 | same | PR-AUC | +0.0518 | +0.0296 to +0.0740 | <0.0001 | No |
| Exclude ERTOTY2 | same | Brier | −0.0021 | −0.0041 to +0.0000 | 0.0508 | No |
| Exploratory adult B1 | adults; AGEY3X removed vs adult full | ROC-AUC | −0.0022 | −0.0117 to +0.0073 | 0.6371 | No (post-primary) |

Sources: `outputs/statistical_inference_intervals_v1_1.csv`;
`outputs/sensitivity_adult_only_v1_1_inference.csv`;
`outputs/sensitivity_all9rds_v1_1_inference.csv`;
`outputs/sensitivity_covid2020_v1_1_inference.csv`;
`outputs/exploratory_adult_age_ablation_v1_1_inference.csv`.

## Diagnostic notes (same table family)

| Diagnostic | Result | Source | Used to change the model? |
|---|---|---|---|
| Corrected VIF (drop-first OHE, training n = 3,831) | 40 finite VIFs; maximum 3.68; none > 5 | `outputs/predictor_vif_drop_reference_v1_1.csv` | No |
| Holdout calibration (full model) | mean *p* = 0.134892; observed = 0.135474; CITL = 0.006; slope = 1.237 | `outputs/holdout_calibration_v1_1.csv` | No (assessment only; not recalibrated) |
| Death sensitivity | Dropping 9 holdout decedents: full ROC 0.774 → 0.772; refit drop 28+9: 0.771 | `outputs/death_sensitivity.csv` | No |
| EMPST6 non-usable | 818 / 5,108 (16.01%); 801 code −1, 9 −7, 2 −8, 6 −15; 96.5% of non-usable among age <16 | `outputs/missingness_analytic_cohort_v1_1.csv`, `outputs/empst6_code_breakdown_v1_1.csv` | No |
