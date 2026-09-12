# Pre-registered statistical inference (Nadeau–Bengio + Holm)

Date of analysis: 2026-09-12 (after B4 and B5 exist).
Source plan: `docs/pre_registration_block_ablation_plan.md` (locked 2026-09-12).
No models were refit. All numbers come from saved 5×5 fold-level CSVs.

## Method

Nadeau & Bengio (2003) corrected resampled t-test: Var_NB = (1/n + n_test/n_train) * s^2, where s^2 is the unbiased sample variance of the n paired fold-level differences, n = r*k = 25, k = 5 folds, r = 5 repeats, and n_test/n_train is the mean validation/training size ratio within each split. t = mean / sqrt(Var_NB) with df = n-1 = 24. Two-sided p-value from Student's t. This is not the naive SE = s/sqrt(25) that would treat folds as independent.

In this experiment:

- k = 5 stratified folds per repeat
- r = 5 repeats
- n = 25 paired fold-level differences (not 25 independent observations)
- df = 24
- mean n_test/n_train = 0.250000 (theoretical 5-fold ratio = 1/4 = 0.25)
- s^2 = unbiased variance of the 25 paired deltas
- alpha = 0.05, two-sided

Family A (A1 only) uses the Nadeau–Bengio p-value with no multiplicity
adjustment. Family B applies Holm–Bonferroni separately within each metric
across the five block contrasts. Holm is not applied to Family A and is
not applied across families or across metrics.

Holm procedure: order the five raw p-values p(1) ≤ … ≤ p(5); the j-th
ordered test uses threshold alpha/(5-j+1); adjusted p(i) =
max_{j≤i} min(1, (5-j+1) p(j)).

Sign convention (not reversed):

- Contrasts are first − second as named (A1: Full − ED-history; B1–B5: reduced − Full).
- ROC/PR: positive mean = first named model has higher discrimination.
- Brier: negative mean = first named model has lower (better) Brier.

The 2.5th–97.5th percentile ranges in earlier CV summaries remain
descriptive empirical ranges. They are not confidence intervals and are
not relabeled as such here.

Locked holdout numbers below are confirmation only. They were not used
to choose hypotheses, compute p-values, or select a model.

## Results

| family | contrast | metric | mean | corrected SE | t | raw p | Holm p | sig. 0.05 | direction |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| A | A1 Full − ED-history | roc_auc | +0.0295 | 0.0121 | +2.437 | 0.0226 | — | yes | Full better than ED-history |
| A | A1 Full − ED-history | pr_auc | +0.0359 | 0.0106 | +3.385 | 0.0024 | — | yes | Full better than ED-history |
| A | A1 Full − ED-history | brier | -0.0017 | 0.0010 | -1.655 | 0.1110 | — | no | Full better (lower Brier) than ED-history |
| B | B1 No-age − Full | roc_auc | -0.0051 | 0.0038 | -1.354 | 0.1884 | 0.8720 | no | Full better than reduced model |
| B | B1 No-age − Full | pr_auc | -0.0017 | 0.0046 | -0.377 | 0.7092 | 1.0000 | no | Full better than reduced model |
| B | B1 No-age − Full | brier | +0.0002 | 0.0004 | +0.460 | 0.6497 | 1.0000 | no | Full better (lower Brier) than reduced model |
| B | B2 No-demographics − Full | roc_auc | +0.0062 | 0.0044 | +1.400 | 0.1744 | 0.8720 | no | reduced model better than Full |
| B | B2 No-demographics − Full | pr_auc | -0.0002 | 0.0050 | -0.038 | 0.9703 | 1.0000 | no | Full better than reduced model |
| B | B2 No-demographics − Full | brier | +0.0000 | 0.0004 | +0.035 | 0.9722 | 1.0000 | no | Full better (lower Brier) than reduced model |
| B | B3 No-health − Full | roc_auc | +0.0049 | 0.0054 | +0.898 | 0.3783 | 1.0000 | no | reduced model better than Full |
| B | B3 No-health − Full | pr_auc | +0.0042 | 0.0050 | +0.849 | 0.4043 | 1.0000 | no | reduced model better than Full |
| B | B3 No-health − Full | brier | -0.0004 | 0.0005 | -0.798 | 0.4328 | 1.0000 | no | reduced model better (lower Brier) than Full |
| B | B4 No-access − Full | roc_auc | -0.0018 | 0.0021 | -0.852 | 0.4029 | 1.0000 | no | Full better than reduced model |
| B | B4 No-access − Full | pr_auc | -0.0017 | 0.0023 | -0.723 | 0.4767 | 1.0000 | no | Full better than reduced model |
| B | B4 No-access − Full | brier | +0.0002 | 0.0002 | +1.226 | 0.2321 | 0.9284 | no | Full better (lower Brier) than reduced model |
| B | B5 No-SES − Full | roc_auc | +0.0019 | 0.0029 | +0.646 | 0.5247 | 1.0000 | no | reduced model better than Full |
| B | B5 No-SES − Full | pr_auc | +0.0065 | 0.0043 | +1.525 | 0.1404 | 0.7019 | no | reduced model better than Full |
| B | B5 No-SES − Full | brier | -0.0006 | 0.0004 | -1.445 | 0.1614 | 0.8072 | no | reduced model better (lower Brier) than Full |

## Family A (primary)

A1 Full − ED-history, Nadeau–Bengio, no Holm:

- ROC-AUC: mean +0.0295, SE 0.0121, t +2.437, p 0.0226, significant at 0.05: yes. Full better than ED-history.
- PR-AUC: mean +0.0359, SE 0.0106, t +3.385, p 0.0024, significant at 0.05: yes. Full better than ED-history.
- Brier: mean -0.0017, SE 0.0010, t -1.655, p 0.1110, significant at 0.05: no. Full better (lower Brier) than ED-history.

Statistical significance is not clinical significance.

## Family B (secondary, Holm within metric)

- roc_auc: no Family-B contrast is significant after Holm.
- pr_auc: no Family-B contrast is significant after Holm.
- brier: no Family-B contrast is significant after Holm.

Removing a block did not produce statistically detectable evidence of a
performance change under this analysis unless the Holm-adjusted p-value
is ≤ 0.05. Non-significance is not evidence of equivalence and does not
mean the block is useless.

## Interpretation

Primary question — incremental value beyond 3-year ED history:
Family A asks whether the full model differs from ED-history on the
training-only 5×5 repeated CV. A statistically significant positive
ROC/PR (and/or negative Brier) difference supports incremental
predictive value on this MEPS Panel 24 analytic sample. That is not
clinical utility, causality, or national performance.

Secondary question — does removing any pre-specified block materially
change performance relative to the full model:
Family B tests reduced − Full. A Holm-significant negative ROC/PR
difference would mean the reduced model was detectably worse than Full.
A Holm-significant positive ROC/PR difference would mean the reduced
model was detectably better. Absence of Holm-significant differences
means this analysis did not detect a change; it does not prove the
removed block has no information and does not prove independence from
other predictors.

The earlier correlation/VIF diagnostic did not show strong cross-block
raw association sufficient to explain the flat ablation pattern, but it
does not establish independence of predictor information. Block ablation
does not isolate independent causal contribution and does not fully
resolve redundancy.

Descriptive repeated-CV means, these inferential tests, and the locked
holdout are three different objects. The holdout increment (Full vs
ED-history about +0.065 ROC / +0.085 PR) remains a confirmation result
and was larger than the CV mean increment. It was not used here for
inference.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical
utility, clinical validation, causality, national performance,
deployment readiness, or generalizability beyond this panel.
