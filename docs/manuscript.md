# Incremental Predictive Value of Pre-Cutoff Health, Access, Demographic, and Socioeconomic Information Beyond Three-Year Emergency Department History: A MEPS Panel 24 Analysis

Nikola Matus

Independent research

This manuscript reports a frozen, internally validated predictive comparison (analysis freeze v1.1.0). All numerical results are taken from saved repository outputs. Metrics are unweighted person-level predictive scores on the MEPS Panel 24 analytic sample. They are not national estimates, causal effects, clinical-utility estimates, or evidence that a model should be deployed.

---

## Abstract

**Background.** Future emergency-department (ED) use is known to be predictable from historical utilization. Less is established about how much incremental predictive information a broader pre-cutoff feature set adds beyond a multi-year ED-history baseline on a public four-year household panel.

**Objective.** To estimate, on the Medical Expenditure Panel Survey (MEPS) Panel 24 analytic sample, how much additional predictive value longitudinal health, utilization, access, demographic, and socioeconomic information provides beyond three-year ED history for predicting any ED use in the subsequent calendar year.

**Methods.** This was an observational, longitudinal, comparative predictive analysis of the Agency for Healthcare Research and Quality MEPS Household Component Panel 24 (public-use file HC-245; 2019–2022). The analytic cohort required unique person identifiers, presence in all four calendar years, and valid ED counts for 2019–2022 (N = 5,108; 693 events; prevalence 0.1357). The predictor cutoff was 31 December 2021. Round-specific predictors were taken from Round 6; Round 7 was unused because it extends into 2022. The outcome was any ED visit in calendar year 2022. The baseline model used three-year ED counts (2019–2021). The full model added pre-cutoff age, sex, race/ethnicity, region, marital status, perceived physical and mental health, insurance, usual source of care, poverty category, income, and employment. Both models were L2-regularized logistic regressions. Preprocessing was fitted within training folds. A 25% stratified split (n = 1,277) was a first-run internal evaluation set, not external validation. Primary inference used training-only repeated 5×5 cross-validation (25 paired fold differences) and a Nadeau–Bengio corrected comparison (df = 24) specified in the documented analysis plan. The study is not formally preregistered. Survey weights were not applied.

**Results.** Under the primary training-only analysis, the full model minus the ED-history baseline improved ROC-AUC by +0.0295 (95% Nadeau–Bengio CI +0.0045 to +0.0546; p = 0.0226) and PR-AUC by +0.0359 (+0.0140 to +0.0578; p = 0.0024). The Brier-score increment was −0.0017 (−0.0038 to +0.0004; p = 0.1110) and was not statistically detected (lower Brier is better). On the internal holdout, person-level bootstrap percentile 95% intervals (B = 2,000) for the same increments were 0.028 to 0.101 (ROC-AUC), 0.047 to 0.121 (PR-AUC), and −0.009 to −0.003 (Brier). An adult-only sensitivity did not detect the ROC increment (Δ = +0.0194; p = 0.113).

**Conclusions.** On this mixed-age analytic sample, pre-cutoff information beyond three-year ED history provided statistically detectable incremental discrimination in ROC-AUC and PR-AUC. The Brier increment was not statistically detected under the primary inference procedure. The study does not establish causal effects, preventability, clinical utility, external validity, or nationally representative performance.

---

## 1. Introduction

Emergency-department utilization is a long-standing subject of epidemiologic and predictive research. Across health-system registration data, hospital discharge records, administrative claims, and national surveys, later ED use can be predicted from historical utilization and other patient-level information (Wu et al., 2016; Pereira et al., 2016; Gao et al., 2018; Chiu et al., 2023; Stockbridge et al., 2014). Prior ED visits are repeatedly among the strongest predictors of later visits, including short-horizon revisits and next-year frequent use (Montoy et al., 2019; Chiu et al., 2020; Chiu et al., 2023; Wu et al., 2016; Krieg et al., 2016). Gao et al. (2018) reported a particularly clear discrimination increment when prior-year utilization was added to demographics for 30-day Veterans Affairs revisits.

That literature answers the first-order question of whether future ED use is predictable. It does not, by itself, answer a narrower incremental question: after a strong multi-year ED-history baseline is specified, how much additional discrimination is available from other information that is demonstrably known before a calendar-year cutoff?

The distinction between prediction and explanation matters here. Many studies include prior utilization as one covariate among others, compare algorithms on a full feature set, or model frequent use among people who already visited an ED. Association reviews document that public insurance, chronic illness, mental health problems, and poorer self-rated health are related to frequent ED use (Hunt et al., 2006; Krieg et al., 2016; Giannouchos et al., 2019). Those findings motivate richer feature sets, but they are not nested discrimination tests against an ED-history-only model. Short-horizon electronic health record studies of 72-hour to 30-day return visits establish operational revisit prediction, not next-year person-level any-ED use in a household survey (Hong et al., 2019; Montoy et al., 2019).

