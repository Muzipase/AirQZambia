"""Retrieve global feature importance scores from the SHAP explainer.

Wraps ``ShapExplainer.get_summary`` so the rest of the pipeline can
access importance rankings without depending on the SHAP API directly.
"""

from typing import Dict, Any
from src.explainability.shap_explainer import ShapExplainer


def get_feature_importance(explainer: ShapExplainer) -> Dict[str, Any]:
    """Return a feature-name-to-importance mapping from the explainer."""
    return explainer.get_summary()
