"""
Stage 2 — Load and inspect (load half).

Loads the Stata (.dta) release of HC-245. Hard-fails if core identifier,
ED-year, or AHRQ longitudinal-design variables are absent.
"""
import pandas as pd

from . import config


class SchemaAssumptionError(RuntimeError):
    pass


def load_data(path) -> pd.DataFrame:
    df = pd.read_stata(path, convert_categoricals=False)
    df.columns = [c.upper() for c in df.columns]
    validate_core_schema(df)
    return df


def validate_core_schema(df: pd.DataFrame) -> None:
    missing = []
    if config.PERSON_ID not in df.columns:
        missing.append(config.PERSON_ID)
    for label, var in config.ED_VISIT_VARS.items():
        if var not in df.columns:
            missing.append(f"{var} ({label})")
    for var in config.SURVEY_DESIGN_VARS:
        if var not in df.columns:
            missing.append(var)

    if missing:
        raise SchemaAssumptionError(
            "The downloaded file does not contain the variables this pipeline "
            f"requires. Missing: {missing}. HC-245 must include DUPERSID, "
            "ERTOTY1–Y4, YEARIND, ALL9RDS, LONGWT, VARSTR, and VARPSU. "
            "Refusing to guess or silently drop the cohort/design rule."
        )

    if df[config.PERSON_ID].isna().any():
        raise SchemaAssumptionError(
            f"{config.PERSON_ID} contains missing values; cannot uniquely identify persons."
        )

    for var in config.ED_VISIT_VARS.values():
        col = df[var]
        non_numeric = pd.to_numeric(col, errors="coerce").isna() & col.notna()
        if non_numeric.any():
            raise SchemaAssumptionError(
                f"{var} contains non-numeric values that failed to coerce; expected a visit count."
            )
        real_values = pd.to_numeric(col, errors="coerce").dropna()
        implausible = real_values[
            (real_values < -9) | ((real_values > 0) & (real_values != real_values.round()))
        ]
        if not implausible.empty:
            raise SchemaAssumptionError(
                f"{var} contains values outside the expected "
                "{sentinels ∪ non-negative integers} range."
            )
