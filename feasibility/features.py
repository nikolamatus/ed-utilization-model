"""
Stage 4 — Prediction problem, sentinel recode, feature audit, leakage guard.

A column may enter X only when:
  1. it has a FeatureSpec,
  2. temporal availability is known (or time-invariant),
  3. availability_year <= 2021,
  4. allowed_by_cutoff is True and agrees with the temporal rule,
  5. it is not a known Y4 / 2022 / Round 8–9 counterpart,
  6. it does not look like a post-cutoff HC-245 name.

Unknown availability fails closed: the feature is not used.
"""
from __future__ import annotations

import re

import pandas as pd

from . import config
from .config import FeatureMetadataError, FeatureSpec, validate_feature_metadata


class LeakageError(RuntimeError):
    pass


# Annual Y4 suffixes from HC-245 Table 1 (TOTEXPY4, AGEY4X, INSCOVY4, …).
_Y4_SUFFIX = re.compile(r"Y4(X|F|C)?$", re.IGNORECASE)
# Round 8/9 names: STEM + 8/9 + optional X/H (RTHLTH8, MARRY8X, EMPST8H).
_ROUND_89 = re.compile(r"^[A-Z]+(8|9)(X|H)?$", re.IGNORECASE)
_ROUND_89_MOD = re.compile(r"^[A-Z]+(8|9)_M\d+$", re.IGNORECASE)


