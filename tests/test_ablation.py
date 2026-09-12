"""In-memory tests for feature-family ablation. No real HC-245 required."""
import numpy as np
import pandas as pd
import pytest

from feasibility import ablation, config, features, modeling


def test_family_lists_are_nested_and_leakage_safe():
    ablation.assert_families_leakage_safe()
    cols = ablation.family_column_map()
    ed = set(config.PREDICTOR_ED_VARS)
    assert cols["ed_history_only"] == config.PREDICTOR_ED_VARS
    for name in ("ed_demographics", "ed_health", "ed_access", "ed_socioeconomic", "full_model"):
        assert ed.issubset(cols[name])
        assert config.OUTCOME_ED_VAR not in cols[name]
        assert not any(features.looks_post_cutoff(c) for c in cols[name])
    assert set(cols["full_model"]) == {s.name for s in config.allowed_predictor_specs()}
    union = set()
    for name in ("ed_history_only", "ed_demographics", "ed_health", "ed_access", "ed_socioeconomic"):
        union.update(cols[name])
    assert union == set(cols["full_model"])


def test_family_lists_do_not_add_new_predictors():
    production = {s.name for s in config.allowed_predictor_specs()}
    for cols in ablation.family_column_map().values():
        assert set(cols) <= production


def test_decedent_mask_flags_yearind1_deaths_only_by_died():
    df = pd.DataFrame({
        "DIED": [0, 1, 1, 0, -1],
        "YEARIND": [1, 1, 1, 1, 1],
    })
    mask = ablation.decedent_mask(df)
    assert mask.tolist() == [False, True, True, False, False]


def test_decedent_mask_requires_died():
    with pytest.raises(RuntimeError, match="DIED"):
        ablation.decedent_mask(pd.DataFrame({"YEARIND": [1, 1]}))


def test_split_matches_production_split():
    rng = np.random.default_rng(0)
    n = 80
    y = pd.Series([0] * 60 + [1] * 20)
    X = pd.DataFrame({
        "ERTOTY1": rng.integers(0, 3, n),
        "ERTOTY2": rng.integers(0, 3, n),
        "ERTOTY3": rng.integers(0, 3, n),
        "AGEY3X": rng.integers(18, 80, n),
    })
    decedent = pd.Series([False] * 70 + [True] * 10)
    X_train, X_test, y_train, y_test = modeling._split(X, y)
    A_train, A_test, b_train, b_test, d_train, d_test = ablation.split_with_death_flag(X, y, decedent)
    pd.testing.assert_index_equal(X_train.index, A_train.index)
    pd.testing.assert_series_equal(y_train, b_train)
    assert len(d_train) == len(A_train)
    assert len(d_test) == len(A_test)


def test_ablation_deltas_and_interpretation():
    results = [
        modeling.EvalResult("ed_history_only", 100, 0.13, 0.70, 0.33, 0.11, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
        modeling.EvalResult("ed_demographics", 100, 0.13, 0.73, 0.36, 0.10, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
        modeling.EvalResult("ed_health", 100, 0.13, 0.74, 0.38, 0.10, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
        modeling.EvalResult("ed_access", 100, 0.13, 0.705, 0.335, 0.11, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
        modeling.EvalResult("ed_socioeconomic", 100, 0.13, 0.71, 0.34, 0.11, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
        modeling.EvalResult("full_model", 100, 0.13, 0.77, 0.41, 0.09, 0.8, 0.1, 0.9, 0.5, 0.1, 0.5, "n", {}),
    ]
    table = ablation.ablation_table(results, 0.70, 0.33)
    assert table.set_index("model").loc["ed_health", "delta_roc_vs_ed_history"] == pytest.approx(0.04)
    assert table.set_index("model").loc["full_model", "delta_pr_vs_ed_history"] == pytest.approx(0.08)
    info = ablation.interpret_ablation(table)
    assert info["largest_family"] == "ed_health"
    assert info["distributed"] is True


def test_fit_family_rejects_outcome_column():
    with pytest.raises(features.LeakageError):
        features.assert_no_leakage(["ERTOTY1", "ERTOTY4"])
