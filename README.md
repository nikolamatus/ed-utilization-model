# Incremental Prediction of Future ED Utilization Beyond Historical ED Use

Research and methodology project using public-use AHRQ Medical
Expenditure Panel Survey (MEPS) data. This is **not** a clinical
prediction tool, a validated clinical model, a deployment-ready system,
a national risk calculator, a causal study, or evidence of clinical
utility.

## Research question

> How much additional predictive value can longitudinal health,
> utilization, access, demographic, and socioeconomic information
> provide beyond historical ED utilization alone?

The analysis uses MEPS Panel 24, four-year longitudinal public-use file
**HC-245 (2019–2022)**. The prediction cutoff is **31 December 2021**.
The primary outcome is **any emergency-department (ED) visit in calendar
year 2022** (`ERTOTY4 ≥ 1`). A ≥2-visit construct was counted
descriptively and was **not modeled**.

The ED-history baseline uses `ERTOTY1`, `ERTOTY2`, and `ERTOTY3`
(2019–2021). The full model uses only variables classified as available
on or before the prediction cutoff, together with time-invariant
variables, plus those three ED-history counts. `ERTOTY4` and other
post-cutoff fields do not enter the predictor set.

Results are **unweighted predictive findings on the MEPS Panel 24
analytic sample**. They are not national population estimates and are
not evidence of clinical deployment performance.

## What this study found

In this MEPS Panel 24 analytic sample, adding pre-cutoff health, utilization, access, demographic, and socioeconomic information to three years of ED history produced a mean incremental ROC-AUC of 0.0295 and PR-AUC of 0.0359 under repeated training-only cross-validation. Both discrimination increments were statistically detectable under the plan-specified Nadeau–Bengio analysis. The corresponding Brier-score difference was −0.0017 and was not statistically detected. These findings indicate incremental predictive information beyond historical ED utilization in this analytic sample, but do not establish clinical usefulness, causality, generalizability, or deployment performance.

## Headline results (saved outputs)

Analytic cohort: **N = 5,108** persons (`YEARIND == 1` and valid
non-sentinel `ERTOTY1`–`ERTOTY4`); **693** 2022 ED events
(prevalence **0.13567**). Locked holdout: **n = 1,277** (173 events).

**Locked 25% holdout** (`outputs/model_metrics.csv`):

| Model                     | ROC-AUC | PR-AUC | Brier |
| ------------------------- | ------: | -----: | ----: |
| Prevalence only           |   0.500 |  0.135 | 0.117 |
| Prior-year ED (`ERTOTY3`) |   0.627 |  0.251 | 0.108 |
| 3-year ED history         |   0.709 |  0.331 | 0.105 |
| Full regularized logistic |   0.774 |  0.416 | 0.099 |

Holdout increment, full minus 3-year ED history: **+0.065 ROC-AUC**,
**+0.085 PR-AUC**, **−0.006 Brier**. Person-level bootstrap percentile
95% CIs (B = 2,000, seed 20210915): ΔROC **0.028 to 0.101**, ΔPR
**0.047 to 0.121**, ΔBrier **−0.009 to −0.003**
(`outputs/holdout_bootstrap_v1_1.csv`). Lower Brier is better, so a
negative ΔBrier favors the full model.

The holdout point estimates are larger than the cross-validation estimates; because the holdout was part of the first-run/development-stage pipeline, the cross-validation estimates are used for the primary inferential comparison.

The 25% split is a **first-run / development-stage internal evaluation
set** (seed 42). It was scored during the original pipeline and used by
the research-triage gate. It is not an external, pristine, or
independently confirmatory sample. Inferential *p*-values come from
training-only cross-validation, not from the holdout.

**Repeated 5×5 CV** on the training portion only (n = 3,831;
`outputs/repeated_cv_summary.csv`):

- ED-history mean ROC-AUC **0.685**, PR-AUC **0.307**, Brier **0.108**
- Full-model mean ROC-AUC **0.714**, PR-AUC **0.343**, Brier **0.106**
- Mean increment **+0.030 ROC-AUC**, **+0.036 PR-AUC**, **−0.0017 Brier**

