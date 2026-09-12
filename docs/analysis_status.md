# Analysis status

Research-status ledger for the locked MEPS Panel 24 analysis.

## STATUS

| Phase | Status |
|---|---|
| Exploratory / model-comparison phase | **COMPLETE** |
| Statistical inference | **COMPLETE** |
| Documentation phase | **IN PROGRESS** |

No additional exploratory ablations, model comparisons, hyperparameter
searches, or predictor-selection analyses are planned as part of this
locked analysis.

---

## Completed analyses

### 1. Initial feasibility run

- **Purpose:** Construct the analytic cohort, enforce leakage controls,
  fit prevalence / prior-year / 3-year ED / full logistic models, write
  holdout metrics, calibration, and the research triage gate.
- **Pre-registered:** No (first-run feasibility).
- **Exploratory or confirmatory:** Exploratory design lock for the
  subsequent sequence; holdout metrics are confirmatory only for later
  comparisons, not for model selection.
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

### 2. Locked holdout (same run)

- **Purpose:** 25% stratified confirmation split (seed 42).
- **Pre-registered:** Split rule fixed before later ablations;
  holdout not authorized for inference.
- **Exploratory or confirmatory:** Confirmation / generalization check.
- **Changed the production model:** No.
- **Outputs:** same first-run metric and prediction files as above.

### 3. Feature-family ablation

- **Purpose:** Add predictor families to the ED-history baseline on the
  locked holdout (Design A).
- **Pre-registered:** No.
- **Exploratory or confirmatory:** Exploratory.
- **Changed the production model:** No.
- **Outputs:** `outputs/feature_family_ablation.csv`,
  `outputs/ablation_summary.md`.
- **Command:** `python -m feasibility.ablation`.

### 4. Death sensitivity (same ablation module)

- **Purpose:** Refit / rescore after dropping `YEARIND == 1` decedents.
- **Pre-registered:** No.
- **Exploratory or confirmatory:** Sensitivity only.
- **Changed the production model:** No. Primary cohort unchanged.
- **Outputs:** `outputs/death_sensitivity.csv`.

### 5. Repeated CV

- **Purpose:** Training-only 5×5 repeated stratified CV of ED-history
  vs full model; source of Family A fold deltas.
- **Pre-registered:** Design later adopted as the locked A1 source.
- **Exploratory or confirmatory:** Descriptive CV plus locked source
  for confirmatory Family A inference.
- **Changed the production model:** No.
- **Outputs:** `outputs/repeated_cv_metrics.csv`,
  `outputs/repeated_cv_summary.csv`, `outputs/repeated_cv_summary.md`.
- **Command:** `python -m feasibility.repeated_cv`.

### 6. Age ablation (B1)

- **Purpose:** Leave-one-block-out of `AGEY3X`.
- **Pre-registered:** Contrast later listed as B1 in the locked plan
  (already run at plan date).
- **Exploratory or confirmatory:** Block ablation; later used as a
  confirmatory Family B contrast.
- **Changed the production model:** No.
- **Outputs:** `outputs/age_ablation_cv.csv`,
  `outputs/age_ablation_holdout.csv`, `outputs/age_ablation_summary.md`.
- **Command:** `python -m feasibility.age_ablation`.

### 7. Demographic ablation (B2)

- **Purpose:** Remove `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`; keep
  `AGEY3X`.
- **Pre-registered:** Listed as B2 (already run at plan date).
- **Exploratory or confirmatory:** Block ablation; later Family B.
- **Changed the production model:** No.
- **Outputs:** `outputs/demographic_ablation_cv.csv`,
  `outputs/demographic_ablation_holdout.csv`,
  `outputs/demographic_ablation_summary.md`.
- **Command:** `python -m feasibility.demographic_ablation`.

### 8. Health ablation (B3)

- **Purpose:** Remove `RTHLTH6`, `MNHLTH6`; audit analytic missingness
  on those two variables.
