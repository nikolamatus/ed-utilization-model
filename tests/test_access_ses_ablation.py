"""In-memory tests for B4 access and B5 SES block ablations."""
import numpy as np
import pandas as pd

from feasibility import features, repeated_cv, block_ablation
from feasibility.access_ablation import ACCESS_SPEC
from feasibility.ses_ablation import SES_SPEC


def test_access_block_is_inscovy3_haveus6_only():
    block_ablation.assert_column_sets(ACCESS_SPEC)
    assert ACCESS_SPEC.block == ("INSCOVY3", "HAVEUS6")
    reduced = block_ablation.reduced_columns(ACCESS_SPEC)
    for name in ACCESS_SPEC.block:
        assert name in block_ablation.FULL_COLUMNS
        assert name not in reduced
    for name in ACCESS_SPEC.must_retain:
        assert name in reduced
    assert "POVCATY3" in reduced and "EMPST6" in reduced
    features.assert_no_leakage(reduced)


def test_ses_block_is_povcat_ttlp_empst_only():
    block_ablation.assert_column_sets(SES_SPEC)
    assert SES_SPEC.block == ("POVCATY3", "TTLPY3X", "EMPST6")
    reduced = block_ablation.reduced_columns(SES_SPEC)
    for name in SES_SPEC.block:
        assert name in block_ablation.FULL_COLUMNS
        assert name not in reduced
    for name in SES_SPEC.must_retain:
        assert name in reduced
    assert "INSCOVY3" in reduced and "HAVEUS6" in reduced
    features.assert_no_leakage(reduced)


def test_access_and_ses_are_separate_blocks():
    assert set(ACCESS_SPEC.block).isdisjoint(SES_SPEC.block)


def test_block_ablation_uses_same_cv_splitter():
    y = np.array([0] * 40 + [1] * 40)
    x = np.zeros((80, 1))
    a = list(repeated_cv.cv_splitter().split(x, y))
    b = list(block_ablation.repeated_cv.cv_splitter().split(x, y))
    assert len(a) == len(b) == 25
    for (tr1, va1), (tr2, va2) in zip(a, b):
        np.testing.assert_array_equal(tr1, tr2)
        np.testing.assert_array_equal(va1, va2)


def _synthetic_folds(prefix: str) -> pd.DataFrame:
    return pd.DataFrame({
        "delta_roc_full_minus_ed": [0.03] * 25,
        "delta_pr_full_minus_ed": [0.04] * 25,
        "delta_brier_full_minus_ed": [-0.002] * 25,
        f"delta_roc_{prefix}_minus_ed": [0.01] * 20 + [-0.01] * 5,
        f"delta_pr_{prefix}_minus_ed": [0.02] * 23 + [-0.01] * 2,
        f"delta_brier_{prefix}_minus_ed": [-0.001] * 18 + [0.001] * 7,
        f"delta_roc_{prefix}_minus_full": [-0.01] * 25,
        f"delta_pr_{prefix}_minus_full": [-0.01] * 25,
        f"delta_brier_{prefix}_minus_full": [0.001] * 25,
        "ed_roc_auc": [0.68] * 25,
        "ed_pr_auc": [0.30] * 25,
        "ed_brier": [0.11] * 25,
        "full_roc_auc": [0.71] * 25,
        "full_pr_auc": [0.34] * 25,
        "full_brier": [0.108] * 25,
        f"{prefix}_roc_auc": [0.69] * 25,
        f"{prefix}_pr_auc": [0.32] * 25,
        f"{prefix}_brier": [0.109] * 25,
    })


def test_access_summarize_deltas():
    summary = block_ablation.summarize_deltas(_synthetic_folds("noaccess"), ACCESS_SPEC)
    row = summary.set_index("metric")
    assert row.loc["delta_roc_noaccess_minus_ed", "n_folds_positive"] == 20
    assert row.loc["delta_pr_noaccess_minus_ed", "n_folds_positive"] == 23
    assert row.loc["delta_brier_noaccess_minus_ed", "n_folds_improved_brier"] == 18


def test_ses_summarize_deltas():
    summary = block_ablation.summarize_deltas(_synthetic_folds("noses"), SES_SPEC)
    row = summary.set_index("metric")
    assert row.loc["delta_roc_noses_minus_ed", "n_folds_positive"] == 20
    assert row.loc["delta_brier_noses_minus_ed", "n_folds_improved_brier"] == 18


def test_write_summary_has_no_significance_language(tmp_path):
    holdout = pd.DataFrame([
        {"model": "ed_history", "roc_auc": 0.71, "pr_auc": 0.33, "brier_score": 0.105},
        {"model": "full_model", "roc_auc": 0.77, "pr_auc": 0.42, "brier_score": 0.099},
        {"model": "full_without_access", "roc_auc": 0.75, "pr_auc": 0.39, "brier_score": 0.101},
        {"model": "delta_full_minus_ed", "roc_auc": 0.06, "pr_auc": 0.09, "brier_score": -0.006},
        {"model": "delta_noaccess_minus_ed", "roc_auc": 0.04, "pr_auc": 0.06, "brier_score": -0.004},
        {"model": "delta_noaccess_minus_full", "roc_auc": -0.02, "pr_auc": -0.03, "brier_score": 0.002},
    ])
    path = tmp_path / "access_ablation_summary.md"
    block_ablation.write_summary(path, _synthetic_folds("noaccess"), holdout, ACCESS_SPEC)
    text = path.read_text(encoding="utf-8")
    assert "B4" in text
    assert "INSCOVY3" in text and "HAVEUS6" in text
    assert "not confidence intervals" in text
    assert "No p-value" in text
    assert "Nadeau-Bengio" in text
    assert "Holm-Bonferroni" in text
    lowered = text.lower()
    assert "p = " not in lowered
    assert "statistically significant" not in lowered
    assert block_ablation.CROSS_EXPERIMENT_NOTE in text
