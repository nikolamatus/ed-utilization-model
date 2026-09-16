# Table 2. Primary comparison: full longitudinal-information model minus 3-year ED-history baseline

Training-only repeated 5×5 stratified cross-validation (25 paired fold
differences). Inference: Nadeau–Bengio corrected resampled *t*-test,
df = 24, two-sided α = 0.05. Family A *p*-values are **unadjusted**.
Increments are Full − Baseline. **Lower Brier is better**, so a negative
ΔBrier favors the full model.

Sources: `outputs/repeated_cv_summary.csv` (means);
`outputs/statistical_inference.csv` and
`outputs/statistical_inference_intervals_v1_1.csv` (SE, CI, *p*).

| Metric | Baseline mean | Full mean | Increment (Full − Baseline) | 95% Nadeau–Bengio CI | Unadjusted *p* |
|---|---:|---:|---:|---|---:|
| ROC-AUC | 0.6848 | 0.7143 | +0.0295 | +0.0045 to +0.0546 | 0.0226 |
| PR-AUC | 0.3067 | 0.3426 | +0.0359 | +0.0140 to +0.0578 | 0.0024 |
| Brier score | 0.1077 | 0.1060 | −0.0017 | −0.0038 to +0.0004 | 0.1110 |

Family A multiplicity (disclosed, not applied): ROC *p* = 0.0226 would not
survive a simple Bonferroni correction across the three metrics
(0.0226 × 3 = 0.0678); PR *p* = 0.0024 would (0.0024 × 3 = 0.0072).
That correction was not specified in the documented analysis plan and is
not used to alter the result.