- **Pre-registered:** Listed as B3 (already run at plan date).
- **Exploratory or confirmatory:** Block ablation; later Family B.
- **Changed the production model:** No.
- **Outputs:** `outputs/health_ablation_cv.csv`,
  `outputs/health_ablation_holdout.csv`,
  `outputs/health_ablation_summary.md`.
- **Command:** `python -m feasibility.health_ablation`.

### 9. Predictor correlation / VIF diagnostic

- **Purpose:** Pairwise association and VIF on the training portion.
- **Pre-registered:** Execution order item 1 in the locked plan;
  diagnostic only.
- **Exploratory or confirmatory:** Diagnostic.
- **Changed the production model:** No.
- **Outputs:** `outputs/predictor_correlation_matrix.csv`,
  `outputs/predictor_vif.csv`.
- **Command:** `python -m feasibility.diagnostics`.

### 10. Pre-registration

- **Purpose:** Lock Family A / Family B contrasts, Holm plan, and the
  rule that inference waits until B4 and B5 exist.
- **Pre-registered:** This *is* the locked document.
- **Exploratory or confirmatory:** Protocol lock.
- **Changed the production model:** No.
- **Outputs:** `docs/pre_registration_block_ablation_plan.md`
  (committed 2026-09-12). **Do not edit.** The file still says B4/B5
  “Not yet run” because it was locked before those runs; that wording
  is historical lock-state text, not current project status.

### 11. Access ablation (B4)

- **Purpose:** Remove `INSCOVY3`, `HAVEUS6`.
- **Pre-registered:** Yes (B4).
- **Exploratory or confirmatory:** Pre-specified block ablation;
  descriptive file contains no p-values.
- **Changed the production model:** No.
- **Outputs:** `outputs/access_ablation_cv.csv`,
  `outputs/access_ablation_holdout.csv`,
  `outputs/access_ablation_summary.md`.
- **Command:** `python -m feasibility.access_ablation`.

### 12. SES ablation (B5)

- **Purpose:** Remove `POVCATY3`, `TTLPY3X`, `EMPST6`.
- **Pre-registered:** Yes (B5).
- **Exploratory or confirmatory:** Pre-specified block ablation;
  descriptive file contains no p-values.
- **Changed the production model:** No.
- **Outputs:** `outputs/ses_ablation_cv.csv`,
  `outputs/ses_ablation_holdout.csv`, `outputs/ses_ablation_summary.md`.
- **Command:** `python -m feasibility.ses_ablation`.

### 13. Final statistical inference

- **Purpose:** Nadeau–Bengio tests on saved fold CSVs; Family A
  unadjusted; Family B Holm within each metric.
- **Pre-registered:** Yes (method locked; executed after B4 and B5).
- **Exploratory or confirmatory:** Confirmatory for the pre-specified
  contrast set.
- **Changed the production model:** No. No refit.
- **Outputs:** `outputs/statistical_inference.csv`,
  `outputs/statistical_inference_summary.md`.
- **Command:** `python -m feasibility.statistical_inference`.

### 14. Repeat-level robustness check

- **Purpose:** One-sample t-test on five Family A repeat-level means
  (df = 4).
- **Pre-registered:** No. Additional sensitivity analysis only.
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

## Next research stage (not started)

Do **not** implement the next stage in this documentation task.

1. Documentation freeze (after human review of this package).
2. Methods / results manuscript.
3. Reproducibility packaging.
4. External / temporal validation using another appropriate public
   dataset or a later MEPS panel.

A research-freeze manifest and repository packaging pass are
explicitly out of scope until after human review.

## Figures note

The completed analysis wrote PNGs under `outputs/figures/`
(calibration, family ablation, repeated CV, block ablations,
correlation heatmap, statistical inference). Those files were not
regenerated or modified in this documentation pass. Narrative results
cite the CSV/JSON sources that generated the figures.
