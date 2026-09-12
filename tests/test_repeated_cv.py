"""In-memory tests for training-only repeated CV. No real HC-245 required."""
import numpy as np
import pandas as pd
import pytest

from feasibility import config, features, modeling, repeated_cv


def test_cv_predictor_sets_match_production_and_are_leakage_safe():
    features.assert_no_leakage(repeated_cv.ED_COLUMNS)
    features.assert_no_leakage(repeated_cv.FULL_COLUMNS)
    assert repeated_cv.ED_COLUMNS == config.PREDICTOR_ED_VARS
    assert set(repeated_cv.FULL_COLUMNS) == {s.name for s in config.allowed_predictor_specs()}
    assert config.OUTCOME_ED_VAR not in repeated_cv.FULL_COLUMNS
    assert not any(features.looks_post_cutoff(c) for c in repeated_cv.FULL_COLUMNS)


def test_training_portion_matches_production_split_and_leaves_holdout_aside():
    rng = np.random.default_rng(1)
    n = 80
    y = pd.Series([0] * 60 + [1] * 20)
    X = pd.DataFrame({
        "ERTOTY1": rng.integers(0, 3, n),
        "AGEY3X": rng.integers(18, 80, n),
    })
    X_tr, y_tr, X_ho, y_ho = repeated_cv.training_portion(X, y)
    prod_tr, prod_te, prod_ytr, prod_yte = modeling._split(X, y)
    pd.testing.assert_index_equal(X_tr.index, prod_tr.index)
    pd.testing.assert_series_equal(y_tr, prod_ytr)
    pd.testing.assert_index_equal(X_ho.index, prod_te.index)
    assert len(X_tr) + len(X_ho) == n
    assert len(X_ho) == 20  # 25% of 80


def test_cv_splitter_is_5x5_with_recorded_seed():
    splitter = repeated_cv.cv_splitter()
    assert splitter.get_n_splits() == 25
    assert getattr(splitter, "n_repeats", 5) == 5
    assert splitter.random_state == 2021
    y = np.array([0] * 40 + [1] * 40)
    X = np.zeros((80, 1))
    pairs = list(splitter.split(X, y))
    assert len(pairs) == 25
    assert repeated_cv.HOLDOUT_SEED == 42
    assert repeated_cv.CV_RANDOM_STATE == 2021


def test_describe_numeric_and_summary_counts():
    values = pd.Series([0.02, 0.03, 0.04, 0.05, 0.06])
    stats = repeated_cv.describe_numeric(values)
    assert stats["n"] == 5
    assert stats["mean"] == pytest.approx(0.04)
    assert stats["min"] == 0.02
    assert stats["max"] == 0.06
    fold_df = pd.DataFrame({
        "ed_roc_auc": [0.70] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.76] * 24 + [0.69],
        "full_pr_auc": [0.36] * 25,
        "full_brier": [0.10] * 25,
        "delta_roc_auc": [0.06] * 24 + [-0.01],
        "delta_pr_auc": [0.06] * 25,
        "delta_brier": [-0.01] * 25,
    })
    summary = repeated_cv.summary_table(fold_df)
    counts = summary.set_index("metric")
    assert counts.loc["n_folds_positive_delta_roc_auc", "mean"] == 24
    assert counts.loc["n_folds_positive_delta_pr_auc", "mean"] == 25
    assert counts.loc["n_folds_brier_improved", "mean"] == 25


def test_run_repeated_cv_stays_inside_training_rows():
    rng = np.random.default_rng(2)
    n = 120
    y = pd.Series([0] * 90 + [1] * 30)
    X = pd.DataFrame({
        "ERTOTY1": rng.integers(0, 4, n),
        "ERTOTY2": rng.integers(0, 4, n),
        "ERTOTY3": rng.integers(0, 4, n),
        "AGEY3X": rng.integers(10, 80, n),
        "SEX": rng.integers(1, 3, n),
        "RACETHX": rng.integers(1, 4, n),
        "REGIONY3": rng.integers(1, 5, n),
        "MARRY6X": rng.integers(1, 4, n),
        "RTHLTH6": rng.integers(1, 6, n),
        "MNHLTH6": rng.integers(1, 6, n),
        "INSCOVY3": rng.integers(1, 4, n),
        "HAVEUS6": rng.integers(1, 3, n),
        "POVCATY3": rng.integers(1, 6, n),
        "TTLPY3X": rng.integers(0, 80000, n),
        "EMPST6": rng.integers(1, 5, n),
    })
    X_tr, y_tr, X_ho, _ = repeated_cv.training_portion(X, y)
    # Poison the unused holdout so a leak would be visible if someone trained on it.
    X_ho.loc[:, "AGEY3X"] = -999
    fold_df = repeated_cv.run_repeated_cv(X_tr, y_tr)
    assert len(fold_df) == 25
    assert fold_df["holdout_used"].eq(False).all()
    assert fold_df["n_cv_train"].sum() > 0
    assert (fold_df["n_cv_train"] + fold_df["n_cv_val"] == len(X_tr)).all()
    assert set(fold_df["repeat"].unique()) == {0, 1, 2, 3, 4}
    assert "delta_roc_auc" in fold_df.columns
