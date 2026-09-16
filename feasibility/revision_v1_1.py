"""
v1.1 reporting and sensitivity analyses.

Writes only new filenames. Does not overwrite locked v1.0 outputs and
does not change the primary cohort, outcome, predictors, seeds, or
estimator used for the original Family A / Family B results.

Run: python -m feasibility.revision_v1_1
Do not run python -m feasibility.run from this module.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import (
    ablation,
    config,
    download,
    features,
    ingest,
    inspect as inspect_stage,
    longitudinal,
    modeling,
    repeated_cv,
    statistical_inference as si,
)

BOOTSTRAP_SEED = 20210915
BOOTSTRAP_REPLICATES = 2000
ADULT_AGE_CUTOFF = 18.0
T_CRIT_24 = float(stats.t.ppf(0.975, 24))
V1_1_TAG = "v1.1"

ED_COLUMNS = list(ablation.FAMILY_COLUMNS["ed_history_only"])
FULL_COLUMNS = list(ablation.FAMILY_COLUMNS["full_model"])
NO_AGE_COLUMNS = [c for c in FULL_COLUMNS if c != "AGEY3X"]
COVID_ED_COLUMNS = ["ERTOTY1", "ERTOTY3"]
COVID_FULL_COLUMNS = [c for c in FULL_COLUMNS if c != "ERTOTY2"]

LOCKED_HOLDOUT = {
    "ed_roc": 0.709095145346402,
    "ed_pr": 0.33079411280933274,
    "ed_brier": 0.10528623721670442,
    "full_roc": 0.7740062410991038,
    "full_pr": 0.41593508223653725,
    "full_brier": 0.09938997744487747,
}


class RevisionV11Error(RuntimeError):
    """Raised when a v1.1 analysis cannot be completed without touching locked files."""


@dataclass(frozen=True)
class LoadedCohort:
    usable: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series
    X_train: pd.DataFrame
    y_train: pd.Series
    X_holdout: pd.DataFrame
    y_holdout: pd.Series


def _assert_new_path(path) -> None:
    name = path.name
    if "v1_1" not in name and "v1.1" not in name:
        raise RevisionV11Error(f"Refusing to write {path}; v1.1 outputs must use a v1_1 filename.")


def _write_csv(df: pd.DataFrame, path) -> None:
    _assert_new_path(path)
    df.to_csv(path, index=False)


def _write_text(text: str, path) -> None:
    _assert_new_path(path)
    path.write_text(text, encoding="utf-8")


def load_cohort_with_usable_split() -> tuple[LoadedCohort, pd.DataFrame, pd.DataFrame]:
    raw_file = download.find_raw_file()
    if raw_file is None:
        raise FileNotFoundError("No HC-245 .dta file in data/raw/.")
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df).reset_index(drop=True)
    features.assert_no_leakage(FULL_COLUMNS)
    X = features.build_feature_matrix(usable, FULL_COLUMNS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)
    X_train, X_holdout, y_train, y_holdout = modeling._split(X, y)
    u_train, u_holdout, _, _ = modeling._split(usable, y)
    if not X_train.index.equals(u_train.index) or not X_holdout.index.equals(u_holdout.index):
        raise RevisionV11Error("Usable-frame split does not align with the predictor-matrix split.")
    cohort = LoadedCohort(
        usable=usable,
        X=X.reset_index(drop=True),
        y=pd.Series(np.asarray(y), name="y"),
        X_train=X_train.reset_index(drop=True),
        y_train=pd.Series(np.asarray(y_train), name="y"),
        X_holdout=X_holdout.reset_index(drop=True),
        y_holdout=pd.Series(np.asarray(y_holdout), name="y"),
    )
    return cohort, u_train.reset_index(drop=True), u_holdout.reset_index(drop=True)


def nadeau_bengio_interval(mean: float, se: float, df: int = 24, alpha: float = 0.05) -> tuple[float, float]:
    tcrit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    return mean - tcrit * se, mean + tcrit * se


def write_nb_intervals() -> pd.DataFrame:
    src = config.OUTPUTS_DIR / "statistical_inference.csv"
    if not src.exists():
        raise RevisionV11Error(f"Missing locked inference table: {src}")
    table = pd.read_csv(src)
    lo, hi = [], []
    for _, row in table.iterrows():
        a, b = nadeau_bengio_interval(
            float(row["mean_difference"]),
            float(row["corrected_se"]),
            df=int(row["df"]),
        )
        lo.append(a)
        hi.append(b)
    out = table.copy()
    out["ci_method"] = "mean ± t_{1-alpha/2, df} × Nadeau–Bengio corrected SE"
    out["ci_alpha"] = 0.05
    out["ci_lower"] = lo
    out["ci_upper"] = hi
    out["sign_convention"] = (
        "Difference is first − second as named in `contrast`. "
        "For ROC/PR, positive favors the first-named model. "
        "For Brier, negative favors the first-named model (lower Brier is better)."
    )
    _write_csv(out, config.OUTPUTS_DIR / "statistical_inference_intervals_v1_1.csv")
    return out


def write_analytic_missingness(usable: pd.DataFrame) -> pd.DataFrame:
    cols = list(FULL_COLUMNS) + [config.OUTCOME_ED_VAR]
    table = inspect_stage.missingness_table(usable, cols)
    table.insert(0, "population", "analytic_cohort_YEARIND1_valid_ERTOTY1toY4")
    table.insert(1, "n_population", len(usable))
    _write_csv(table, config.OUTPUTS_DIR / "missingness_analytic_cohort_v1_1.csv")
    return table


def design_matrix_drop_reference(X: pd.DataFrame, columns: list[str] | None = None):
    """Preprocessor like the production pipeline, but OHE drops a reference level."""
    columns = list(columns or FULL_COLUMNS)
    numeric, categorical = features.split_columns_by_treatment(columns)
    transformers = []
    if numeric:
        transformers.append((
            "num",
            Pipeline([
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
            ]),
            numeric,
        ))
    if categorical:
        transformers.append((
            "cat",
            Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("ohe", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False)),
            ]),
            categorical,
        ))
    pre = ColumnTransformer(transformers)
    transformed = pre.fit_transform(X[columns])
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    names = list(pre.get_feature_names_out())
    return np.asarray(transformed, dtype=float), names, numeric, categorical


def variance_inflation_factors_drop_reference(X: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """
    VIF after dropping one reference dummy per categorical variable.

    Descriptive only. Not used to remove predictors. The production model
    still uses OneHotEncoder without drop (L2-regularized).
    """
    from .diagnostics import _source_variable

    columns = list(columns or FULL_COLUMNS)
    numeric, categorical = features.split_columns_by_treatment(columns)
    mat, names, _, _ = design_matrix_drop_reference(X, columns)
    vifs = []
    for j in range(mat.shape[1]):
        y = mat[:, j]
        others = np.delete(mat, j, axis=1)
        if not np.isfinite(y).all() or np.nanstd(y) == 0:
            vifs.append(float("inf"))
            continue
        model = LinearRegression()
        model.fit(others, y)
        r2 = float(model.score(others, y))
        if r2 >= 1.0 - 1e-12:
            vifs.append(float("inf"))
        else:
            vifs.append(float(1.0 / (1.0 - r2)))
    sources = [_source_variable(n, numeric, categorical) for n in names]
    return pd.DataFrame({
        "design_column": names,
        "source_variable": sources,
        "VIF": vifs,
        "encoding": "one_hot_drop_first",
        "role": "descriptive_only_not_used_for_predictor_removal",
    })


def write_vif_drop_reference(X_train: pd.DataFrame) -> pd.DataFrame:
    vif = variance_inflation_factors_drop_reference(X_train, FULL_COLUMNS)
    _write_csv(vif, config.OUTPUTS_DIR / "predictor_vif_drop_reference_v1_1.csv")
    n_inf = int(np.isinf(vif["VIF"]).sum())
    n_gt10 = int((vif["VIF"] > 10).sum())
    n_gt5 = int((vif["VIF"] > 5).sum())
    finite = vif["VIF"].to_numpy(dtype=float)
    finite = finite[np.isfinite(finite)]
    max_vif = float(np.max(finite)) if finite.size else float("nan")
    notes = f"""# Corrected VIF diagnostic (v1.1)

