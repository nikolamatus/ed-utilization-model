# Incremental Predictive Value of Longitudinal Health and Socioeconomic Information Beyond Historical Emergency Department Utilization: A Reproducible MEPS Panel 24 Analysis

Nikola Matus  
Independent research

This document is a manuscript draft based on a frozen empirical analysis. It is not a journal-specific submission package. All numerical results are taken from saved repository outputs and are unweighted predictive metrics on the MEPS Panel 24 analytic sample. They are not national estimates, clinical-utility estimates, or causal effects.

---

## 1. Abstract

**Background.** Future emergency-department (ED) use is known to be predictable from historical utilization and other patient characteristics. Prior ED visits are typically among the strongest predictors. Less is established about how much incremental discrimination a broader pre-cutoff feature set adds beyond a multi-year ED-history-only baseline on a public four-year household panel.

**Objective.** To estimate, on the Medical Expenditure Panel Survey (MEPS) Panel 24 analytic sample, the incremental predictive value of pre-specified demographic, health, access, and socioeconomic information beyond three-year ED utilization history when predicting any ED visit in calendar year 2022.

**Methods.** The analysis used the AHRQ MEPS Household Component Panel 24 four-year longitudinal public-use file HC-245 (2019–2022). The analytic cohort required unique person identifiers, presence in all four calendar years (`YEARIND == 1`), and valid non-sentinel ED counts for 2019–2022 (N = 5,108; 693 events; prevalence 0.136). The prediction cutoff was 31 December 2021. The primary outcome was any 2022 ED visit (`ERTOTY4 ≥ 1`). A ≥2-visit construct was counted descriptively and was not modeled. The ED-history baseline used `ERTOTY1`–`ERTOTY3`. The full model added age, sex, race/ethnicity, region, marital status, perceived physical and mental health, insurance, usual source of care, poverty category, income, and employment, all specified as available on or before the cutoff or time-invariant. Models were L2-regularized logistic regressions (`C = 1.0`). A locked 25% stratified holdout (n = 1,277) was used for confirmation only. Inferential comparisons used training-only repeated 5×5 stratified cross-validation and a pre-registered Nadeau–Bengio corrected resampled *t*-test. Leave-one-block-out contrasts were Holm-adjusted within each metric. All reported metrics are unweighted analytic-sample scores.

**Results.** On the locked holdout, three-year ED history achieved ROC-AUC 0.709, PR-AUC 0.331, and Brier 0.105; the full model achieved 0.774, 0.416, and 0.099. Repeated cross-validation mean increments (full minus ED history) were +0.0295 ROC-AUC, +0.0359 PR-AUC, and −0.0017 Brier. Under the pre-specified Nadeau–Bengio analysis (df = 24), the ROC-AUC and PR-AUC increments were statistically detected (*p* = 0.0226 and 0.0024); the Brier increment was not (*p* = 0.1110). No leave-one-block-out contrast was statistically detected after Holm correction. A repeat-level sensitivity analysis supported the discrimination finding but was not treated as a replacement for the pre-registered test.

**Conclusions.** The primary discrimination hypothesis was supported: adding pre-cutoff information beyond three-year ED utilization history produced statistically detectable improvements in ROC-AUC and PR-AUC under the pre-specified Nadeau–Bengio analysis. The Brier improvement was directionally favorable but was not statistically detected under that analysis. No single pre-specified predictor block was shown to account for the incremental discrimination. However, the block-ablation design cannot distinguish distributed information from more subtle redundancy. This is a methodological and predictive analysis of one MEPS panel. It is not a clinical tool, a national risk estimate, or evidence of clinical utility.

---

## 2. Introduction

Emergency-department utilization is a long-standing subject of epidemiologic and predictive research. Across health-system registration data, hospital discharge records, administrative claims, and national surveys, later ED use can be predicted from historical utilization and other patient-level information (Wu et al., 2016; Pereira et al., 2016; Gao et al., 2018; Chiu et al., 2023; Stockbridge et al., 2014). Prior ED visits are repeatedly among the strongest predictors of later visits, including short-horizon revisits and next-year frequent use (Montoy et al., 2019; Chiu et al., 2020; Chiu et al., 2023; Wu et al., 2016; Krieg et al., 2016). Gao et al. (2018) reported a particularly clear discrimination increment when prior-year utilization was added to demographics for 30-day Veterans Affairs revisits.

That literature already answers the first-order question of whether future ED use is predictable. It does not, by itself, answer a narrower incremental question: after a strong multi-year ED-history baseline is specified, how much additional discrimination is available from other information that is demonstrably known before a calendar-year cutoff?

The distinction matters. Many studies include prior utilization as one covariate among others, compare algorithms on a full feature set, or model frequent use among people who already visited an ED. Association reviews document that public insurance, chronic illness, mental health problems, and poorer self-rated health are related to frequent ED use (Hunt et al., 2006; Krieg et al., 2016; Giannouchos et al., 2019). Those findings motivate richer feature sets, but they are not nested discrimination tests against an ED-history-only model. Short-horizon electronic health record studies of 72-hour to 30-day return visits establish operational revisit prediction, not next-year person-level any-ED use in a household survey (Hong et al., 2019; Montoy et al., 2019).

