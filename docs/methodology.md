# Methodology

This document describes the analysis as implemented in `feasibility/`
and as used to produce the saved files under `outputs/`. It is a
methods record, not a design sketch. Auto-generated run notes in
`outputs/*.md` are supporting artifacts; this file is the narrative
Methods section.

This is a **predictive research analysis** of MEPS Panel 24. It is not
a clinical prediction tool, a validated clinical model, a
deployment-ready system, a national risk calculator, or a causal study.

---

## 1. Study objective

Estimate, on the MEPS Panel 24 analytic sample, how much incremental
predictive discrimination a pre-specified pre-cutoff feature set adds
beyond three-year ED utilization history when predicting any ED visit
in calendar year 2022.

## 2. Research question

> How much additional predictive value can longitudinal health,
> utilization, access, demographic, and socioeconomic information
> provide beyond historical ED utilization alone?

Two pre-specified inferential questions were later locked in
`docs/pre_registration_block_ablation_plan.md` (do not edit that file):

- **Family A (primary):** incremental discrimination of the full model
  versus the ED-history baseline.
- **Family B (secondary):** change in performance when one pre-specified
  predictor block is removed from the full model.

Those questions are distinct from the earlier feature-family ablation,
which *added* families to the ED-history baseline on the locked holdout.

## 3. Data source

AHRQ MEPS Household Component, Panel 24, four-year longitudinal
public-use file **HC-245 (2019–2022)**. The raw file used is
`data/raw/h245.dta` (5,565 persons × 5,321 variables). The pipeline
does not download the file. Details: `docs/data_sources.md`.

NHAMCS was not used. It is visit-level and has no persistent person
identifier for prior → future person-level prediction.

## 4. Longitudinal cohort construction

Implemented in `feasibility/longitudinal.py`.

A person is in the analytic cohort when all of the following hold:

1. `YEARIND == 1` (present in the file for all four calendar years
   2019–2022; HC-245 documentation §2.1.2).
2. Valid non-sentinel `ERTOTY1`, `ERTOTY2`, `ERTOTY3`, and `ERTOTY4`.
3. Unique `DUPERSID`. Duplicate person rows fail the run.

Analytic **N = 5,108**. `ALL9RDS` is required to exist and is reported
(`ALL9RDS == 1` count = 4,883 on the raw file; analytic ∩ `ALL9RDS == 1`
= 4,883). It is **not** an inclusion criterion.

`LONGWT`, `VARSTR`, and `VARPSU` are required at ingest and recorded.
They are **not** applied to sklearn metrics.

**The current predictive analysis reports unweighted analytic-sample
performance and does not make national population estimates.**

Persons with `YEARIND != 1` (including many births, late entrants, and
deaths or institutionalization before 2022) are excluded. Thirty-seven
`YEARIND == 1` decedents (`DIED == 1`) with a valid `ERTOTY4` remain in
the primary cohort. A later sensitivity analysis dropped them; it did
not replace the cohort.

## 5. Prediction time origin and temporal cutoff

- Time origin / cutoff: **31 December 2021**
- Outcome window: calendar year **2022**
- Predictors must be demonstrably available in 2021 or earlier, or
  time-invariant.
- Unknown temporal availability is treated as not usable (fail closed).
- Round 7 overlaps 2021/2022 and is **not** used as a predictor.

## 6. Outcome definition

Primary outcome (`future_ed_visit`):

> 1 if `ERTOTY4 ≥ 1`, else 0

(`ERTOTY4 > 0` is equivalent for these integer visit counts.)

A secondary construct `future_high_ed_use` (`ERTOTY4 ≥ 2`) was counted
for inspection only (209 events in the analytic cohort). It was **not
modeled** and was not used for the first-run decision gate or for
inference.

## 7. Predictor specification

### ED-history baseline

`ERTOTY1`, `ERTOTY2`, `ERTOTY3`

### Full model (production predictor set)

`AGEY3X`, `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`, `RTHLTH6`,
`MNHLTH6`, `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `TTLPY3X`, `EMPST6`,
`ERTOTY1`, `ERTOTY2`, `ERTOTY3`

No `ERTOTY4` or other post-cutoff field is a predictor.

Treatment (`feasibility/config.py`):

- **Numeric:** `AGEY3X`, `TTLPY3X`, `ERTOTY1`, `ERTOTY2`, `ERTOTY3`
- **Categorical:** `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`, `RTHLTH6`,
  `MNHLTH6`, `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `EMPST6`

