"""
Feature-family ablation and death-exclusion sensitivity.

Does not change the primary cohort, split, outcome, leakage rule, or
first-run output filenames. Writes:

  outputs/feature_family_ablation.csv
  outputs/death_sensitivity.csv
  outputs/ablation_summary.md
  outputs/figures/feature_family_ablation.png
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from . import config, download, features, ingest, longitudinal, modeling

DIED = "DIED"

ED_HISTORY = list(config.PREDICTOR_ED_VARS)

FAMILY_COLUMNS: dict[str, list[str]] = {
    "ed_history_only": list(ED_HISTORY),
    "ed_demographics": ED_HISTORY + ["AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X"],
    "ed_health": ED_HISTORY + ["RTHLTH6", "MNHLTH6"],
    "ed_access": ED_HISTORY + ["INSCOVY3", "HAVEUS6"],
    "ed_socioeconomic": ED_HISTORY + ["POVCATY3", "TTLPY3X", "EMPST6"],
    "full_model": [spec.name for spec in config.allowed_predictor_specs()],
}

FAMILY_ORDER = [
    "ed_history_only",
    "ed_demographics",
    "ed_health",
    "ed_access",
    "ed_socioeconomic",
    "full_model",
]


def family_column_map() -> dict[str, list[str]]:
    return {name: list(cols) for name, cols in FAMILY_COLUMNS.items()}


def assert_families_leakage_safe() -> None:
    for name, cols in FAMILY_COLUMNS.items():
        if config.OUTCOME_ED_VAR in cols:
            raise features.LeakageError(f"{name} includes the outcome variable.")
        features.assert_no_leakage(cols)
        extra = set(cols) - set(FAMILY_COLUMNS["full_model"])
        if extra:
            raise features.LeakageError(f"{name} uses predictors outside the production set: {extra}")


def decedent_mask(df: pd.DataFrame) -> pd.Series:
    """YEARIND==1 is already required of the analytic cohort; flag DIED==1."""
    if DIED not in df.columns:
        raise RuntimeError(
            f"{DIED} is required for the death-sensitivity analysis and is missing from the file."
        )
    died = pd.to_numeric(df[DIED], errors="coerce")
    return (died == 1).reindex(df.index, fill_value=False)


def _fit_family(X_train, y_train, X_test, y_test, cols: list[str], model_name: str):
    present = [c for c in cols if c in X_train.columns]
    if present != cols:
        missing = set(cols) - set(present)
        raise RuntimeError(f"{model_name} missing columns: {missing}")
    numeric, categorical = features.split_columns_by_treatment(cols)
    result, pipe, y_prob = modeling.full_logistic_model(
        X_train[cols], y_train, X_test[cols], y_test, numeric, categorical, model_name=model_name
    )
    return result, pipe, y_prob


def split_with_death_flag(X: pd.DataFrame, y: pd.Series, decedent: pd.Series):
    """Same split as modeling._split (seed, 25%, stratify=y) plus aligned DIED flag."""
    return train_test_split(
        X,
        y,
        decedent.reindex(X.index),
        test_size=0.25,
        random_state=config.RANDOM_SEED,
        stratify=y,
    )


def _original_best_ed_baseline_roc() -> float | None:
    path = config.OUTPUTS_DIR / "model_metrics.csv"
    if not path.exists():
        return None
    metrics = pd.read_csv(path)
    row = metrics.loc[metrics["model_name"] == "baseline_3_three_year_ed_history"]
    if row.empty:
        return None
    return float(row.iloc[0]["roc_auc"])


def ablation_table(results: list[modeling.EvalResult], ed_roc: float, ed_pr: float) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append({
            "model": result.model_name,
            "n_test": result.n_test,
            "prevalence": result.prevalence,
            "roc_auc": result.roc_auc,
            "pr_auc": result.pr_auc,
            "brier_score": result.brier_score,
            "delta_roc_vs_ed_history": None if result.roc_auc is None else result.roc_auc - ed_roc,
            "delta_pr_vs_ed_history": None if result.pr_auc is None else result.pr_auc - ed_pr,
        })
    return pd.DataFrame(rows)


def death_sensitivity_table(
    original_full: modeling.EvalResult,
    original_on_survivors: modeling.EvalResult,
    refit_on_survivors: modeling.EvalResult,
    n_decedents_train: int,
    n_decedents_test: int,
) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "comparison": "original_full_model_original_test",
            "n_test": original_full.n_test,
            "n_decedents_train_dropped": 0,
            "n_decedents_test_dropped": 0,
            "roc_auc": original_full.roc_auc,
            "pr_auc": original_full.pr_auc,
            "brier_score": original_full.brier_score,
            "delta_roc_vs_original_full": 0.0,
            "delta_pr_vs_original_full": 0.0,
            "delta_brier_vs_original_full": 0.0,
            "note": "Primary full model on the original holdout. Cohort unchanged.",
        },
        {
            "comparison": "original_full_model_survivor_test",
            "n_test": original_on_survivors.n_test,
            "n_decedents_train_dropped": 0,
            "n_decedents_test_dropped": n_decedents_test,
            "roc_auc": original_on_survivors.roc_auc,
            "pr_auc": original_on_survivors.pr_auc,
            "brier_score": original_on_survivors.brier_score,
            "delta_roc_vs_original_full": original_on_survivors.roc_auc - original_full.roc_auc,
            "delta_pr_vs_original_full": original_on_survivors.pr_auc - original_full.pr_auc,
            "delta_brier_vs_original_full": original_on_survivors.brier_score - original_full.brier_score,
            "note": "Same fitted original model, evaluated after dropping decedents from the test fold only.",
        },
        {
            "comparison": "full_model_refit_excluding_yearind1_decedents",
            "n_test": refit_on_survivors.n_test,
            "n_decedents_train_dropped": n_decedents_train,
            "n_decedents_test_dropped": n_decedents_test,
            "roc_auc": refit_on_survivors.roc_auc,
            "pr_auc": refit_on_survivors.pr_auc,
            "brier_score": refit_on_survivors.brier_score,
            "delta_roc_vs_original_full": refit_on_survivors.roc_auc - original_full.roc_auc,
            "delta_pr_vs_original_full": refit_on_survivors.pr_auc - original_full.pr_auc,
            "delta_brier_vs_original_full": refit_on_survivors.brier_score - original_full.brier_score,
            "note": "Sensitivity only. Primary YEARIND==1 cohort is not replaced.",
        },
    ])


def interpret_ablation(table: pd.DataFrame) -> dict:
    families = table[table["model"] != "full_model"].copy()
    families = families[families["model"] != "ed_history_only"]
    if families.empty:
        raise RuntimeError("Ablation table missing family rows.")
    top = families.loc[families["delta_roc_vs_ed_history"].idxmax()]
    full = table.set_index("model").loc["full_model"]
    positive = families[families["delta_roc_vs_ed_history"] > 0.01]
    return {
        "largest_family": top["model"],
        "largest_family_delta_roc": float(top["delta_roc_vs_ed_history"]),
        "largest_family_delta_pr": float(top["delta_pr_vs_ed_history"]),
        "full_delta_roc": float(full["delta_roc_vs_ed_history"]),
        "full_delta_pr": float(full["delta_pr_vs_ed_history"]),
        "n_families_with_roc_lift_gt_0_01": int(len(positive)),
        "distributed": len(positive) >= 2,
    }


def write_ablation_figure(table: pd.DataFrame, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    plot_df = table[table["model"] != "ed_history_only"].copy()
    labels = plot_df["model"].tolist()
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - width / 2, plot_df["delta_roc_vs_ed_history"], width, label="Δ ROC-AUC vs ED history")
    ax.bar(x + width / 2, plot_df["delta_pr_vs_ed_history"], width, label="Δ PR-AUC vs ED history")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Lift versus ED-history-only")
    ax.set_title("Feature-family ablation (same holdout, unweighted)")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def write_summary(
    path,
    interpretation: dict,
    ablation: pd.DataFrame,
    death: pd.DataFrame,
    n_decedents: int,
) -> None:
    refit = death.set_index("comparison").loc["full_model_refit_excluding_yearind1_decedents"]
    original = death.set_index("comparison").loc["original_full_model_original_test"]
    roc_change = abs(refit["delta_roc_vs_original_full"])
    material = roc_change >= 0.01 or abs(refit["delta_pr_vs_original_full"]) >= 0.01
    pattern = (
        "distributed across more than one family"
        if interpretation["distributed"]
        else "dominated by a single family"
    )
    death_line = (
        f"Excluding the {n_decedents} YEARIND==1 decedents "
        f"{'does' if material else 'does not'} materially change performance "
        f"(full-model ROC-AUC change {refit['delta_roc_vs_original_full']:+.3f}, "
        f"PR-AUC change {refit['delta_pr_vs_original_full']:+.3f} versus the original full-test metrics)."
    )
    supported = interpretation["full_delta_roc"] >= 0.02 and interpretation["full_delta_pr"] >= 0.01
    md = f"""# Feature-family ablation and death sensitivity

