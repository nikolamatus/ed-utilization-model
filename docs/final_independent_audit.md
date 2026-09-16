# Independent final scientific audit

**Role.** External skeptical reviewer of the repository in its current
working-tree state. This audit does not assume the v1.1 revision is
correct because it was produced in a prior session.

**Scope.** Source code, tests, locked v1.0 outputs, v1.1 outputs, analysis
plan, README, manuscript and reporting documents, revision notes,
completion report, research chronology, and Git history.

**What was not done.** No `python -m feasibility.run`. No alternative
analyses to chase different results. No automatic repair of findings.
Primary locked numbers were recomputed from saved fold tables using the
repository’s own `nadeau_bengio_ttest` / `holm_adjust` functions; models
were not refit for Family A.

**Audit date.** 2026-09-15–16 (working tree inspected after v1.1 files
were present and uncommitted).

**Overall judgment.** The locked primary analysis, validation design,
leakage controls, and current living documentation (README, manuscript
body, methodology body, limitations, chronology) are internally coherent,
reproducible, and scientifically defensible. A skeptical reviewer who
inspects code and outputs can reconstruct what was planned, what was
analyzed, what was added later, and how every important number was
produced. Leftover “Pre-registered” / “untouched confirmation” wording
remains in some headings, a status ledger, generator templates, and
locked generated summaries. Those are reporting residues, not validity
flaws.

**No additional substantive methodological issue was identified in this
independent audit.**

---

## How to read the classifications

| Class | Meaning in this audit |
|---|---|
| Critical | Would materially undermine validity of the primary analysis. |
| Major | Requires correction before submission (methods, numbers, or claims). |
| Minor | Reporting/clarity inconsistency that does not change the analysis. |
| No issue | Audited and supported by code and/or locked outputs. |

Each finding lists file, function if applicable, evidence, assessment,
and recommended action. Recommended actions are **not implemented** in
this pass.

---

## Executive findings

| ID | Topic | Class |
|---|---|---|
| F1 | Primary Family A numbers originate from locked outputs and recompute | No issue |
| F2 | Baseline/full predictor definition; `ERTOTY4` excluded from X | No issue |
| F3 | Temporal and preprocessing leakage | No issue |
| F4 | Holdout is first-run internal evaluation; primary inference is training CV | No issue |
| F5 | Holdout bootstrap B=2000, seed 20210915, reported CIs | No issue |
| F6 | Original VIF invalid; corrected VIF descriptive only; production unchanged | No issue |
| F7 | Cox logistic calibration assessment; no recalibration | No issue |
| F8 | Adult-only sensitivity vs exploratory age ablation, labeled correctly | No issue |
| F9 | Family A unadjusted; Family B Holm m=5 implemented correctly | No issue |
| F10 | `LONGWT` recorded, unused; estimand unweighted | No issue |
| F11 | Missing data / `EMPST6` ~16%; imputation inside training folds | No issue |
| F12 | No evaluation-set influence on C, predictors, or Family A/B hypotheses | No issue |
| F13 | Provenance: documented plan, not formal preregistration; Git not rewritten | No issue |
| F14 | Living docs do not claim external validation, causality, or clinical utility | No issue |
| F15 | Seeds, commands, warning not to re-run `feasibility.run`; 84 tests passed | No issue |
| F16 | Locked v1.0 output hashes unchanged by v1.1 | No issue |
| F17 | Scientific interpretation matches evidence | No issue |
| M1 | Leftover “Pre-registered” headings/fields in living documents | Minor |
| M2 | Leftover “untouched / confirmation / Pre-registered” in locked generated summaries and generator templates | Minor |
| M3 | v1.1 artifacts present in the working tree but not committed to Git | Minor |

No Critical findings. No Major findings.

---

## 1. Repository inspection

Inspected, among other paths:

- `feasibility/config.py`, `features.py`, `modeling.py`, `longitudinal.py`,
  `report.py`, `run.py`, `repeated_cv.py`, `ablation.py`,
  `statistical_inference.py`, `diagnostics.py`, `revision_v1_1.py`
