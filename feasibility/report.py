"""
Stage 9 — Feasibility report and research-triage gate.

The gate is an engineering/research triage tool, NOT a validated
statistical decision rule. GREEN means the *intended* question
(incremental value beyond prior ED use) appears worth pursuing with
this file. Prior-ED AUC > 0.55 alone is never sufficient for GREEN.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config

GATE_NOTE = (
    "This gate is an engineering/research triage tool, not a validated "
    "statistical decision rule. Thresholds are conservative and pre-specified "
    "for this feasibility pass. GREEN requires evidence that the broader "
    "pre-2022 feature set adds value beyond historical ED utilization — not "
    "merely that prior ED use predicts future ED use."
)

# Triage floors. Documented as such; not optimized to produce GREEN.
MIN_USABLE_N = 2000
MIN_OUTCOME_EVENTS = 100
MIN_OUTCOME_PREVALENCE = 0.03
MIN_BASELINE_ROC_AUC = 0.55
MIN_INCREMENTAL_ROC_LIFT = 0.02
MIN_INCREMENTAL_PR_LIFT = 0.01
CORE_FAMILIES = frozenset({"prior_utilization", "demographics"})
ADDITIONAL_FAMILIES = frozenset({"health_status", "access", "socioeconomic"})
MIN_PRESENT_ALLOWED_FRACTION = 0.60


def _component(status: str, reasons: list[str]) -> dict:
    return {"status": status, "reasons": reasons}


def decide_gate(context: dict) -> tuple[str, dict]:
    """
    context keys (all optional-safe with conservative defaults):
      usable_n, n_outcome_events, outcome_prevalence,
      families_present (iterable), n_allowed_candidates, n_present_allowed,
      longitudinal_ok, leakage_ok, calibration_produced, unique_persons,
      baseline2_roc_auc, baseline2_pr_auc,
      full_roc_auc, full_pr_auc,
      best_ed_baseline_roc_auc, best_ed_baseline_pr_auc,
      weighted
    """
    usable_n = int(context.get("usable_n") or 0)
    n_events = int(context.get("n_outcome_events") or 0)
    prevalence = float(context.get("outcome_prevalence") or 0.0)
    families = set(context.get("families_present") or [])
    n_allowed = int(context.get("n_allowed_candidates") or 0)
    n_present = int(context.get("n_present_allowed") or 0)

    data_reasons = []
    if usable_n < MIN_USABLE_N:
        data_reasons.append(
            f"Analytic cohort ({usable_n}) is below the {MIN_USABLE_N} triage floor."
        )
    if n_events < MIN_OUTCOME_EVENTS:
        data_reasons.append(
            f"Primary-outcome events ({n_events}) are below the {MIN_OUTCOME_EVENTS} triage floor."
        )
    if prevalence < MIN_OUTCOME_PREVALENCE:
        data_reasons.append(
            f"Outcome prevalence ({prevalence:.2%}) is below {MIN_OUTCOME_PREVALENCE:.0%}."
        )
    missing_core = sorted(CORE_FAMILIES - families)
    if missing_core:
        data_reasons.append(f"Required predictor families missing from X: {missing_core}.")
    if not (families & ADDITIONAL_FAMILIES):
        data_reasons.append(
            "No health_status, access, or socioeconomic predictor is present. "
            "The run can only test prior-ED persistence, which is not the intended question."
        )
    if n_allowed and (n_present / n_allowed) < MIN_PRESENT_ALLOWED_FRACTION:
        data_reasons.append(
            f"Only {n_present}/{n_allowed} allowed candidates are present "
            f"(below {MIN_PRESENT_ALLOWED_FRACTION:.0%})."
        )
    if not context.get("longitudinal_ok", False):
        data_reasons.append("Documented YEARIND==1 longitudinal cohort rule was not applied.")
    data = _component("FAIL" if data_reasons else "PASS", data_reasons or ["Analytic sample and predictor families clear the triage floors."])

    b2 = context.get("baseline2_roc_auc")
    baseline_reasons = []
    if b2 is None or b2 < MIN_BASELINE_ROC_AUC:
        baseline_reasons.append(
            f"Prior-year-ED baseline ROC-AUC ({b2}) does not clear the "
            f"{MIN_BASELINE_ROC_AUC} triage floor versus chance."
        )
    baseline = _component(
        "FAIL" if baseline_reasons else "PASS",
        baseline_reasons or [
            f"Prior-ED baseline ROC-AUC ({b2:.3f}) clears the triage floor. "
            "This is expected persistence, not research feasibility by itself."
        ],
    )

    full_roc = context.get("full_roc_auc")
    full_pr = context.get("full_pr_auc")
    ed_roc = context.get("best_ed_baseline_roc_auc")
    ed_pr = context.get("best_ed_baseline_pr_auc")
    incr_reasons = []
    if full_roc is None or full_pr is None or ed_roc is None or ed_pr is None:
        incr_reasons.append(
            "Incremental value cannot be assessed (missing full-model or ED-baseline "
            "ROC-AUC / PR-AUC). Insufficient evidence."
        )
        incremental = _component("INSUFFICIENT", incr_reasons)
    else:
        roc_lift = full_roc - ed_roc
        pr_lift = full_pr - ed_pr
        if roc_lift < MIN_INCREMENTAL_ROC_LIFT:
            incr_reasons.append(
                f"Full-model ROC-AUC lift vs best ED baseline is {roc_lift:.3f} "
                f"(need ≥ {MIN_INCREMENTAL_ROC_LIFT})."
            )
        if pr_lift < MIN_INCREMENTAL_PR_LIFT:
            incr_reasons.append(
                f"Full-model PR-AUC lift vs best ED baseline is {pr_lift:.3f} "
                f"(need ≥ {MIN_INCREMENTAL_PR_LIFT}). PR-AUC is a primary metric."
            )
        incremental = _component(
            "FAIL" if incr_reasons else "PASS",
            incr_reasons or [
                f"Full model improves ROC-AUC by {roc_lift:.3f} and PR-AUC by {pr_lift:.3f} "
                "over the best ED-history baseline (triage lifts only)."
            ],
        )

    ready_reasons = []
    if not context.get("leakage_ok", False):
        ready_reasons.append("Leakage invariant was not confirmed for this run.")
    if not context.get("calibration_produced", False):
        ready_reasons.append("Calibration table was not produced.")
    if not context.get("unique_persons", False):
        ready_reasons.append("Person identifiers are not unique.")
    if context.get("weighted", False):
        ready_reasons.append(
            "weighted=True is set but this pipeline does not implement "
            "survey-design-adjusted inference."
        )
    if not context.get("longitudinal_ok", False):
        ready_reasons.append("Cohort definition was not applied.")
    readiness = _component(
        "FAIL" if ready_reasons else "PASS",
        ready_reasons or [
            "Leakage check, unique persons, YEARIND cohort rule, and calibration "
            "outputs are in place. Metrics remain unweighted analytic-sample scores."
        ],
    )

    components = {
        "data_feasibility": data,
        "baseline_signal": baseline,
        "incremental_value": incremental,
        "research_readiness": readiness,
    }

    reasons = []
    for key, comp in components.items():
        for r in comp["reasons"]:
            reasons.append(f"[{key}] {r}")

    data_fail = data["status"] == "FAIL"
    ready_fail = readiness["status"] == "FAIL"
    all_pass = all(c["status"] == "PASS" for c in components.values())

    if all_pass:
        status = "GREEN"
        reasons = [
            "Data feasibility, baseline signal, incremental value over ED history, "
            "and research-readiness checks all passed the pre-specified triage floors."
        ] + reasons
    elif data_fail or ready_fail:
        status = "RED"
    else:
        status = "YELLOW"

    details = {
        "status": status,
        "components": components,
        "reasons": reasons,
        "note": GATE_NOTE,
    }
    return status, details


def write_feasibility_summary(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str))


def write_methodology_md(path: Path, payload: dict) -> None:
    gate = payload["decision_gate"]
    cohort = payload.get("cohort", {})
    secondary = payload.get("secondary_outcome_high_ed_use", {})
    cal = payload.get("calibration", {})
    md = f"""# Feasibility Methodology & Results