Same analytic cohort, same 25% stratified holdout (seed={config.RANDOM_SEED}),
same outcome, same leakage rule, and the same regularized logistic
architecture as the first real run. First-run output filenames were not
replaced.

## Largest incremental family
**{interpretation['largest_family']}**
ROC-AUC versus ED-history-only: {interpretation['largest_family_delta_roc']:+.3f}
PR-AUC versus ED-history-only: {interpretation['largest_family_delta_pr']:+.3f}

## Is the full-model lift concentrated or distributed?
The full-model lift versus ED-history-only is **{pattern}**.
Full model Δ ROC-AUC: {interpretation['full_delta_roc']:+.3f}
Full model Δ PR-AUC: {interpretation['full_delta_pr']:+.3f}
Families with ROC-AUC lift > 0.01 versus ED history: {interpretation['n_families_with_roc_lift_gt_0_01']}

## Death sensitivity
{death_line}

Original full model (original test): ROC-AUC={original['roc_auc']:.3f}, PR-AUC={original['pr_auc']:.3f}, Brier={original['brier_score']:.3f}
Refit excluding YEARIND==1 decedents: ROC-AUC={refit['roc_auc']:.3f}, PR-AUC={refit['pr_auc']:.3f}, Brier={refit['brier_score']:.3f}

