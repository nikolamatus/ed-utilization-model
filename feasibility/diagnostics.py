"""
Predictor redundancy diagnostic (pairwise association + VIF).

Uses the same 3,831-person training portion and the same preprocessing
design matrix as the full logistic model. Does not fit ablation models,
does not drop predictors, and does not write existing experiment files.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

from . import config, download, features, ingest, longitudinal, modeling, repeated_cv

PREDICTORS = list(repeated_cv.FULL_COLUMNS)
ABLATED_BLOCKS = ["AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X", "RTHLTH6", "MNHLTH6"]
PENDING_BLOCKS = ["INSCOVY3", "HAVEUS6", "POVCATY3", "TTLPY3X", "EMPST6"]
ASSOC_FLAG = 0.5
VIF_FLAG_MODERATE = 5.0
VIF_FLAG_HIGH = 10.0


def _pairwise_complete(a: pd.Series, b: pd.Series) -> tuple[pd.Series, pd.Series]:
    mask = a.notna() & b.notna()
    return a[mask], b[mask]


def correlation_ratio_eta(categorical: pd.Series, numeric: pd.Series) -> float:
    cat, num = _pairwise_complete(categorical, numeric)
    if cat.empty or num.nunique() < 2 or cat.nunique() < 1:
        return float("nan")
    values = num.to_numpy(dtype=float)
    ss_tot = float(np.sum((values - values.mean()) ** 2))
    if ss_tot <= 0:
        return float("nan")
    ss_between = 0.0
    for _, grp in num.groupby(cat, observed=False):
        ss_between += len(grp) * (float(grp.mean()) - float(values.mean())) ** 2
    return float(np.sqrt(ss_between / ss_tot))


def cramers_v(a: pd.Series, b: pd.Series) -> float:
    x, y = _pairwise_complete(a, b)
    if x.empty or x.nunique() < 2 or y.nunique() < 2:
        return float("nan")
    table = pd.crosstab(x, y)
    chi2 = chi2_contingency(table, correction=False)[0]
    n = int(table.to_numpy().sum())
    k = min(table.shape[0] - 1, table.shape[1] - 1)
    if n == 0 or k <= 0:
        return float("nan")
    return float(np.sqrt(chi2 / (n * k)))


def point_biserial(numeric: pd.Series, binary: pd.Series) -> float:
    num, cat = _pairwise_complete(numeric, binary)
    if num.empty or cat.nunique() != 2 or num.nunique() < 2:
        return float("nan")
    codes = pd.Categorical(cat).codes.astype(float)
    return float(pearsonr(num.to_numpy(dtype=float), codes)[0])


def pairwise_associations(X: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Long-format pairwise associations among raw predictors."""
    columns = list(columns or PREDICTORS)
    numeric, categorical = features.split_columns_by_treatment(columns)
    numeric_set = set(numeric)
    rows = []
    for i, a in enumerate(columns):
        for b in columns[i + 1:]:
            sa, sb = X[a], X[b]
            a_num, b_num = a in numeric_set, b in numeric_set
            if a_num and b_num:
                xa, xb = _pairwise_complete(sa, sb)
                pear = float(pearsonr(xa, xb)[0]) if len(xa) > 2 and xa.nunique() > 1 and xb.nunique() > 1 else float("nan")
                spear = float(spearmanr(xa, xb)[0]) if len(xa) > 2 and xa.nunique() > 1 and xb.nunique() > 1 else float("nan")
                rows.append({"var_a": a, "var_b": b, "association_type": "pearson", "value": pear})
                rows.append({"var_a": a, "var_b": b, "association_type": "spearman", "value": spear})
            elif (not a_num) and (not b_num):
                rows.append({
                    "var_a": a, "var_b": b,
                    "association_type": "cramers_v",
                    "value": cramers_v(sa, sb),
                })
            else:
                cat_name, num_name = (a, b) if not a_num else (b, a)
                cat_s, num_s = X[cat_name], X[num_name]
                n_levels = int(_pairwise_complete(cat_s, num_s)[0].nunique())
                if n_levels == 2:
                    rows.append({
                        "var_a": a, "var_b": b,
                        "association_type": "point_biserial",
                        "value": point_biserial(num_s, cat_s),
                    })
                else:
                    rows.append({
                        "var_a": a, "var_b": b,
                        "association_type": "correlation_ratio_eta",
                        "value": correlation_ratio_eta(cat_s, num_s),
                    })
    return pd.DataFrame(rows)