### Documented Family B blocks

| ID | Block removed | Variables |
|---|---|---|
| B1 | Age | `AGEY3X` |
| B2 | Demographics | `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X` (`AGEY3X` retained) |
| B3 | Health | `RTHLTH6`, `MNHLTH6` |
| B4 | Access | `INSCOVY3`, `HAVEUS6` |
| B5 | Socioeconomic | `POVCATY3`, `TTLPY3X`, `EMPST6` |

Access and SES are two separate blocks.

## 8. Temporal leakage controls

Implemented in `feasibility/features.py` and `feasibility/config.py`.

Every column in X must have a `FeatureSpec` whose availability is on or
before 2021 or time-invariant. `allowed_by_cutoff` is computed from that
rule and cannot be set independently. Name-pattern checks for Y4 and
Round 8/9 names are a backup. Tests cover `ERTOTY4`, `AGEY4X` /
`INSCOVY4`, and `RTHLTH8` / `EMPST9`. `assert_no_leakage` is called
before fitting.

## 9. Sentinel and missing-data handling

Documented MEPS codes −1, −7, −8, and −9 are recoded to missing. That
named set is **not exhaustive**: `features.recode_sentinels` treats
**every negative value** as non-usable, including codes that appear in
HC-245 but are outside the named set (for example `EMPST6` = −15). They
are never passed through as numeric measurements.

Missing values are then imputed inside the sklearn Pipeline (median for
numeric, most frequent for categorical). This is a single-imputation
first-pass strategy, not multiple imputation. Missingness is not used
as a predictor. No missingness indicators were added.

On the analytic cohort, `EMPST6` is non-usable for 16.01% of persons,
overwhelmingly because employment status is structurally inapplicable
for children. Those values are mode-imputed within each training fit
(the modal category is employed). `EMPST6` coefficients must not be
interpreted as causal or substantive employment effects. The imputer is
fit on training data only, so this step does not create evaluation-set
leakage. The adult-only sensitivity is a related population check. An
explicit inapplicable category was not used and could be considered in
future work.

## 10. Preprocessing

Implemented in `feasibility/modeling.py` as an sklearn `Pipeline` with
`ColumnTransformer`:

- Numeric: `SimpleImputer(strategy="median")` → `StandardScaler`
- Categorical: `SimpleImputer(strategy="most_frequent")` →
  `OneHotEncoder(handle_unknown="ignore")` (no dummy dropped)

The preprocessor is fit on the training fold only, then applied to the
validation or holdout fold.

## 11. Baseline model

Three baselines are scored on the locked holdout:

1. Prevalence-only: constant probability equal to the training
   prevalence.
2. Prior-year ED: regularized logistic on `ERTOTY3` only.
3. Three-year ED history: regularized logistic on `ERTOTY1`–`Y3`.

The inferential ED-history comparator is baseline 3.

## 12. Full model

L2-regularized logistic regression (`sklearn.linear_model.LogisticRegression`,
default L2 penalty, `C=1.0`, `max_iter=2000`, `random_state=42`).
Hyperparameters were not tuned. No other algorithm was added after the
first-run model.

## 13. First-run holdout evaluation

Person-level stratified split, `test_size=0.25`, `random_state=42`,
stratified on the binary 2022 outcome (`modeling._split`). Training
n = 3,831; holdout n = 1,277 (173 events).

This split is a **first-run / development-stage internal evaluation
set**. It was scored in the original pipeline. It was **not** used to
choose the model, tune hyperparameters, choose hypotheses, or compute
inferential p-values. It **was** used by the research-triage gate
(`report.decide_gate`) and by Design A add-on ablation. It is not
external, pristine, or independently confirmatory.

A first-run research triage “decision gate” (`report.decide_gate`) was
computed from holdout metrics. That gate is an engineering/research
triage tool, not a statistical decision rule and not a claim of
clinical readiness.