MEPS is a nationally representative household panel with persistent person identifiers and annual utilization totals. It has been used for longitudinal association with next-year ED use and for incremental prediction of high cost. Stockbridge, Wilson, and Pagán (2014) used MEPS Panel 14 to relate year-1 psychological distress, including year-1 ED counts, to year-2 ED use with survey-weighted hurdle models. That paper establishes that a time-ordered MEPS design can support next-year ED analysis; it does not report ROC-AUC, PR-AUC, or Brier increments versus an ED-history-only baseline. Fleishman and Cohen (2010) compared nested models for year-2 high expenditure on earlier two-year panels and found that health status added little after condition-based scores. That is an incremental prediction design for cost, not for any-ED visits.

The present study uses the AHRQ MEPS Panel 24 four-year longitudinal public-use file HC-245 (2019–2022). In a targeted, non-PRISMA review of PubMed, PMC, publisher sites, and AHRQ documentation (September 2026; approximately 70 titles screened and about 18 retained), no directly matching study was identified that compared an explicit multi-year ED-history-only baseline with a richer pre-cutoff demographic, health, access, and socioeconomic model for next-year any-ED use on MEPS Panel 24 / HC-245 (see `docs/related_work.md`). That is a positioning statement about the literature reviewed. It is not a claim that no such study exists, that this is the first ED prediction study, or that this is the first MEPS ED study.

The contribution is incremental and methodological: a leakage-controlled, time-ordered comparison of a three-year ED-history baseline with a pre-specified fuller feature set, evaluated with locked holdout confirmation, repeated stratified cross-validation, pre-registered Nadeau–Bengio inference (Nadeau and Bengio, 2003), and leave-one-block-out ablation. Individual design elements are not claimed to be novel in isolation.

This paper describes a frozen analysis. It is a predictive research study of one public-use panel. It is not a clinical prediction tool, a validated clinical model, a deployment-ready system, a national risk calculator, or a causal study.

---

## 3. Research question and hypothesis

The research question is:

> How much additional predictive value can longitudinal health, utilization, access, demographic, and socioeconomic information provide beyond historical ED utilization alone?

Two inferential questions were locked in `docs/pre_registration_block_ablation_plan.md` before access-block and socioeconomic-block ablation and before the statistical pass:

- **Family A (primary).** Incremental discrimination of the full pre-cutoff model versus the three-year ED-history baseline on training-only repeated cross-validation.
- **Family B (secondary).** Change in performance when one pre-specified predictor block is removed from the full model.

The primary hypothesis is that the full model improves ROC-AUC and PR-AUC relative to three-year ED history under the pre-specified Nadeau–Bengio analysis. Brier score is reported as a proper scoring rule; a Brier increment was not required for the primary discrimination hypothesis.

These questions are distinct from an earlier exploratory feature-family ablation that *added* families to the ED-history baseline on the locked holdout. Adding a family to ED history is not the same contrast as removing that block from the full model.

---

## 4. Data source

The data source is the Agency for Healthcare Research and Quality (AHRQ) Medical Expenditure Panel Survey (MEPS), Household Component, Panel 24, four-year longitudinal public-use file **HC-245**, covering calendar years **2019–2022** (Rounds 1–9). The ingested file used for this analysis contained 5,565 persons and 5,321 variables. The person identifier is `DUPERSID`.

The analysis used a user-supplied official Stata file placed at `data/raw/h245.dta`. The pipeline does not download from AHRQ and does not redistribute the microdata. HC-245 documentation is at:

https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml

The National Hospital Ambulatory Medical Care Survey (NHAMCS) was not used. It is visit-level and does not provide a persistent person identifier suitable for prior-to-future person-level prediction in this design.

The HC-245 documentation states that AHRQ requests users cite AHRQ and the Medical Expenditure Panel Survey as the data source in publications or research based on these data. AHRQ does not specify a required bibliographic format beyond that request.

Survey design variables `LONGWT`, `VARSTR`, and `VARPSU` were required at ingest and recorded. They were not applied to sklearn metrics. `ALL9RDS` was recorded as the AHRQ subset flag for weighted national four-year estimates when used with `LONGWT`. It was not an inclusion criterion.

**All performance metrics in this paper are unweighted analytic-sample metrics. The study does not produce national MEPS estimates.**

---

## 5. Study population and cohort construction

A person entered the analytic cohort when all of the following held:

1. Unique `DUPERSID`. Duplicate person rows fail the run.
2. `YEARIND == 1`, indicating presence in the file for all four calendar years 2019–2022 (HC-245 documentation §2.1.2).
3. Valid, non-missing, non-sentinel values of `ERTOTY1`, `ERTOTY2`, `ERTOTY3`, and `ERTOTY4`. Documented MEPS codes −1, −7, −8, and −9, and any other negative, are treated as non-usable.

The resulting analytic sample is **N = 5,108**, with **693** 2022 any-ED events (prevalence **0.13567**). The raw file contained 5,565 unique persons. `ALL9RDS == 1` on the raw file was 4,883; the intersection of the analytic cohort with `ALL9RDS == 1` was also 4,883. Persons with 1, 2, 3, or 4 observed years on the raw file numbered 191, 160, 106, and 5,108.

Persons with `YEARIND != 1`, including many births, late entrants, and deaths or institutionalization before 2022, were excluded. Thirty-seven persons with `YEARIND == 1` and `DIED == 1` remained in the primary cohort because a valid 2022 ED total was observed while they were in scope. A later sensitivity analysis dropped those decedents; it did not replace the primary cohort.

