from pathlib import Path
from typing import Any, Optional

try:
	import pandas as pd
except Exception:  # pragma: no cover - pandas optional
	pd = None

try:
	import joblib
except Exception:  # pragma: no cover - joblib optional
	joblib = None


def _ensure_parent(path: Path) -> None:
	path = Path(path)
	if not path.parent.exists():
		path.parent.mkdir(parents=True, exist_ok=True)


def save_dataframe(df: "pd.DataFrame", path: str, index: bool = False, **kwargs) -> Path:
	"""Save a pandas DataFrame to CSV or Parquet depending on file suffix.

	Args:
		df: DataFrame to save.
		path: Target file path (supports .csv, .parquet, .pkl).
		index: Whether to write row index (for CSV/Parquet).
		**kwargs: Extra kwargs forwarded to pandas writer.

	Returns:
		Path to saved file.
	"""
	if pd is None:
		raise RuntimeError("pandas is required to use save_dataframe")

	p = Path(path)
	_ensure_parent(p)
	suf = p.suffix.lower()
	if suf in (".csv",):
		df.to_csv(p, index=index, **kwargs)
	elif suf in (".parquet", ".pq"):
		df.to_parquet(p, index=index, **kwargs)
	elif suf in (".pkl", ".pickle"):
		df.to_pickle(p, **kwargs)
	else:
		# default to CSV
		df.to_csv(p, index=index, **kwargs)
	return p


def load_dataframe(path: str) -> "pd.DataFrame":
	"""Load a DataFrame from CSV, Parquet or pickle based on suffix."""
	if pd is None:
		raise RuntimeError("pandas is required to use load_dataframe")
	p = Path(path)
	suf = p.suffix.lower()
	if suf == ".csv":
		return pd.read_csv(p)
	if suf in (".parquet", ".pq"):
		return pd.read_parquet(p)
	if suf in (".pkl", ".pickle"):
		return pd.read_pickle(p)
	# try csv fallback
	return pd.read_csv(p)


def save_model(obj: Any, path: str) -> Path:
	"""Serialize an object to disk using joblib.

	Raises a RuntimeError if `joblib` is not available.
	"""
	if joblib is None:
		raise RuntimeError("joblib is required to use save_model")
	p = Path(path)
	_ensure_parent(p)
	joblib.dump(obj, p)
	return p


def load_model(path: str) -> Any:
	if joblib is None:
		raise RuntimeError("joblib is required to use load_model")
	return joblib.load(path)


def save_json(obj: Any, path: str, indent: Optional[int] = 2) -> Path:
	import json

	p = Path(path)
	_ensure_parent(p)
	with p.open("w", encoding="utf-8") as f:
		json.dump(obj, f, indent=indent)
	return p


def load_json(path: str) -> Any:
	import json

	p = Path(path)
	with p.open("r", encoding="utf-8") as f:
		return json.load(f)


__all__ = [
	"save_dataframe",
	"load_dataframe",
	"save_model",
	"load_model",
	"save_json",
	"load_json",
]

