"""
Demographic-block ablation: full model vs full without SEX, RACETHX,
REGIONY3, and MARRY6X. AGEY3X is retained. Same training-only 5x5 CV
folds as repeated_cv, plus a locked holdout check.

Does not write first-run, family-ablation, repeated-CV, or age-ablation
filenames.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from . import config, download, features, ingest, longitudinal, repeated_cv

AGE_VAR = "AGEY3X"
DEMO_BLOCK = ["SEX", "RACETHX", "REGIONY3", "MARRY6X"]
ED_COLUMNS = list(repeated_cv.ED_COLUMNS)
FULL_COLUMNS = list(repeated_cv.FULL_COLUMNS)
NO_DEMO_COLUMNS = [c for c in FULL_COLUMNS if c not in DEMO_BLOCK]

# Established age-ablation CV means (outputs/age_ablation_summary.md).
# Cited only for comparison; not recomputed and not used for selection.
AGE_ABLATION_CV = {
    "full_minus_ed_roc": 0.0295,
    "full_minus_ed_pr": 0.0359,
    "noage_minus_ed_roc": 0.0244,
    "noage_minus_ed_pr": 0.0342,
}


def no_demo_columns() -> list[str]:
    return list(NO_DEMO_COLUMNS)


def assert_column_sets() -> None:
    missing_block = [c for c in DEMO_BLOCK if c not in FULL_COLUMNS]
    if missing_block:
        raise RuntimeError(f"Demographic block missing from full set: {missing_block}")
    if AGE_VAR not in FULL_COLUMNS:
        raise RuntimeError(f"{AGE_VAR} must be in the production full set.")
    if AGE_VAR not in NO_DEMO_COLUMNS:
        raise RuntimeError(f"{AGE_VAR} must remain in the no-demographics set.")
    leftover = set(DEMO_BLOCK) & set(NO_DEMO_COLUMNS)
    if leftover:
        raise RuntimeError(f"Demographic block must be fully removed: {leftover}")
    if set(NO_DEMO_COLUMNS) != set(FULL_COLUMNS) - set(DEMO_BLOCK):
        raise RuntimeError(
            "No-demographics set must equal the full set minus SEX, RACETHX, "
            "REGIONY3, and MARRY6X only."
        )
    features.assert_no_leakage(ED_COLUMNS)
    features.assert_no_leakage(FULL_COLUMNS)
    features.assert_no_leakage(NO_DEMO_COLUMNS)


def run_paired_cv(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """Same folds as repeated_cv (seed 2021, 5x5) with a third no-demo model."""
    X_train = X_train.reset_index(drop=True)
    y_train = pd.Series(np.asarray(y_train), name="y")
    rows = []
    splitter = repeated_cv.cv_splitter()
    for i, (tr_idx, va_idx) in enumerate(splitter.split(X_train, y_train)):
        repeat = i // repeated_cv.CV_N_SPLITS
        fold = i % repeated_cv.CV_N_SPLITS
        X_tr, X_va = X_train.iloc[tr_idx], X_train.iloc[va_idx]
        y_tr, y_va = y_train.iloc[tr_idx], y_train.iloc[va_idx]
        ed = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, ED_COLUMNS, "ed_history")
        full = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, FULL_COLUMNS, "full_model")
        nodemo = repeated_cv.fit_on_fold(
            X_tr, y_tr, X_va, y_va, NO_DEMO_COLUMNS, "full_without_demographics"
        )
        rows.append({
            "repeat": repeat,
            "fold": fold,
            "fold_index": i,
            "n_cv_train": int(len(y_tr)),
            "n_cv_val": int(len(y_va)),
            "ed_roc_auc": ed.roc_auc,
            "ed_pr_auc": ed.pr_auc,
            "ed_brier": ed.brier_score,
            "full_roc_auc": full.roc_auc,
            "full_pr_auc": full.pr_auc,
            "full_brier": full.brier_score,
            "nodemo_roc_auc": nodemo.roc_auc,
            "nodemo_pr_auc": nodemo.pr_auc,
            "nodemo_brier": nodemo.brier_score,
            "delta_roc_full_minus_ed": full.roc_auc - ed.roc_auc,
            "delta_pr_full_minus_ed": full.pr_auc - ed.pr_auc,
            "delta_brier_full_minus_ed": full.brier_score - ed.brier_score,
            "delta_roc_nodemo_minus_ed": nodemo.roc_auc - ed.roc_auc,
            "delta_pr_nodemo_minus_ed": nodemo.pr_auc - ed.pr_auc,
            "delta_brier_nodemo_minus_ed": nodemo.brier_score - ed.brier_score,
            "delta_roc_nodemo_minus_full": nodemo.roc_auc - full.roc_auc,
            "delta_pr_nodemo_minus_full": nodemo.pr_auc - full.pr_auc,
            "delta_brier_nodemo_minus_full": nodemo.brier_score - full.brier_score,
            "holdout_seed": repeated_cv.HOLDOUT_SEED,
            "cv_random_state": repeated_cv.CV_RANDOM_STATE,
            "holdout_used": False,
        })
    return pd.DataFrame(rows)


def summarize_deltas(fold_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        "nodemo_roc_auc", "nodemo_pr_auc", "nodemo_brier",
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        "delta_roc_nodemo_minus_ed", "delta_pr_nodemo_minus_ed", "delta_brier_nodemo_minus_ed",
        "delta_roc_nodemo_minus_full", "delta_pr_nodemo_minus_full", "delta_brier_nodemo_minus_full",
    ]
    rows = []
    for col in cols:
        stats = repeated_cv.describe_numeric(fold_df[col])
        stats["metric"] = col
        if col.startswith("delta_roc") or col.startswith("delta_pr"):
            stats["n_folds_positive"] = int((fold_df[col] > 0).sum())
        elif col.startswith("delta_brier"):
            stats["n_folds_improved_brier"] = int((fold_df[col] < 0).sum())
        rows.append(stats)
    return pd.DataFrame(rows)


def evaluate_locked_holdout(X_train, y_train, X_holdout, y_holdout) -> pd.DataFrame:
    """Fit on the original training portion only; score the locked 25% holdout."""
    rows = []
    for name, cols in (
        ("ed_history", ED_COLUMNS),
        ("full_model", FULL_COLUMNS),
        ("full_without_demographics", NO_DEMO_COLUMNS),
    ):
        result = repeated_cv.fit_on_fold(X_train, y_train, X_holdout, y_holdout, cols, name)
        rows.append({
            "model": name,
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": result.roc_auc,
            "pr_auc": result.pr_auc,
            "brier_score": result.brier_score,
        })
    table = pd.DataFrame(rows)
    ed = table.set_index("model").loc["ed_history"]
    full = table.set_index("model").loc["full_model"]
    nodemo = table.set_index("model").loc["full_without_demographics"]
    extras = pd.DataFrame([
        {
            "model": "delta_full_minus_ed",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": full["roc_auc"] - ed["roc_auc"],
            "pr_auc": full["pr_auc"] - ed["pr_auc"],
            "brier_score": full["brier_score"] - ed["brier_score"],
        },
        {
            "model": "delta_nodemo_minus_ed",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": nodemo["roc_auc"] - ed["roc_auc"],
            "pr_auc": nodemo["pr_auc"] - ed["pr_auc"],
            "brier_score": nodemo["brier_score"] - ed["brier_score"],
        },
        {
            "model": "delta_nodemo_minus_full",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": nodemo["roc_auc"] - full["roc_auc"],
            "pr_auc": nodemo["pr_auc"] - full["pr_auc"],
            "brier_score": nodemo["brier_score"] - full["brier_score"],
        },
    ])
    return pd.concat([table, extras], ignore_index=True)


def write_figure(fold_df: pd.DataFrame, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].boxplot(
        [fold_df["delta_roc_full_minus_ed"], fold_df["delta_roc_nodemo_minus_ed"]],
        tick_labels=["Full − ED", "No-demo − ED"],
    )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("CV Δ ROC-AUC")
    axes[1].boxplot(
        [fold_df["delta_pr_full_minus_ed"], fold_df["delta_pr_nodemo_minus_ed"]],
        tick_labels=["Full − ED", "No-demo − ED"],
    )
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("CV Δ PR-AUC")
    fig.suptitle(
        "Demographic-block ablation (same training CV folds; holdout unused for selection)"
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _fmt_stats_table(summary: pd.DataFrame, metrics: list[str]) -> str:
    row = summary.set_index("metric")
    lines = [
        "| metric | mean | SD | median | min | max | p2.5 | p97.5 | n_pos / n_brier_better |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in metrics:
        r = row.loc[name]
        extra = ""
        if "n_folds_positive" in r.index and pd.notna(r["n_folds_positive"]):
            extra = f"{int(r['n_folds_positive'])}/25"
        elif "n_folds_improved_brier" in r.index and pd.notna(r["n_folds_improved_brier"]):
            extra = f"{int(r['n_folds_improved_brier'])}/25"
        lines.append(
            f"| {name} | {r['mean']:.4f} | {r['std']:.4f} | {r['median']:.4f} | "
            f"{r['min']:.4f} | {r['max']:.4f} | {r['p2_5']:.4f} | {r['p97_5']:.4f} | {extra} |"
        )
    return "\n".join(lines)


def write_summary(path, fold_df: pd.DataFrame, holdout: pd.DataFrame) -> None:
    n = len(fold_df)
    summary = summarize_deltas(fold_df)
    full_ed_roc = fold_df["delta_roc_full_minus_ed"]
    nodemo_ed_roc = fold_df["delta_roc_nodemo_minus_ed"]
    full_ed_pr = fold_df["delta_pr_full_minus_ed"]
    nodemo_ed_pr = fold_df["delta_pr_nodemo_minus_ed"]
    remain_roc = float(nodemo_ed_roc.mean() / full_ed_roc.mean()) if full_ed_roc.mean() else float("nan")
    remain_pr = float(nodemo_ed_pr.mean() / full_ed_pr.mean()) if full_ed_pr.mean() else float("nan")
    disappeared_roc = 1.0 - remain_roc
    disappeared_pr = 1.0 - remain_pr
    n_nodemo_pos_roc = int((nodemo_ed_roc > 0).sum())
    n_nodemo_pos_pr = int((nodemo_ed_pr > 0).sum())
    n_full_pos_roc = int((full_ed_roc > 0).sum())
    n_full_pos_pr = int((full_ed_pr > 0).sum())
    n_nodemo_brier = int((fold_df["delta_brier_nodemo_minus_ed"] < 0).sum())
    concentrated = remain_roc < 0.5
    ho = holdout.set_index("model")
    abs_table = _fmt_stats_table(summary, [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        "nodemo_roc_auc", "nodemo_pr_auc", "nodemo_brier",
    ])
    delta_table = _fmt_stats_table(summary, [
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        "delta_roc_nodemo_minus_ed", "delta_pr_nodemo_minus_ed", "delta_brier_nodemo_minus_ed",
        "delta_roc_nodemo_minus_full", "delta_pr_nodemo_minus_full", "delta_brier_nodemo_minus_full",
    ])
    if remain_roc > 1.0:
        roc_disappear_text = (
            f"Removing the block did not reduce the mean ROC increment "
            f"(full {full_ed_roc.mean():+.3f}; no-demographics {nodemo_ed_roc.mean():+.3f}). "
            f"The mean increment is slightly larger without these four variables. "
            f"That is a small paired difference (mean no-demo−full ROC "
            f"{fold_df['delta_roc_nodemo_minus_full'].mean():+.3f}) and should not be "
            f"read as evidence that the variables are harmful or that a reduced "
            f"model should be selected."
        )
        concentration_text = (
            "The mean ROC increment does not shrink when SEX, RACETHX, REGIONY3, "
            "and MARRY6X are removed from the full model. Together with the "
            "age-ablation result (AGEY3X accounted for only a modest slice), "
            "this does not support concentration of incremental signal in the "
            "non-age demographic block. Residual increment remains attributable "
            "to age, health, access, and/or SES in this design."
        )
        vs_age_clause = (
            "Removing these four variables did not shrink the increment, whereas "
            "removing AGEY3X alone reduced it modestly. The non-age demographic "
            "block is not a larger driver than age in this leave-one-block-out design."
        )
    elif concentrated:
        roc_disappear_text = (
            f"About {disappeared_roc:.0%} of the mean ROC increment is associated "
            f"with including SEX, RACETHX, REGIONY3, and MARRY6X "
            f"({remain_roc:.0%} remains without them)."
        )
        concentration_text = (
            "These four demographic variables account for more than half of the "
            "mean ROC increment. Incremental signal is substantially concentrated "
            "in the remaining demographic block, though residual increment may "
            "still exist in age, health, access, and SES."
        )
        vs_age_clause = (
            "Removing these four variables reduces the increment more than "
            "removing age alone did."
        )
    else:
        roc_disappear_text = (
            f"About {disappeared_roc:.0%} of the mean ROC increment is associated "
            f"with including SEX, RACETHX, REGIONY3, and MARRY6X "
            f"({remain_roc:.0%} remains without them)."
        )
        concentration_text = (
            "At least half of the mean ROC increment remains after removing "
            "SEX, RACETHX, REGIONY3, and MARRY6X. Together with the age-ablation "
            "result, this favors incremental signal that is distributed across "
            "non-ED information rather than concentrated in these four variables."
        )
        vs_age_clause = (
            "Removing these four variables changes the increment less than, or "
            "comparably to, removing age, in the sense that most of the increment remains."
        )

    md = f"""# Demographic-block ablation (SEX, RACETHX, REGIONY3, MARRY6X removed)

