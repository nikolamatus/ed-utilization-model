"""
Shared full-model leave-one-block-out runner used by B4 (access) and
B5 (SES). Same folds, seeds, preprocessing, and holdout rule as the
age / demographic / health experiments.

Does not write those earlier experiment filenames. Does not compute
p-values, Nadeau-Bengio corrections, or Holm-Bonferroni adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config, download, features, ingest, longitudinal, repeated_cv

ED_COLUMNS = list(repeated_cv.ED_COLUMNS)
FULL_COLUMNS = list(repeated_cv.FULL_COLUMNS)

CROSS_EXPERIMENT_NOTE = (
    "Feature-family ablation and full-model block ablation address different "
    "questions: the former measures marginal contribution when adding a family "
    "to an ED-history baseline, whereas the latter measures how much "
    "performance changes when removing a block from the full model."
)

# Prior Family-B remaining increments vs ED-history (descriptive only).
PRIOR_VS_ED = {
    "B1 age (AGEY3X)": (0.0244, 0.0342),
    "B2 demographics (SEX, RACETHX, REGIONY3, MARRY6X)": (0.0358, 0.0357),
    "B3 health (RTHLTH6, MNHLTH6)": (0.0344, 0.0401),
}


@dataclass(frozen=True)
class BlockSpec:
    experiment_id: str
    slug: str
    title: str
    block: tuple[str, ...]
    reduced_model_name: str
    prefix: str
    must_retain: tuple[str, ...]


def reduced_columns(spec: BlockSpec) -> list[str]:
    return [c for c in FULL_COLUMNS if c not in spec.block]


def assert_column_sets(spec: BlockSpec) -> None:
    missing = [c for c in spec.block if c not in FULL_COLUMNS]
    if missing:
        raise RuntimeError(f"{spec.experiment_id} block missing from full set: {missing}")
    reduced = reduced_columns(spec)
    leftover = set(spec.block) & set(reduced)
    if leftover:
        raise RuntimeError(f"{spec.experiment_id} block must be fully removed: {leftover}")
    if set(reduced) != set(FULL_COLUMNS) - set(spec.block):
        raise RuntimeError(f"{spec.experiment_id} reduced set must equal full minus that block only.")
    for name in spec.must_retain:
        if name not in reduced:
            raise RuntimeError(f"{name} must remain in the {spec.slug} reduced set.")
    features.assert_no_leakage(ED_COLUMNS)
    features.assert_no_leakage(FULL_COLUMNS)
    features.assert_no_leakage(reduced)


def run_paired_cv(X_train: pd.DataFrame, y_train: pd.Series, spec: BlockSpec) -> pd.DataFrame:
    X_train = X_train.reset_index(drop=True)
    y_train = pd.Series(np.asarray(y_train), name="y")
    reduced = reduced_columns(spec)
    p = spec.prefix
    rows = []
    splitter = repeated_cv.cv_splitter()
    for i, (tr_idx, va_idx) in enumerate(splitter.split(X_train, y_train)):
        repeat = i // repeated_cv.CV_N_SPLITS
        fold = i % repeated_cv.CV_N_SPLITS
        X_tr, X_va = X_train.iloc[tr_idx], X_train.iloc[va_idx]
        y_tr, y_va = y_train.iloc[tr_idx], y_train.iloc[va_idx]
        ed = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, ED_COLUMNS, "ed_history")
        full = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, FULL_COLUMNS, "full_model")
        red = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, reduced, spec.reduced_model_name)
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
            f"{p}_roc_auc": red.roc_auc,
            f"{p}_pr_auc": red.pr_auc,
            f"{p}_brier": red.brier_score,
            "delta_roc_full_minus_ed": full.roc_auc - ed.roc_auc,
            "delta_pr_full_minus_ed": full.pr_auc - ed.pr_auc,
            "delta_brier_full_minus_ed": full.brier_score - ed.brier_score,
            f"delta_roc_{p}_minus_ed": red.roc_auc - ed.roc_auc,
            f"delta_pr_{p}_minus_ed": red.pr_auc - ed.pr_auc,
            f"delta_brier_{p}_minus_ed": red.brier_score - ed.brier_score,
            f"delta_roc_{p}_minus_full": red.roc_auc - full.roc_auc,
            f"delta_pr_{p}_minus_full": red.pr_auc - full.pr_auc,
            f"delta_brier_{p}_minus_full": red.brier_score - full.brier_score,
            "holdout_seed": repeated_cv.HOLDOUT_SEED,
            "cv_random_state": repeated_cv.CV_RANDOM_STATE,
            "holdout_used": False,
            "experiment_id": spec.experiment_id,
        })
    return pd.DataFrame(rows)


def summarize_deltas(fold_df: pd.DataFrame, spec: BlockSpec) -> pd.DataFrame:
    p = spec.prefix
    cols = [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        f"{p}_roc_auc", f"{p}_pr_auc", f"{p}_brier",
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        f"delta_roc_{p}_minus_ed", f"delta_pr_{p}_minus_ed", f"delta_brier_{p}_minus_ed",
        f"delta_roc_{p}_minus_full", f"delta_pr_{p}_minus_full", f"delta_brier_{p}_minus_full",
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


def evaluate_locked_holdout(X_train, y_train, X_holdout, y_holdout, spec: BlockSpec) -> pd.DataFrame:
    reduced = reduced_columns(spec)
    p = spec.prefix
    rows = []
    for name, cols in (
        ("ed_history", ED_COLUMNS),
        ("full_model", FULL_COLUMNS),
        (spec.reduced_model_name, reduced),
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
            "experiment_id": spec.experiment_id,
        })
    table = pd.DataFrame(rows)
    ed = table.set_index("model").loc["ed_history"]
    full = table.set_index("model").loc["full_model"]
    red = table.set_index("model").loc[spec.reduced_model_name]
    extras = pd.DataFrame([
        {
            "model": "delta_full_minus_ed",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": full["roc_auc"] - ed["roc_auc"],
            "pr_auc": full["pr_auc"] - ed["pr_auc"],
            "brier_score": full["brier_score"] - ed["brier_score"],
            "experiment_id": spec.experiment_id,
        },
        {
            "model": f"delta_{p}_minus_ed",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": red["roc_auc"] - ed["roc_auc"],
            "pr_auc": red["pr_auc"] - ed["pr_auc"],
            "brier_score": red["brier_score"] - ed["brier_score"],
            "experiment_id": spec.experiment_id,
        },
        {
            "model": f"delta_{p}_minus_full",
            "split": "locked_holdout_not_used_for_selection",
            "n_train": int(len(y_train)),
            "n_test": int(len(y_holdout)),
            "roc_auc": red["roc_auc"] - full["roc_auc"],
            "pr_auc": red["pr_auc"] - full["pr_auc"],
            "brier_score": red["brier_score"] - full["brier_score"],
            "experiment_id": spec.experiment_id,
        },
    ])
    return pd.concat([table, extras], ignore_index=True)


def write_figure(fold_df: pd.DataFrame, spec: BlockSpec, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    p = spec.prefix
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].boxplot(
        [fold_df["delta_roc_full_minus_ed"], fold_df[f"delta_roc_{p}_minus_ed"]],
        tick_labels=["Full − ED", f"No-{spec.slug} − ED"],
    )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("CV Δ ROC-AUC")
    axes[1].boxplot(
        [fold_df["delta_pr_full_minus_ed"], fold_df[f"delta_pr_{p}_minus_ed"]],
        tick_labels=["Full − ED", f"No-{spec.slug} − ED"],
    )
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("CV Δ PR-AUC")
    fig.suptitle(
        f"{spec.title} (same training CV folds; holdout unused for selection)"
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


def write_summary(path, fold_df: pd.DataFrame, holdout: pd.DataFrame, spec: BlockSpec) -> None:
    n = len(fold_df)
    p = spec.prefix
    summary = summarize_deltas(fold_df, spec)
    full_ed_roc = fold_df["delta_roc_full_minus_ed"]
    red_ed_roc = fold_df[f"delta_roc_{p}_minus_ed"]
    full_ed_pr = fold_df["delta_pr_full_minus_ed"]
    red_ed_pr = fold_df[f"delta_pr_{p}_minus_ed"]
    full_ed_brier = fold_df["delta_brier_full_minus_ed"]
    red_ed_brier = fold_df[f"delta_brier_{p}_minus_ed"]
    remain_roc = float(red_ed_roc.mean() / full_ed_roc.mean()) if full_ed_roc.mean() else float("nan")
    remain_pr = float(red_ed_pr.mean() / full_ed_pr.mean()) if full_ed_pr.mean() else float("nan")
    disappeared_roc = 1.0 - remain_roc
    block_list = ", ".join(spec.block)
    ho = holdout.set_index("model")
    if remain_roc > 1.0:
        roc_text = (
            f"Removing {block_list} did not reduce the mean ROC increment "
            f"(full {full_ed_roc.mean():+.3f}; no-{spec.slug} {red_ed_roc.mean():+.3f}). "
            f"The paired no-{spec.slug}−full mean ROC is "
            f"{fold_df[f'delta_roc_{p}_minus_full'].mean():+.3f}. That is a "
            f"descriptive difference and is not a reason to select the reduced model."
        )
    else:
        roc_text = (
            f"About {disappeared_roc:.0%} of the mean ROC increment vs ED-history "
            f"is associated with including {block_list} "
            f"({remain_roc:.0%} remains without them)."
        )
    prior_lines = "\n".join(
        f"- {label}: +{roc:.3f} ROC / +{pr:.3f} PR."
        for label, (roc, pr) in PRIOR_VS_ED.items()
    )
    abs_table = _fmt_stats_table(summary, [
        "ed_roc_auc", "ed_pr_auc", "ed_brier",
        "full_roc_auc", "full_pr_auc", "full_brier",
        f"{p}_roc_auc", f"{p}_pr_auc", f"{p}_brier",
    ])
    delta_table = _fmt_stats_table(summary, [
        "delta_roc_full_minus_ed", "delta_pr_full_minus_ed", "delta_brier_full_minus_ed",
        f"delta_roc_{p}_minus_ed", f"delta_pr_{p}_minus_ed", f"delta_brier_{p}_minus_ed",
        f"delta_roc_{p}_minus_full", f"delta_pr_{p}_minus_full", f"delta_brier_{p}_minus_full",
    ])
    md = f"""# {spec.title}