Generated automatically by `feasibility/run.py`. No number in this file was
typed in by hand.

This is an initial feasibility experiment using publicly available MEPS data.
It is **not** a national risk-prediction product.

## Dataset
{config.MEPS_SOURCE['dataset_name']} ({config.MEPS_SOURCE['puf_id']}, {config.MEPS_SOURCE['coverage']})

## Population
- Rows in raw file: {payload['shape']['n_rows']:,}
- Unique persons (DUPERSID): {payload['shape']['n_unique_persons']:,}
- Duplicate person rows: {payload['duplicate_check']['n_duplicate_person_rows']}
- Analytic cohort rule: {cohort.get('cohort_rule', 'YEARIND==1 AND valid ERTOTY1–Y4')}
- YEARIND==1 count: {cohort.get('n_yearind_all_four_years', 'n/a')}
- ALL9RDS==1 count (reported, not required): {cohort.get('n_all9rds', 'n/a')}
- Analytic cohort n: {payload['usable_n']:,}
- Analytic ∩ ALL9RDS: {cohort.get('n_analytic_and_all9rds', 'n/a')}

ALL9RDS is **not** the inclusion rule. It is the AHRQ subset for weighted
national four-year estimates. This run does not produce those estimates.

## Outcome (primary, modeled)
- `future_ed_visit` = 1 if ERTOTY4 ≥ 1 else 0, among valid non-sentinel ERTOTY4
- Prevalence of ≥1 ED visit: {payload['outcome_prevalence']:.2%}
- Event count: {payload.get('n_outcome_events', 'n/a')}

