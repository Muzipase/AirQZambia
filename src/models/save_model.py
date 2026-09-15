"""Model persistence utilities.

Serializes trained scikit-learn models (or any picklable object) to disk via
joblib so they can be reloaded at serving time by the FastAPI endpoint.
"""

import joblib
from pathlib import Path


def save_model(model, path: Path):
    """Serialize *model* to *path*, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
