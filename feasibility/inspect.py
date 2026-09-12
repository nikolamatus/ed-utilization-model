"""Stage 2 — Load and inspect (inspect half). All numbers are computed from df."""
import numpy as np
import pandas as pd

from . import config
from .features import recode_sentinels


def basic_shape(df: pd.DataFrame) -> dict:
    return {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "n_unique_persons": int(df[config.PERSON_ID].nunique()),
    }


def missingness_table(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    True NA and MEPS sentinels are both non-usable. valid_count excludes both.
    """
    rows = []
    for col in columns:
        if col not in df.columns:
            rows.append({
                "variable": col,
                "present_in_file": False,
                "missing_count": None,
                "sentinel_count": None,
                "nonusable_count": None,
                "missing_pct": None,
                "valid_count": None,
                "valid_pct": None,
            })
            continue
        series = df[col]
        n = len(series)
        n_true_na = int(series.isna().sum())
        numeric = pd.to_numeric(series, errors="coerce")
        n_sentinel = int(numeric.isin(config.SENTINEL_VALUES).sum())
        recoded = recode_sentinels(series)
        n_valid = int(recoded.notna().sum())
        n_nonusable = n - n_valid
        rows.append({
            "variable": col,
            "present_in_file": True,
            "missing_count": n_true_na,
            "sentinel_count": n_sentinel,
            "nonusable_count": n_nonusable,
            "missing_pct": round(100 * n_nonusable / n, 2) if n else None,
            "valid_count": n_valid,
            "valid_pct": round(100 * n_valid / n, 2) if n else None,
        })
    return pd.DataFrame(rows)


def ed_utilization_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, var in config.ED_VISIT_VARS.items():
        if var not in df.columns:
            continue
        valid = recode_sentinels(df[var]).dropna()
        rows.append({
            "year_label": label,
            "variable": var,
            "n_valid": int(valid.shape[0]),
            "zero_visits": int((valid == 0).sum()),
            "one_visit": int((valid == 1).sum()),
            "two_plus_visits": int((valid >= 2).sum()),
            "mean_visits": round(float(valid.mean()), 4) if not valid.empty else None,
            "median_visits": float(valid.median()) if not valid.empty else None,
        })
    return pd.DataFrame(rows)


def prior_vs_future_table(df: pd.DataFrame) -> pd.DataFrame:
    """2021 ED bucket → 2022 any-ED rate, among rows with valid both years."""
    prior = recode_sentinels(df[config.ED_VISIT_VARS["year3_2021"]])
    future = recode_sentinels(df[config.ED_VISIT_VARS["year4_2022"]])
    valid = prior.notna() & future.notna()
    prior, future = prior[valid], future[valid]

    bucket = pd.cut(prior, bins=[-0.1, 0.1, 1.1, 2.1, np.inf], labels=["0", "1", "2", "3+"])
    frame = pd.DataFrame({"prior_2021_bucket": bucket, "future_any_ed": (future >= 1).astype(int)})
    table = frame.groupby("prior_2021_bucket", observed=True).agg(
        n=("future_any_ed", "size"),
        future_any_ed_rate=("future_any_ed", "mean"),
    ).reset_index()
    table["future_any_ed_rate"] = table["future_any_ed_rate"].round(4)
    return table