The locked file `outputs/predictor_vif.csv` applies VIF to the production
design matrix, which one-hot encodes categoricals **without** dropping a
reference level. Auxiliary regressions of each dummy on the remaining
columns (including the other levels of the same factor, plus an
intercept in `LinearRegression`) are then linearly dependent. That is
the dummy-variable trap. Almost all categorical columns therefore have
infinite VIF. Those infinities are an encoding artifact, not evidence
that the corresponding predictors must be removed, and they were never
used to change the model.

This v1.1 table repeats VIF after `OneHotEncoder(drop="first")` on the
same 3,831-person training portion. The dropped level is sklearn's
default first category after imputation, not a scientifically chosen
reference; any single dropped level removes the trap. Auxiliary VIF
regressions include an intercept. The diagnostic is **descriptive
only**. VIF was never a prespecified removal rule, and no predictor is
dropped because of these values. The production model remains
L2-regularized logistic regression on the original (no drop) encoding.

- Design columns: {len(vif)}
- Max VIF: {max_vif:.3f}
- VIF > 5: {n_gt5}
- VIF > 10: {n_gt10}
- Infinite VIF after drop-first: {n_inf}

All corrected VIFs below 5 means this diagnostic did not flag strong
linear collinearity on the reference-dropped training design matrix.
That is not proof of independence (pairwise η associations remain),
and it is not a reason to add or remove predictors.
"""
    _write_text(notes, config.OUTPUTS_DIR / "predictor_vif_v1_1_notes.md")
    return vif


def fit_probabilities(X_train, y_train, X_eval, cols: list[str]) -> np.ndarray:
    features.assert_no_leakage(cols)
    numeric, categorical = features.split_columns_by_treatment(cols)
    _result, _pipe, y_prob = modeling.full_logistic_model(
        X_train[cols], y_train, X_eval[cols], pd.Series(np.zeros(len(X_eval)), index=X_eval.index),
        numeric, categorical, model_name="tmp",
    )
    return np.asarray(y_prob, dtype=float)


def logit(p: np.ndarray) -> np.ndarray:
    clipped = np.clip(p, 1e-12, 1.0 - 1e-12)
    return np.log(clipped / (1.0 - clipped))


def calibration_in_the_large(y: np.ndarray, lp: np.ndarray, max_iter: int = 100) -> float:
    """Intercept with slope fixed at 1: logit(P(Y=1)) = a + logit(p)."""
    a = 0.0
    y = np.asarray(y, dtype=float)
    lp = np.asarray(lp, dtype=float)
    for _ in range(max_iter):
        eta = np.clip(a + lp, -50.0, 50.0)
        p_hat = 1.0 / (1.0 + np.exp(-eta))
        weight = p_hat * (1.0 - p_hat)
        score = float(np.sum(y - p_hat))
        hess = float(np.sum(weight))
        if hess <= 0:
            break
        da = score / hess
        a += da
        if abs(da) < 1e-12:
            break
    return float(a)


def calibration_intercept_slope(y: np.ndarray, p: np.ndarray) -> dict:
    """
    Cox logistic calibration assessment (not recalibration).

    Joint model: logit(P(Y=1)) = a + b * logit(p), unpenalized.
    Also reports calibration-in-the-large (a with b fixed at 1).
    Predicted probabilities are not replaced.
    """
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    lp = logit(p)
    x = lp.reshape(-1, 1)
    # C=np.inf is sklearn's unpenalized logistic (penalty=None is deprecated).
    clf = LogisticRegression(
        C=np.inf,
        solver="lbfgs",
        max_iter=2000,
        random_state=config.RANDOM_SEED,
    )
    clf.fit(x, y)
    return {
        "n": int(len(y)),
        "events": int(y.sum()),
        "mean_predicted": float(np.mean(p)),
        "observed_prevalence": float(np.mean(y)),
        "calibration_in_the_large": calibration_in_the_large(y, lp),
        "calibration_intercept": float(clf.intercept_[0]),
        "calibration_slope": float(clf.coef_[0, 0]),
        "method": (
            "Cox logistic calibration on first-run holdout: unpenalized "
            "logit(Y) = a + b logit(p). CITL is a with b fixed at 1. "
            "Assessment only; probabilities are not recalibrated."
        ),
    }


def binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y)
    p = np.asarray(p)
    if len(np.unique(y)) < 2:
        return {"roc_auc": np.nan, "pr_auc": np.nan, "brier": float(brier_score_loss(y, p))}
    return {
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
    }


def bootstrap_holdout_metrics(
    y: np.ndarray,
    p_ed: np.ndarray,
    p_full: np.ndarray,
    n_boot: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    n = len(y)
    rows = []
    n_degenerate = 0
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yb = y[idx]
        if yb.min() == yb.max():
            n_degenerate += 1
            continue
        ed = binary_metrics(yb, p_ed[idx])
        full = binary_metrics(yb, p_full[idx])
        rows.append({
            "replicate": b,
            "ed_roc_auc": ed["roc_auc"],
            "full_roc_auc": full["roc_auc"],
            "delta_roc_auc": full["roc_auc"] - ed["roc_auc"],
            "ed_pr_auc": ed["pr_auc"],
            "full_pr_auc": full["pr_auc"],
            "delta_pr_auc": full["pr_auc"] - ed["pr_auc"],
            "ed_brier": ed["brier"],
            "full_brier": full["brier"],
            "delta_brier": full["brier"] - ed["brier"],
        })
    boot = pd.DataFrame(rows)
    records = []
    for metric in [
        "ed_roc_auc", "full_roc_auc", "delta_roc_auc",
        "ed_pr_auc", "full_pr_auc", "delta_pr_auc",
        "ed_brier", "full_brier", "delta_brier",
    ]:
        s = boot[metric].to_numpy(dtype=float)
        records.append({
            "metric": metric,
            "point_estimate_source": "locked_holdout_refit_verified",
            "n_holdout": n,
            "n_bootstrap_requested": n_boot,
            "n_bootstrap_valid": int(len(boot)),
            "n_degenerate_skipped": n_degenerate,
            "bootstrap_seed": seed,
            "resampling_unit": "person-level (y, p_ed, p_full) pairs with replacement",
            "ci_method": "percentile",
            "ci_lower": float(np.percentile(s, 2.5)),
            "ci_upper": float(np.percentile(s, 97.5)),
            "bootstrap_mean": float(np.mean(s)),
            "bootstrap_median": float(np.median(s)),
            "sign_convention": (
                "delta_* = full − ED-history; ROC/PR positive favors full; "
                "Brier negative favors full (lower Brier is better)"
            ),
        })
    summary = pd.DataFrame(records)
    return boot, summary


def write_holdout_uncertainty(cohort: LoadedCohort) -> dict:
    p_ed = fit_probabilities(cohort.X_train, cohort.y_train, cohort.X_holdout, ED_COLUMNS)
    p_full = fit_probabilities(cohort.X_train, cohort.y_train, cohort.X_holdout, FULL_COLUMNS)
    y = cohort.y_holdout.to_numpy(dtype=int)
    ed = binary_metrics(y, p_ed)
    full = binary_metrics(y, p_full)
    for key, locked, got in [
        ("ed_roc", LOCKED_HOLDOUT["ed_roc"], ed["roc_auc"]),
        ("ed_pr", LOCKED_HOLDOUT["ed_pr"], ed["pr_auc"]),
        ("ed_brier", LOCKED_HOLDOUT["ed_brier"], ed["brier"]),
        ("full_roc", LOCKED_HOLDOUT["full_roc"], full["roc_auc"]),
        ("full_pr", LOCKED_HOLDOUT["full_pr"], full["pr_auc"]),
        ("full_brier", LOCKED_HOLDOUT["full_brier"], full["brier"]),
    ]:
        if abs(locked - got) > 1e-12:
            raise RevisionV11Error(
                f"Holdout refit mismatch for {key}: locked={locked}, refit={got}"
            )

    boot, summary = bootstrap_holdout_metrics(y, p_ed, p_full)
    point_map = {
        "ed_roc_auc": ed["roc_auc"],
        "full_roc_auc": full["roc_auc"],
        "delta_roc_auc": full["roc_auc"] - ed["roc_auc"],
        "ed_pr_auc": ed["pr_auc"],
        "full_pr_auc": full["pr_auc"],
        "delta_pr_auc": full["pr_auc"] - ed["pr_auc"],
        "ed_brier": ed["brier"],
        "full_brier": full["brier"],
        "delta_brier": full["brier"] - ed["brier"],
    }
    summary.insert(1, "point_estimate", summary["metric"].map(point_map))
    _write_csv(summary, config.OUTPUTS_DIR / "holdout_bootstrap_v1_1.csv")

    cal_rows = []
    for name, p in [("ed_history", p_ed), ("full_model", p_full)]:
        row = calibration_intercept_slope(y, p)
        row["model"] = name
        row["dataset"] = "first_run_holdout_internal_evaluation"
        row["exploratory"] = True
        cal_rows.append(row)
    cal = pd.DataFrame(cal_rows)
    _write_csv(cal, config.OUTPUTS_DIR / "holdout_calibration_v1_1.csv")

    def _row(metric: str) -> pd.Series:
        return summary.set_index("metric").loc[metric]

    md = f"""# Holdout bootstrap and calibration (v1.1)

