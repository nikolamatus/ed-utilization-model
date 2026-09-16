# Adult-only sensitivity (AGEY3X ≥ 18)

Sensitivity analysis only. **Does not replace** the primary YEARIND==1
Family A comparison.

Restricts the original seed-42 split to persons aged ≥ 18 at the 2021 cutoff. Persons under 18 in the analytic cohort: 898. This addresses a population-definition concern, not a performance-chasing exercise.

## Sample

- Training subset n = 3162
- Holdout subset n = 1048 (events 166, prevalence 0.1584)
- Original seed-42 split membership is preserved; the subset is not re-randomized.

## Training-only 5×5 Nadeau–Bengio (Full − ED-history)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | +0.0194 | 0.0118 | +1.643 | 0.1134 | -0.0050 to +0.0438 |
| PR-AUC | +0.0299 | 0.0090 | +3.312 | 0.0029 | +0.0113 to +0.0486 |
| Brier | -0.0014 | 0.0010 | -1.331 | 0.1958 | -0.0035 to +0.0008 |

Sign convention: Δ = Full − ED-history. Lower Brier is better, so a
negative ΔBrier favors the full model.

## First-run holdout subset (descriptive)

| metric | ED-history | Full | Δ |
|---|---:|---:|---:|
| ROC-AUC | 0.7141 | 0.7586 | +0.0445 |
| PR-AUC | 0.3663 | 0.4303 | +0.0640 |
| Brier | 0.1192 | 0.1140 | -0.0052 |

Holdout subset metrics are internal evaluation, not a new primary.
