"""
Repeat-level robustness check for Family A only (Full − ED-history).

Uses the saved 25 fold-level deltas. Does not refit models and does not
replace the plan-specified Nadeau–Bengio test.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy import stats

from . import config

A1_PATH = "repeated_cv_metrics.csv"
DELTA_COLUMNS = {
    "roc_auc": "delta_roc_auc",
    "pr_auc": "delta_pr_auc",
    "brier": "delta_brier",
}
N_REPEATS = 5
N_SPLITS = 5
ALPHA = 0.05

# Plan-specified Nadeau–Bengio Family A results (outputs/statistical_inference.csv).
# Quoted for comparison only; not recomputed here as the primary test.
NB_PRIMARY = {
    "roc_auc": {"t": 2.437488418766643, "p": 0.02257265024089372, "df": 24, "significant": True},
    "pr_auc": {"t": 3.384577131109761, "p": 0.002448632579066552, "df": 24, "significant": True},
    "brier": {"t": -1.6545239421996543, "p": 0.11104215575277274, "df": 24, "significant": False},
}


def load_a1_folds() -> pd.DataFrame:
    path = config.OUTPUTS_DIR / A1_PATH
    df = pd.read_csv(path)
    if len(df) != N_REPEATS * N_SPLITS:
        raise ValueError(f"{A1_PATH} must have 25 rows; found {len(df)}.")
    if set(df["repeat"]) != set(range(N_REPEATS)):
        raise ValueError("repeat identifiers must be 0..4.")
    counts = df.groupby("repeat").size()
    if not (counts == N_SPLITS).all():
        raise ValueError("Each repeat must contain exactly 5 folds.")
    return df.sort_values(["repeat", "fold"]).reset_index(drop=True)


def repeat_level_means(df: pd.DataFrame) -> pd.DataFrame:
    """One mean paired delta per repeat, for each Family A metric."""
    rows = []
    for metric, col in DELTA_COLUMNS.items():
        grouped = df.groupby("repeat", sort=True)[col].mean()
        if len(grouped) != N_REPEATS:
            raise ValueError(f"{metric} did not produce 5 repeat-level means.")
        for repeat, value in grouped.items():
            rows.append({
                "contrast": "Full − ED-history",
                "metric": metric,
                "repeat": int(repeat),
                "n_folds_in_repeat": N_SPLITS,
                "repeat_mean_delta": float(value),
            })
    return pd.DataFrame(rows)


def one_sample_t_on_repeat_means(values: np.ndarray) -> dict:
    values = np.asarray(values, dtype=float)
    if values.size != N_REPEATS:
        raise ValueError("Repeat-level test requires exactly 5 means.")
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(N_REPEATS))
    t_stat = mean / se if se > 0 else float("inf")
    p_value = float(2.0 * stats.t.sf(abs(t_stat), N_REPEATS - 1))
    return {
        "n_repeats": N_REPEATS,
        "df": N_REPEATS - 1,
        "mean_of_repeat_means": mean,
        "t_statistic": float(t_stat),
        "p_value": p_value,
        "significant_at_0.05": bool(p_value <= ALPHA),
    }


def analyze_family_a(df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    folds = df if df is not None else load_a1_folds()
    means = repeat_level_means(folds)
    rows = []
    for metric, col in DELTA_COLUMNS.items():
        metric_means = means.loc[means["metric"] == metric].sort_values("repeat")
        test = one_sample_t_on_repeat_means(metric_means["repeat_mean_delta"].to_numpy())
        nb = NB_PRIMARY[metric]
        rows.append({
            "family": "A",
            "contrast": "Full − ED-history",
            "metric": metric,
            "repeat_0_mean": float(metric_means.iloc[0]["repeat_mean_delta"]),
            "repeat_1_mean": float(metric_means.iloc[1]["repeat_mean_delta"]),
            "repeat_2_mean": float(metric_means.iloc[2]["repeat_mean_delta"]),
            "repeat_3_mean": float(metric_means.iloc[3]["repeat_mean_delta"]),
            "repeat_4_mean": float(metric_means.iloc[4]["repeat_mean_delta"]),
            "repeat_level_t": test["t_statistic"],
            "repeat_level_p": test["p_value"],
            "repeat_level_df": test["df"],
            "repeat_level_significant_0.05": test["significant_at_0.05"],
            "nb_t": nb["t"],
            "nb_p": nb["p"],
            "nb_df": nb["df"],
            "nb_significant_0.05": nb["significant"],
            "source_file": A1_PATH,
            "source_column": col,
            "note": (
                "Repeat-level t-test uses 5 repeat means (df=4). The repeats "
                "share the same training sample, so this is not a more "
                "conservative variance estimate. It does not replace the "
                "plan-specified Nadeau-Bengio test."
            ),
        })
    return means, pd.DataFrame(rows)


def write_summary(path, means: pd.DataFrame, tests: pd.DataFrame) -> None:
    lines = [
        "| metric | r0 | r1 | r2 | r3 | r4 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in DELTA_COLUMNS:
        m = means[means["metric"] == metric].sort_values("repeat")
        vals = " | ".join(f"{v:+.4f}" for v in m["repeat_mean_delta"])
        lines.append(f"| {metric} | {vals} |")
    mean_table = "\n".join(lines)

    cmp_lines = [
        "| metric | NB t (df=24) | NB p | NB sig. 0.05 | repeat-level t (df=4) | repeat-level p | repeat-level sig. 0.05 |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for _, r in tests.iterrows():
        cmp_lines.append(
            f"| {r['metric']} | {r['nb_t']:+.3f} | {r['nb_p']:.4f} | "
            f"{'yes' if r['nb_significant_0.05'] else 'no'} | "
            f"{r['repeat_level_t']:+.3f} | {r['repeat_level_p']:.4f} | "
            f"{'yes' if r['repeat_level_significant_0.05'] else 'no'} |"
        )
    cmp_table = "\n".join(cmp_lines)

    roc = tests.set_index("metric").loc["roc_auc"]
    pr = tests.set_index("metric").loc["pr_auc"]
    br = tests.set_index("metric").loc["brier"]
    roc_survives = bool(roc["repeat_level_significant_0.05"])
    pr_survives = bool(pr["repeat_level_significant_0.05"])

    md = f"""# Repeat-level robustness check (Family A only)

