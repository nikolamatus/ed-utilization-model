# Revision v1.1 plan

Audit completed before substantive analysis changes. This plan records
identified issues, evidence, proposed corrections, and whether each
correction changes the analysis or only reporting.

**Non-negotiable constraints**

- Do not change the primary outcome, prediction horizon, predictor set,
  cohort rule, seeds, or locked first-run filenames to chase better
  metrics.
- Do not overwrite `outputs/` historical primary result files.
- Do not edit `docs/pre_registration_block_ablation_plan.md` (historical
  artifact; filename uses “pre-registration” language that this revision
  will not retroactively validate as formal preregistration).
- Do not run `python -m feasibility.run`.
- New analyses use new filenames (`*_v1_1.*`, `*_sensitivity_*`,
  `*_holdout_bootstrap_*`, `*_calibration_*`).
- Do not treat Git history as the complete research chronology.

Primary scientific question (unchanged):

> How much additional predictive value can longitudinal health,
> utilization, access, demographic, and socioeconomic information
> provide beyond historical ED utilization alone for predicting any ED
> use in the subsequent year?

Primary comparison (unchanged): three-year ED-history baseline
(`ERTOTY1`–`ERTOTY3`) versus the prespecified full pre-cutoff model.

---

## Audit snapshot

| Item | Finding |
| --- | --- |
| Package | `ed-utilization-model` 1.0.0 |
| Data | MEPS HC-245 Panel 24 (2019–2022), user-supplied `h245.dta` |
| Cohort | `YEARIND==1` and valid non-sentinel `ERTOTY1`–`Y4`; N = 5,108; 693 events |
| Split | 25% stratified holdout, seed 42; train n = 3,831; holdout n = 1,277 |
| Estimator | L2 logistic, `C=1.0`, `random_state=42`; no hyperparameter search |
| CV | Training-only 5×5 `RepeatedStratifiedKFold`, seed 2021 |
| Inference | Nadeau–Bengio on 25 paired fold deltas; Family B Holm within metric |
| Locked primary deltas | ΔROC +0.02954; ΔPR +0.03590; ΔBrier −0.00167 (`outputs/statistical_inference.csv`) |
| Git | All commits dated 2026-09-12; first research commit `12733c6` already contains plan, code, and outputs |

Independent reproduction from saved fold tables matches the locked
Family A numbers. Do not alter the analysis to recover or improve them.

---

## Issue register

### 1. Holdout described as untouched confirmation

| Field | Content |
| --- | --- |
| **Issue** | README, manuscript, methodology, CV summaries, and inference summaries call the 25% split an “untouched,” “locked confirmation,” or implicitly independent confirmatory set. |
| **Evidence** | `modeling._split` is used in the first-run pipeline (`feasibility/run.py`). `report.decide_gate` consumes holdout ROC/PR lifts (`MIN_INCREMENTAL_ROC_LIFT=0.02`, `MIN_INCREMENTAL_PR_LIFT=0.01`). Design A feature-family ablation also scores the same holdout. Later CV reconstructs the split and leaves it unused for *inference*, but the holdout was available during development and informed the triage gate. |
| **Methodological concern** | “Untouched / external / independently confirmatory” overstates independence. The split was not used to choose predictors, `C`, or Family A/B hypotheses, but it was used for first-run evaluation and a research-triage gate. |
| **Proposed correction** | Reporting only. Call it a **first-run / development-stage internal evaluation set** (held-out internal evaluation). State that inferential p-values come from training-only CV, not the holdout. Do not create a new test set. |
| **Changes analysis?** | No |
| **Affects primary results?** | No |
| **Expected outputs** | Updated README, manuscript, methodology, results, limitations, analysis_status |
| **Validation** | Terminology review; locked CSVs unchanged |

### 2. Holdout metrics lack uncertainty intervals

| Field | Content |
| --- | --- |
| **Issue** | Holdout ROC-AUC, PR-AUC, and Brier are reported as points only. |
| **Evidence** | `outputs/model_metrics.csv`; `predictions.csv` stores full-model `y_true`/`y_prob` only. |
| **Methodological concern** | Point estimates on n = 1,277 (173 events) are noisy; intervals are needed for honest reporting. |
| **Proposed correction** | New analysis. Refit the locked ED-history and full pipelines on the reconstructed training portion (same seeds/hyperparameters), verify exact match to locked holdout metrics, then bootstrap person-level `(y, p_ed, p_full)` pairs. Percentile CIs. Document B, seed, resampling unit, degenerate-sample handling. Do not rerun to prefer an interval. |
| **Changes analysis?** | Adds a reporting analysis; does not replace locked points |
| **Affects primary results?** | No (primary inference remains CV/NB) |
| **Expected outputs** | `outputs/holdout_bootstrap_v1_1.csv`, `outputs/holdout_bootstrap_v1_1_summary.md` |
| **Validation** | Refit matches locked metrics to 1e-12; tests on synthetic bootstrap |

