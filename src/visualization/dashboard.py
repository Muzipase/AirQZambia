"""Streamlit dashboard renderers for surfacing pipeline results.

Provides a thin, optional-Streamlit layer: when Streamlit is installed the
helpers render widgets; otherwise they gracefully return the raw data so the
same calls work in headless/non-interactive contexts.
"""

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
	"""Render a DataFrame as a Streamlit table if available; otherwise return the frame.

	Parameters
	----------
	df : pandas.DataFrame
		Data to display.
	caption : str, optional
		Optional caption shown above the table.
	"""
	if st is None:
		return df
	st.dataframe(df, caption=caption)
	return True


__all__ = ["show_metrics", "show_dataframe"]