def association_square_matrix(assoc: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """One display value per pair: Pearson, point-biserial, eta, or Cramer's V."""
    mat = pd.DataFrame(np.eye(len(columns)), index=columns, columns=columns, dtype=float)
    for _, rec in assoc.iterrows():
        if rec["association_type"] == "spearman":
            continue
        a, b, val = rec["var_a"], rec["var_b"], rec["value"]
        mat.loc[a, b] = val
        mat.loc[b, a] = val
    return mat


def flagged_associations(assoc: pd.DataFrame, threshold: float = ASSOC_FLAG) -> pd.DataFrame:
    out = assoc.dropna(subset=["value"]).copy()
    out = out[out["association_type"] != "spearman"]
    return out[out["value"].abs() > threshold].sort_values("value", key=np.abs, ascending=False)


def _source_variable(design_name: str, numeric_cols: list[str], categorical_cols: list[str]) -> str:
    rest = design_name
    if rest.startswith("num__"):
        rest = rest[5:]
    elif rest.startswith("cat__"):
        rest = rest[5:]
    for col in sorted(numeric_cols + categorical_cols, key=len, reverse=True):
        if rest == col or rest.startswith(f"{col}_"):
            return col
    return rest


def design_matrix_and_names(X: pd.DataFrame, columns: list[str] | None = None):
    """Fit the existing full-model preprocessor on X; return transformed array and names."""
    columns = list(columns or PREDICTORS)
    numeric, categorical = features.split_columns_by_treatment(columns)
    pre = modeling._preprocessor(numeric, categorical)
    transformed = pre.fit_transform(X[columns])
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    names = list(pre.get_feature_names_out())
    sources = [_source_variable(n, numeric, categorical) for n in names]
    return np.asarray(transformed, dtype=float), names, sources


def variance_inflation_factors(X: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """VIF on the design matrix the full logistic model actually sees."""
    mat, names, sources = design_matrix_and_names(X, columns)
    n_cols = mat.shape[1]
    vifs = []
    for j in range(n_cols):
        y = mat[:, j]
        others = np.delete(mat, j, axis=1)
        if not np.isfinite(y).all() or np.nanstd(y) == 0:
            vifs.append(float("inf"))
            continue
        try:
            model = LinearRegression()
            model.fit(others, y)
            r2 = float(model.score(others, y))
        except ValueError:
            vifs.append(float("inf"))
            continue
        if r2 >= 1.0 - 1e-12:
            vifs.append(float("inf"))
        else:
            vifs.append(float(1.0 / (1.0 - r2)))
    return pd.DataFrame({
        "design_column": names,
        "source_variable": sources,
        "VIF": vifs,
    })


def write_heatmap(mat: pd.DataFrame, path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(10, 8))
    arr = mat.to_numpy(dtype=float)
    im = ax.imshow(arr, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(mat.columns)))
    ax.set_yticks(range(len(mat.index)))
    ax.set_xticklabels(mat.columns, rotation=90, fontsize=8)
    ax.set_yticklabels(mat.index, fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title(
        "Pairwise associations (Pearson / point-biserial / η / Cramér's V)\n"
        "Training portion only; diagnostic, not a modeling change"
    )
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def load_training_predictors() -> pd.DataFrame:
    raw_file = download.find_raw_file()
    if raw_file is None:
        raise FileNotFoundError("No HC-245 .dta file in data/raw/.")
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)
    usable = longitudinal.usable_prediction_population(df)
    X = features.build_feature_matrix(usable, PREDICTORS)
    y = features.build_outcome(usable)["future_ed_visit"].astype(int)
    X_train, _y_train, _X_ho, _y_ho = repeated_cv.training_portion(X, y)
    return X_train.reset_index(drop=True)


def run_diagnostic() -> dict:
    features.assert_no_leakage(PREDICTORS)
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    X_train = load_training_predictors()
    assoc = pairwise_associations(X_train, PREDICTORS)
    vif = variance_inflation_factors(X_train, PREDICTORS)
    mat = association_square_matrix(assoc, PREDICTORS)

    assoc.to_csv(config.OUTPUTS_DIR / "predictor_correlation_matrix.csv", index=False)
    vif.to_csv(config.OUTPUTS_DIR / "predictor_vif.csv", index=False)
    write_heatmap(mat, config.FIGURES_DIR / "predictor_correlation_heatmap.png")

    flagged = flagged_associations(assoc)
    vif_gt5 = vif[vif["VIF"] > VIF_FLAG_MODERATE]
    vif_gt10 = vif[vif["VIF"] > VIF_FLAG_HIGH]
    print(f"Training rows: {len(X_train)}")
    print(f"Association pairs written: {len(assoc)}")
    print(f"Flagged |association| > {ASSOC_FLAG}: {len(flagged)}")
    print(f"Design columns: {len(vif)}; VIF>5: {len(vif_gt5)}; VIF>10: {len(vif_gt10)}")
    return {"associations": assoc, "vif": vif, "heatmap": mat, "n_train": len(X_train)}


def main() -> int:
    run_diagnostic()
    return 0


if __name__ == "__main__":
    sys.exit(main())
