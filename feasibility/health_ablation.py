"""
Health-status block ablation: full model vs full without RTHLTH6 and
MNHLTH6. Age, demographics, access, SES, and ED-history are retained.
Same training-only 5x5 CV folds as repeated_cv, plus a locked holdout
check and an analytic-cohort missingness audit.

Does not write first-run, family-ablation, repeated-CV, age-ablation,
or demographic-ablation filenames.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from . import config, download, features, ingest, inspect, longitudinal, repeated_cv

HEALTH_BLOCK = ["RTHLTH6", "MNHLTH6"]
RETAINED_DEMOGRAPHICS = ["AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X"]
ED_COLUMNS = list(repeated_cv.ED_COLUMNS)
FULL_COLUMNS = list(repeated_cv.FULL_COLUMNS)
NO_HEALTH_COLUMNS = [c for c in FULL_COLUMNS if c not in HEALTH_BLOCK]

# Prior full-model block-ablation CV means, cited only for comparison.
AGE_ABLATION_CV = {
    "noage_minus_ed_roc": 0.0244,
    "noage_minus_ed_pr": 0.0342,
}
DEMO_ABLATION_CV = {
    "nodemo_minus_ed_roc": 0.0358,
    "nodemo_minus_ed_pr": 0.0357,
}

CROSS_EXPERIMENT_NOTE = (
    "Feature-family ablation and full-model block ablation address different "
    "questions: the former measures marginal contribution when adding a family "
    "to an ED-history baseline, whereas the latter measures how much "
    "performance changes when removing a block from the full model."
)


def no_health_columns() -> list[str]:
    return list(NO_HEALTH_COLUMNS)


def assert_column_sets() -> None:
    missing_block = [c for c in HEALTH_BLOCK if c not in FULL_COLUMNS]
    if missing_block:
        raise RuntimeError(f"Health block missing from full set: {missing_block}")
    leftover = set(HEALTH_BLOCK) & set(NO_HEALTH_COLUMNS)
    if leftover:
        raise RuntimeError(f"Health block must be fully removed: {leftover}")
    if set(NO_HEALTH_COLUMNS) != set(FULL_COLUMNS) - set(HEALTH_BLOCK):
        raise RuntimeError(
            "No-health set must equal the full set minus RTHLTH6 and MNHLTH6 only."
        )
    for name in RETAINED_DEMOGRAPHICS + ED_COLUMNS:
        if name not in NO_HEALTH_COLUMNS:
            raise RuntimeError(f"{name} must remain in the no-health set.")
    features.assert_no_leakage(ED_COLUMNS)
    features.assert_no_leakage(FULL_COLUMNS)
    features.assert_no_leakage(NO_HEALTH_COLUMNS)


def health_missingness_audit(analytic: pd.DataFrame) -> pd.DataFrame:
    """Analytic-cohort missingness only. Does not change sentinel handling."""
    table = inspect.missingness_table(analytic, HEALTH_BLOCK)
    rows = []
    n = int(len(analytic))
    for _, rec in table.iterrows():
        rows.append({
            "variable": rec["variable"],
            "population": "analytic_cohort",
            "analytic_n": n,
            "valid_count": rec["valid_count"],
            "sentinel_count": rec["sentinel_count"],
            "true_na_count": rec["missing_count"],
            "missing_pct_after_sentinel_recode": rec["missing_pct"],
        })
    return pd.DataFrame(rows)


def run_paired_cv(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """Same folds as repeated_cv (seed 2021, 5x5) with a third no-health model."""
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
        nohealth = repeated_cv.fit_on_fold(
            X_tr, y_tr, X_va, y_va, NO_HEALTH_COLUMNS, "full_without_health"
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
            "nohealth_roc_auc": nohealth.roc_auc,
            "nohealth_pr_auc": nohealth.pr_auc,
            "nohealth_brier": nohealth.brier_score,
            "delta_roc_full_minus_ed": full.roc_auc - ed.roc_auc,
            "delta_pr_full_minus_ed": full.pr_auc - ed.pr_auc,
            "delta_brier_full_minus_ed": full.brier_score - ed.brier_score,
            "delta_roc_nohealth_minus_ed": nohealth.roc_auc - ed.roc_auc,
            "delta_pr_nohealth_minus_ed": nohealth.pr_auc - ed.pr_auc,
            "delta_brier_nohealth_minus_ed": nohealth.brier_score - ed.brier_score,
            "delta_roc_nohealth_minus_full": nohealth.roc_auc - full.roc_auc,
            "delta_pr_nohealth_minus_full": nohealth.pr_auc - full.pr_auc,
            "delta_brier_nohealth_minus_full": nohealth.brier_score - full.brier_score,
            "holdout_seed": repeated_cv.HOLDOUT_SEED,
            "cv_random_state": repeated_cv.CV_RANDOM_STATE,
            "holdout_used": False,
        })
    return pd.DataFrame(rows)


def summarize_deltas(fold_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        "nohealth_roc_auc", "nohealth_pr_auc", "nohealth_brier",
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        "delta_roc_nohealth_minus_ed", "delta_pr_nohealth_minus_ed",
        "delta_brier_nohealth_minus_ed",
        "delta_roc_nohealth_minus_full", "delta_pr_nohealth_minus_full",
        "delta_brier_nohealth_minus_full",
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
        ("full_without_health", NO_HEALTH_COLUMNS),
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
    nohealth = table.set_index("model").loc["full_without_health"]
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
            "model": "delta_nohealth_minus_ed",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": nohealth["roc_auc"] - ed["roc_auc"],
            "pr_auc": nohealth["pr_auc"] - ed["pr_auc"],
            "brier_score": nohealth["brier_score"] - ed["brier_score"],
        },
        {
            "model": "delta_nohealth_minus_full",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": nohealth["roc_auc"] - full["roc_auc"],
            "pr_auc": nohealth["pr_auc"] - full["pr_auc"],
            "brier_score": nohealth["brier_score"] - full["brier_score"],
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
        [fold_df["delta_roc_full_minus_ed"], fold_df["delta_roc_nohealth_minus_ed"]],
        tick_labels=["Full − ED", "No-health − ED"],
    )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("CV Δ ROC-AUC")
    axes[1].boxplot(
        [fold_df["delta_pr_full_minus_ed"], fold_df["delta_pr_nohealth_minus_ed"]],
        tick_labels=["Full − ED", "No-health − ED"],
    )
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("CV Δ PR-AUC")
    fig.suptitle(
        "Health-status ablation (same training CV folds; holdout unused for selection)"
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


def _fmt_missingness(audit: pd.DataFrame) -> str:
    lines = [
        "| variable | analytic N | valid count | sentinel count | missing % after sentinel recode |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, rec in audit.iterrows():
        lines.append(
            f"| {rec['variable']} | {int(rec['analytic_n'])} | "
            f"{int(rec['valid_count'])} | {int(rec['sentinel_count'])} | "
            f"{float(rec['missing_pct_after_sentinel_recode']):.2f} |"
        )
    return "\n".join(lines)


def write_summary(
    path,
    fold_df: pd.DataFrame,
    holdout: pd.DataFrame,
    missingness: pd.DataFrame,
) -> None:
    n = len(fold_df)
    summary = summarize_deltas(fold_df)
    full_ed_roc = fold_df["delta_roc_full_minus_ed"]
    noh_ed_roc = fold_df["delta_roc_nohealth_minus_ed"]
    full_ed_pr = fold_df["delta_pr_full_minus_ed"]
    noh_ed_pr = fold_df["delta_pr_nohealth_minus_ed"]
    full_ed_brier = fold_df["delta_brier_full_minus_ed"]
    noh_ed_brier = fold_df["delta_brier_nohealth_minus_ed"]
    remain_roc = float(noh_ed_roc.mean() / full_ed_roc.mean()) if full_ed_roc.mean() else float("nan")
    remain_pr = float(noh_ed_pr.mean() / full_ed_pr.mean()) if full_ed_pr.mean() else float("nan")
    disappeared_roc = 1.0 - remain_roc
    n_noh_pos_roc = int((noh_ed_roc > 0).sum())
    n_noh_pos_pr = int((noh_ed_pr > 0).sum())
    n_full_pos_roc = int((full_ed_roc > 0).sum())
    n_full_pos_pr = int((full_ed_pr > 0).sum())
    n_noh_brier = int((noh_ed_brier < 0).sum())
    n_full_brier = int((full_ed_brier < 0).sum())
    ho = holdout.set_index("model")
    miss_max = float(missingness["missing_pct_after_sentinel_recode"].max())
    if miss_max < 5:
        miss_note = (
            f"After sentinel recoding, missingness on these two variables is "
            f"under 5% in the analytic cohort (max {miss_max:.2f}%). That is a "
            f"descriptive characteristic of this sample, not a reason to change "
            f"imputation or add missingness indicators."
        )
    elif miss_max < 15:
        miss_note = (
            f"After sentinel recoding, missingness is {miss_max:.2f}% at most "
            f"in the analytic cohort. That is a modest descriptive feature of "
            f"the experiment. Existing median/mode imputation inside each "
            f"training fold is unchanged. Missingness is not treated as a predictor."
        )
    else:
        miss_note = (
            f"After sentinel recoding, missingness reaches {miss_max:.2f}% in "
            f"the analytic cohort. That is a notable descriptive limitation for "
            f"interpreting the health-status block, but sentinel handling and "
            f"imputation were not changed for this experiment."
        )

    if remain_roc > 1.0:
        roc_text = (
            f"Removing RTHLTH6 and MNHLTH6 did not reduce the mean ROC increment "
            f"(full {full_ed_roc.mean():+.3f}; no-health {noh_ed_roc.mean():+.3f}). "
            f"The paired no-health−full mean ROC is "
            f"{fold_df['delta_roc_nohealth_minus_full'].mean():+.3f}. That is a "
            f"small descriptive difference and is not a reason to select the "
            f"reduced model."
        )
        remain_text = (
            "Removing health status does not eliminate the incremental signal. "
            "Substantial increment vs ED-history remains. Residual signal may "
            "arise from the remaining predictor groups (age, other demographics, "
            "access, socioeconomic status). This experiment does not isolate "
            "which of those groups is responsible."
        )
    elif remain_roc < 0.5:
        roc_text = (
            f"About {disappeared_roc:.0%} of the mean ROC increment vs ED-history "
            f"is associated with including RTHLTH6 and MNHLTH6 "
            f"({remain_roc:.0%} remains without them)."
        )
        remain_text = (
            "Removing health status removes more than half of the mean ROC "
            "increment. Residual increment vs ED-history may still arise from "
            "the remaining predictor groups; this experiment does not attribute "
            "that remainder to access or socioeconomic variables specifically."
        )
    else:
        roc_text = (
            f"About {disappeared_roc:.0%} of the mean ROC increment vs ED-history "
            f"is associated with including RTHLTH6 and MNHLTH6 "
            f"({remain_roc:.0%} remains without them)."
        )
        remain_text = (
            "Removing health status does not eliminate most of the incremental "
            "signal. Substantial increment vs ED-history remains. Residual "
            "signal may arise from the remaining predictor groups (age, other "
            "demographics, access, socioeconomic status). This experiment does "
            "not isolate which of those groups is responsible."
        )

    abs_table = _fmt_stats_table(summary, [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        "nohealth_roc_auc", "nohealth_pr_auc", "nohealth_brier",
    ])
    delta_table = _fmt_stats_table(summary, [
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        "delta_roc_nohealth_minus_ed", "delta_pr_nohealth_minus_ed",
        "delta_brier_nohealth_minus_ed",
        "delta_roc_nohealth_minus_full", "delta_pr_nohealth_minus_full",
        "delta_brier_nohealth_minus_full",
    ])

    md = f"""# Health-status block ablation (RTHLTH6 and MNHLTH6 removed)

