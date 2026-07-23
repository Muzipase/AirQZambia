from typing import Optional
from pathlib import Path

try:
	import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - matplotlib optional
	plt = None


def plot_time_series(df, x: str, y: str, title: Optional[str] = None, show: bool = False, savepath: Optional[str] = None):
	"""Create a simple time-series line plot using matplotlib.

	df: pandas-like object supporting indexing by column name.
	"""
	if plt is None:
		raise RuntimeError("matplotlib is required for plotting")

	fig, ax = plt.subplots(figsize=(8, 4))
	ax.plot(df[x], df[y], marker=".")
	ax.set_xlabel(x)
	ax.set_ylabel(y)
	if title:
		ax.set_title(title)
	fig.tight_layout()
	if savepath:
		p = Path(savepath)
		p.parent.mkdir(parents=True, exist_ok=True)
		fig.savefig(p)
	if show:
		plt.show()
	plt.close(fig)
	return fig


__all__ = ["plot_time_series"]