The 25% split (seed 42, n = {len(y)}, events = {int(y.sum())}) is a
**first-run / development-stage internal evaluation set**. It was scored
during the original pipeline and used by the research-triage gate. It is
not an external, pristine, or independently confirmatory sample.

Primary inferential evidence remains the training-only 5×5
Nadeau–Bengio comparison. These intervals describe uncertainty in the
holdout *point* metrics only.

## Bootstrap

- Resampling unit: person-level `(y, p_ed, p_full)` pairs
- Replicates requested: {BOOTSTRAP_REPLICATES}
- Valid replicates: {int(summary['n_bootstrap_valid'].iloc[0])}
- Degenerate (single-class) replicates skipped: {int(summary['n_degenerate_skipped'].iloc[0])}
- Seed: {BOOTSTRAP_SEED}
- Interval: percentile 2.5th–97.5th

Sign convention: Δ = Full − ED-history. Positive ΔROC/ΔPR favors Full.
Negative ΔBrier favors Full because **lower Brier is better**.

| metric | point | 95% percentile CI |
|---|---:|---|
| ED-history ROC-AUC | {_row('ed_roc_auc')['point_estimate']:.4f} | {_row('ed_roc_auc')['ci_lower']:.4f} to {_row('ed_roc_auc')['ci_upper']:.4f} |
| Full ROC-AUC | {_row('full_roc_auc')['point_estimate']:.4f} | {_row('full_roc_auc')['ci_lower']:.4f} to {_row('full_roc_auc')['ci_upper']:.4f} |
| Δ ROC-AUC | {_row('delta_roc_auc')['point_estimate']:+.4f} | {_row('delta_roc_auc')['ci_lower']:+.4f} to {_row('delta_roc_auc')['ci_upper']:+.4f} |
| ED-history PR-AUC | {_row('ed_pr_auc')['point_estimate']:.4f} | {_row('ed_pr_auc')['ci_lower']:.4f} to {_row('ed_pr_auc')['ci_upper']:.4f} |
| Full PR-AUC | {_row('full_pr_auc')['point_estimate']:.4f} | {_row('full_pr_auc')['ci_lower']:.4f} to {_row('full_pr_auc')['ci_upper']:.4f} |
| Δ PR-AUC | {_row('delta_pr_auc')['point_estimate']:+.4f} | {_row('delta_pr_auc')['ci_lower']:+.4f} to {_row('delta_pr_auc')['ci_upper']:+.4f} |
| ED-history Brier | {_row('ed_brier')['point_estimate']:.4f} | {_row('ed_brier')['ci_lower']:.4f} to {_row('ed_brier')['ci_upper']:.4f} |
| Full Brier | {_row('full_brier')['point_estimate']:.4f} | {_row('full_brier')['ci_lower']:.4f} to {_row('full_brier')['ci_upper']:.4f} |
| Δ Brier | {_row('delta_brier')['point_estimate']:+.4f} | {_row('delta_brier')['ci_lower']:+.4f} to {_row('delta_brier')['ci_upper']:+.4f} |

