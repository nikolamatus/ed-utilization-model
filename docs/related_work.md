# Related Work

This document is a targeted literature review for the present study’s
research question:

> How much additional predictive value can longitudinal health,
> utilization, access, demographic, and socioeconomic information
> provide beyond historical ED utilization alone?

It is **not** a PRISMA systematic review. Searches used PubMed, PMC,
publisher sites, and AHRQ documentation (September 2026). Search-result
snippets were not treated as sufficient evidence; abstracts or full
texts were opened before a paper was used for a substantive claim.
Absence of a paper from this review does **not** prove that no such
paper exists.

The present analysis is a predictive research study of AHRQ MEPS Panel
24 (HC-245), not a clinical deployment study. It does not claim
clinical utility, national prediction performance, causal inference, or
external validity.

---

## Search notes

Queries included combinations of: MEPS + emergency department +
prediction / longitudinal utilization; prior / previous ED visits +
future ED; incremental predictive value + ED; frequent ED use +
machine learning; ED utilization + socioeconomic / insurance
prediction; “Panel 24” / HC-245 + ED prediction; and Nadeau–Bengio
cross-validation inference.

Approximately 70 unique titles or abstracts were screened from those
searches. About 18 papers were retained as directly or strongly
relevant and are cited below. Additional AHRQ/MEPS documentation was
used for data-source context only.

---

## 1. Predicting Emergency Department Utilization

Prior research has established that future emergency-department (ED)
use is predictable to a useful degree from historical utilization and
other patient-level information, across several data types:

