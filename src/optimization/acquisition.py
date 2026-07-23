import numpy as np
import math


def expected_improvement(mean: float, std: float, best: float) -> float:
    if std <= 0:
        return 0.0
    improvement = mean - best
    z = improvement / std
    return float(improvement * 0.5 * (1 + math.erf(z / math.sqrt(2))) + std * math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi))