- `tests/` (11 test modules)
- `outputs/statistical_inference.csv`, `repeated_cv_metrics.csv`,
  `model_metrics.csv`, `predictor_vif.csv` (v1.0 locked)
- `outputs/*v1_1*` (v1.1 reporting files)
- `docs/pre_registration_block_ablation_plan.md`, README, manuscript,
  methodology, results, limitations, chronology, revision notes,
  completion report, analysis status, reporting checklist
- `git log`, `git reflog`, `git ls-tree HEAD` for locked CSVs

Claims below are tied to those files, not to a prior completion summary.

---

## 2. Primary analysis — independent verification

**Finding F1 — No issue**

- **File:** `outputs/statistical_inference.csv`;
  `outputs/repeated_cv_metrics.csv`; `feasibility/statistical_inference.py`
  (`nadeau_bengio_ttest`).
- **Evidence:** Locked Family A rows:

  | Metric | mean Δ (Full − ED-history) | raw p | df | n |
  |---|---:|---:|---:|---:|
  | ROC-AUC | +0.029538965588917016 | 0.02257265024089372 | 24 | 25 |
  | PR-AUC | +0.03590249349377811 | 0.002448632579066552 | 24 | 25 |
  | Brier | −0.0016696542068063728 | 0.11104215575277274 | 24 | 25 |

  Rounded reporting (+0.0295, +0.0359, −0.0017; p = 0.0226, 0.0024,
  0.1110) matches. Independent recomputation from the 25 fold-level
  `delta_*` columns with `nadeau_bengio_ttest` and mean
  `n_cv_val/n_cv_train` reproduced the same means, t statistics, df, and
  p-values. `repeated_cv_metrics.csv` has 25 rows, `holdout_used` all
  `False`, `cv_random_state` all `2021`. Contrast label is
  `Full − ED-history`. Brier direction in the CSV is
  “Full better (lower Brier) than ED-history.” Formula in code:
  `Var_NB = (1/n + n_test/n_train) * s^2`, `df = n-1 = 24`. Family A
  `holm_adjusted_p_value` is blank (unadjusted). Inference reads saved
  fold CSVs and does not score the holdout for p-values.
- **Assessment:** Reported primary numbers originate from the locked
  analysis. Sign convention, lower-Brier-is-better, 5×5 CV, 25 paired
  differences, Nadeau–Bengio correction, df = 24, and training-only
  inference are implemented as documented. Holdout metrics are not the
  inferential test.
- **Recommended action:** None.

---

## 3. Primary model definition

**Finding F2 — No issue**

- **File:** `feasibility/config.py` (`PREDICTOR_ED_VARS`, `OUTCOME_ED_VAR`,
  `CANDIDATE_FEATURES`, `allowed_predictor_specs`);
  `feasibility/ablation.py` (`FAMILY_COLUMNS`).
- **Evidence:** Baseline ED-history columns are exactly `ERTOTY1`,
  `ERTOTY2`, `ERTOTY3`. Outcome is `ERTOTY4` with
  `allowed_by_cutoff=False`, `treatment="outcome"`. Full predictor set
  from `allowed_predictor_specs()` (independently printed): `AGEY3X`,
  `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`, `RTHLTH6`, `MNHLTH6`,
  `INSCOVY3`, `HAVEUS6`, `POVCATY3`, `TTLPY3X`, `EMPST6`, `ERTOTY1`,
  `ERTOTY2`, `ERTOTY3`. `assert_no_leakage` refuses `ERTOTY4` and Y4/R8/R9
  names. Production `C = 1.0` in `modeling._classifier`. No code path
  drops predictors from VIF or from observed holdout performance.
- **Assessment:** Baseline and full models match the documented
  comparison. `ERTOTY4` cannot enter X. Predictors stop at the 2021
  cutoff (or time-invariant). The comparison was not revised after seeing
  metrics.
- **Recommended action:** None.

---

## 4. Temporal leakage

**Finding F3 — No issue**

