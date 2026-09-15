"""Global constants shared across the AirQ Zambia pipeline.

Covers reproducibility seeds, date / time formatting strings, and
naming conventions for persisted model artefacts.
"""

DEFAULT_SEED = 42
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

# Model naming
MODEL_FILE_PATTERN = "model-{name}.pkl"

__all__ = ["DEFAULT_SEED", "DATE_FORMAT", "TIME_FORMAT", "MODEL_FILE_PATTERN"]

