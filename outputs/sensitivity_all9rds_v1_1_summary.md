# ALL9RDS==1 sensitivity

Sensitivity analysis only. **Does not replace** the primary YEARIND==1
Family A comparison.

Primary inclusion remains YEARIND==1. ALL9RDS==1 is AHRQ’s complete nine-round subset used with LONGWT for national longitudinal estimates. This sensitivity asks whether requiring complete-round participation changes the incremental-value conclusion. It is not adopted as primary.

## Sample

- Training subset n = 3663
- Holdout subset n = 1220 (events 166, prevalence 0.1361)
- Original seed-42 split membership is preserved; the subset is not re-randomized.

## Training-only 5×5 Nadeau–Bengio (Full − ED-history)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | +0.0311 | 0.0121 | +2.571 | 0.0168 | +0.0061 to +0.0562 |
| PR-AUC | +0.0381 | 0.0130 | +2.929 | 0.0073 | +0.0112 to +0.0649 |
| Brier | -0.0018 | 0.0011 | -1.612 | 0.1201 | -0.0041 to +0.0005 |

Sign convention: Δ = Full − ED-history. Lower Brier is better, so a
negative ΔBrier favors the full model.

## First-run holdout subset (descriptive)

| metric | ED-history | Full | Δ |
|---|---:|---:|---:|
| ROC-AUC | 0.7072 | 0.7704 | +0.0632 |
| PR-AUC | 0.3343 | 0.4171 | +0.0828 |
| Brier | 0.1055 | 0.0998 | -0.0057 |

Holdout subset metrics are internal evaluation, not a new primary.
