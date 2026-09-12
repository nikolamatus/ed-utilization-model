# Health-status block ablation (RTHLTH6 and MNHLTH6 removed)

Same analytic cohort, same 2022 any-ED outcome, same training portion
(n=3,831), same 5x5 RepeatedStratifiedKFold
(random_state=2021) as the existing repeated-CV,
age-ablation, and demographic-block experiments. AGEY3X and SEX, RACETHX,
REGIONY3, MARRY6X remain in Model C. Preprocessing is fit inside each fold.
The original 25% holdout is scored only after CV, as a locked check. It was
not used to choose a model. Existing experiment files were not overwritten.

Removed from Model C only: RTHLTH6, MNHLTH6.

Feature-family ablation and full-model block ablation address different questions: the former measures marginal contribution when adding a family to an ED-history baseline, whereas the latter measures how much performance changes when removing a block from the full model.

The 2.5th and 97.5th percentiles below are descriptive summaries of the 25
paired fold deltas. They are not confidence intervals. The 25 folds are not treated as 25 independent observations. No significance test and no
Nadeau-Bengio correction is applied here.

## Analytic-cohort missingness audit

Reporting only. Sentinel handling, imputation, and cohort construction are
unchanged. Missingness is not used as a predictor.

| variable | analytic N | valid count | sentinel count | missing % after sentinel recode |
|---|---:|---:|---:|---:|
| RTHLTH6 | 5108 | 5105 | 3 | 0.06 |
| MNHLTH6 | 5108 | 5103 | 5 | 0.10 |

After sentinel recoding, missingness on these two variables is under 5% in the analytic cohort (max 0.10%). That is a descriptive characteristic of this sample, not a reason to change imputation or add missingness indicators.

## CV absolute metrics (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ed_roc_auc | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 | 0.6231 | 0.7306 |  |
| ed_pr_auc | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 | 0.2443 | 0.3616 |  |
| ed_brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 | 0.1034 | 0.1129 |  |
| full_roc_auc | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 | 0.6772 | 0.7566 |  |
| full_pr_auc | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 | 0.2872 | 0.4036 |  |
| full_brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 | 0.1010 | 0.1112 |  |
| nohealth_roc_auc | 0.7192 | 0.0259 | 0.7258 | 0.6742 | 0.7731 | 0.6765 | 0.7571 |  |
| nohealth_pr_auc | 0.3469 | 0.0342 | 0.3492 | 0.2851 | 0.4138 | 0.2898 | 0.4091 |  |
| nohealth_brier | 0.1056 | 0.0030 | 0.1056 | 0.1000 | 0.1110 | 0.1005 | 0.1108 |  |

## Paired fold-level deltas (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delta_roc_full_minus_ed | 0.0295 | 0.0225 | 0.0240 | -0.0105 | 0.0778 | -0.0044 | 0.0718 | 23/25 |
| delta_pr_full_minus_ed | 0.0359 | 0.0197 | 0.0399 | -0.0002 | 0.0684 | 0.0016 | 0.0638 | 24/25 |
| delta_brier_full_minus_ed | -0.0017 | 0.0019 | -0.0016 | -0.0047 | 0.0014 | -0.0047 | 0.0013 | 19/25 |
| delta_roc_nohealth_minus_ed | 0.0344 | 0.0208 | 0.0313 | -0.0047 | 0.0731 | 0.0004 | 0.0681 | 24/25 |
| delta_pr_nohealth_minus_ed | 0.0401 | 0.0162 | 0.0425 | 0.0072 | 0.0705 | 0.0096 | 0.0662 | 25/25 |
| delta_brier_nohealth_minus_ed | -0.0020 | 0.0017 | -0.0023 | -0.0054 | 0.0016 | -0.0051 | 0.0011 | 23/25 |
| delta_roc_nohealth_minus_full | 0.0049 | 0.0101 | 0.0042 | -0.0064 | 0.0412 | -0.0063 | 0.0300 | 17/25 |
| delta_pr_nohealth_minus_full | 0.0042 | 0.0093 | 0.0036 | -0.0123 | 0.0245 | -0.0102 | 0.0211 | 16/25 |
| delta_brier_nohealth_minus_full | -0.0004 | 0.0009 | -0.0002 | -0.0022 | 0.0013 | -0.0020 | 0.0011 | 16/25 |

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## 1. How much incremental value disappears without health status?
CV mean Δ ROC-AUC vs ED-history: full +0.030; no-health +0.034.
Removing RTHLTH6 and MNHLTH6 did not reduce the mean ROC increment (full +0.030; no-health +0.034). The paired no-health−full mean ROC is +0.005. That is a small descriptive difference and is not a reason to select the reduced model.
CV mean Δ PR-AUC vs ED-history: full +0.036; no-health +0.040
(112% of the PR increment remains without the health-status block).

## 2. Does the no-health model still outperform ED history across repeated CV?
ROC-AUC increment vs ED-history is positive in 24/25 folds
(full model: 23/25).
PR-AUC increment is positive in 25/25 folds
(full model: 24/25).
These counts describe paired folds. They are not a significance test.

## 3. What happens to PR-AUC?
PR-AUC increment vs ED-history mean +0.040
(full +0.036); positive in 25/25 folds.
Mean no-health−full PR +0.004.

## 4. What happens to Brier score?
Mean Brier vs ED-history: full -0.0017; no-health -0.0020.
Brier improved vs ED-history in 23/25 folds (full model: 19/25).
Mean no-health−full Brier -0.0004.

## 5–6. Comparison with age and demographic-block ablation
Feature-family ablation and full-model block ablation address different questions: the former measures marginal contribution when adding a family to an ED-history baseline, whereas the latter measures how much performance changes when removing a block from the full model.

Age, demographic-block, and this health-status experiment are the same
kind of question: each removes a block from the current full model.

- Age ablation (AGEY3X removed): remaining increment vs ED-history about
  +0.024 ROC / +0.034 PR.
- Demographic-block ablation (SEX, RACETHX, REGIONY3, MARRY6X removed;
  AGEY3X kept): remaining increment vs ED-history about
  +0.036 ROC / +0.036 PR.
- Health-status ablation (RTHLTH6, MNHLTH6 removed): remaining increment
  vs ED-history +0.034 ROC / +0.040 PR.

These three remaining-increment figures can be compared with each other
because they use the same full-model leave-block-out design. They should
not be compared numerically with the earlier feature-family "add to
ED-history" deltas.

## 7. Does removing health status eliminate most incremental signal?
Removing health status does not eliminate the incremental signal. Substantial increment vs ED-history remains. Residual signal may arise from the remaining predictor groups (age, other demographics, access, socioeconomic status). This experiment does not isolate which of those groups is responsible.

## 8. Locked holdout (not used for selection)
- ED-history: ROC-AUC 0.709, PR-AUC 0.331, Brier 0.105
- Full model: ROC-AUC 0.774, PR-AUC 0.416, Brier 0.099
- Full without health: ROC-AUC 0.765, PR-AUC 0.410, Brier 0.100
- Holdout Δ full−ED: ROC +0.065, PR +0.085
- Holdout Δ no-health−ED: ROC +0.056, PR +0.079
- Holdout Δ no-health−full: ROC -0.009, PR -0.006

Treat the holdout only as a locked confirmation, not as evidence used to pick a model.

## 9. Missingness as a limitation
After sentinel recoding, missingness on these two variables is under 5% in the analytic cohort (max 0.10%). That is a descriptive characteristic of this sample, not a reason to change imputation or add missingness indicators.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
