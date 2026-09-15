"""Build a SHAP force plot for a single prediction instance.

The resulting plot object can be embedded in the Streamlit or
Next.js frontend to visualise individual prediction explanations.
"""

import shap
import pandas as pd


def build_force_plot(explainer, input_df: pd.DataFrame):
    """Render a SHAP force plot for the given input row.

    Args:
        explainer: A ``ShapExplainer`` instance (or compatible wrapper).
        input_df: Single-row DataFrame of features to explain.

    Returns:
        A ``shap.Explanation`` force-plot object, or ``None`` on failure.
    """
    shap_values = explainer.explainer.shap_values(input_df)
    try:
        return shap.force_plot(
            explainer.explainer.expected_value,
            shap_values,
            input_df,
            matplotlib=False,
            show=False,
        )
    except Exception:
        return None
