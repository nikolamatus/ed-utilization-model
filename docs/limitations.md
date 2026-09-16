# Limitations

These limitations apply regardless of the first-run decision-gate
status and regardless of which inferential tests were statistically
detected. State them whenever these results are described.

This study **demonstrates** unweighted predictive discrimination on the
MEPS Panel 24 analytic sample under a locked design. It **suggests**
that a broader pre-cutoff feature set can add incremental
discrimination beyond three-year ED history in that sample. It
**leaves unknown** whether that increment would appear in other
panels, other populations, weighted national estimates, clinical
settings, or later time periods.

---

## 1. Public-use MEPS population and representativeness

MEPS-HC samples the U.S. civilian noninstitutionalized population. It
excludes incarcerated people, active-duty military, and
institutionalized populations, and structurally undersamples people
experiencing homelessness. Panel 24 overlaps COVID-19; AHRQ documents
comparability concerns related to phone-based interviewing. Results are
not a description of all U.S. ED users.

## 2. Unweighted analytic-sample predictive metrics

All reported ROC-AUC, PR-AUC, and Brier values are unweighted sklearn
scores on the constructed analytic sample. They describe that sample,
not a survey-weighted population.

## 3. No survey-weighted national inference

`LONGWT`, `VARSTR`, and `VARPSU` were ingested and recorded. They were
not applied. The study does not produce national MEPS estimates and
does not support statements about national predictive performance.

## 4. Single-panel validation

All modeling, ablation, and inference use MEPS Panel 24 only. A random
stratified holdout on one panel is not an independent population.

## 5. No external validation

No other survey, claims file, EHR extract, or health-system dataset was
used. Transport to other data-generating processes is unknown.

## 6. No temporal validation on later panels

The outcome year is 2022 on the same panel used to form 2019–2021
predictors. Later MEPS panels were not used as a temporal test set.

## 7. Model simplicity

The production model is L2-regularized logistic regression. No tree
ensembles, survival models, or sequence models were compared after
lock. Incremental discrimination is specific to this estimator class.

## 8. Fixed hyperparameters

`C=1.0`, `max_iter=2000`, and the seeds were fixed. There was no
hyperparameter search. A different regularization strength could change
absolute metrics and, in principle, some contrasts.

## 9. Imputation strategy

Sentinels and **any other negative** are recoded to missing, then median
(numeric) or most-frequent (categorical) imputed inside each training
fold. This is single imputation, not multiple imputation, and not a
missingness model. The documented MEPS codes −1, −7, −8, and −9 are
examples, not an exhaustive list (HC-245 also contains `EMPST6` = −15).

On the analytic cohort, 16.01% of `EMPST6` values are non-usable,
overwhelmingly because employment is structurally inapplicable for
children. Those values are mode-imputed (modal category: employed).
`EMPST6` coefficients should not be interpreted as causal or
substantive employment effects. The imputer is fit on training data
only. The adult-only sensitivity is a related population check. An
explicit inapplicable category was not used.

## 10. Missingness

Raw-file non-usable rates after this recode are about 5–8% for many
candidates and 21.89% for `EMPST6`. Analytic-cohort missingness
(`outputs/missingness_analytic_cohort_v1_1.csv`) is 16.01% for
`EMPST6`, 1.27% for `HAVEUS6`, 0.06% for `RTHLTH6`, and 0.10% for
`MNHLTH6`. Other modeled predictors are complete after recode.
Missingness was not used as a predictor.

## 11. Mortality

Persons not in all four years are excluded via `YEARIND`. Thirty-seven
`YEARIND == 1` decedents remain in the primary cohort because a valid
`ERTOTY4` was observed while they were in scope. A sensitivity analysis
changed holdout ROC-AUC from 0.774 to 0.771 and did not replace the
cohort. Competing risk of death is not modeled.

## 12. Outcome definition

The primary outcome is any self- or proxy-reported ED visit in 2022
(`ERTOTY4 ≥ 1`). It is not claims-adjudicated utilization, not acuity,
and not avoidable vs unavoidable ED use.

## 13. ≥2 ED outcome not modeled

`ERTOTY4 ≥ 2` was constructed (209 events; prevalence 0.041) and was
not modeled. Whether a high-utilizer analysis is viable remains a
separate question.

## 14. Children and adults not separately modeled

Age is a single numeric predictor. Children and adults were not fit as
separate cohorts. Some predictors (employment, marital status) have
different meaning or inapplicability by age.