Documented Family B contrast {spec.experiment_id} (2026-09-12 plan).
Same analytic cohort, same 2022 any-ED outcome, same training portion
(n=3,831), same 5x5 RepeatedStratifiedKFold
(random_state={repeated_cv.CV_RANDOM_STATE}) as the locked repeated-CV
and B1–B3 block ablations. Preprocessing is fit inside each fold.
The original 25% holdout is scored only after CV, as a locked check.
It was not used to choose a model. Existing experiment files were not
overwritten.

Removed from Model C only: {block_list}.
Retained: {", ".join(spec.must_retain)}.

{CROSS_EXPERIMENT_NOTE}

The vs-ED-history contrasts below are descriptive continuity only. They
are not additional Family B hypotheses. Family B is the five
leave-one-block-out contrasts versus the full model.

The 2.5th and 97.5th percentiles below are descriptive summaries of the 25
paired fold deltas. They are not confidence intervals. The 25 folds are not treated as 25 independent observations. No p-value, no Nadeau-Bengio
correction, and no Holm-Bonferroni adjustment is computed in this file.

## CV absolute metrics (25 folds)

{abs_table}

## Paired fold-level deltas (25 folds)

{delta_table}

Brier n_pos counts folds where the delta is *negative* (lower Brier is better).

## Incremental value vs ED-history after removing the block
CV mean Δ ROC-AUC vs ED-history: full {full_ed_roc.mean():+.3f}; no-{spec.slug} {red_ed_roc.mean():+.3f}.
{roc_text}
CV mean Δ PR-AUC vs ED-history: full {full_ed_pr.mean():+.3f}; no-{spec.slug} {red_ed_pr.mean():+.3f}
({remain_pr:.0%} of the PR increment remains without the block).
ROC increment vs ED-history is positive in {int((red_ed_roc > 0).sum())}/{n} folds
(full: {int((full_ed_roc > 0).sum())}/{n}).
PR increment vs ED-history is positive in {int((red_ed_pr > 0).sum())}/{n} folds
(full: {int((full_ed_pr > 0).sum())}/{n}).
These counts describe paired folds. They are not a significance test.

