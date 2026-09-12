"""Unit tests for Nadeau–Bengio and Holm on synthetic paired differences."""
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from feasibility import statistical_inference as si


def test_nadeau_bengio_manual_example():
    deltas = np.array([0.02, 0.04, 0.00, 0.03, -0.01] + [0.01] * 20, dtype=float)
    assert deltas.size == 25
    ratio = 0.25
    mean = float(deltas.mean())
    s2 = float(deltas.var(ddof=1))
    var_nb = (1.0 / 25.0 + ratio) * s2
    se = np.sqrt(var_nb)
    t_stat = mean / se
    p = 2.0 * stats.t.sf(abs(t_stat), 24)
    got = si.nadeau_bengio_ttest(deltas, ratio)
    assert got.n == 25
    assert got.df == 24
    assert got.mean == pytest.approx(mean)
    assert got.corrected_se == pytest.approx(se)
    assert got.t_statistic == pytest.approx(t_stat)
    assert got.p_value == pytest.approx(p)
    naive_se = np.sqrt(s2 / 25.0)
    assert got.corrected_se > naive_se


def test_holm_ordering_and_adjusted_values():
    raw = [0.04, 0.01, 0.20, 0.03, 0.50]
    adj = si.holm_adjust(raw)
    # sorted: 0.01, 0.03, 0.04, 0.20, 0.50
    # 5*0.01=0.05; max(0.05,4*0.03=0.12)=0.12; max(0.12,3*0.04=0.12)=0.12
    # max(0.12,2*0.20=0.40)=0.40; max(0.40,1*0.50=0.50)=0.50
    expected = {
        0.04: 0.12,
        0.01: 0.05,
        0.20: 0.40,
        0.03: 0.12,
        0.50: 0.50,
    }
    for p, a in zip(raw, adj):
        assert a == pytest.approx(expected[p])


def test_family_a_has_no_holm_and_family_b_does():
    tables = {}
    rng = np.random.default_rng(0)
    for cid, spec in si.CONTRASTS.items():
        n_train = np.array([3064, 3065, 3065, 3065, 3065] * 5)
        n_val = 3831 - n_train
        roc = rng.normal(0.01 if cid == "A1" else 0.0, 0.01, 25)
        pr = rng.normal(0.01 if cid == "A1" else 0.0, 0.01, 25)
        brier = rng.normal(-0.001 if cid == "A1" else 0.0, 0.001, 25)
        tables[cid] = pd.DataFrame({
            "repeat": np.repeat(range(5), 5),
            "fold": np.tile(range(5), 5),
            "fold_index": range(25),
            "n_cv_train": n_train,
            "n_cv_val": n_val,
            spec["columns"]["roc"]: roc,
            spec["columns"]["pr"]: pr,
            spec["columns"]["brier"]: brier,
        })
    # A1 also needs the canonical column names used by verify/load, but
    # analyze_contrasts only needs the mapped columns.
    tables["A1"]["delta_roc_auc"] = tables["A1"][si.CONTRASTS["A1"]["columns"]["roc"]]
    tables["A1"]["delta_pr_auc"] = tables["A1"][si.CONTRASTS["A1"]["columns"]["pr"]]
    tables["A1"]["delta_brier"] = tables["A1"][si.CONTRASTS["A1"]["columns"]["brier"]]
    result = si.analyze_contrasts(tables, 0.25)
    a = result[result["family"] == "A"]
    b = result[result["family"] == "B"]
    assert a["holm_adjusted_p_value"].isna().all()
    assert b["holm_adjusted_p_value"].notna().all()
    for metric in ("roc_auc", "pr_auc", "brier"):
        raw = b.loc[b["metric"] == metric, "raw_p_value"].tolist()
        adj = b.loc[b["metric"] == metric, "holm_adjusted_p_value"].tolist()
        assert adj == pytest.approx(si.holm_adjust(raw))


def test_brier_direction_is_not_sign_flipped():
    assert "lower Brier" in si.direction_text("A1", "brier", -0.002)
    assert "Full better" in si.direction_text("A1", "brier", -0.002)
    assert "reduced model better" in si.direction_text("B1", "brier", -0.002)
    assert "Full better" in si.direction_text("B1", "brier", 0.002)
    assert "Full better than ED-history" == si.direction_text("A1", "roc_auc", 0.03)
    assert "Full better than reduced" in si.direction_text("B4", "pr_auc", -0.01)


def test_require_fold_ids_rejects_malformed_input():
    bad = pd.DataFrame({"repeat": [0], "fold": [0], "x": [1]})
    with pytest.raises(si.InferenceInputError, match="missing fold identifiers"):
        si._require_fold_ids(bad, "bad.csv")
    incomplete = pd.DataFrame({
        "repeat": [0] * 24,
        "fold": list(range(5)) * 4 + [0, 1, 2, 3],
        "fold_index": list(range(24)),
    })
    with pytest.raises(si.InferenceInputError, match="24 rows"):
        si._require_fold_ids(incomplete, "short.csv")
    wrong = pd.DataFrame({
        "repeat": np.repeat(range(5), 5),
        "fold": np.tile(range(5), 5),
        "fold_index": list(range(24)) + [99],
    })
    with pytest.raises(si.InferenceInputError):
        si._require_fold_ids(wrong, "wrong_index.csv")


def test_holm_rejects_invalid_p_values():
    with pytest.raises(si.InferenceInputError):
        si.holm_adjust([0.1, 1.2])


def test_five_by_five_constants():
    assert si.N_REPEATS == 5
    assert si.N_SPLITS == 5
    assert si.N_ESTIMATES == 25
    assert si.DF == 24


def test_saved_fold_tables_align_without_writing():
    tables = si.load_contrast_tables()
    ratio = si.verify_alignment(tables)
    assert set(tables) == set(si.CONTRASTS)
    assert all(len(df) == 25 for df in tables.values())
    assert 0.24 < ratio < 0.26
