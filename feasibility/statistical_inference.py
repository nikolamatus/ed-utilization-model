"""
Pre-registered inferential pass: Nadeau–Bengio corrected t-tests and
Holm–Bonferroni within Family B.

Reads only already-saved 5x5 fold-level CSVs. Does not refit models.
Does not write prior experiment filenames.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from . import config

N_REPEATS = 5
N_SPLITS = 5
N_ESTIMATES = N_REPEATS * N_SPLITS
ALPHA = 0.05
DF = N_ESTIMATES - 1

# Nadeau & Bengio (2003) corrected resampled t-test:
#   Var_NB(mean) = (1/n + n_test/n_train) * s^2
#   t = mean / sqrt(Var_NB), df = n - 1
# n = number of train/test estimates (here 25), not independent observations.
# n_test/n_train is the fold-level test-to-train ratio (5-fold => ~1/4).
NADEAU_BENGIO_FORMULA = (
    "Nadeau & Bengio (2003) corrected resampled t-test: "
    "Var_NB = (1/n + n_test/n_train) * s^2, where s^2 is the unbiased "
    "sample variance of the n paired fold-level differences, n = r*k = 25, "
    "k = 5 folds, r = 5 repeats, and n_test/n_train is the mean validation/"
    "training size ratio within each split. t = mean / sqrt(Var_NB) with "
    "df = n-1 = 24. Two-sided p-value from Student's t. This is not the "
    "naive SE = s/sqrt(25) that would treat folds as independent."
)

CONTRASTS = {
    "A1": {
        "family": "A",
        "contrast": "Full − ED-history",
        "path": "repeated_cv_metrics.csv",
        "columns": {
            "roc": "delta_roc_auc",
            "pr": "delta_pr_auc",
            "brier": "delta_brier",
        },
    },
    "B1": {
        "family": "B",
        "contrast": "No-age − Full",
        "path": "age_ablation_cv.csv",
        "columns": {
            "roc": "delta_roc_noage_minus_full",
            "pr": "delta_pr_noage_minus_full",
            "brier": "delta_brier_noage_minus_full",
        },
    },
    "B2": {
        "family": "B",
        "contrast": "No-demographics − Full",
        "path": "demographic_ablation_cv.csv",
        "columns": {
            "roc": "delta_roc_nodemo_minus_full",
            "pr": "delta_pr_nodemo_minus_full",
            "brier": "delta_brier_nodemo_minus_full",
        },
    },
    "B3": {
        "family": "B",
        "contrast": "No-health − Full",
        "path": "health_ablation_cv.csv",
        "columns": {
            "roc": "delta_roc_nohealth_minus_full",
            "pr": "delta_pr_nohealth_minus_full",
            "brier": "delta_brier_nohealth_minus_full",
        },
    },
    "B4": {
        "family": "B",
        "contrast": "No-access − Full",
        "path": "access_ablation_cv.csv",
        "columns": {
            "roc": "delta_roc_noaccess_minus_full",
            "pr": "delta_pr_noaccess_minus_full",
            "brier": "delta_brier_noaccess_minus_full",
        },
    },
    "B5": {
        "family": "B",
        "contrast": "No-SES − Full",
        "path": "ses_ablation_cv.csv",
        "columns": {
            "roc": "delta_roc_noses_minus_full",
            "pr": "delta_pr_noses_minus_full",
            "brier": "delta_brier_noses_minus_full",
        },
    },
}

A1_CROSSCHECK_FILES = [
    ("age_ablation_cv.csv", "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed"),
    ("demographic_ablation_cv.csv", "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed"),
    ("health_ablation_cv.csv", "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed"),
    ("access_ablation_cv.csv", "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed"),
    ("ses_ablation_cv.csv", "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed"),
]


class InferenceInputError(ValueError):
    """Raised when saved fold tables are missing, incomplete, or misaligned."""


@dataclass(frozen=True)
class NBResult:
    n: int
    mean: float
    sample_variance: float
    test_train_ratio: float
    corrected_variance: float
    corrected_se: float
    t_statistic: float
    df: int
    p_value: float


def nadeau_bengio_ttest(deltas: np.ndarray, test_train_ratio: float) -> NBResult:
    """Corrected resampled t-test (Nadeau & Bengio 2003) on paired differences."""
    d = np.asarray(deltas, dtype=float)
    if d.size < 2:
        raise InferenceInputError("Need at least two paired differences.")
    if test_train_ratio <= 0:
        raise InferenceInputError("test/train ratio must be positive.")
    n = int(d.size)
    mean = float(d.mean())
    s2 = float(d.var(ddof=1))
    var_nb = (1.0 / n + test_train_ratio) * s2
    se = float(np.sqrt(var_nb))
    t_stat = mean / se if se > 0 else float("inf")
    df = n - 1
    p = float(2.0 * stats.t.sf(abs(t_stat), df))
    return NBResult(
        n=n,
        mean=mean,
        sample_variance=s2,
        test_train_ratio=float(test_train_ratio),
        corrected_variance=float(var_nb),
        corrected_se=se,
        t_statistic=float(t_stat),
        df=df,
        p_value=p,
    )


def holm_adjust(p_values: list[float], alpha: float = ALPHA) -> list[float]:
    """
    Holm–Bonferroni adjusted p-values.

    Sort p(1) <= ... <= p(m). Then
    p_holm(i) = max_{j<=i} min(1, (m-j+1) * p(j)),
    returned in the original order.
    """
    p = np.asarray(p_values, dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise InferenceInputError("Holm adjustment requires finite p-values in [0, 1].")
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = min(1.0, (m - rank) * float(p[idx]))
        running = max(running, candidate)
        adj[idx] = running
    return adj.tolist()


def _require_fold_ids(df: pd.DataFrame, source: str) -> pd.DataFrame:
    needed = {"repeat", "fold", "fold_index"}
    missing = needed - set(df.columns)
    if missing:
        raise InferenceInputError(f"{source} is missing fold identifiers: {sorted(missing)}")
    out = df.copy()
    out["repeat"] = out["repeat"].astype(int)
    out["fold"] = out["fold"].astype(int)
    out["fold_index"] = out["fold_index"].astype(int)
    if len(out) != N_ESTIMATES:
        raise InferenceInputError(f"{source} has {len(out)} rows; expected {N_ESTIMATES}.")
    expected_index = list(range(N_ESTIMATES))
    if sorted(out["fold_index"].tolist()) != expected_index:
        raise InferenceInputError(f"{source} fold_index is not 0..24.")
    if set(out["repeat"]) != set(range(N_REPEATS)):
        raise InferenceInputError(f"{source} repeat identifiers are not 0..4.")
    if set(out["fold"]) != set(range(N_SPLITS)):
        raise InferenceInputError(f"{source} fold identifiers are not 0..4.")
    reconstructed = out["repeat"] * N_SPLITS + out["fold"]
    if not (reconstructed == out["fold_index"]).all():
        raise InferenceInputError(f"{source} fold_index is inconsistent with repeat*5+fold.")
    return out.sort_values(["repeat", "fold"]).reset_index(drop=True)


def _mean_test_train_ratio(df: pd.DataFrame, source: str) -> float:
    if "n_cv_train" not in df.columns or "n_cv_val" not in df.columns:
        raise InferenceInputError(f"{source} missing n_cv_train / n_cv_val.")
    ratios = df["n_cv_val"].astype(float) / df["n_cv_train"].astype(float)
    if not np.isfinite(ratios).all() or (ratios <= 0).any():
        raise InferenceInputError(f"{source} has invalid train/val sizes.")
    return float(ratios.mean())


def load_contrast_tables() -> dict[str, pd.DataFrame]:
    tables = {}
    for cid, spec in CONTRASTS.items():
        path = config.OUTPUTS_DIR / spec["path"]
        if not path.exists():
            raise InferenceInputError(f"Missing fold-level file for {cid}: {path}")
        tables[cid] = _require_fold_ids(pd.read_csv(path), spec["path"])
    return tables


def verify_alignment(tables: dict[str, pd.DataFrame]) -> float:
    """Confirm identical 5x5 IDs and that A1 matches every block file's Full−ED."""
    keys = None
    for cid, df in tables.items():
        current = list(zip(df["repeat"].tolist(), df["fold"].tolist(), df["fold_index"].tolist()))
        if keys is None:
            keys = current
        elif current != keys:
            raise InferenceInputError(f"{cid} fold identifiers do not match A1/repeated-CV.")
    a1 = tables["A1"]
    for filename, roc_col, pr_col, brier_col in A1_CROSSCHECK_FILES:
        other = _require_fold_ids(pd.read_csv(config.OUTPUTS_DIR / filename), filename)
        if not np.allclose(a1["delta_roc_auc"], other[roc_col], atol=1e-12, rtol=0):
            raise InferenceInputError(f"A1 ROC deltas do not match {filename}.")
        if not np.allclose(a1["delta_pr_auc"], other[pr_col], atol=1e-12, rtol=0):
            raise InferenceInputError(f"A1 PR deltas do not match {filename}.")
        if not np.allclose(a1["delta_brier"], other[brier_col], atol=1e-12, rtol=0):
            raise InferenceInputError(f"A1 Brier deltas do not match {filename}.")
    return _mean_test_train_ratio(a1, "repeated_cv_metrics.csv")