### 3. Calibration is a reliability diagram only

| Field | Content |
| --- | --- |
| **Issue** | Holdout calibration is a quantile-binned table (`outputs/calibration.csv`) without intercept/slope. |
| **Evidence** | `modeling.calibration_table` / `write_calibration_outputs`. No logit-of-p regression. |
| **Methodological concern** | Discrimination is reported more thoroughly than calibration. Intercept/slope are standard assessment quantities. Must not fit a recalibration model on the evaluation set and then report the recalibrated probabilities as validation. |
| **Proposed correction** | New assessment only: logistic regression of holdout `y` on `logit(p)` for the locked full-model probabilities (and ED-history, for comparison). Report intercept and slope. Label as first-run holdout assessment, not independent validation and not post-hoc recalibration. |
| **Changes analysis?** | Adds assessment; does not change predicted probabilities used in primary metrics |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/holdout_calibration_v1_1.csv` |
| **Validation** | Intercept/slope finite; locked `calibration.csv` hash unchanged |

### 4. VIF on full dummy matrix is invalid

| Field | Content |
| --- | --- |
| **Issue** | `variance_inflation_factors` uses the production OHE (`OneHotEncoder` without dropping a level). Categorical dummies are linearly dependent with the intercept-equivalent span, producing infinite VIF for essentially all one-hot columns. |
| **Evidence** | `outputs/predictor_vif.csv`: `cat__SEX_1.0`, `cat__SEX_2.0`, and other dummies are `inf`. Numeric VIFs are finite. |
| **Methodological concern** | Reporting those infinities as multicollinearity evidence is misleading. VIF was diagnostic only and was **not** used to drop predictors. |
| **Proposed correction** | Keep the historical file. Add a corrected diagnostic that drops a reference level per categorical variable, still **without removing predictors from the model**. State that VIF is descriptive, not a modeling rule. |
| **Changes analysis?** | Diagnostic only |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/predictor_vif_drop_reference_v1_1.csv`, `outputs/predictor_vif_v1_1_notes.md` |
| **Validation** | Categorical VIFs finite unless genuine collinearity; tests on synthetic dummy-trap vs drop-first |

### 5. “Pre-registered” overstates provenance

| Field | Content |
| --- | --- |
| **Issue** | Docs call the block-ablation plan “pre-registered.” Git first contains the plan in `12733c6` (2026-09-12) together with analysis code and locked outputs. |
| **Evidence** | `git log`: all commits 2026-09-12. No independently dated external artifact establishes a plan-creation date. Researcher recollection: plan existed locally before Git. |
| **Methodological concern** | Formal preregistration (OSF/clinicaltrials/etc.) is not evidenced. Calling the plan “post-hoc” solely because it entered Git with the first research commit would also be a category error: Git incorporation ≠ research-plan creation. |
| **Proposed correction** | Reporting/chronology. Use **documented analysis plan** / **repository analysis plan**. Distinguish: (1) claimed local plan creation (recollection); (2) Git incorporation 2026-09-12; (3) original analysis artifacts in the same commit; (4) later documentation and this v1.1 revision. Do not rewrite Git history. Do not backdate. |
| **Changes analysis?** | No |
| **Affects primary results?** | No |
| **Expected outputs** | `docs/research_chronology.md`; terminology edits in reporting docs (not the historical plan file) |
| **Validation** | Chronology table uses evidence categories; no fabricated timestamps |

### 6. Family A reports three metrics without a stated metric family

| Field | Content |
| --- | --- |
| **Issue** | The analysis plan says Family A is “one pre-specified hypothesis” with no multiplicity correction, but ROC-AUC, PR-AUC, and Brier are all tested. |
| **Evidence** | `docs/pre_registration_block_ablation_plan.md` Family A section; `statistical_inference.py` tests three A1 metrics, Holm only on Family B. |
| **Methodological concern** | ROC *p* = 0.0226 would not survive a post-hoc Bonferroni ×3 (threshold 0.0167); PR *p* = 0.0024 would. Applying a new correction because ROC is fragile would be result-dependent. |
| **Proposed correction** | Reporting only. Keep the plan-specified rule (no Holm inside Family A). State that three complementary metrics were always reported; primary inferential contrast is Full − ED-history; discrimination evidence is ROC and PR; Brier is probabilistic accuracy (lower is better; Δ = Full − Baseline). Note the unadjusted three-metric family as a limitation a conservative reader may apply. |
| **Changes analysis?** | No |
| **Affects primary results?** | No |
| **Expected outputs** | Manuscript/results/limitations language; `docs/reporting_checklist.md` |
| **Validation** | Locked `statistical_inference.csv` unchanged |

