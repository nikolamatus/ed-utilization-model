# Revision v1.1 notes

Substantive changes made after the audit in `docs/revision_v1_1_plan.md`.
Locked v1.0 scientific outputs were not overwritten. SHA-256 hashes of
the 46 files listed in `tests/test_diagnostics.py::LOCKED_OUTPUTS` were
unchanged after `python -m feasibility.revision_v1_1`.

`docs/pre_registration_block_ablation_plan.md` was not edited.

---

## 1. Holdout terminology

- **Original:** “untouched,” “confirmation,” “locked confirmation.”
- **Issue:** The split was scored in `feasibility.run` and used by
  `report.decide_gate` and Design A ablation.
- **Correction:** Describe it as a first-run / development-stage
  internal evaluation set. Inference remains training-only CV.
- **Reason:** Accuracy of validation claims, independent of metrics.
- **Results changed:** No.
- **Files:** README, manuscript, methodology, results, limitations,
  analysis_status, chronology.

## 2. Holdout bootstrap intervals

- **Original:** Point estimates only.
- **Issue:** n = 1,277 / 173 events needs uncertainty.
- **Correction:** Refit locked pipelines (matched `model_metrics.csv`
  to 1e-12), then percentile bootstrap of person-level `(y, p_ed,
  p_full)` pairs. B = 2,000; seed 20210915; 0 degenerate replicates.
- **Reason:** Standard reporting; seed is new and documented, not
  chosen after seeing intervals.
- **Results changed:** No change to locked points. New CIs: ΔROC 0.028
  to 0.101; ΔPR 0.047 to 0.121; ΔBrier −0.009 to −0.003.
- **Files:** `feasibility/revision_v1_1.py`,
  `outputs/holdout_bootstrap_v1_1.csv`,
  `outputs/holdout_bootstrap_v1_1_summary.md`.

## 3. Calibration intercept / slope

- **Original:** Quantile reliability diagram only; then v1.1 joint
  intercept/slope.
- **Issue (this audit):** Confirm Cox logistic definition and avoid
  reading the joint intercept as overall prevalence miscalibration.
- **Verification:** Entire first-run holdout (n = 1,277, 173 events);
  `y` ∈ {{0,1}}; `p` = predicted probability; `logit(p)` =
  log(p/(1−p)); unpenalized `logit(Y) = a + b logit(p)` via sklearn
  `C=np.inf`, matching `penalty=None` and matching independent Newton
  MLE to ~2e-4. No recalibration: production probabilities unchanged.
- **Correction:** Report calibration-in-the-large (a with b fixed at
  1) alongside the joint (a, b). Full-model CITL = 0.006; mean(p) =
  0.135 vs observed 0.135. Joint a = 0.402 is the offset at p = 0.5
  when slope is free. Slope b = 1.237: predicted logits somewhat too
  small in magnitude. Not described as severe miscalibration.
- **Results changed:** Locked model unchanged. Intercept/slope
  unchanged. CITL added as a companion quantity.
- **Files:** `outputs/holdout_calibration_v1_1.csv`,
  `outputs/holdout_bootstrap_v1_1_summary.md`.

## 4. VIF dummy trap

- **Original locked diagnostic:** VIF on production OHE without
  dropping a level; categorical VIFs infinite. **Invalid** (dummy-
  variable trap: each factor’s full dummy set plus intercept in the
  auxiliary regression is linearly dependent).
- **v1.1 correction (reconfirmed this audit):** `OneHotEncoder(drop=
  "first")` on the same training portion; auxiliary regressions include
  an intercept. All 40 VIFs finite; max 3.68; none > 5. Dropped level
  is sklearn’s default first category, not a scientific reference.
- **Not done:** No predictor removed. Production model still uses
  no-drop OHE with L2. Locked `predictor_vif.csv` preserved as the
  historical (invalid-for-categoricals) file.
- **Collinearity statement:** The corrected diagnostic does not flag
  strong linear collinearity on the reference-dropped matrix. Pairwise
  η associations remain. Independence is not proven.
- **Files:** `outputs/predictor_vif_drop_reference_v1_1.csv`,
  `outputs/predictor_vif_v1_1_notes.md`.

## 5. Analysis-plan terminology and chronology

- **Original:** “Pre-registered.”
- **Issue:** No formal registry. Plan entered Git in `12733c6`
  (2026-09-12) with code and outputs. Researcher recollection of
  earlier local drafting is not independently dated. No independently
  dated external artifact establishes a plan-creation date.
