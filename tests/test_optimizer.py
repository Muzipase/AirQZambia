import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

from src.optimization.acquisition import expected_improvement


def test_expected_improvement_positive_when_above_best():
    ei = expected_improvement(mean=5.0, std=1.0, best=3.0)
    assert ei > 0, "EI should be positive when mean > best"


def test_expected_improvement_zero_when_std_zero():
    ei = expected_improvement(mean=5.0, std=0.0, best=3.0)
    assert ei == 0.0, "EI should be 0 when std is 0"


def test_expected_improvement_non_negative():
    ei = expected_improvement(mean=1.0, std=2.0, best=5.0)
    assert ei >= 0, "EI should never be negative"