The unit of analysis is the person. Results describe this constructed analytic sample, not the U.S. civilian noninstitutionalized population as a weighted survey estimate.

---

## 6. Prediction target and temporal cutoff

The time origin and prediction cutoff is **31 December 2021**. The outcome window is calendar year **2022**.

The primary outcome is any ED visit in 2022:

> `future_ed_visit` = 1 if `ERTOTY4 ≥ 1`, else 0.

For these integer visit counts, `ERTOTY4 > 0` is equivalent. `ERTOTY4` is never a predictor.

A secondary construct, `future_high_ed_use` (`ERTOTY4 ≥ 2`), was counted for inspection only: 209 events in the analytic cohort (prevalence 0.04092). It was **not modeled** and was not used for inference.

Predictors were required to be demonstrably available in 2021 or earlier, or time-invariant. Unknown temporal availability was treated as not usable (fail closed). Round 7 overlaps 2021 and 2022 and was not used as a predictor.

---

## 7. Predictor specification

### 7.1 ED-history baseline

`ERTOTY1`, `ERTOTY2`, `ERTOTY3` (emergency-room visit counts in 2019, 2020, and 2021).

### 7.2 Full model

The production predictor set is:

`AGEY3X`, `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`, `RTHLTH6`, `MNHLTH6`, `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `TTLPY3X`, `EMPST6`, `ERTOTY1`, `ERTOTY2`, `ERTOTY3`.

Treatment:

- **Numeric:** `AGEY3X`, `TTLPY3X`, `ERTOTY1`, `ERTOTY2`, `ERTOTY3`
- **Categorical:** `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`, `RTHLTH6`, `MNHLTH6`, `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `EMPST6`

These are confirmed HC-245 longitudinal names. Full-year consolidated aliases such as `AGE42X` or `INSCOV21` were not used.

### 7.3 Pre-registered Family B blocks

| ID | Block removed | Variables |
|---|---|---|
| B1 | Age | `AGEY3X` |
| B2 | Demographics | `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X` (`AGEY3X` retained) |
| B3 | Health | `RTHLTH6`, `MNHLTH6` |
| B4 | Access | `INSCOVY3`, `HAVEUS6` |
| B5 | Socioeconomic | `POVCATY3`, `TTLPY3X`, `EMPST6` |

Access and socioeconomic status were specified as two separate blocks.

Homelessness, substance-use disorder, and food insecurity were not represented as such. The public-use file did not provide variables that were treated as sufficiently defensible direct measures of those constructs for this locked predictor set. Related items that exist on HC-245 (for example `SDAFRDHOME5`, SNAP purchase variables, or SAQ alcohol/tobacco items) were not used and were not relabeled as those constructs.

---

## 8. Leakage prevention

Every candidate column has a feature specification whose allowed status is computed from temporal availability: a feature may enter *X* only if it is available in 2021 or earlier or is time-invariant. `allowed_by_cutoff` cannot be set independently of that rule. Name-pattern checks for Y4 and Round 8/9 counterparts are a backup. Known post-cutoff names, including `AGEY4X`, `INSCOVY4`, `RTHLTH8`, `EMPST8`, and `ERTOTY4`, are registered as banned. Round 7 is overlapping and unused.

`assert_no_leakage` is called before fitting. Tests cover leakage of the outcome and of post-cutoff age, insurance, health, and employment names.

The 2022 outcome and other post-cutoff fields do not enter the predictor set.

---

## 9. Baseline and full models

All models are L2-regularized logistic regressions (`sklearn.linear_model.LogisticRegression`, default L2 penalty, `C = 1.0`, `max_iter = 2000`, `random_state = 42`). Hyperparameters were not tuned. No tree ensemble, survival model, or sequence model was added after the first-run model.

Three baselines were scored on the locked holdout:

1. Prevalence only: constant probability equal to the training prevalence.
2. Prior-year ED: regularized logistic regression on `ERTOTY3` only.
3. Three-year ED history: regularized logistic regression on `ERTOTY1`–`ERTOTY3`.

The inferential comparator is baseline 3. The full model uses the production predictor set in Section 7.2 with the same estimator class.

This is regularized logistic regression, not an algorithm-competition study.

---

## 10. Preprocessing

MEPS sentinel codes −1, −7, −8, and −9, and any other negative, are recoded to missing. They are never passed through as numeric measurements. Missingness is not used as a predictor; no missingness indicators were added.

Preprocessing is an sklearn `Pipeline` with `ColumnTransformer`, fit on the training fold only:

- Numeric: median imputation, then standard scaling.
- Categorical: most-frequent imputation, then one-hot encoding with `handle_unknown="ignore"` (no reference level dropped).

This is single imputation, not multiple imputation.

---

## 11. Validation design

A person-level stratified 25% holdout (`test_size = 0.25`, `random_state = 42`, stratified on the binary 2022 outcome) produced a training portion of **n = 3,831** and a holdout of **n = 1,277** (173 events; prevalence 0.13547).

The holdout was a confirmation split for the selected primary comparison. It was not used to choose the model, tune hyperparameters, choose hypotheses, or compute inferential *p*-values.

Repeated cross-validation reconstructed that holdout with seed 42, left it unused, and applied `RepeatedStratifiedKFold` (5 repeats × 5 folds, `random_state = 2021`) on the training portion only. Preprocessing and the classifier were refit inside each training fold. This produced 25 paired fold-level estimates of ED-history versus full-model performance. The 25 folds are not treated as 25 independent observations.

