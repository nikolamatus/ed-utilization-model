"""B4 — Access-block ablation. Removes only INSCOVY3 and HAVEUS6."""
from __future__ import annotations

import sys

from .block_ablation import BlockSpec, assert_column_sets, run_experiment

ACCESS_SPEC = BlockSpec(
    experiment_id="B4",
    slug="access",
    title="Access-block ablation (INSCOVY3 and HAVEUS6 removed)",
    block=("INSCOVY3", "HAVEUS6"),
    reduced_model_name="full_without_access",
    prefix="noaccess",
    must_retain=(
        "AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X",
        "RTHLTH6", "MNHLTH6",
        "POVCATY3", "TTLPY3X", "EMPST6",
        "ERTOTY1", "ERTOTY2", "ERTOTY3",
    ),
)


def main() -> int:
    assert_column_sets(ACCESS_SPEC)
    run_experiment(ACCESS_SPEC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
