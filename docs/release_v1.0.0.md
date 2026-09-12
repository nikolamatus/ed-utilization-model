# v1.0.0 Research Release

**Title:** Reproducible Longitudinal ED Utilization Prediction Framework

**Suggested release title:** MEPS Panel 24 Longitudinal ED Utilization Prediction Study

**Author:** Nikola Matus

**Dataset:** AHRQ Medical Expenditure Panel Survey, Panel 24, HC-245, 2019–2022

**Prediction cutoff:** 31 December 2021

**Primary outcome:** Any ED visit during calendar year 2022

**Analytic cohort:** N = 5,108

**2022 ED events:** 693

**Locked holdout:** n = 1,277

**Repeated CV:** 5×5 RepeatedStratifiedKFold on the reconstructed training portion

**Primary finding:** The full pre-cutoff model demonstrated incremental discrimination beyond three years of ED utilization history.

**Pre-registered Family A** (Nadeau–Bengio corrected *t*-test; values from `outputs/statistical_inference.csv`):

- ROC-AUC mean difference +0.0295, *p* = 0.0226
- PR-AUC mean difference +0.0359, *p* = 0.0024
- Brier mean difference −0.0017, *p* = 0.1110

## Important scope

This is a reproducible research artifact. It is **not** a clinically validated prediction model, a national risk calculator, a causal study, a deployment-ready system, or evidence of clinical utility.

Reported metrics are unweighted analytic-sample scores on MEPS Panel 24. They are not national population estimates. The locked holdout is a confirmation split. Inferential Family A results come from training-only repeated cross-validation. A ≥2-visit construct was counted descriptively and was not modeled.

## Contents of this release

- Source code (`feasibility/`)
- Tests (`tests/`)
- Methodology (`docs/methodology.md`)
- Results (`docs/results.md`)
- Limitations (`docs/limitations.md`)
- Pre-registration (`docs/pre_registration_block_ablation_plan.md`)
- Related work (`docs/related_work.md`)
- Manuscript draft (`docs/manuscript.md`)
- Saved analysis outputs (`outputs/`)

## Data availability

HC-245 is an AHRQ public-use MEPS file. This repository does **not** redistribute the microdata. Researchers must obtain the official file independently from AHRQ, place it at `data/raw/h245.dta`, and follow AHRQ public-use conditions. See `docs/data_sources.md`.

## Reproducibility

Installation, test commands, and the warning not to re-run `python -m feasibility.run` against this completed analysis are in `README.md`. The implemented methods are recorded in `docs/methodology.md`.
