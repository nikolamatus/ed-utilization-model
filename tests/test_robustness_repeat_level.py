"""Tests for the Family A repeat-level robustness check."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from feasibility import config, robustness_repeat_level as rl
from test_diagnostics import LOCKED_OUTPUTS


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _locked_hashes() -> dict[str, str]:
    return {str(p): _sha256(p) for p in LOCKED_OUTPUTS if p.exists()}


def test_repeat_level_means_return_five_per_metric():
    folds = pd.DataFrame({
        "repeat": np.repeat(range(5), 5),
        "fold": np.tile(range(5), 5),
        "delta_roc_auc": np.arange(25, dtype=float),
        "delta_pr_auc": np.arange(25, dtype=float) / 10.0,
        "delta_brier": -np.arange(25, dtype=float) / 100.0,
    })
    means = rl.repeat_level_means(folds)
    assert set(means["metric"]) == {"roc_auc", "pr_auc", "brier"}
    for metric in ("roc_auc", "pr_auc", "brier"):
        subset = means[means["metric"] == metric]
        assert len(subset) == 5
        assert list(subset["repeat"]) == [0, 1, 2, 3, 4]
    roc0 = means[(means["metric"] == "roc_auc") & (means["repeat"] == 0)]["repeat_mean_delta"].iloc[0]
    assert roc0 == pytest.approx(2.0)


def test_one_sample_t_on_known_values():
    values = np.array([0.02, 0.03, 0.025, 0.015, 0.022])
    got = rl.one_sample_t_on_repeat_means(values)
    assert got["df"] == 4
    assert got["n_repeats"] == 5
    assert got["mean_of_repeat_means"] == pytest.approx(float(values.mean()))
    from scipy import stats
    t, p = stats.ttest_1samp(values, 0.0)
    assert got["t_statistic"] == pytest.approx(float(t))
    assert got["p_value"] == pytest.approx(float(p))


def test_analyze_family_a_on_saved_folds_without_writing():
    means, tests = rl.analyze_family_a()
    assert len(means) == 15
    assert len(tests) == 3
    assert set(tests["metric"]) == {"roc_auc", "pr_auc", "brier"}
    for _, row in tests.iterrows():
        assert row["repeat_level_df"] == 4
        assert row["nb_df"] == 24


def test_function_does_not_modify_locked_outputs():
    before = _locked_hashes()
    assert before
    rl.analyze_family_a()
    after = _locked_hashes()
    assert after == before
