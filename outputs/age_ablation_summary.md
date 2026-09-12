# Age ablation (AGEY3X removed)

Same analytic cohort, same training portion (n=3,831), same 5x5
RepeatedStratifiedKFold (random_state=2021) as the
existing repeated-CV experiment. Preprocessing is fit inside each fold.
The original 25% holdout is scored only after CV, as a locked check. It
was not used to choose a model. Existing holdout and CV files were not
overwritten.

## CV absolute metrics (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ed_roc_auc | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 | 0.6231 | 0.7306 |  |
| ed_pr_auc | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 | 0.2443 | 0.3616 |  |
| ed_brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 | 0.1034 | 0.1129 |  |
| full_roc_auc | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 | 0.6772 | 0.7566 |  |
| full_pr_auc | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 | 0.2872 | 0.4036 |  |
| full_brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 | 0.1010 | 0.1112 |  |
| noage_roc_auc | 0.7092 | 0.0270 | 0.7189 | 0.6658 | 0.7565 | 0.6689 | 0.7484 |  |
| noage_pr_auc | 0.3409 | 0.0317 | 0.3444 | 0.2925 | 0.3920 | 0.2937 | 0.3890 |  |
| noage_brier | 0.1062 | 0.0029 | 0.1058 | 0.1009 | 0.1108 | 0.1018 | 0.1108 |  |

## Paired fold-level deltas (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delta_roc_full_minus_ed | 0.0295 | 0.0225 | 0.0240 | -0.0105 | 0.0778 | -0.0044 | 0.0718 | 23/25 |
| delta_pr_full_minus_ed | 0.0359 | 0.0197 | 0.0399 | -0.0002 | 0.0684 | 0.0016 | 0.0638 | 24/25 |
| delta_brier_full_minus_ed | -0.0017 | 0.0019 | -0.0016 | -0.0047 | 0.0014 | -0.0047 | 0.0013 | 19/25 |
| delta_roc_noage_minus_ed | 0.0244 | 0.0212 | 0.0212 | -0.0226 | 0.0663 | -0.0100 | 0.0627 | 23/25 |
| delta_pr_noage_minus_ed | 0.0342 | 0.0175 | 0.0408 | -0.0002 | 0.0612 | 0.0026 | 0.0573 | 24/25 |
| delta_brier_noage_minus_ed | -0.0015 | 0.0016 | -0.0019 | -0.0039 | 0.0014 | -0.0039 | 0.0013 | 19/25 |
| delta_roc_noage_minus_full | -0.0051 | 0.0071 | -0.0056 | -0.0176 | 0.0139 | -0.0152 | 0.0090 | 5/25 |
| delta_pr_noage_minus_full | -0.0017 | 0.0085 | -0.0025 | -0.0158 | 0.0147 | -0.0142 | 0.0147 | 11/25 |
| delta_brier_noage_minus_full | 0.0002 | 0.0007 | 0.0003 | -0.0009 | 0.0011 | -0.0009 | 0.0011 | 10/25 |

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## 1. How much incremental value disappears without age?
CV mean Δ ROC-AUC vs ED-history: full +0.030; no-age +0.024.
About 17% of the mean ROC increment is associated with including AGEY3X
(83% remains without age).
CV mean Δ PR-AUC vs ED-history: full +0.036; no-age +0.034
(95% of the PR increment remains without age).

## 2. Does the no-age model still outperform ED history consistently?
ROC-AUC increment vs ED-history is positive in 23/25 folds
(full model: 23/25).

## 3. Does the no-age model retain meaningful PR-AUC improvement?
PR-AUC increment vs ED-history is positive in 24/25 folds;
mean +0.034.

## 4. Is age the dominant driver, or does substantial signal remain?
Age is important but not the entire story: at least half of the mean ROC increment remains without AGEY3X.

## 5. Comparison with the original full-model CV result
Original repeated-CV mean increment was about +0.030 ROC / +0.036 PR.
This experiment's full-vs-ED means should match that paired design
(full +0.030 ROC / +0.036 PR).
No-age vs ED is +0.024 ROC / +0.034 PR.

## 6. Locked holdout (not used for selection)
- ED-history: ROC-AUC 0.709, PR-AUC 0.331, Brier 0.105
- Full model: ROC-AUC 0.774, PR-AUC 0.416, Brier 0.099
- Full without age: ROC-AUC 0.771, PR-AUC 0.404, Brier 0.100
- Holdout Δ full−ED: ROC +0.065, PR +0.085
- Holdout Δ no-age−ED: ROC +0.062, PR +0.074

Treat the holdout only as a locked confirmation, not as evidence used to pick a model.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