v1.1 adds person-level bootstrap percentile intervals
(`outputs/holdout_bootstrap_v1_1.csv`; B = 2,000; seed 20210915) and
calibration intercept/slope assessment
(`outputs/holdout_calibration_v1_1.csv`) on this same split. Those
quantities do not replace the locked point estimates and are not
recalibration.

## 14. Repeated cross-validation

Implemented in `feasibility/repeated_cv.py`.

The original 25% holdout is reconstructed with seed 42 and then left
unused. On the training portion only (n = 3,831):

- `RepeatedStratifiedKFold`
- 5 repeats × 5 folds
- `random_state=2021`
- Preprocessing and the classifier are refit inside each training fold.

This produces 25 paired fold-level estimates of ED-history vs full
model. The 25 folds are **not** treated as 25 independent observations.

## 15. Calibration assessment

For the first-run full model on the first-run holdout, a quantile-binned
reliability table (`outputs/calibration.csv`) is written via
`sklearn.calibration.calibration_curve`. v1.1 adds intercept and slope
from an unpenalized logistic regression of holdout `y` on `logit(p)`
(`outputs/holdout_calibration_v1_1.csv`): Cox calibration
`logit(Y) = a + b logit(p)` plus calibration-in-the-large (a with b
fixed at 1). That fit is **assessment
only**: predicted probabilities are not replaced, and the split is not
independent external validation. The joint intercept is the offset at
predicted p = 0.5 when slope is free; overall prevalence calibration
is described by mean(p) versus mean(y) and by CITL. Threshold metrics at 0.5 are
exploratory descriptive metrics only. They are not an optimized or
clinical operating point.

## 16. Predictor-family ablation

Implemented in `feasibility/ablation.py`. **Design A:** add one family
at a time to the ED-history baseline and score the **same locked
holdout**. Families: demographics, health, access, socioeconomic, plus
the full model.

This answers a different question from leave-one-block-out.

A death-sensitivity analysis in the same module dropped `YEARIND == 1`
decedents (28 train / 9 test) and refit the full model. It did not
change the production cohort or model.

## 17. Documented block-ablation analysis

Implemented in `feasibility/age_ablation.py`,
`demographic_ablation.py`, `health_ablation.py`,
`access_ablation.py`, and `ses_ablation.py`, sharing
`feasibility/block_ablation.py`.

**Design B:** remove one pre-specified block from the full model and
compare the reduced model with the full model on the same 5×5 training
folds (and, descriptively, with ED-history).

Do not conflate Design A and Design B. Adding demographics to
ED-history is not the same contrast as removing the demographic block
from the full model.

The contrast set, Family A / Family B structure, Holm plan, and the
commitment that inference would wait until B4 and B5 existed are
recorded in `docs/pre_registration_block_ablation_plan.md`. That file
was locked before B4 and B5 were run and is **not** updated after those
runs (its B4/B5 “Not yet run” lines are historical lock-state text).

## 18. Predictor redundancy diagnostic

Implemented in `feasibility/diagnostics.py` on the training portion
(n = 3,831) only. Pairwise associations (Pearson, Spearman,
point-biserial, correlation ratio η, Cramér’s V) and variance inflation
factors on the one-hot design matrix. Flag threshold |association| >
0.5. The diagnostic did **not** drop predictors, change the production
model, or alter the contrast set.

Infinite VIFs on one-hot columns in the locked table are a structural
artifact of encoding without dropping a reference level, not evidence
of a data error. A v1.1 diagnostic with `drop="first"` yields finite
VIFs, all < 5 (`outputs/predictor_vif_drop_reference_v1_1.csv`). VIF
was never a removal rule.

## 19. Statistical inference

Implemented in `feasibility/statistical_inference.py`. Reads saved
fold-level CSVs only. Does not refit models.

**Nadeau–Bengio corrected resampled t-test** as implemented:

\[
\mathrm{Var}_{NB}(\bar{d}) = \left(\frac{1}{n} + \frac{n_{\mathrm{test}}}{n_{\mathrm{train}}}\right) s^{2},
\quad
t = \frac{\bar{d}}{\sqrt{\mathrm{Var}_{NB}}},
\quad
\mathrm{df} = n - 1
\]

where \(s^{2}\) is the unbiased sample variance of the \(n\) paired
fold-level differences.