- **File / functions:** `feasibility/features.py`
  (`looks_post_cutoff`, `assert_no_leakage`, `build_feature_matrix`,
  `recode_sentinels`); `feasibility/config.py` (`is_temporally_allowed`,
  `validate_feature_metadata`, `POST_CUTOFF_FEATURES`);
  `feasibility/modeling.py` (`_preprocessor`, `full_logistic_model`);
  `feasibility/repeated_cv.py` (`fit_on_fold`);
  `feasibility/revision_v1_1.py` (`bootstrap_holdout_metrics`,
  `calibration_intercept_slope`).
- **Evidence:**
  - Annual MEPS predictors used are Y3 / Round 6 names with
    `availability_year <= 2021`, or time-invariant (`SEX`, `RACETHX`).
  - ED history is Y1–Y3 only. `ERTOTY4` is listed as outcome and in
    `POST_CUTOFF_NAMES`.
  - Name-pattern guards block `Y4` suffixes and Round 8/9 stems.
  - Unknown availability fails closed (`allowed_by_cutoff` cannot be set
    independently of the temporal rule).
  - Longitudinal aggregation is YEARIND==1 person-level annual totals,
    not post-cutoff rolling features.
  - Imputation and scaling live inside an sklearn `Pipeline` fitted on
    the training matrix of each fit (`pipe.fit(X_train, y_train)`).
  - No feature-selection search. No hyperparameter search. Production
    OHE does not drop a level (`OneHotEncoder(handle_unknown="ignore")`).
  - v1.1 bootstrap resamples frozen `(y, p_ed, p_full)` pairs; it does
    not refit inside replicates.
  - v1.1 calibration fits `logit(Y) = a + b logit(p)` on locked
    probabilities and does not replace them.
- **Assessment:** Information unavailable at prediction time does not
  enter X. Preprocessing leakage into evaluation folds was not found.
  Calibration and bootstrap do not feed holdout labels back into the
  production model.
- **Recommended action:** None.

---

## 5. Validation design

**Finding F4 — No issue**

- **File / functions:** `feasibility/modeling.py` (`_split`);
  `feasibility/report.py` (`decide_gate`);
  `feasibility/repeated_cv.py` (`training_portion`, `holdout_used=False`);
  README; `docs/manuscript.md` § validation paragraphs.
- **Evidence:** Holdout is `train_test_split(..., test_size=0.25,
  random_state=42, stratify=y)`. Sizes asserted in
  `revision_v1_1.run_revision`: train 3,831, holdout 1,277. First-run
  scoring is in `feasibility/run.py` via `decide_gate`, which uses
  holdout ROC/PR lifts against triage floors (0.02 / 0.01). Family A
  p-values come from training-only 5×5 CV (`holdout_used=False`).
  Predictors and `C=1.0` are not chosen from the holdout. README and
  manuscript currently call the split a **first-run / development-stage
  internal evaluation set**, not external validation, not a pristine
  test set, and not independently confirmatory.
- **Assessment:** The holdout was scored in the original pipeline and
  informed the triage gate. It did not select the model class, `C`, or
  the Family A/B hypotheses. Training CV is independent of holdout
  metrics for inference. Living terminology matches that design.
- **Recommended action:** None for the design. Residual “confirmation /
  untouched” phrases in locked generated files are M2.

---

## 6. Holdout bootstrap

**Finding F5 — No issue**

- **File / function:** `feasibility/revision_v1_1.py`
  (`BOOTSTRAP_SEED = 20210915`, `BOOTSTRAP_REPLICATES = 2000`,
  `bootstrap_holdout_metrics`); `outputs/holdout_bootstrap_v1_1.csv`.