The 2.5th–97.5th percentiles of fold-level differences are descriptive empirical ranges, not conventional confidence intervals.

---

## 12. Performance metrics

Primary reported metrics are ROC-AUC, PR-AUC, and Brier score. PR-AUC is relevant because the outcome is uncommon (analytic prevalence 0.136). Brier score is a proper scoring rule; lower is better.

Threshold-dependent metrics (accuracy, sensitivity, specificity, precision, recall) at probability 0.5 were computed on the holdout as exploratory descriptive metrics only. They are not an optimized or clinical operating point.

Calibration for the first-run full model on the locked holdout is a quantile-binned reliability table. It is a descriptive check, not a recalibration analysis.

---

## 13. Statistical inference

Inference reads saved fold-level CSVs and does not refit models.

The pre-specified test is the Nadeau–Bengio corrected resampled *t*-test (Nadeau and Bengio, 2003):

\[
\mathrm{Var}_{NB}(\bar{d}) = \left(\frac{1}{n} + \frac{n_{\mathrm{test}}}{n_{\mathrm{train}}}\right) s^{2},
\quad
t = \frac{\bar{d}}{\sqrt{\mathrm{Var}_{NB}}},
\quad
\mathrm{df} = n - 1
\]

where \(s^{2}\) is the unbiased sample variance of the \(n\) paired fold-level differences, \(n = 25\), \(k = 5\), \(r = 5\), the test/train ratio is the mean validation-to-training size within each split (saved value 0.250000), and \(\mathrm{df} = 24\). Tests are two-sided at \(\alpha = 0.05\).

This is not the naive standard error \(s / \sqrt{25}\).

Family A uses the unadjusted Nadeau–Bengio *p*-value. Family B applies Holm–Bonferroni separately within ROC-AUC, PR-AUC, and Brier across the five leave-one-block-out contrasts. Holm is not applied to Family A and is not applied across families or across metrics.

Reduced-versus-ED-history deltas from block ablations are descriptive and are not additional Family B hypotheses.

---

## 14. Pre-registration

The contrast set, Family A / Family B structure, Holm plan, estimator, cohort, outcome, seeds, and the rule that inference would wait until B4 and B5 existed are recorded in `docs/pre_registration_block_ablation_plan.md`, committed 2026-09-12. That file was locked before B4 and B5 were run. Its B4/B5 “Not yet run” lines are historical lock-state text, not current project status. The file is not edited after those runs.

The statistical pass used saved fold-level CSVs only. No predictors, cohort definition, or estimator settings were changed after lock.

The feature-family add-on ablation, death sensitivity, predictor-redundancy diagnostic, and repeat-level robustness check were not pre-registered as inferential replacements for Families A and B.

---

## 15. Sensitivity analyses

**Death sensitivity.** Thirty-seven `YEARIND == 1` decedents remained in the primary cohort. Dropping nine decedents from the original holdout changed full-model ROC-AUC from 0.774006 to 0.772214. Refitting after dropping 28 training and 9 test decedents gave ROC-AUC 0.770905. The change was not treated as material and did not replace the primary cohort.

**Predictor redundancy diagnostic.** On the training portion (n = 3,831), pairwise associations and variance inflation factors were computed. Flagged associations with |value| > 0.5 (Spearman excluded from the flag rule) included `AGEY3X`–`MARRY6X` (correlation ratio η = 0.8099) and `POVCATY3`–`TTLPY3X` (η = 0.5975). Numeric VIFs were all below 5. Infinite VIFs on one-hot columns are a structural artifact of encoding without dropping a reference level. The diagnostic did not drop predictors or change the production model. It does not prove independence.

**Repeat-level robustness.** The 25 Family A fold deltas were averaged within each of the five repeats, yielding five repeat-level means per metric. A standard one-sample two-sided *t*-test of those means against 0 was run (df = 4). The five repeats are a resampling unit, not five independent population samples. This analysis does not replace the pre-registered Nadeau–Bengio test.

**Feature-family add-on ablation (Design A).** Families were added one at a time to ED history and scored on the locked holdout. This is a different contrast from leave-one-block-out and is reported as exploratory confirmation, not as Family B.

---

## 16. Results

All numbers below are unweighted analytic-sample metrics from saved outputs. Fold-level percentile ranges are descriptive.

### 16.1 Locked holdout

Source: `outputs/model_metrics.csv`.

| Model | n | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|---:|
| Prevalence only | 1,277 | 0.500 | 0.135 | 0.117 |
| Prior-year ED (`ERTOTY3`) | 1,277 | 0.627 | 0.251 | 0.108 |
| 3-year ED history | 1,277 | 0.709 | 0.331 | 0.105 |
| Full regularized logistic | 1,277 | 0.774 | 0.416 | 0.099 |

Exact saved values for the inferential comparator and full model: ED-history ROC-AUC 0.709095, PR-AUC 0.330794, Brier 0.105286; full model 0.774006, 0.415935, 0.099390. Holdout increment, full minus three-year ED history: **+0.064911 ROC-AUC**, **+0.085141 PR-AUC**, Brier **−0.005896**.

The locked holdout produced larger incremental gains than the repeated-CV mean and should therefore be interpreted as confirmation on one split rather than as the expected effect size.

