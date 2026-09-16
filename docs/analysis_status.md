# Analysis status

Research-status ledger for the locked MEPS Panel 24 analysis.

## STATUS

| Phase | Status |
|---|---|
| Exploratory / model-comparison phase | **COMPLETE** |
| Statistical inference | **COMPLETE** |
| Documentation phase | **COMPLETE** |

No additional exploratory ablations, model comparisons, hyperparameter
searches, or predictor-selection analyses are planned as part of this
locked analysis.

---

## Completed analyses

### 1. Initial feasibility run

- **Purpose:** Construct the analytic cohort, enforce leakage controls,
  fit prevalence / prior-year / 3-year ED / full logistic models, write
  holdout metrics, calibration, and the research triage gate.
- **Documented analysis plan:** No (first-run feasibility).
- **Classification:** Exploratory design lock for the subsequent
  sequence. Holdout metrics are first-run internal evaluation scores,
  not independently confirmatory validation and not used for model
  selection.
- **Changed the production model:** Defined it. Later work did not
  replace the predictor set, cohort, or estimator.
- **Outputs:** `outputs/model_metrics.csv`, `outputs/predictions.csv`,
  `outputs/calibration.csv`, `outputs/population_summary.csv`,
  `outputs/missingness.csv`, `outputs/ed_utilization_summary.csv`,
  `outputs/prior_vs_future_ed.csv`, `outputs/years_observed.csv`,
  `outputs/feature_audit.csv`, `outputs/feasibility_summary.json`,
  `outputs/methodology.md`.
- **Command:** `python -m feasibility.run` — **do not re-run** against
  this completed analysis (overwrites first-run files).

### 2. First-run holdout (same run)

- **Purpose:** 25% stratified first-run internal evaluation (seed 42).
- **Documented analysis plan:** Split rule later used as the locked
  reconstruction; holdout not authorized for inference.
- **Classification:** Development-stage internal evaluation; not
  external confirmation.
- **Changed the production model:** No.
- **Outputs:** same first-run metric and prediction files as above.

### 3. Feature-family ablation

- **Purpose:** Add predictor families to the ED-history baseline on the
  locked holdout (Design A).
- **Documented analysis plan:** No.
- **Exploratory or confirmatory:** Exploratory.
- **Changed the production model:** No.
- **Outputs:** `outputs/feature_family_ablation.csv`,
  `outputs/ablation_summary.md`.
- **Command:** `python -m feasibility.ablation`.

### 4. Death sensitivity (same ablation module)

- **Purpose:** Refit / rescore after dropping `YEARIND == 1` decedents.
- **Documented analysis plan:** No.
- **Exploratory or confirmatory:** Sensitivity only.
- **Changed the production model:** No. Primary cohort unchanged.
- **Outputs:** `outputs/death_sensitivity.csv`.

### 5. Repeated CV

- **Purpose:** Training-only 5×5 repeated stratified CV of ED-history
  vs full model; source of Family A fold deltas.
- **Documented analysis plan:** Design later adopted as the locked A1 source.
- **Classification:** Descriptive CV plus locked source for Family A
  inference.
- **Changed the production model:** No.
- **Outputs:** `outputs/repeated_cv_metrics.csv`,
  `outputs/repeated_cv_summary.csv`, `outputs/repeated_cv_summary.md`.
- **Command:** `python -m feasibility.repeated_cv`.

### 6. Age ablation (B1)

- **Purpose:** Leave-one-block-out of `AGEY3X`.
- **Documented analysis plan:** Contrast later listed as B1 in the locked plan
  (already run at plan date).
- **Classification:** Block ablation; later used as a Family B contrast.
- **Changed the production model:** No.
- **Outputs:** `outputs/age_ablation_cv.csv`,
  `outputs/age_ablation_holdout.csv`, `outputs/age_ablation_summary.md`.
- **Command:** `python -m feasibility.age_ablation`.

### 7. Demographic ablation (B2)

- **Purpose:** Remove `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`; keep
  `AGEY3X`.
- **Documented analysis plan:** Listed as B2 (already run at plan date).
- **Exploratory or confirmatory:** Block ablation; later Family B.
- **Changed the production model:** No.
- **Outputs:** `outputs/demographic_ablation_cv.csv`,
  `outputs/demographic_ablation_holdout.csv`,
  `outputs/demographic_ablation_summary.md`.
- **Command:** `python -m feasibility.demographic_ablation`.

### 8. Health ablation (B3)

- **Purpose:** Remove `RTHLTH6`, `MNHLTH6`; audit analytic missingness
  on those two variables.
- **Documented analysis plan:** Listed as B3 (already run at plan date).
- **Exploratory or confirmatory:** Block ablation; later Family B.
- **Changed the production model:** No.
- **Outputs:** `outputs/health_ablation_cv.csv`,
  `outputs/health_ablation_holdout.csv`,
  `outputs/health_ablation_summary.md`.
- **Command:** `python -m feasibility.health_ablation`.

### 9. Predictor correlation / VIF diagnostic

- **Purpose:** Pairwise association and VIF on the training portion.
- **Documented analysis plan:** Execution order item 1 in the locked plan;
  diagnostic only.
- **Exploratory or confirmatory:** Diagnostic.
- **Changed the production model:** No.
- **Outputs:** `outputs/predictor_correlation_matrix.csv`,
  `outputs/predictor_vif.csv`.