Refit of the locked pipelines on the reconstructed training portion
matched `outputs/model_metrics.csv` to 1e-12 before bootstrapping.
The bootstrap was not rerun to obtain a preferred interval.

## Calibration intercept and slope

Cox logistic calibration on the **entire** first-run holdout
(n = {len(y)}, events = {int(y.sum())}, binary `y` in {{0,1}}, `p` =
predicted probability, `logit(p)` = log(p/(1-p))). Joint unpenalized
model: logit(P(Y=1)) = a + b logit(p). Calibration-in-the-large (CITL)
is a with b fixed at 1. This is **assessment only**: predicted
probabilities are not replaced, and the production model is not
recalibrated. The split is internal, not external validation.

| model | mean predicted | observed prevalence | CITL (b=1) | intercept a | slope b |
|---|---:|---:|---:|---:|---:|
| ED-history | {cal.loc[cal['model']=='ed_history','mean_predicted'].iloc[0]:.4f} | {cal.loc[cal['model']=='ed_history','observed_prevalence'].iloc[0]:.4f} | {cal.loc[cal['model']=='ed_history','calibration_in_the_large'].iloc[0]:.4f} | {cal.loc[cal['model']=='ed_history','calibration_intercept'].iloc[0]:.4f} | {cal.loc[cal['model']=='ed_history','calibration_slope'].iloc[0]:.4f} |
| Full | {cal.loc[cal['model']=='full_model','mean_predicted'].iloc[0]:.4f} | {cal.loc[cal['model']=='full_model','observed_prevalence'].iloc[0]:.4f} | {cal.loc[cal['model']=='full_model','calibration_in_the_large'].iloc[0]:.4f} | {cal.loc[cal['model']=='full_model','calibration_intercept'].iloc[0]:.4f} | {cal.loc[cal['model']=='full_model','calibration_slope'].iloc[0]:.4f} |

