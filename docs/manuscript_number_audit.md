# Manuscript number audit (v1.1.0 freeze)

Documentation only. Source artifacts were **not** altered to match the
manuscript. Rounded manuscript values are checked against saved files.
Interpretation checks record whether the manuscript statement matches
the frozen scientific meaning.

Editorial pass (publication cleanup): encoding verified as UTF-8;
incorrect “five relevant interview rounds … end in 2021” sentence was
replaced with Round 6 / Round 7 language consistent with HC-245 and
AHRQ fielding dates. Holdout point increments in the manuscript body
are now publication-rounded (+0.065 / +0.085 / −0.006); exact saved
values remain in `outputs/model_metrics.csv` and
`outputs/holdout_bootstrap_v1_1.csv`. No frozen numerical result was
changed.

Primary sources live under `outputs/`. Cohort event counts 693 and 209
were confirmed by applying the frozen cohort constructors to local
`h245.dta` without writing new model fits.

| ID | Manuscript statement | Value | Source file | Field / row | Interpretation check |
|---|---|---|---|---|---|
| A1 | Analytic N | 5,108 | `population_summary.csv` | `n_analytic_cohort` | Pass |
| A2 | Events | 693 | `docs/results.md` §A; `features.build_outcome` on frozen cohort | `future_ed_visit` sum | Pass (693/5108) |
| A3 | Abstract prevalence | 0.1357 | 693/5108 = 0.1356695 | rounded from exact 0.13567 in results ledger | Pass; methods use 0.13567 |
| A4 | Methods prevalence | 0.13567 | `docs/results.md` | Analytic prevalence | Pass |
| A5 | Training n | 3,831 | 0.75 × 5108 with stratified split seed 42; `sensitivity_*` n_train primary | 3831 | Pass |
| A6 | Holdout n | 1,277 | `model_metrics.csv` | `n_test` | Pass |
| A7 | Holdout events | 173 | `holdout_calibration_v1_1.csv` | `events` | Pass |
| A8 | Holdout prevalence | 0.13547 | `model_metrics.csv` | `prevalence` 0.13547377 | Pass |
| A9 | Raw file N / columns | 5,565 / 5,321 | `population_summary.csv` | `n_rows`, `n_columns` | Pass |
| A10 | ALL9RDS | 4,883 | `population_summary.csv` | `n_all9rds`, `n_analytic_and_all9rds` | Pass |
| A11 | Years observed 1/2/3/4 | 191/160/106/5108 | `years_observed.csv` | persons | Pass |
| A12 | In-scope decedents | 37 (28+9) | `death_sensitivity.csv` | train_dropped + test_dropped | Pass |
| A13 | Aged <18 | 898 | adult sensitivity (5108−3162−1048); `empst6_code_breakdown_v1_1.csv` | `AGEY3X,lt_18` | Pass |
| A14 | High-utilizer count / prevalence | 209 / 0.04092 | `docs/results.md`; `future_high_ed_use` sum | 209/5108=0.040916 | Pass; not modeled |
| B1 | Family A ΔROC | +0.0295 | `statistical_inference_intervals_v1_1.csv` | family A, roc_auc, `mean_difference` 0.02953897 | Pass |
| B2 | Family A ROC 95% CI | +0.0045 to +0.0546 | same | `ci_lower` 0.00452739, `ci_upper` 0.05455054 | Pass |
| B3 | Family A ROC p | 0.0226 | `statistical_inference.csv` | `raw_p_value` 0.02257265 | Pass |
| B4 | Family A ΔPR | +0.0359 | intervals | 0.03590249 | Pass |
| B5 | Family A PR 95% CI | +0.0140 to +0.0578 | intervals | 0.01400933, 0.05779566 | Pass |
| B6 | Family A PR p | 0.0024 | inference | 0.00244863 | Pass |
| B7 | Family A ΔBrier | −0.0017 | intervals | −0.00166965 | Pass; lower Brier better |
| B8 | Family A Brier 95% CI | −0.0038 to +0.0004 | intervals | −0.00375243, +0.00041312 | Pass; includes 0 |
| B9 | Family A Brier p | 0.1110 | inference | 0.11104216 | Pass; not detected |
| B10 | Family A t / SE / df | t 2.437 / 3.385 / −1.655; SE 0.0121 / 0.0106 / 0.0010; df 24 | inference | `t_statistic`, `corrected_se`, `df` | Pass |
| B11 | test/train ratio | 0.250000 | inference | `test_train_ratio` 0.250000021 | Pass |
| B12 | n estimates / repeats / splits | 25 / 5 / 5 | inference | `n_estimates`, `n_repeats`, `n_splits` | Pass |
| B13 | Bonferroni disclosure | 0.0226×3=0.0678; 0.0024×3=0.0072 | derived from rounded p | not applied | Pass; disclosed, not used to change result |
| C1 | CV ED ROC/PR/Brier means | 0.6848 / 0.3067 / 0.1077 | `repeated_cv_summary.csv` | ed_history_* mean | Pass |
| C2 | CV full ROC/PR/Brier means | 0.7143 / 0.3426 / 0.1060 | same | full_* mean | Pass |
| C3 | Fold directional counts | 23/25 ROC; 24/25 PR; 19/25 Brier | `repeated_cv_summary.csv` | n_folds_* | Pass |
| D1 | Holdout ED ROC/PR/Brier | 0.709 / 0.331 / 0.105 | `model_metrics.csv` baseline_3 | 0.709095 / 0.330794 / 0.105286 | Pass |
| D2 | Holdout full ROC/PR/Brier | 0.774 / 0.416 / 0.099 | same model_4 | 0.774006 / 0.415935 / 0.099390 | Pass |
| D3 | Holdout Δ (manuscript rounding) | +0.065 / +0.085 / −0.006 | `model_metrics.csv` / bootstrap point | +0.064911 / +0.085141 / −0.005896 | Pass; rounding for readability |
| D4 | Prior-year ED holdout ROC | 0.627 | `model_metrics.csv` baseline_2 | 0.627340 | Pass |
| D5 | Prevalence-only ROC | 0.500 | baseline_1 | 0.5 | Pass |
| D6 | Bootstrap B / seed / degenerate | 2,000 / 20210915 / 0 | `holdout_bootstrap_v1_1.csv` | n_bootstrap_*, seed, n_degenerate_skipped | Pass |
| D7 | Bootstrap ΔROC CI | 0.028–0.101 | same delta_roc_auc | 0.028135–0.100741 | Pass (manuscript rounding) |
| D8 | Bootstrap ΔPR CI | 0.047–0.121 | delta_pr_auc | 0.047334–0.121207 | Pass |
| D9 | Bootstrap ΔBrier CI | −0.009 to −0.003 | delta_brier | −0.008701 to −0.002882 | Pass |
| D10 | Holdout sensitivity/specificity at 0.5 | 0.104 / 0.995 | `model_metrics.csv` model_4 | 0.104046 / 0.994565 | Pass; exploratory only |
| E1 | Full mean predicted | 0.134892 | `holdout_calibration_v1_1.csv` full_model | `mean_predicted` 0.13489248 | Pass |
| E2 | Observed holdout rate | 0.135474 | same | `observed_prevalence` 0.13547377 | Pass |
| E3 | CITL | ≈0.006 | same | 0.005625 | Pass |
| E4 | Calibration slope | ≈1.237 | same | 1.236801 | Pass |
| E5 | Joint intercept | 0.402 | same | 0.401990 | Pass; not prevalence bias |
| F1 | EMPST6 non-usable | 818 / 16.01% | `missingness_analytic_cohort_v1_1.csv` | EMPST6 nonusable_count, missing_pct | Pass |
| F2 | EMPST6 codes −1/−7/−8/−15 | 801 / 9 / 2 / 6 | `empst6_code_breakdown_v1_1.csv` | code rows; verified on frozen cohort | Pass |
| F3 | EMPST6 non-usable age <16 | 96.5% (789/818) | same | `nonusable_AGEY3X_lt_16` | Pass |
| F4 | HAVEUS6 / RTHLTH6 / MNHLTH6 missing % | 1.27 / 0.06 / 0.10 | missingness table | missing_pct | Pass (limitations; manuscript mentions EMPST6 in body) |
| G1 | VIF columns / max / >5 | 40 / 3.68 / 0 | `predictor_vif_v1_1_notes.md`; drop-first CSV | max AGEY3X 3.68143 | Pass; diagnostic only |
| G2 | η AGE–MARRY / POV–income | 0.8099 / 0.5975 | `predictor_correlation_matrix.csv` | AGEY3X–MARRY6X 0.809889; POVCATY3–TTLPY3X 0.597505 | Pass as diagnostic, not removal |
| H1 | Family B Holm: none detected | all `significant_at_0.05` False | `statistical_inference.csv` family B | Holm p ≥ 0.7019 | Pass; blocks not ranked |
| H2 | B1–B5 ROC means | −0.0051, +0.0062, +0.0049, −0.0018, +0.0019 | same | mean_difference | Pass |
| H3 | Remaining ΔROC vs ED ≈ +0.024 to +0.036 | derived Full Δ + (reduced−full) | 0.0244 to 0.0358 | Pass; descriptive |
| H4 | Design A ED+demographics ΔROC | +0.043 | `feature_family_ablation.csv` ed_demographics | 0.043332 | Pass; exploratory holdout |
| I1 | Adult train/holdout/events | 3,162 / 1,048 / 166 | `sensitivity_adult_only_v1_1_inference.csv` | n_train, n_holdout, holdout_events | Pass |
| I2 | Adult ΔROC / p / CI | +0.0194 / 0.113 / −0.0050 to 0.0438 | same roc_auc | 0.019400; p 0.113359; CI −0.004965, 0.043766 | Pass; not a replacement primary |
| I3 | Adult ΔPR / p | +0.0299 / 0.0029 | pr_auc | 0.029943; p 0.002926 | Pass |
| I4 | Adult ΔBrier / p | −0.0014 / 0.196 | brier | −0.001370; p 0.195777 | Pass |
| I5 | Exploratory adult B1 ΔROC / p | −0.0022 / 0.637 | `exploratory_adult_age_ablation_v1_1_inference.csv` | −0.002208; p 0.637128 | Pass; post-primary |
| I6 | ALL9RDS n / ΔROC / p | 3,663 / 1,220; +0.0311; 0.0168 | `sensitivity_all9rds_v1_1_inference.csv` | matches | Pass; not primary |
| I7 | ALL9RDS ΔPR / ΔBrier | +0.0381 p=0.0073; −0.0018 p=0.120 | same | 0.038073 / −0.001819 | Pass |
| I8 | Exclude ERTOTY2 ΔROC | +0.0460 p=0.0006 | `sensitivity_covid2020_v1_1_inference.csv` | 0.045964; p 0.000593 | Pass; weaker comparator |
| I9 | Exclude ERTOTY2 holdout ED ROC | 0.684 vs 0.709 | same `holdout_ed`; model_metrics 0.709 | 0.683919 vs 0.709095 | Pass |
| I10 | Death holdout ROC path | 0.774006 → 0.772214 → 0.770905 | `death_sensitivity.csv` | roc_auc rows | Pass; cohort unchanged |
| J1 | Repeat-level p (ROC/PR/Brier) | 0.0003 / 0.0003 / 0.0006 | `robustness_repeat_level_test.csv` | 0.000265 / 0.000290 / 0.000621; df=4 | Pass; diagnostic, understates uncertainty |
| J2 | Repeat-level means (rounded) | see manuscript §3.8 | same repeat_*_mean | matches prior draft rounding | Pass |
| K1 | Seeds | 42 / 2021 / 20210915 | config; bootstrap CSV; CV files | holdout / RepeatedStratifiedKFold / bootstrap | Pass |
| K2 | C / max_iter | 1.0 / 2000 | methodology / modeling.py | fixed; no search | Pass |
| K3 | Weights applied | false | `population_summary.csv` | `weights_applied` | Pass |
| K4 | Git plan incorporation | 2026-09-12 | `docs/research_chronology.md` | first research commit | Pass; not formal preregistration |

## Consistency search (living manuscript)

Terms checked in `docs/manuscript.md` after the publication rewrite:

| Term | Allowed use in manuscript | Issue? |
|---|---|---|
| pre-registered / preregistered | Only to deny formal preregistration and to note locked filename/historical artifacts | No |
| conservative (inferential) | Not used for the repeat-level test | No |
| external validation | Only negated | No |
| nationally representative | MEPS survey *design* distinguished from this study’s estimand; results not claimed as national | No |
| causal | Only negated | No |
| avoidance / preventable | Only negated | No |
| clinical decision support | Only negated | No |

Locked v1.0 files (for example `outputs/robustness_repeat_level_test.csv` note field “pre-registered”, generated v1.0 summaries) may still contain historical wording. They were not rewritten.

## Conflicts left untouched

- Locked v1.0 VIF table still contains infinities from the dummy-variable trap; the manuscript uses the v1.1 drop-first diagnostic and states that the locked table is invalid for dummies.
- Locked repeat-level CSV note still says the procedure does not replace the “pre-registered” Nadeau–Bengio test. Living text says documented analysis plan.