def direction_text(contrast_id: str, metric: str, mean: float) -> str:
    if metric in {"roc_auc", "pr_auc"}:
        first_better = mean > 0
        if contrast_id == "A1":
            return (
                "Full better than ED-history"
                if first_better else
                "ED-history better than Full" if mean < 0 else "no mean difference"
            )
        return (
            "reduced model better than Full"
            if first_better else
            "Full better than reduced model" if mean < 0 else "no mean difference"
        )
    # Brier: lower is better, so negative mean means first model is better.
    first_better = mean < 0
    if contrast_id == "A1":
        return (
            "Full better (lower Brier) than ED-history"
            if first_better else
            "ED-history better (lower Brier) than Full" if mean > 0 else "no mean difference"
        )
    return (
        "reduced model better (lower Brier) than Full"
        if first_better else
        "Full better (lower Brier) than reduced model" if mean > 0 else "no mean difference"
    )


def analyze_contrasts(tables: dict[str, pd.DataFrame], test_train_ratio: float) -> pd.DataFrame:
    metric_cols = {"roc_auc": "roc", "pr_auc": "pr", "brier": "brier"}
    rows = []
    for cid, spec in CONTRASTS.items():
        df = tables[cid]
        for metric, key in metric_cols.items():
            col = spec["columns"][key]
            if col not in df.columns:
                raise InferenceInputError(f"{cid} missing column {col}")
            nb = nadeau_bengio_ttest(df[col].to_numpy(dtype=float), test_train_ratio)
            rows.append({
                "family": spec["family"],
                "contrast_id": cid,
                "contrast": spec["contrast"],
                "metric": metric,
                "n_estimates": nb.n,
                "n_repeats": N_REPEATS,
                "n_splits": N_SPLITS,
                "df": nb.df,
                "test_train_ratio": nb.test_train_ratio,
                "mean_difference": nb.mean,
                "sample_variance": nb.sample_variance,
                "corrected_variance": nb.corrected_variance,
                "corrected_se": nb.corrected_se,
                "t_statistic": nb.t_statistic,
                "raw_p_value": nb.p_value,
                "holm_adjusted_p_value": np.nan,
                "significant_at_0.05": False,
                "direction": direction_text(cid, metric, nb.mean),
                "source_file": spec["path"],
                "source_column": col,
            })
    result = pd.DataFrame(rows)
    for metric in metric_cols:
        mask = (result["family"] == "B") & (result["metric"] == metric)
        idx = result.index[mask]
        adj = holm_adjust(result.loc[idx, "raw_p_value"].tolist(), ALPHA)
        result.loc[idx, "holm_adjusted_p_value"] = adj
        result.loc[idx, "significant_at_0.05"] = [p <= ALPHA for p in adj]
    family_a = result["family"] == "A"
    result.loc[family_a, "holm_adjusted_p_value"] = np.nan
    result.loc[family_a, "significant_at_0.05"] = result.loc[family_a, "raw_p_value"] <= ALPHA
    return result