Interpretation for the full model on this split:

- Overall rate: mean predicted probability is essentially the observed
  prevalence, and CITL is near 0. That is **not** evidence of a large
  systematic over- or under-prediction of event frequency.
- Joint intercept a is the log-odds adjustment at predicted p = 0.5
  when slope is also estimated. It should not be read as overall
  miscalibration of prevalence.
- Slope b > 1 means predicted logits are somewhat too small in
  magnitude (risks a bit too close to the mean). That pattern is
  compatible with L2 shrinkage. It is mild, not a claim of severe
  miscalibration.
- These quantities are from the first-run internal holdout.

The locked quantile-binned reliability table (`outputs/calibration.csv`)
is unchanged.
"""
    _write_text(md, config.OUTPUTS_DIR / "holdout_bootstrap_v1_1_summary.md")
    return {"summary": summary, "calibration": cal, "ed": ed, "full": full}


def paired_cv(X_train: pd.DataFrame, y_train: pd.Series, ed_cols: list[str], full_cols: list[str]) -> pd.DataFrame:
    features.assert_no_leakage(ed_cols)
    features.assert_no_leakage(full_cols)
    X_train = X_train.reset_index(drop=True)
    y_train = pd.Series(np.asarray(y_train), name="y")
    rows = []
    splitter = repeated_cv.cv_splitter()
    for i, (tr_idx, va_idx) in enumerate(splitter.split(X_train, y_train)):
        repeat = i // repeated_cv.CV_N_SPLITS
        fold = i % repeated_cv.CV_N_SPLITS
        X_tr, X_va = X_train.iloc[tr_idx], X_train.iloc[va_idx]
        y_tr, y_va = y_train.iloc[tr_idx], y_train.iloc[va_idx]
        ed = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, ed_cols, "ed_history")
        full = repeated_cv.fit_on_fold(X_tr, y_tr, X_va, y_va, full_cols, "full_model")
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
            "cv_random_state": repeated_cv.CV_RANDOM_STATE,
            "n_splits": repeated_cv.CV_N_SPLITS,
            "n_repeats": repeated_cv.CV_N_REPEATS,
        })
    return pd.DataFrame(rows)


def holdout_pair(X_train, y_train, X_ho, y_ho, ed_cols, full_cols) -> dict:
    p_ed = fit_probabilities(X_train, y_train, X_ho, ed_cols)
    p_full = fit_probabilities(X_train, y_train, X_ho, full_cols)
    y = np.asarray(y_ho, dtype=int)
    ed = binary_metrics(y, p_ed)
    full = binary_metrics(y, p_full)
    return {
        "n_train": int(len(y_train)),
        "n_holdout": int(len(y)),
        "holdout_events": int(y.sum()),
        "holdout_prevalence": float(np.mean(y)),
        "ed_roc_auc": ed["roc_auc"],
        "ed_pr_auc": ed["pr_auc"],
        "ed_brier": ed["brier"],
        "full_roc_auc": full["roc_auc"],
        "full_pr_auc": full["pr_auc"],
        "full_brier": full["brier"],
        "delta_roc_auc": full["roc_auc"] - ed["roc_auc"],
        "delta_pr_auc": full["pr_auc"] - ed["pr_auc"],
        "delta_brier": full["brier"] - ed["brier"],
    }


def summarize_sensitivity(name: str, reason: str, folds: pd.DataFrame, holdout: dict) -> pd.DataFrame:
    ratio = float((folds["n_cv_val"] / folds["n_cv_train"]).mean())
    rows = []
    for metric, col in [
        ("roc_auc", "delta_roc_auc"),
        ("pr_auc", "delta_pr_auc"),
        ("brier", "delta_brier"),
    ]:
        nb = si.nadeau_bengio_ttest(folds[col].to_numpy(dtype=float), ratio)
        lo, hi = nadeau_bengio_interval(nb.mean, nb.corrected_se, df=nb.df)
        rows.append({
            "sensitivity": name,
            "reason": reason,
            "metric": metric,
            "n_train": holdout["n_train"],
            "n_holdout": holdout["n_holdout"],
            "holdout_events": holdout["holdout_events"],
            "cv_mean_difference": nb.mean,
            "cv_corrected_se": nb.corrected_se,
            "cv_t_statistic": nb.t_statistic,
            "cv_df": nb.df,
            "cv_raw_p_value": nb.p_value,
            "cv_ci_lower": lo,
            "cv_ci_upper": hi,
            "holdout_ed": holdout[f"ed_{'roc_auc' if metric=='roc_auc' else 'pr_auc' if metric=='pr_auc' else 'brier'}"],
            "holdout_full": holdout[f"full_{'roc_auc' if metric=='roc_auc' else 'pr_auc' if metric=='pr_auc' else 'brier'}"],
            "holdout_delta": holdout[f"delta_{'roc_auc' if metric=='roc_auc' else 'pr_auc' if metric=='pr_auc' else 'brier'}"],
            "primary_replacement": False,
            "sign_convention": "Δ = Full − ED-history; lower Brier is better",
        })
    return pd.DataFrame(rows)


def run_population_sensitivity(
    name: str,
    reason: str,
    X_train, y_train, X_ho, y_ho,
    train_mask: pd.Series,
    ho_mask: pd.Series,
    ed_cols: list[str],
    full_cols: list[str],
) -> dict:
    Xtr = X_train.loc[train_mask].reset_index(drop=True)
    ytr = y_train.loc[train_mask].reset_index(drop=True)
    Xho = X_ho.loc[ho_mask].reset_index(drop=True)
    yho = y_ho.loc[ho_mask].reset_index(drop=True)
    folds = paired_cv(Xtr, ytr, ed_cols, full_cols)
    holdout = holdout_pair(Xtr, ytr, Xho, yho, ed_cols, full_cols)
    summary = summarize_sensitivity(name, reason, folds, holdout)
    return {"folds": folds, "holdout": holdout, "summary": summary}


def write_sensitivity_bundle(prefix: str, title: str, body: str, result: dict) -> None:
    _write_csv(result["folds"], config.OUTPUTS_DIR / f"{prefix}_cv.csv")
    _write_csv(pd.DataFrame([result["holdout"]]), config.OUTPUTS_DIR / f"{prefix}_holdout.csv")
    _write_csv(result["summary"], config.OUTPUTS_DIR / f"{prefix}_inference.csv")
    inf = result["summary"].set_index("metric")
    ho = result["holdout"]
    md = f"""# {title}