- **Health-system / registration data.** Wu et al. used Indiana ED
  registration data from 2008 to predict frequent use over the next two
  years (AUC 0.83–0.92 depending on the visit threshold), with baseline
  visit count among the strongest predictors ([Wu et al.,
  2016](#wu-2016)).
- **Hospital discharge records.** Pereira et al. predicted next-year
  low / medium / high ED frequency from the prior year’s California
  discharge records and reported that logistic regression and tree
  ensembles could discriminate high-frequency users ([Pereira et al.,
  2016](#pereira-2016)).
- **Administrative claims / insurance files.** Gao et al. predicted
  30-day ED revisits among Veterans Affairs (VA) patients and showed
  large gains when prior-year utilization was added to demographics
  ([Gao et al., 2018](#gao-2018)). Chiu et al. predicted next-year
  frequent ED use (≥3 or ≥5 visits) in Quebec chronic-disease adults
  ([Chiu et al., 2023](#chiu-2023)).
- **National surveys.** Stockbridge et al. used a MEPS longitudinal
  panel to relate year-1 psychological distress (and covariates,
  including year-1 ED counts) to year-2 ED use ([Stockbridge et al.,
  2014](#stockbridge-2014)). Bobashev et al. predicted ≥3 ED visits in
  the same survey year from NSDUH health and socioeconomic items
  ([Bobashev et al., 2021](#bobashev-2021)).

A large parallel literature predicts **short-horizon revisits**
(72 hours to 30 days) from encounter-level electronic health record
(EHR) data rather than calendar-year person-level utilization
([Hong et al., 2019](#hong-2019); [Montoy et al., 2019](#montoy-2019)).
Those studies establish predictability of return visits but answer a
different operational question than next-year any-ED use in a household
survey.

Reviews of frequent ED use consistently find that frequent users are a
small share of patients and a large share of visits, and that public
insurance, chronic illness, mental health and substance-use problems,
and poorer self-rated health are associated with frequent use
([Hunt et al., 2006](#hunt-2006); [Krieg et al., 2016](#krieg-2016);
[Giannouchos et al., 2019](#giannouchos-2019)). Association reviews are
not the same as incremental prediction studies.

---

## 2. Importance of Prior ED Utilization

Prior ED utilization is repeatedly identified as the strongest, or one
of the strongest, predictors of later ED use.

- Montoy et al. found that recent previous ED visits had the highest
  odds of a 14-day revisit among nearly 6.7 million index discharges,
  stronger than other patient, hospital, or community characteristics
  ([Montoy et al., 2019](#montoy-2019)).
- Chiu et al. (2020) reported that the number of previous ED visits
  was the most important associated factor for persistent frequent use
  in Quebec ([Chiu et al., 2020](#chiu-2020)).
- Chiu et al. (2023) found that previous-year ED visit count was the
  most important variable across logistic regression and several
  machine-learning models ([Chiu et al., 2023](#chiu-2023)).
- Wu et al. reported that total visits in the baseline year were a
  strong predictor of subsequent frequent use ([Wu et al.,
  2016](#wu-2016)).
- Krieg et al.’s scoping review noted that being a frequent user in
  the previous year was, in at least one included study, the only
  independent predictor of the following year’s level of ED use
  ([Krieg et al., 2016](#krieg-2016)).

Gao et al. quantified the **discrimination** contribution of
prior-year utilization: a demographics-only model had C-statistics
about 0.56, which rose to 0.75 when prior-year utilization was added
([Gao et al., 2018](#gao-2018)). That result supports treating
historical utilization as a strong baseline, not as an afterthought.

The present study therefore uses a three-year ED-history baseline
(`ERTOTY1`–`ERTOTY3`) as the primary comparator. That choice is
motivated by this literature. It is not a claim that no prior study
recognized the importance of previous visits.

---

## 3. Longitudinal Prediction and MEPS

MEPS is a nationally representative household panel with person
identifiers and annual utilization totals. It has been used for
**longitudinal association** and **expenditure prediction**, and less
often for **discrimination-focused prediction of future ED use**.

### MEPS studies of future ED use

Stockbridge, Wilson, and Pagán used MEPS Panel 14 (2009–2010;
analytic n = 9,473 adults) to examine psychological distress in 2009
and ED utilization in 2010. They used survey-weighted
negative-binomial–logit hurdle models, adjusted for demographics,
insurance, poverty, comorbidity, smoking, and **2009 ED visit count**.
Serious and even milder distress were associated with higher adjusted
odds of any 2010 ED visit ([Stockbridge et al.,
2014](#stockbridge-2014)).

What that paper establishes: a time-ordered MEPS design can relate
year-1 health and social covariates, including prior ED counts, to
year-2 any-ED use.

What it does not establish: incremental **predictive discrimination**
of a richer feature set versus an ED-history-only baseline; ROC-AUC /
PR-AUC / Brier performance; leakage-controlled machine-learning
evaluation; or results for a four-year panel predicting 2022 use.

### MEPS studies of future utilization or cost (not ED-primary)

Fleishman and Cohen used MEPS Panels 1–8 to predict being in the top
expenditure decile in year 2 from year-1 information. They compared
nested models (demographics/insurance baseline, then chronic
conditions, DCG scores, self-rated health, and functioning) and
reported c-statistics around 0.83–0.86 in derivation/validation
samples. Adding health status and functioning after condition-based
scores increased the c-statistic only slightly (0.833 to 0.836 in
derivation) ([Fleishman and Cohen, 2010](#fleishman-2010)).

That paper establishes that MEPS two-year panels support prospective
prediction and incremental model comparison — for **high cost**, not
for any-ED visits, and not with an ED-history-only baseline.

### MEPS Panel 24 / HC-245

AHRQ released HC-245 as the Panel 24 four-year longitudinal public-use
file (2019–2022), with annual ED counts `ERTOTY1`–`ERTOTY4`
([AHRQ, HC-245](#ahrq-hc245)). In the literature reviewed, **no study
was identified** that used Panel 24 / HC-245 to predict 2022 ED
utilization from 2019–2021 information.

Earlier two-year MEPS panels (for example Panel 14) have been used for
next-year ED *association* ([Stockbridge et al.,
2014](#stockbridge-2014)). Those designs differ in panel, years,
outcome framing, and evaluation.

---

## 4. Additional Demographic, Health, Access, and Socioeconomic Information

Reviews and multivariable models include demographics, insurance,
socioeconomic status, self-rated health, comorbidity, and mental
health as correlates of ED use ([Krieg et al., 2016](#krieg-2016);
[Giannouchos et al., 2019](#giannouchos-2019); [Stockbridge et al.,
2014](#stockbridge-2014); [Bobashev et al., 2021](#bobashev-2021)).
That literature shows that these domains are **associated** with ED
use. Association after adjustment is not the same as a measured
increment in predictive discrimination beyond a utilization-history
baseline.

Studies that *do* quantify incremental discrimination in related
settings include:

- **Gao et al. (2018).** Demographics only → C ≈ 0.56; plus prior-year
  utilization → C = 0.748; plus comorbidities → C ≈ 0.76–0.77 on a
  30-day VA revisit outcome ([Gao et al., 2018](#gao-2018)).
  Utilization added most of the lift; comorbidities added a smaller
  further increment. The baseline was demographics, not
  utilization-only. The cohort was VA ED users, not a household survey
  of any-ED use.
- **Pereira et al. (2016).** Sequentially added prior utilization,
  demographics, distance, and clinical features when predicting
  next-year ED-frequency class in California discharge data
  ([Pereira et al., 2016](#pereira-2016)). This is an explicit
  feature-group comparison, but not MEPS and not an any-ED binary
  outcome with a locked ED-history-only logistic baseline.
- **Fleishman and Cohen (2010).** Incremental clinical and health
  information beyond a demographic/insurance baseline for high-cost
  prediction in MEPS ([Fleishman and Cohen, 2010](#fleishman-2010)).
- **Hong et al. (2019).** For 72-hour/9-day return, XGBoost on a full
  EHR feature set improved test AUC only modestly over administrative
  or triage-time subsets (for example 0.76 vs 0.73 for 72-hour return)
  ([Hong et al., 2019](#hong-2019)). That is incremental clinical
  information, not an ED-history-only vs survey-domain design.
- **Stockbridge et al. (2014).** Distress remained associated with
  next-year ED use after adjustment for 2009 ED counts and other
  covariates, but no nested AUC comparison versus ED history alone was
  reported ([Stockbridge et al., 2014](#stockbridge-2014)).

**Particular question.** Among papers opened for this review, **no
directly matching study was identified** that (i) used prior ED
history **alone** as an explicit predictive baseline, (ii) added
longitudinal demographic, health, access, and socioeconomic
information available before a defined cutoff, (iii) predicted a
defined future individual-level ED event, and (iv) reported a
quantitative discrimination comparison of those two models.

Studies that are close but not matching are documented in
[Section 8](#8-closest-prior-studies). This is not a claim that no
such study exists.

---

## 5. Machine Learning for ED Utilization Prediction

A substantial machine-learning literature predicts frequent ED use or
early return.

Chiu et al. compared logistic regression with gradient boosting,
naïve Bayes, neural networks, and random forests for next-year
frequent use among 451,775 Quebec ED users with chronic disease. Most
models performed similarly; random forests with a binarized outcome
performed worse. Previous-year ED visits dominated variable
importance. The authors concluded that algorithm innovations may only
slightly refine predictions and that **access to other variables may
be more helpful** ([Chiu et al., 2023](#chiu-2023)).

Pereira et al. likewise found logistic regression competitive with
decision trees and AdaBoost for discriminating high-frequency users
([Pereira et al., 2016](#pereira-2016)). Hong et al. used gradient
boosting on a high-dimensional EHR feature set for 72-hour and 9-day
return ([Hong et al., 2019](#hong-2019)). Safaripour and Lim compared
several classifiers on Korean Health Panel data and reported large
algorithm gaps versus logistic regression ([Safaripour and Lim,
2022](#safaripour-2022)); that paper is an algorithm-comparison study
of frequent-user classification and did not isolate incremental value
beyond an ED-history baseline. Its design is not treated here as
evidence that complex models are generally required.

Taken together, prior ED-prediction work has shown that:

- algorithm choice *can* matter, but often does not once a strong
  utilization feature is present;
- prior utilization can dominate prediction;
- richer feature sets can add value, sometimes modestly;
- simple models can perform competitively;
- additional information can be more important than algorithm
  complexity ([Chiu et al., 2023](#chiu-2023); [Gao et al.,
  2018](#gao-2018)).

The present project therefore treats **incremental information value**,
not algorithm competition, as the primary scientific question. Regularized
logistic regression is used as a locked estimator, not as a claim that
no other algorithm could perform as well or better.

---

## 6. What Remains Unclear

To the extent identified in this review, several points remain unclear:

1. How much **predictive discrimination** (ROC-AUC, PR-AUC, Brier)
   additional pre-cutoff survey domains add **beyond a multi-year
   ED-history-only model** for next-year any-ED use in a public U.S.
   household panel.
2. Whether that increment, if present, is concentrated in one
   predictor block or remains after leave-one-block-out comparisons.
3. How such an increment behaves under **repeated resampling** and
   **corrected inference** that does not treat cross-validation folds
   as independent observations ([Nadeau and Bengio,
   2003](#nadeau-2003)).
4. Whether findings from VA, EHR, or claims frequent-user models
   transport to unweighted MEPS analytic-sample prediction.
5. Whether Panel 24 / 2019–2022 results, which overlap COVID-19
   interviewing changes documented by AHRQ, match earlier MEPS panels.

---

## 7. Positioning of the Present Study

Prior research has established that future ED utilization can be
predicted from historical utilization and other patient-level
characteristics, and that prior ED use is typically a dominant
predictor.

The present study focuses more narrowly on the **incremental
predictive value of information beyond longitudinal ED utilization
history**, using a public four-year MEPS cohort (Panel 24, HC-245)
and an explicitly time-ordered cutoff (end of 2021 → 2022 any-ED
visit).

The analysis evaluates whether additional pre-cutoff demographic,
health, access, and socioeconomic information improves discrimination
beyond a strong three-year ED-history baseline, rather than primarily
asking which machine-learning algorithm performs best.

The study further examines whether observed incremental performance is
robust across repeated stratified cross-validation and a
pre-registered Nadeau–Bengio test, and whether removal of
pre-specified predictor blocks produces statistically detectable
performance changes.

This is best understood as an **incremental empirical and
methodological contribution** to an existing prediction literature,
not as the first study of ED prediction, the first MEPS ED study, or
the first machine-learning ED model.

Individual design elements (holdout evaluation, cross-validation,
ablation, leakage control, calibration tables) are not claimed to be
individually novel. The intended distinction is that they are
combined, pre-specified where noted, and applied to a public
longitudinal MEPS file with an explicit utilization-history baseline.

---

## 8. Closest Prior Studies

Ranked by **methodological similarity** to the present design
(longitudinal person-level future ED outcome; role of prior ED
history; incremental comparison of information; public or
population data), not by journal prestige.

### 1. Gao, Pellerin, and Kaminsky (2018)

**What this paper already establishes.** In a VA ED-user cohort,
prior-year utilization added a large increment in C-statistic over
demographics alone when predicting 30-day revisit; comorbidities added
a smaller further increment. Temporal split: FY2013 predictors,
FY2014 outcome.

**What this project does differently.** MEPS household panel; any-ED
in the next calendar year among persons with four-year follow-up, not
30-day revisit among recent ED users; explicit **ED-history-only**
baseline rather than demographics-first nesting; three years of ED
counts; access/SES/health blocks; repeated CV and Nadeau–Bengio
inference.

**What this project does not establish that the paper already
established.** Performance in a VA health-system population;
usefulness of a comorbidity classification system for 30-day revisit
risk; operational targeting of “frequent flyers” in that system.

### 2. Stockbridge, Wilson, and Pagán (2014)

**What this paper already establishes.** MEPS two-year panel data can
be used in a time-ordered design (year-1 distress and covariates,
including year-1 ED counts → year-2 ED use). Distress is associated
with next-year any-ED use after survey-weighted adjustment.

**What this project does differently.** Four-year Panel 24 / 2019–2022;
primary question is incremental discrimination beyond three-year ED
history; reports ROC/PR/Brier and inferential tests rather than
adjusted odds ratios as the main result; does not focus on the K6
distress scale.

**What this project does not establish that the paper already
established.** Nationally weighted association of psychological
distress with next-year ED volume; hurdle-model decomposition of any
use versus count among users.

### 3. Chiu, Courteau, Dufour, Vanasse, and Hudon (2023)

**What this paper already establishes.** In a large Quebec
chronic-disease ED-user cohort, previous-year ED visits dominate
frequent-user prediction; several machine-learning algorithms do not
outperform logistic regression; additional variables may matter more
than new algorithms.

**What this project does differently.** Predicts any ED visit, not
frequent use (≥3 or ≥5); uses MEPS rather than billing/hospital
registers; locks a single estimator and tests information increments
and block removal.

**What this project does not establish that the paper already
established.** Comparative algorithm performance on a 450,000-person
administrative cohort; prediction of frequent use among people who
already had an ED visit and a chronic-disease diagnosis.

### 4. Pereira et al. (2016)

**What this paper already establishes.** Next-year ED-frequency class
can be predicted from the prior year of California discharge data.
Feature groups (prior utilization, demographics, distance, clinical)
can be added sequentially. Logistic regression can compete with tree
ensembles.

**What this project does differently.** Survey rather than hospital
discharge data; binary any-ED outcome; three-year history; no
distance-to-ED feature; inferential comparison of nested information
sets rather than multi-class accuracy alone.

**What this project does not establish that the paper already
established.** Multi-class frequency prediction; geographic distance
features; temporal validation across 2011–2013 California discharge
years.

### 5. Wu, Grannis, Xu, and Finnell (2016)

**What this paper already establishes.** Registration-only features,
including baseline visit count, can predict subsequent frequent ED
use with high AUC at high visit thresholds.

**What this project does differently.** Person-level household survey;
any-ED rather than high-threshold frequent use; richer
socioeconomic/health items than registration data; does not use
chief-complaint syndromes or distance.

**What this project does not establish that the paper already
established.** Feasibility of a registration-data screening algorithm
across 96 Indiana EDs; PPV at extreme frequent-use thresholds.

### 6. Fleishman and Cohen (2010)

**What this paper already establishes.** MEPS two-year panels support
prospective prediction and incremental comparison of clinical and
health-status information for **high-cost** cases, with a later-panel
validation set.

**What this project does differently.** Outcome is 2022 any-ED visit,
not top-decile expenditure; baseline is ED history, not
age/sex/insurance; no DCG scores; unweighted analytic-sample
metrics.

**What this project does not establish that the paper already
established.** Survey-weighted national high-cost prediction;
external validation on later MEPS panels; incremental value of DCG
scores.

### 7. Montoy, Tamayo-Sarver, Miller, Baer, and Peabody (2019)

**What this paper already establishes.** Previous ED use is a stronger
predictor of short-term bounceback than other measured patient,
hospital, or community factors in a very large multi-state discharge
sample.

**What this project does differently.** Calendar-year prediction
horizon; incremental discrimination metrics versus an ED-history
model; MEPS.

**What this project does not establish that the paper already
established.** 14-day revisit risk among discharged ED patients at
scale; diagnosis-specific odds (cellulitis, alcohol, heart failure).

### 8. Chiu et al. (2020)

**What this paper already establishes.** Persistent frequent ED use
among people with chronic conditions is strongly associated with
previous ED visits and with socioeconomic and comorbidity factors.

**What this project does differently.** Prediction and incremental
discrimination rather than regression association for persistent
frequent use; includes people with no prior-year ED visit in the
analytic cohort.

**What this project does not establish that the paper already
established.** Three-year persistence of frequent use in Quebec
administrative data.

---

## Structured evidence table

Fields that could not be verified from the opened abstract or paper
are marked **not verified**. DOIs are listed only when seen on a
publisher, PubMed, or PMC page.

### Stockbridge, Wilson, and Pagán (2014)

| Field | Content |
|---|---|
| Authors | Erica L. Stockbridge, Fernando A. Wilson, José A. Pagán |
| Year | 2014 |
| Title | Psychological Distress and Emergency Department Utilization in the United States: Evidence from the Medical Expenditure Panel Survey |
| Journal | Academic Emergency Medicine |
| DOI | 10.1111/acem.12369 (verified) |
| URL | https://doi.org/10.1111/acem.12369 |
| Dataset | MEPS Panel 14 (2009–2010) |
| Study population | U.S. civilian noninstitutionalized adults with SAQ in both years |
| Sample size | 9,473 (methods); abstract also states 9,743 |
| Prediction target | Any ED visit and ED visit count in 2010 |
| Prediction horizon | Next calendar year |
| Predictors available before prediction | 2009 K6 distress, demographics, insurance, poverty, comorbidity, smoking, 2009 ED count |
| Role of prior ED utilization | Covariate (2009 ED visits) |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | No (adjusted association, not nested AUC) |
| Socioeconomic/access variables | Yes (poverty, insurance) |
| Machine learning | No (survey-weighted hurdle models) |
| Validation design | Single-panel observational model; complex-survey inference |
| Primary performance metrics | Adjusted odds ratios / rate ratios |
| Main conclusion | Distress, including below the “serious” threshold, is associated with next-year ED use |
| Relationship to this project | Closest identified **MEPS longitudinal next-year ED** study |
| Limitations/relevance | Not a discrimination comparison versus ED history alone |

### Fleishman and Cohen (2010)

| Field | Content |
|---|---|
| Authors | John A. Fleishman, Joel W. Cohen |
| Year | 2010 |
| Title | Using Information on Clinical Conditions to Predict High-Cost Patients |
| Journal | Health Services Research |
| DOI | 10.1111/j.1475-6773.2009.01080.x (verified) |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC2838159/ |
| Dataset | MEPS Panels 1–8 (1996–2003 cohorts) |
| Study population | Two-year MEPS respondents with positive longitudinal weight |
| Sample size | Derivation N = 52,918 (Panels 1–4); validation N = 61,155 (Panels 5–8) |
| Prediction target | Top 10% of year-2 expenditures |
| Prediction horizon | Next year of a two-year panel |
| Predictors available before prediction | Year-1 demographics, insurance, conditions, DCG, health status, functioning |
| Role of prior ED utilization | Not an ED-history baseline (expenditure models; ED events contribute to cost) |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | Yes (nested models / c-statistic) |
| Socioeconomic/access variables | Insurance; age/sex baseline |
| Machine learning | No (weighted logistic regression) |
| Validation design | Later MEPS panels as validation |
| Primary performance metrics | c-statistic, BIC, sensitivity, PPV |
| Main conclusion | Condition-based information predicts high-cost cases well; health status adds little once conditions are included |
| Relationship to this project | Closest identified **MEPS incremental prediction** paper, different outcome |
| Limitations/relevance | Not an ED-utilization outcome |

### Gao, Pellerin, and Kaminsky (2018)

| Field | Content |
|---|---|
| Authors | Kelly Gao, Gene Pellerin, Laurence Kaminsky |
| Year | 2018 |
| Title | Predicting 30-Day Emergency Department Revisits |
| Journal | The American Journal of Managed Care |
| DOI | not verified on a publisher DOI page in this review |
| URL | https://www.ajmc.com/view/predicting-30day-emergency-department-revisits (verified); PubMed 30452204 |
| Dataset | Administrative data, 4 VA hospitals, upstate New York |
| Study population | Patients with ED visits, FY2013–FY2014 |
| Sample size | 22,734 |
| Prediction target | Any 30-day ED revisit in FY2014 |
| Prediction horizon | 30 days after ED discharge; predictors from prior fiscal year |
| Predictors available before prediction | Demographics, SES/insurance, prior-year utilization and cost, CCS comorbidities |
| Role of prior ED utilization | Core feature block (prior-year ED visits/revisits and other utilization) |
| Explicit ED-history baseline | No; demographics-only then + utilization then + comorbidity |
| Incremental predictive value tested | Yes (C-statistic: ~0.56 → 0.748 → ~0.76–0.77) |
| Socioeconomic/access variables | Yes (income, insurance, homelessness indicator) |
| Machine learning | No (logistic regression) |
| Validation design | Split sample; FY2013 → FY2014 |
| Primary performance metrics | C-statistic |
| Main conclusion | Prior-year utilization greatly improves 30-day revisit prediction over demographics; comorbidities add a smaller increment |
| Relationship to this project | Closest identified **incremental-discrimination** ED paper |
| Limitations/relevance | VA ED users; 30-day revisit; not utilization-only baseline first |

### Chiu, Courteau, Dufour, Vanasse, and Hudon (2023)

| Field | Content |
|---|---|
| Authors | Yohann M. Chiu, Josiane Courteau, Isabelle Dufour, Alain Vanasse, Catherine Hudon |
| Year | 2023 |
| Title | Machine learning to improve frequent emergency department use prediction: a retrospective cohort study |
| Journal | Scientific Reports |
| DOI | 10.1038/s41598-023-27568-6 (verified) |
| URL | https://doi.org/10.1038/s41598-023-27568-6 |
| Dataset | Quebec RAMQ medical/administrative files |
| Study population | Adults with ≥1 ED visit in 2012–2013 and ≥1 listed chronic condition; remote areas and deaths in the outcome year excluded |
| Sample size | 451,775 ED users |
| Prediction target | ≥3 and ≥5 ED visits in the year after index |
| Prediction horizon | 1 year after a randomly assigned index ED visit |
| Predictors available before prediction | Demographics, deprivation, insurance plan status, prior hospitalization, prior-year ED visits, Charlson, listed diagnoses |
| Role of prior ED utilization | Most important predictor |
| Explicit ED-history baseline | No (full feature set compared across algorithms) |
| Incremental predictive value tested | Not as nested information models; variable importance emphasized |
| Socioeconomic/access variables | Yes (deprivation, public drug-plan status) |
| Machine learning | Yes (LR, GBM, NB, NN, RF) |
| Validation design | Predictive comparison with AUC and related metrics (see paper for split details) |
| Primary performance metrics | ROC-AUC, sensitivity, specificity, PPV, NPV |
| Main conclusion | No algorithm clearly outperformed the others; prior ED visits dominated; other variables may help more than new algorithms |
| Relationship to this project | Strongest identified justification for focusing on **information**, not algorithms |
| Limitations/relevance | Frequent-use outcome among prior ED users with chronic disease |

### Pereira, Singh, Hon, McKelvey, De Cock, and Sushmita (2016)

| Field | Content |
|---|---|
| Authors | Mayana Pereira, Vikhyati Singh, Chun Pan Hon, T. Greg McKelvey, Martine De Cock, Shanu Sushmita |
| Year | 2016 |
| Title | Predicting Future Frequent Users of Emergency Departments in California State |
| Journal | ACM BCB ’16 proceedings |
| DOI | 10.1145/2975167.2985845 (verified on the paper PDF) |
| URL | https://faculty.washington.edu/mdecock/papers/mpereira2016a.pdf |
| Dataset | California OSHPD hospital discharge records, 2009–2013 |
| Study population | Patients with ED visits in the source files |
| Sample size | not verified in the opened text |
| Prediction target | Next-year low (≤1), medium (2–4), or high (≥5) ED frequency |
| Prediction horizon | Coming 12 months |
| Predictors available before prediction | Prior-year admissions/ED visits, age/sex/race, distance, comorbidities/severity |
| Role of prior ED utilization | Explicit feature group; sequential addition studied |
| Explicit ED-history baseline | Partial (utilization group added/compared with other groups) |
| Incremental predictive value tested | Yes (feature-group expansion) |
| Socioeconomic/access variables | Distance to ED; race/demographics; not a full SES block |
| Machine learning | Yes (LR, decision trees, AdaBoost) |
| Validation design | Train 2009–2010; test 2011–2013 |
| Primary performance metrics | Discrimination for frequency classes (AUC/sensitivity discussed) |
| Main conclusion | Models discriminate high-frequency users; results stable across test years; extreme frequency classes easier than moderate |
| Relationship to this project | Close **longitudinal feature-group** design on hospital data |
| Limitations/relevance | Conference paper; not MEPS; not any-ED binary |

### Wu, Grannis, Xu, and Finnell (2016)

| Field | Content |
|---|---|
| Authors | Jianmin Wu, Shaun J. Grannis, Huiping Xu, John T. Finnell |
| Year | 2016 |
| Title | A practical method for predicting frequent use of emergency department care using routinely available electronic registration data |
| Journal | BMC Emergency Medicine |
| DOI | 10.1186/s12873-016-0076-3 (verified) |
| URL | https://doi.org/10.1186/s12873-016-0076-3 |
| Dataset | Indiana Public Health Emergency Surveillance System registration data, 96 EDs |
| Study population | Linked unique ED patients, 2008–2010 |
| Sample size | Prior descriptive paper cited 2.8 million patients / 7.4 million visits; model-specific n not separately verified here |
| Prediction target | Frequent use over the subsequent two years (thresholds from 8 to 16+ visits) |
| Prediction horizon | 2009–2010 from 2008 baseline |
| Predictors available before prediction | Age, sex, proximity, baseline visit count, chief-complaint syndromes |
| Role of prior ED utilization | Strong predictor (baseline-year visits) |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | Not as a published utilization-only vs full AUC table in the opened text |
| Socioeconomic/access variables | Distance; not income/insurance |
| Machine learning | No (multivariable logistic regression) |
| Validation design | Discrimination via ROC; not a later-state external validation |
| Primary performance metrics | AUC, sensitivity, PPV |
| Main conclusion | Registration data can predict future frequent use with acceptable to high AUC |
| Relationship to this project | Close **future frequent-use** prediction with prior visits as a leading feature |
| Limitations/relevance | Registration-only; high-threshold frequent use |

### Hong, Haimovich, and Taylor (2019)

| Field | Content |
|---|---|
| Authors | Woo Suk Hong, Adrian Daniel Haimovich, Richard Andrew Taylor |
| Year | 2019 |
| Title | Predicting 72-hour and 9-day return to the emergency department using machine learning |
| Journal | JAMIA Open |
| DOI | 10.1093/jamiaopen/ooz019 (verified) |
| URL | https://pmc.ncbi.nlm.nih.gov/articles/PMC6951979/ |
| Dataset | Single-center adult ED EHR (Yale; two EDs) |
| Study population | Adult ED discharges |
| Sample size | 330,631 discharges |
| Prediction target | 72-hour and 9-day ED return |
| Prediction horizon | 72 hours and 9 days after discharge |
| Predictors available before prediction | Administrative subset, triage-time subset, or ~1,500 EHR variables including prior ED visits, vitals, labs, medications, diagnoses |
| Role of prior ED utilization | High information gain (prior ED visits and admissions) |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | Yes, in a different nesting: administrative vs triage vs full EHR (small AUC gains; full XGBoost 0.76 / 0.75 vs administrative XGBoost 0.73 / 0.74) |
| Socioeconomic/access variables | Insurance status among risk factors |
| Machine learning | Yes (logistic regression and XGBoost) |
| Validation design | Held-out test set; DeLong CIs |
| Primary performance metrics | Test AUC 0.69–0.76 depending on model and horizon |
| Main conclusion | Early return is predictable; adding comprehensive clinical data yields small but statistically significant AUC gains over administrative data; prior utilization remains informative |
| Relationship to this project | Example of **short-horizon EHR** prediction, not next-year survey prediction |
| Limitations/relevance | Different horizon, data, and target |

### Montoy, Tamayo-Sarver, Miller, Baer, and Peabody (2019)

| Field | Content |
|---|---|
| Authors | Juan Carlos C. Montoy, Joshua H. Tamayo-Sarver, Gregg Miller, Amy Baer, Christopher Peabody |
| Year | 2019 |
| Title | Predicting Emergency Department “Bouncebacks”: A Retrospective Cohort Analysis |
| Journal | Western Journal of Emergency Medicine |
| DOI | 10.5811/westjem.2019.8.43221 (verified) |
| URL | https://doi.org/10.5811/westjem.2019.8.43221 |
| Dataset | Administrative data from a physician partnership; 80 hospitals in 7 states |
| Study population | Discharged ED patients, July 2014–June 2016 |
| Sample size | 6,699,717 index visits |
| Prediction target | 14-day return visit |
| Prediction horizon | 14 days |
| Predictors available before prediction | Patient, visit, hospital, and community characteristics; previous ED visits |
| Role of prior ED utilization | Strongest predictor (OR ≈ 3.06 for frequent-visitor status) |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | No nested AUC versus history-only |
| Socioeconomic/access variables | Public insurance; community characteristics |
| Machine learning | No (multivariable logistic regression) |
| Validation design | Observational cohort; not a locked ML holdout |
| Primary performance metrics | Odds ratios; 12.6% 14-day revisit risk |
| Main conclusion | Previous ED use is the strongest predictor of short-term revisit |
| Relationship to this project | Strong evidence for a utilization-history baseline |
| Limitations/relevance | Short horizon; association/prediction of bouncebacks |

### Bobashev, Warren, and Wu (2021)

| Field | Content |
|---|---|
| Authors | Georgiy Bobashev, Lauren Klein Warren, Li-Tzy Wu |
| Year | 2021 |
| Title | Predictive model of multiple emergency department visits among adults: analysis of the data from the National Survey of Drug Use and Health (NSDUH) |
| Journal | BMC Health Services Research |
| DOI | 10.1186/s12913-021-06221-w (verified via publisher/PubMed context) |
| URL | https://pubmed.ncbi.nlm.nih.gov/33766009/ |
| Dataset | NSDUH 2015–2018 public-use files |
| Study population | Adults ≥18 years |
| Sample size | not verified in the opened abstract |
| Prediction target | ≥3 ED visits in the past 12 months |
| Prediction horizon | Same-year recall (not a future window after a cutoff) |
| Predictors available before prediction | Concurrent survey demographics, income, health, substance use, mental health |
| Role of prior ED utilization | Outcome is past-year ED count; not a lagged ED-history baseline |
| Explicit ED-history baseline | No |
| Incremental predictive value tested | Algorithm comparison, not utilization-only vs rich lagged features |
| Socioeconomic/access variables | Yes (income and related items) |
| Machine learning | Yes (regression, trees, random forests) |
| Validation design | Models compared on independent yearly datasets; test AUC up to ~0.80 |
| Primary performance metrics | ROC-AUC |
| Main conclusion | Self-rated health, mental-health symptoms, income, and chronic conditions predict multiple past-year ED visits in a national survey |
| Relationship to this project | National-survey **prediction** of multiple ED visits; not future-from-past |
| Limitations/relevance | Contemporaneous predictors and outcome; leakage relative to a cutoff design |

### Additional strongly relevant papers (shorter entries)

| Paper | Why relevant | Not a match because |
|---|---|---|
| Chiu et al., 2020, *PLOS One*, DOI 10.1371/journal.pone.0229022 | Previous ED visits dominate persistent frequent use; SES and comorbidity associated | Association/odds ratios; frequent-use persistence, not any-ED incremental AUC |
| Krieg et al., 2016, *BMC Health Serv Res*, DOI 10.1186/s12913-016-1852-1 | Scoping review: prior frequent use often predicts later frequent use | Review, not a new incremental experiment |
| Giannouchos et al., 2019, *J Eval Clin Pract*, DOI 10.1111/jep.13137 | U.S. frequent-user characteristics after ACA-era studies | Review of characteristics, not nested prediction |
| Hunt et al., 2006, *Ann Emerg Med*, DOI 10.1016/j.annemergmed.2005.12.030 | Foundational frequent-user epidemiology | Not a prospective incremental prediction study |
| Safaripour and Lim, 2022, *Health Informatics J*, DOI 10.1177/14604582221106396 | Health-panel ML vs logistic regression for frequent users | Algorithm comparison; Korean Health Panel; not ED-history incremental design |
| Nadeau and Bengio, 2003, *Machine Learning*, DOI 10.1023/A:1024068626366 | Corrected variance for resampled generalization-error comparisons | Methodology only |

---

## References

AHRQ. *MEPS HC-245: Panel 24, 4-Year Longitudinal Public Use File*.
https://meps.ahrq.gov/data_stats/download_data/pufs/h245/h245doc.shtml
{#ahrq-hc245}

Bobashev, G., Warren, L. K., & Wu, L.-T. (2021). Predictive model of
multiple emergency department visits among adults: analysis of the
data from the National Survey of Drug Use and Health (NSDUH). *BMC
Health Services Research*.
https://pubmed.ncbi.nlm.nih.gov/33766009/
DOI 10.1186/s12913-021-06221-w
{#bobashev-2021}

Chiu, Y. M., Courteau, J., Dufour, I., Vanasse, A., & Hudon, C.
(2023). Machine learning to improve frequent emergency department use
prediction: a retrospective cohort study. *Scientific Reports, 13*,
1981. https://doi.org/10.1038/s41598-023-27568-6
{#chiu-2023}

Chiu, Y. M., Vanasse, A., Courteau, J., Chouinard, M.-C., Dubois,
M.-F., Dubuc, N., Elazhary, N., Dufour, I., & Hudon, C. (2020).
Persistent frequent emergency department users with chronic
conditions: A population-based cohort study. *PLOS ONE*.
https://doi.org/10.1371/journal.pone.0229022
{#chiu-2020}

Fleishman, J. A., & Cohen, J. W. (2010). Using information on
clinical conditions to predict high-cost patients. *Health Services
Research, 45*(2), 532–552.
https://doi.org/10.1111/j.1475-6773.2009.01080.x
{#fleishman-2010}

Gao, K., Pellerin, G., & Kaminsky, L. (2018). Predicting 30-day
emergency department revisits. *The American Journal of Managed Care,
24*(11), e358–e364.
https://www.ajmc.com/view/predicting-30day-emergency-department-revisits
PubMed 30452204. Publisher DOI not independently verified in this
review.
{#gao-2018}

Giannouchos, T. V., Kum, H.-C., Foster, M., & Ohsfeldt, R. L.
(2019). Characteristics and predictors of adult frequent emergency
department users in the United States: A systematic literature
review. *Journal of Evaluation in Clinical Practice, 25*(3), 420–433.
https://doi.org/10.1111/jep.13137
{#giannouchos-2019}

Hong, W. S., Haimovich, A. D., & Taylor, R. A. (2019). Predicting
72-hour and 9-day return to the emergency department using machine
learning. *JAMIA Open, 2*(3), 346–352.
https://doi.org/10.1093/jamiaopen/ooz019
{#hong-2019}

Hunt, K. A., Weber, E. J., Showstack, J. A., Colby, D. C., &
Callaham, M. L. (2006). Characteristics of frequent users of
emergency departments. *Annals of Emergency Medicine, 48*(1), 1–8.
https://doi.org/10.1016/j.annemergmed.2005.12.030
{#hunt-2006}

Krieg, C., Hudon, C., Chouinard, M.-C., et al. (2016). Individual
predictors of frequent emergency department use: a scoping review.
*BMC Health Services Research, 16*, 594.
https://doi.org/10.1186/s12913-016-1852-1
{#krieg-2016}

Montoy, J. C. C., Tamayo-Sarver, J. H., Miller, G. A., Baer, A. B.,
& Peabody, C. R. (2019). Predicting emergency department
“bouncebacks”: A retrospective cohort analysis. *Western Journal of
Emergency Medicine*.
https://doi.org/10.5811/westjem.2019.8.43221
{#montoy-2019}

Nadeau, C., & Bengio, Y. (2003). Inference for the generalization
error. *Machine Learning, 52*, 239–281.
https://doi.org/10.1023/A:1024068626366
{#nadeau-2003}

Pereira, M., Singh, V., Hon, C. P., McKelvey, T. G., De Cock, M., &
Sushmita, S. (2016). Predicting future frequent users of emergency
departments in California State. In *Proceedings of the 7th ACM
International Conference on Bioinformatics, Computational Biology,
and Health Informatics* (BCB ’16).
https://doi.org/10.1145/2975167.2985845
{#pereira-2016}

Safaripour, R., & Lim, H. J. (2022). Comparative analysis of machine
learning approaches for predicting frequent emergency department
visits. *Health Informatics Journal*.
https://doi.org/10.1177/14604582221106396
{#safaripour-2022}

Stockbridge, E. L., Wilson, F. A., & Pagán, J. A. (2014).
Psychological distress and emergency department utilization in the
United States: Evidence from the Medical Expenditure Panel Survey.
*Academic Emergency Medicine*.
https://doi.org/10.1111/acem.12369
{#stockbridge-2014}

Wu, J., Grannis, S. J., Xu, H., & Finnell, J. T. (2016). A practical
method for predicting frequent use of emergency department care
using routinely available electronic registration data. *BMC
Emergency Medicine, 16*, 12.
https://doi.org/10.1186/s12873-016-0076-3
{#wu-2016}

### TODO (bibliographic completeness)

- Confirm Gao et al. (2018) publisher DOI if a journal style requires
  it (PMID 30452204 and the AJMC URL are verified).
- If Bouckaert & Frank is discussed in a later manuscript, add a
  complete citation from the original paper; it is not implemented in
  this repository and is not used as a source here.
