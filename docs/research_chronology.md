# Research chronology

This document distinguishes **research chronology**, **file chronology**,
and **Git/repository chronology**. They are not the same.

Git records when files entered this repository. It does **not**, by
itself, establish when the researcher conceived the study, drafted an
analysis plan locally, or ran code outside version control.

A file’s first Git commit is the date that file was **incorporated into
this repository**. It is not automatically the file’s creation date.

Formal preregistration (for example OSF or ClinicalTrials.gov) is a
separate claim from “a written analysis plan existed.” This study has a
**documented analysis plan** in the repository. It is **not** described
here as formally preregistered.

---

## Evidence inspected

| Source | What it can show | What it cannot show |
| --- | --- | --- |
| `git log` | When commits entered this repo (all on 2026-09-12) | When files were first authored locally |
| First research commit `12733c6` | Plan file, code, and `outputs/` entered Git together | Whether the plan was written before the analysis |
| File contents / locked CSVs | What the analysis actually did | Calendar dates of local drafts |
| ChatGPT share `https://chatgpt.com/share/6aa9dcde-30bc-83e8-b26e-4862e1d63c53` | A provenance **lead**: the shared page contains discussion of MEPS Panel 24, Family A, Nadeau–Bengio, and block ablation | An independently verified plan-creation date. Fetch metadata `capturedAt` is 2026-09-16. Other dates on the page are product/UI changelog dates, not message timestamps. Share `create_time` converted to 2026-09-16 00:03 UTC, after repository incorporation. |
| Researcher recollection | Claim that the plan was written outside Git before repository initialization | Independent corroboration of that date |
| `docs/pre_registration_block_ablation_plan.md` | Stated status: locked before B4/B5 ablation; filename uses “pre-registration” | Formal registry deposit |

No timestamps were invented. Git history was not rewritten.

---

## Four dates/concepts

| Concept | Best-supported statement | Status |
| --- | --- | --- |
| 1. Research-plan creation | Researcher recollection: drafted locally (and formatted with ChatGPT assistance) before Git existed. Independent calendar date **not established**. | Researcher recollection; uncertain exact date |
| 2. Git/repository incorporation of the plan | `docs/pre_registration_block_ablation_plan.md` first appears in `12733c6` (2026-09-12 16:11:14 −0600). | Independently documented by Git |
| 3. Original analysis / code development | The same commit already contains pipeline code and locked `outputs/` (holdout metrics, repeated CV, ablations, inference). Local development before that commit is plausible and **not dated by Git**. | Supported by repository evidence for incorporation; local pre-Git work is recollection/uncertain |
| 4. Later analyses or extensions | Same-day documentation/release commits after `12733c6` (scipy note, public-release hardening, manuscript, v1.0.0 version alignment). This v1.1 revision is a later reporting/sensitivity pass and is **not** part of the original locked analysis. | Supported by repository evidence |

---

## Chronology table

| Event | Evidence | Approximate/Exact date | Status | Interpretation |
| --- | --- | --- | --- | --- |
| Analysis-plan drafting outside Git | Researcher recollection; ChatGPT share as a lead | Unknown | Researcher recollection | Do not label post-hoc solely because Git is later. Do not claim a verified prospective date. |
| ChatGPT share used as formatting/development aid | Share URL; page discusses Family A / Nadeau / block ablation; title on fetch was “Assess EB 2 NIW Chances” (conversation may mix topics) | Share fetch 2026-09-16; message dates not independently recovered | Provenance lead; not a verified creation date | Cannot prove the plan predates analysis |
| Repository initialized / first research commit | `12733c6` “Complete empirical analysis and research documentation” | 2026-09-12 16:11:14 −0600 | Independently documented | Plan, code, and results entered Git together |
| scipy / reproducibility doc fix | `63a6be1` | 2026-09-12 | Independently documented | Documentation, not a new primary analysis |
| Public-release hardening | `ca7e2bd`, `00e43aa`, `e14c53b` | 2026-09-12 | Independently documented | Packaging/docs |
| Manuscript added | `63dcb9c` | 2026-09-12 | Independently documented | Reporting of the already-locked analysis |
| v1.0.0 release notes / version bump | `01eb0f0`, `9a33d93` | 2026-09-12 | Independently documented | Release metadata |
| v1.1 publication revision | This revision’s files (`docs/revision_v1_1_*.md`, `feasibility/revision_v1_1.py`, new `outputs/*v1_1*`) | 2026-09-15–16 (this pass) | Supported by contemporaneous artifact | Later reporting, bootstrap/calibration assessment, VIF correction, labeled sensitivities. Not retroactive original analyses. |