- **Evidence:** CSV records B requested = 2,000, valid = 2,000,
  degenerate skipped = 0, seed = 20210915, resampling unit =
  person-level `(y, p_ed, p_full)` pairs with replacement, CI method =
  percentile, sign convention Full − Baseline. Degenerate handling:
  skip replicates with a single class in `y`. No refit inside the loop.
  Reported intervals from the CSV:

  | Contrast | ci_lower | ci_upper | Documented rounding |
  |---|---:|---:|---|
  | ΔROC | 0.028134586570366497 | 0.10074113692955854 | 0.028 to 0.101 |
  | ΔPR | 0.04733417121147044 | 0.12120669696796915 | 0.047 to 0.121 |
  | ΔBrier | −0.008701451531868071 | −0.002882337662615194 | −0.009 to −0.003 |

  Point estimates are the locked holdout differences (ΔROC +0.0649,
  ΔPR +0.0851, ΔBrier −0.0059), labeled
  `locked_holdout_refit_verified`.
- **Assessment:** Implementation and reported intervals match. These
  intervals describe the first-run holdout, not Family A CV inference.
- **Recommended action:** None.

---

## 7. VIF

**Finding F6 — No issue**

- **File / functions:** `feasibility/diagnostics.py`
  (`design_matrix_and_names` uses production `_preprocessor`;
  `variance_inflation_factors` uses `sklearn.linear_model.LinearRegression`,
  intercept on by default); `feasibility/modeling.py` (`OneHotEncoder`
  without `drop`); `feasibility/revision_v1_1.py`
  (`design_matrix_drop_reference`, `variance_inflation_factors_drop_reference`);
  `outputs/predictor_vif.csv`; `outputs/predictor_vif_drop_reference_v1_1.csv`.
- **Evidence:** Locked original table has 50 design columns; 45 infinite
  VIFs, all on one-hot dummies that retain every level (e.g. both
  `cat__SEX_1.0` and `cat__SEX_2.0`). Numeric VIFs are finite (AGEY3X
  3.681). That is the dummy-variable trap (all levels + intercept).
  Corrected table: 40 finite VIFs, max 3.6814319417618684, none > 5.
  Column `role` = `descriptive_only_not_used_for_predictor_removal`.
  Production encoder is still no-drop OHE with L2. Manuscript states
  VIF “does not prove independence.”
- **Assessment:** Original diagnostic is invalid for categoricals for
  the stated reasons. Corrected diagnostic uses a reference-category
  drop. Results were not used to alter the production model. No
  unsupported “no collinearity / independence” claim in the manuscript
  body.
- **Recommended action:** None.

---

## 8. Calibration

**Finding F7 — No issue**

- **File / functions:** `feasibility/revision_v1_1.py`
  (`calibration_in_the_large`, `calibration_intercept_slope`);
  `outputs/holdout_calibration_v1_1.csv`; locked
  `feasibility/modeling.py` `calibration_table` (quantile reliability,
  does not replace probabilities).
- **Evidence:** Full-model row of the v1.1 table:

  | Quantity | Value |
  |---|---:|
  | n | 1,277 |
  | events | 173 |
  | mean predicted | 0.13489247813459015 |
  | observed prevalence | 0.13547376664056382 |
  | CITL (b fixed at 1) | 0.0056253310564784624 |
  | joint intercept a | 0.401990289998952 |
  | joint slope b | 1.236800519202104 |

  Method string: unpenalized `logit(Y) = a + b logit(p)`; assessment
  only; probabilities not recalibrated. Dataset labeled
  `first_run_holdout_internal_evaluation`. sklearn `C=np.inf`.
  Manuscript distinguishes CITL (overall event-rate calibration), joint
  intercept (offset at p = 0.5 when slope is free), and slope > 1
  (predictions somewhat compressed toward the mean). It does not call
  the model severely miscalibrated or “well calibrated.”
- **Assessment:** Calculation and interpretation are supported.
  Near-zero CITL with slope ≈ 1.24 is mild compression, compatible with
  L2 shrinkage, not overall prevalence bias. No recalibration of
  production probabilities.
- **Recommended action:** None.

---

## 9. Adult-only analyses

**Finding F8 — No issue**

- **File:** `outputs/sensitivity_adult_only_v1_1_inference.csv`;
  `outputs/exploratory_adult_age_ablation_v1_1_inference.csv`;
  `feasibility/revision_v1_1.py` (`run_population_sensitivity`,
  `run_exploratory_adult_age_ablation`); manuscript § adult paragraphs.
