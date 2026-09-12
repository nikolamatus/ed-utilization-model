# Repeat-level robustness check (Family A only)

Diagnostic only. The pre-registered primary test remains the
Nadeau–Bengio corrected t-test (df = 24) on the 25 paired fold deltas.
This file does not replace that test and was not applied to Family B.

## Method

The 25 Full − ED-history fold-level deltas from
`outputs/repeated_cv_metrics.csv` were grouped by repeat (5 repeats × 5
folds). The mean delta within each repeat was computed for ROC-AUC,
PR-AUC, and Brier, yielding 5 numbers per metric. A standard one-sample
two-sided t-test of those 5 repeat-level means against 0 was run
(df = 4).

This test uses only 5 independent observations (the repeats). It is far
less powered than the Nadeau–Bengio test. It is run specifically as a
conservative robustness check on the Family A ROC result (NB p = 0.0226),
which was close to the 0.05 threshold under the primary correction.

No model was refit. Existing experiment outputs were not modified.

## Repeat-level means (Full − ED-history)

| metric | r0 | r1 | r2 | r3 | r4 |
|---|---:|---:|---:|---:|---:|
| roc_auc | +0.0359 | +0.0272 | +0.0221 | +0.0287 | +0.0337 |
| pr_auc | +0.0438 | +0.0326 | +0.0265 | +0.0360 | +0.0405 |
| brier | -0.0019 | -0.0018 | -0.0011 | -0.0015 | -0.0021 |

## Comparison with the pre-registered Nadeau–Bengio test

| metric | NB t (df=24) | NB p | NB sig. 0.05 | repeat-level t (df=4) | repeat-level p | repeat-level sig. 0.05 |
|---|---:|---:|---|---:|---:|---|
| roc_auc | +2.437 | 0.0226 | yes | +12.135 | 0.0003 | yes |
| pr_auc | +3.385 | 0.0024 | yes | +11.850 | 0.0003 | yes |
| brier | -1.655 | 0.1110 | no | -9.747 | 0.0006 | yes |

- Repeat-level ROC: t = +12.135, p = 0.0003, df = 4, significant at 0.05: yes.
- Repeat-level PR: t = +11.850, p = 0.0003, df = 4, significant at 0.05: yes.
- Repeat-level Brier: t = -9.747, p = 0.0006, df = 4, significant at 0.05: yes.

## Conclusion relative to Family A discrimination

The primary hypothesis is that the full model has higher discrimination
than 3-year ED history. Under Nadeau–Bengio, ROC (p = 0.0226) and PR
(p = 0.0024) were significant; Brier was not.

Under this conservative repeat-level check, ROC is significant
and PR is significant at alpha = 0.05.
The Family A discrimination finding survives this check for both ROC and PR.

This changes no prior conclusion by itself. It is additional evidence to
report alongside the pre-registered Nadeau–Bengio result, not a
replacement for it.

Unweighted MEPS Panel 24 analytic-sample results only.
