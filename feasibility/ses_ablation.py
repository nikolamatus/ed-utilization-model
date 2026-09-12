"""B5 — SES-block ablation. Removes only POVCATY3, TTLPY3X, and EMPST6."""
from __future__ import annotations

import sys

from .block_ablation import BlockSpec, assert_column_sets, run_experiment

SES_SPEC = BlockSpec(
    experiment_id="B5",
    slug="ses",
    title="SES-block ablation (POVCATY3, TTLPY3X, and EMPST6 removed)",
    block=("POVCATY3", "TTLPY3X", "EMPST6"),
    reduced_model_name="full_without_ses",
    prefix="noses",
    must_retain=(
        "AGEY3X", "SEX", "RACETHX", "REGIONY3", "MARRY6X",
        "RTHLTH6", "MNHLTH6",
        "INSCOVY3", "HAVEUS6",
        "ERTOTY1", "ERTOTY2", "ERTOTY3",
    ),
)


def main() -> int:
    assert_column_sets(SES_SPEC)
    run_experiment(SES_SPEC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