- **Evidence:** Adult Full vs ED-history (AGEY3X ≥ 18; train 3,162,
  holdout 1,048): ΔROC +0.019400…, p = 0.113358…; ΔPR +0.029943…,
  p = 0.002925…. Flags: `primary_replacement=False`; reason =
  population-definition. Exploratory adult B1 (drop `AGEY3X` only):
  No-age − Full ΔROC −0.002208…, p = 0.637128…. Flags:
  `exploratory_post_primary`, `prespecified=False`,
  `primary_replacement=False`. Code raises if the no-age block is not
  exactly `AGEY3X`. Manuscript: mixed-age ROC “should not be presented
  as demonstrated for adults alone”; exploratory ablation “is not used
  to explain” the adult Full-vs-ED ROC.
- **Assessment:** Analyses are separated and labeled as required. The
  manuscript does not claim the mixed-age ROC finding in adults, and
  does not use the null age ablation to explain the adult ROC result.
- **Recommended action:** None.

---

## 10. Multiplicity

**Finding F9 — No issue**

- **File / functions:** `feasibility/statistical_inference.py`
  (`holm_adjust`, Family A vs B construction);
  `outputs/statistical_inference.csv`; manuscript § inference and
  limitation 22.
- **Evidence:** Family A: three co-reported metrics, unadjusted
  p-values, Holm column empty. Manuscript states this is a limitation
  and that a post-hoc Bonferroni ×3 was not applied because it was not
  in the plan. Family B: Holm within each metric across m = 5 contrasts.
  Independent `holm_adjust` on the five raw p-values per metric matched
  the locked Holm column (`np.allclose` True for ROC, PR, and Brier).
  Holdout descriptive metrics, VIF, calibration, Design A add-on
  ablation, and v1.1 sensitivities are labeled non-primary / not Family A
  replacements (`primary_replacement=False` on sensitivity tables).
- **Assessment:** Documentation of unadjusted Family A is accurate.
  Family B Holm is implemented correctly. Secondary analyses are not
  misrepresented as extra Family A tests. No new correction was invented
  to change significance.
- **Recommended action:** None.

---

## 11. Survey weights

**Finding F10 — No issue**

- **File:** `feasibility/config.py` (`LONGWT`);
  `feasibility/longitudinal.py`; `feasibility/report.py`;
  grep of `feasibility/` for `sample_weight` / `LONGWT` application.
- **Evidence:** `LONGWT`, `VARSTR`, and `VARPSU` are required at ingest
  and recorded. No `sample_weight` is passed to sklearn estimators.
  README/manuscript estimand: unweighted person-level predictive
  performance on the analytic sample, not national estimates. MEPS is
  described as a nationally representative *survey* in related-work
  context, not as the estimand of these metrics.
- **Assessment:** Weights unused is correctly described. The manuscript
  does not treat unweighted AUCs as national performance parameters.
- **Recommended action:** None. Do not introduce weighting.

---

## 12. Missing data

**Finding F11 — No issue**

- **File:** `outputs/missingness_analytic_cohort_v1_1.csv`;
  `feasibility/features.py` (`recode_sentinels`);
  `feasibility/modeling.py` (`SimpleImputer` inside the pipeline);
  `docs/methodology.md` § sentinel and missing-data handling.
- **Evidence:** Analytic cohort N = 5,108. `EMPST6` nonusable_count =
  818, missing_pct = 16.01, valid_pct = 83.99. Sentinels (−1/−7/−8/−9
  and other negatives) become NA before imputation. Pipeline: median
  (numeric) / most-frequent (categorical), fit on training data of each
  model fit. No missingness indicators. Methodology calls this
  single-imputation, not multiple imputation.
- **Assessment:** Reported ~16% `EMPST6` missingness is exact (16.01%).
  Missing-data processing is inside training fits. No missingness
  leakage into evaluation features was found. Manuscript/methodology
  description matches the code.
