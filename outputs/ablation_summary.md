# Feature-family ablation and death sensitivity

Same analytic cohort, same 25% stratified holdout (seed=42),
same outcome, same leakage rule, and the same regularized logistic
architecture as the first real run. First-run output filenames were not
replaced.

## Largest incremental family
**ed_demographics**
ROC-AUC versus ED-history-only: +0.043
PR-AUC versus ED-history-only: +0.069

## Is the full-model lift concentrated or distributed?
The full-model lift versus ED-history-only is **distributed across more than one family**.
Full model Δ ROC-AUC: +0.065
Full model Δ PR-AUC: +0.085
Families with ROC-AUC lift > 0.01 versus ED history: 4

## Death sensitivity
Excluding the 37 YEARIND==1 decedents does not materially change performance (full-model ROC-AUC change -0.003, PR-AUC change -0.005 versus the original full-test metrics).

Original full model (original test): ROC-AUC=0.774, PR-AUC=0.416, Brier=0.099
Refit excluding YEARIND==1 decedents: ROC-AUC=0.771, PR-AUC=0.411, Brier=0.098

This does not replace the primary YEARIND==1 cohort.

## Does the original research question remain supported?
Yes, on this holdout the pre-cutoff non-ED families still add ranking value beyond three-year ED history.

Unweighted analytic-sample metrics only. Not a national estimate, clinical
validation, or causal finding.
