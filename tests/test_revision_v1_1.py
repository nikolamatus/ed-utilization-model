"""Unit tests for v1.1 reporting/sensitivity helpers. Do not overwrite locked files."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from feasibility import config, revision_v1_1 as v11
from test_diagnostics import LOCKED_OUTPUTS


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_refuses_to_write_non_v11_filenames(tmp_path, monkeypatch):
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(v11.RevisionV11Error, match="v1_1"):
        v11._write_csv(df, tmp_path / "model_metrics.csv")
    with pytest.raises(v11.RevisionV11Error, match="v1_1"):
        v11._write_text("x", tmp_path / "statistical_inference.csv")
    v11._write_csv(df, tmp_path / "holdout_bootstrap_v1_1.csv")
    assert (tmp_path / "holdout_bootstrap_v1_1.csv").exists()


def test_nadeau_bengio_interval_matches_manual():
    mean, se, df = 0.029538965588917016, 0.012118607564036587, 24
    lo, hi = v11.nadeau_bengio_interval(mean, se, df=df)
    tcrit = float(__import__("scipy.stats", fromlist=["t"]).t.ppf(0.975, 24))
    assert lo == pytest.approx(mean - tcrit * se)
    assert hi == pytest.approx(mean + tcrit * se)
    assert lo < mean < hi


def test_brier_sign_convention_in_bootstrap_summary():
    rng = np.random.default_rng(0)
    y = np.array([0, 0, 0, 1, 1, 0, 1, 0] * 20)
    p_ed = np.clip(0.1 + 0.2 * y + rng.normal(0, 0.05, len(y)), 0.01, 0.99)
    p_full = np.clip(0.08 + 0.35 * y + rng.normal(0, 0.05, len(y)), 0.01, 0.99)
    _boot, summary = v11.bootstrap_holdout_metrics(y, p_ed, p_full, n_boot=50, seed=1)
    assert "lower Brier is better" in summary["sign_convention"].iloc[0]
    brier_row = summary.set_index("metric").loc["delta_brier"]
    assert brier_row["ci_lower"] <= brier_row["ci_upper"]


def test_bootstrap_skips_single_class_replicates():
    y = np.array([0, 0, 0, 0, 1])
    p = np.full(5, 0.2)
    boot, summary = v11.bootstrap_holdout_metrics(y, p, p, n_boot=200, seed=0)
    assert int(summary["n_degenerate_skipped"].iloc[0]) > 0
    assert len(boot) == int(summary["n_bootstrap_valid"].iloc[0])
    assert len(boot) + int(summary["n_degenerate_skipped"].iloc[0]) == 200


def test_vif_drop_first_finite_when_full_dummy_is_infinite():
    n = 80
    rng = np.random.default_rng(1)
    X = pd.DataFrame({
        "AGEY3X": rng.normal(40, 12, n),
        "TTLPY3X": rng.normal(20000, 5000, n),
        "ERTOTY1": rng.integers(0, 3, n),
        "ERTOTY2": rng.integers(0, 3, n),
        "ERTOTY3": rng.integers(0, 3, n),
        "SEX": rng.choice([1, 2], n),
        "RACETHX": rng.choice([1, 2, 3], n),
        "REGIONY3": rng.choice([1, 2, 3, 4], n),
        "MARRY6X": rng.choice([1, 2, 3], n),
        "RTHLTH6": rng.choice([1, 2, 3, 4, 5], n),
        "MNHLTH6": rng.choice([1, 2, 3, 4, 5], n),
        "INSCOVY3": rng.choice([1, 2, 3], n),
        "HAVEUS6": rng.choice([1, 2], n),
        "POVCATY3": rng.choice([1, 2, 3, 4, 5], n),
        "EMPST6": rng.choice([1, 2, 3, 4], n),
    })
    from feasibility import diagnostics
    vif_full = diagnostics.variance_inflation_factors(X, list(X.columns))
    vif_drop = v11.variance_inflation_factors_drop_reference(X, list(X.columns))
    assert np.isinf(vif_full.loc[vif_full["source_variable"] == "SEX", "VIF"]).all()
    sex_drop = vif_drop.loc[vif_drop["source_variable"] == "SEX", "VIF"]
    assert len(sex_drop) == 1
    assert np.isfinite(sex_drop).all()


def test_calibration_assessment_does_not_mutate_probabilities():
    y = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 0], dtype=int)
    p = np.array([0.1, 0.2, 0.8, 0.7, 0.15, 0.6, 0.3, 0.25, 0.9, 0.05])
    p_copy = p.copy()
    out = v11.calibration_intercept_slope(y, p)
    assert np.array_equal(p, p_copy)
    assert "not recalibrated" in out["method"]
    assert "calibration_in_the_large" in out
    assert np.isfinite(out["calibration_in_the_large"])
    assert np.isfinite(out["calibration_intercept"])
    assert np.isfinite(out["calibration_slope"])


def test_calibration_in_the_large_near_zero_when_rates_match():
    rng = np.random.default_rng(0)
    p = np.clip(rng.uniform(0.05, 0.4, 400), 1e-6, 1 - 1e-6)
    y = (rng.uniform(0, 1, 400) < p).astype(int)
    lp = v11.logit(p)
    citl = v11.calibration_in_the_large(y, lp)
    assert abs(citl) < 0.5


def test_no_age_block_matches_documented_b1():
    from feasibility import age_ablation
    assert v11.NO_AGE_COLUMNS == age_ablation.NO_AGE_COLUMNS
    assert "AGEY3X" not in v11.NO_AGE_COLUMNS
    assert set(v11.FULL_COLUMNS) - set(v11.NO_AGE_COLUMNS) == {"AGEY3X"}


def test_covid_columns_drop_only_2020_ed_count():
    assert "ERTOTY2" not in v11.COVID_ED_COLUMNS
    assert "ERTOTY2" not in v11.COVID_FULL_COLUMNS
    assert v11.COVID_ED_COLUMNS == ["ERTOTY1", "ERTOTY3"]
    assert set(v11.FULL_COLUMNS) - set(v11.COVID_FULL_COLUMNS) == {"ERTOTY2"}


def test_revision_constants_do_not_change_locked_seeds():
    assert v11.BOOTSTRAP_SEED != config.RANDOM_SEED
    assert v11.BOOTSTRAP_REPLICATES == 2000
    assert config.RANDOM_SEED == 42


def test_locked_outputs_untouched_by_nonwriting_helpers():
    before = {str(p): _sha256(p) for p in LOCKED_OUTPUTS if p.exists()}
    assert before
    y = np.array([0, 1, 0, 1, 0, 0, 1, 0] * 10)
    p = np.linspace(0.05, 0.9, len(y))
    v11.binary_metrics(y, p)
    v11.calibration_intercept_slope(y, p)
    v11.nadeau_bengio_interval(0.03, 0.01)
    after = {str(p): _sha256(p) for p in LOCKED_OUTPUTS if p.exists()}
    assert after == before