- **Recommended action:** None.

---

## 13. Model / tuning leakage

**Finding F12 — No issue**

- **File:** `feasibility/modeling.py` (`_classifier` C=1.0; threshold
  0.5 labeled exploratory); `feasibility/report.py` (`decide_gate`);
  absence of `GridSearch` / `RandomizedSearch` / `CalibratedClassifier`
  in `feasibility/`.
- **Evidence:** Estimator, C, predictor list, and 0.5 threshold are
  fixed. Gate uses holdout lifts only as a research-triage tool and does
  not write a new predictor set or C. Feature selection is the
  documented allowed list, not a performance search. Calibration does
  not replace probabilities.
- **Assessment:** Evaluation-set information influenced the GREEN/not
  GREEN triage label, which is disclosed. It did not influence model
  definition, hyperparameters, feature selection, operating-point
  optimization, or Family A/B hypotheses.
- **Recommended action:** None.

---

## 14. Provenance / Git chronology

**Finding F13 — No issue**

- **File:** `git log`, `git reflog`, `git log --pretty=fuller`;
  `docs/research_chronology.md`;
  `docs/pre_registration_block_ablation_plan.md`.
- **Evidence:** First research commit is `12733c6` (2026-09-12),
  message “Complete empirical analysis and research documentation,”
  containing plan, code, and locked outputs. Nine commits, all dated
  2026-09-12. Reflog: initial commit, ordinary commits, one
  `merge origin/master`; no rebase, reset, or amend entries. Sampled
  AuthorDate equals CommitDate. Chronology distinguishes (1) plan
  creation (recollection; date not independently established), (2) Git
  incorporation 2026-09-12, (3) original analysis in the same snapshot,
  (4) later docs/release and this v1.1 pass. Living docs use
  “documented analysis plan,” not “formally preregistered,” except
  leftover headings (M1/M2).
- **Assessment:** Git incorporation is not treated as plan-creation
  date. Git order is not treated as proof that the plan is post-hoc.
  Formal preregistration is not claimed in the manuscript body. No
  evidence that Git history was rewritten. Absence of rewrite cannot be
  proved beyond this clone’s reflog; nothing in the reflog suggests it.
- **Recommended action:** None for chronology policy. Heading clean-up
  is M1.

---

## 15. Internal consistency (overclaim search)

**Finding F14 — No issue (living scientific claims)**

Searched for: preregistered; prospectively registered; external
validation; independent test set; no collinearity; well calibrated;
significant in adults; causal; preventable; ED avoidance; nationally
representative (as estimand); demonstrates clinical utility.

- **Evidence:** README, manuscript conclusions, limitations, and results
  explicitly deny clinical utility, causality, national estimates,
  external validation, and adult generalization of the ROC finding.
  “MEPS is a nationally representative household panel” appears as a
  *dataset description* in related work, not as a claim about these
  unweighted metrics. VIF text says it does not prove independence.
  Calibration is not called “well calibrated.” Threshold 0.5 metrics
  are exploratory. No “preventable ED” or “ED avoidance” efficacy claim
  in the manuscript conclusions.
- **Assessment:** Living scientific claims are not stronger than the
  evidence. Residual heading vocabulary is M1/M2, not an overclaim in
  the results/conclusions.
- **Recommended action:** None beyond M1/M2.

---

## 16. Reproducibility

**Finding F15 — No issue**

- **File:** `feasibility/config.py` (`RANDOM_SEED = 42`);
  `feasibility/repeated_cv.py` (`CV_RANDOM_STATE = 2021`);
  `feasibility/revision_v1_1.py` (`BOOTSTRAP_SEED = 20210915`);
  `pyproject.toml` (version 1.0.0; pandas/numpy/sklearn/scipy/matplotlib;
  pytest>=7.4); README reproducibility section.
