# Feasibility Methodology & Results

Generated automatically by `feasibility/run.py`. No number in this file was
typed in by hand.

This is an initial feasibility experiment using publicly available MEPS data.
It is **not** a national risk-prediction product.

## Dataset
MEPS HC-245: Panel 24, 4-Year Longitudinal Public Use File (HC-245, 2019-2022)

## Population
- Rows in raw file: 5,565
- Unique persons (DUPERSID): 5,565
- Duplicate person rows: 0
- Analytic cohort rule: YEARIND==1 AND valid non-sentinel ERTOTY1–Y4
- YEARIND==1 count: 5108
- ALL9RDS==1 count (reported, not required): 4883
- Analytic cohort n: 5,108
- Analytic ∩ ALL9RDS: 4883

ALL9RDS is **not** the inclusion rule. It is the AHRQ subset for weighted
national four-year estimates. This run does not produce those estimates.

## Outcome (primary, modeled)
- `future_ed_visit` = 1 if ERTOTY4 ≥ 1 else 0, among valid non-sentinel ERTOTY4
- Prevalence of ≥1 ED visit: 13.57%
- Event count: 693

## Secondary outcome (≥2 ED visits) — not modeled
- Status: not_modeled_future_analysis
- Events (inspection only): 209
- Constructed for event-count inspection only. Not modeled, not used by the decision gate, and not claimed as part of this experiment. Adequacy of a ≥2-visit analysis is unknown until the real HC-245 file is loaded.

## Prediction design
- Cutoff: 2021-12-31. Outcome window: 2022 calendar year.
- Predictors: confirmed HC-245 names available by end of 2021 (see feature_audit.csv)
- `ERTOTY4` and other 2022 / Y4 / Round 8–9 counterparts cannot enter X
  (`LeakageError` if they do; unknown-availability columns fail closed)

## Evaluation
- Split: 25% person-level holdout, stratified on the primary outcome, seed=42
- Ranking metrics: ROC-AUC and PR-AUC (PR-AUC is primary at modest prevalence)
- Proper scoring: Brier
- Calibration: written to calibration.csv
- Sensitivity/specificity/precision/recall: exploratory at threshold 0.5 only

## Survey design disclosure
This run does **not** apply MEPS survey weights (`LONGWT`) or design
variables (`VARSTR`, `VARPSU`). Metrics describe **unweighted predictive
performance on this analytic sample**. They are **not** nationally
representative MEPS estimates. Survey-design-adjusted inference is outside
the scope of this initial feasibility experiment.

## Decision gate: **GREEN**
This gate is an engineering/research triage tool, not a validated statistical decision rule. Thresholds are conservative and pre-specified for this feasibility pass. GREEN requires evidence that the broader pre-2022 feature set adds value beyond historical ED utilization — not merely that prior ED use predicts future ED use.

- Data feasibility, baseline signal, incremental value over ED history, and research-readiness checks all passed the pre-specified triage floors.
- [data_feasibility] Analytic sample and predictor families clear the triage floors.
- [baseline_signal] Prior-ED baseline ROC-AUC (0.627) clears the triage floor. This is expected persistence, not research feasibility by itself.
- [incremental_value] Full model improves ROC-AUC by 0.065 and PR-AUC by 0.085 over the best ED-history baseline (triage lifts only).
- [research_readiness] Leakage check, unique persons, YEARIND cohort rule, and calibration outputs are in place. Metrics remain unweighted analytic-sample scores.

## Limitations (always report)
- MEPS-HC samples the civilian noninstitutionalized population and
  structurally excludes or undersamples people experiencing homelessness.
  This project does not predict homelessness or housing instability.
- No substance-use-disorder or food-insecurity predictors are used.
- Utilization and health status are self/proxy-reported.
- Panel 24 overlaps COVID-19 data-collection changes.
- Association/prediction only. No causal claim.
- Not clinically validated and not deployment-ready.
