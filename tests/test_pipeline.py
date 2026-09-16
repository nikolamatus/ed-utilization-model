"""
In-memory tests for leakage, sentinels, cohort, preprocessing, and the
decision gate. No real HC-245 microdata required or accessed.
"""
import pandas as pd
import pytest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from feasibility import config, features, ingest, inspect as inspect_stage, longitudinal, modeling, report
from feasibility.config import FeatureMetadataError, FeatureSpec, validate_feature_metadata


def _survey_cols(n, yearind=1, all9=1):
    return {
        config.YEARIND: [yearind] * n,
        config.ALL9RDS: [all9] * n,
        config.LONGWT: [1.0] * n,
        config.VARSTR: [1] * n,
        config.VARPSU: [1] * n,
    }


def _toy_df():
    n = 4
    return pd.DataFrame({
        config.PERSON_ID: ["P1", "P2", "P3", "P4"],
        "ERTOTY1": [0, 1, -1, 2],
        "ERTOTY2": [0, 0, 3, 2],
        "ERTOTY3": [1, 0, 2, -7],
        "ERTOTY4": [0, 2, 1, 0],
        "SEX": [1, 2, 1, 2],
        "RACETHX": [1, 2, 3, 1],
        "AGEY3X": [40, 55, 12, 70],
        "REGIONY3": [1, 2, 3, 4],
        "MARRY6X": [1, 2, 1, 2],
        "RTHLTH6": [1, 3, 2, 4],
        "MNHLTH6": [1, 2, 3, 2],
        "INSCOVY3": [1, 2, 3, 1],
        "HAVEUS6": [1, 1, 2, 1],
        "POVCATY3": [1, 3, 4, 2],
        "TTLPY3X": [20000, 40000, -1, 80000],
        "EMPST6": [1, 2, -1, 1],
        **_survey_cols(n),
    })


def test_years_observed_table_counts_only_valid_values():
    table = longitudinal.years_observed_table(_toy_df()).set_index("years_observed")["persons"].to_dict()
    assert table[4] == 2
    assert table[3] == 2


def test_usable_population_requires_yearind_and_valid_ed():
    df = _toy_df()
    usable = longitudinal.usable_prediction_population(df)
    assert set(usable[config.PERSON_ID]) == {"P1", "P2"}

    extra = df.iloc[[0]].copy()
    extra[config.PERSON_ID] = "P5"
    extra[config.YEARIND] = 15
    extra["ERTOTY1"] = 0
    extra["ERTOTY2"] = 0
    extra["ERTOTY3"] = 0
    extra["ERTOTY4"] = 0
    combined = pd.concat([df, extra], ignore_index=True)
    usable2 = longitudinal.usable_prediction_population(combined)
    assert "P5" not in set(usable2[config.PERSON_ID])
    assert set(usable2[config.PERSON_ID]) == {"P1", "P2"}


def test_all9rds_is_reported_but_not_required():
    df = _toy_df()
    df.loc[df[config.PERSON_ID] == "P1", config.ALL9RDS] = 0
    usable = longitudinal.usable_prediction_population(df)
    assert "P1" in set(usable[config.PERSON_ID])
    summary = longitudinal.cohort_summary(df, usable)
    assert summary["n_analytic_and_all9rds"] == 1


def test_duplicate_persons_fail():
    df = _toy_df()
    df.loc[1, config.PERSON_ID] = "P1"
    with pytest.raises(longitudinal.CohortDefinitionError):
        longitudinal.assert_unique_persons(df)


def test_confirmed_hc245_predictor_names_are_accepted():
    df = _toy_df()
    audit = features.build_feature_audit(df)
    usable = features.usable_predictor_columns(audit)
    for name in (
        "AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X", "RTHLTH6",
        "MNHLTH6", "INSCOVY3", "HAVEUS6", "POVCATY3", "TTLPY3X", "EMPST6",
        "ERTOTY1", "ERTOTY2", "ERTOTY3",
    ):
        assert name in usable
        assert audit.loc[audit["feature"] == name, "allowed_by_cutoff"].iloc[0]
    assert "ERTOTY4" not in usable
    X = features.build_feature_matrix(df, usable)
    assert "ERTOTY4" not in X.columns
    features.assert_no_leakage(list(X.columns))


def test_build_feature_matrix_rejects_ertoty4():
    with pytest.raises(features.LeakageError):
        features.build_feature_matrix(_toy_df(), ["ERTOTY1", "ERTOTY4"])