- **Evidence:** README lists `python -m feasibility.revision_v1_1` as
  the v1.1 command (new `*_v1_1*` filenames). README states: **Do not
  re-run `python -m feasibility.run` against an existing completed
  analysis** because it would overwrite locked first-run artifacts.
  Actual test execution (`.venv` interpreter):

  ```
  84 passed in 88.91s
  ```

  (`python -m pytest -q --tb=no`, exit code 0.)
- **Assessment:** Seeds, dependency declaration, commands, output-path
  convention, test count, and the `run` warning are as required.
- **Recommended action:** None.

---

## 17. Locked output integrity

**Finding F16 — No issue**

- **File:** `git ls-tree HEAD` vs `git hash-object` of working-tree
  files; `git diff HEAD -- outputs/` for tracked files.
- **Evidence:** Blob SHA1 identity:

  | Path | HEAD blob |
  |---|---|
  | `outputs/statistical_inference.csv` | `1f29cc1d5f8c24943c772cc0a74c63930dd7bdbd` |
  | `outputs/repeated_cv_metrics.csv` | `f786a7ffd6f7a06a01d8574647ab515ee78559f0` |
  | `outputs/model_metrics.csv` | `5889965c40b8cce95fa639f8556586f0d2f7f123` |
  | `outputs/predictor_vif.csv` | `60934cbe2b2a0f405abe05e360d0f75653119a4f` |

  Working-tree SHA1s match. `git diff HEAD` for those files, figures,
  and tables is empty. v1.1 files are additional untracked
  `*_v1_1*` paths, not replacements of v1.0 names.
- **Assessment:** v1.1 work did not silently modify locked primary
  results, v1.0 outputs, original figures, or original tables.
- **Recommended action:** None. Do not regenerate locked files to
  refresh wording (see M2).

---

## 18. Scientific interpretation

**Finding F17 — No issue**

- **File:** `docs/manuscript.md` abstract, results, discussion,
  limitations, conclusions; README headline results.
- **Evidence:** Conclusions distinguish incremental discrimination
  (ROC/PR detected on mixed-age CV), probabilistic accuracy (Brier
  favorable, not detected), calibration (CITL near 0; slope mildly > 1),
  internal validation (first-run holdout + training CV), subgroup
  sensitivity (adult ROC not detected), and exploratory post-primary
  ablation (age among adults, null). They deny causal effects,
  preventable ED use, clinical utility, and national performance.
- **Assessment:** Interpretation matches the evidence. Predictive
  association is not converted into a causal or operational claim.
- **Recommended action:** None.

---

## 19. Minor reporting residues (not methodological)

### M1 — Leftover “Pre-registered” in living documents — Minor

- **File:** `docs/manuscript.md` heading “### 7.3 Pre-registered Family B
  blocks”; `docs/methodology.md` heading “### Pre-registered Family B
  blocks”; `docs/analysis_status.md` fields “Pre-registered: Yes (B4)”
  and “Yes (B5)” (the same ledger also states “Formal preregistration:
  No” for the plan file); `docs/release_v1.0.0.md` “**Pre-registered
  Family A**”; `docs/analysis_status.md` item 1 “holdout metrics are
  confirmatory only for later comparisons.”
- **Function:** N/A (documentation).
- **Evidence:** Manuscript body and README correctly say the study is
  **not formally preregistered** and that the holdout is a first-run
  internal evaluation set. Headings and some ledger fields still use
  “Pre-registered” / “confirmatory” as shorthand for “listed in the
  documented analysis plan” or “later check.”
- **Assessment:** A reviewer skimming headings could think OSF-style
  preregistration or independent confirmation exists. The body text
  contradicts that reading. This does not change numbers or methods.
- **Recommended action:** Rename headings to “Documented Family B
  blocks” / “Plan-specified Family A.” In `analysis_status.md`, replace
  “Pre-registered: Yes” with “Listed in documented analysis plan: Yes”
  and drop “confirmatory” for the holdout. Do not edit
  `docs/pre_registration_block_ablation_plan.md` (historical lock file).
  Do not change the locked primary analysis. **Not implemented in this
  audit.**

### M2 — Leftover wording in locked generated summaries and generators — Minor

