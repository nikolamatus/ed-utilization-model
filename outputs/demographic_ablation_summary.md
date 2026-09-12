# Demographic-block ablation (SEX, RACETHX, REGIONY3, MARRY6X removed)

Same analytic cohort, same training portion (n=3,831), same 5x5
RepeatedStratifiedKFold (random_state=2021) as the
existing repeated-CV and age-ablation experiments. AGEY3X is retained.
Preprocessing is fit inside each fold. The original 25% holdout is scored
only after CV, as a locked check. It was not used to choose a model.
Existing holdout, repeated-CV, family-ablation, and age-ablation files
were not overwritten.

Removed from Model C only: SEX, RACETHX, REGIONY3, MARRY6X.

## CV absolute metrics (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ed_roc_auc | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 | 0.6231 | 0.7306 |  |
| ed_pr_auc | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 | 0.2443 | 0.3616 |  |
| ed_brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 | 0.1034 | 0.1129 |  |
| full_roc_auc | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 | 0.6772 | 0.7566 |  |
| full_pr_auc | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 | 0.2872 | 0.4036 |  |
| full_brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 | 0.1010 | 0.1112 |  |
| nodemo_roc_auc | 0.7205 | 0.0258 | 0.7265 | 0.6815 | 0.7666 | 0.6821 | 0.7608 |  |
| nodemo_pr_auc | 0.3424 | 0.0375 | 0.3497 | 0.2810 | 0.4081 | 0.2838 | 0.4069 |  |
| nodemo_brier | 0.1060 | 0.0032 | 0.1053 | 0.1006 | 0.1119 | 0.1008 | 0.1114 |  |

## Paired fold-level deltas (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delta_roc_full_minus_ed | 0.0295 | 0.0225 | 0.0240 | -0.0105 | 0.0778 | -0.0044 | 0.0718 | 23/25 |
| delta_pr_full_minus_ed | 0.0359 | 0.0197 | 0.0399 | -0.0002 | 0.0684 | 0.0016 | 0.0638 | 24/25 |
| delta_brier_full_minus_ed | -0.0017 | 0.0019 | -0.0016 | -0.0047 | 0.0014 | -0.0047 | 0.0013 | 19/25 |
| delta_roc_nodemo_minus_ed | 0.0358 | 0.0234 | 0.0263 | -0.0021 | 0.0867 | -0.0019 | 0.0748 | 23/25 |
| delta_pr_nodemo_minus_ed | 0.0357 | 0.0207 | 0.0387 | -0.0074 | 0.0714 | -0.0048 | 0.0695 | 22/25 |
| delta_brier_nodemo_minus_ed | -0.0017 | 0.0018 | -0.0016 | -0.0055 | 0.0020 | -0.0051 | 0.0012 | 21/25 |
| delta_roc_nodemo_minus_full | 0.0062 | 0.0083 | 0.0046 | -0.0027 | 0.0297 | -0.0026 | 0.0236 | 17/25 |
| delta_pr_nodemo_minus_full | -0.0002 | 0.0093 | -0.0015 | -0.0141 | 0.0277 | -0.0126 | 0.0185 | 10/25 |
| delta_brier_nodemo_minus_full | 0.0000 | 0.0008 | 0.0001 | -0.0023 | 0.0012 | -0.0016 | 0.0010 | 12/25 |

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## 1. How much incremental value disappears without the demographic block?
CV mean Δ ROC-AUC vs ED-history: full +0.030; no-demographics +0.036.
Removing the block did not reduce the mean ROC increment (full +0.030; no-demographics +0.036). The mean increment is slightly larger without these four variables. That is a small paired difference (mean no-demo−full ROC +0.006) and should not be read as evidence that the variables are harmful or that a reduced model should be selected.
CV mean Δ PR-AUC vs ED-history: full +0.036; no-demographics +0.036
(99% of the PR increment remains without the block).

## 2. Does the no-demographics model still outperform ED history consistently?
ROC-AUC increment vs ED-history is positive in 23/25 folds
(full model: 23/25).
PR-AUC increment is positive in 22/25 folds
(full model: 24/25).
Brier improved vs ED-history in 21/25 folds.

## 3. How much PR-AUC improvement remains?
PR-AUC increment vs ED-history mean +0.036
(full +0.036); positive in 22/25 folds.

## 4. Comparison with the previous age-ablation result
Age ablation (AGEY3X removed, these four variables kept) left about
+0.024 ROC / +0.034 PR
vs ED-history (roughly 83% of the ROC increment and 95% of the PR increment).
This demographic-block ablation (AGEY3X kept; SEX, RACETHX, REGIONY3, MARRY6X
removed) leaves +0.036 ROC / +0.036 PR
vs ED-history. Removing these four variables did not shrink the increment, whereas removing AGEY3X alone reduced it modestly. The non-age demographic block is not a larger driver than age in this leave-one-block-out design.

## 5. Distributed vs concentrated in demographic variables?
The mean ROC increment does not shrink when SEX, RACETHX, REGIONY3, and MARRY6X are removed from the full model. Together with the age-ablation result (AGEY3X accounted for only a modest slice), this does not support concentration of incremental signal in the non-age demographic block. Residual increment remains attributable to age, health, access, and/or SES in this design.

## 6. Locked holdout (not used for selection)
- ED-history: ROC-AUC 0.709, PR-AUC 0.331, Brier 0.105
- Full model: ROC-AUC 0.774, PR-AUC 0.416, Brier 0.099
- Full without demographics: ROC-AUC 0.771, PR-AUC 0.410, Brier 0.100
- Holdout Δ full−ED: ROC +0.065, PR +0.085
- Holdout Δ no-demographics−ED: ROC +0.061, PR +0.079

Treat the holdout only as a locked confirmation, not as evidence used to pick a model.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
