"""
Stage 5/6 — Baselines, regularized logistic model, evaluation.

Split: single random person-level holdout (25%), stratified on the
outcome, seed = config.RANDOM_SEED. This is a sample-overfitting check,
not a later-panel validation. Temporal order is enforced in features,
not in the split.

Threshold-based metrics (sensitivity, specificity, precision, recall,
accuracy) are exploratory values at a fixed threshold of 0.5. They are
not an optimized or clinical cutoff.

PR-AUC is a primary metric alongside ROC-AUC because expected prevalence
is modest. Calibration is written on the production path for the full
model.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import config

THRESHOLD_NOTE = (
    "Threshold-dependent exploratory metrics at decision_threshold=0.5. "
    "Not an optimized operating point and not a clinical cutoff."
)


@dataclass
class EvalResult:
    model_name: str
    n_test: int
    prevalence: float
    roc_auc: float | None
    pr_auc: float | None
    brier_score: float | None
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    recall: float
    decision_threshold: float
    threshold_metrics_note: str
    confusion: dict = field(default_factory=dict)


def _split(X: pd.DataFrame, y: pd.Series):
    return train_test_split(
        X, y, test_size=0.25, random_state=config.RANDOM_SEED, stratify=y
    )


def _classifier() -> LogisticRegression:
    return LogisticRegression(max_iter=2000, C=1.0, random_state=config.RANDOM_SEED)


def evaluate_binary(
    model_name: str,
    y_true: pd.Series,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> EvalResult:
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) else float("nan")
    specificity = tn / (tn + fp) if (tn + fp) else float("nan")
    try:
        roc_auc = roc_auc_score(y_true, y_prob) if len(set(y_true)) > 1 else None
    except ValueError:
        roc_auc = None
    try:
        pr_auc = average_precision_score(y_true, y_prob) if len(set(y_true)) > 1 else None
    except ValueError:
        pr_auc = None
    return EvalResult(
        model_name=model_name,
        n_test=len(y_true),
        prevalence=float(np.mean(y_true)),
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        brier_score=float(brier_score_loss(y_true, y_prob)),
        accuracy=float((y_pred == y_true).mean()),
        sensitivity=float(sensitivity),
        specificity=float(specificity),
        precision=float(precision_score(y_true, y_pred, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, zero_division=0)),
        decision_threshold=threshold,
        threshold_metrics_note=THRESHOLD_NOTE,
        confusion={"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    )


def baseline_prevalence(y_train: pd.Series, y_test: pd.Series) -> EvalResult:
    p = float(y_train.mean())
    y_prob = np.full(len(y_test), p)
    return evaluate_binary("baseline_1_prevalence_only", y_test, y_prob)


def _fit_numeric_logistic(X_train, y_train, X_test, y_test, cols: list[str], model_name: str) -> EvalResult:
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", _classifier()),
    ])
    pipe.fit(X_train[cols], y_train)
    y_prob = pipe.predict_proba(X_test[cols])[:, 1]
    return evaluate_binary(model_name, y_test, y_prob)


def baseline_prior_year_only(X_train, y_train, X_test, y_test, prior_col: str) -> EvalResult:
    return _fit_numeric_logistic(
        X_train, y_train, X_test, y_test, [prior_col], "baseline_2_prior_year_ed_only"
    )


def baseline_three_year_history(X_train, y_train, X_test, y_test, cols: list[str]) -> EvalResult:
    return _fit_numeric_logistic(
        X_train, y_train, X_test, y_test, cols, "baseline_3_three_year_ed_history"
    )


def _preprocessor(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    transformers = []
    if numeric_cols:
        transformers.append((
            "num",
            Pipeline([
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
            ]),
            numeric_cols,
        ))
    if categorical_cols:
        transformers.append((
            "cat",
            Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("ohe", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical_cols,
        ))
    if not transformers:
        raise ValueError("No numeric or categorical predictors supplied.")
    return ColumnTransformer(transformers)


def full_logistic_model(
    X_train,
    y_train,
    X_test,
    y_test,
    numeric_cols: list[str],
    categorical_cols: list[str],
    model_name: str = "model_4_regularized_logistic_full_features",
):
    pipe = Pipeline([
        ("pre", _preprocessor(numeric_cols, categorical_cols)),
        ("clf", _classifier()),
    ])
    pipe.fit(X_train, y_train)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    result = evaluate_binary(model_name, y_test, y_prob)
    return result, pipe, y_prob


def calibration_table(y_true, y_prob, n_bins: int = 10) -> pd.DataFrame:
    """Quantile-binned reliability table. Falls back to fewer uniform bins if needed."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    try:
        frac_pos, mean_pred = calibration_curve(
            y_true, y_prob, n_bins=n_bins, strategy="quantile"
        )
    except ValueError:
        bins = max(2, min(5, int(len(np.unique(y_prob)))))
        frac_pos, mean_pred = calibration_curve(
            y_true, y_prob, n_bins=bins, strategy="uniform"
        )
    return pd.DataFrame({
        "mean_predicted": mean_pred,
        "observed_fraction": frac_pos,
    })


def calibration_points(y_true, y_prob, n_bins: int = 10):
    """Kept as a thin wrapper; production path writes calibration_table()."""
    table = calibration_table(y_true, y_prob, n_bins=n_bins)
    return list(zip(table["mean_predicted"].tolist(), table["observed_fraction"].tolist()))


def write_calibration_outputs(y_true, y_prob, csv_path, figure_path, n_bins: int = 10) -> pd.DataFrame:
    table = calibration_table(y_true, y_prob, n_bins=n_bins)
    table.to_csv(csv_path, index=False)
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="perfect calibration")
        ax.plot(
            table["mean_predicted"],
            table["observed_fraction"],
            marker="o",
            color="black",
            label="full logistic (test)",
        )
        ax.set_xlabel("Mean predicted probability")
        ax.set_ylabel("Observed event fraction")
        ax.set_title("Reliability diagram (exploratory, unweighted test fold)")
        ax.legend()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        fig.tight_layout()
        fig.savefig(figure_path, dpi=120)
        plt.close(fig)
    except Exception:
        pass
    return table