Sensitivity analysis only. **Does not replace** the primary YEARIND==1
Family A comparison.

{body}

## Sample

- Training subset n = {ho['n_train']}
- Holdout subset n = {ho['n_holdout']} (events {ho['holdout_events']}, prevalence {ho['holdout_prevalence']:.4f})
- Original seed-42 split membership is preserved; the subset is not re-randomized.

## Training-only 5×5 Nadeau–Bengio (Full − ED-history)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | {inf.loc['roc_auc','cv_mean_difference']:+.4f} | {inf.loc['roc_auc','cv_corrected_se']:.4f} | {inf.loc['roc_auc','cv_t_statistic']:+.3f} | {inf.loc['roc_auc','cv_raw_p_value']:.4f} | {inf.loc['roc_auc','cv_ci_lower']:+.4f} to {inf.loc['roc_auc','cv_ci_upper']:+.4f} |
| PR-AUC | {inf.loc['pr_auc','cv_mean_difference']:+.4f} | {inf.loc['pr_auc','cv_corrected_se']:.4f} | {inf.loc['pr_auc','cv_t_statistic']:+.3f} | {inf.loc['pr_auc','cv_raw_p_value']:.4f} | {inf.loc['pr_auc','cv_ci_lower']:+.4f} to {inf.loc['pr_auc','cv_ci_upper']:+.4f} |
| Brier | {inf.loc['brier','cv_mean_difference']:+.4f} | {inf.loc['brier','cv_corrected_se']:.4f} | {inf.loc['brier','cv_t_statistic']:+.3f} | {inf.loc['brier','cv_raw_p_value']:.4f} | {inf.loc['brier','cv_ci_lower']:+.4f} to {inf.loc['brier','cv_ci_upper']:+.4f} |

Sign convention: Δ = Full − ED-history. Lower Brier is better, so a
negative ΔBrier favors the full model.

## First-run holdout subset (descriptive)

| metric | ED-history | Full | Δ |
|---|---:|---:|---:|
| ROC-AUC | {ho['ed_roc_auc']:.4f} | {ho['full_roc_auc']:.4f} | {ho['delta_roc_auc']:+.4f} |
| PR-AUC | {ho['ed_pr_auc']:.4f} | {ho['full_pr_auc']:.4f} | {ho['delta_pr_auc']:+.4f} |
| Brier | {ho['ed_brier']:.4f} | {ho['full_brier']:.4f} | {ho['delta_brier']:+.4f} |