- **Command:** `python -m feasibility.diagnostics`.

### 10. Repository analysis plan

- **Purpose:** Lock Family A / Family B contrasts, Holm plan, and the
  rule that inference waits until B4 and B5 exist.
- **Formal preregistration:** No. Documented repository analysis plan.
  See `docs/research_chronology.md`.
- **Classification:** Protocol lock for later B4/B5 and the statistical pass.
- **Changed the production model:** No.
- **Outputs:** `docs/pre_registration_block_ablation_plan.md`
  (entered Git 2026-09-12). **Do not edit.** The file still says B4/B5
  “Not yet run” because it was locked before those runs; that wording
  is historical lock-state text, not current project status.

### 11. Access ablation (B4)

- **Purpose:** Remove `INSCOVY3`, `HAVEUS6`.
- **Documented analysis plan:** Yes (B4).
- **Exploratory or confirmatory:** Pre-specified block ablation;
  descriptive file contains no p-values.
- **Changed the production model:** No.
- **Outputs:** `outputs/access_ablation_cv.csv`,
  `outputs/access_ablation_holdout.csv`,
  `outputs/access_ablation_summary.md`.
- **Command:** `python -m feasibility.access_ablation`.

### 12. SES ablation (B5)

- **Purpose:** Remove `POVCATY3`, `TTLPY3X`, `EMPST6`.
- **Documented analysis plan:** Yes (B5).
- **Exploratory or confirmatory:** Pre-specified block ablation;
  descriptive file contains no p-values.
- **Changed the production model:** No.
- **Outputs:** `outputs/ses_ablation_cv.csv`,
  `outputs/ses_ablation_holdout.csv`, `outputs/ses_ablation_summary.md`.
- **Command:** `python -m feasibility.ses_ablation`.

### 13. Final statistical inference

- **Purpose:** Nadeau–Bengio tests on saved fold CSVs; Family A
  unadjusted; Family B Holm within each metric.
- **Documented analysis plan:** Yes (method locked; executed after B4 and B5).
- **Classification:** Primary inferential pass for the documented contrast set.
- **Changed the production model:** No. No refit.
- **Outputs:** `outputs/statistical_inference.csv`,
  `outputs/statistical_inference_summary.md`.
- **Command:** `python -m feasibility.statistical_inference`.

### 14. Repeat-level robustness check

- **Purpose:** One-sample t-test on five Family A repeat-level means
  (df = 4). Descriptive sensitivity only; repeats share the same
  training sample, so smaller p-values are not stronger evidence.
- **Documented analysis plan:** No. Additional sensitivity analysis only.
- **Exploratory or confirmatory:** Sensitivity; does not replace
  Nadeau–Bengio.
- **Changed the production model:** No. No refit.
- **Outputs:** `outputs/robustness_repeat_level_test.csv`,
  `outputs/robustness_repeat_level_summary.md`.
- **Command:** `python -m feasibility.robustness_repeat_level`.

---

## Locked statement

No additional exploratory ablations, model comparisons, hyperparameter
searches, or predictor-selection analyses are planned as part of this
locked analysis.

---

## v1.1 publication revision (later; not part of the v1.0 lock)

These analyses were added after the frozen v1.0 result set. They do
not overwrite locked files and do not replace Family A / Family B.

| Analysis | Classification | Outputs |
|---|---|---|
| Holdout bootstrap CIs | Post-development reporting | `outputs/holdout_bootstrap_v1_1.*` |
| Holdout calibration intercept/slope | Exploratory assessment | `outputs/holdout_calibration_v1_1.csv` |
| VIF with reference drop | Diagnostic correction | `outputs/predictor_vif_drop_reference_v1_1.csv` |
| Analytic-cohort missingness | Reporting | `outputs/missingness_analytic_cohort_v1_1.csv` |
| NB 95% CIs from locked table | Reporting | `outputs/statistical_inference_intervals_v1_1.csv` |
| Adult-only Full vs ED-history | Sensitivity | `outputs/sensitivity_adult_only_v1_1_*` |
| Adult-only age ablation (drop AGEY3X) | Exploratory / post-primary | `outputs/exploratory_adult_age_ablation_v1_1_*` |
| ALL9RDS==1 | Sensitivity | `outputs/sensitivity_all9rds_v1_1_*` |
| Exclude ERTOTY2 | Sensitivity | `outputs/sensitivity_covid2020_v1_1_*` |

Command: `python -m feasibility.revision_v1_1`.

Chronology: [`docs/research_chronology.md`](research_chronology.md).
Notes: [`docs/revision_v1_1_notes.md`](revision_v1_1_notes.md).
Completion: [`docs/revision_v1_1_completion.md`](revision_v1_1_completion.md).

---

A research manuscript draft is complete and is in
`docs/manuscript.md`.

## Next research stage (not started)

1. External / temporal validation using another appropriate public
   dataset or a later MEPS panel.

## Figures note

The completed analysis wrote PNGs under `outputs/figures/`
(calibration, family ablation, repeated CV, block ablations,
correlation heatmap, statistical inference). Those files were not
regenerated or modified in this documentation pass. Narrative results
cite the CSV/JSON sources that generated the figures.
