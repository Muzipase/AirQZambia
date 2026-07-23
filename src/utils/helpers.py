from pathlib import Path
from typing import Any, Iterable, Iterator, List
import os
import yaml
import random

try:
	import numpy as np
except Exception:  # pragma: no cover - numpy optional
	np = None


def ensure_dir(path: str) -> Path:
	p = Path(path)
	if p.suffix:  # looks like a file path
		p = p.parent
	p.mkdir(parents=True, exist_ok=True)
	return p


def load_yaml(path: str) -> Any:
	p = Path(path)
	with p.open("r", encoding="utf-8") as f:
		return yaml.safe_load(f)


def save_yaml(obj: Any, path: str) -> Path:
	p = Path(path)
	ensure_dir(str(p))
	with p.open("w", encoding="utf-8") as f:
		yaml.safe_dump(obj, f, sort_keys=False)
	return p


def set_seed(seed: int) -> None:
	random.seed(seed)
	if np is not None:
		np.random.seed(seed)


def chunked(iterable: Iterable, size: int) -> Iterator[List[Any]]:
	"""Yield successive chunks from iterable of given size."""
	chunk = []
	for item in iterable:
		chunk.append(item)
		if len(chunk) >= size:
			yield chunk
			chunk = []
	if chunk:
		yield chunk


__all__ = ["ensure_dir", "load_yaml", "save_yaml", "set_seed", "chunked"]

