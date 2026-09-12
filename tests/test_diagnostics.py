"""Tests for the correlation/VIF diagnostic. Does not write experiment files."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from feasibility import config, diagnostics, download, features, ingest, longitudinal

LOCKED_OUTPUTS = [
    config.OUTPUTS_DIR / "model_metrics.csv",
    config.OUTPUTS_DIR / "feasibility_summary.json",
    config.OUTPUTS_DIR / "predictions.csv",
    config.OUTPUTS_DIR / "calibration.csv",
    config.OUTPUTS_DIR / "feature_audit.csv",
    config.OUTPUTS_DIR / "population_summary.csv",
    config.OUTPUTS_DIR / "years_observed.csv",
    config.OUTPUTS_DIR / "prior_vs_future_ed.csv",
    config.OUTPUTS_DIR / "ed_utilization_summary.csv",
    config.OUTPUTS_DIR / "missingness.csv",
    config.OUTPUTS_DIR / "methodology.md",
    config.OUTPUTS_DIR / "repeated_cv_metrics.csv",
    config.OUTPUTS_DIR / "repeated_cv_summary.csv",
    config.OUTPUTS_DIR / "repeated_cv_summary.md",
    config.OUTPUTS_DIR / "feature_family_ablation.csv",
    config.OUTPUTS_DIR / "death_sensitivity.csv",
    config.OUTPUTS_DIR / "ablation_summary.md",
    config.OUTPUTS_DIR / "age_ablation_cv.csv",
    config.OUTPUTS_DIR / "age_ablation_holdout.csv",
    config.OUTPUTS_DIR / "age_ablation_summary.md",
    config.OUTPUTS_DIR / "demographic_ablation_cv.csv",
    config.OUTPUTS_DIR / "demographic_ablation_holdout.csv",
    config.OUTPUTS_DIR / "demographic_ablation_summary.md",
    config.OUTPUTS_DIR / "health_ablation_cv.csv",
    config.OUTPUTS_DIR / "health_ablation_holdout.csv",
    config.OUTPUTS_DIR / "health_ablation_summary.md",
    config.OUTPUTS_DIR / "predictor_correlation_matrix.csv",
    config.OUTPUTS_DIR / "predictor_vif.csv",
    config.FIGURES_DIR / "predictor_correlation_heatmap.png",
    config.OUTPUTS_DIR / "access_ablation_cv.csv",
    config.OUTPUTS_DIR / "access_ablation_holdout.csv",
    config.OUTPUTS_DIR / "access_ablation_summary.md",
    config.OUTPUTS_DIR / "ses_ablation_cv.csv",
    config.OUTPUTS_DIR / "ses_ablation_holdout.csv",
    config.OUTPUTS_DIR / "ses_ablation_summary.md",
    config.FIGURES_DIR / "calibration.png",
    config.FIGURES_DIR / "feature_family_ablation.png",
    config.FIGURES_DIR / "repeated_cv_incremental_value.png",
    config.FIGURES_DIR / "age_ablation.png",
    config.FIGURES_DIR / "demographic_ablation.png",
    config.FIGURES_DIR / "health_ablation.png",
    config.FIGURES_DIR / "access_ablation.png",
    config.FIGURES_DIR / "ses_ablation.png",
    config.OUTPUTS_DIR / "statistical_inference.csv",
    config.OUTPUTS_DIR / "statistical_inference_summary.md",
    config.FIGURES_DIR / "statistical_inference.png",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _locked_hashes() -> dict[str, str]:
    return {str(p): _sha256(p) for p in LOCKED_OUTPUTS if p.exists()}


def _synthetic_frame(n: int = 80) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "AGEY3X": rng.normal(40, 15, n),
        "TTLPY3X": rng.normal(20000, 8000, n),
        "ERTOTY1": rng.integers(0, 4, n),
        "ERTOTY2": rng.integers(0, 4, n),
        "ERTOTY3": rng.integers(0, 4, n),
        "SEX": rng.choice([1, 2], n),
        "RACETHX": rng.choice([1, 2, 3, 4], n),
        "REGIONY3": rng.choice([1, 2, 3, 4], n),
        "MARRY6X": rng.choice([1, 2, 3], n),
        "RTHLTH6": rng.choice([1, 2, 3, 4, 5], n),
        "MNHLTH6": rng.choice([1, 2, 3, 4, 5], n),
        "INSCOVY3": rng.choice([1, 2, 3], n),
        "HAVEUS6": rng.choice([1, 2], n),
        "POVCATY3": rng.choice([1, 2, 3, 4, 5], n),
        "EMPST6": rng.choice([1, 2, 3, 4], n),
    })


def test_pairwise_associations_expected_shape_on_synthetic():
    X = _synthetic_frame()
    cols = list(X.columns)
    assoc = diagnostics.pairwise_associations(X, cols)
    assert set(assoc.columns) == {"var_a", "var_b", "association_type", "value"}
    n_num, n_cat = 5, 10
    expected = n_num * (n_num - 1)  # pearson + spearman
    expected += n_cat * (n_cat - 1) // 2  # cramers
    expected += n_num * n_cat  # eta or point-biserial
    assert len(assoc) == expected
    assert assoc["association_type"].isin(
        {"pearson", "spearman", "cramers_v", "point_biserial", "correlation_ratio_eta"}
    ).all()
    assert assoc[["var_a", "var_b"]].apply(lambda r: r["var_a"] != r["var_b"], axis=1).all()


def test_vif_returns_design_columns_on_synthetic():
    X = _synthetic_frame()
    vif = diagnostics.variance_inflation_factors(X, list(X.columns))
    assert list(vif.columns) == ["design_column", "source_variable", "VIF"]
    assert len(vif) >= len(X.columns)
    assert vif["source_variable"].isin(X.columns).all()
    assert vif["VIF"].notna().all()


def test_perfect_numeric_collinearity_has_high_vif():
    n = 40
    x = np.linspace(0, 1, n)
    frame = pd.DataFrame({
        "AGEY3X": x,
        "TTLPY3X": 2 * x,
        "ERTOTY1": np.zeros(n),
        "SEX": [1, 2] * 20,
    })
    vif = diagnostics.variance_inflation_factors(frame, list(frame.columns))
    age_vif = vif.loc[vif["source_variable"] == "AGEY3X", "VIF"].max()
    assert age_vif > 10 or np.isinf(age_vif)


def test_cramers_v_and_eta_on_known_relationship():
    cat = pd.Series(["a", "a", "b", "b", "c", "c"])
    other = pd.Series(["x", "x", "y", "y", "z", "z"])
    assert diagnostics.cramers_v(cat, other) == pytest.approx(1.0)
    num = pd.Series([1.0, 1.0, 5.0, 5.0, 9.0, 9.0])
    assert diagnostics.correlation_ratio_eta(cat, num) == pytest.approx(1.0)


def _analytic_matrix():
    raw = download.find_raw_file()
    if raw is None:
        pytest.skip("HC-245 not present")
    df = ingest.load_data(raw)
    usable = longitudinal.usable_prediction_population(df)
    return features.build_feature_matrix(usable, diagnostics.PREDICTORS)


def test_diagnostics_run_on_analytic_cohort_without_exceptions():
    X = _analytic_matrix()
    assert X.shape[1] == 15
    assert len(X) >= 5108
    assoc = diagnostics.pairwise_associations(X, diagnostics.PREDICTORS)
    vif = diagnostics.variance_inflation_factors(X, diagnostics.PREDICTORS)
    assert set(assoc.columns) == {"var_a", "var_b", "association_type", "value"}
    assert list(vif.columns) == ["design_column", "source_variable", "VIF"]
    n_num, n_cat = 5, 10
    expected = n_num * (n_num - 1) + n_cat * (n_cat - 1) // 2 + n_num * n_cat
    assert len(assoc) == expected
    assert len(vif) >= 15
    assert vif["source_variable"].isin(diagnostics.PREDICTORS).all()


def test_diagnostic_functions_do_not_modify_locked_outputs():
    before = _locked_hashes()
    assert before, "expected locked experiment outputs to exist"
    X = _analytic_matrix()
    diagnostics.pairwise_associations(X, diagnostics.PREDICTORS)
    diagnostics.variance_inflation_factors(X, diagnostics.PREDICTORS)
    after = _locked_hashes()
    assert after == before


def test_training_portion_helper_matches_repeated_cv():
    raw = download.find_raw_file()
    if raw is None:
        pytest.skip("HC-245 not present")
    X_train = diagnostics.load_training_predictors()
    assert len(X_train) == 3831
    assert list(X_train.columns) == diagnostics.PREDICTORS
    features.assert_no_leakage(list(X_train.columns))