MEPS is designed as a nationally representative household panel with persistent person identifiers and annual utilization totals. That design property of the survey is distinct from this study’s unweighted analytic-sample estimand. MEPS has been used for longitudinal association with next-year ED use and for incremental prediction of high cost. Stockbridge, Wilson, and Pagán (2014) used MEPS Panel 14 to relate year-1 psychological distress, including year-1 ED counts, to year-2 ED use with survey-weighted hurdle models. That paper establishes that a time-ordered MEPS design can support next-year ED analysis; it does not report ROC-AUC, PR-AUC, or Brier increments versus an ED-history-only baseline. Fleishman and Cohen (2010) compared nested models for year-2 high expenditure on earlier two-year panels and found that health status added little after condition-based scores. That is an incremental prediction design for cost, not for any-ED visits.

The present study uses the AHRQ MEPS Panel 24 four-year longitudinal public-use file HC-245 (2019–2022). In a targeted, non-PRISMA review of PubMed, PMC, publisher sites, and AHRQ documentation (September 2026; approximately 70 titles screened and about 18 retained), no directly matching study was identified that compared an explicit multi-year ED-history-only baseline with a richer pre-cutoff demographic, health, access, and socioeconomic model for next-year any-ED use on MEPS Panel 24 / HC-245. That is a positioning statement about the literature reviewed. It is not a claim that no such study exists, that this is the first ED prediction study, or that this is the first MEPS ED study.

The contribution is incremental and methodological: a leakage-controlled, time-ordered comparison of a three-year ED-history baseline with a documented fuller feature set, evaluated with first-run internal holdout evaluation, repeated stratified cross-validation, Nadeau–Bengio inference specified in the documented analysis plan (Nadeau and Bengio, 2003), and leave-one-block-out ablation. Individual design elements are not claimed to be novel in isolation.

**Scientific question.** How much additional predictive value can longitudinal health, utilization, access, demographic, and socioeconomic information provide beyond historical ED utilization alone for predicting any ED use in the subsequent year?

This paper describes a frozen analysis. It is a predictive research study of one public-use panel. It is not a clinical prediction tool, a validated clinical model, a deployment-ready system, a national risk calculator, an ED-avoidance intervention, a preventability study, or a causal study.

---

## 2. Methods

### 2.1 Data source

The data source is the Agency for Healthcare Research and Quality (AHRQ) Medical Expenditure Panel Survey (MEPS), Household Component, Panel 24, four-year longitudinal public-use file HC-245, covering calendar years 2019–2022 (Rounds 1–9). The ingested file contained 5,565 persons and 5,321 variables. The person identifier is DUPERSID.

The analysis used a user-supplied official Stata file. The pipeline does not download from AHRQ and does not redistribute the microdata. HC-245 documentation is at:

https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml

The National Hospital Ambulatory Medical Care Survey was not used. It is visit-level and does not provide a persistent person identifier suitable for prior-to-future person-level prediction in this design.

Survey design variables LONGWT, VARSTR, and VARPSU were recorded at ingest and were not applied. ALL9RDS, the AHRQ subset flag for weighted national four-year estimates when used with LONGWT, was recorded and was not an inclusion criterion.

**Estimand.** Unweighted person-level predictive performance within the analytic sample, not a nationally representative MEPS population estimate.

### 2.2 Cohort

A person entered the analytic cohort when all of the following held:

1. Unique DUPERSID.
2. YEARIND = 1, indicating presence in the file for all four calendar years 2019–2022 (HC-245 documentation section 2.1.2).
3. Valid, non-missing, non-sentinel values of ERTOTY1, ERTOTY2, ERTOTY3, and ERTOTY4. Documented MEPS codes −1, −7, −8, and −9 are examples; any negative, including codes outside that named set (for example EMPST6 = −15), was treated as non-usable.

The resulting analytic sample is N = 5,108, with 693 any-ED events in 2022 (prevalence 0.13567). The raw file contained 5,565 unique persons. ALL9RDS = 1 on the raw file was 4,883; the intersection with the analytic cohort was also 4,883. Persons with 1, 2, 3, or 4 observed years on the raw file numbered 191, 160, 106, and 5,108.

Persons with YEARIND ≠ 1, including many births, late entrants, and deaths or institutionalization before 2022, were excluded. Thirty-seven persons with YEARIND = 1 who died remained in the primary cohort because a valid 2022 ED total was observed while they were in scope. A later sensitivity analysis dropped those decedents; it did not replace the primary cohort.

The unit of analysis is the person. Results describe this constructed analytic sample, not the U.S. civilian noninstitutionalized population as a weighted survey estimate. Table 1 reports the cohort flow. Sex, race/ethnicity, and related demographic distributions are not reported as a conventional Table 1 because those summaries are not stored in the frozen outputs; they were not manufactured.

### 2.3 Outcome

The primary outcome is any ED visit in calendar year 2022, coded 1 if ERTOTY4 ≥ 1 and 0 otherwise. ERTOTY4 is never a predictor.

A secondary construct, ERTOTY4 ≥ 2, was counted for inspection only: 209 events in the analytic cohort (prevalence 0.04092). It was not modeled and was not used for inference.

### 2.4 Predictor information and temporal cutoff

The time origin and prediction cutoff is 31 December 2021. The outcome window is calendar year 2022. Panel 24 comprises nine interview rounds over 2019–2022. Round-specific predictors used in the model are Round 6 items (2021). Calendar-year predictors are year-1 through year-3 fields. Round 7 was excluded because it extends into 2022. Rounds 8–9 and year-4 names cannot enter the predictor set. Earlier rounds contribute only through pre-2022 annual totals or time-invariant characteristics, not through later-round names. The study is observational and time-ordered; it is not prospective follow-up of a newly enrolled clinical cohort.

