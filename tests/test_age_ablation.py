"""In-memory tests for age ablation. No real HC-245 required."""
import numpy as np
import pandas as pd

from feasibility import features, repeated_cv, age_ablation


def test_no_age_set_is_full_minus_agey3x_only():
    age_ablation.assert_column_sets()
    assert age_ablation.AGE_VAR == "AGEY3X"
    assert "AGEY3X" in age_ablation.FULL_COLUMNS
    assert "AGEY3X" not in age_ablation.NO_AGE_COLUMNS
    assert set(age_ablation.no_age_columns()) == set(age_ablation.FULL_COLUMNS) - {"AGEY3X"}
    assert age_ablation.ED_COLUMNS == repeated_cv.ED_COLUMNS
    features.assert_no_leakage(age_ablation.NO_AGE_COLUMNS)


def test_age_ablation_uses_same_cv_splitter():
    a = list(repeated_cv.cv_splitter().split(np.zeros((80, 1)), np.array([0] * 40 + [1] * 40)))
    b = list(age_ablation.repeated_cv.cv_splitter().split(np.zeros((80, 1)), np.array([0] * 40 + [1] * 40)))
    assert len(a) == len(b) == 25
    for (tr1, va1), (tr2, va2) in zip(a, b):
        np.testing.assert_array_equal(tr1, tr2)
        np.testing.assert_array_equal(va1, va2)


def test_paired_deltas_on_synthetic_fold_table():
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_noage_minus_ed": [0.01] * 20 + [-0.01] * 5,
        "delta_pr_noage_minus_ed": [0.02] * 25,
        "delta_brier_noage_minus_ed": [-0.001] * 25,
        "delta_roc_noage_minus_full": [-0.02] * 25,
        "delta_pr_noage_minus_full": [-0.02] * 25,
        "delta_brier_noage_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "noage_roc_auc": [0.69] * 25,
        "noage_pr_auc": [0.32] * 25,
        "noage_brier": [0.109] * 25,
    })
    summary = age_ablation.summarize_deltas(fold_df)
    row = summary.set_index("metric")
    assert row.loc["delta_roc_noage_minus_ed", "n_folds_positive"] == 20
    assert row.loc["delta_pr_noage_minus_ed", "n_folds_positive"] == 25
    assert row.loc["delta_roc_full_minus_ed", "mean"] == 0.03


def test_write_summary_includes_requested_stats(tmp_path):
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_noage_minus_ed": [0.015] * 25,
        "delta_pr_noage_minus_ed": [0.02] * 25,
        "delta_brier_noage_minus_ed": [-0.001] * 25,
        "delta_roc_noage_minus_full": [-0.015] * 25,
        "delta_pr_noage_minus_full": [-0.02] * 25,
        "delta_brier_noage_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "noage_roc_auc": [0.695] * 25,
        "noage_pr_auc": [0.32] * 25,
        "noage_brier": [0.109] * 25,
    })
    holdout = pd.DataFrame([
        {"model": "ed_history", "roc_auc": 0.71, "pr_auc": 0.33, "brier_score": 0.105},
        {"model": "full_model", "roc_auc": 0.77, "pr_auc": 0.42, "brier_score": 0.099},
        {"model": "full_without_age", "roc_auc": 0.75, "pr_auc": 0.39, "brier_score": 0.101},
        {"model": "delta_full_minus_ed", "roc_auc": 0.06, "pr_auc": 0.09, "brier_score": -0.006},
        {"model": "delta_noage_minus_ed", "roc_auc": 0.04, "pr_auc": 0.06, "brier_score": -0.004},
        {"model": "delta_noage_minus_full", "roc_auc": -0.02, "pr_auc": -0.03, "brier_score": 0.002},
    ])
    path = tmp_path / "age_ablation_summary.md"
    age_ablation.write_summary(path, fold_df, holdout)
    text = path.read_text(encoding="utf-8")
    assert "delta_roc_noage_minus_ed" in text
    assert "p2.5" in text
    assert "locked_holdout" not in text or "Locked holdout" in text
    assert "not used for selection" in text.lower() or "not used to choose" in text.lower()