- **File:** `outputs/statistical_inference_summary.md` title
  “Pre-registered statistical inference”;
  `outputs/repeated_cv_summary.md` “final untouched benchmark”;
  `outputs/age_ablation_summary.md` and other `*_ablation_summary.md`
  “Treat the holdout only as a locked confirmation”;
  `feasibility/statistical_inference.py` module docstring and
  `write_summary` template (“Pre-registered inferential pass”;
  “confirmation only”); `feasibility/repeated_cv.py` and
  `feasibility/block_ablation.py` summary templates
  (“untouched” / “locked confirmation”);
  `feasibility/robustness_repeat_level.py` “pre-registered Nadeau–Bengio.”
- **Function:** `statistical_inference` markdown writer; ablation
  `write_summary` helpers.
- **Evidence:** These phrases are in v1.0 generated artifacts and in
  the code that would regenerate them. Regenerating those files to
  fix wording would overwrite locked v1.0 outputs.
- **Assessment:** Historical generated text overstates holdout
  independence and plan provenance. Living README/manuscript already
  correct the record. Overwriting locked summaries would be worse than
  leaving the residue, unless done as a clearly labeled documentation
  patch that does not touch numeric CSVs.
- **Recommended action:** Prefer leaving locked `outputs/*.md` unchanged.
  Optionally update *generator* strings so a future accidental re-run
  does not re-emit “Pre-registered” / “untouched.” Do not rerun
  `feasibility.statistical_inference` or ablation modules against the
  locked analysis. **Not implemented in this audit.**

### M3 — v1.1 not yet in Git HEAD — Minor

- **File:** working tree vs `HEAD` (`9a33d93`). Untracked:
  `feasibility/revision_v1_1.py`, `tests/test_revision_v1_1.py`,
  `docs/revision_v1_1_*.md`, `docs/research_chronology.md`,
  manuscript/methodology/results updates, `outputs/*v1_1*`. Tracked
  modification: `README.md`.
- **Evidence:** `git ls-tree HEAD` does not contain v1.1 outputs. A
  clone of current `HEAD` would not reproduce the bootstrap, corrected
  VIF, calibration intercept/slope, or adult sensitivities without the
  working tree.
- **Assessment:** This is a packaging/reproducibility snapshot issue,
  not an analysis error. The scientific audit is of the working tree,
  which is complete.
- **Recommended action:** When the researcher is ready, commit v1.1
  files (not `data/raw/h245.dta`, not `__pycache__`). Do not rewrite
  history. **Not implemented in this audit.**

---

## 20. Post-audit disposition

Genuine issues identified: **M1, M2, M3** (all Minor).

They can be corrected without changing the locked primary analysis:

- M1 is heading/ledger wording in living docs.
- M2 should **not** be “fixed” by regenerating locked numeric or
  summary artifacts; optional generator-string edits only.
- M3 is a later commit of already-written v1.1 files.

No redesign is indicated. No Critical or Major methodological defect
was found.

**No additional substantive methodological issue was identified in this
independent audit.**

---

## Verdict against the stated standard

A skeptical peer reviewer who inspects the actual code, locked outputs,
validation design, provenance documentation, and manuscript can
determine:

1. **What was planned:** documented Family A / Family B plan in
   `docs/pre_registration_block_ablation_plan.md`, not a formal registry
   deposit; plan creation date not independently established.
2. **What was analyzed:** unweighted person-level prediction of 2022
   any-ED use from pre-cutoff features vs three-year ED history, L2
   logistic, training-only 5×5 Nadeau–Bengio inference.
3. **What was added later:** v1.1 bootstrap, Cox calibration, drop-first
   VIF, labeled sensitivities, chronology/reporting corrections.
4. **What the model can and cannot establish:** incremental
   discrimination and (non-detected) Brier improvement on this panel;
   not causality, clinical utility, national performance, or adult ROC
   generalization.
5. **How important numbers were produced:** locked CSVs plus the
   functions named in this report.

That standard is met, with the minor heading/ledger residues above.