**ED-history baseline.** ERTOTY1, ERTOTY2, and ERTOTY3 (emergency-room visit counts in 2019, 2020, and 2021).

**Full model.** Age as of 31 December 2021, sex, race/ethnicity, census region, Round 6 marital status, Round 6 perceived physical and mental health, 2021 insurance coverage, Round 6 usual source of care, 2021 poverty category, 2021 person income, Round 6 employment status, and the three ED-history counts. Confirmed HC-245 longitudinal names were used; full-year consolidated aliases were not used.

Homelessness, substance-use disorder, and food insecurity were not represented as such. Related items that exist on HC-245 were not used and were not relabeled as those constructs.

A fail-closed temporal leakage procedure excluded post-cutoff and temporally uncertain variables, with explicit checks for year-4 and later-round fields. Predictors were required to be demonstrably available in 2021 or earlier, or time-invariant.

**Family B blocks** (each removed from the full model, one at a time):

| ID | Block removed | Contents |
|---|---|---|
| B1 | Age | Age as of 31 December 2021 |
| B2 | Demographics | Sex, race/ethnicity, region, marital status (age retained) |
| B3 | Health | Perceived physical and mental health |
| B4 | Access | Insurance coverage and usual source of care |
| B5 | Socioeconomic | Poverty category, income, and employment |

### 2.5 Models

All models are L2-regularized logistic regressions (penalty C = 1.0). Hyperparameters were not tuned. No tree ensemble, survival model, or sequence model was added after the first-run model.

Three baselines were scored on the locked holdout: (1) prevalence only, a constant probability equal to the training prevalence; (2) prior-year ED only (2021 counts); and (3) three-year ED history. The inferential comparator is baseline 3. The full model uses the production predictor set with the same estimator class. This is regularized logistic regression, not an algorithm-competition study.

### 2.6 Preprocessing and missingness

MEPS sentinel codes −1, −7, −8, and −9, and any other negative, are recoded to missing. They are never passed through as numeric measurements. The named sentinel list is not exhaustive. Missingness is not used as a predictor; no missingness indicators were added.

Preprocessing is fitted on the training fold only: median imputation and standard scaling for numeric fields; most-frequent imputation and one-hot encoding for categorical fields (no reference level dropped). This is single imputation, not multiple imputation.

On the analytic cohort, EMPST6 is non-usable for 818 of 5,108 persons (16.01%): 801 coded −1, 9 coded −7, 2 coded −8, and 6 coded −15. Of those non-usable observations, 96.5% were among participants under 16 years of age, consistent with structural inapplicability of employment rather than sporadic item nonresponse. Those values are represented through modal imputation (modal valid category: employed) rather than an explicit inapplicable category. The EMPST6 coefficient should not be interpreted as a clean causal employment effect. The adult-only sensitivity is a related population check.

### 2.7 Train/holdout split and repeated cross-validation

A person-level stratified 25% split (seed 42, stratified on the binary 2022 outcome) produced a training portion of n = 3,831 and a holdout of n = 1,277 (173 events; prevalence 0.13547).

That split is a first-run, development-stage internal evaluation set. It was scored during original model fitting and was used during development for a research-triage decision. It was not used to choose predictors, tune regularization, choose Family A/B hypotheses, or compute inferential p-values. It is not an external, pristine, or independently confirmatory sample.

Repeated cross-validation left that holdout unused and applied 5 repeats × 5 stratified folds (seed 2021) on the training portion only. Preprocessing and the classifier were refit inside each training fold. This produced 25 paired fold-level estimates of ED-history versus full-model performance. The 25 folds are not treated as 25 independent observations. The 2.5th–97.5th percentiles of fold-level differences are descriptive empirical ranges, not conventional confidence intervals.

### 2.8 Performance metrics

Primary reported metrics are ROC-AUC, PR-AUC, and Brier score. PR-AUC is reported alongside ROC-AUC because the outcome is relatively uncommon (analytic prevalence 0.1357). Brier score is a proper scoring rule for probabilistic accuracy; **lower is better**. Differences are Full − ED-history, so a negative ΔBrier favors the full model.

Threshold-dependent metrics at probability 0.5 were computed on the holdout as exploratory descriptive metrics only. They are not an optimized or clinical operating point.

### 2.9 Statistical inference

Inference reads saved fold-level results and does not refit models.

The plan-specified test is the Nadeau–Bengio corrected resampled t-test (Nadeau and Bengio, 2003):

\[
\mathrm{Var}_{NB}(\bar{d}) = \left(\frac{1}{n} + \frac{n_{\mathrm{test}}}{n_{\mathrm{train}}}\right) s^{2},
\quad
t = \frac{\bar{d}}{\sqrt{\mathrm{Var}_{NB}}},
\quad
\mathrm{df} = n - 1
\]

where \(s^{2}\) is the unbiased sample variance of the n paired fold-level differences, n = 25, and the test/train ratio is the empirical validation-to-training size used by the implementation (saved value 0.250000), with df = 24. Tests are two-sided at α = 0.05. This is not the naive standard error \(s / \sqrt{25}\).

