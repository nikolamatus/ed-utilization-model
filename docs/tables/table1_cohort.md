# Table 1. Analytic cohort construction (unweighted)

Sources: `outputs/population_summary.csv`, `outputs/years_observed.csv`,
`outputs/death_sensitivity.csv`, `outputs/empst6_code_breakdown_v1_1.csv`.
Demographic distributions (sex, race/ethnicity, region, poverty) are
**not tabulated** because they are not stored as summary statistics in
the frozen outputs; manufacturing them would be a new analysis.

| Step / quantity | N | Notes |
|---|---:|---|
| Raw HC-245 extract | 5,565 | Unique `DUPERSID`; 5,321 variables; 0 duplicate person rows |
| Persons with 1 / 2 / 3 observed years (raw) | 191 / 160 / 106 | Not eligible under `YEARIND == 1` |
| `YEARIND == 1` and valid `ERTOTY1`–`Y4` | 5,108 | Analytic cohort |
| 2022 any-ED events (`ERTOTY4 ≥ 1`) | 693 | Prevalence 0.13567 |
| ≥2 ED visits in 2022 | 209 | Descriptive only; not modeled (prevalence 0.04092) |
| `ALL9RDS == 1` (raw and analytic intersection) | 4,883 | Selection flag; not an inclusion criterion |
| Persons aged <18 (`AGEY3X`) | 898 | Adult-only sensitivity denominator |
| `YEARIND == 1` decedents remaining in cohort | 37 | 28 in training portion, 9 in holdout |
| Training portion (75%, seed 42) | 3,831 | Stratified on the binary outcome |
| First-run holdout (25%, seed 42) | 1,277 | 173 events; prevalence 0.13547 |

Survey weights (`LONGWT`, `VARSTR`, `VARPSU`) were recorded and **not applied**.
The estimand is unweighted person-level predictive performance within this sample.