Same analytic cohort, same 2022 any-ED outcome, same training portion
(n=3,831), same 5x5 RepeatedStratifiedKFold
(random_state={repeated_cv.CV_RANDOM_STATE}) as the existing repeated-CV,
age-ablation, and demographic-block experiments. AGEY3X and SEX, RACETHX,
REGIONY3, MARRY6X remain in Model C. Preprocessing is fit inside each fold.
The original 25% holdout is scored only after CV, as a locked check. It was
not used to choose a model. Existing experiment files were not overwritten.

Removed from Model C only: RTHLTH6, MNHLTH6.

{CROSS_EXPERIMENT_NOTE}

The 2.5th and 97.5th percentiles below are descriptive summaries of the 25
paired fold deltas. They are not confidence intervals. The 25 folds are not treated as 25 independent observations. No significance test and no
Nadeau-Bengio correction is applied here.

## Analytic-cohort missingness audit

Reporting only. Sentinel handling, imputation, and cohort construction are
unchanged. Missingness is not used as a predictor.

{_fmt_missingness(missingness)}

{miss_note}

## CV absolute metrics (25 folds)

{abs_table}

## Paired fold-level deltas (25 folds)

{delta_table}

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## 1. How much incremental value disappears without health status?
CV mean Δ ROC-AUC vs ED-history: full {full_ed_roc.mean():+.3f}; no-health {noh_ed_roc.mean():+.3f}.
{roc_text}
CV mean Δ PR-AUC vs ED-history: full {full_ed_pr.mean():+.3f}; no-health {noh_ed_pr.mean():+.3f}
({remain_pr:.0%} of the PR increment remains without the health-status block).