**Family A** uses the unadjusted Nadeau–Bengio p-value for each of ROC-AUC, PR-AUC, and Brier. The documented analysis plan described Family A as one primary contrast (Full − ED-history) and did not apply Holm inside Family A. The three metrics are complementary rather than interchangeable. ROC p = 0.0226 would not survive a simple Bonferroni correction across the three metrics, while PR p = 0.0024 would. That correction was not applied, because it was not specified in the plan and would be result-dependent.

**Family B** applies Holm–Bonferroni separately within ROC-AUC, PR-AUC, and Brier across the five leave-one-block-out contrasts (Holm, 1979). Holm is not applied across families or across metrics.

A repeat-level one-sample t-test of the five repeat means (df = 4) is a descriptive robustness diagnostic. Because the same training sample is reused across repeats, its nominal uncertainty is understated and its p-values can be smaller than the primary Nadeau–Bengio estimates. The primary inference remains the Nadeau–Bengio result.

### 2.10 Holdout bootstrap

Uncertainty for first-run holdout increments used a person-level paired bootstrap of outcome and predicted-probability pairs with B = 2,000, seed 20210915, and percentile intervals. Zero degenerate replicates were skipped. This is an internal holdout evaluation and bootstrap uncertainty assessment, not external validation.

### 2.11 Calibration

Calibration for the first-run full model includes a quantile-binned reliability diagram and a Cox logistic calibration assessment on the entire first-run holdout. Predicted probabilities were not recalibrated. Calibration-in-the-large (CITL) is the intercept with slope fixed at 1. Overall event-rate calibration was close. A slope greater than 1 indicates some compression of predicted risks toward the mean; it is not characterized here as severe miscalibration.

### 2.12 Variance inflation factors

A production encoding that does not drop a one-hot reference level produces invalid infinite VIFs for categorical dummies (dummy-variable trap). A diagnostic VIF after dropping a reference level on the training portion is reported. That diagnostic is descriptive only. VIF was never used to remove predictors.

### 2.13 Sensitivity analyses

Labeled sensitivities, none of which replace the mixed-age primary analysis:

- Death: drop decedents from holdout evaluation or refit after excluding in-scope decedents.
- Adult-only: restrict the original split to persons aged ≥18 years.
- ALL9RDS: restrict the original split to complete nine-round interview participation.
- Exclude 2020 ED counts: drop ERTOTY2 from both nested models.
- Exploratory adult age ablation (post-primary): remove age within the adult subset. This is exploratory and is not used to explain the adult full-versus-ED result.

An earlier exploratory analysis added predictor families one at a time to ED history on the locked holdout. Adding a family to ED history is not the same contrast as removing that block from the full model.

### 2.14 Survey weights

The analysis did not apply MEPS survey weights. The estimand is unweighted person-level predictive performance within the analytic sample rather than a nationally representative MEPS population estimate.

### 2.15 Reproducibility and analysis-plan provenance

The contrast set, Family A / Family B structure, Holm plan, estimator, cohort, outcome, seeds, and the rule that inference would wait until access and socioeconomic ablations existed are recorded in a repository analysis-plan file that entered Git on 2026-09-12. That file is a documented analysis plan, not a formal preregistration. Git history is evidence of repository history, not complete research history. The study is not described as formally preregistered.

Seeds: holdout and logistic regression, 42; repeated cross-validation, 2021; holdout bootstrap, 20210915. Software environment is recorded with the v1.1 freeze. The first-run analysis command overwrites locked holdout artifacts and should not be re-run against this completed analysis.

Reporting was informed by TRIPOD, TRIPOD+AI, and PROBAST concepts (Collins et al., 2015, 2024; Wolff et al., 2019) without a claim of formal compliance.

---

## 3. Results

All numbers below are unweighted analytic-sample metrics from saved outputs.

### 3.1 Cohort

Table 1 summarizes cohort construction. Analytic N = 5,108; 693 events; prevalence 0.13567; training n = 3,831; holdout n = 1,277 with 173 events. Figure 1 shows the temporal structure.

**Table 1.** Analytic cohort construction (unweighted). Demographic distributions are omitted because they are not stored as frozen summary tables.

| Step / quantity | N | Notes |
|---|---:|---|
| Raw HC-245 extract | 5,565 | Unique persons; 5,321 variables |
| Persons with 1 / 2 / 3 observed years (raw) | 191 / 160 / 106 | Not eligible under YEARIND = 1 |
| Analytic cohort (YEARIND = 1, valid ED counts 2019–2022) | 5,108 | |
| 2022 any-ED events | 693 | Prevalence 0.13567 |
| ≥2 ED visits in 2022 (not modeled) | 209 | Prevalence 0.04092 |
| ALL9RDS = 1 | 4,883 | Not an inclusion criterion |
| Aged <18 years | 898 | Adult-only sensitivity denominator |
| In-scope decedents remaining | 37 | 28 train / 9 holdout |
| Training / first-run holdout | 3,831 / 1,277 | Holdout 173 events; prevalence 0.13547 |

### 3.2 Primary comparison (Family A)

Table 2 and Figure 2 report the primary training-only comparison. Mean cross-validated ROC-AUC was 0.6848 (ED history) versus 0.7143 (full). Mean PR-AUC was 0.3067 versus 0.3426. Mean Brier was 0.1077 versus 0.1060. Increments (Full − Baseline) were +0.0295 ROC-AUC (95% CI +0.0045 to +0.0546; p = 0.0226), +0.0359 PR-AUC (+0.0140 to +0.0578; p = 0.0024), and −0.0017 Brier (−0.0038 to +0.0004; p = 0.1110).