def test_known_y4_predictor_cannot_enter_x():
    df = _toy_df()
    df["AGEY4X"] = [41, 56, 13, 71]
    df["INSCOVY4"] = [1, 2, 3, 1]
    with pytest.raises(features.LeakageError):
        features.build_feature_matrix(df, ["AGEY3X", "AGEY4X"])
    with pytest.raises(features.LeakageError):
        features.build_feature_matrix(df, ["INSCOVY3", "INSCOVY4"])


def test_round_8_9_predictor_cannot_enter_x():
    df = _toy_df()
    df["RTHLTH8"] = [1, 2, 3, 1]
    df["EMPST9"] = [1, 2, 1, 2]
    with pytest.raises(features.LeakageError):
        features.build_feature_matrix(df, ["RTHLTH6", "RTHLTH8"])
    with pytest.raises(features.LeakageError):
        features.build_feature_matrix(df, ["EMPST6", "EMPST9"])
    assert features.looks_post_cutoff("RTHLTH8")
    assert features.looks_post_cutoff("MNHLTH9")
    assert not features.looks_post_cutoff("RTHLTH6")
    assert not features.looks_post_cutoff("AGEY3X")


def test_post_cutoff_cannot_be_manually_marked_allowed():
    illegal = FeatureSpec(
        name="AGEY4X",
        family="demographics",
        description="should fail",
        availability_year=2022,
        time_invariant=False,
        allowed_by_cutoff=True,
        treatment="numeric",
        documentation_status="confirmed",
    )
    with pytest.raises(FeatureMetadataError):
        validate_feature_metadata(illegal)
    unknown = FeatureSpec(
        name="UNDOCUMENTED_VAR",
        family="other",
        description="unknown year",
        availability_year=None,
        time_invariant=False,
        allowed_by_cutoff=True,
        treatment="numeric",
        documentation_status="hypothesized",
    )
    with pytest.raises(FeatureMetadataError):
        validate_feature_metadata(unknown)


def test_unknown_column_fails_closed():
    with pytest.raises(features.LeakageError, match="no FeatureSpec"):
        features.build_feature_matrix(_toy_df(), ["NOT_A_REAL_VARIABLE"])


def test_every_column_in_x_has_availability_at_or_before_cutoff():
    df = _toy_df()
    audit = features.build_feature_audit(df)
    cols = features.usable_predictor_columns(audit)
    X = features.build_feature_matrix(df, cols)
    for name in X.columns:
        spec = config.FEATURE_INDEX[name]
        assert spec.allowed_by_cutoff
        if spec.time_invariant:
            continue
        assert spec.availability_year is not None
        assert spec.availability_year <= config.PREDICTION_CUTOFF_YEAR


def test_negative_sentinels_become_missing_not_numeric_values():
    series = pd.Series([0, 1, -1, -7, -8, -9, -15, 3])
    recoded = features.recode_sentinels(series)
    assert recoded.tolist()[:2] == [0.0, 1.0]
    assert recoded.iloc[2:7].isna().all()
    assert recoded.iloc[7] == 3.0

    df = _toy_df()
    X = features.build_feature_matrix(df, ["TTLPY3X", "EMPST6", "ERTOTY1"])
    assert pd.isna(X.loc[2, "TTLPY3X"])
    assert pd.isna(X.loc[2, "EMPST6"])
    assert (X["ERTOTY1"] == -1).sum() == 0


def test_build_outcome_sentinels_and_secondary_not_modeled():
    df = _toy_df()
    out = features.build_outcome(df)
    assert out["future_ed_visit"].tolist() == [0, 1, 1, 0]
    assert out["future_high_ed_use"].tolist() == [0, 1, 0, 0]
    info = features.secondary_outcome_inspection(out)
    assert info["status"] == "not_modeled_future_analysis"
    assert info["n_events"] == 1
    assert "Not modeled" in info["note"]


def test_categorical_and_numeric_split_and_pipeline():
    cols = ["AGEY3X", "SEX", "REGIONY3", "RTHLTH6", "INSCOVY3", "POVCATY3", "EMPST6", "TTLPY3X"]
    numeric, categorical = features.split_columns_by_treatment(cols)
    assert set(numeric) == {"AGEY3X", "TTLPY3X"}
    assert set(categorical) == {"SEX", "REGIONY3", "RTHLTH6", "INSCOVY3", "POVCATY3", "EMPST6"}

    df = _toy_df()
    X = features.build_feature_matrix(df, cols)
    y = features.build_outcome(df)["future_ed_visit"].astype(int)
    result, pipe, _prob = modeling.full_logistic_model(X, y, X, y, numeric, categorical)
    assert result.roc_auc is not None
    fitted = pipe.named_steps["pre"]
    trans_names = [name for name, _, _ in fitted.transformers]
    assert "cat" in trans_names and "num" in trans_names
    cat_pipe = fitted.named_transformers_["cat"]
    num_pipe = fitted.named_transformers_["num"]
    assert isinstance(cat_pipe.named_steps["impute"], SimpleImputer)
    assert isinstance(cat_pipe.named_steps["ohe"], OneHotEncoder)
    assert isinstance(num_pipe.named_steps["impute"], SimpleImputer)
    assert result.threshold_metrics_note.startswith("Threshold-dependent")