## Brier
Mean Brier vs ED-history: full {full_ed_brier.mean():+.4f}; no-{spec.slug} {red_ed_brier.mean():+.4f}.
Brier improved vs ED-history in {int((red_ed_brier < 0).sum())}/{n} folds
(full: {int((full_ed_brier < 0).sum())}/{n}).
Mean no-{spec.slug}−full Brier {fold_df[f'delta_brier_{p}_minus_full'].mean():+.4f}.

## Family B contrast vs the full model (descriptive)
Mean no-{spec.slug}−full: ROC {fold_df[f'delta_roc_{p}_minus_full'].mean():+.3f},
PR {fold_df[f'delta_pr_{p}_minus_full'].mean():+.3f}.
Positive ROC delta vs full in {int((fold_df[f'delta_roc_{p}_minus_full'] > 0).sum())}/{n} folds;
positive PR delta vs full in {int((fold_df[f'delta_pr_{p}_minus_full'] > 0).sum())}/{n} folds.
No p-value is reported here.

## Comparison with prior full-model block ablations
{CROSS_EXPERIMENT_NOTE}

Remaining increment vs ED-history from earlier leave-block-out experiments:
{prior_lines}
- {spec.experiment_id} {spec.slug} ({block_list}): {red_ed_roc.mean():+.3f} ROC / {red_ed_pr.mean():+.3f} PR.