This does not replace the primary YEARIND==1 cohort.

## Does the original research question remain supported?
{'Yes, on this holdout the pre-cutoff non-ED families still add ranking value beyond three-year ED history.' if supported else 'Not clearly, on this holdout the full-model lift over ED history no longer meets the original triage floors.'}

Unweighted analytic-sample metrics only. Not a national estimate, clinical
validation, or causal finding.
"""
    path.write_text(md, encoding="utf-8")


def run_experiment() -> dict:
    assert_families_leakage_safe()
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = download.main()
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df)
    decedent = decedent_mask(usable)

    audit = features.build_feature_audit(usable)
    usable_cols = features.usable_predictor_columns(audit)
    expected_full = FAMILY_COLUMNS["full_model"]
    if usable_cols != expected_full:
        # order-independent equality
        if set(usable_cols) != set(expected_full):
            raise RuntimeError(
                f"Production usable columns {usable_cols} do not match ablation full set {expected_full}."
            )
    X = features.build_feature_matrix(usable, expected_full)
    features.assert_no_leakage(list(X.columns))
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)

    X_train, X_test, y_train, y_test, died_train, died_test = split_with_death_flag(X, y, decedent)

    fitted = []
    full_prob = None
    for name in FAMILY_ORDER:
        result, pipe, y_prob = _fit_family(
            X_train, y_train, X_test, y_test, FAMILY_COLUMNS[name], name
        )
        fitted.append(result)
        if name == "full_model":
            full_prob = y_prob

    ed = next(r for r in fitted if r.model_name == "ed_history_only")
    ablation = ablation_table(fitted, ed.roc_auc, ed.pr_auc)
    original_best_ed = _original_best_ed_baseline_roc()
    if original_best_ed is not None:
        ablation["delta_roc_vs_original_best_ed_baseline"] = ablation["roc_auc"] - original_best_ed
    ablation.to_csv(config.OUTPUTS_DIR / "feature_family_ablation.csv", index=False)

    original_full = next(r for r in fitted if r.model_name == "full_model")
    survivor_train = ~np.asarray(died_train, dtype=bool)
    survivor_test = ~np.asarray(died_test, dtype=bool)
    n_dec_train = int((~survivor_train).sum())
    n_dec_test = int((~survivor_test).sum())

    original_on_survivors = modeling.evaluate_binary(
        "original_full_on_survivor_test",
        pd.Series(np.asarray(y_test)[survivor_test]),
        np.asarray(full_prob)[survivor_test],
    )
    refit, _pipe, _prob = _fit_family(
        X_train.iloc[np.where(survivor_train)[0]],
        y_train.iloc[np.where(survivor_train)[0]],
        X_test.iloc[np.where(survivor_test)[0]],
        y_test.iloc[np.where(survivor_test)[0]],
        FAMILY_COLUMNS["full_model"],
        "full_model_refit_excluding_yearind1_decedents",
    )

    death = death_sensitivity_table(
        original_full, original_on_survivors, refit, n_dec_train, n_dec_test
    )
    death.to_csv(config.OUTPUTS_DIR / "death_sensitivity.csv", index=False)

    interpretation = interpret_ablation(ablation)
    write_ablation_figure(ablation, config.FIGURES_DIR / "feature_family_ablation.png")
    write_summary(
        config.OUTPUTS_DIR / "ablation_summary.md",
        interpretation,
        ablation,
        death,
        n_decedents=int(decedent.sum()),
    )
    print("Ablation written to", config.OUTPUTS_DIR / "feature_family_ablation.csv")
    print("Death sensitivity written to", config.OUTPUTS_DIR / "death_sensitivity.csv")
    return {"ablation": ablation, "death": death, "interpretation": interpretation}


def main() -> int:
    run_experiment()
    return 0


if __name__ == "__main__":
    sys.exit(main())