ROC-AUC and PR-AUC provide evidence of incremental discrimination on this analytic sample. The Brier-score increment was not statistically detected under the primary inference procedure. Lower Brier is better; the Brier result is not described as significant, and the study does not claim an overall improvement in prediction error.

Fold-level directional counts (descriptive): 23/25 positive ΔROC, 24/25 positive ΔPR, 19/25 Brier improved.

**Table 2.** Primary model comparison, training-only 5×5 cross-validation. Increments are Full − Baseline. Lower Brier is better. Family A p-values are unadjusted.

| Metric | Baseline | Full | Increment | 95% CI | Unadjusted *p* |
|---|---:|---:|---:|---|---:|
| ROC-AUC | 0.6848 | 0.7143 | +0.0295 | +0.0045 to +0.0546 | 0.0226 |
| PR-AUC | 0.3067 | 0.3426 | +0.0359 | +0.0140 to +0.0578 | 0.0024 |
| Brier | 0.1077 | 0.1060 | −0.0017 | −0.0038 to +0.0004 | 0.1110 |

### 3.3 Internal holdout and bootstrap

On the first-run holdout (n = 1,277), three-year ED history achieved ROC-AUC 0.709, PR-AUC 0.331, and Brier 0.105; the full model achieved 0.774, 0.416, and 0.099. Holdout increment, full minus three-year ED history: +0.065 ROC-AUC, +0.085 PR-AUC, −0.006 Brier.

Person-level bootstrap percentile 95% intervals (B = 2,000, seed 20210915; 0 degenerate replicates): ΔROC-AUC 0.028 to 0.101; ΔPR-AUC 0.047 to 0.121; ΔBrier −0.009 to −0.003.

The holdout increment is larger than the repeated-CV mean and should be read as one internal split, not as the expected effect size and not as external confirmation. Inferential p-values come from training-only cross-validation.

Prior-year ED only scored holdout ROC-AUC 0.627; prevalence-only scored 0.500. Those are descriptive nested baselines, not Family A hypotheses. Threshold metrics at probability 0.5 are exploratory only (full-model sensitivity 0.104, specificity 0.995).

### 3.4 Calibration

On the first-run holdout, the full model’s mean predicted probability was 0.134892 and the observed event rate was 0.135474. CITL was approximately 0.006; the calibration slope was approximately 1.237. Overall event-rate calibration was close. Slope > 1 indicates some compression of predicted risks toward the mean, compatible with L2 shrinkage. This is not characterized as severe miscalibration. Probabilities were not recalibrated. Figure 3 shows the quantile reliability diagram with these statistics annotated.

### 3.5 Block ablations (Family B)

No leave-one-block-out contrast was statistically detected after Holm correction within each metric (Table 3). No single documented predictor block was shown to account for the increment. The block-ablation design cannot distinguish distributed information from more subtle redundancy. Non-significant Family B tests are not evidence that reduced models are equivalent to the full model or that any block can be dropped. Remaining cross-validated mean ROC increments versus ED history after each removal stayed in a similar range (approximately +0.024 to +0.036). Blocks are not ranked.

**Table 3.** Family B contrasts (reduced − full), Holm-adjusted within metric. Detected at 0.05: none.

| Contrast | ROC Δ (Holm *p*) | PR Δ (Holm *p*) | Brier Δ (Holm *p*) |
|---|---|---|---|
| B1 No-age − Full | −0.0051 (0.872) | −0.0017 (1.000) | +0.0002 (1.000) |
| B2 No-demographics − Full | +0.0062 (0.872) | −0.0002 (1.000) | +0.0000 (1.000) |
| B3 No-health − Full | +0.0049 (1.000) | +0.0042 (1.000) | −0.0004 (1.000) |
| B4 No-access − Full | −0.0018 (1.000) | −0.0017 (1.000) | +0.0002 (0.928) |
| B5 No-SES − Full | +0.0019 (1.000) | +0.0065 (0.702) | −0.0006 (0.807) |

An exploratory holdout add-on analysis found the largest single-family increment when demographics were added to ED history (holdout ΔROC +0.043). That contrast is not interchangeable with Family B and is reported as supplementary internal evaluation only.

### 3.6 Sensitivity analyses

Table 4 and Figure 4 summarize labeled sensitivities. None replaces the mixed-age primary analysis.

**Adult-only** (age ≥18 years; 898 persons under 18 excluded; train 3,162; holdout 1,048 with 166 events): ΔROC-AUC +0.0194 (p = 0.113); ΔPR-AUC +0.0299 (p = 0.0029); ΔBrier −0.0014 (p = 0.196). The primary mixed-age ROC finding was not demonstrated in adults alone.

**Exploratory adult age ablation** (post-primary): No-age minus Full ΔROC-AUC −0.0022 (p = 0.637). Age did not show a statistically detected incremental contribution among adults. This diagnostic is not used to explain the adult full-versus-ED ROC result.

**ALL9RDS = 1** (train 3,663; holdout 1,220): ΔROC +0.0311 (p = 0.0168); ΔPR +0.0381 (p = 0.0073); ΔBrier −0.0018 (p = 0.120). Directionally unchanged; not adopted as primary.