## Secondary outcome (≥2 ED visits) — not modeled
- Status: {secondary.get('status', 'not_modeled_future_analysis')}
- Events (inspection only): {secondary.get('n_events', 'n/a')}
- {secondary.get('note', '')}

## Prediction design
- Cutoff: 2021-12-31. Outcome window: 2022 calendar year.
- Predictors: confirmed HC-245 names available by end of 2021 (see feature_audit.csv)
- `ERTOTY4` and other 2022 / Y4 / Round 8–9 counterparts cannot enter X
  (`LeakageError` if they do; unknown-availability columns fail closed)

## Evaluation
- Split: 25% person-level holdout, stratified on the primary outcome, seed={config.RANDOM_SEED}
- Ranking metrics: ROC-AUC and PR-AUC (PR-AUC is primary at modest prevalence)
- Proper scoring: Brier
- Calibration: {'written to calibration.csv' if cal.get('produced') else 'not produced'}
- Sensitivity/specificity/precision/recall: exploratory at threshold 0.5 only

## Survey design disclosure
This run does **not** apply MEPS survey weights (`LONGWT`) or design
variables (`VARSTR`, `VARPSU`). Metrics describe **unweighted predictive
performance on this analytic sample**. They are **not** nationally
representative MEPS estimates. Survey-design-adjusted inference is outside
the scope of this initial feasibility experiment.

## Decision gate: **{gate['status']}**
{gate.get('note', '')}

{chr(10).join('- ' + r for r in gate.get('reasons', []))}

## Limitations (always report)
- MEPS-HC samples the civilian noninstitutionalized population and
  structurally excludes or undersamples people experiencing homelessness.
  This project does not predict homelessness or housing instability.
- No substance-use-disorder or food-insecurity predictors are used.
- Utilization and health status are self/proxy-reported.
- Panel 24 overlaps COVID-19 data-collection changes.
- Association/prediction only. No causal claim.
- Not clinically validated and not deployment-ready.
"""
    path.write_text(md, encoding="utf-8")