def recode_sentinels(series: pd.Series) -> pd.Series:
    """
    Convert MEPS negative sentinel codes and any other negative to NA.

    Documented MEPS codes −1 / −7 / −8 / −9 (inapplicable, refused, DK,
    not ascertained) are never numeric measurements. The named set is not
    exhaustive: HC-245 also contains other negatives (for example EMPST6
    = −15). Any negative is treated as non-usable and must not be imputed
    as a numeric value.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.mask(numeric.isin(config.SENTINEL_VALUES) | (numeric < 0))


def is_valid_observed(series: pd.Series) -> pd.Series:
    return recode_sentinels(series).notna()


def looks_post_cutoff(name: str) -> bool:
    """Name-level backup so leakage is not a single-variable denylist."""
    n = name.upper()
    if n in config.POST_CUTOFF_NAMES:
        return True
    if _Y4_SUFFIX.search(n):
        return True
    if _ROUND_89.match(n) or _ROUND_89_MOD.match(n):
        return True
    return False


def assert_spec_allowed_as_predictor(spec: FeatureSpec) -> None:
    validate_feature_metadata(spec)
    if not spec.allowed_by_cutoff or not spec.is_temporally_allowed():
        raise LeakageError(
            f"{spec.name} is not allowed as a predictor "
            f"(availability_year={spec.availability_year}, "
            f"allowed_by_cutoff={spec.allowed_by_cutoff})."
        )
    if looks_post_cutoff(spec.name):
        raise LeakageError(f"{spec.name} is a post-cutoff (2022 / Y4 / R8–R9) variable.")


def _resolve_spec(name: str) -> FeatureSpec:
    spec = config.FEATURE_INDEX.get(name)
    if spec is None:
        raise LeakageError(
            f"{name} has no FeatureSpec; temporal availability is unknown. "
            "Failing closed — refusing to put it in X."
        )
    return spec


def assert_no_leakage(columns: list[str]) -> None:
    """Executable invariant: every column in X is pre-cutoff."""
    for name in columns:
        if looks_post_cutoff(name):
            raise LeakageError(
                f"Post-cutoff variable {name} cannot enter the predictor matrix."
            )
        spec = _resolve_spec(name)
        if spec.availability_year is None and not spec.time_invariant:
            raise LeakageError(
                f"{name} has unknown temporal availability and cannot enter X."
            )
        if spec.availability_year is not None and spec.availability_year > config.PREDICTION_CUTOFF_YEAR:
            raise LeakageError(
                f"{name} availability_year={spec.availability_year} is after "
                f"cutoff {config.PREDICTION_CUTOFF_YEAR}."
            )
        assert_spec_allowed_as_predictor(spec)


def build_feature_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec in config.CANDIDATE_FEATURES + config.POST_CUTOFF_FEATURES:
        present = spec.name in df.columns
        usable = bool(spec.allowed_by_cutoff and present)
        if spec.treatment == "outcome":
            reason = "OUTCOME year 2022 — must never enter X"
        elif not spec.allowed_by_cutoff:
            reason = (
                f"{spec.description} | post-cutoff "
                f"(availability_year={spec.availability_year})"
            )
        elif not present:
            reason = f"{spec.description} | NOT PRESENT under this exact name"
        else:
            reason = spec.description
        rows.append({
            "feature": spec.name,
            "source_variable": spec.name,
            "family": spec.family,
            "description": spec.description,
            "availability_year": spec.availability_year,
            "time_invariant": spec.time_invariant,
            "time_availability": (
                "time-invariant" if spec.time_invariant else str(spec.availability_year)
            ),
            "allowed_by_cutoff": spec.allowed_by_cutoff,
            "treatment": spec.treatment,
            "documentation_status": spec.documentation_status,
            "present_in_file": present,
            "usable": usable,
            "reason": reason,
        })
    return pd.DataFrame(rows)


def usable_predictor_columns(audit: pd.DataFrame) -> list[str]:
    names = audit.loc[audit["usable"], "feature"].tolist()
    assert_no_leakage(names)
    return names


def split_columns_by_treatment(columns: list[str]) -> tuple[list[str], list[str]]:
    numeric, categorical = [], []
    for name in columns:
        spec = _resolve_spec(name)
        if spec.treatment == "categorical":
            categorical.append(name)
        elif spec.treatment == "numeric":
            numeric.append(name)
        else:
            raise LeakageError(f"{name} has treatment={spec.treatment} and cannot enter X.")
    return numeric, categorical


def build_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """
    Primary outcome is modeled: future_ed_visit (ERTOTY4 >= 1).

    future_high_ed_use (ERTOTY4 >= 2) is constructed for event-count
    inspection only. It is not modeled in this feasibility experiment.
    """
    out = pd.DataFrame(index=df.index)
    visits = recode_sentinels(df[config.OUTCOME_ED_VAR])
    out["future_ed_visits"] = visits
    out["future_ed_visit"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    out.loc[visits.notna(), "future_ed_visit"] = (visits[visits.notna()] >= 1).astype("int64")
    out["future_high_ed_use"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    out.loc[visits.notna(), "future_high_ed_use"] = (visits[visits.notna()] >= 2).astype("int64")
    return out


def secondary_outcome_inspection(outcomes: pd.DataFrame) -> dict:
    """Counts only. Not a modeled endpoint and not a gate input."""
    high = outcomes["future_high_ed_use"]
    n = int(high.notna().sum())
    events = int((high == 1).sum())
    return {
        "status": "not_modeled_future_analysis",
        "definition": "future_high_ed_use = 1 if ERTOTY4 >= 2",
        "n_with_valid_outcome": n,
        "n_events": events,
        "prevalence": (events / n) if n else None,
        "note": (
            "Constructed for event-count inspection only. Not modeled, not "
            "used by the decision gate, and not claimed as part of this "
            "experiment. Adequacy of a ≥2-visit analysis is unknown until "
            "the real HC-245 file is loaded."
        ),
    }


def build_feature_matrix(df: pd.DataFrame, usable_cols: list[str]) -> pd.DataFrame:
    assert_no_leakage(usable_cols)
    frame = pd.DataFrame(index=df.index)
    for col in usable_cols:
        frame[col] = recode_sentinels(df[col])
    return frame


# Re-export for tests that construct illegal specs.
__all__ = [
    "LeakageError",
    "FeatureMetadataError",
    "recode_sentinels",
    "is_valid_observed",
    "looks_post_cutoff",
    "assert_spec_allowed_as_predictor",
    "assert_no_leakage",
    "build_feature_audit",
    "usable_predictor_columns",
    "split_columns_by_treatment",
    "build_outcome",
    "secondary_outcome_inspection",
    "build_feature_matrix",
]
