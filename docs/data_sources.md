# Data sources

This project uses one public-use AHRQ file. Variable names were checked
against the HC-245 documentation (including Table 1 naming) and the
public codebook. Runtime ingest still requires the listed columns to
exist on the loaded file.

## Dataset

**AHRQ Medical Expenditure Panel Survey (MEPS), Household Component**

- **Panel 24**
- **PUF ID:** HC-245
- **File:** Panel 24, 4-Year Longitudinal Public Use File
- **Coverage:** calendar years **2019–2022** (Rounds 1–9)
- **Documentation:** https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml
- **Raw file used:** `data/raw/h245.dta`
- **Ingested shape:** 5,565 persons × 5,321 variables
  (`outputs/feasibility_summary.json`, `outputs/population_summary.csv`)
- **Person identifier:** `DUPERSID` (one row per person in this file)

The pipeline does **not** download from AHRQ. `feasibility/download.py`
locates a user-supplied `.dta` in `data/raw/` and records file size and
SHA-256 in `data/raw/provenance.json`.

Obtain the official public-use file from AHRQ (this repository does
not redistribute it):

1. Open the HC-245 documentation page above.
2. From the HC-245 download page linked there, download the
   Stata-format Data File (`.zip`).
3. Unzip it and place the resulting `.dta` file at `data/raw/h245.dta`.

Do not substitute a two-year longitudinal file and treat it as
equivalent.

## Core design variables

| Variable | Role in this study | Meaning (HC-245 / codebook) |
|---|---|---|
| `DUPERSID` | Person ID | DUID + PID. Must be unique. Duplicates fail the run. |
| `ERTOTY1` | Predictor | Emergency-room visits, calendar year 2019 |
| `ERTOTY2` | Predictor | Emergency-room visits, calendar year 2020 |
| `ERTOTY3` | Predictor | Emergency-room visits, calendar year 2021 |
| `ERTOTY4` | Outcome only | Emergency-room visits, calendar year 2022. Never a predictor. |
| `YEARIND` | Cohort inclusion | Year-participation indicator. `YEARIND == 1` means the person is in the file for all four calendar years 2019–2022 (HC-245 documentation §2.1.2). |
| `ALL9RDS` | Reported, not required | In-scope and data collected in all nine interview rounds. AHRQ’s subset for weighted national four-year estimates when used with `LONGWT`. |
| `LONGWT` | Recorded, not applied | Longitudinal weight |
| `VARSTR` | Recorded, not applied | Variance stratum |
| `VARPSU` | Recorded, not applied | Variance primary sampling unit |
| `DIED` | Sensitivity only | Used in the death-sensitivity analysis; not a predictor |

### Analytic cohort vs survey design vs predictors

- **Analytic cohort requirements:** unique `DUPERSID`; `YEARIND == 1`;
  valid (non-missing, non-sentinel) `ERTOTY1`–`ERTOTY4`. Analytic
  **N = 5,108**. `ALL9RDS == 1` count on the raw file is **4,883**;
  analytic ∩ `ALL9RDS == 1` is **4,883**. `ALL9RDS` is not an inclusion
  criterion.
- **Survey weighting / design variables:** `LONGWT`, `VARSTR`, `VARPSU`
  (and `ALL9RDS` as the AHRQ national-estimate subset flag) are required
  at ingest and recorded. They are **not** applied to sklearn metrics.
- **Predictor variables:** the 15 pre-cutoff fields listed below.

**The current predictive analysis reports unweighted analytic-sample
performance and does not make national population estimates.**

## Predictors used (pre-cutoff only)

Confirmed HC-245 names. Full-year consolidated aliases such as
`AGE42X` or `INSCOV21` are **not** used and do not exist on this file.