def write_figure(table: pd.DataFrame, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    order = ["A1", "B1", "B2", "B3", "B4", "B5"]
    labels = [CONTRASTS[c]["contrast"] for c in order]
    for ax, metric, title in (
        (axes[0], "roc_auc", "ROC-AUC difference"),
        (axes[1], "pr_auc", "PR-AUC difference"),
    ):
        sub = table[table["metric"] == metric].set_index("contrast_id").loc[order]
        y = np.arange(len(order))
        ax.errorbar(
            sub["mean_difference"],
            y,
            xerr=sub["corrected_se"],
            fmt="o",
            color="black",
            capsize=3,
        )
        ax.axvline(0, color="gray", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(title)
        ax.set_xlabel("Mean paired difference ± NB SE")
        ax.invert_yaxis()
    fig.suptitle(
        "Nadeau–Bengio corrected SE (5×5 repeated CV). "
        "Error bars are not confidence intervals from independent folds."
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _fmt_p(value) -> str:
    if pd.isna(value):
        return "—"
    v = float(value)
    if v < 0.0001:
        return "<0.0001"
    return f"{v:.4f}"


def write_summary(path, table: pd.DataFrame, test_train_ratio: float) -> None:
    def row(cid, metric):
        return table.set_index(["contrast_id", "metric"]).loc[(cid, metric)]

    a_roc = row("A1", "roc_auc")
    a_pr = row("A1", "pr_auc")
    a_br = row("A1", "brier")

    lines = [
        "| family | contrast | metric | mean | corrected SE | t | raw p | Holm p | sig. 0.05 | direction |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, r in table.iterrows():
        holm = _fmt_p(r["holm_adjusted_p_value"])
        sig = "yes" if bool(r["significant_at_0.05"]) else "no"
        lines.append(
            f"| {r['family']} | {r['contrast_id']} {r['contrast']} | {r['metric']} | "
            f"{r['mean_difference']:+.4f} | {r['corrected_se']:.4f} | "
            f"{r['t_statistic']:+.3f} | {_fmt_p(r['raw_p_value'])} | {holm} | "
            f"{sig} | {r['direction']} |"
        )
    results_table = "\n".join(lines)

    family_b_sig = []
    for metric in ("roc_auc", "pr_auc", "brier"):
        hits = table[(table["family"] == "B") & (table["metric"] == metric) & (table["significant_at_0.05"])]
        if hits.empty:
            family_b_sig.append(f"- {metric}: no Family-B contrast is significant after Holm.")
        else:
            names = ", ".join(hits["contrast_id"] + " " + hits["contrast"])
            family_b_sig.append(f"- {metric}: Holm-significant: {names}.")

    md = f"""# Pre-registered statistical inference (Nadeau–Bengio + Holm)

Date of analysis: 2026-09-12 (after B4 and B5 exist).
Source plan: `docs/pre_registration_block_ablation_plan.md` (locked 2026-09-12).
No models were refit. All numbers come from saved 5×5 fold-level CSVs.

## Method

{NADEAU_BENGIO_FORMULA}

In this experiment:

- k = 5 stratified folds per repeat
- r = 5 repeats
- n = 25 paired fold-level differences (not 25 independent observations)
- df = 24
- mean n_test/n_train = {test_train_ratio:.6f} (theoretical 5-fold ratio = 1/4 = 0.25)
- s^2 = unbiased variance of the 25 paired deltas
- alpha = 0.05, two-sided

Family A (A1 only) uses the Nadeau–Bengio p-value with no multiplicity
adjustment. Family B applies Holm–Bonferroni separately within each metric
across the five block contrasts. Holm is not applied to Family A and is
not applied across families or across metrics.

Holm procedure: order the five raw p-values p(1) ≤ … ≤ p(5); the j-th
ordered test uses threshold alpha/(5-j+1); adjusted p(i) =
max_{{j≤i}} min(1, (5-j+1) p(j)).

Sign convention (not reversed):

- Contrasts are first − second as named (A1: Full − ED-history; B1–B5: reduced − Full).
- ROC/PR: positive mean = first named model has higher discrimination.
- Brier: negative mean = first named model has lower (better) Brier.

The 2.5th–97.5th percentile ranges in earlier CV summaries remain
descriptive empirical ranges. They are not confidence intervals and are
not relabeled as such here.

Locked holdout numbers below are confirmation only. They were not used
to choose hypotheses, compute p-values, or select a model.

## Results

{results_table}

## Family A (primary)

A1 Full − ED-history, Nadeau–Bengio, no Holm:

- ROC-AUC: mean {a_roc['mean_difference']:+.4f}, SE {a_roc['corrected_se']:.4f}, t {a_roc['t_statistic']:+.3f}, p {_fmt_p(a_roc['raw_p_value'])}, significant at 0.05: {"yes" if a_roc['significant_at_0.05'] else "no"}. {a_roc['direction']}.
- PR-AUC: mean {a_pr['mean_difference']:+.4f}, SE {a_pr['corrected_se']:.4f}, t {a_pr['t_statistic']:+.3f}, p {_fmt_p(a_pr['raw_p_value'])}, significant at 0.05: {"yes" if a_pr['significant_at_0.05'] else "no"}. {a_pr['direction']}.
- Brier: mean {a_br['mean_difference']:+.4f}, SE {a_br['corrected_se']:.4f}, t {a_br['t_statistic']:+.3f}, p {_fmt_p(a_br['raw_p_value'])}, significant at 0.05: {"yes" if a_br['significant_at_0.05'] else "no"}. {a_br['direction']}.

Statistical significance is not clinical significance.

## Family B (secondary, Holm within metric)

{chr(10).join(family_b_sig)}

Removing a block did not produce statistically detectable evidence of a
performance change under this analysis unless the Holm-adjusted p-value
is ≤ 0.05. Non-significance is not evidence of equivalence and does not
mean the block is useless.

## Interpretation

Primary question — incremental value beyond 3-year ED history:
Family A asks whether the full model differs from ED-history on the
training-only 5×5 repeated CV. A statistically significant positive
ROC/PR (and/or negative Brier) difference supports incremental
predictive value on this MEPS Panel 24 analytic sample. That is not
clinical utility, causality, or national performance.

Secondary question — does removing any pre-specified block materially
change performance relative to the full model:
Family B tests reduced − Full. A Holm-significant negative ROC/PR
difference would mean the reduced model was detectably worse than Full.
A Holm-significant positive ROC/PR difference would mean the reduced
model was detectably better. Absence of Holm-significant differences
means this analysis did not detect a change; it does not prove the
removed block has no information and does not prove independence from
other predictors.

The earlier correlation/VIF diagnostic did not show strong cross-block
raw association sufficient to explain the flat ablation pattern, but it
does not establish independence of predictor information. Block ablation
does not isolate independent causal contribution and does not fully
resolve redundancy.

Descriptive repeated-CV means, these inferential tests, and the locked
holdout are three different objects. The holdout increment (Full vs
ED-history about +0.065 ROC / +0.085 PR) remains a confirmation result
and was larger than the CV mean increment. It was not used here for
inference.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical
utility, clinical validation, causality, national performance,
deployment readiness, or generalizability beyond this panel.
"""
    path.write_text(md, encoding="utf-8")


def run_inference() -> pd.DataFrame:
    tables = load_contrast_tables()
    ratio = verify_alignment(tables)
    table = analyze_contrasts(tables, ratio)
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(config.OUTPUTS_DIR / "statistical_inference.csv", index=False)
    write_figure(table, config.FIGURES_DIR / "statistical_inference.png")
    write_summary(config.OUTPUTS_DIR / "statistical_inference_summary.md", table, ratio)
    print(f"Nadeau-Bengio n_test/n_train ratio: {ratio:.6f}")
    print(f"Inference rows written: {len(table)}")
    return table


def main() -> int:
    run_inference()
    return 0


if __name__ == "__main__":
    sys.exit(main())