**Family A** (documented analysis plan; Nadeau–Bengio corrected t-test,
df = 24; `outputs/statistical_inference.csv` and
`outputs/statistical_inference_intervals_v1_1.csv`):

- ROC-AUC mean difference **+0.0295**, *t* = 2.437, *p* = 0.0226, 95% CI **0.0045 to 0.0546**
- PR-AUC mean difference **+0.0359**, *t* = 3.385, *p* = 0.0024, 95% CI **0.0140 to 0.0578**
- Brier mean difference **−0.0017**, *t* = −1.655, *p* = 0.1110, 95% CI **−0.0038 to +0.0004**

Under the plan-specified Nadeau–Bengio analysis, the full model showed
statistically detectable incremental ROC-AUC and PR-AUC relative to the
3-year ED-history baseline; the Brier-score increment was not
statistically detected. The study is not formally preregistered; see
[`docs/research_chronology.md`](docs/research_chronology.md).

**Family B** (five leave-one-block-out contrasts vs the full model,
Holm–Bonferroni within each metric): no contrast showed a statistically
detectable performance change. That is not evidence that any block is
unnecessary.

A repeat-level diagnostic (df = 4) is not a more conservative
inferential test: the five repeats share the same training sample, so
smaller *p*-values understate uncertainty and do not replace the
Nadeau–Bengio result. See [`docs/results.md`](docs/results.md).

v1.1 adult-only sensitivity (AGEY3X ≥ 18; train n = 3,162, holdout
n = 1,048): CV ΔROC +0.0194 (*p* = 0.113), ΔPR +0.0299 (*p* = 0.0029),
ΔBrier −0.0014 (*p* = 0.196). The adult ROC increment was not detected.
That result is reported because the mixed-age cohort is a population
definition issue; it is not used to replace the primary analysis.

## Methods (concise)

- **Data:** user-supplied `h245.dta` (5,565 persons, 5,321 variables).
  The pipeline does not download from AHRQ.
- **Cohort:** unique `DUPERSID`; `YEARIND == 1`; valid non-sentinel
  `ERTOTY1`–`Y4`. `ALL9RDS` is reported (4,883), not required.
- **Model:** L2-regularized logistic regression, `C = 1.0`,
  `random_state = 42`, `max_iter = 2000`.
- **Preprocessing:** sklearn `Pipeline` / `ColumnTransformer`; median
  impute + scale for numeric columns; most-frequent impute + one-hot
  encode for categorical columns. Fitted inside each training fold.
- **Validation:** 25% stratified first-run internal evaluation
  (`random_state = 42`); then 5×5 `RepeatedStratifiedKFold`
  (`random_state = 2021`) on the reconstructed training portion only.
- **Metrics:** ROC-AUC, PR-AUC, Brier. PR-AUC is reported because
  prevalence is modest (~0.1357); it is more sensitive to positive-class
  ranking than ROC-AUC. Lower Brier is better. Threshold metrics at 0.5
  are exploratory only. Calibration: locked reliability diagram plus
  v1.1 intercept/slope assessment on the first-run holdout (not
  recalibration).
- **Inference:** Nadeau–Bengio corrected resampled *t*-test on 25 paired
  fold differences; Family A unadjusted across three complementary
  metrics; Family B Holm–Bonferroni separately for ROC, PR, and Brier.
- **Estimand:** unweighted person-level predictive performance on the
  analytic sample. MEPS survey weights are recorded and not applied.

Software versions for the v1.1 freeze: [`docs/environment_v1_1.md`](docs/environment_v1_1.md).

Full methods: [`docs/methodology.md`](docs/methodology.md).
Limitations: [`docs/limitations.md`](docs/limitations.md).
Analysis plan (not formal preregistration): [`docs/pre_registration_block_ablation_plan.md`](docs/pre_registration_block_ablation_plan.md).
Chronology: [`docs/research_chronology.md`](docs/research_chronology.md).
Research manuscript: [`docs/manuscript.md`](docs/manuscript.md).
Publication tables: [`docs/tables/`](docs/tables/).
Publication figures (redrawn from frozen CSVs): [`docs/figures/`](docs/figures/).
Number audit: [`docs/manuscript_number_audit.md`](docs/manuscript_number_audit.md).

