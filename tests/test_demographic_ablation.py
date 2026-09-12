"""In-memory tests for demographic-block ablation. No real HC-245 required."""
import numpy as np
import pandas as pd

from feasibility import features, repeated_cv, demographic_ablation


def test_no_demo_set_is_full_minus_four_demographics_only():
    demographic_ablation.assert_column_sets()
    assert demographic_ablation.DEMO_BLOCK == ["SEX", "RACETHX", "REGIONY3", "MARRY6X"]
    assert demographic_ablation.AGE_VAR == "AGEY3X"
    assert "AGEY3X" in demographic_ablation.FULL_COLUMNS
    assert "AGEY3X" in demographic_ablation.NO_DEMO_COLUMNS
    for name in demographic_ablation.DEMO_BLOCK:
        assert name in demographic_ablation.FULL_COLUMNS
        assert name not in demographic_ablation.NO_DEMO_COLUMNS
    assert set(demographic_ablation.no_demo_columns()) == (
        set(demographic_ablation.FULL_COLUMNS) - set(demographic_ablation.DEMO_BLOCK)
    )
    assert demographic_ablation.ED_COLUMNS == repeated_cv.ED_COLUMNS
    features.assert_no_leakage(demographic_ablation.NO_DEMO_COLUMNS)


def test_demographic_ablation_uses_same_cv_splitter():
    y = np.array([0] * 40 + [1] * 40)
    x = np.zeros((80, 1))
    a = list(repeated_cv.cv_splitter().split(x, y))
    b = list(demographic_ablation.repeated_cv.cv_splitter().split(x, y))
    assert len(a) == len(b) == 25
    for (tr1, va1), (tr2, va2) in zip(a, b):
        np.testing.assert_array_equal(tr1, tr2)
        np.testing.assert_array_equal(va1, va2)


def test_paired_deltas_on_synthetic_fold_table():
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_nodemo_minus_ed": [0.01] * 18 + [-0.01] * 7,
        "delta_pr_nodemo_minus_ed": [0.02] * 22 + [-0.01] * 3,
        "delta_brier_nodemo_minus_ed": [-0.001] * 16 + [0.001] * 9,
        "delta_roc_nodemo_minus_full": [-0.02] * 25,
        "delta_pr_nodemo_minus_full": [-0.02] * 25,
        "delta_brier_nodemo_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "nodemo_roc_auc": [0.69] * 25,
        "nodemo_pr_auc": [0.32] * 25,
        "nodemo_brier": [0.109] * 25,
    })
    summary = demographic_ablation.summarize_deltas(fold_df)
    row = summary.set_index("metric")
    assert row.loc["delta_roc_nodemo_minus_ed", "n_folds_positive"] == 18
    assert row.loc["delta_pr_nodemo_minus_ed", "n_folds_positive"] == 22
    assert row.loc["delta_brier_nodemo_minus_ed", "n_folds_improved_brier"] == 16
    assert row.loc["delta_roc_full_minus_ed", "mean"] == 0.03


def test_write_summary_includes_requested_stats(tmp_path):
    fold_df = pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        "delta_roc_nodemo_minus_ed": [0.018] * 25,
        "delta_pr_nodemo_minus_ed": [0.022] * 25,
        "delta_brier_nodemo_minus_ed": [-0.001] * 25,
        "delta_roc_nodemo_minus_full": [-0.012] * 25,
        "delta_pr_nodemo_minus_full": [-0.018] * 25,
        "delta_brier_nodemo_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        "nodemo_roc_auc": [0.698] * 25,
        "nodemo_pr_auc": [0.322] * 25,
        "nodemo_brier": [0.109] * 25,
    })
    holdout = pd.DataFrame([
        {"model": "ed_history", "roc_auc": 0.71, "pr_auc": 0.33, "brier_score": 0.105},
        {"model": "full_model", "roc_auc": 0.77, "pr_auc": 0.42, "brier_score": 0.099},
        {"model": "full_without_demographics", "roc_auc": 0.74, "pr_auc": 0.37, "brier_score": 0.102},
        {"model": "delta_full_minus_ed", "roc_auc": 0.06, "pr_auc": 0.09, "brier_score": -0.006},
        {"model": "delta_nodemo_minus_ed", "roc_auc": 0.03, "pr_auc": 0.04, "brier_score": -0.003},
        {"model": "delta_nodemo_minus_full", "roc_auc": -0.03, "pr_auc": -0.05, "brier_score": 0.003},
    ])
    path = tmp_path / "demographic_ablation_summary.md"
    demographic_ablation.write_summary(path, fold_df, holdout)
    text = path.read_text(encoding="utf-8")
    assert "AGEY3X is retained" in text
    assert "delta_roc_nodemo_minus_ed" in text
    assert "p2.5" in text
    assert "SEX" in text and "MARRY6X" in text
    assert "not used to choose" in text.lower() or "not used for selection" in text.lower()