---

## Original analysis versus later analyses

### Original locked analysis (v1.0 result set)

Treat as the original empirical core, whatever its pre-Git drafting date:

- Cohort, leakage controls, first-run holdout metrics
- Training-only 5×5 repeated CV (Family A source)
- Feature-family add-on ablation (Design A; exploratory)
- Death sensitivity
- Leave-one-block-out B1–B5 (Family B)
- Nadeau–Bengio + Holm inference on saved folds
- Repeat-level robustness check
- Correlation/VIF diagnostic (VIF encoding later judged invalid for categoricals)

These locked files must not be overwritten.

### Formalization / documentation

The analysis-plan file, README, methodology, results, limitations, and
manuscript describe that core. The plan file’s **Git** date is 2026-09-12.
The plan’s **authoring** date is not independently established.

The filename `pre_registration_block_ablation_plan.md` is historical
wording. It is a repository analysis plan. It is not evidence of formal
preregistration. That file is left unchanged as a historical artifact.

### Later (v1.1) analyses

Added after lock, labeled as such:

- Holdout bootstrap percentile intervals
- Holdout calibration intercept/slope (assessment, not recalibration)
- VIF with reference-category drop (descriptive)
- Analytic-cohort missingness table
- Nadeau–Bengio 95% CIs derived from locked estimates
- Adult-only sensitivity
- ALL9RDS==1 sensitivity
- Exclude-`ERTOTY2` (2020) sensitivity

Do not present these as if they were in the original plan.

---

## Terminology the reporting should use

| Avoid as an overclaim | Prefer |
| --- | --- |
| Formally preregistered | Documented analysis plan / repository analysis plan |
| Untouched / pristine / external holdout | First-run / development-stage internal evaluation set |
| Independently confirmatory holdout | Held-out internal evaluation; inference is training-only CV |
| Post-hoc plan (on Git-order grounds alone) | Plan entered Git on 2026-09-12; original creation date uncertain |
| Causal effect of predictors | Incremental predictive value / association for prediction |

---

## Narrowest defensible provenance statement

The analysis plan is a written repository document that entered Git on
2026-09-12 in the same commit as the empirical outputs. The researcher
reports that the plan was prepared locally before Git initialization.
Git cannot confirm or refute that recollection. A ChatGPT share exists
as a provenance lead and does not independently establish a creation
date. The study should not be called formally preregistered. The plan
should not be called post-hoc merely because it was committed with the
first research snapshot.

---

## Historical locked generated wording

Several v1.0 generated markdown files (for example
`outputs/statistical_inference_summary.md`,
`outputs/repeated_cv_summary.md`, ablation summaries, and
`outputs/robustness_repeat_level_summary.md`) still contain historical
phrases such as “Pre-registered,” “untouched,” “confirmation,” or
“conservative robustness check.” Those artifacts are preserved
byte-for-byte as historical evidence. Generator templates in
`feasibility/` were updated so that a future accidental re-run would
not re-emit the superseded wording. Current scientific interpretation
is in `docs/manuscript.md`, `docs/methodology.md`, `docs/results.md`,
and `docs/limitations.md`. Do not regenerate locked v1.0 files to
refresh wording.
