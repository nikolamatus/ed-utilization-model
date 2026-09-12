# Pre-registration: full-model block-ablation contrast set

**Date committed:** 2026-09-12  
**Status:** locked before access-block (B4) and SES-block (B5) ablation  
**Scope:** MEPS Panel 24 HC-245 analytic cohort; unweighted person-level
regularized logistic models already used in this repository.

This document is written **before** any further ablation is run. It does
not contain results from B4 or B5. No result, contrast definition, or
statistical procedure in this document may be revised after B4 or B5
are run. If a change is needed later, it must be logged as a dated
amendment with a reason, not a silent edit.

This document does **not** authorize significance testing, Nadeau–Bengio
correction, or multiplicity adjustment until B4 and B5 exist.

---

## Research questions already in progress

Primary question (Family A): how much incremental discrimination does the
current full predictor set add beyond three-year ED history?

Secondary question (Family B): how much does performance change when one
pre-specified predictor block is removed from the current full model?

These are different questions from the earlier feature-family ablation,
which *added* families to an ED-history baseline. Feature-family deltas
and full-model leave-one-block-out deltas are not directly commensurate.

---

## Design constraints (unchanged)

- Same analytic cohort (`YEARIND==1` and valid non-sentinel `ERTOTY1`–`Y4`).
- Same 2022 any-ED outcome (`ERTOTY4 ≥ 1`).
- Same 3,831-person training portion recovered by the existing repeated-CV
  implementation (holdout seed 42).
- Same 5×5 `RepeatedStratifiedKFold` (`n_splits=5`, `n_repeats=5`,
  `random_state=2021`).
- Same locked 25% holdout; holdout is confirmation only and is not used
  for model selection, tuning, or hypothesis choice.
- Same preprocessing (median/mode imputation, scaling, one-hot encoding),
  fitted inside each training fold.
- Same regularized logistic configuration (`C=1.0`, no hyperparameter
  search).
- Same leakage controls. No new predictors. No feature engineering.
- No cohort, outcome, or methodology change.

---

## Full contrast set (six total)

### Family A — primary (one pre-specified hypothesis)

No multiplicity correction is applied inside Family A because it contains
a single primary hypothesis.

| ID | Contrast | Status |
|---|---|---|
| A1 | Full − ED-history | Already run; locked (`outputs/repeated_cv_metrics.csv` and paired block-ablation CSVs that reproduce the same full-vs-ED folds) |

ED-history predictors: `ERTOTY1`, `ERTOTY2`, `ERTOTY3`.

Full-model predictors: `AGEY3X`, `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`,
`RTHLTH6`, `MNHLTH6`, `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `TTLPY3X`,
`EMPST6`, `ERTOTY1`, `ERTOTY2`, `ERTOTY3`.

### Family B — secondary (five leave-one-block-out contrasts vs the full model)

Holm–Bonferroni correction will be applied **within this family of 5**
only, and **only after B4 and B5 exist**.

| ID | Contrast | Block removed from the full model | Status |
|---|---|---|---|
| B1 | No-age − Full | `AGEY3X` | Already run; locked |
| B2 | No-demographics − Full | `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X` (`AGEY3X` retained) | Already run; locked |
| B3 | No-health − Full | `RTHLTH6`, `MNHLTH6` | Already run; locked |
| B4 | No-access − Full | `INSCOVY3`, `HAVEUS6` | **Not yet run** |
| B5 | No-SES − Full | `POVCATY3`, `TTLPY3X`, `EMPST6` | **Not yet run** |

Access (`INSCOVY3`, `HAVEUS6`) and SES (`POVCATY3`, `TTLPY3X`, `EMPST6`)
will be ablated as **two separate blocks**, consistent with every prior
block ablation (age alone, demographics as one block, health as one
block). They are **not** being collapsed into a single “access/SES”
block.

Each of B4 and B5 will also report the paired contrasts vs ED-history,
as prior block ablations did, for descriptive continuity. Those
vs-ED-history contrasts are **not** additional Family B hypotheses and
are not included in the Holm–Bonferroni family of 5.

---

## Metrics (unchanged)

For every fold of every contrast:

- ROC-AUC
- PR-AUC
- Brier score

Fold-level summaries (mean, SD, median, min, max, 2.5th percentile,
97.5th percentile, count of positive ROC/PR deltas, count of improved
Brier) remain **descriptive**. The 2.5th and 97.5th percentiles are not
confidence intervals. The 25 folds are not treated as 25 independent
observations.

---

## Statistical method (deferred)

The statistical pass will be run **only after B4 and B5 exist**.

Method, committed now:

1. Use the already-saved fold-level CSVs from all five block-ablation
   experiments (and the locked repeated-CV file for A1 if needed).
   **No refitting** at the statistical-pass stage.
2. Apply the **Nadeau–Bengio corrected variance estimator** appropriate
   to 5×5 repeated CV (folds within a repeat are not independent) to
   each contrast.
3. Family A (A1 only): Nadeau–Bengio correction; **no** multiplicity
   adjustment (sole primary hypothesis).
4. Family B (B1–B5): Nadeau–Bengio correction on each of the five
   contrasts vs the full model, then **Holm–Bonferroni** across the five
   Family B p-values.

No significance testing, no Nadeau–Bengio correction, and no
Holm–Bonferroni adjustment will be performed before B4 and B5 are
complete.

---

## Execution order from this date

1. Predictor redundancy diagnostic (correlation + VIF) on the training
   portion — diagnostic only; does not change the model or the contrast
   set.
2. Run B4 (access ablation) exactly as age / demographics / health were
   run. No significance testing.
3. Run B5 (SES ablation) the same way. No significance testing.
4. Only then: statistical pass on the saved fold-level CSVs.

---

## What this document does not claim

This is not a claim of clinical utility, causality, national
performance, deployment readiness, or generalizability beyond MEPS
Panel 24. It does not authorize dropping, combining, or transforming
predictors on the basis of the diagnostic step.

---

## Amendment log

*(none at commitment date 2026-09-12)*