### 7. Nadeau–Bengio implementation

| Field | Content |
| --- | --- |
| **Issue** | Need to verify the corrected t-test rather than trust comments. |
| **Evidence** | `nadeau_bengio_ttest`: `Var_NB = (1/n + n_test/n_train) * s^2`, `t = mean / sqrt(Var_NB)`, df = n−1 = 24, two-sided Student-t. Mean `n_test/n_train` ≈ 0.25. Paired fold deltas. Tests in `tests/test_statistical_inference.py` reproduce the formula and show corrected SE > naive SE. |
| **Methodological concern** | None identified in the implementation. Naive t-tests would overstate precision (Brier naive *p* is much smaller than NB *p* = 0.111). |
| **Proposed correction** | Preserve. Add 95% CIs as `mean ± t_{0.975,24} × corrected_se` written to a **new** file derived from the locked table. Document the formula more clearly in reporting docs. |
| **Changes analysis?** | Reporting intervals from locked estimates; no refit |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/statistical_inference_intervals_v1_1.csv` |
| **Validation** | Intervals reconstruct from locked mean/SE; tests |

### 8. Adult-only population definition

| Field | Content |
| --- | --- |
| **Issue** | Analytic cohort includes children. Employment and some health/access items are often inapplicable for minors (`EMPST6` raw non-usable 21.89%). |
| **Evidence** | Prior audit: 898 / 5,108 with `AGEY3X < 18`. Limitations already note child inapplicability. |
| **Methodological concern** | Mixing pediatric and adult persons is a meaningful population-definition issue for SES/employment predictors, independent of performance. |
| **Proposed correction** | Sensitivity: subset the **original** seed-42 train/holdout assignment to `AGEY3X >= 18` (do not re-draw the split). Repeat training-only 5×5 CV (seed 2021) and holdout scoring. Label as sensitivity, not a new primary. |
| **Changes analysis?** | New sensitivity only |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/sensitivity_adult_only_v1_1_cv.csv`, `_holdout.csv`, `_summary.md` |
| **Validation** | Sample/event counts; leakage asserts; locked files unchanged |

### 9. ALL9RDS restriction

| Field | Content |
| --- | --- |
| **Issue** | Primary cohort is `YEARIND==1`, not `ALL9RDS==1`. Analytic ∩ ALL9RDS = 4,883 vs 5,108 (225 persons). |
| **Evidence** | `feasibility/longitudinal.py` documents the choice: ALL9RDS is AHRQ’s complete nine-round subset for weighted national estimates. |
| **Methodological concern** | Complete-round participation is a selection/missingness concern, not a reason to change the primary estimand. A sensitivity is justified; making ALL9RDS primary would be a new study. |
| **Proposed correction** | Sensitivity on the original split restricted to `ALL9RDS==1`. Do not adopt as primary regardless of result. |
| **Changes analysis?** | New sensitivity only |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/sensitivity_all9rds_v1_1_cv.csv`, `_holdout.csv`, `_summary.md` |
| **Validation** | n_analytic_and_all9rds = 4,883; locked files unchanged |

### 10. COVID / 2020 utilization disruption

| Field | Content |
| --- | --- |
| **Issue** | Three-year ED history includes `ERTOTY2` (2020), a year of atypical ED volume. |
| **Evidence** | Limitations already note Panel 24 overlaps COVID-19. |
| **Methodological concern** | Legitimate disruption concern, independent of observed metrics. Changing the primary baseline to drop 2020 would redefine the scientific comparison. |
| **Proposed correction** | Sensitivity: same persons and split; ED-history uses `ERTOTY1`+`ERTOTY3` only; full model drops `ERTOTY2` only. Label clearly. Do not replace the 3-year baseline. |
| **Changes analysis?** | New sensitivity only |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/sensitivity_covid2020_v1_1_cv.csv`, `_holdout.csv`, `_summary.md` |
| **Validation** | Predictor lists exclude `ERTOTY2`; leakage asserts |

### 11. Temporal-strict sensitivity — not indicated