Same analytic cohort, same training portion (n=3,831), same 5x5
RepeatedStratifiedKFold (random_state={repeated_cv.CV_RANDOM_STATE}) as the
existing repeated-CV and age-ablation experiments. AGEY3X is retained.
Preprocessing is fit inside each fold. The original 25% holdout is scored
only after CV, as a locked check. It was not used to choose a model.
Existing holdout, repeated-CV, family-ablation, and age-ablation files
were not overwritten.

Removed from Model C only: SEX, RACETHX, REGIONY3, MARRY6X.

## CV absolute metrics (25 folds)

{abs_table}

## Paired fold-level deltas (25 folds)

{delta_table}

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## 1. How much incremental value disappears without the demographic block?
CV mean Δ ROC-AUC vs ED-history: full {full_ed_roc.mean():+.3f}; no-demographics {nodemo_ed_roc.mean():+.3f}.
{roc_disappear_text}
CV mean Δ PR-AUC vs ED-history: full {full_ed_pr.mean():+.3f}; no-demographics {nodemo_ed_pr.mean():+.3f}
({remain_pr:.0%} of the PR increment remains without the block).

## 2. Does the no-demographics model still outperform ED history consistently?
ROC-AUC increment vs ED-history is positive in {n_nodemo_pos_roc}/{n} folds
(full model: {n_full_pos_roc}/{n}).
PR-AUC increment is positive in {n_nodemo_pos_pr}/{n} folds
(full model: {n_full_pos_pr}/{n}).
Brier improved vs ED-history in {n_nodemo_brier}/{n} folds.

