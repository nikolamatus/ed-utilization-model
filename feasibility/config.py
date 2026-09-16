"""
Central configuration for the feasibility pipeline.

Predictor names below are the confirmed HC-245 longitudinal names (AHRQ
Table 1 / public codebook), not full-year consolidated aliases.

A feature may enter X only if it is demonstrably available on or before
the prediction cutoff (2021-12-31). That rule is enforced by
`validate_feature_metadata` plus the leakage checks in `features.py`.
Unknown temporal availability is treated as not usable (fail closed).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = REPO_ROOT / "data" / "raw"
OUTPUTS_DIR = REPO_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"

MEPS_SOURCE = {
    "dataset_name": "MEPS HC-245: Panel 24, 4-Year Longitudinal Public Use File",
    "puf_id": "HC-245",
    "coverage": "2019-2022",
    "doc_url": "https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml",
    "stata_zip_hint": "Data File, Stata format (.zip) — listed on the h245 download page",
}

PERSON_ID = "DUPERSID"

# AHRQ longitudinal design variables. Required at ingest so the cohort
# rule cannot silently fall back to ED-counts-only.
YEARIND = "YEARIND"
ALL9RDS = "ALL9RDS"
LONGWT = "LONGWT"
VARSTR = "VARSTR"
VARPSU = "VARPSU"
SURVEY_DESIGN_VARS = (YEARIND, ALL9RDS, LONGWT, VARSTR, VARPSU)

# YEARIND==1 means the person has data for all four calendar years
# 2019–2022 (HC-245 documentation, section 2.1.2).
YEARIND_ALL_FOUR_YEARS = 1

PREDICTION_CUTOFF_YEAR = 2021
OUTCOME_YEAR = 2022

# Documented MEPS missing/inapplicable/refused/DK codes commonly used
# in this file. They are never valid numeric measurements. The set is
# not exhaustive: recode_sentinels() treats every negative value as
# non-usable, including codes such as EMPST6 = -15 that appear in HC-245
# but are not in this named set.
SENTINEL_VALUES = frozenset({-1, -7, -8, -9})

ED_VISIT_VARS = {
    "year1_2019": "ERTOTY1",
    "year2_2020": "ERTOTY2",
    "year3_2021": "ERTOTY3",
    "year4_2022": "ERTOTY4",
}
PREDICTOR_ED_VARS = [ED_VISIT_VARS["year1_2019"], ED_VISIT_VARS["year2_2020"], ED_VISIT_VARS["year3_2021"]]
OUTCOME_ED_VAR = ED_VISIT_VARS["year4_2022"]

RANDOM_SEED = 42


class FeatureMetadataError(ValueError):
    """Raised when allowed_by_cutoff disagrees with temporal availability."""


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    family: str
    description: str
    availability_year: int | None
    time_invariant: bool
    allowed_by_cutoff: bool
    treatment: str  # numeric | categorical | outcome
    documentation_status: str

    def is_temporally_allowed(self) -> bool:
        """True only when availability is known and on/before the cutoff."""
        if self.treatment == "outcome":
            return False
        if self.time_invariant:
            return True
        if self.availability_year is None:
            return False
        return self.availability_year <= PREDICTION_CUTOFF_YEAR


def validate_feature_metadata(spec: FeatureSpec) -> None:
    """
    Fail closed: allowed_by_cutoff must match the temporal rule.

    A post-cutoff feature cannot be marked allowed=True.
    An unknown-availability feature cannot be marked allowed=True.
    """
    computed = spec.is_temporally_allowed()
    if spec.allowed_by_cutoff != computed:
        raise FeatureMetadataError(
            f"{spec.name}: allowed_by_cutoff={spec.allowed_by_cutoff} disagrees "
            f"with temporal rule (availability_year={spec.availability_year}, "
            f"time_invariant={spec.time_invariant}, cutoff={PREDICTION_CUTOFF_YEAR}, "
            f"computed_allowed={computed})."
        )
    if spec.allowed_by_cutoff and spec.availability_year is None and not spec.time_invariant:
        raise FeatureMetadataError(
            f"{spec.name}: allowed_by_cutoff=True but temporal availability is unknown."
        )
    if (
        spec.availability_year is not None
        and spec.availability_year > PREDICTION_CUTOFF_YEAR
        and spec.allowed_by_cutoff
    ):
        raise FeatureMetadataError(
            f"{spec.name}: availability_year={spec.availability_year} is after "
            f"cutoff {PREDICTION_CUTOFF_YEAR}; cannot be allowed."
        )


def _f(
    name: str,
    family: str,
    description: str,
    availability_year: int | None,
    *,
    time_invariant: bool = False,
    treatment: str = "numeric",
    documentation_status: str = "confirmed",
) -> FeatureSpec:
    spec = FeatureSpec(
        name=name,
        family=family,
        description=description,
        availability_year=availability_year,
        time_invariant=time_invariant,
        allowed_by_cutoff=False,  # placeholder; set from the temporal rule
        treatment=treatment,
        documentation_status=documentation_status,
    )
    allowed = spec.is_temporally_allowed()
    spec = FeatureSpec(
        name=name,
        family=family,
        description=description,
        availability_year=availability_year,
        time_invariant=time_invariant,
        allowed_by_cutoff=allowed,
        treatment=treatment,
        documentation_status=documentation_status,
    )
    validate_feature_metadata(spec)
    return spec


# Confirmed HC-245 candidates available by 2021-12-31, plus the outcome row.
CANDIDATE_FEATURES: list[FeatureSpec] = [
    _f("AGEY3X", "demographics", "Age as of 12/31/2021 (edited/imputed)", 2021, treatment="numeric"),
    _f("SEX", "demographics", "Sex (time-invariant)", None, time_invariant=True, treatment="categorical"),
    _f("RACETHX", "demographics", "Race/ethnicity edited/imputed (time-invariant)", None, time_invariant=True, treatment="categorical"),
    _f("REGIONY3", "demographics", "Census region as of 12/31/2021", 2021, treatment="categorical"),
    _f("MARRY6X", "demographics", "Marital status, Round 6 (2021), edited/imputed", 2021, treatment="categorical"),
    _f("RTHLTH6", "health_status", "Perceived health status, Round 6 (2021)", 2021, treatment="categorical"),
    _f("MNHLTH6", "health_status", "Perceived mental health status, Round 6 (2021)", 2021, treatment="categorical"),
    _f("INSCOVY3", "access", "Health insurance coverage indicator, 2021", 2021, treatment="categorical"),
    _f("HAVEUS6", "access", "Usual source of care provider, Round 6 (2021)", 2021, treatment="categorical"),
    _f("POVCATY3", "socioeconomic", "Family income as % of poverty line, 2021", 2021, treatment="categorical"),
    _f("TTLPY3X", "socioeconomic", "Person total income, 2021", 2021, treatment="numeric"),
    _f("EMPST6", "socioeconomic", "Employment status, Round 6 (2021)", 2021, treatment="categorical"),
    _f("ERTOTY1", "prior_utilization", "Emergency room visits, 2019", 2019, treatment="numeric"),
    _f("ERTOTY2", "prior_utilization", "Emergency room visits, 2020", 2020, treatment="numeric"),
    _f("ERTOTY3", "prior_utilization", "Emergency room visits, 2021", 2021, treatment="numeric"),
    FeatureSpec(
        name="ERTOTY4",
        family="outcome",
        description="Emergency room visits, 2022 — PRIMARY OUTCOME, never a predictor",
        availability_year=2022,
        time_invariant=False,
        allowed_by_cutoff=False,
        treatment="outcome",
        documentation_status="confirmed",
    ),
]

# Known 2022 / Y4 / Round 8–9 counterparts. Listed so the leakage guard
# does not depend on a single outcome name. Round 7 is overlapping
# 2021/2022 and is intentionally not used as a predictor.
POST_CUTOFF_FEATURES: list[FeatureSpec] = [
    _f("AGEY4X", "demographics", "Age as of 12/31/2022 — post-cutoff", 2022, treatment="numeric"),
    _f("REGIONY4", "demographics", "Census region as of 12/31/2022 — post-cutoff", 2022, treatment="categorical"),
    _f("REGION8", "demographics", "Census region, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("REGION9", "demographics", "Census region, Round 9 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("MARRY8X", "demographics", "Marital status, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("RTHLTH8", "health_status", "Perceived health, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("RTHLTH9", "health_status", "Perceived health, Round 9 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("MNHLTH8", "health_status", "Perceived mental health, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("MNHLTH9", "health_status", "Perceived mental health, Round 9 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("INSCOVY4", "access", "Health insurance coverage indicator, 2022 — post-cutoff", 2022, treatment="categorical"),
    _f("HAVEUS8", "access", "Usual source of care, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("POVCATY4", "socioeconomic", "Poverty category, 2022 — post-cutoff", 2022, treatment="categorical"),
    _f("TTLPY4X", "socioeconomic", "Person total income, 2022 — post-cutoff", 2022, treatment="numeric"),
    _f("EMPST8", "socioeconomic", "Employment status, Round 8 (2022) — post-cutoff", 2022, treatment="categorical"),
    _f("EMPST9", "socioeconomic", "Employment status, Round 9 (2022) — post-cutoff", 2022, treatment="categorical"),
]

for _spec in CANDIDATE_FEATURES + POST_CUTOFF_FEATURES:
    validate_feature_metadata(_spec)

FEATURE_INDEX: dict[str, FeatureSpec] = {s.name: s for s in CANDIDATE_FEATURES}
for _spec in POST_CUTOFF_FEATURES:
    FEATURE_INDEX.setdefault(_spec.name, _spec)

POST_CUTOFF_NAMES = frozenset(
    {s.name for s in POST_CUTOFF_FEATURES} | {OUTCOME_ED_VAR}
)


def allowed_predictor_specs() -> list[FeatureSpec]:
    return [s for s in CANDIDATE_FEATURES if s.allowed_by_cutoff]


def numeric_predictor_names() -> list[str]:
    return [s.name for s in allowed_predictor_specs() if s.treatment == "numeric"]


def categorical_predictor_names() -> list[str]:
    return [s.name for s in allowed_predictor_specs() if s.treatment == "categorical"]