Threshold metrics at 0.5 are exploratory only (full-model sensitivity 0.104, specificity 0.995). Calibration showed imperfect alignment of predicted and observed event rates across deciles; that table was not used as a recalibration result.

### 16.2 Repeated cross-validation

Source: `outputs/repeated_cv_summary.csv`. Training portion only; holdout unused.

| Metric | Mean | SD | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| ED-history ROC-AUC | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 |
| ED-history PR-AUC | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 |
| ED-history Brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 |
| Full ROC-AUC | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 |
| Full PR-AUC | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 |
| Full Brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 |

Paired deltas, full minus ED history:

| Metric | Mean | SD | Median | Min | Max | Directional count |
|---|---:|---:|---:|---:|---:|---:|
| Δ ROC-AUC | +0.0295 | 0.0225 | +0.0240 | −0.0105 | +0.0778 | 23/25 positive |
| Δ PR-AUC | +0.0359 | 0.0197 | +0.0399 | −0.0002 | +0.0684 | 24/25 positive |
| Δ Brier | −0.0017 | 0.0019 | −0.0016 | −0.0047 | +0.0014 | 19/25 improved |

### 16.3 Primary inference (Family A)

Source: `outputs/statistical_inference.csv`. Nadeau–Bengio, 25 paired differences, df = 24, two-sided, α = 0.05, no multiplicity adjustment.

| Metric | Mean difference | Corrected SE | *t* | *p* | Significant at 0.05 |
|---|---:|---:|---:|---:|---|
| ROC-AUC | +0.0295 | 0.0121 | +2.437 | 0.0226 | yes |
| PR-AUC | +0.0359 | 0.0106 | +3.385 | 0.0024 | yes |
| Brier | −0.0017 | 0.0010 | −1.655 | 0.1110 | no |

Exact saved values: ROC mean +0.02953897, SE 0.01211861, *t* +2.437488, *p* = 0.02257265; PR mean +0.03590249, SE 0.01060767, *t* +3.384577, *p* = 0.00244863; Brier mean −0.00166965, SE 0.00100914, *t* −1.654524, *p* = 0.11104216.

The primary discrimination hypothesis was supported: adding pre-cutoff information beyond three-year ED utilization history produced statistically detectable improvements in ROC-AUC and PR-AUC under the pre-specified Nadeau–Bengio analysis. The Brier improvement was directionally favorable but was not statistically detected under that analysis.

Statistical significance is not clinical significance.

### 16.4 Feature-family add-on ablation (Design A)

Source: `outputs/feature_family_ablation.csv`. Same locked holdout. Exploratory; not commensurate with Family B.

| Model | ROC-AUC | PR-AUC | Brier | Δ ROC vs ED | Δ PR vs ED |
|---|---:|---:|---:|---:|---:|
| ED history only | 0.709 | 0.331 | 0.105 | 0 | 0 |
| ED + demographics | 0.752 | 0.400 | 0.101 | +0.043 | +0.069 |
| ED + health | 0.739 | 0.377 | 0.103 | +0.030 | +0.046 |
| ED + access | 0.740 | 0.356 | 0.104 | +0.031 | +0.025 |
| ED + socioeconomic | 0.746 | 0.382 | 0.103 | +0.037 | +0.051 |
| Full model | 0.774 | 0.416 | 0.099 | +0.065 | +0.085 |

On this holdout, adding the demographic family to ED history produced the largest single-family increment. That does not identify an independent causal contribution and does not replace Family B.

### 16.5 Leave-one-block-out ablations (Design B)

Sources: `outputs/age_ablation_cv.csv`, `demographic_ablation_cv.csv`, `health_ablation_cv.csv`, `access_ablation_cv.csv`, `ses_ablation_cv.csv`, and `outputs/statistical_inference.csv`. Same 5×5 training folds as Section 16.2.

Remaining CV mean increment versus ED history after removing the named block:

| Contrast | Remaining Δ ROC vs ED | Remaining Δ PR vs ED |
|---|---:|---:|
| Full model (reference) | +0.0295 | +0.0359 |
| B1 no-age | +0.0244 | +0.0342 |
| B2 no-demographics | +0.0358 | +0.0357 |
| B3 no-health | +0.0344 | +0.0401 |
| B4 no-access | +0.0278 | +0.0343 |
| B5 no-SES | +0.0314 | +0.0424 |

Family B contrasts (reduced minus full), Nadeau–Bengio with Holm–Bonferroni within each metric:

