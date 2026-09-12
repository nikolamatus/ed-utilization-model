# Results

Authoritative narrative of the **saved** findings. Numbers are taken
from files under `outputs/`. This is unweighted predictive performance
on the MEPS Panel 24 analytic sample. It is not national performance,
clinical utility, causality, or deployment evidence.

The 2.5th–97.5th fold-delta ranges below are **descriptive empirical
distributions of fold-level differences**. They are not conventional
confidence intervals. Fold-level observations are correlated; inferential
analysis therefore uses the Nadeau–Bengio corrected t-test rather than
naive fold-level variance.

---

## A. Cohort

Source: `outputs/feasibility_summary.json`,
`outputs/population_summary.csv`, `outputs/years_observed.csv`,
`outputs/death_sensitivity.csv`.

| Quantity | Value |
|---|---:|
| Raw file N | 5,565 persons (5,321 variables) |
| Unique `DUPERSID` | 5,565 (0 duplicates) |
| `YEARIND == 1` | 5,108 |
| Analytic N | **5,108** |
| 2022 any-ED events (`ERTOTY4 ≥ 1`) | **693** |
| Analytic prevalence | **0.13567** |
| `ALL9RDS == 1` (raw file) | 4,883 |
| Analytic ∩ `ALL9RDS == 1` | 4,883 |
| ≥2 ED visits in 2022 (descriptive only) | 209 (prevalence 0.04092) |
| `YEARIND == 1` decedents remaining in cohort | 37 |
| Persons with 1 / 2 / 3 / 4 observed years (raw) | 191 / 160 / 106 / 5,108 |

Locked holdout (25%, seed 42): **n = 1,277**, **173** events,
prevalence 0.13547. Training portion: **n = 3,831**.

Weights applied: **false**.

---

## B. Baseline and full holdout results

Source: `outputs/model_metrics.csv`. Threshold metrics at 0.5 are
exploratory only and are not interpreted as an operating point.

| Model | n_test | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|---:|
| Prevalence only | 1,277 | 0.500000 | 0.135474 | 0.117121 |
| Prior-year ED (`ERTOTY3`) | 1,277 | 0.627340 | 0.251424 | 0.108442 |
| 3-year ED history | 1,277 | 0.709095 | 0.330794 | 0.105286 |
| Full regularized logistic | 1,277 | 0.774006 | 0.415935 | 0.099390 |

Holdout increment, full minus 3-year ED history: **+0.064911 ROC-AUC**,
**+0.085141 PR-AUC**, Brier **−0.005896**.

The first-run research triage gate recorded GREEN
(`outputs/feasibility_summary.json`). That gate is not a statistical
test and is not a claim of clinical readiness.

Calibration: quantile-binned mean predicted vs observed fractions are
in `outputs/calibration.csv` for the first-run full model. The table
shows the usual pattern that predicted risk is imperfectly aligned with
observed event rates across deciles; it is a descriptive reliability
check, not a recalibration analysis.

Death sensitivity (`outputs/death_sensitivity.csv`): dropping 9
decedents from the original test fold changed full-model ROC-AUC from
0.774006 to 0.772214. Refitting after dropping 28 train and 9 test
decedents gave ROC-AUC 0.770905. The change was not treated as material
and did not replace the primary cohort.

---

## C. Repeated cross-validation

Source: `outputs/repeated_cv_summary.csv` (training portion only;
holdout unused; 5×5, seed 2021).

### Absolute metrics (25 folds)

| Metric | Mean | SD | Median | Min | Max | p2.5 | p97.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ED-history ROC-AUC | 0.6848 | 0.0327 | 0.6847 | 0.6163 | 0.7323 | 0.6231 | 0.7306 |
| ED-history PR-AUC | 0.3067 | 0.0358 | 0.3171 | 0.2424 | 0.3664 | 0.2443 | 0.3616 |
| ED-history Brier | 0.1077 | 0.0030 | 0.1071 | 0.1023 | 0.1132 | 0.1034 | 0.1129 |
| Full ROC-AUC | 0.7143 | 0.0257 | 0.7218 | 0.6762 | 0.7669 | 0.6772 | 0.7566 |
| Full PR-AUC | 0.3426 | 0.0350 | 0.3434 | 0.2823 | 0.4046 | 0.2872 | 0.4036 |
| Full Brier | 0.1060 | 0.0031 | 0.1054 | 0.1002 | 0.1117 | 0.1010 | 0.1112 |

### Paired deltas, full minus ED-history

