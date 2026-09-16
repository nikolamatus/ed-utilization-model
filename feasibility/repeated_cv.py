"""
Repeated stratified CV on the *training portion only*.

The original 25% holdout is reconstructed with seed 42 and then left
unused. This module does not write first-run holdout filenames.

Writes:
  outputs/repeated_cv_metrics.csv
  outputs/repeated_cv_summary.csv
  outputs/repeated_cv_summary.md
  outputs/figures/repeated_cv_incremental_value.png
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold

from . import ablation, config, download, features, ingest, longitudinal, modeling

HOLDOUT_SEED = config.RANDOM_SEED  # 42 — only to recover the training 3,831
CV_N_SPLITS = 5
CV_N_REPEATS = 5
CV_RANDOM_STATE = 2021  # dedicated CV seed; not used for holdout or model selection
ED_COLUMNS = list(ablation.FAMILY_COLUMNS["ed_history_only"])
FULL_COLUMNS = list(ablation.FAMILY_COLUMNS["full_model"])

HOLDOUT_BENCHMARK = {
    "source": "first-run holdout (outputs/model_metrics.csv); not refit here; not used for inference",
    "ed_history_roc_auc": 0.709095145346402,
    "ed_history_pr_auc": 0.33079411280933274,
    "ed_history_brier": 0.10528623721670442,
    "full_roc_auc": 0.7740062410991038,
    "full_pr_auc": 0.41593508223653725,
    "full_brier": 0.09938997744487747,
    "delta_roc": 0.06491109575270182,
    "delta_pr": 0.0851409694272045,
}


def training_portion(X: pd.DataFrame, y: pd.Series):
    """Reconstruct the original 75% train fold. The 25% holdout is discarded."""
    X_train, X_holdout, y_train, y_holdout = modeling._split(X, y)
    return X_train, y_train, X_holdout, y_holdout


def cv_splitter() -> RepeatedStratifiedKFold:
    return RepeatedStratifiedKFold(
        n_splits=CV_N_SPLITS,
        n_repeats=CV_N_REPEATS,
        random_state=CV_RANDOM_STATE,
    )


def describe_numeric(values: pd.Series) -> dict:
    s = pd.to_numeric(values, errors="coerce").dropna()
    return {
        "n": int(s.shape[0]),
        "mean": float(s.mean()),
        "std": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
        "median": float(s.median()),
        "min": float(s.min()),
        "max": float(s.max()),
        "p2_5": float(s.quantile(0.025)),
        "p97_5": float(s.quantile(0.975)),
    }


def fit_on_fold(X_tr, y_tr, X_va, y_va, cols: list[str], model_name: str) -> modeling.EvalResult:
    features.assert_no_leakage(cols)
    numeric, categorical = features.split_columns_by_treatment(cols)
    result, _pipe, _prob = modeling.full_logistic_model(
        X_tr[cols], y_tr, X_va[cols], y_va, numeric, categorical, model_name=model_name
    )
    return result


def run_repeated_cv(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """25 fold-level rows. Preprocessing is fit inside each fold via the sklearn Pipeline."""
    X_train = X_train.reset_index(drop=True)
    y_train = pd.Series(np.asarray(y_train), name="y")
    rows = []
    splitter = cv_splitter()
    for i, (tr_idx, va_idx) in enumerate(splitter.split(X_train, y_train)):
        repeat = i // CV_N_SPLITS
        fold = i % CV_N_SPLITS
        X_tr, X_va = X_train.iloc[tr_idx], X_train.iloc[va_idx]
        y_tr, y_va = y_train.iloc[tr_idx], y_train.iloc[va_idx]
        ed = fit_on_fold(X_tr, y_tr, X_va, y_va, ED_COLUMNS, "ed_history")
        full = fit_on_fold(X_tr, y_tr, X_va, y_va, FULL_COLUMNS, "full_model")
        rows.append({
            "repeat": repeat,
            "fold": fold,
            "fold_index": i,
            "n_cv_train": int(len(y_tr)),
            "n_cv_val": int(len(y_va)),
            "val_prevalence": float(np.mean(y_va)),
            "ed_roc_auc": ed.roc_auc,
            "ed_pr_auc": ed.pr_auc,
            "ed_brier": ed.brier_score,
            "full_roc_auc": full.roc_auc,
            "full_pr_auc": full.pr_auc,
            "full_brier": full.brier_score,
            "delta_roc_auc": full.roc_auc - ed.roc_auc,
            "delta_pr_auc": full.pr_auc - ed.pr_auc,
            "delta_brier": full.brier_score - ed.brier_score,
            "holdout_seed": HOLDOUT_SEED,
            "cv_random_state": CV_RANDOM_STATE,
            "n_splits": CV_N_SPLITS,
            "n_repeats": CV_N_REPEATS,
            "holdout_used": False,
        })
    return pd.DataFrame(rows)


def summary_table(fold_df: pd.DataFrame) -> pd.DataFrame:
    blocks = []
    metric_map = {
        "ed_roc_auc": "ed_history_roc_auc",
        "ed_pr_auc": "ed_history_pr_auc",
        "ed_brier": "ed_history_brier",
        "full_roc_auc": "full_roc_auc",
        "full_pr_auc": "full_pr_auc",
        "full_brier": "full_brier",
        "delta_roc_auc": "delta_roc_auc_full_minus_ed",
        "delta_pr_auc": "delta_pr_auc_full_minus_ed",
        "delta_brier": "delta_brier_full_minus_ed",
    }
    for col, label in metric_map.items():
        stats = describe_numeric(fold_df[col])
        stats["metric"] = label
        blocks.append(stats)
    table = pd.DataFrame(blocks)
    n_pos_roc = int((fold_df["delta_roc_auc"] > 0).sum())
    n_pos_pr = int((fold_df["delta_pr_auc"] > 0).sum())
    n_neg_brier = int((fold_df["delta_brier"] < 0).sum())
    extra = pd.DataFrame([
        {
            "metric": "n_folds_positive_delta_roc_auc",
            "n": int(len(fold_df)),
            "mean": n_pos_roc,
            "std": np.nan,
            "median": n_pos_roc,
            "min": n_pos_roc,
            "max": n_pos_roc,
            "p2_5": np.nan,
            "p97_5": np.nan,
        },
        {
            "metric": "n_folds_positive_delta_pr_auc",
            "n": int(len(fold_df)),
            "mean": n_pos_pr,
            "std": np.nan,
            "median": n_pos_pr,
            "min": n_pos_pr,
            "max": n_pos_pr,
            "p2_5": np.nan,
            "p97_5": np.nan,
        },
        {
            "metric": "n_folds_brier_improved",
            "n": int(len(fold_df)),
            "mean": n_neg_brier,
            "std": np.nan,
            "median": n_neg_brier,
            "min": n_neg_brier,
            "max": n_neg_brier,
            "p2_5": np.nan,
            "p97_5": np.nan,
        },
        {
            "metric": "note",
            "n": int(len(fold_df)),
            "mean": np.nan,
            "std": np.nan,
            "median": np.nan,
            "min": np.nan,
            "max": np.nan,
            "p2_5": np.nan,
            "p97_5": np.nan,
        },
    ])
    return pd.concat([table, extra], ignore_index=True)


def write_figure(fold_df: pd.DataFrame, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].boxplot(fold_df["delta_roc_auc"], vert=True)
    axes[0].axhline(HOLDOUT_BENCHMARK["delta_roc"], linestyle="--", color="gray", label="holdout +0.065")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("CV Δ ROC-AUC (full − ED)")
    axes[0].set_ylabel("Delta")
    axes[0].legend(fontsize=8)
    axes[1].boxplot(fold_df["delta_pr_auc"], vert=True)
    axes[1].axhline(HOLDOUT_BENCHMARK["delta_pr"], linestyle="--", color="gray", label="holdout +0.085")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("CV Δ PR-AUC (full − ED)")
    axes[1].legend(fontsize=8)
    fig.suptitle("Repeated CV incremental value (train portion only; holdout unused)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def write_summary_md(path, fold_df: pd.DataFrame, summary: pd.DataFrame) -> None:
    stats = summary.set_index("metric")
    n = len(fold_df)
    n_pos_roc = int((fold_df["delta_roc_auc"] > 0).sum())
    n_pos_pr = int((fold_df["delta_pr_auc"] > 0).sum())
    n_brier_better = int((fold_df["delta_brier"] < 0).sum())
    mean_droc = stats.loc["delta_roc_auc_full_minus_ed", "mean"]
    mean_dpr = stats.loc["delta_pr_auc_full_minus_ed", "mean"]
    mean_dbrier = stats.loc["delta_brier_full_minus_ed", "mean"]
    holdout_optimistic_roc = HOLDOUT_BENCHMARK["delta_roc"] > stats.loc["delta_roc_auc_full_minus_ed", "p97_5"]
    holdout_optimistic_pr = HOLDOUT_BENCHMARK["delta_pr"] > stats.loc["delta_pr_auc_full_minus_ed", "p97_5"]
    if holdout_optimistic_roc or holdout_optimistic_pr:
        optimism = (
            "The first-run holdout lifts sit at or above the upper tail of this "
            "repeated-CV distribution and may be somewhat optimistic relative to "
            "typical training-fold increments."
        )
        strengthen = "The CV evidence supports a positive increment but suggests the single holdout lift is on the high side."
    elif mean_droc > 0 and n_pos_roc >= int(0.8 * n):
        optimism = (
            "The first-run holdout lifts are larger than the CV means but are not "
            "extreme relative to the empirical 2.5th-97.5th percentile range."
        )
        strengthen = "The CV evidence strengthens the holdout finding: the increment is repeatedly positive on the training portion."
    else:
        optimism = "The CV increment is weaker or less consistent than the holdout result."
        strengthen = "The CV evidence weakens confidence that the holdout increment is stable."

    consistently_better = n_pos_roc == n and n_pos_pr == n
    md = f"""# Repeated stratified CV (training portion only)

