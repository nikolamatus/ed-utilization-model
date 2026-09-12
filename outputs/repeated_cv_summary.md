# Repeated stratified CV (training portion only)

This experiment does **not** replace the first-run 25% holdout.
The holdout (n_test=1,277) remains the final untouched benchmark.
CV uses only the original training portion (n=3,831), reconstructed with
holdout seed=42. RepeatedStratifiedKFold: 5 repeats
x 5 folds, random_state=2021. Stratified on the
2022 any-ED outcome. Preprocessing is fit inside each CV training fold.

These percentiles are an **empirical repeated-CV distribution**, not
formal external-validation confidence intervals.

## Untouched holdout benchmark (not refit)
- ED-history ROC-AUC 0.709, PR-AUC 0.331, Brier 0.105
- Full model ROC-AUC 0.774, PR-AUC 0.416, Brier 0.099
- Incremental ROC-AUC +0.065, PR-AUC +0.085

## Repeated-CV means (25 folds)
- ED-history ROC-AUC 0.685 (SD 0.033)
- Full model ROC-AUC 0.714 (SD 0.026)
- ED-history PR-AUC 0.307 (SD 0.036)
- Full model PR-AUC 0.343 (SD 0.035)
- Mean incremental ROC-AUC +0.030 (SD 0.023; min -0.010; max +0.078; 2.5th -0.004; 97.5th +0.072)
- Mean incremental PR-AUC +0.036 (SD 0.020; min -0.000; max +0.068; 2.5th +0.002; 97.5th +0.064)
- Mean incremental Brier -0.0017 (negative means the full model is better)

## Answers
1. Is the full model consistently better than ED history during repeated CV?
   ROC-AUC increment was positive in 23/25 folds; PR-AUC in 24/25 folds.

2. Incremental ROC-AUC positive in most/all folds?
   23/25 folds positive.

3. Incremental PR-AUC positive in most/all folds?
   24/25 folds positive.

4. Does Brier generally improve?
   Brier was lower (better) for the full model in 19/25 folds. Mean Brier delta -0.0017.

5. Does CV strengthen or weaken the original holdout finding?
   The CV evidence supports a positive increment but suggests the single holdout lift is on the high side.

6. Signs the holdout +0.065 / +0.085 may be unusually optimistic?
   The untouched holdout lifts sit at or above the upper tail of this repeated-CV distribution and may be somewhat optimistic relative to typical training-fold increments.

Unweighted analytic-sample CV only. Not a national estimate, clinical
validation, causal finding, or deployment result.
