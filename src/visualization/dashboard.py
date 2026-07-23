from typing import Dict, Any, Optional

try:
	import streamlit as st
except Exception:  # pragma: no cover - streamlit optional
	st = None


def show_metrics(metrics: Dict[str, Any]):
	"""Render key/value metrics in Streamlit if available; otherwise return the dict."""
	if st is None:
		return metrics
	cols = st.columns(len(metrics))
	for col, (k, v) in zip(cols, metrics.items()):
		col.metric(label=k, value=v)
	return True


def show_dataframe(df, caption: Optional[str] = None):
	if st is None:
		return df
	st.dataframe(df, caption=caption)
	return True


__all__ = ["show_metrics", "show_dataframe"]

