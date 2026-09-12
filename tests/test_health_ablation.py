"""In-memory tests for health-status block ablation. No real HC-245 required."""
import numpy as np
import pandas as pd

from feasibility import features, repeated_cv, health_ablation


def test_no_health_set_is_full_minus_rthlth6_mnhlth6_only():
    health_ablation.assert_column_sets()
    assert health_ablation.HEALTH_BLOCK == ["RTHLTH6", "MNHLTH6"]
    for name in health_ablation.HEALTH_BLOCK:
        assert name in health_ablation.FULL_COLUMNS
        assert name not in health_ablation.NO_HEALTH_COLUMNS
    for name in health_ablation.RETAINED_DEMOGRAPHICS + health_ablation.ED_COLUMNS:
        assert name in health_ablation.NO_HEALTH_COLUMNS
    assert set(health_ablation.no_health_columns()) == (
        set(health_ablation.FULL_COLUMNS) - set(health_ablation.HEALTH_BLOCK)
    )
    assert health_ablation.ED_COLUMNS == repeated_cv.ED_COLUMNS
    features.assert_no_leakage(health_ablation.NO_HEALTH_COLUMNS)


def test_health_ablation_uses_same_cv_splitter():
    y = np.array([0] * 40 + [1] * 40)
    x = np.zeros((80, 1))
    a = list(repeated_cv.cv_splitter().split(x, y))
    b = list(health_ablation.repeated_cv.cv_splitter().split(x, y))
    assert len(a) == len(b) == 25
    for (tr1, va1), (tr2, va2) in zip(a, b):
        np.testing.assert_array_equal(tr1, tr2)
        np.testing.assert_array_equal(va1, va2)


def test_health_missingness_audit_on_synthetic_analytic_cohort():
    analytic = pd.DataFrame({
        "RTHLTH6": [1, 2, 3, -1, -9, 4, 5, 1, 2, 3],
        "MNHLTH6": [1, 2, -7, 3, 4, 5, np.nan, 1, 2, 3],
    })
    audit = health_ablation.health_missingness_audit(analytic)
    row = audit.set_index("variable")
    assert int(row.loc["RTHLTH6", "analytic_n"]) == 10
    assert int(row.loc["RTHLTH6", "valid_count"]) == 8
    assert int(row.loc["RTHLTH6", "sentinel_count"]) == 2
    assert float(row.loc["RTHLTH6", "missing_pct_after_sentinel_recode"]) == 20.0
    assert int(row.loc["MNHLTH6", "valid_count"]) == 8
    assert int(row.loc["MNHLTH6", "sentinel_count"]) == 1


def test_paired_deltas_on_synthetic_fold_table():
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_nohealth_minus_ed": [0.01] * 19 + [-0.01] * 6,
        "delta_pr_nohealth_minus_ed": [0.02] * 21 + [-0.01] * 4,
        "delta_brier_nohealth_minus_ed": [-0.001] * 17 + [0.001] * 8,
        "delta_roc_nohealth_minus_full": [-0.02] * 25,
        "delta_pr_nohealth_minus_full": [-0.02] * 25,
        "delta_brier_nohealth_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "nohealth_roc_auc": [0.69] * 25,
        "nohealth_pr_auc": [0.32] * 25,
        "nohealth_brier": [0.109] * 25,
    })
    summary = health_ablation.summarize_deltas(fold_df)
    row = summary.set_index("metric")
    assert row.loc["delta_roc_nohealth_minus_ed", "n_folds_positive"] == 19
    assert row.loc["delta_pr_nohealth_minus_ed", "n_folds_positive"] == 21
    assert row.loc["delta_brier_nohealth_minus_ed", "n_folds_improved_brier"] == 17
    assert row.loc["delta_roc_full_minus_ed", "mean"] == 0.03


def test_write_summary_includes_cross_experiment_distinction(tmp_path):
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_nohealth_minus_ed": [0.018] * 25,
        "delta_pr_nohealth_minus_ed": [0.022] * 25,
        "delta_brier_nohealth_minus_ed": [-0.001] * 25,
        "delta_roc_nohealth_minus_full": [-0.012] * 25,
        "delta_pr_nohealth_minus_full": [-0.018] * 25,
        "delta_brier_nohealth_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "nohealth_roc_auc": [0.698] * 25,
        "nohealth_pr_auc": [0.322] * 25,
        "nohealth_brier": [0.109] * 25,
    })
    holdout = pd.DataFrame([
        {"model": "ed_history", "roc_auc": 0.71, "pr_auc": 0.33, "brier_score": 0.105},
        {"model": "full_model", "roc_auc": 0.77, "pr_auc": 0.42, "brier_score": 0.099},
        {"model": "full_without_health", "roc_auc": 0.74, "pr_auc": 0.37, "brier_score": 0.102},
        {"model": "delta_full_minus_ed", "roc_auc": 0.06, "pr_auc": 0.09, "brier_score": -0.006},
        {"model": "delta_nohealth_minus_ed", "roc_auc": 0.03, "pr_auc": 0.04, "brier_score": -0.003},
        {"model": "delta_nohealth_minus_full", "roc_auc": -0.03, "pr_auc": -0.05, "brier_score": 0.003},
    ])
    missingness = pd.DataFrame([
        {
            "variable": "RTHLTH6",
            "analytic_n": 5108,
            "valid_count": 5000,
            "sentinel_count": 108,
            "missing_pct_after_sentinel_recode": 2.11,
        },
        {
            "variable": "MNHLTH6",
            "analytic_n": 5108,
            "valid_count": 4990,
            "sentinel_count": 118,
            "missing_pct_after_sentinel_recode": 2.31,
        },
    ])
    path = tmp_path / "health_ablation_summary.md"
    health_ablation.write_summary(path, fold_df, holdout, missingness)
    text = path.read_text(encoding="utf-8")
    assert health_ablation.CROSS_EXPERIMENT_NOTE in text
    assert "not confidence intervals" in text
    assert "not treated as 25 independent observations" in text
    assert "RTHLTH6" in text and "MNHLTH6" in text
    assert "AGEY3X" in text
    assert "confidence interval" not in text.lower() or "not confidence intervals" in text
    assert "not used to choose" in text.lower() or "not used for selection" in text.lower()