This experiment does **not** replace the first-run 25% holdout.
The holdout (n_test=1,277) remains a first-run internal evaluation set
(not an external, pristine, or independently confirmatory benchmark).
CV uses only the original training portion (n=3,831), reconstructed with
holdout seed={HOLDOUT_SEED}. RepeatedStratifiedKFold: {CV_N_REPEATS} repeats
x {CV_N_SPLITS} folds, random_state={CV_RANDOM_STATE}. Stratified on the
2022 any-ED outcome. Preprocessing is fit inside each CV training fold.

These percentiles are an **empirical repeated-CV distribution**, not
formal external-validation confidence intervals.

## First-run holdout metrics (not refit; not used for inference)
- ED-history ROC-AUC {HOLDOUT_BENCHMARK['ed_history_roc_auc']:.3f}, PR-AUC {HOLDOUT_BENCHMARK['ed_history_pr_auc']:.3f}, Brier {HOLDOUT_BENCHMARK['ed_history_brier']:.3f}
- Full model ROC-AUC {HOLDOUT_BENCHMARK['full_roc_auc']:.3f}, PR-AUC {HOLDOUT_BENCHMARK['full_pr_auc']:.3f}, Brier {HOLDOUT_BENCHMARK['full_brier']:.3f}
- Incremental ROC-AUC {HOLDOUT_BENCHMARK['delta_roc']:+.3f}, PR-AUC {HOLDOUT_BENCHMARK['delta_pr']:+.3f}

