# Table 3. Family B leave-one-block-out contrasts (reduced minus full)

Same 25 training-only folds as Table 2. Holm–Bonferroni adjustment is
applied **within each metric** across the five contrasts (m = 5). Blocks
are **not ranked**. A non-significant contrast is not evidence that the
block can be dropped.

Source: `outputs/statistical_inference.csv` and
`outputs/statistical_inference_intervals_v1_1.csv`.

Sign convention: Δ = (model without the named block) − Full. For ROC/PR,
negative Δ means the full model is better. For Brier, positive Δ means
the full model is better (lower Brier).

| Contrast | Metric | Mean Δ | 95% CI | Raw *p* | Holm *p* | Detected at 0.05 |
|---|---|---:|---|---:|---:|---|
| B1 No-age − Full | ROC-AUC | −0.0051 | −0.0130 to +0.0027 | 0.1884 | 0.8720 | No |
| B1 No-age − Full | PR-AUC | −0.0017 | −0.0112 to +0.0077 | 0.7092 | 1.0000 | No |
| B1 No-age − Full | Brier | +0.0002 | −0.0006 to +0.0009 | 0.6497 | 1.0000 | No |
| B2 No-demographics − Full | ROC-AUC | +0.0062 | −0.0030 to +0.0154 | 0.1744 | 0.8720 | No |
| B2 No-demographics − Full | PR-AUC | −0.0002 | −0.0106 to +0.0102 | 0.9703 | 1.0000 | No |
| B2 No-demographics − Full | Brier | +0.0000 | −0.0008 to +0.0009 | 0.9722 | 1.0000 | No |
| B3 No-health − Full | ROC-AUC | +0.0049 | −0.0063 to +0.0161 | 0.3783 | 1.0000 | No |
| B3 No-health − Full | PR-AUC | +0.0042 | −0.0061 to +0.0145 | 0.4043 | 1.0000 | No |
| B3 No-health − Full | Brier | −0.0004 | −0.0013 to +0.0006 | 0.4328 | 1.0000 | No |
| B4 No-access − Full | ROC-AUC | −0.0018 | −0.0061 to +0.0025 | 0.4029 | 1.0000 | No |
| B4 No-access − Full | PR-AUC | −0.0017 | −0.0064 to +0.0031 | 0.4767 | 1.0000 | No |
| B4 No-access − Full | Brier | +0.0002 | −0.0001 to +0.0005 | 0.2321 | 0.9284 | No |
| B5 No-SES − Full | ROC-AUC | +0.0019 | −0.0041 to +0.0079 | 0.5247 | 1.0000 | No |
| B5 No-SES − Full | PR-AUC | +0.0065 | −0.0023 to +0.0154 | 0.1404 | 0.7019 | No |
| B5 No-SES − Full | Brier | −0.0006 | −0.0014 to +0.0002 | 0.1614 | 0.8072 | No |

Blocks: B1 `AGEY3X`; B2 `SEX`, `RACETHX`, `REGIONY3`, `MARRY6X`; B3
`RTHLTH6`, `MNHLTH6`; B4 `INSCOVY3`, `HAVEUS6`; B5 `POVCATY3`, `TTLPY3X`,
`EMPST6`.
