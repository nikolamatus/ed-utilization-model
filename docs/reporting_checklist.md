# Reporting checklist (prediction-model study)

Informed by TRIPOD / TRIPOD+AI items and PROBAST risk-of-bias concepts.
This checklist documents what the repository actually reports. It is
**not** a claim of formal TRIPOD or PROBAST compliance.

| # | Item | Where reported | Status |
| --- | --- | --- | --- |
| 1 | Title identifies a prediction-model study | `docs/manuscript.md` title | Addressed |
| 2 | Abstract: objective, design, results, predictive (not causal) interpretation | `docs/manuscript.md` §1 | Addressed; v1.1 tightens holdout/plan wording |
| 3 | Scientific question / estimand | Incremental predictive value of the full pre-cutoff model vs 3-year ED history for next-year any-ED use, unweighted, analytic sample | Addressed |
| 4 | Data source | MEPS HC-245 Panel 24, 2019–2022; `docs/data_sources.md` | Addressed |
| 5 | Study population and inclusion | Unique `DUPERSID`; `YEARIND==1`; valid `ERTOTY1`–`Y4`; N = 5,108 | Addressed |
| 6 | Unit of analysis | Person | Addressed |
| 7 | Prediction target | Any 2022 ED visit: `ERTOTY4 ≥ 1` after sentinel recode | Addressed |
| 8 | Secondary endpoint | `ERTOTY4 ≥ 2` counted, **not modeled** | Addressed |
| 9 | Prediction horizon / cutoff | Predictors through 2021-12-31; outcome calendar 2022 | Addressed |
| 10 | Predictor availability | FeatureSpec `availability_year` / time-invariant; fail-closed leakage guard | Addressed |
| 11 | Baseline model | `ERTOTY1`, `ERTOTY2`, `ERTOTY3` | Addressed |
| 12 | Full model predictors | 15 prespecified pre-cutoff fields listed in the analysis plan | Addressed |
| 13 | Sample size and events | 5,108 persons; 693 events; holdout 1,277 / 173 | Addressed |
| 14 | Missing data | Sentinels → NA; median/mode impute inside training folds; analytic missingness table in v1.1 | Addressed in v1.1 |
| 15 | Preprocessing leakage | sklearn Pipeline fit on training fold / training portion only | Addressed |
| 16 | Hyperparameters | `C=1.0` fixed; no search | Addressed |
| 17 | Validation design | 25% stratified split seed 42; then 5×5 RepeatedStratifiedKFold seed 2021 on training portion | Addressed |
| 18 | Holdout role | First-run internal evaluation; triage gate used holdout lifts; **not** external validation | Corrected in v1.1 reporting |
| 19 | Primary metrics | ROC-AUC, PR-AUC, Brier, with sign convention | Addressed; v1.1 adds holdout CIs |
| 20 | Why PR-AUC | Outcome prevalence ≈ 0.136; PR-AUC is prevalence-sensitive and complements ROC-AUC | Strengthen in v1.1 prose |
| 21 | Inferential comparison | Nadeau–Bengio on 25 paired fold deltas; Family A unadjusted; Family B Holm within metric | Implementation audited and preserved |
| 22 | Multiplicity | Family A: three complementary metrics, no correction (limitation noted). Family B: Holm m=5 per metric. Descriptive metrics unadjusted. | Addressed in v1.1 prose |
| 23 | Calibration | Locked reliability diagram; v1.1 intercept/slope assessment on holdout (not recalibration) | Addressed in v1.1 |
| 24 | Survey weights | `LONGWT`/`VARSTR`/`VARPSU` recorded, not applied; estimand is unweighted prediction | Addressed |
| 25 | Sensitivity analyses | Death (original); adult-only, ALL9RDS, exclude-2020 ED (v1.1). Temporal-strict not run (not indicated). | Addressed |
| 26 | VIF / collinearity | Original table invalid for dummies; v1.1 drop-first diagnostic; no predictor removal | Addressed in v1.1 |
| 27 | Analysis-plan provenance | Documented plan; not formal preregistration; Git ≠ research chronology | `docs/research_chronology.md` |
| 28 | Limitations | Internal validation, unweighted estimand, single panel, COVID-era panel, no clinical utility claim | `docs/limitations.md` |
| 29 | Reproducibility | Seeds 42 / 2021 / bootstrap 20210915; `pyproject.toml`; `docs/environment_v1_1.md`; pytest; locked outputs | Addressed |
| 30 | Causal language avoided | Predictive value, discrimination, calibration, incremental performance | Enforce in v1.1 edits |

## Explicitly not claimed

- Formal TRIPOD compliance
- PROBAST “low risk of bias” rating
- External or temporal validation
- Clinical usefulness / decision-curve net benefit (not evaluated)
- Nationally representative performance
- Formal preregistration