| Family | Name | Availability / treatment |
|---|---|---|
| Demographics | `AGEY3X` | Age as of 12/31/2021; numeric |
| Demographics | `SEX` | Time-invariant; categorical |
| Demographics | `RACETHX` | Time-invariant; categorical |
| Demographics | `REGIONY3` | Census region as of 12/31/2021; categorical |
| Demographics | `MARRY6X` | Marital status, Round 6 (2021); categorical |
| Health status | `RTHLTH6` | Perceived health, Round 6 (2021); categorical |
| Health status | `MNHLTH6` | Perceived mental health, Round 6 (2021); categorical |
| Access | `INSCOVY3` | Health insurance coverage indicator, 2021; categorical |
| Access | `HAVEUS6` | Usual source of care, Round 6 (2021); categorical |
| Socioeconomic | `POVCATY3` | Family income as % of poverty line, 2021; categorical |
| Socioeconomic | `TTLPY3X` | Person total income, 2021; numeric |
| Socioeconomic | `EMPST6` | Employment status, Round 6 (2021); categorical |
| Prior utilization | `ERTOTY1`, `ERTOTY2`, `ERTOTY3` | 2019–2021 ED counts; numeric |

Known post-cutoff counterparts (`AGEY4X`, `INSCOVY4`, `RTHLTH8`,
`RTHLTH9`, `EMPST8`, and other Y4 / Round 8–9 names) are registered as
banned. **Round 7 overlaps 2021/2022 and is not used as a predictor.**

## Sentinels, negatives, and missingness

Documented MEPS codes **−1, −7, −8, −9** (inapplicable, refused, don’t
know, not ascertained) are never treated as numeric measurements. That
named set is **not exhaustive**. Any other negative is also treated as
non-usable, including codes that appear in this HC-245 extract outside
the named list (for example `EMPST6` = −15). `features.recode_sentinels`
maps all of those values to missing. The model then applies median
imputation (numeric) or most-frequent imputation (categorical) inside
the training fold.

Raw-file missingness after this recode (`outputs/missingness.csv`,
N = 5,565) is highest for `EMPST6` (21.89% non-usable) and is typically
about 5–8% for other candidates. In the **analytic cohort**
(N = 5,108; `outputs/missingness_analytic_cohort_v1_1.csv`), `EMPST6` is
non-usable for 16.01%, overwhelmingly because employment status is
structurally inapplicable for children. Those values are mode-imputed
(modal category: employed) and must not be read as causal employment
effects. `RTHLTH6` and `MNHLTH6` missingness after recode is 0.06% and
0.10%. `HAVEUS6` is 1.27%. Other modeled predictors are complete after
recode.

Missingness is not used as a predictor. No missingness indicators were
added.

## Longitudinal completeness and deaths

Persons not in all four calendar years (`YEARIND != 1`), including many
births, late entrants, and deaths or institutionalization before 2022,
are excluded. **37** persons with `YEARIND == 1` and `DIED == 1` remain
in the primary cohort (valid 2022 ED total observed while in scope). A
sensitivity analysis dropped those decedents; full-model holdout
ROC-AUC changed from 0.774 to 0.771. That does not replace the primary
cohort.

## Constructs that are not represented

| Construct | Why unused |
|---|---|
| Homelessness / housing instability | No direct public-use homelessness variable. `SDAFRDHOME5` is an SDOH *affordable housing* item, not homelessness. It was not used and must not be relabeled as homelessness. |
| Substance-use disorder | No confirmed SUD diagnosis variable. SAQ alcohol/tobacco items are not SUD diagnoses and were not used. |
| Food insecurity | No food-security scale was used. SNAP purchase variables (`FOODSTY*`) are not a food-insecurity diagnosis and were not used. |

Related items may exist on HC-245. They are out of scope for this locked
predictor set.

## AHRQ public-use constraints

HC-245 is distributed by AHRQ as a public-use file. Users must obtain it
from AHRQ and follow AHRQ public-use conditions. This repository does
not redistribute the microdata. Do not attempt to identify individuals.

The HC-245 documentation states: “The Agency for Healthcare Research
and Quality requests that users cite AHRQ and the Medical Expenditure
Panel Survey as the data source in any publications or research based
upon these data.” AHRQ does not specify a required bibliographic format
beyond that request. The file used here is MEPS HC-245, Panel 24,
4-Year Longitudinal Public Use File (2019–2022);
https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml
