# COVID-year (exclude ERTOTY2) sensitivity

Sensitivity analysis only. **Does not replace** the primary YEARIND==1
Family A comparison.

Same persons and seed-42 split. ED-history uses ERTOTY1 and ERTOTY3 only; the full model uses the prespecified predictors except ERTOTY2. The primary comparison remains three-year ED history including 2020. This addresses pandemic disruption of utilization, not a search for a larger increment.

## Sample

- Training subset n = 3831
- Holdout subset n = 1277 (events 173, prevalence 0.1355)
- Original seed-42 split membership is preserved; the subset is not re-randomized.

## Training-only 5×5 Nadeau–Bengio (Full − ED-history)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | +0.0460 | 0.0116 | +3.953 | 0.0006 | +0.0220 to +0.0700 |
| PR-AUC | +0.0518 | 0.0108 | +4.809 | 0.0001 | +0.0296 to +0.0740 |
| Brier | -0.0021 | 0.0010 | -2.057 | 0.0508 | -0.0041 to +0.0000 |

Sign convention: Δ = Full − ED-history. Lower Brier is better, so a
negative ΔBrier favors the full model.

## First-run holdout subset (descriptive)

| metric | ED-history | Full | Δ |
|---|---:|---:|---:|
| ROC-AUC | 0.6839 | 0.7731 | +0.0892 |
| PR-AUC | 0.3069 | 0.4086 | +0.1018 |
| Brier | 0.1062 | 0.0998 | -0.0064 |

Holdout subset metrics are internal evaluation, not a new primary.
