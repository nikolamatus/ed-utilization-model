# Holdout bootstrap and calibration (v1.1)

The 25% split (seed 42, n = 1277, events = 173) is a
**first-run / development-stage internal evaluation set**. It was scored
during the original pipeline and used by the research-triage gate. It is
not an external, pristine, or independently confirmatory sample.

Primary inferential evidence remains the training-only 5×5
Nadeau–Bengio comparison. These intervals describe uncertainty in the
holdout *point* metrics only.

## Bootstrap

- Resampling unit: person-level `(y, p_ed, p_full)` pairs
- Replicates requested: 2000
- Valid replicates: 2000
- Degenerate (single-class) replicates skipped: 0
- Seed: 20210915
- Interval: percentile 2.5th–97.5th

Sign convention: Δ = Full − ED-history. Positive ΔROC/ΔPR favors Full.
Negative ΔBrier favors Full because **lower Brier is better**.

| metric | point | 95% percentile CI |
|---|---:|---|
| ED-history ROC-AUC | 0.7091 | 0.6668 to 0.7523 |
| Full ROC-AUC | 0.7740 | 0.7337 to 0.8104 |
| Δ ROC-AUC | +0.0649 | +0.0281 to +0.1007 |
| ED-history PR-AUC | 0.3308 | 0.2670 to 0.4002 |
| Full PR-AUC | 0.4159 | 0.3445 to 0.4908 |
| Δ PR-AUC | +0.0851 | +0.0473 to +0.1212 |
| ED-history Brier | 0.1053 | 0.0928 to 0.1179 |
| Full Brier | 0.0994 | 0.0876 to 0.1113 |
| Δ Brier | -0.0059 | -0.0087 to -0.0029 |

Refit of the locked pipelines on the reconstructed training portion
matched `outputs/model_metrics.csv` to 1e-12 before bootstrapping.
The bootstrap was not rerun to obtain a preferred interval.

## Calibration intercept and slope

Cox logistic calibration on the **entire** first-run holdout
(n = 1277, events = 173, binary `y` in {0,1}, `p` =
predicted probability, `logit(p)` = log(p/(1-p))). Joint unpenalized
model: logit(P(Y=1)) = a + b logit(p). Calibration-in-the-large (CITL)
is a with b fixed at 1. This is **assessment only**: predicted
probabilities are not replaced, and the production model is not
recalibrated. The split is internal, not external validation.

| model | mean predicted | observed prevalence | CITL (b=1) | intercept a | slope b |
|---|---:|---:|---:|---:|---:|
| ED-history | 0.1347 | 0.1355 | 0.0070 | 0.5052 | 1.2770 |
| Full | 0.1349 | 0.1355 | 0.0056 | 0.4020 | 1.2368 |

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