def test_calibration_is_produced():
    y = pd.Series([0, 0, 1, 1, 0, 1, 0, 1])
    p = [0.1, 0.2, 0.8, 0.7, 0.3, 0.9, 0.2, 0.6]
    table = modeling.calibration_table(y, p, n_bins=4)
    assert {"mean_predicted", "observed_fraction"} <= set(table.columns)
    assert len(table) >= 2
    points = modeling.calibration_points(y, p, n_bins=4)
    assert points == list(zip(table["mean_predicted"], table["observed_fraction"]))


def test_schema_requires_longitudinal_design_vars():
    df = _toy_df()
    ingest.validate_core_schema(df)
    slim = df.drop(columns=[config.YEARIND])
    with pytest.raises(ingest.SchemaAssumptionError, match="YEARIND"):
        ingest.validate_core_schema(slim)


def test_missingness_valid_count_excludes_sentinels():
    table = inspect_stage.missingness_table(_toy_df(), ["TTLPY3X", "EMPST6"])
    ttlp = table.set_index("variable").loc["TTLPY3X"]
    assert ttlp["sentinel_count"] == 1
    assert ttlp["valid_count"] == 3


def _gate_base(**overrides):
    ctx = {
        "usable_n": 10000,
        "n_outcome_events": 1500,
        "outcome_prevalence": 0.15,
        "families_present": ["prior_utilization", "demographics", "health_status", "access"],
        "n_allowed_candidates": 14,
        "n_present_allowed": 12,
        "longitudinal_ok": True,
        "leakage_ok": True,
        "calibration_produced": True,
        "unique_persons": True,
        "baseline2_roc_auc": 0.70,
        "baseline2_pr_auc": 0.25,
        "full_roc_auc": 0.74,
        "full_pr_auc": 0.30,
        "best_ed_baseline_roc_auc": 0.70,
        "best_ed_baseline_pr_auc": 0.25,
        "weighted": False,
    }
    ctx.update(overrides)
    return ctx


def test_decision_gate_red_when_data_inadequate():
    status, details = report.decide_gate(_gate_base(
        usable_n=50, n_outcome_events=5, outcome_prevalence=0.02, baseline2_roc_auc=0.51,
        full_roc_auc=None, full_pr_auc=None, best_ed_baseline_roc_auc=None, best_ed_baseline_pr_auc=None,
    ))
    assert status == "RED"
    assert details["components"]["data_feasibility"]["status"] == "FAIL"


def test_decision_gate_not_green_from_baseline_signal_alone():
    status, details = report.decide_gate(_gate_base(
        families_present=["prior_utilization", "demographics"],
        n_present_allowed=5,
        full_roc_auc=0.71,
        full_pr_auc=0.26,
        best_ed_baseline_roc_auc=0.70,
        best_ed_baseline_pr_auc=0.25,
    ))
    assert status != "GREEN"
    assert details["components"]["incremental_value"]["status"] != "PASS" or \
        details["components"]["data_feasibility"]["status"] == "FAIL"


def test_decision_gate_yellow_when_no_incremental_lift():
    status, details = report.decide_gate(_gate_base(
        full_roc_auc=0.705,
        full_pr_auc=0.252,
        best_ed_baseline_roc_auc=0.70,
        best_ed_baseline_pr_auc=0.25,
    ))
    assert status == "YELLOW"
    assert details["components"]["data_feasibility"]["status"] == "PASS"
    assert details["components"]["baseline_signal"]["status"] == "PASS"
    assert details["components"]["incremental_value"]["status"] == "FAIL"


def test_decision_gate_green_only_when_all_components_pass():
    status, details = report.decide_gate(_gate_base())
    assert status == "GREEN"
    assert all(c["status"] == "PASS" for c in details["components"].values())


def test_registered_metadata_is_internally_consistent():
    for spec in config.CANDIDATE_FEATURES + config.POST_CUTOFF_FEATURES:
        validate_feature_metadata(spec)
    assert config.FEATURE_INDEX["ERTOTY4"].allowed_by_cutoff is False
    assert config.FEATURE_INDEX["AGEY3X"].allowed_by_cutoff is True
    assert config.FEATURE_INDEX["AGEY4X"].allowed_by_cutoff is False
