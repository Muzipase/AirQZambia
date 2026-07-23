import shap
import pandas as pd


def build_force_plot(explainer, input_df: pd.DataFrame):
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
