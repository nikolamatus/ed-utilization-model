# Access-block ablation (INSCOVY3 and HAVEUS6 removed)

Pre-registered Family B contrast B4 (2026-09-12 plan).
Same analytic cohort, same 2022 any-ED outcome, same training portion
(n=3,831), same 5x5 RepeatedStratifiedKFold
(random_state=2021) as the locked repeated-CV
and B1–B3 block ablations. Preprocessing is fit inside each fold.
The original 25% holdout is scored only after CV, as a locked check.
It was not used to choose a model. Existing experiment files were not
overwritten.

Removed from Model C only: INSCOVY3, HAVEUS6.
Retained: AGEY3X, SEX, RACETHX, REGIONY3, MARRY6X, RTHLTH6, MNHLTH6, POVCATY3, TTLPY3X, EMPST6, ERTOTY1, ERTOTY2, ERTOTY3.

Feature-family ablation and full-model block ablation address different questions: the former measures marginal contribution when adding a family to an ED-history baseline, whereas the latter measures how much performance changes when removing a block from the full model.

The vs-ED-history contrasts below are descriptive continuity only. They
are not additional Family B hypotheses. Family B is the five
leave-one-block-out contrasts versus the full model.

The 2.5th and 97.5th percentiles below are descriptive summaries of the 25
paired fold deltas. They are not confidence intervals. The 25 folds are not treated as 25 independent observations. No p-value, no Nadeau-Bengio
correction, and no Holm-Bonferroni adjustment is computed in this file.

## CV absolute metrics (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ed_roc_auc | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 | 0.6231 | 0.7306 |  |
| ed_pr_auc | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 | 0.2443 | 0.3616 |  |
| ed_brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 | 0.1034 | 0.1129 |  |
| full_roc_auc | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 | 0.6772 | 0.7566 |  |
| full_pr_auc | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 | 0.2872 | 0.4036 |  |
| full_brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 | 0.1010 | 0.1112 |  |
| noaccess_roc_auc | 0.7125 | 0.0252 | 0.7199 | 0.6742 | 0.7646 | 0.6750 | 0.7554 |  |
| noaccess_pr_auc | 0.3410 | 0.0355 | 0.3450 | 0.2806 | 0.4047 | 0.2848 | 0.4018 |  |
| noaccess_brier | 0.1062 | 0.0031 | 0.1057 | 0.1005 | 0.1121 | 0.1013 | 0.1115 |  |

## Paired fold-level deltas (25 folds)

| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delta_roc_full_minus_ed | 0.0295 | 0.0225 | 0.0240 | -0.0105 | 0.0778 | -0.0044 | 0.0718 | 23/25 |
| delta_pr_full_minus_ed | 0.0359 | 0.0197 | 0.0399 | -0.0002 | 0.0684 | 0.0016 | 0.0638 | 24/25 |
| delta_brier_full_minus_ed | -0.0017 | 0.0019 | -0.0016 | -0.0047 | 0.0014 | -0.0047 | 0.0013 | 19/25 |
| delta_roc_noaccess_minus_ed | 0.0278 | 0.0239 | 0.0249 | -0.0162 | 0.0778 | -0.0079 | 0.0739 | 23/25 |
| delta_pr_noaccess_minus_ed | 0.0343 | 0.0222 | 0.0382 | -0.0072 | 0.0683 | -0.0015 | 0.0675 | 24/25 |
| delta_brier_noaccess_minus_ed | -0.0015 | 0.0020 | -0.0012 | -0.0045 | 0.0017 | -0.0045 | 0.0013 | 18/25 |
| delta_roc_noaccess_minus_full | -0.0018 | 0.0039 | -0.0016 | -0.0085 | 0.0077 | -0.0082 | 0.0051 | 8/25 |
| delta_pr_noaccess_minus_full | -0.0017 | 0.0042 | -0.0025 | -0.0096 | 0.0106 | -0.0080 | 0.0074 | 7/25 |
| delta_brier_noaccess_minus_full | 0.0002 | 0.0003 | 0.0003 | -0.0005 | 0.0006 | -0.0004 | 0.0006 | 5/25 |

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## Incremental value vs ED-history after removing the block
CV mean Δ ROC-AUC vs ED-history: full +0.030; no-access +0.028.
About 6% of the mean ROC increment vs ED-history is associated with including INSCOVY3, HAVEUS6 (94% remains without them).
CV mean Δ PR-AUC vs ED-history: full +0.036; no-access +0.034
(95% of the PR increment remains without the block).
ROC increment vs ED-history is positive in 23/25 folds
(full: 23/25).
PR increment vs ED-history is positive in 24/25 folds
(full: 24/25).
These counts describe paired folds. They are not a significance test.

## Brier
Mean Brier vs ED-history: full -0.0017; no-access -0.0015.
Brier improved vs ED-history in 18/25 folds
(full: 19/25).
Mean no-access−full Brier +0.0002.

## Family B contrast vs the full model (descriptive)
Mean no-access−full: ROC -0.002,
PR -0.002.
Positive ROC delta vs full in 8/25 folds;
positive PR delta vs full in 7/25 folds.
No p-value is reported here.

## Comparison with prior full-model block ablations
Feature-family ablation and full-model block ablation address different questions: the former measures marginal contribution when adding a family to an ED-history baseline, whereas the latter measures how much performance changes when removing a block from the full model.

Remaining increment vs ED-history from earlier leave-block-out experiments:
- B1 age (AGEY3X): +0.024 ROC / +0.034 PR.
- B2 demographics (SEX, RACETHX, REGIONY3, MARRY6X): +0.036 ROC / +0.036 PR.
- B3 health (RTHLTH6, MNHLTH6): +0.034 ROC / +0.040 PR.
- B4 access (INSCOVY3, HAVEUS6): +0.028 ROC / +0.034 PR.

## Locked holdout (not used for selection)
- ED-history: ROC-AUC 0.709, PR-AUC 0.331, Brier 0.105
- Full model: ROC-AUC 0.774, PR-AUC 0.416, Brier 0.099
- full_without_access: ROC-AUC 0.770, PR-AUC 0.414, Brier 0.100
- Holdout Δ full−ED: ROC +0.065, PR +0.085
- Holdout Δ no-access−ED: ROC +0.061, PR +0.083
- Holdout Δ no-access−full: ROC -0.004, PR -0.002

Treat the holdout only as a locked confirmation, not as evidence used to pick a model.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
