"""Generate a SHAP beeswarm summary plot for the given feature matrix.

The plot is returned as a matplotlib-compatible object suitable for
embedding in the Streamlit dashboard.
"""

import shap
import pandas as pd


def create_summary_plot(explainer, X: pd.DataFrame):
    """Render a SHAP beeswarm summary plot.

    Args:
        explainer: A ``ShapExplainer`` instance (or compatible wrapper).
        X: Feature matrix to visualise.

    Returns:
        The plot object produced by ``shap.summary_plot``, or ``None``
        if rendering fails.
    """
    shap_values = explainer.explainer.shap_values(X)
    try:
        return shap.summary_plot(shap_values, X, show=False)
    except Exception:
        return None
