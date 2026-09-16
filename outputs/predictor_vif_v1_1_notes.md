# Corrected VIF diagnostic (v1.1)

The locked file `outputs/predictor_vif.csv` applies VIF to the production
design matrix, which one-hot encodes categoricals **without** dropping a
reference level. Auxiliary regressions of each dummy on the remaining
columns (including the other levels of the same factor, plus an
intercept in `LinearRegression`) are then linearly dependent. That is
the dummy-variable trap. Almost all categorical columns therefore have
infinite VIF. Those infinities are an encoding artifact, not evidence
that the corresponding predictors must be removed, and they were never
used to change the model.

This v1.1 table repeats VIF after `OneHotEncoder(drop="first")` on the
same 3,831-person training portion. The dropped level is sklearn's
default first category after imputation, not a scientifically chosen
reference; any single dropped level removes the trap. Auxiliary VIF
regressions include an intercept. The diagnostic is **descriptive
only**. VIF was never a prespecified removal rule, and no predictor is
dropped because of these values. The production model remains
L2-regularized logistic regression on the original (no drop) encoding.

- Design columns: 40
- Max VIF: 3.681
- VIF > 5: 0
- VIF > 10: 0
- Infinite VIF after drop-first: 0

All corrected VIFs below 5 means this diagnostic did not flag strong
linear collinearity on the reference-dropped training design matrix.
That is not proof of independence (pairwise η associations remain),
and it is not a reason to add or remove predictors.