## Locked holdout (not used for selection)
- ED-history: ROC-AUC {ho.loc['ed_history', 'roc_auc']:.3f}, PR-AUC {ho.loc['ed_history', 'pr_auc']:.3f}, Brier {ho.loc['ed_history', 'brier_score']:.3f}
- Full model: ROC-AUC {ho.loc['full_model', 'roc_auc']:.3f}, PR-AUC {ho.loc['full_model', 'pr_auc']:.3f}, Brier {ho.loc['full_model', 'brier_score']:.3f}
- {spec.reduced_model_name}: ROC-AUC {ho.loc[spec.reduced_model_name, 'roc_auc']:.3f}, PR-AUC {ho.loc[spec.reduced_model_name, 'pr_auc']:.3f}, Brier {ho.loc[spec.reduced_model_name, 'brier_score']:.3f}
- Holdout Δ full−ED: ROC {ho.loc['delta_full_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc['delta_full_minus_ed', 'pr_auc']:+.3f}
- Holdout Δ no-{spec.slug}−ED: ROC {ho.loc[f'delta_{p}_minus_ed', 'roc_auc']:+.3f}, PR {ho.loc[f'delta_{p}_minus_ed', 'pr_auc']:+.3f}
- Holdout Δ no-{spec.slug}−full: ROC {ho.loc[f'delta_{p}_minus_full', 'roc_auc']:+.3f}, PR {ho.loc[f'delta_{p}_minus_full', 'pr_auc']:+.3f}

Treat the holdout as a first-run internal evaluation set, not as
evidence used to pick a model. It is not external, pristine, or
independently confirmatory validation.

Unweighted MEPS Panel 24 analytic-sample results only. Not clinical utility,
causality, national performance, or deployment readiness.
"""
    path.write_text(md, encoding="utf-8")


def run_experiment(spec: BlockSpec) -> dict:
    assert_column_sets(spec)
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = download.find_raw_file()
    if raw_file is None:
        raise FileNotFoundError("No HC-245 .dta file in data/raw/.")
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df)
    X = features.build_feature_matrix(usable, FULL_COLUMNS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)
    X_train, y_train, X_holdout, y_holdout = repeated_cv.training_portion(X, y)

    fold_df = run_paired_cv(X_train, y_train, spec)
    fold_df.to_csv(config.OUTPUTS_DIR / f"{spec.slug}_ablation_cv.csv", index=False)

    holdout = evaluate_locked_holdout(X_train, y_train, X_holdout, y_holdout, spec)
    holdout.to_csv(config.OUTPUTS_DIR / f"{spec.slug}_ablation_holdout.csv", index=False)

    write_figure(fold_df, spec, config.FIGURES_DIR / f"{spec.slug}_ablation.png")
    write_summary(
        config.OUTPUTS_DIR / f"{spec.slug}_ablation_summary.md",
        fold_df,
        holdout,
        spec,
    )
    print(f"{spec.experiment_id} {spec.slug}-ablation CV folds written: {len(fold_df)}")
    print("Locked holdout scored after CV; existing output files not modified.")
    return {"cv": fold_df, "holdout": holdout, "spec": spec}
