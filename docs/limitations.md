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

Sentinels and other negatives are recoded to missing, then median
(numeric) or most-frequent (categorical) imputed inside each training
fold. This is single imputation, not multiple imputation, and not a
missingness model.

## 10. Missingness

Raw-file non-usable rates after sentinel recode are about 5–8% for many
candidates and 21.89% for `EMPST6`. Analytic-cohort missingness was
audited in detail only for `RTHLTH6` (0.06%) and `MNHLTH6` (0.10%).
Employment and some health items are inapplicable for children and
become missing after recode. Missingness was not used as a predictor.

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
associated. Numeric VIFs were below 5; one-hot VIFs are infinite by
encoding design. The diagnostic does not prove independence and did not
change the model.

## 20. Limits of block ablation

Leave-one-block-out cannot distinguish distributed independent
information from more subtle redundancy. Non-significant Family B
contrasts are not evidence that a block is unnecessary or that reduced
models are equivalent to the full model.

## 21. Limits of the repeat-level sensitivity analysis

The five repeat-level means are a resampling unit (df = 4), not five
independent population samples. The test is an additional sensitivity
analysis. Where it disagrees with the pre-registered Nadeau–Bengio
Brier result, the pre-specified Brier result stands.

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
another appropriate public dataset or a later MEPS panel, pre-specified
in advance, without recycling this holdout or these p-values as if they
were external confirmation.

---

## What this study demonstrates, suggests, and leaves unknown

**Demonstrates.** On the MEPS Panel 24 analytic sample, under the
locked cohort, predictor set, regularized logistic model, and
pre-specified Nadeau–Bengio analysis, the full pre-cutoff feature set
had statistically detectable incremental ROC-AUC and PR-AUC versus
three-year ED history. No Family B contrast was statistically detected
after Holm correction.

**Suggests.** Additional pre-cutoff survey information can improve
predictive discrimination relative to ED counts alone in this sample.
The increment does not appear to collapse when any one pre-specified
block is removed.

**Unknown.** Whether the increment is distributed independent
information or residual redundancy; whether Brier would be detected
under a different inferential choice (the pre-specified test did not
detect it); whether children and adults differ; whether a ≥2-visit
outcome is predictable; whether weighted national estimates would
agree; and whether any of this would hold in another panel, another
dataset, or a clinical system.