**Exclude 2020 ED counts:** the ED-history baseline was weaker (holdout ROC-AUC 0.684 versus 0.709 with three-year history), so the increment was larger (ΔROC +0.0460, p = 0.0006). That is expected when a year of ED counts is removed from the comparator. It does not replace the three-year baseline.

**Death sensitivity.** Dropping nine decedents from the original holdout changed full-model ROC-AUC from 0.774 to 0.772. Refitting after dropping 28 training and 9 test decedents gave ROC-AUC 0.771. The primary cohort was not replaced.

### 3.7 VIF diagnostic

The corrected drop-first diagnostic on the training portion produced 40 finite VIF values, maximum approximately 3.68, and no VIF > 5. VIF was diagnostic only and was not used to remove predictors. Pairwise association flags included age with marital status (η = 0.8099) and poverty category with income (η = 0.5975). The diagnostic does not prove independence.

### 3.8 Repeat-level diagnostic

Averaging the 25 Family A fold deltas within each of five repeats yielded smaller p-values (ROC p = 0.0003; PR p = 0.0003; Brier p = 0.0006; df = 4) than Nadeau–Bengio. Those smaller p-values understate uncertainty because repeats share the training sample. Repeat-level Brier “significance” does not overturn the primary Brier result (p = 0.1110).

---

## 4. Discussion

### 4.1 Principal finding

The principal finding is incremental, not absolute. Three-year ED history already discriminated 2022 any-ED use on this analytic sample (holdout ROC-AUC 0.709; cross-validated mean 0.685). That is consistent with a large literature in which prior ED use is a dominant predictor (Gao et al., 2018; Montoy et al., 2019; Chiu et al., 2023; Wu et al., 2016). The question addressed here is what remains after that baseline is specified.

On the mixed-age analytic sample, adding documented pre-cutoff health, access, demographic, and socioeconomic information produced statistically detectable incremental ROC-AUC and PR-AUC under the plan-specified Nadeau–Bengio analysis. The increments are modest in absolute terms (about +0.03 ROC-AUC and +0.04 PR-AUC on repeated cross-validation). They should not be oversold as a highly accurate prediction system.

### 4.2 What incremental discrimination means

Incremental discrimination means that, for this estimator class and this sample, ranking of persons by predicted risk of any next-year ED use improved somewhat when the fuller pre-cutoff feature set was added to three-year ED counts. It does not establish that those features cause ED use, that ED visits are preventable, that an intervention targeting high predicted risk would reduce utilization, that the model is ready for clinical decision support, or that performance would hold in another panel, claims file, or health system.

### 4.3 Brier score

The Brier increment was directionally favorable (lower Brier is better) and was not statistically detected under the primary inference procedure. The study therefore does not claim an overall improvement in prediction error. Family A reports three complementary metrics without multiplicity correction; a reader applying Bonferroni across the three tests would retain the PR-AUC result and not the ROC-AUC result. That correction was not applied retroactively.

### 4.4 Why a strong ED-history baseline matters

The first-run holdout increment exceeded the repeated-CV mean. That split is one internal evaluation, not an expected effect size and not external confirmation. Bootstrap intervals on the holdout quantify resampling uncertainty for that split; they do not convert the holdout into an independent test set.

A weak baseline can make additional covariates look more informative than they are. The three-year ED-history model already outperformed both a prevalence-only classifier and a single prior-year ED count on the internal holdout. Incremental claims in this paper are therefore claims about information beyond that strong comparator, not about whether next-year ED use is predictable at all.

### 4.5 Adult-only result

The adult-only sensitivity did not detect the ROC increment while still detecting PR-AUC. The mixed-age Family A ROC finding therefore should not be presented as demonstrated for adults alone. Structural inapplicability of employment (and some other items) among children is a population-definition issue, not a reason to silently drop children from the locked primary cohort. An exploratory adult-only drop of age did not detect a change versus the adult full model; that diagnostic is not used to explain the adult full-versus-ED result.

ALL9RDS restriction did not change the discrimination conclusion. Excluding 2020 ED counts weakened the history baseline and enlarged the increment; that is a change of comparator, not stronger evidence for the original question.

### 4.6 Predictor blocks

Leave-one-block-out results did not identify a single block whose removal statistically accounted for the increment. Remaining cross-validated mean ROC increments versus ED history stayed in a similar range after each removal. No single documented predictor block was shown to account for the incremental discrimination. The block-ablation design cannot distinguish distributed information from more subtle redundancy, and it does not establish which family causes or drives ED utilization.

### 4.7 Relation to prior work

This study is closest, among papers in the targeted review, to incremental-information designs rather than algorithm bake-offs. Gao et al. (2018) quantified utilization increments for 30-day VA revisits among recent ED users. Stockbridge et al. (2014) used a two-year MEPS panel for survey-weighted association with next-year ED use. Fleishman and Cohen (2010) nested incremental models for high cost. Chiu et al. (2023) found that prior-year ED visits dominated algorithm comparisons for frequent use. The present analysis differs in panel, outcome (any 2022 ED visit among four-year participants), baseline (explicit three-year ED-history-only model), metric set, and inferential procedure. Those differences are design differences, not claims of superiority in real-world healthcare populations.

