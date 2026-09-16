# Revision v1.1 completion report

Publication-revision pass of the frozen MEPS Panel 24 ED-utilization
study. Goal: truthful, reproducible reporting. Not metric optimization.

---

## Scientific question

How much additional **predictive** value can longitudinal health,
utilization, access, demographic, and socioeconomic information provide
beyond historical ED utilization alone for predicting **any ED use in
the subsequent year** (2022) on the MEPS Panel 24 analytic sample?

This is a predictive health-services study. It is not causal inference,
preventability, clinical-decision-support validation, or an
ED-avoidance intervention.

## Primary comparison

- **Baseline:** three-year ED history (`ERTOTY1`, `ERTOTY2`, `ERTOTY3`).
- **Full model:** those counts plus the documented pre-cutoff health,
  access, demographic, and socioeconomic fields.
- Unchanged. Not redefined because another contrast was larger.

## Primary results (verified from locked outputs)

Source: `outputs/statistical_inference.csv` and
`outputs/statistical_inference_intervals_v1_1.csv`.
Training-only 5×5 CV; Δ = Full − ED-history; lower Brier is better.

| Metric | Mean Δ | 95% NB CI | t | p |
|---|---:|---|---:|---:|
| ROC-AUC | +0.0295 | 0.0045 to 0.0546 | +2.437 | 0.0226 |
| PR-AUC | +0.0359 | 0.0140 to 0.0578 | +3.385 | 0.0024 |
| Brier | −0.0017 | −0.0038 to +0.0004 | −1.655 | 0.1110 |

These match the previously reported approximate values (+0.0295,
+0.0359, −0.0017). They were **not** altered to recover those numbers.

First-run holdout points (locked `outputs/model_metrics.csv`), verified
by refit to 1e-12 before bootstrap: ED-history ROC 0.709 / PR 0.331 /
Brier 0.105; full 0.774 / 0.416 / 0.099. Bootstrap percentile 95% CIs
(B = 2,000, seed 20210915): ΔROC 0.028 to 0.101; ΔPR 0.047 to 0.121;
ΔBrier −0.009 to −0.003.

PR-AUC is reported because prevalence is about 0.136; it is more
sensitive to positive-class ranking than ROC-AUC.

## Inferential method

Nadeau–Bengio corrected resampled t-test on 25 paired fold differences:

`Var_NB = (1/n + n_test/n_train) * s²`, n = 25, df = 24, two-sided
Student-t. Implementation audited in `feasibility/statistical_inference.py`
and preserved. Naive SEs are not used.

Family A: unadjusted (plan-specified). Family B: Holm within each
metric across five block contrasts (verified).

## Holdout

25% stratified split, seed 42, n = 1,277. **First-run / development-stage
internal evaluation.** Used by the original pipeline and triage gate.
Not external, pristine, or independently confirmatory. Inferential
p-values are from training-only CV.

## Leakage

Temporal: predictors are Y3 / Round 6 / time-invariant; `ERTOTY4` and
Y4/R8/R9 names are blocked. Preprocessing: sklearn Pipeline fit on
training folds only. No leakage requiring a code fix was found.
Temporal-strict sensitivity was **not** run because it was not
indicated.

## VIF

The **original** locked diagnostic (`outputs/predictor_vif.csv`) is
**not valid** for categorical predictors: one-hot encoding without a
reference level creates the dummy-variable trap, so almost all dummy
VIFs are infinite. Those infinities were never used to drop predictors.

The **corrected** diagnostic drops one reference level
(`outputs/predictor_vif_drop_reference_v1_1.csv`): all 40 VIFs finite,
max 3.68, none > 5. Descriptive only. Primary model unchanged.

## Calibration

Locked quantile reliability diagram unchanged. Production model not
recalibrated.

Verified Cox logistic calibration on the **entire** first-run holdout
(n = 1,277, 173 events; `y` binary; `p` on the probability scale):

- Full model: mean predicted 0.1349 vs observed prevalence 0.1355
- Calibration-in-the-large (slope fixed at 1): **0.006**
- Joint intercept a: **0.402** (offset at predicted p = 0.5 when slope
  is free; not a statement about overall event-rate bias)
- Joint slope b: **1.237** (predicted logits somewhat too small in
  magnitude / risks a bit too close to the mean)

Independent Newton MLE matched sklearn `C=np.inf` to about 2×10⁻⁴.
This is an internal-holdout assessment, not external validation, and
is not described as severe miscalibration.

