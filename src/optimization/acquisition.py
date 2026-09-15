"""Acquisition functions for Bayesian optimization.

Provides the Expected Improvement (EI) acquisition function, which balances
exploration of uncertain regions with exploitation of regions expected to
outperform the current best observation.
"""

import numpy as np
import math


def expected_improvement(mean: float, std: float, best: float) -> float:
    """Compute Expected Improvement given a predicted mean, std, and current best score."""
    if std <= 0:
        return 0.0
    improvement = mean - best
    z = improvement / std
    return float(improvement * 0.5 * (1 + math.erf(z / math.sqrt(2))) + std * math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi))