| Contrast | Metric | Mean | SE | *t* | Raw *p* | Holm *p* | Sig. 0.05 |
|---|---|---:|---:|---:|---:|---:|---|
| B1 No-age − Full | ROC | −0.0051 | 0.0038 | −1.354 | 0.1884 | 0.8720 | no |
| B1 No-age − Full | PR | −0.0017 | 0.0046 | −0.377 | 0.7092 | 1.0000 | no |
| B1 No-age − Full | Brier | +0.0002 | 0.0004 | +0.460 | 0.6497 | 1.0000 | no |
| B2 No-demographics − Full | ROC | +0.0062 | 0.0044 | +1.400 | 0.1744 | 0.8720 | no |
| B2 No-demographics − Full | PR | −0.0002 | 0.0050 | −0.038 | 0.9703 | 1.0000 | no |
| B2 No-demographics − Full | Brier | +0.0000 | 0.0004 | +0.035 | 0.9722 | 1.0000 | no |
| B3 No-health − Full | ROC | +0.0049 | 0.0054 | +0.898 | 0.3783 | 1.0000 | no |
| B3 No-health − Full | PR | +0.0042 | 0.0050 | +0.849 | 0.4043 | 1.0000 | no |
| B3 No-health − Full | Brier | −0.0004 | 0.0005 | −0.798 | 0.4328 | 1.0000 | no |
| B4 No-access − Full | ROC | −0.0018 | 0.0021 | −0.852 | 0.4029 | 1.0000 | no |
| B4 No-access − Full | PR | −0.0017 | 0.0023 | −0.723 | 0.4767 | 1.0000 | no |
| B4 No-access − Full | Brier | +0.0002 | 0.0002 | +1.226 | 0.2321 | 0.9284 | no |
| B5 No-SES − Full | ROC | +0.0019 | 0.0029 | +0.646 | 0.5247 | 1.0000 | no |
| B5 No-SES − Full | PR | +0.0065 | 0.0043 | +1.525 | 0.1404 | 0.7019 | no |
| B5 No-SES − Full | Brier | −0.0006 | 0.0004 | −1.445 | 0.1614 | 0.8072 | no |

No pre-specified leave-one-block-out contrast showed a statistically detectable performance change under the pre-specified corrected analysis.

No single pre-specified predictor block was shown to account for the incremental discrimination. However, the block-ablation design cannot distinguish distributed information from more subtle redundancy.

That statement does not mean that no block matters, that blocks are equivalent, that predictors are independent, or that any block is unnecessary.

### 16.6 Repeat-level robustness

Source: `outputs/robustness_repeat_level_test.csv`. Family A only; df = 4.

Repeat-level means (full minus ED history):

| Metric | r0 | r1 | r2 | r3 | r4 | *t* | *p* | NB *p* (primary) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ROC-AUC | +0.0359 | +0.0272 | +0.0221 | +0.0287 | +0.0337 | +12.135 | 0.0003 | 0.0226 |
| PR-AUC | +0.0438 | +0.0326 | +0.0265 | +0.0360 | +0.0405 | +11.850 | 0.0003 | 0.0024 |
| Brier | −0.0019 | −0.0018 | −0.0011 | −0.0015 | −0.0021 | −9.747 | 0.0006 | 0.1110 |

The repeat-level sensitivity analysis was supportive of the discrimination finding but was treated as additional sensitivity evidence rather than a replacement for the pre-registered Nadeau–Bengio analysis.

ROC-AUC and PR-AUC remained significant under the sensitivity analysis. Brier became significant at the repeat level (*p* = 0.0006) while remaining non-significant under the pre-specified Nadeau–Bengio test (*p* = 0.1110). The pre-specified Brier result stands.

---

## 17. Discussion

The primary result is incremental, not absolute. Three-year ED history already discriminated 2022 any-ED use on this analytic sample (holdout ROC-AUC 0.709; CV mean 0.685). That is consistent with a large literature in which prior ED use is a dominant predictor (Gao et al., 2018; Montoy et al., 2019; Chiu et al., 2023; Wu et al., 2016). The question addressed here is what remains after that baseline is specified.

The primary discrimination hypothesis was supported: adding pre-cutoff information beyond three-year ED utilization history produced statistically detectable improvements in ROC-AUC and PR-AUC under the pre-specified Nadeau–Bengio analysis. The Brier improvement was directionally favorable but was not statistically detected under that analysis.

The locked holdout increment (+0.065 ROC-AUC, +0.085 PR-AUC) exceeded the repeated-CV mean increment (+0.030 ROC-AUC, +0.036 PR-AUC). The locked holdout produced larger incremental gains than the repeated-CV mean and should therefore be interpreted as confirmation on one split rather than as the expected effect size. Inference uses the training-only paired fold differences, not the holdout *p*-value, which was never computed.

Leave-one-block-out results did not identify a single block whose removal statistically accounted for the increment. Remaining CV mean ROC increments versus ED history stayed in a similar range after each removal (approximately +0.024 to +0.036). No single pre-specified predictor block was shown to account for the incremental discrimination. However, the block-ablation design cannot distinguish distributed information from more subtle redundancy. Non-significant Family B tests are not evidence that reduced models are equivalent to the full model or that any block can be dropped for substantive reasons.

The exploratory holdout add-on ablation found the largest single-family increment when demographics were added to ED history. That contrast is not interchangeable with removing the demographic block from the full model, and Family B did not detect a demographic-block effect after Holm correction. The two designs answer different questions.

The repeat-level sensitivity analysis was supportive of the discrimination finding but was treated as additional sensitivity evidence rather than a replacement for the pre-registered Nadeau–Bengio analysis. Where the two procedures disagree on Brier, the pre-specified result is retained.

This study is closest, among papers in the targeted review, to incremental-information designs rather than algorithm bake-offs. Gao et al. (2018) quantified utilization increments for 30-day VA revisits among recent ED users. Stockbridge et al. (2014) used a two-year MEPS panel for survey-weighted association with next-year ED use. Fleishman and Cohen (2010) nested incremental models for high cost. Chiu et al. (2023) found that prior-year ED visits dominated algorithm comparisons for frequent use. The present analysis differs in panel, outcome (any 2022 ED visit among four-year participants), baseline (explicit three-year ED-history-only model), metric set, and inferential procedure. Those differences are design differences, not claims of superiority in real-world healthcare populations.