| Metric | Mean | SD | Median | Min | Max | p2.5 | p97.5 | Directional count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Δ ROC-AUC | +0.0295 | 0.0225 | +0.0240 | −0.0105 | +0.0778 | −0.0044 | +0.0718 | 23/25 positive |
| Δ PR-AUC | +0.0359 | 0.0197 | +0.0399 | −0.0002 | +0.0684 | +0.0016 | +0.0638 | 24/25 positive |
| Δ Brier | −0.0017 | 0.0019 | −0.0016 | −0.0047 | +0.0014 | −0.0047 | +0.0013 | 19/25 improved |

The locked-holdout increment (+0.065 ROC / +0.085 PR) is larger than
the repeated-CV mean increment (+0.030 ROC / +0.036 PR). The holdout
is treated as optimistic relative to the CV distribution, not as the
inferential estimate.

---

## D. Feature-family ablation (add family to ED-history)

Source: `outputs/feature_family_ablation.csv`. Same locked holdout as
section B. **Design A** — not commensurate with leave-one-block-out.

| Model | ROC-AUC | PR-AUC | Brier | Δ ROC vs ED | Δ PR vs ED |
|---|---:|---:|---:|---:|---:|
| ED history only | 0.709095 | 0.330794 | 0.105286 | 0 | 0 |
| ED + demographics | 0.752427 | 0.399777 | 0.101100 | +0.043332 | +0.068983 |
| ED + health | 0.739259 | 0.377270 | 0.102886 | +0.030164 | +0.046476 |
| ED + access | 0.740104 | 0.355656 | 0.104048 | +0.031009 | +0.024862 |
| ED + socioeconomic | 0.745730 | 0.382150 | 0.102876 | +0.036635 | +0.051356 |
| Full model | 0.774006 | 0.415935 | 0.099390 | +0.064911 | +0.085141 |

On this holdout, adding the demographic family to ED history produced
the largest single-family increment. That does not identify an
independent causal contribution and does not replace Family B.

---

## E. Age, demographic, health, access, and SES block ablations

Sources: `outputs/age_ablation_summary.md`,
`demographic_ablation_summary.md`, `health_ablation_summary.md`,
`access_ablation_summary.md`, `ses_ablation_summary.md`, and the
paired CSVs. Same 5×5 training folds as section C. **Design B.**

Remaining increment versus ED-history after removing the named block
(CV means):

| Contrast | Remaining Δ ROC vs ED | Remaining Δ PR vs ED |
|---|---:|---:|
| Full model (reference) | +0.0295 | +0.0359 |
| B1 no-age | +0.0244 | +0.0342 |
| B2 no-demographics | +0.0358 | +0.0357 |
| B3 no-health | +0.0344 | +0.0401 |
| B4 no-access | +0.0278 | +0.0343 |
| B5 no-SES | +0.0314 | +0.0424 |

Mean reduced-minus-full deltas (the Family B contrasts; inferential
tests are in section G/H):

| Contrast | Mean Δ ROC | Mean Δ PR | Mean Δ Brier |
|---|---:|---:|---:|
| B1 No-age − Full | −0.0051 | −0.0017 | +0.0002 |
| B2 No-demographics − Full | +0.0062 | −0.0002 | +0.0000 |
| B3 No-health − Full | +0.0049 | +0.0042 | −0.0004 |
| B4 No-access − Full | −0.0018 | −0.0017 | +0.0002 |
| B5 No-SES − Full | +0.0019 | +0.0065 | −0.0006 |

Locked-holdout reduced-model scores (confirmation only):

| Model | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|
| Full | 0.774 | 0.416 | 0.099 |
| Without age | 0.771 | 0.404 | 0.100 |
| Without demographics | 0.771 | 0.410 | 0.100 |
| Without health | 0.765 | 0.410 | 0.100 |
| Without access | 0.770 | 0.414 | 0.100 |
| Without SES | 0.774 | 0.417 | 0.099 |

Analytic-cohort health missingness after sentinel recode (`health`
ablation audit): `RTHLTH6` 3/5,108 (0.06%); `MNHLTH6` 5/5,108 (0.10%).

---

## F. Predictor redundancy diagnostic

Source: `outputs/predictor_correlation_matrix.csv`,
`outputs/predictor_vif.csv`. Training portion n = 3,831. Did not
modify the production model.

Strongest flagged associations (|value| > 0.5, Spearman excluded from
the flag rule):

- `AGEY3X`–`MARRY6X`: correlation ratio η = 0.8099
- `POVCATY3`–`TTLPY3X`: correlation ratio η = 0.5975

Numeric VIFs (all < 5):

| Variable | VIF |
|---|---:|
| `AGEY3X` | 3.68 |
| `TTLPY3X` | 2.07 |
| `ERTOTY1` | 1.18 |
| `ERTOTY2` | 1.14 |
| `ERTOTY3` | 1.14 |