## 2. Does the no-health model still outperform ED history across repeated CV?
ROC-AUC increment vs ED-history is positive in {n_noh_pos_roc}/{n} folds
(full model: {n_full_pos_roc}/{n}).
PR-AUC increment is positive in {n_noh_pos_pr}/{n} folds
(full model: {n_full_pos_pr}/{n}).
These counts describe paired folds. They are not a significance test.

## 3. What happens to PR-AUC?
PR-AUC increment vs ED-history mean {noh_ed_pr.mean():+.3f}
(full {full_ed_pr.mean():+.3f}); positive in {n_noh_pos_pr}/{n} folds.
Mean no-health−full PR {fold_df['delta_pr_nohealth_minus_full'].mean():+.3f}.

## 4. What happens to Brier score?
Mean Brier vs ED-history: full {full_ed_brier.mean():+.4f}; no-health {noh_ed_brier.mean():+.4f}.
Brier improved vs ED-history in {n_noh_brier}/{n} folds (full model: {n_full_brier}/{n}).
Mean no-health−full Brier {fold_df['delta_brier_nohealth_minus_full'].mean():+.4f}.

## 5–6. Comparison with age and demographic-block ablation
{CROSS_EXPERIMENT_NOTE}

Age, demographic-block, and this health-status experiment are the same
kind of question: each removes a block from the current full model.