Exact settings:

- 25 paired fold differences (\(n = r \times k = 25\))
- \(k = 5\) folds, repeated 5 times
- test/train ratio = mean validation/training size within each split
  (saved value 0.250000; theoretical 5-fold ratio = 0.25)
- \(\mathrm{df} = 24\)
- two-sided Student’s *t*
- \(\alpha = 0.05\)
- Family A: unadjusted Nadeau–Bengio p-value
- Family B: Holm–Bonferroni **separately** for ROC-AUC, PR-AUC, and
  Brier (five contrasts within each metric). Holm is not applied to
  Family A and is not applied across families or across metrics.

Holm: order \(p_{(1)} \le \cdots \le p_{(m)}\); adjusted
\(p(i) = \max_{j \le i} \min\bigl(1, (m-j+1)\, p_{(j)}\bigr)\).

This is **not** the naive \(\mathrm{SE} = s / \sqrt{25}\) that would
treat folds as independent.

Source named in the implementation: Nadeau & Bengio (2003). TODO:
complete bibliographic citation from the original paper if a manuscript
requires a formal reference list.

Bouckaert & Frank is **not** implemented as a separate variance
estimator in this repository. TODO: add a complete citation only if a
manuscript discusses that related literature; do not invent publication
details here.

## 20. Repeat-level robustness analysis

Implemented in `feasibility/robustness_repeat_level.py`. Family A only.
Reads `outputs/repeated_cv_metrics.csv`. Does not refit.

The 25 fold deltas are averaged within each of the five repeats,
yielding five repeat-level means per metric. A standard one-sample
two-sided *t*-test of those five means against 0 is run (\(\mathrm{df}
= 4\)).

**The repeat-level test was an additional sensitivity analysis and did
not replace the Nadeau–Bengio analysis.**

The five repeats reuse the same underlying training sample. Collapsing
each repeat to one mean and treating those five means as independent
understates uncertainty. Smaller repeat-level *p*-values are therefore
**not** stronger evidence and must not be read as a more conservative
inferential test. Repeat-level Brier significance does not overturn the
primary Brier result (*p* = 0.1110).

## 21. Reproducibility

Python ≥ 3.10. Dependencies: `pandas`, `numpy`, `scikit-learn`,
`scipy`, `matplotlib` (`pyproject.toml`). Exact versions used to
document the v1.1 freeze are in `docs/environment_v1_1.md`. `scipy` is
required by the inference, robustness, and diagnostics modules.

Install and test:

```bash
pip install -e ".[dev]"
python -m pytest
```

Place official `h245.dta` at `data/raw/h245.dta`. Do **not** re-run
`python -m feasibility.run` against a completed analysis; that command
overwrites first-run holdout artifacts.

Later modules write their own filenames. The completed v1.0 sequence
was:

1. `python -m feasibility.run`
2. `python -m feasibility.ablation`
3. `python -m feasibility.repeated_cv`
4. `python -m feasibility.age_ablation`
5. `python -m feasibility.demographic_ablation`
6. `python -m feasibility.health_ablation`
7. `python -m feasibility.diagnostics`
8. `python -m feasibility.access_ablation`
9. `python -m feasibility.ses_ablation`
10. `python -m feasibility.statistical_inference`
11. `python -m feasibility.robustness_repeat_level`

v1.1 reporting analyses (new filenames only):

12. `python -m feasibility.revision_v1_1`

Seeds: holdout / logistic `random_state=42`; repeated CV
`random_state=2021`; v1.1 holdout bootstrap `20210915`.

Locked v1.0 generated summaries (for example
`outputs/statistical_inference_summary.md`,
`outputs/repeated_cv_summary.md`,
`outputs/robustness_repeat_level_summary.md`) retain historical wording
such as “Pre-registered,” “untouched,” or “conservative.” Those files
are preserved byte-for-byte. Current interpretation is in this document,
the manuscript, and the generator templates.

## Research positioning

This Methods document describes what was implemented. How the design
relates to prior ED-prediction and MEPS studies is reviewed separately
in `docs/related_work.md`. The analysis is positioned as a test of
incremental information beyond a three-year ED-history baseline, not as
an algorithm-competition study and not as a claim of a previously
unstudied prediction problem.
