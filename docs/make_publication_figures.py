"""
Publication figures from frozen v1.1/v1.0 outputs.

Does not refit models, does not write locked v1.0 filenames, and does not
change statistical results. Reads saved CSVs only.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "figures"
SRC = REPO / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def _style() -> None:
    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def fig1_temporal() -> None:
    fig, ax = plt.subplots(figsize=(8.2, 2.8))
    ax.set_xlim(2018.6, 2023.2)
    ax.set_ylim(0, 4)
    ax.axis("off")
    years = [(2019, "Y1\nERTOTY1"), (2020, "Y2\nERTOTY2"), (2021, "Y3 / R6\npredictors"), (2022, "Y4\nERTOTY4")]
    for i, (yr, lab) in enumerate(years):
        color = "#4C78A8" if yr < 2022 else "#E45756"
        ax.barh(2.2, 0.85, left=yr - 0.42, height=0.9, color=color, alpha=0.85)
        ax.text(yr, 2.2, lab, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
    ax.annotate(
        "Prediction cutoff\n31 Dec 2021",
        xy=(2021.5, 1.55),
        xytext=(2020.1, 0.45),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=8,
        ha="center",
    )
    ax.text(2022.0, 3.35, "Outcome window (not in X)", ha="center", fontsize=8, color="#E45756")
    ax.text(2020.0, 3.35, "Predictor window (fail-closed)", ha="center", fontsize=8, color="#4C78A8")
    ax.text(
        2020.7,
        0.15,
        "Round 7 overlaps 2021–2022 and is unused. Rounds 8–9 / Y4 names cannot enter X.",
        ha="center",
        fontsize=8,
    )
    ax.set_title("Temporal structure of the prediction problem")
    fig.savefig(OUT / "fig1_temporal_structure.png")
    plt.close(fig)


def fig2_primary_increments() -> None:
    inf = pd.read_csv(SRC / "statistical_inference_intervals_v1_1.csv")
    a = inf[(inf["family"] == "A")].set_index("metric")
    labels = ["ROC-AUC", "PR-AUC", "Brier"]
    keys = ["roc_auc", "pr_auc", "brier"]
    means = [a.loc[k, "mean_difference"] for k in keys]
    lo = [a.loc[k, "ci_lower"] for k in keys]
    hi = [a.loc[k, "ci_upper"] for k in keys]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.axvline(0, color="#888888", linewidth=1)
    xerr = np.vstack([np.array(means) - np.array(lo), np.array(hi) - np.array(means)])
    ax.errorbar(means, y, xerr=xerr, fmt="o", color="#4C78A8", capsize=4, markersize=7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Mean increment (Full − 3-year ED history)\nNadeau–Bengio 95% CI; training-only 5×5 CV")
    ax.set_title("Primary incremental performance (Nadeau–Bengio 95% CIs)")
    ax.text(
        0.02,
        -0.32,
        "Negative ΔBrier favors the full model (lower Brier is better). Internal validation only.",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
    )
    fig.savefig(OUT / "fig2_primary_increments.png")
    plt.close(fig)


def fig3_calibration() -> None:
    cal = pd.read_csv(SRC / "calibration.csv")
    cox = pd.read_csv(SRC / "holdout_calibration_v1_1.csv")
    full = cox[cox["model"] == "full_model"].iloc[0]
    fig, ax = plt.subplots(figsize=(4.8, 4.8))
    ax.plot([0, 1], [0, 1], color="#888888", linestyle="--", linewidth=1, label="Perfect calibration")
    ax.plot(
        cal["mean_predicted"],
        cal["observed_fraction"],
        marker="o",
        color="#4C78A8",
        label="Quantile bins (locked first-run holdout)",
    )
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.5)
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed event fraction")
    ax.set_title("Calibration on the first-run internal holdout")
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.text(
        0.05,
        0.92,
        f"CITL={full['calibration_in_the_large']:.3f}; slope={full['calibration_slope']:.3f}\n"
        f"mean p={full['mean_predicted']:.3f}; observed={full['observed_prevalence']:.3f}\n"
        "Not recalibrated; not external validation.",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
    )
    fig.savefig(OUT / "fig3_calibration_holdout.png")
    plt.close(fig)


def fig4_sensitivity() -> None:
    rows = []
    adult = pd.read_csv(SRC / "sensitivity_adult_only_v1_1_inference.csv")
    all9 = pd.read_csv(SRC / "sensitivity_all9rds_v1_1_inference.csv")
    covid = pd.read_csv(SRC / "sensitivity_covid2020_v1_1_inference.csv")
    primary = pd.read_csv(SRC / "statistical_inference_intervals_v1_1.csv")
    p = primary[(primary["family"] == "A") & (primary["metric"] == "roc_auc")].iloc[0]
    rows.append(("Primary (mixed-age)", p["mean_difference"], p["ci_lower"], p["ci_upper"]))
    a = adult[adult["metric"] == "roc_auc"].iloc[0]
    rows.append(("Sensitivity: adult-only", a["cv_mean_difference"], a["cv_ci_lower"], a["cv_ci_upper"]))
    n9 = all9[all9["metric"] == "roc_auc"].iloc[0]
    rows.append(("Sensitivity: ALL9RDS = 1", n9["cv_mean_difference"], n9["cv_ci_lower"], n9["cv_ci_upper"]))
    c = covid[covid["metric"] == "roc_auc"].iloc[0]
    rows.append(("Sensitivity: exclude ERTOTY2", c["cv_mean_difference"], c["cv_ci_lower"], c["cv_ci_upper"]))
    labels, means, lo, hi = zip(*rows)
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    ax.axvline(0, color="#888888", linewidth=1)
    xerr = np.vstack([np.array(means) - np.array(lo), np.array(hi) - np.array(means)])
    ax.errorbar(means, y, xerr=xerr, fmt="o", color="#4C78A8", capsize=4, markersize=7)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("ΔROC-AUC (Full − ED-history), Nadeau–Bengio 95% CI")
    ax.set_title("ROC increment: primary analysis and labeled sensitivities")
    ax.text(
        0.0,
        -0.28,
        "Sensitivities are not replacement primary analyses and are not external confirmation.",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
    )
    fig.savefig(OUT / "fig4_sensitivity_roc.png")
    plt.close(fig)


def main() -> None:
    _style()
    fig1_temporal()
    fig2_primary_increments()
    fig3_calibration()
    fig4_sensitivity()
    print("Wrote publication figures to", OUT)


if __name__ == "__main__":
    main()
