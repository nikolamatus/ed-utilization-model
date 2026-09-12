"""
python -m feasibility.run

Runs the full feasibility pipeline end to end and writes every output file
under outputs/. Fails loudly if any schema/leakage/cohort assumption is
violated.
"""
import dataclasses
import sys

import pandas as pd

from . import config, download, features, ingest, inspect as inspect_stage, longitudinal, modeling, report


def main() -> int:
    config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    raw_file = download.main()
    df = ingest.load_data(raw_file)
    longitudinal.assert_unique_persons(df)

    shape = inspect_stage.basic_shape(df)
    candidate_names = [s.name for s in config.CANDIDATE_FEATURES]
    missingness = inspect_stage.missingness_table(df, candidate_names)
    missingness.to_csv(config.OUTPUTS_DIR / "missingness.csv", index=False)
    ed_summary = inspect_stage.ed_utilization_summary(df)
    ed_summary.to_csv(config.OUTPUTS_DIR / "ed_utilization_summary.csv", index=False)
    prior_vs_future = inspect_stage.prior_vs_future_table(df)
    prior_vs_future.to_csv(config.OUTPUTS_DIR / "prior_vs_future_ed.csv", index=False)

    dup_check = longitudinal.duplicate_person_check(df)
    years_table = longitudinal.years_observed_table(df)
    years_table.to_csv(config.OUTPUTS_DIR / "years_observed.csv", index=False)
    usable_df = longitudinal.usable_prediction_population(df)
    usable_n = len(usable_df)
    cohort = longitudinal.cohort_summary(df, usable_df)
    pd.DataFrame([shape | dup_check | cohort | {"usable_prediction_population": usable_n}]).to_csv(
        config.OUTPUTS_DIR / "population_summary.csv", index=False
    )

    audit = features.build_feature_audit(usable_df)
    audit.to_csv(config.OUTPUTS_DIR / "feature_audit.csv", index=False)
    usable_cols = features.usable_predictor_columns(audit)
    X = features.build_feature_matrix(usable_df, usable_cols)
    features.assert_no_leakage(list(X.columns))
    outcomes = features.build_outcome(usable_df)
    y = outcomes["future_ed_visit"].astype(int)
    secondary = features.secondary_outcome_inspection(outcomes)

    outcome_prevalence = float(y.mean())
    n_outcome_events = int(y.sum())

    X_train, X_test, y_train, y_test = modeling._split(X, y)
    results = [modeling.baseline_prevalence(y_train, y_test)]

    prior_col = config.ED_VISIT_VARS["year3_2021"]
    if prior_col in X.columns:
        results.append(modeling.baseline_prior_year_only(X_train, y_train, X_test, y_test, prior_col))
    hist_cols = [c for c in config.PREDICTOR_ED_VARS if c in X.columns]
    if hist_cols:
        results.append(modeling.baseline_three_year_history(X_train, y_train, X_test, y_test, hist_cols))

    numeric_cols, categorical_cols = features.split_columns_by_treatment(usable_cols)
    y_prob_full = None
    if numeric_cols or categorical_cols:
        full_result, _pipe, y_prob_full = modeling.full_logistic_model(
            X_train, y_train, X_test, y_test, numeric_cols, categorical_cols
        )
        results.append(full_result)
        preds_df = X_test.copy()
        preds_df["y_true"] = y_test.values
        preds_df["y_prob"] = y_prob_full
        preds_df.to_csv(config.OUTPUTS_DIR / "predictions.csv", index=False)

    pd.DataFrame([dataclasses.asdict(r) for r in results]).to_csv(
        config.OUTPUTS_DIR / "model_metrics.csv", index=False
    )

    calibration_produced = False
    if y_prob_full is not None:
        modeling.write_calibration_outputs(
            y_test,
            y_prob_full,
            config.OUTPUTS_DIR / "calibration.csv",
            config.FIGURES_DIR / "calibration.png",
        )
        calibration_produced = True

    def _metric(name, field):
        row = next((r for r in results if r.model_name == name), None)
        return None if row is None else getattr(row, field)

    ed_baselines = [r for r in results if r.model_name in {
        "baseline_2_prior_year_ed_only", "baseline_3_three_year_ed_history"
    }]
    best_ed_roc = max((r.roc_auc for r in ed_baselines if r.roc_auc is not None), default=None)
    best_ed_pr = max((r.pr_auc for r in ed_baselines if r.pr_auc is not None), default=None)

    families_present = sorted({
        config.FEATURE_INDEX[c].family for c in usable_cols if c in config.FEATURE_INDEX
    })
    n_allowed = len(config.allowed_predictor_specs())
    n_present_allowed = int(audit.loc[audit["usable"]].shape[0])

    gate_context = {
        "usable_n": usable_n,
        "n_outcome_events": n_outcome_events,
        "outcome_prevalence": outcome_prevalence,
        "families_present": families_present,
        "n_allowed_candidates": n_allowed,
        "n_present_allowed": n_present_allowed,
        "longitudinal_ok": True,
        "leakage_ok": True,
        "calibration_produced": calibration_produced,
        "unique_persons": dup_check["n_duplicate_person_rows"] == 0,
        "baseline2_roc_auc": _metric("baseline_2_prior_year_ed_only", "roc_auc"),
        "baseline2_pr_auc": _metric("baseline_2_prior_year_ed_only", "pr_auc"),
        "full_roc_auc": _metric("model_4_regularized_logistic_full_features", "roc_auc"),
        "full_pr_auc": _metric("model_4_regularized_logistic_full_features", "pr_auc"),
        "best_ed_baseline_roc_auc": best_ed_roc,
        "best_ed_baseline_pr_auc": best_ed_pr,
        "weighted": False,
    }
    gate_status, gate_details = report.decide_gate(gate_context)

    payload = {
        "shape": shape,
        "duplicate_check": dup_check,
        "cohort": cohort,
        "usable_n": usable_n,
        "outcome_prevalence": outcome_prevalence,
        "n_outcome_events": n_outcome_events,
        "secondary_outcome_high_ed_use": secondary,
        "weighted": False,
        "metric_scope": "unweighted_predictive_performance_on_analytic_sample",
        "not_national_estimates": True,
        "calibration": {"produced": calibration_produced, "path": "calibration.csv"},
        "decision_gate": gate_details,
        "model_metrics_summary": [dataclasses.asdict(r) for r in results],
        "families_present": families_present,
    }
    report.write_feasibility_summary(config.OUTPUTS_DIR / "feasibility_summary.json", payload)
    report.write_methodology_md(config.OUTPUTS_DIR / "methodology.md", payload)

    print(f"\nDone. Decision gate: {gate_status}")
    for r in gate_details["reasons"]:
        print(f"  - {r}")
    print(f"\nFull output written to {config.OUTPUTS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