- **Correction:** “Documented / repository analysis plan.” Chronology
  table with evidence categories. Do not call the plan post-hoc on
  Git-order grounds alone. Do not rewrite Git history.
- **Results changed:** No.
- **Files:** `docs/research_chronology.md` and reporting docs.

## 6. Family A multiplicity (reporting only)

- **Original:** Plan said one Family A hypothesis; three metrics tested
  without correction.
- **Issue:** ROC *p* = 0.0226 would not survive Bonferroni ×3.
- **Correction:** Document the limitation. Do **not** apply a new
  correction (that would be result-dependent).
- **Results changed:** No. Locked p-values retained.

## 7. Nadeau–Bengio intervals from locked table

- **Original:** Mean, SE, t, p reported; no CI column.
- **Issue:** Reporting completeness.
- **Correction:** 95% CI = mean ± t_{0.975,24} × corrected SE. Formula
  audited and preserved.
- **Results changed:** No. Family A ROC CI 0.0045 to 0.0546; PR 0.0140
  to 0.0578; Brier −0.0038 to +0.0004.
- **Files:** `outputs/statistical_inference_intervals_v1_1.csv`.

## 8. Adult-only sensitivity

- **Original:** Mixed-age primary cohort (898 / 5,108 aged < 18).
- **Issue:** EMPST6 analytic missingness 16.01%; employment often
  inapplicable for children.
- **Correction:** Subset original seed-42 split to AGEY3X ≥ 18; repeat
  5×5 CV. Not a new primary.
- **Reason:** Population definition, independent of performance.
- **Results changed:** New sensitivity only. ΔROC +0.0194, *p* = 0.113
  (not detected); ΔPR +0.0299, *p* = 0.0029; ΔBrier −0.0014, *p* =
  0.196. This is **less favorable** for ROC than the primary and is
  reported as such.
- **Files:** `outputs/sensitivity_adult_only_v1_1_*`.

## 8b. Exploratory adult-only age ablation (this audit)

- **Original:** Mixed-age Family B1 (drop AGEY3X) already existed;
  adult-only sensitivity compared Full vs ED-history only.
- **Issue:** Optional diagnostic of whether age contributes
  disproportionately among adults.
- **Correction:** Same adult subset and 5×5 seed; documented B1 block
  only (`AGEY3X`). Exploratory / post-primary. Not prespecified.
- **Reason:** Infrastructure already existed; no new methodological
  decisions. Not run to explain or reverse the adult Full-vs-ED ROC.
- **Results:** CV No-age − Full ΔROC −0.0022 (*p* = 0.637); ΔPR
  −0.0007 (*p* = 0.857); ΔBrier +0.0002 (*p* = 0.642). No detected
  change. Not promoted to primary.
- **Files:** `outputs/exploratory_adult_age_ablation_v1_1_*`.

## 9. ALL9RDS sensitivity

- **Original:** YEARIND==1 primary; ALL9RDS reported not required.
- **Issue:** 225 analytic persons lack complete nine-round flags.
- **Correction:** Subset original split to ALL9RDS==1.
- **Reason:** Selection/missingness check, not result chasing.
- **Results changed:** New sensitivity. Discrimination conclusion
  unchanged (ΔROC *p* = 0.0168; ΔPR *p* = 0.0073; ΔBrier *p* = 0.120).
- **Files:** `outputs/sensitivity_all9rds_v1_1_*`.

## 10. Exclude-2020 ED count sensitivity

- **Original:** Three-year history includes ERTOTY2.
- **Issue:** 2020 utilization disruption.
- **Correction:** Same persons/split; drop ERTOTY2 from both nested
  models. Primary baseline unchanged.
- **Reason:** Pandemic disruption, specified before looking at this
  increment.
- **Results changed:** New sensitivity. ED-history holdout ROC fell
  from 0.709 to 0.684, so ΔROC rose. Interpreted as a weaker
  comparator, not stronger evidence for the original question.
- **Files:** `outputs/sensitivity_covid2020_v1_1_*`.

## 11. Analytic-cohort missingness table

- **Original:** Raw-file missingness only.
- **Correction:** `outputs/missingness_analytic_cohort_v1_1.csv`.
- **Results changed:** No modeling change.

## 12. Analyses not run

- Temporal-strict Round-6 drop: current boundary already excludes
  Round 7+ / Y4.
- Weighted primary or weighted sensitivity: different estimand; not
  original plan.
- New external test set; multiple imputation; retuning; VIF-based
  dropping; Family A Bonferroni; `python -m feasibility.run`.

## 13. Tests

Added `tests/test_revision_v1_1.py`. Existing tests retained.