## What this project is not

It is not an ED intervention, early-warning system, or clinical
decision-support product. Those ideas, if pursued, would be future work
requiring external/temporal validation, clinical evaluation, and
governance that this repository does not provide.

## Reproducibility

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

Unit tests are in-memory where possible. Some tests read the saved
fold-level CSVs and, if `data/raw/h245.dta` is present, the analytic
cohort for diagnostics.

Place the official HC-245 Stata file at `data/raw/h245.dta` (see
[`docs/data_sources.md`](docs/data_sources.md)). The pipeline never fetches the file.

**Do not re-run `python -m feasibility.run` against an existing completed
analysis.** That command writes first-run holdout artifacts
(`model_metrics.csv`, `predictions.csv`, and related files) and would
overwrite locked outputs.

Later modules write **new** filenames only (ablation, repeated CV,
block ablations, diagnostics, inference, robustness). Re-running those
modules would overwrite *their* files, not the first-run holdout, but
the locked analysis is not intended to be regenerated.

Entry points that exist in the repository (for the completed sequence):

| Command | Role |
| ------- | ---- |
| `python -m feasibility.run` | First-run cohort, holdout, calibration (do not overwrite) |
| `python -m feasibility.ablation` | Feature-family add-on ablation + death sensitivity |
| `python -m feasibility.repeated_cv` | Training-only 5×5 CV |
| `python -m feasibility.age_ablation` | B1 |
| `python -m feasibility.demographic_ablation` | B2 |
| `python -m feasibility.health_ablation` | B3 |
| `python -m feasibility.diagnostics` | Correlation / VIF |
| `python -m feasibility.access_ablation` | B4 |
| `python -m feasibility.ses_ablation` | B5 |
| `python -m feasibility.statistical_inference` | Nadeau–Bengio + Holm (saved CSVs only) |
| `python -m feasibility.robustness_repeat_level` | Family A repeat-level check (saved CSVs only) |
| `python -m feasibility.revision_v1_1` | v1.1 reporting analyses only (`*_v1_1*` filenames) |

## Data use

HC-245 is an AHRQ **public-use** MEPS file. Users must obtain it from
AHRQ, follow AHRQ public-use conditions, and must not attempt to
identify individuals. This repository does not redistribute the
microdata (`data/raw/` is gitignored). Cite AHRQ and the Medical
Expenditure Panel Survey when using the data. See
[`docs/data_sources.md`](docs/data_sources.md).

## Repository layout

```
feasibility/    analysis modules
docs/           methods, results, limitations, analysis plan, chronology
tests/          unit tests
data/raw/       user-supplied h245.dta (gitignored)
outputs/        saved tables and figures from the completed analysis
```

Status ledger: [`docs/analysis_status.md`](docs/analysis_status.md).

## License

Original source code and documentation in this repository are released
under the MIT License (see [`LICENSE`](LICENSE)). That license does not
grant rights to AHRQ MEPS microdata. Users must obtain HC-245 from AHRQ
and follow AHRQ public-use conditions.

## Citation

Cite this repository using the metadata in [`CITATION.cff`](CITATION.cff).
This is a research software citation for the frozen MEPS Panel 24
analysis. It is not a peer-reviewed journal article and does not have
a DOI yet.

## Related work

A targeted review of prior ED-prediction, MEPS, and incremental-information
studies is in [`docs/related_work.md`](docs/related_work.md). In the literature reviewed, future
ED use is already known to be predictable from historical utilization and
other patient characteristics, and prior ED visits are typically a dominant
predictor. No directly matching study was identified that compared an
explicit multi-year ED-history-only baseline with a richer pre-cutoff
demographic/health/access/socioeconomic model for next-year any-ED use
on MEPS Panel 24 / HC-245. That is a positioning statement, not a claim
that no such study exists.