All 45 one-hot encoded columns have infinite VIF. That is a structural
artifact of `OneHotEncoder` without dropping a reference level, not a
finding that those categories are independently collinear in a
substantive sense.

The diagnostic does **not** prove predictor independence and did not
modify the production model.

---

## G. Primary statistical inference (Family A)

Source: `outputs/statistical_inference.csv`. Nadeau–Bengio, 25 paired
differences, k = 5, r = 5, test/train ratio ≈ 0.25, df = 24, two-sided,
α = 0.05, no multiplicity adjustment.

| Metric | Mean difference | Corrected SE | t | df | p | Significant at 0.05 |
|---|---:|---:|---:|---:|---:|---|
| ROC-AUC | +0.0295 | 0.0121 | +2.437 | 24 | 0.0226 | yes |
| PR-AUC | +0.0359 | 0.0106 | +3.385 | 24 | 0.0024 | yes |
| Brier | −0.0017 | 0.0010 | −1.655 | 24 | 0.1110 | no |

Exact saved values: ROC mean +0.02953897, SE 0.01211861, t +2.437488,
p = 0.02257265; PR mean +0.03590249, SE 0.01060767, t +3.384577,
p = 0.00244863; Brier mean −0.00166965, SE 0.00100914, t −1.654524,
p = 0.11104216.

**The primary discrimination hypothesis is supported for ROC-AUC and
PR-AUC under the pre-specified analysis.**

**Brier improvement was directionally favorable but not statistically
detected under the pre-specified analysis.**

Statistical significance is not clinical significance.

---

## H. Family B (Holm-adjusted leave-one-block-out)

Source: `outputs/statistical_inference.csv`. Holm–Bonferroni applied
separately within ROC, PR, and Brier across the five contrasts.

| Contrast | Metric | Mean | SE | t | Raw p | Holm p | Sig. 0.05 |
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

**No pre-specified leave-one-block-out contrast showed statistically
detectable performance change under the pre-specified corrected
analysis.**

That statement does **not** mean that no block matters, that blocks are
equivalent, that predictors are independent, that blocks are
unnecessary, or that the full model contains redundant information with
certainty.

---

## I. Repeat-level robustness

Source: `outputs/robustness_repeat_level_test.csv`. Family A only.
Five repeat-level means; one-sample t-test, df = 4. Additional
sensitivity analysis; **does not replace** the pre-registered
Nadeau–Bengio test. The five repeats are the repeat-level resampling
unit, not five independent population samples.

Repeat-level means (Full − ED-history):

| Metric | r0 | r1 | r2 | r3 | r4 |
|---|---:|---:|---:|---:|---:|
| ROC-AUC | +0.0359 | +0.0272 | +0.0221 | +0.0287 | +0.0337 |
| PR-AUC | +0.0438 | +0.0326 | +0.0265 | +0.0360 | +0.0405 |
| Brier | −0.0019 | −0.0018 | −0.0011 | −0.0015 | −0.0021 |

| Metric | Repeat-level t | p | df | Sig. 0.05 | NB p (primary) |
|---|---:|---:|---:|---|---:|
| ROC-AUC | +12.135 | 0.0003 | 4 | yes | 0.0226 |
| PR-AUC | +11.850 | 0.0003 | 4 | yes | 0.0024 |
| Brier | −9.747 | 0.0006 | 4 | yes | 0.1110 |

**ROC and PR remain significant under the sensitivity analysis.**

**Brier differs from the primary NB conclusion and therefore does not
replace the pre-specified Brier result.** The pre-specified Brier test
remains non-significant (p = 0.1110).

---

## J. Locked holdout interpretation

The locked holdout was used as a confirmation / generalization check
for the selected primary comparison (full vs 3-year ED history). It was
not used to choose the model, tune hyperparameters, choose hypotheses,
or perform statistical inference.

The holdout increment (+0.065 ROC / +0.085 PR) and the repeated-CV mean
increment (+0.030 ROC / +0.036 PR) are different objects. Inference
uses the training-only 5×5 paired differences.

---

## K. Scientific interpretation

Under the pre-specified Family A analysis, the full pre-cutoff feature
set showed statistically detectable incremental discrimination versus
three-year ED history on ROC-AUC and PR-AUC in this analytic sample.
Brier improvement was directionally favorable and was not statistically
detected under that analysis.

**No single pre-specified predictor block was shown to account for the
incremental discrimination, and substantial incremental performance
remained after removal of each block.**

**The block-ablation design cannot distinguish distributed independent
information from more subtle redundancy.**

The analysis does not establish that incremental signal is “distributed
across the predictor set” as a proven fact. It does not establish
clinical utility, national predictive performance, or readiness for
deployment.