The analysis does not establish clinical utility, national predictive performance, causal effects of age, insurance, income, or health status, or readiness for deployment. Statistically detectable incremental discrimination on an unweighted analytic sample is a narrower claim.

---

## 18. Limitations

These limitations apply regardless of which tests were statistically detected.

1. **Unweighted analytic-sample metrics.** ROC-AUC, PR-AUC, and Brier values describe the constructed MEPS Panel 24 analytic sample. They are not survey-weighted population estimates.

2. **No national inference.** `LONGWT`, `VARSTR`, and `VARPSU` were recorded and not applied. The study does not support statements about national predictive performance.

3. **Single-panel validation.** All modeling, ablation, and inference use Panel 24 only. A random stratified holdout on one panel is not an independent population.

4. **No external validation.** No other survey, claims file, EHR extract, or health-system dataset was used.

5. **No temporal validation on later panels.** The outcome year is 2022 on the same panel used to form 2019–2021 predictors.

6. **COVID-era panel.** Panel 24 overlaps COVID-19. AHRQ documents comparability concerns related to phone-based interviewing.

7. **MEPS population coverage.** MEPS-HC samples the U.S. civilian noninstitutionalized population. It excludes incarcerated people, active-duty military, and institutionalized populations, and structurally undersamples people experiencing homelessness.

8. **Model class.** The estimator is L2-regularized logistic regression with fixed `C = 1.0`. Incremental discrimination is specific to this estimator class.

9. **Single imputation.** Sentinels are recoded to missing, then median or most-frequent imputed inside each fold. This is not multiple imputation.

10. **Missingness.** Raw-file non-usable rates after sentinel recode are about 5–8% for many candidates and 21.89% for `EMPST6`. Analytic-cohort missingness was audited in detail for `RTHLTH6` (0.06%) and `MNHLTH6` (0.10%). Employment and some health items are inapplicable for children.

11. **Mortality.** Competing risk of death is not modeled. Thirty-seven in-scope decedents remain in the primary cohort.

12. **Outcome definition.** The outcome is any self- or proxy-reported ED visit in 2022. It is not claims-adjudicated utilization, acuity, or avoidable versus unavoidable ED use.

13. **≥2 ED visits not modeled.** The high-utilizer construct was counted (209 events) and not modeled.

14. **Children and adults not separated.** Age is a single numeric predictor. Some covariates have different meaning or inapplicability by age.

15. **No clinical utility analysis.** No decision-curve, net-benefit, or intervention-impact analysis was performed.

16. **No clinical threshold.** Metrics at probability 0.5 are exploratory.

17. **No causal interpretation.** Ablation deltas are predictive associations, not effects of intervening on a block.

18. **Predictor association.** Age and marital status, and poverty category and income, are associated. The diagnostic does not prove independence.

19. **Limits of block ablation.** Leave-one-block-out cannot distinguish distributed independent information from more subtle redundancy.

20. **Limits of repeat-level sensitivity.** Five repeat-level means are a resampling unit (df = 4), not five independent samples.

21. **Survey versus operational data.** Coding, missingness, case-mix, and outcome ascertainment differ from EHR or claims systems. Performance in a hospital, payer, or regional system is unknown.

22. **Targeted literature review.** The related-work review was targeted and not a PRISMA systematic review. Absence of a paper from that review does not prove that no such paper exists.

---

## 19. Reproducibility and data availability

Code, tests, documentation, and saved outputs are in the public repository. Original code and documentation are released under the MIT License. That license does not grant rights to AHRQ MEPS microdata.

HC-245 is an AHRQ public-use file. This repository does not redistribute `h245.dta`. Researchers must obtain the official Stata-format file from AHRQ, place it at `data/raw/h245.dta`, and follow AHRQ public-use conditions, including not attempting to identify individuals. Cite AHRQ and the Medical Expenditure Panel Survey as the data source.

Dependencies are declared in `pyproject.toml` (Python ≥ 3.10; pandas, numpy, scikit-learn, scipy, matplotlib). Installation and tests:

```bash
python -m venv .venv
pip install -e ".[dev]"
python -m pytest
```

The completed analysis sequence is documented in `docs/methodology.md`. The first-run command `python -m feasibility.run` overwrites locked holdout artifacts and should not be re-run against this completed analysis. Later modules write their own filenames. Seeds: holdout and logistic `random_state = 42`; repeated CV `random_state = 2021`.

Authoritative numeric sources for this draft are `outputs/model_metrics.csv`, `outputs/repeated_cv_summary.csv`, `outputs/statistical_inference.csv`, `outputs/feature_family_ablation.csv`, the five block-ablation CV files, and `outputs/robustness_repeat_level_test.csv`. Narrative supporting documents are `docs/methodology.md`, `docs/results.md`, `docs/limitations.md`, `docs/data_sources.md`, `docs/related_work.md`, `docs/analysis_status.md`, and `docs/pre_registration_block_ablation_plan.md`.

---

## 20. Conclusion

On the MEPS Panel 24 analytic sample, under a locked cohort, predictor set, regularized logistic estimator, and pre-specified Nadeau–Bengio analysis, the full pre-cutoff feature set showed statistically detectable incremental ROC-AUC and PR-AUC versus three-year ED history. The Brier increment was directionally favorable and was not statistically detected under that analysis.