## 15. No clinical utility

No decision-curve, net-benefit, or intervention-impact analysis was
performed. Statistically detectable incremental discrimination is not
clinical utility.

## 16. No clinical threshold optimization

Sensitivity, specificity, precision, and recall were reported only at
probability 0.5 as exploratory descriptive metrics. No clinical cutoff
was selected or validated.

## 17. No causal interpretation

Predictor coefficients and ablation deltas are predictive associations.
Removing a block is not an intervention and does not identify a causal
effect of age, insurance, income, or health status on ED use.

## 18. No deployment validation

There is no prospective silent-mode test, workflow study, fairness
audit for deployment, or site-level implementation evaluation. The
repository is not a clinical decision-support system.

## 19. Predictor redundancy

`AGEY3X`–`MARRY6X` (η = 0.81) and `POVCATY3`–`TTLPY3X` (η = 0.60) are
associated. The locked one-hot VIF table is invalid for categoricals
because no reference level was dropped (dummy-variable trap). The
corrected drop-first diagnostic has all VIFs < 5. Pairwise η
associations remain. The diagnostic does not prove independence and
did not change the model.

## 20. Limits of block ablation

Leave-one-block-out cannot distinguish distributed independent
information from more subtle redundancy. Non-significant Family B
contrasts are not evidence that a block is unnecessary or that reduced
models are equivalent to the full model.

## 21. Limits of the repeat-level sensitivity analysis

The five repeats reuse the same underlying training sample. Collapsing
each repeat to one mean and running a *t*-test on five means (df = 4)
understates uncertainty relative to the Nadeau–Bengio correction on 25
paired fold differences. The procedure is a descriptive sensitivity
diagnostic, **not** a more conservative inferential test. Smaller
repeat-level *p*-values must not be interpreted as stronger evidence.
Repeat-level Brier significance (*p* ≈ 0.0006) does not overturn the
primary Brier result (Nadeau–Bengio *p* = 0.1110).

## 22. Generalizability to real-world healthcare systems

MEPS is a household survey, not an EHR or claims operational extract.
Coding, missingness, case-mix, and outcome ascertainment differ from
health-system data. Performance in a hospital, payer, or regional
system is unknown.

## 23. Lack of direct validated homelessness, SUD, and food-insecurity measures

The public-use file did not provide a sufficiently defensible direct
variable for homelessness, substance-use disorder, or food insecurity
for this study, so those constructs were not represented as such.
`SDAFRDHOME5` is not homelessness. SNAP purchase variables are not a
food-insecurity diagnosis. Alcohol/tobacco SAQ items are not SUD
diagnoses. None of those items were used as predictors.

## 24. Need for external / temporal validation

Any claim beyond this locked Panel 24 analysis requires a new study:
another appropriate public dataset or a later MEPS panel, specified
in advance, without recycling this first-run holdout or these p-values as if they
were external confirmation.

## 25. Adult-only ROC increment not detected (v1.1)

Restricting the original split to `AGEY3X ≥ 18` (898 children excluded)
yielded CV ΔROC +0.0194 (*p* = 0.113). The mixed-age Family A ROC
result should not be presented as an adult-only finding.

## 26. Analysis-plan provenance

The repository analysis plan entered Git on 2026-09-12 with the first
research snapshot. That is not formal preregistration, and Git order
alone does not make the plan post-hoc. See
`docs/research_chronology.md`.

---

## What this study demonstrates, suggests, and leaves unknown

**Demonstrates.** On the MEPS Panel 24 mixed-age analytic sample, under the
locked cohort, predictor set, regularized logistic model, and
plan-specified Nadeau–Bengio analysis, the full pre-cutoff feature set
had statistically detectable incremental ROC-AUC and PR-AUC versus
three-year ED history. No Family B contrast was statistically detected
after Holm correction. The adult-only ROC increment was **not**
detected.

**Suggests.** Additional pre-cutoff survey information can improve
predictive discrimination relative to ED counts alone in this mixed-age
sample. The increment does not appear to collapse when any one
documented predictor block is removed.

**Unknown.** Whether the increment is distributed independent
information or residual redundancy; whether Brier would be detected
under a different inferential choice (the plan-specified test did not
detect it); whether the ROC increment holds in adults (v1.1 did not
detect it); whether a ≥2-visit outcome is predictable; whether weighted
national estimates would agree; and whether any of this would hold in
another panel, another dataset, or a clinical system.
