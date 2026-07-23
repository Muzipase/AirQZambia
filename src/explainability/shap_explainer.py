import numpy as np
import pandas as pd
import shap


class ShapExplainer:
    def __init__(self, model, background_data: pd.DataFrame):
        self.model = model
        self.background_data = background_data.copy()
        self.feature_names = list(background_data.columns)
        background_sample = self.background_data.sample(
            n=min(len(self.background_data), 50), random_state=42
        )
        self.explainer = shap.KernelExplainer(
            self._model_predict, background_sample, link="identity"
        )

    def _model_predict(self, data: np.ndarray) -> np.ndarray:
        df = pd.DataFrame(data, columns=self.feature_names)
        if hasattr(self.model, "predict_proba") and callable(getattr(self.model, "predict_proba", None)):
            return self.model.predict_proba(df)
        return self.model.decision_function(df)

    def get_summary(self):
        background_sample = self.background_data.sample(
            n=min(len(self.background_data), 25), random_state=42
        )
        shap_values = self.explainer.shap_values(background_sample)

        if isinstance(shap_values, list):
            aggregated = np.mean([np.abs(values).mean(axis=0) for values in shap_values], axis=0)
        else:
            aggregated = np.mean(np.abs(shap_values), axis=0)

        return {
            feature: float(aggregated[idx])
            for idx, feature in enumerate(self.feature_names)
        }

    def explain_instance(self, input_df: pd.DataFrame):
        shap_values = self.explainer.shap_values(input_df)
        if isinstance(shap_values, list):
            values = [vals[0].tolist() if len(vals) else [] for vals in shap_values]
        else:
            values = shap_values[0].tolist() if shap_values.ndim > 1 else shap_values.tolist()

        ev = getattr(self.explainer, "expected_value", None)
        if ev is not None:
            base_values = [float(v) for v in ev] if hasattr(ev, "__iter__") else [float(ev)]
        else:
            base_values = []
        return {
            "feature_names": self.feature_names,
            "shap_values": values,
            "base_values": base_values,
        }