Holdout subset metrics are internal evaluation, not a new primary.
"""
    _write_text(md, config.OUTPUTS_DIR / f"{prefix}_summary.md")


def run_exploratory_adult_age_ablation(
    X_train, y_train, X_ho, y_ho, train_mask: pd.Series, ho_mask: pd.Series,
) -> dict:
    """
    Exploratory/post-primary: Family B age block (drop AGEY3X only)
    inside the adult-only subset of the original seed-42 split.

    Uses the existing B1 column definition and the same 5×5 CV seed.
    Does not replace the mixed-age primary analysis or the adult-only
    Full-vs-ED sensitivity.
    """
    from . import age_ablation

    age_ablation.assert_column_sets()
    if set(NO_AGE_COLUMNS) != set(age_ablation.NO_AGE_COLUMNS):
        raise RevisionV11Error("Adult age ablation must use the documented B1 AGEY3X-only block.")
    Xtr = X_train.loc[train_mask].reset_index(drop=True)
    ytr = y_train.loc[train_mask].reset_index(drop=True)
    Xho = X_ho.loc[ho_mask].reset_index(drop=True)
    yho = y_ho.loc[ho_mask].reset_index(drop=True)
    folds = age_ablation.run_paired_cv(Xtr, ytr)
    ratio = float((folds["n_cv_val"] / folds["n_cv_train"]).mean())
    rows = []
    for metric, col in [
        ("roc_auc", "delta_roc_noage_minus_full"),
        ("pr_auc", "delta_pr_noage_minus_full"),
        ("brier", "delta_brier_noage_minus_full"),
    ]:
        nb = si.nadeau_bengio_ttest(folds[col].to_numpy(dtype=float), ratio)
        lo, hi = nadeau_bengio_interval(nb.mean, nb.corrected_se, df=nb.df)
        rows.append({
            "analysis": "exploratory_adult_age_ablation",
            "classification": "exploratory_post_primary",
            "prespecified": False,
            "contrast": "No-age − Full (AGEY3X removed; adult subset)",
            "metric": metric,
            "n_train": int(len(ytr)),
            "n_holdout": int(len(yho)),
            "cv_mean_difference": nb.mean,
            "cv_corrected_se": nb.corrected_se,
            "cv_t_statistic": nb.t_statistic,
            "cv_df": nb.df,
            "cv_raw_p_value": nb.p_value,
            "cv_ci_lower": lo,
            "cv_ci_upper": hi,
            "sign_convention": (
                "Δ = No-age − Full. For ROC/PR, negative means Full is better "
                "(age contributes). For Brier, positive means Full is better."
            ),
            "primary_replacement": False,
        })
    inference = pd.DataFrame(rows)
    p_full = fit_probabilities(Xtr, ytr, Xho, FULL_COLUMNS)
    p_noage = fit_probabilities(Xtr, ytr, Xho, NO_AGE_COLUMNS)
    y = np.asarray(yho, dtype=int)
    full = binary_metrics(y, p_full)
    noage = binary_metrics(y, p_noage)
    holdout = {
        "n_train": int(len(ytr)),
        "n_holdout": int(len(y)),
        "holdout_events": int(y.sum()),
        "holdout_prevalence": float(np.mean(y)),
        "full_roc_auc": full["roc_auc"],
        "full_pr_auc": full["pr_auc"],
        "full_brier": full["brier"],
        "noage_roc_auc": noage["roc_auc"],
        "noage_pr_auc": noage["pr_auc"],
        "noage_brier": noage["brier"],
        "delta_roc_noage_minus_full": noage["roc_auc"] - full["roc_auc"],
        "delta_pr_noage_minus_full": noage["pr_auc"] - full["pr_auc"],
        "delta_brier_noage_minus_full": noage["brier"] - full["brier"],
    }
    _write_csv(folds, config.OUTPUTS_DIR / "exploratory_adult_age_ablation_v1_1_cv.csv")
    _write_csv(pd.DataFrame([holdout]), config.OUTPUTS_DIR / "exploratory_adult_age_ablation_v1_1_holdout.csv")
    _write_csv(inference, config.OUTPUTS_DIR / "exploratory_adult_age_ablation_v1_1_inference.csv")
    inf = inference.set_index("metric")
    md = f"""# Exploratory adult-only age ablation (v1.1)

**Classification:** exploratory / post-primary. Not prespecified. Does
**not** replace the mixed-age Family A primary comparison and does
**not** replace the adult-only Full-versus-ED-history sensitivity.

Purpose: within the already-defined adult subset of the original seed-42
split, apply the documented B1 contrast (remove `AGEY3X` only from the
full model) using the same 5×5 CV seed (2021). The question is whether
age appears to contribute disproportionately among adults. This is not
a search over alternative age specifications.

## Sample

- Adult training n = {holdout['n_train']}
- Adult holdout n = {holdout['n_holdout']} (events {holdout['holdout_events']})

## Training-only 5×5 Nadeau–Bengio (No-age − Full)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | {inf.loc['roc_auc','cv_mean_difference']:+.4f} | {inf.loc['roc_auc','cv_corrected_se']:.4f} | {inf.loc['roc_auc','cv_t_statistic']:+.3f} | {inf.loc['roc_auc','cv_raw_p_value']:.4f} | {inf.loc['roc_auc','cv_ci_lower']:+.4f} to {inf.loc['roc_auc','cv_ci_upper']:+.4f} |
| PR-AUC | {inf.loc['pr_auc','cv_mean_difference']:+.4f} | {inf.loc['pr_auc','cv_corrected_se']:.4f} | {inf.loc['pr_auc','cv_t_statistic']:+.3f} | {inf.loc['pr_auc','cv_raw_p_value']:.4f} | {inf.loc['pr_auc','cv_ci_lower']:+.4f} to {inf.loc['pr_auc','cv_ci_upper']:+.4f} |
| Brier | {inf.loc['brier','cv_mean_difference']:+.4f} | {inf.loc['brier','cv_corrected_se']:.4f} | {inf.loc['brier','cv_t_statistic']:+.3f} | {inf.loc['brier','cv_raw_p_value']:.4f} | {inf.loc['brier','cv_ci_lower']:+.4f} to {inf.loc['brier','cv_ci_upper']:+.4f} |

Sign convention matches Family B: Δ = No-age − Full. Negative ΔROC/ΔPR
means the full model (with age) had higher discrimination.

## Adult holdout subset (descriptive)

| metric | Full | No-age | No-age − Full |
|---|---:|---:|---:|
| ROC-AUC | {holdout['full_roc_auc']:.4f} | {holdout['noage_roc_auc']:.4f} | {holdout['delta_roc_noage_minus_full']:+.4f} |
| PR-AUC | {holdout['full_pr_auc']:.4f} | {holdout['noage_pr_auc']:.4f} | {holdout['delta_pr_noage_minus_full']:+.4f} |
| Brier | {holdout['full_brier']:.4f} | {holdout['noage_brier']:.4f} | {holdout['delta_brier_noage_minus_full']:+.4f} |

