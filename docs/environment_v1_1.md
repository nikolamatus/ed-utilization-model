# Software environment (v1.1 freeze)

This record describes the environment used to inspect, document, and
freeze the v1.1 reporting revision. It is not a claim that every
historical v1.0 byte was produced on this exact interpreter.

## Machine used for the v1.1 documentation freeze

| Item | Value |
|---|---|
| OS | Windows 10 (`win32`) |
| Python | 3.14.7 (`MSC v.1944 64 bit (AMD64)`) |
| pandas | 3.0.5 |
| numpy | 2.5.3 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| matplotlib | 3.11.2 |

A complete `pip freeze` from this environment is in
[`docs/pip_freeze_v1_1.txt`](pip_freeze_v1_1.txt).

Declared ranges remain in `pyproject.toml` (package version **1.1.0**).

## Reproduction accuracy

- **Locked v1.0 artifacts** in `outputs/` that existed before this
  revision (primary CSVs, figures, and generated v1.0 summaries) remain
  **byte-identical**. They were not regenerated.
- **v1.1 numerical results** (`outputs/*v1_1*`) are expected to
  reproduce to **solver / library tolerance** across platforms, not
  necessarily bit-for-bit. Small floating-point differences from BLAS,
  OpenMP, or package versions do not change scientific conclusions
  (Family A signs, detection decisions, bootstrap interval rounding,
  VIF < 5, or calibration interpretation).
- Do not re-run `python -m feasibility.run` against this completed
  analysis. v1.1 reporting uses `python -m feasibility.revision_v1_1`.
