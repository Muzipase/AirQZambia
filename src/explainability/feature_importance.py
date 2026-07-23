from typing import Dict, Any
from src.explainability.shap_explainer import ShapExplainer


def get_feature_importance(explainer: ShapExplainer) -> Dict[str, Any]:
    return explainer.get_summary()