### 4.8 Implications for future prediction research

Implications for future prediction research, rather than for immediate clinical use, include: (i) specifying a strong utilization-history baseline before attributing performance to richer social or health features; (ii) keeping temporal cutoffs fail-closed; (iii) reporting ROC, PR, and a proper scoring rule together; (iv) treating mixed-age survey items with structurally inapplicable fields as a population-definition problem; and (v) validating on later panels or external data before any operational claim.

---

## 5. Limitations

These limitations apply regardless of which tests were statistically detected.

1. **Unweighted analytic-sample metrics.** ROC-AUC, PR-AUC, and Brier values describe the constructed MEPS Panel 24 analytic sample. They are not survey-weighted population estimates and do not imply national representativeness.

2. **No national inference.** Survey design variables were recorded and not applied.

3. **Single-panel, internal validation.** All modeling uses Panel 24. The 25% split is a first-run internal evaluation set. There is no external or later-panel test set.

4. **Not prospective.** The design is time-ordered and observational. Participants were not enrolled for prediction and then followed independently.

5. **COVID-era panel.** Panel 24 overlaps COVID-19. AHRQ documents comparability concerns related to phone-based interviewing.

6. **MEPS population coverage.** MEPS-HC samples the U.S. civilian noninstitutionalized population. It excludes incarcerated people, active-duty military, and institutionalized populations, and structurally undersamples people experiencing homelessness.

7. **Model class.** The estimator is L2-regularized logistic regression with fixed regularization. Incremental discrimination is specific to this estimator class.

8. **Single imputation without missingness indicators.** Sentinels and any other negatives are recoded to missing, then median or most-frequent imputed inside each fold. EMPST6 non-usable values (16.01%) are overwhelmingly structurally inapplicable for children and are mode-imputed (employed). Those coefficients are not causal employment effects.

9. **Mortality.** Competing risk of death is not modeled. Thirty-seven in-scope decedents remain in the primary cohort.

10. **Outcome definition.** The outcome is any self- or proxy-reported ED visit in 2022. It is not claims-adjudicated utilization, acuity, or avoidable versus unavoidable ED use.

11. **Two or more ED visits not modeled.** The high-utilizer construct was counted (209 events) and not modeled.

12. **Children and adults mixed in the primary analysis.** The adult-only ROC increment was not detected (p = 0.113). The primary Family A ROC result should not be generalized as an adult-only finding.

13. **No clinical utility analysis.** No decision-curve, net-benefit, or intervention-impact analysis was performed. Metrics at probability 0.5 are exploratory.

14. **No causal interpretation.** Ablation deltas are predictive associations, not effects of intervening on a block.

15. **Family A reports three metrics without multiplicity correction.** ROC p = 0.0226 would not survive Bonferroni ×3; PR would. That correction was not applied.

16. **Analysis plan is documented, not formally preregistered.** Git incorporation on 2026-09-12 does not date local plan creation. Locked v1.0 generated summaries may still contain historical “pre-registered” wording; those artifacts were not rewritten.

17. **Targeted literature review.** Absence of a paper from the targeted review does not prove that no such paper exists.

18. **Calibration and VIF are internal diagnostics.** They do not convert the holdout into external validation and were not used to change the model.

---

## 6. Conclusion

On the MEPS Panel 24 mixed-age analytic sample, under a locked cohort, predictor set, regularized logistic estimator, and plan-specified Nadeau–Bengio analysis, the full pre-cutoff feature set showed statistically detectable incremental ROC-AUC and PR-AUC versus three-year ED history. The Brier increment was directionally favorable and was not statistically detected. Incremental discrimination on an unweighted internal evaluation is a narrower claim than clinical usefulness, causal explanation, preventability, or national prediction performance. Those claims would require a different study.

---

## 7. Data, code, and reproducibility statement

Code, tests, documentation, and saved outputs are in the public repository (analysis tag v1.1.0). Original code and documentation are released under the MIT License. That license does not grant rights to AHRQ MEPS microdata.

HC-245 is an AHRQ public-use file. This repository does not redistribute the microdata. Researchers must obtain the official Stata-format file from AHRQ and follow AHRQ public-use conditions, including not attempting to identify individuals. Cite AHRQ and the Medical Expenditure Panel Survey as the data source.

Dependencies are declared in the project metadata (Python ≥ 3.10; pandas, numpy, scikit-learn, scipy, matplotlib). A number-by-number mapping from this manuscript to frozen output files is in `docs/manuscript_number_audit.md`. The first-run analysis command overwrites locked holdout artifacts and should not be re-run against this completed analysis.

---

## 8. Supplementary material

Publication figures (redrawn from frozen outputs; locked first-run figures were not overwritten):

- **Figure 1.** Temporal structure of the prediction problem.
- **Figure 2.** Primary cross-validation increments with Nadeau–Bengio 95% confidence intervals.
- **Figure 3.** Calibration on the first-run internal holdout (not external validation).
- **Figure 4.** ROC increment under the primary analysis and labeled sensitivities (sensitivities are not confirmatory replacements).

Full-precision tables, EMPST6 code breakdown, environment freeze, and historical first-run figures are in the repository supplementary files. Figure files: `docs/figures/`.

---

## Author contribution

