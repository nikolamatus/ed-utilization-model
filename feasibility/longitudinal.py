"""
Stage 3 — Longitudinal cohort.

Primary analytic cohort (unweighted predictive experiment)
--------------------------------------------------------
A person is eligible when ALL of the following hold:

1. YEARIND == 1
   AHRQ's constructed flag for "person is in the file for all four
   calendar years 2019–2022" (HC-245 documentation §2.1.2). This is the
   design-relevant inclusion for a 2019–2021 → 2022 prediction.

2. Valid (non-missing, non-sentinel) ERTOTY1, ERTOTY2, ERTOTY3, ERTOTY4
   so predictors and the 2022 outcome can actually be constructed.

3. Unique DUPERSID (duplicate person rows fail the run).

Why YEARIND==1 and not ALL9RDS==1
---------------------------------
ALL9RDS==1 means in-scope *and* data collected in all nine interview
rounds. AHRQ recommends that subset (with LONGWT) for nationally
representative four-year longitudinal *estimates*.

This experiment is an unweighted predictive exercise on an analytic
sample. YEARIND==1 matches the four-year window without additionally
requiring complete nine-round interview participation. People who were
in all four years but missed a round can still have valid annual ED
totals; dropping them would be an ALL9RDS complete-case restriction
that is more appropriate for weighted population inference, which this
pass does not perform.

ALL9RDS is required to exist on the file and is reported (overlap with
the analytic cohort) so the limitation is visible. It is not an
inclusion criterion.

Deaths, births, attrition
-------------------------
- Births / late entrants (ENTRSRVY) and people not in all four years
  have YEARIND != 1 and are excluded.
- Deaths or institutionalization in 2019–2021 typically imply YEARIND
  != 1 or a sentinel on a later ERTOT year, and are excluded.
- Deaths in 2022 with YEARIND==1 and a valid ERTOTY4 remain eligible;
  their 2022 utilization is observed for however long they were in
  scope. This is a limitation, not silently "fixed."

Survey weights
--------------
LONGWT, VARSTR, and VARPSU are required at ingest and recorded. They
are not applied to the sklearn metrics. Results are unweighted
predictive performance on this analytic sample, not national estimates.
"""
from __future__ import annotations

import pandas as pd

from . import config
from .features import is_valid_observed


class CohortDefinitionError(RuntimeError):
    pass


def duplicate_person_check(df: pd.DataFrame) -> dict:
    n_rows = len(df)
    n_unique = df[config.PERSON_ID].nunique()
    return {
        "n_rows": n_rows,
        "n_unique_persons": n_unique,
        "n_duplicate_person_rows": n_rows - n_unique,
    }


def assert_unique_persons(df: pd.DataFrame) -> None:
    dup = df[config.PERSON_ID].duplicated()
    if dup.any():
        raise CohortDefinitionError(
            f"{int(dup.sum())} duplicate {config.PERSON_ID} values; "
            "cannot treat rows as unique persons."
        )


def years_observed_table(df: pd.DataFrame) -> pd.DataFrame:
    valid_flags = pd.DataFrame(index=df.index)
    for var in config.ED_VISIT_VARS.values():
        valid_flags[var] = is_valid_observed(df[var])
    years_observed = valid_flags.sum(axis=1)
    counts = years_observed.value_counts().sort_index()
    return counts.rename_axis("years_observed").reset_index(name="persons")


def valid_ed_all_four_years(df: pd.DataFrame) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for var in config.PREDICTOR_ED_VARS + [config.OUTCOME_ED_VAR]:
        mask &= is_valid_observed(df[var])
    return mask


def yearind_all_four_years(df: pd.DataFrame) -> pd.Series:
    yearind = pd.to_numeric(df[config.YEARIND], errors="coerce")
    return yearind == config.YEARIND_ALL_FOUR_YEARS


def all9rds_complete(df: pd.DataFrame) -> pd.Series:
    flag = pd.to_numeric(df[config.ALL9RDS], errors="coerce")
    return flag == 1


def complete_four_year_cases(df: pd.DataFrame) -> int:
    """Rows with valid ED counts in all four years (not the analytic cohort)."""
    return int(valid_ed_all_four_years(df).sum())


def usable_prediction_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Primary analytic cohort: YEARIND==1 AND valid ED counts in 2019–2022.
    """
    if config.YEARIND not in df.columns:
        raise CohortDefinitionError(
            f"{config.YEARIND} is required for the longitudinal cohort rule."
        )
    mask = yearind_all_four_years(df) & valid_ed_all_four_years(df)
    return df.loc[mask].copy()


def cohort_summary(df: pd.DataFrame, usable: pd.DataFrame) -> dict:
    n_all9 = int(all9rds_complete(df).sum()) if config.ALL9RDS in df.columns else None
    n_usable_and_all9 = (
        int(all9rds_complete(usable).sum()) if config.ALL9RDS in usable.columns else None
    )
    return {
        "cohort_rule": "YEARIND==1 AND valid non-sentinel ERTOTY1–Y4",
        "why_not_all9rds": (
            "ALL9RDS==1 is the AHRQ subset for weighted national longitudinal "
            "estimates. This experiment is unweighted prediction; YEARIND==1 "
            "matches the 2019–2022 window without requiring complete 9-round "
            "interviews."
        ),
        "n_raw": int(len(df)),
        "n_yearind_all_four_years": int(yearind_all_four_years(df).sum()),
        "n_valid_ed_all_four_years": int(valid_ed_all_four_years(df).sum()),
        "n_all9rds": n_all9,
        "n_analytic_cohort": int(len(usable)),
        "n_analytic_and_all9rds": n_usable_and_all9,
        "weights_applied": False,
        "survey_weight_note": (
            "LONGWT/VARSTR/VARPSU are recorded if present and are not applied. "
            "Metrics are unweighted predictive performance on the analytic "
            "sample, not nationally representative MEPS estimates."
        ),
    }