## Repeated-CV means (25 folds)
- ED-history ROC-AUC {stats.loc['ed_history_roc_auc', 'mean']:.3f} (SD {stats.loc['ed_history_roc_auc', 'std']:.3f})
- Full model ROC-AUC {stats.loc['full_roc_auc', 'mean']:.3f} (SD {stats.loc['full_roc_auc', 'std']:.3f})
- ED-history PR-AUC {stats.loc['ed_history_pr_auc', 'mean']:.3f} (SD {stats.loc['ed_history_pr_auc', 'std']:.3f})
- Full model PR-AUC {stats.loc['full_pr_auc', 'mean']:.3f} (SD {stats.loc['full_pr_auc', 'std']:.3f})
- Mean incremental ROC-AUC {mean_droc:+.3f} (SD {stats.loc['delta_roc_auc_full_minus_ed', 'std']:.3f}; min {stats.loc['delta_roc_auc_full_minus_ed', 'min']:+.3f}; max {stats.loc['delta_roc_auc_full_minus_ed', 'max']:+.3f}; 2.5th {stats.loc['delta_roc_auc_full_minus_ed', 'p2_5']:+.3f}; 97.5th {stats.loc['delta_roc_auc_full_minus_ed', 'p97_5']:+.3f})
- Mean incremental PR-AUC {mean_dpr:+.3f} (SD {stats.loc['delta_pr_auc_full_minus_ed', 'std']:.3f}; min {stats.loc['delta_pr_auc_full_minus_ed', 'min']:+.3f}; max {stats.loc['delta_pr_auc_full_minus_ed', 'max']:+.3f}; 2.5th {stats.loc['delta_pr_auc_full_minus_ed', 'p2_5']:+.3f}; 97.5th {stats.loc['delta_pr_auc_full_minus_ed', 'p97_5']:+.3f})
- Mean incremental Brier {mean_dbrier:+.4f} (negative means the full model is better)