- Age ablation (AGEY3X removed): remaining increment vs ED-history about
  +{AGE_ABLATION_CV['noage_minus_ed_roc']:.3f} ROC / +{AGE_ABLATION_CV['noage_minus_ed_pr']:.3f} PR.
- Demographic-block ablation (SEX, RACETHX, REGIONY3, MARRY6X removed;
  AGEY3X kept): remaining increment vs ED-history about
  +{DEMO_ABLATION_CV['nodemo_minus_ed_roc']:.3f} ROC / +{DEMO_ABLATION_CV['nodemo_minus_ed_pr']:.3f} PR.
- Health-status ablation (RTHLTH6, MNHLTH6 removed): remaining increment
  vs ED-history {noh_ed_roc.mean():+.3f} ROC / {noh_ed_pr.mean():+.3f} PR.

These three remaining-increment figures can be compared with each other
because they use the same full-model leave-block-out design. They should
not be compared numerically with the earlier feature-family "add to
ED-history" deltas.

## 7. Does removing health status eliminate most incremental signal?
{remain_text}

## 8. Locked holdout (not used for selection)
- ED-history: ROC-AUC {ho.loc['ed_history', 'roc_auc']:.3f}, PR-AUC {ho.loc['ed_history', 'pr_auc']:.3f}, Brier {ho.loc['ed_history', 'brier_score']:.3f}
- Full model: ROC-AUC {ho.loc['full_model', 'roc_auc']:.3f}, PR-AUC {ho.loc['full_model', 'pr_auc']:.3f}, Brier {ho.loc['full_model', 'brier_score']:.3f}
- Full without health: ROC-AUC {ho.loc['full_without_health', 'roc_auc']:.3f}, PR-AUC {ho.loc['full_without_health', 'pr_auc']:.3f}, Brier {ho.loc['full_without_health', 'brier_score']:.3f}
- Holdout Δ full−ED: ROC {ho.loc['delta_full_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc['delta_full_minus_ed', 'pr_auc']:+.3f}
- Holdout Δ no-health−ED: ROC {ho.loc['delta_nohealth_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc['delta_nohealth_minus_ed', 'pr_auc']:+.3f}
- Holdout Δ no-health−full: ROC {ho.loc['delta_nohealth_minus_full', 'roc_auc']:+.3f}, PR {ho.loc['delta_nohealth_minus_full', 'pr_auc']:+.3f}

Treat the holdout as a first-run internal evaluation set, not as
evidence used to pick a model. It is not external, pristine, or
independently confirmatory validation.

## 9. Missingness as a limitation
{miss_note}

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
    missingness = health_missingness_audit(usable)
    print("Analytic-cohort health missingness:")
    print(missingness.to_string(index=False))

    X = features.build_feature_matrix(usable, FULL_COLUMNS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)
    X_train, y_train, X_holdout, y_holdout = repeated_cv.training_portion(X, y)

    fold_df = run_paired_cv(X_train, y_train)
    fold_df.to_csv(config.OUTPUTS_DIR / "health_ablation_cv.csv", index=False)

    holdout = evaluate_locked_holdout(X_train, y_train, X_holdout, y_holdout)
    holdout.to_csv(config.OUTPUTS_DIR / "health_ablation_holdout.csv", index=False)

    write_figure(fold_df, config.FIGURES_DIR / "health_ablation.png")
    write_summary(
        config.OUTPUTS_DIR / "health_ablation_summary.md",
        fold_df,
        holdout,
        missingness,
    )
    print(f"Health-ablation CV folds written: {len(fold_df)}")
    print("Locked holdout scored after CV; existing output files not modified.")
    return {"cv": fold_df, "holdout": holdout, "missingness": missingness}


def main() -> int:
    run_experiment()
    return 0


if __name__ == "__main__":
    sys.exit(main())