| Field | Content |
| --- | --- |
| **Issue** | Mandate asks whether a stricter temporal boundary is needed. |
| **Evidence** | Predictors are Y3 / Round 6 / time-invariant. Round 7 (overlapping 2021/2022) and all Y4 / R8 / R9 names are excluded by `features.assert_no_leakage` and `looks_post_cutoff`. Outcome is `ERTOTY4` only. Preprocessing is fit inside training folds. |
| **Methodological concern** | None identified that requires dropping Round-6 2021 variables. Artificial extra restrictions would make the methods look stricter without changing the prediction question. |
| **Proposed correction** | Do **not** run a temporal-strict sensitivity. Document the audit. |
| **Changes analysis?** | No |
| **Affects primary results?** | No |
| **Expected outputs** | Chronology/completion notes only |
| **Validation** | Existing leakage tests remain the control |

### 12. Survey weights unused

| Field | Content |
| --- | --- |
| **Issue** | `LONGWT`/`VARSTR`/`VARPSU` ingested, not applied. |
| **Evidence** | `longitudinal.py`, population_summary, methodology. |
| **Methodological concern** | The estimand is individual-level predictive performance on the analytic sample, not a national prevalence or nationally representative performance parameter. Automatically adding weights would change the estimand and was not the original plan. |
| **Proposed correction** | Reporting only: state the estimand clearly. Do not add a weighted primary or a result-driven weighted sensitivity. |
| **Changes analysis?** | No |
| **Affects primary results?** | No |
| **Expected outputs** | Reporting docs |

### 13. Preprocessing / leakage

| Field | Content |
| --- | --- |
| **Issue** | Need to confirm transformations are training-fold-only. |
| **Evidence** | sklearn `Pipeline` + `ColumnTransformer`; `repeated_cv.fit_on_fold` fits a new pipeline per fold; holdout preprocessor is fit on training only in `full_logistic_model`. No feature selection or threshold optimization. |
| **Methodological concern** | None identified. |
| **Proposed correction** | Document, do not rewrite. |
| **Changes analysis?** | No |

### 14. Missing data documentation incomplete for the analytic cohort

| Field | Content |
| --- | --- |
| **Issue** | `outputs/missingness.csv` is raw-file missingness. Limitations say analytic missingness was detailed only for health items. |
| **Evidence** | `inspect.missingness_table` in `run.py` uses the full file. |
| **Methodological concern** | Readers cannot see predictor missingness on N = 5,108. Complete-case is not used; single imputation inside folds is. |
| **Proposed correction** | Write analytic-cohort missingness to a new file. Do not introduce multiple imputation. |
| **Changes analysis?** | Reporting table only |
| **Affects primary results?** | No |
| **Expected outputs** | `outputs/missingness_analytic_cohort_v1_1.csv` |

### 15. Holm Family B

| Field | Content |
| --- | --- |
| **Issue** | Verify Holm family definition and calculation. |
| **Evidence** | Holm applied separately within each of ROC, PR, Brier across B1–B5 (m = 5). Not applied across families or metrics. `holm_adjust` matches the standard step-down formula; unit tests check ordering. |
| **Methodological concern** | None in the implementation. Reporting should keep primary vs secondary vs descriptive vs exploratory distinct. |
| **Proposed correction** | Preserve; clarify in reporting. Design A add-on ablation, death sensitivity, VIF, and repeat-level t-test remain non-primary. |
| **Changes analysis?** | No |

### 16. Endpoint

| Field | Content |
| --- | --- |
| **Issue** | Confirm primary endpoint. |
| **Evidence** | `future_ed_visit = (ERTOTY4 >= 1)` after sentinel recode. `future_high_ed_use` (≥2) is inspection-only. Unit of analysis is person (`DUPERSID`). Predictor window 2019–2021; outcome 2022. |
| **Methodological concern** | None. Do not switch endpoints. |
| **Proposed correction** | Document more explicitly in manuscript/checklist. |

---

## Analyses that will not be run

| Analysis | Reason |
| --- | --- |
| New holdout / external test set | Not necessary; would be a new study |
| Weighted sklearn metrics as primary | Different estimand; not original plan |
| Multiple imputation | Existing single imputation inside folds is defensible |
| Hyperparameter retuning | Would be post-development optimization |
| Predictor dropping for VIF | VIF was never a removal rule |
| Temporal-strict Round-6 drop | Current boundary already excludes post-cutoff / Round 7+ |
| Changing Family A multiplicity | Result-dependent; plan specified no correction inside A |
| `python -m feasibility.run` | Would overwrite locked first-run files |

---

## Implementation order

1. This plan (`docs/revision_v1_1_plan.md`) — **this file**.
2. Chronology, notes, reporting checklist.
3. New analysis module `feasibility/revision_v1_1.py` writing only `*_v1_1*` outputs.
4. Reporting terminology updates.
5. Tests; pytest; completion report.

Primary locked numbers remain the v1.0 result set. v1.1 either
documents them more honestly or adds labeled sensitivities/assessments.