## Answers
1. Is the full model consistently better than ED history during repeated CV?
   {'Yes: ROC-AUC and PR-AUC increments were positive in every fold.' if consistently_better else f'ROC-AUC increment was positive in {n_pos_roc}/{n} folds; PR-AUC in {n_pos_pr}/{n} folds.'}

2. Incremental ROC-AUC positive in most/all folds?
   {n_pos_roc}/{n} folds positive.

3. Incremental PR-AUC positive in most/all folds?
   {n_pos_pr}/{n} folds positive.

4. Does Brier generally improve?
   Brier was lower (better) for the full model in {n_brier_better}/{n} folds. Mean Brier delta {mean_dbrier:+.4f}.

5. Does CV strengthen or weaken the original holdout finding?
   {strengthen}

6. Signs the holdout +0.065 / +0.085 may be unusually optimistic?
   {optimism}

Unweighted analytic-sample CV only. Not a national estimate, clinical
validation, causal finding, or deployment result.
"""
    path.write_text(md, encoding="utf-8")


def run_experiment() -> dict:
    features.assert_no_leakage(ED_COLUMNS)
    features.assert_no_leakage(FULL_COLUMNS)
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = download.main()
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df)
    X = features.build_feature_matrix(usable, FULL_COLUMNS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)

    X_train, y_train, X_holdout, y_holdout = training_portion(X, y)
    if len(X_holdout) == 0:
        raise RuntimeError("Holdout reconstruction failed.")
    # Holdout is intentionally unused after this point.
    del X_holdout, y_holdout

    fold_df = run_repeated_cv(X_train, y_train)
    summary = summary_table(fold_df)
    fold_df.to_csv(config.OUTPUTS_DIR / "repeated_cv_metrics.csv", index=False)
    summary.to_csv(config.OUTPUTS_DIR / "repeated_cv_summary.csv", index=False)
    write_figure(fold_df, config.FIGURES_DIR / "repeated_cv_incremental_value.png")
    write_summary_md(config.OUTPUTS_DIR / "repeated_cv_summary.md", fold_df, summary)
    print(f"CV folds written: {len(fold_df)}")
    print(f"Training portion n={len(X_train)}; holdout unused.")
    return {"folds": fold_df, "summary": summary}


def main() -> int:
    run_experiment()
    return 0


if __name__ == "__main__":
    sys.exit(main())