## Sensitivity analyses

| Analysis | Why | What happened to interpretation |
|---|---|---|
| Adult-only Full vs ED-history (AGEY3X ≥ 18) | Population definition | ROC increment **not detected** (p = 0.113); PR still detected. Qualifies the primary ROC finding. **Sensitivity, not primary.** |
| Exploratory adult-only drop of AGEY3X | Existing B1 block inside the adult subset | No detected change (ΔROC −0.0022, p = 0.637). **Exploratory/post-primary.** Not used to explain the adult Full-vs-ED ROC. |
| ALL9RDS==1 | Complete-round selection | Discrimination conclusion unchanged. Not adopted as primary. |
| Exclude ERTOTY2 | 2020 disruption | Baseline weaker; increment larger. Does not replace 3-year history. |
| Death (original) | Mortality in-scope | Already locked; unchanged. |
| Repeat-level (original) | Sensitivity to NB vs repeat means | Unchanged; does not replace NB. |

## Survey weighting

`LONGWT` / `VARSTR` / `VARPSU` recorded, not applied. Estimand is
unweighted person-level predictive performance on the analytic sample,
not national prevalence or nationally representative performance.
Weighted analysis was not added.

## Multiplicity

Primary: Family A Full − ED-history. Three complementary metrics
without correction (limitation documented; correction not added
post hoc). Secondary: Family B Holm m = 5 per metric. Descriptive
holdout/CV means and v1.1 sensitivities are not additional Family A
tests.

## Provenance

| Concept | Statement |
|---|---|
| Plan creation | Researcher recollection of local drafting before Git; exact date uncertain |
| Git incorporation | `12733c6`, 2026-09-12, together with code and outputs |
| Original analysis | Locked v1.0 outputs in that snapshot |
| Later analyses | Same-day docs/release commits; this v1.1 reporting/sensitivity pass |
| Formal preregistration | Not claimed |
| “Post-hoc plan” from Git order alone | Not claimed |

ChatGPT share URL is a provenance lead, not a verified creation date.

## Reproducibility

- Holdout / logistic seed: 42
- CV seed: 2021
- Bootstrap seed: 20210915, B = 2,000
- Dependencies: `pyproject.toml` (package version **1.1.0**);
  exact freeze in `docs/environment_v1_1.md`
- New command: `python -m feasibility.revision_v1_1`
- Do not run `python -m feasibility.run` against the locked analysis
- Tests: existing suite plus `tests/test_revision_v1_1.py`

## Remaining limitations

- Internal validation only; no external or later-panel test.
- Unweighted analytic-sample estimand.
- Adult-only ROC increment not detected.
- Family A three-metric family unadjusted.
- Single-imputation inside folds; EMPST6 16.01% non-usable on the
  analytic cohort, overwhelmingly structurally inapplicable for
  children, then mode-imputed (employed). Not a causal employment
  coefficient.
- COVID-era panel; 2020 included in the primary baseline by design.
- Calibration slope ≠ 1 on the first-run holdout (exploratory).
- Plan creation date not independently established.
- No clinical-utility threshold was prespecified; statistical
  increments are not claims of operational usefulness.

## Analyses run / not run

**Run:** plan, chronology, checklist, notes, completion; NB CIs;
analytic missingness; VIF drop-first (reconfirmed); holdout bootstrap;
Cox calibration intercept/slope plus CITL; adult-only Full vs ED;
exploratory adult age ablation; ALL9RDS; exclude-2020.

**Not run:** `feasibility.run`; temporal-strict Round-6 drop; weighted
models; multiple imputation; retuning; new test set; Family A
Bonferroni; predictor dropping for VIF.

## Final interpretation

On the mixed-age MEPS Panel 24 analytic sample, the documented full
pre-cutoff model showed a statistically detectable increment over
three-year ED history of about **+0.030 ROC-AUC** (95% CI 0.005 to
0.055) and **+0.036 PR-AUC** (0.014 to 0.058) under Nadeau–Bengio
training-only CV. The Brier increment of about **−0.0017** favored the
full model in sign (lower is better) and was not statistically
detected. The first-run holdout increment was larger (+0.065 ROC,
+0.085 PR) and is one internal split. The adult-only sensitivity did
not detect the ROC increment, so the primary ROC finding should not be
presented as demonstrated for adults alone. No Family B block removal
was detected after Holm correction. These quantities describe
unweighted predictive performance on this panel. They do not establish
clinical usefulness, national performance, or causation.
