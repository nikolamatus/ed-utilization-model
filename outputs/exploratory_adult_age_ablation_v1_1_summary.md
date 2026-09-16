# Exploratory adult-only age ablation (v1.1)

**Classification:** exploratory / post-primary. Not prespecified. Does
**not** replace the mixed-age Family A primary comparison and does
**not** replace the adult-only Full-versus-ED-history sensitivity.

Purpose: within the already-defined adult subset of the original seed-42
split, apply the documented B1 contrast (remove `AGEY3X` only from the
full model) using the same 5×5 CV seed (2021). The question is whether
age appears to contribute disproportionately among adults. This is not
a search over alternative age specifications.

## Sample

- Adult training n = 3162
- Adult holdout n = 1048 (events 166)

## Training-only 5×5 Nadeau–Bengio (No-age − Full)

| metric | mean Δ | corrected SE | t | p | 95% CI |
|---|---:|---:|---:|---:|---|
| ROC-AUC | -0.0022 | 0.0046 | -0.478 | 0.6371 | -0.0117 to +0.0073 |
| PR-AUC | -0.0007 | 0.0038 | -0.182 | 0.8567 | -0.0085 to +0.0071 |
| Brier | +0.0002 | 0.0004 | +0.471 | 0.6418 | -0.0006 to +0.0010 |

Sign convention matches Family B: Δ = No-age − Full. Negative ΔROC/ΔPR
means the full model (with age) had higher discrimination.

## Adult holdout subset (descriptive)

| metric | Full | No-age | No-age − Full |
|---|---:|---:|---:|
| ROC-AUC | 0.7586 | 0.7574 | -0.0012 |
| PR-AUC | 0.4303 | 0.4196 | -0.0107 |
| Brier | 0.1140 | 0.1147 | +0.0007 |

This diagnostic is not used to explain away the adult-only Full-versus-ED
ROC result, and it is not promoted to a primary analysis.