The locked holdout produced larger incremental gains than the repeated-CV mean and should therefore be interpreted as confirmation on one split rather than as the expected effect size. The repeat-level sensitivity analysis was supportive of the discrimination finding but was treated as additional sensitivity evidence rather than a replacement for the pre-registered Nadeau–Bengio analysis.

No single pre-specified predictor block was shown to account for the incremental discrimination. However, the block-ablation design cannot distinguish distributed information from more subtle redundancy.

This study demonstrates unweighted predictive increments on one public four-year panel. It does not demonstrate clinical usefulness, clinical validity, deployment readiness, national performance, causal effects, or generalizability beyond MEPS Panel 24. Those claims would require a different study.

---

## Author contribution

The author is responsible for the research question, study design, cohort and leakage rules, predictor lock, validation and inferential plan, analysis-plan decisions, software implementation, repository organization, literature review, drafting of documentation and this manuscript, interpretation of results, and the scientific claims herein. Evaluation of whether analyses were complete, which contrasts were primary, and how findings should be bounded was the author’s responsibility. The author reviewed the analysis outputs, methods, and wording and remains responsible for errors.


---

## References

The literature discussion is a targeted review, not a PRISMA systematic review. Citations below are those used in this draft and documented in `docs/related_work.md`. Gao et al. (2018) is cited from the verified AJMC URL and PubMed record; a publisher DOI was not independently verified in that review.

AHRQ. *MEPS HC-245: Panel 24, 4-Year Longitudinal Public Use File*. https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml

Bobashev, G., Warren, L. K., & Wu, L.-T. (2021). Predictive model of multiple emergency department visits among adults: analysis of the data from the National Survey of Drug Use and Health (NSDUH). *BMC Health Services Research*. https://pubmed.ncbi.nlm.nih.gov/33766009/ DOI 10.1186/s12913-021-06221-w

Chiu, Y. M., Courteau, J., Dufour, I., Vanasse, A., & Hudon, C. (2023). Machine learning to improve frequent emergency department use prediction: a retrospective cohort study. *Scientific Reports, 13*, 1981. https://doi.org/10.1038/s41598-023-27568-6

Chiu, Y. M., Vanasse, A., Courteau, J., Chouinard, M.-C., Dubois, M.-F., Dubuc, N., Elazhary, N., Dufour, I., & Hudon, C. (2020). Persistent frequent emergency department users with chronic conditions: A population-based cohort study. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0229022

Fleishman, J. A., & Cohen, J. W. (2010). Using information on clinical conditions to predict high-cost patients. *Health Services Research, 45*(2), 532–552. https://doi.org/10.1111/j.1475-6773.2009.01080.x

Gao, K., Pellerin, G., & Kaminsky, L. (2018). Predicting 30-day emergency department revisits. *The American Journal of Managed Care, 24*(11), e358–e364. https://www.ajmc.com/view/predicting-30day-emergency-department-revisits PubMed 30452204.

Giannouchos, T. V., Kum, H.-C., Foster, M., & Ohsfeldt, R. L. (2019). Characteristics and predictors of adult frequent emergency department users in the United States: A systematic literature review. *Journal of Evaluation in Clinical Practice, 25*(3), 420–433. https://doi.org/10.1111/jep.13137

Hong, W. S., Haimovich, A. D., & Taylor, R. A. (2019). Predicting 72-hour and 9-day return to the emergency department using machine learning. *JAMIA Open, 2*(3), 346–352. https://doi.org/10.1093/jamiaopen/ooz019

Hunt, K. A., Weber, E. J., Showstack, J. A., Colby, D. C., & Callaham, M. L. (2006). Characteristics of frequent users of emergency departments. *Annals of Emergency Medicine, 48*(1), 1–8. https://doi.org/10.1016/j.annemergmed.2005.12.030

Krieg, C., Hudon, C., Chouinard, M.-C., et al. (2016). Individual predictors of frequent emergency department use: a scoping review. *BMC Health Services Research, 16*, 594. https://doi.org/10.1186/s12913-016-1852-1

Montoy, J. C. C., Tamayo-Sarver, J. H., Miller, G. A., Baer, A. B., & Peabody, C. R. (2019). Predicting emergency department “bouncebacks”: A retrospective cohort analysis. *Western Journal of Emergency Medicine*. https://doi.org/10.5811/westjem.2019.8.43221

Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. *Machine Learning, 52*, 239–281. https://doi.org/10.1023/A:1024068626366

Pereira, M., Singh, V., Hon, C. P., McKelvey, T. G., De Cock, M., & Sushmita, S. (2016). Predicting future frequent users of emergency departments in California State. In *Proceedings of the 7th ACM International Conference on Bioinformatics, Computational Biology, and Health Informatics* (BCB ’16). https://doi.org/10.1145/2975167.2985845

Stockbridge, E. L., Wilson, F. A., & Pagán, J. A. (2014). Psychological distress and emergency department utilization in the United States: Evidence from the Medical Expenditure Panel Survey. *Academic Emergency Medicine*. https://doi.org/10.1111/acem.12369

Wu, J., Grannis, S. J., Xu, H., & Finnell, J. T. (2016). A practical method for predicting frequent use of emergency department care using routinely available electronic registration data. *BMC Emergency Medicine, 16*, 12. https://doi.org/10.1186/s12873-016-0076-3
