# Numerical tolerances for floating point comparisons
FLOAT_EQUALITY_TOLERANCE = 1e-10
"""Default tolerance for floating point equality comparisons."""

DIVISION_BY_ZERO_THRESHOLD = 1e-15
"""Threshold below which a value is considered effectively zero for division."""

CONDITION_EVALUATION_THRESHOLD = 1e-10
"""Threshold for evaluating conditional expressions as true/false."""

DIMENSIONAL_PRECISION_TOLERANCE = 1e-10
"""Tolerance for dimensional signature comparisons."""

PREFIX_LOOKUP_TOLERANCE = 1e-10
"""Default tolerance for SI prefix factor lookup."""

PREFIX_LOOKUP_MIN_TOLERANCE = 1e-15
"""Minimum tolerance for SI prefix factor lookup to avoid expensive searches."""