Descriptive sensitivity diagnostic only. The plan-specified primary test
remains the Nadeau–Bengio corrected t-test (df = 24) on the 25 paired
fold deltas. This file does not replace that test and was not applied
to Family B.

## Method

The 25 Full − ED-history fold-level deltas from
`outputs/repeated_cv_metrics.csv` were grouped by repeat (5 repeats × 5
folds). The mean delta within each repeat was computed for ROC-AUC,
PR-AUC, and Brier, yielding 5 numbers per metric. A standard one-sample
two-sided t-test of those 5 repeat-level means against 0 was run
(df = 4).

The five repeats reuse the same underlying training population. Treating
the five repeat means as independent observations understates
uncertainty relative to the Nadeau–Bengio correction on the 25 paired
fold differences. Smaller repeat-level p-values are therefore **not**
stronger evidence and must not be read as a more conservative inferential
test.

No model was refit. Existing experiment outputs were not modified.

## Repeat-level means (Full − ED-history)

{mean_table}

## Comparison with the plan-specified Nadeau–Bengio test

{cmp_table}

- Repeat-level ROC: t = {roc['repeat_level_t']:+.3f}, p = {roc['repeat_level_p']:.4f}, df = 4, significant at 0.05: {"yes" if roc_survives else "no"}.
- Repeat-level PR: t = {pr['repeat_level_t']:+.3f}, p = {pr['repeat_level_p']:.4f}, df = 4, significant at 0.05: {"yes" if pr_survives else "no"}.
- Repeat-level Brier: t = {br['repeat_level_t']:+.3f}, p = {br['repeat_level_p']:.4f}, df = 4, significant at 0.05: {"yes" if br['repeat_level_significant_0.05'] else "no"}.

## Conclusion relative to Family A discrimination

The primary hypothesis is that the full model has higher discrimination
than 3-year ED history. Under Nadeau–Bengio, ROC (p = 0.0226) and PR
(p = 0.0024) were significant; Brier was not (p = 0.1110).

Under this repeat-level diagnostic, ROC is {"significant" if roc_survives else "not significant"}
and PR is {"significant" if pr_survives else "not significant"} at alpha = 0.05.
The smaller p-values reflect understated variance from treating five
overlapping repeats as independent, not a stronger test. Repeat-level
Brier significance does not overturn the primary Brier result
(Nadeau–Bengio p = 0.1110).

This changes no prior conclusion by itself. It is additional descriptive
evidence to report alongside the plan-specified Nadeau–Bengio result,
not a replacement for it.

Unweighted MEPS Panel 24 analytic-sample results only.
"""
    path.write_text(md, encoding="utf-8")


def run_check() -> dict:
    means, tests = analyze_family_a()
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    tests.to_csv(config.OUTPUTS_DIR / "robustness_repeat_level_test.csv", index=False)
    write_summary(config.OUTPUTS_DIR / "robustness_repeat_level_summary.md", means, tests)
    print("Repeat-level robustness check written (Family A only).")
    return {"means": means, "tests": tests}


def main() -> int:
    run_check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