The author is responsible for the research question, study design, cohort and leakage rules, predictor lock, validation and inferential plan, analysis-plan decisions, software implementation, repository organization, literature review, drafting of documentation and this manuscript, interpretation of results, and the scientific claims herein. Evaluation of whether analyses were complete, which contrasts were primary, and how findings should be bounded was the author’s responsibility. The author reviewed the analysis outputs, methods, and wording and remains responsible for errors.

---

## References

The literature discussion is a targeted review, not a PRISMA systematic review. Gao et al. (2018) is cited from the verified AJMC URL and PubMed record; a publisher DOI was not independently verified.

AHRQ. *MEPS HC-245: Panel 24, 4-Year Longitudinal Public Use File*. https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml

Bobashev, G., Warren, L. K., & Wu, L.-T. (2021). Predictive model of multiple emergency department visits among adults: analysis of the data from the National Survey of Drug Use and Health (NSDUH). *BMC Health Services Research*. https://doi.org/10.1186/s12913-021-06221-w

Chiu, Y. M., Courteau, J., Dufour, I., Vanasse, A., & Hudon, C. (2023). Machine learning to improve frequent emergency department use prediction: a retrospective cohort study. *Scientific Reports, 13*, 1981. https://doi.org/10.1038/s41598-023-27568-6

Chiu, Y. M., Vanasse, A., Courteau, J., Chouinard, M.-C., Dubois, M.-F., Dubuc, N., Elazhary, N., Dufour, I., & Hudon, C. (2020). Persistent frequent emergency department users with chronic conditions: A population-based cohort study. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0229022

Collins, G. S., Reitsma, J. B., Altman, D. G., & Moons, K. G. M. (2015). Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis (TRIPOD): the TRIPOD statement. *BMJ, 350*, g7594. https://doi.org/10.1136/bmj.g7594

Collins, G. S., Moons, K. G. M., Dhiman, P., et al. (2024). TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378. https://doi.org/10.1136/bmj-2023-078378

Fleishman, J. A., & Cohen, J. W. (2010). Using information on clinical conditions to predict high-cost patients. *Health Services Research, 45*(2), 532–552. https://doi.org/10.1111/j.1475-6773.2009.01080.x

Gao, K., Pellerin, G., & Kaminsky, L. (2018). Predicting 30-day emergency department revisits. *The American Journal of Managed Care, 24*(11), e358–e364. https://www.ajmc.com/view/predicting-30day-emergency-department-revisits PubMed 30452204. Publisher DOI not independently verified.

Giannouchos, T. V., Kum, H.-C., Foster, M., & Ohsfeldt, R. L. (2019). Characteristics and predictors of adult frequent emergency department users in the United States: A systematic literature review. *Journal of Evaluation in Clinical Practice, 25*(3), 420–433. https://doi.org/10.1111/jep.13137

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://doi.org/10.2307/4615733

Hong, W. S., Haimovich, A. D., & Taylor, R. A. (2019). Predicting 72-hour and 9-day return to the emergency department using machine learning. *JAMIA Open, 2*(3), 346–352. https://doi.org/10.1093/jamiaopen/ooz019

Hunt, K. A., Weber, E. J., Showstack, J. A., Colby, D. C., & Callaham, M. L. (2006). Characteristics of frequent users of emergency departments. *Annals of Emergency Medicine, 48*(1), 1–8. https://doi.org/10.1016/j.annemergmed.2005.12.030

Krieg, C., Hudon, C., Chouinard, M.-C., et al. (2016). Individual predictors of frequent emergency department use: a scoping review. *BMC Health Services Research, 16*, 594. https://doi.org/10.1186/s12913-016-1852-1

Montoy, J. C. C., Tamayo-Sarver, J. H., Miller, G. A., Baer, A. B., & Peabody, C. R. (2019). Predicting emergency department “bouncebacks”: A retrospective cohort analysis. *Western Journal of Emergency Medicine, 20*, 865–874. https://doi.org/10.5811/westjem.2019.8.43221

Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. *Machine Learning, 52*, 239–281. https://doi.org/10.1023/A:1024068626366

Pereira, M., Singh, V., Hon, C. P., McKelvey, T. G., De Cock, M., & Sushmita, S. (2016). Predicting future frequent users of emergency departments in California State. In *Proceedings of the 7th ACM International Conference on Bioinformatics, Computational Biology, and Health Informatics* (BCB ’16). https://doi.org/10.1145/2975167.2985845

Stockbridge, E. L., Wilson, F. A., & Pagán, J. A. (2014). Psychological distress and emergency department utilization in the United States: Evidence from the Medical Expenditure Panel Survey. *Academic Emergency Medicine*. https://doi.org/10.1111/acem.12369

Wolff, R. F., Moons, K. G. M., Riley, R. D., Whiting, P. F., Westwood, M., Collins, G. S., Reitsma, J. B., Kleijnen, J., & Mallett, S. (2019). PROBAST: A tool to assess the risk of bias and applicability of prediction model studies. *Annals of Internal Medicine, 170*(1), 51–58. https://doi.org/10.7326/M18-1376

Wu, J., Grannis, S. J., Xu, H., & Finnell, J. T. (2016). A practical method for predicting frequent use of emergency department care using routinely available electronic registration data. *BMC Emergency Medicine, 16*, 12. https://doi.org/10.1186/s12873-016-0076-3