## 3. How much PR-AUC improvement remains?
PR-AUC increment vs ED-history mean {nodemo_ed_pr.mean():+.3f}
(full {full_ed_pr.mean():+.3f}); positive in {n_nodemo_pos_pr}/{n} folds.

## 4. Comparison with the previous age-ablation result
Age ablation (AGEY3X removed, these four variables kept) left about
+{AGE_ABLATION_CV['noage_minus_ed_roc']:.3f} ROC / +{AGE_ABLATION_CV['noage_minus_ed_pr']:.3f} PR
vs ED-history (roughly 83% of the ROC increment and 95% of the PR increment).
This demographic-block ablation (AGEY3X kept; SEX, RACETHX, REGIONY3, MARRY6X
removed) leaves {nodemo_ed_roc.mean():+.3f} ROC / {nodemo_ed_pr.mean():+.3f} PR
vs ED-history. {vs_age_clause}

## 5. Distributed vs concentrated in demographic variables?
{concentration_text}

## 6. Locked holdout (not used for selection)
- ED-history: ROC-AUC {ho.loc['ed_history', 'roc_auc']:.3f}, PR-AUC {ho.loc['ed_history', 'pr_auc']:.3f}, Brier {ho.loc['ed_history', 'brier_score']:.3f}
- Full model: ROC-AUC {ho.loc['full_model', 'roc_auc']:.3f}, PR-AUC {ho.loc['full_model', 'pr_auc']:.3f}, Brier {ho.loc['full_model', 'brier_score']:.3f}
- Full without demographics: ROC-AUC {ho.loc['full_without_demographics', 'roc_auc']:.3f}, PR-AUC {ho.loc['full_without_demographics', 'pr_auc']:.3f}, Brier {ho.loc['full_without_demographics', 'brier_score']:.3f}
- Holdout Δ full−ED: ROC {ho.loc['delta_full_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc['delta_full_minus_ed', 'pr_auc']:+.3f}
- Holdout Δ no-demographics−ED: ROC {ho.loc['delta_nodemo_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc['delta_nodemo_minus_ed', 'pr_auc']:+.3f}

Treat the holdout as a first-run internal evaluation set, not as
evidence used to pick a model. It is not external, pristine, or
independently confirmatory validation.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
"""
    path.write_text(md, encoding="utf-8")


def run_experiment() -> dict:
    assert_column_sets()
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = download.main()
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df)
    X = features.build_feature_matrix(usable, FULL_COLUMNS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)
    X_train, y_train, X_holdout, y_holdout = repeated_cv.training_portion(X, y)

    fold_df = run_paired_cv(X_train, y_train)
    fold_df.to_csv(config.OUTPUTS_DIR / "demographic_ablation_cv.csv", index=False)

    holdout = evaluate_locked_holdout(X_train, y_train, X_holdout, y_holdout)
    holdout.to_csv(config.OUTPUTS_DIR / "demographic_ablation_holdout.csv", index=False)

    write_figure(fold_df, config.FIGURES_DIR / "demographic_ablation.png")
    write_summary(config.OUTPUTS_DIR / "demographic_ablation_summary.md", fold_df, holdout)
    print(f"Demographic-ablation CV folds written: {len(fold_df)}")
    print("Locked holdout scored after CV; existing output files not modified.")
    return {"cv": fold_df, "holdout": holdout}


def main() -> int:
    run_experiment()
    return 0


if __name__ == "__main__":
    sys.exit(main())
