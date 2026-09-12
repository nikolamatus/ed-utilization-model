# Reproducible Longitudinal ED Utilization Prediction Framework

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
(2019–2021). The full model uses only information specified as available
on or before the cutoff (or time-invariant), plus those three ED-history
counts. `ERTOTY4` and other post-cutoff fields do not enter the
predictor set.

Results are **unweighted predictive findings on the MEPS Panel 24
analytic sample**. They are not national population estimates and are
not evidence of clinical deployment performance.

## Headline results (saved outputs)

Analytic cohort: **N = 5,108** persons (`YEARIND == 1` and valid
non-sentinel `ERTOTY1`–`ERTOTY4`); **693** 2022 ED events
(prevalence **0.136**). Locked holdout: **n = 1,277** (173 events).

**Locked 25% holdout** (`outputs/model_metrics.csv`):

| Model | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|
| Prevalence only | 0.500 | 0.135 | 0.117 |
| Prior-year ED (`ERTOTY3`) | 0.627 | 0.251 | 0.108 |
| 3-year ED history | 0.709 | 0.331 | 0.105 |
| Full regularized logistic | 0.774 | 0.416 | 0.099 |

Holdout increment, full minus 3-year ED history: **+0.065 ROC-AUC**,
**+0.085 PR-AUC**. The holdout was a confirmation split. It was not used
to choose the model or to compute inferential p-values.

**Repeated 5×5 CV** on the training portion only (n = 3,831;
`outputs/repeated_cv_summary.csv`):

- ED-history mean ROC-AUC **0.685**, PR-AUC **0.307**, Brier **0.108**
- Full-model mean ROC-AUC **0.714**, PR-AUC **0.343**, Brier **0.106**
- Mean increment **+0.030 ROC-AUC**, **+0.036 PR-AUC**

**Pre-registered Family A** (Nadeau–Bengio corrected t-test, df = 24;
`outputs/statistical_inference.csv`):

- ROC-AUC mean difference **+0.0295**, *t* = 2.437, *p* = 0.0226
- PR-AUC mean difference **+0.0359**, *t* = 3.385, *p* = 0.0024
- Brier mean difference **−0.0017**, *t* = −1.655, *p* = 0.1110

The primary discrimination hypothesis is supported for ROC-AUC and
PR-AUC under the pre-specified analysis. The Brier increment was
directionally favorable and was not statistically detected under that
analysis.

**Family B** (five leave-one-block-out contrasts vs the full model,
Holm–Bonferroni within each metric): no contrast showed a statistically
detectable performance change. That is not evidence that any block is
unnecessary.

A repeat-level sensitivity analysis (df = 4) left ROC and PR
significant; it does not replace the pre-registered Nadeau–Bengio test.
See [`docs/results.md`](docs/results.md).

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
- **Validation:** 25% stratified holdout (`random_state = 42`); then
  5×5 `RepeatedStratifiedKFold` (`random_state = 2021`) on the
  reconstructed training portion only.
- **Metrics:** ROC-AUC, PR-AUC, Brier. Threshold metrics at 0.5 are
  exploratory only. Calibration is a quantile-binned reliability table
  for the first-run full model.
- **Inference:** Nadeau–Bengio corrected resampled *t*-test on 25 paired
  fold differences; Family A unadjusted; Family B Holm–Bonferroni
  separately for ROC, PR, and Brier.

Full methods: [`docs/methodology.md`](docs/methodology.md).
Limitations: [`docs/limitations.md`](docs/limitations.md).
Pre-registration: [`docs/pre_registration_block_ablation_plan.md`](docs/pre_registration_block_ablation_plan.md).
Research manuscript: [`docs/manuscript.md`](docs/manuscript.md).

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
|---|---|
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
docs/           methods, results, limitations, pre-registration
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