This diagnostic is not used to explain away the adult-only Full-versus-ED
ROC result, and it is not promoted to a primary analysis.
"""
    _write_text(md, config.OUTPUTS_DIR / "exploratory_adult_age_ablation_v1_1_summary.md")
    return {"folds": folds, "holdout": holdout, "summary": inference}


def run_sensitivities(cohort: LoadedCohort, u_train: pd.DataFrame, u_holdout: pd.DataFrame) -> dict:
    Xtr, ytr = cohort.X_train, cohort.y_train
    Xho, yho = cohort.X_holdout, cohort.y_holdout

    adult_tr = Xtr["AGEY3X"].notna() & (Xtr["AGEY3X"] >= ADULT_AGE_CUTOFF)
    adult_ho = Xho["AGEY3X"].notna() & (Xho["AGEY3X"] >= ADULT_AGE_CUTOFF)
    n_child = int((~(Xtr["AGEY3X"] >= ADULT_AGE_CUTOFF)).sum() + (~(Xho["AGEY3X"] >= ADULT_AGE_CUTOFF)).sum())
    adult = run_population_sensitivity(
        "adult_only",
        "Population-definition: employment and some access/health items are often inapplicable for children.",
        Xtr, ytr, Xho, yho, adult_tr, adult_ho, ED_COLUMNS, FULL_COLUMNS,
    )
    write_sensitivity_bundle(
        "sensitivity_adult_only_v1_1",
        "Adult-only sensitivity (AGEY3X ≥ 18)",
        f"Restricts the original seed-42 split to persons aged ≥ {int(ADULT_AGE_CUTOFF)} "
        f"at the 2021 cutoff. Persons under 18 in the analytic cohort: {n_child}. "
        "This addresses a population-definition concern, not a performance-chasing exercise.",
        adult,
    )

    all9_tr = pd.to_numeric(u_train[config.ALL9RDS], errors="coerce") == 1
    all9_ho = pd.to_numeric(u_holdout[config.ALL9RDS], errors="coerce") == 1
    all9 = run_population_sensitivity(
        "all9rds",
        "Complete nine-round interview participation (AHRQ ALL9RDS==1) as a selection check.",
        Xtr, ytr, Xho, yho, all9_tr, all9_ho, ED_COLUMNS, FULL_COLUMNS,
    )
    write_sensitivity_bundle(
        "sensitivity_all9rds_v1_1",
        "ALL9RDS==1 sensitivity",
        "Primary inclusion remains YEARIND==1. ALL9RDS==1 is AHRQ’s complete "
        "nine-round subset used with LONGWT for national longitudinal estimates. "
        "This sensitivity asks whether requiring complete-round participation "
        "changes the incremental-value conclusion. It is not adopted as primary.",
        all9,
    )

    covid_folds = paired_cv(Xtr, ytr, COVID_ED_COLUMNS, COVID_FULL_COLUMNS)
    covid_holdout = holdout_pair(Xtr, ytr, Xho, yho, COVID_ED_COLUMNS, COVID_FULL_COLUMNS)
    covid = {
        "folds": covid_folds,
        "holdout": covid_holdout,
        "summary": summarize_sensitivity(
            "covid2020_exclude_ERTOTY2",
            "2020 ED volume was disrupted; drop ERTOTY2 from both nested models.",
            covid_folds,
            covid_holdout,
        ),
    }
    write_sensitivity_bundle(
        "sensitivity_covid2020_v1_1",
        "COVID-year (exclude ERTOTY2) sensitivity",
        "Same persons and seed-42 split. ED-history uses ERTOTY1 and ERTOTY3 only; "
        "the full model uses the prespecified predictors except ERTOTY2. "
        "The primary comparison remains three-year ED history including 2020. "
        "This addresses pandemic disruption of utilization, not a search for a larger increment.",
        covid,
    )
    adult_age = run_exploratory_adult_age_ablation(Xtr, ytr, Xho, yho, adult_tr, adult_ho)
    return {"adult": adult, "all9rds": all9, "covid": covid, "adult_age_ablation": adult_age}


def run_revision() -> dict:
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    cohort, u_train, u_holdout = load_cohort_with_usable_split()
    if len(cohort.X_train) != 3831 or len(cohort.X_holdout) != 1277:
        raise RevisionV11Error(
            f"Unexpected split sizes train={len(cohort.X_train)} holdout={len(cohort.X_holdout)}"
        )
    intervals = write_nb_intervals()
    missing = write_analytic_missingness(cohort.usable)
    vif = write_vif_drop_reference(cohort.X_train)
    holdout = write_holdout_uncertainty(cohort)
    sensitivities = run_sensitivities(cohort, u_train, u_holdout)
    manifest = {
        "tag": V1_1_TAG,
        "primary_results_overwritten": False,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "holdout_seed": config.RANDOM_SEED,
        "cv_seed": repeated_cv.CV_RANDOM_STATE,
        "n_train": len(cohort.X_train),
        "n_holdout": len(cohort.X_holdout),
        "n_analytic": len(cohort.usable),
        "vif_drop_reference_rows": int(len(vif)),
        "analytic_missingness_rows": int(len(missing)),
        "nb_interval_rows": int(len(intervals)),
    }
    _write_text(json.dumps(manifest, indent=2), config.OUTPUTS_DIR / "revision_v1_1_manifest.json")
    print("v1.1 revision outputs written.")
    return {
        "intervals": intervals,
        "missing": missing,
        "vif": vif,
        "holdout": holdout,
        "sensitivities": sensitivities,
        "manifest": manifest,
    }


def main() -> int:
    run_revision()
    return 0


if __name__ == "__main__":
    sys.exit(main())
