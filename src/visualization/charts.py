from typing import Optional, Sequence

try:
	import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - matplotlib optional
	plt = None


def bar_chart(categories: Sequence, values: Sequence, title: Optional[str] = None, xlabel: Optional[str] = None, ylabel: Optional[str] = None, savepath: Optional[str] = None):
	if plt is None:
		raise RuntimeError("matplotlib is required for charts")
	fig, ax = plt.subplots(figsize=(6, 4))
	ax.bar(categories, values)
	if title:
		ax.set_title(title)
	if xlabel:
		ax.set_xlabel(xlabel)
	if ylabel:
		ax.set_ylabel(ylabel)
	fig.tight_layout()
	if savepath:
		fig.savefig(savepath)
	plt.close(fig)
	return fig


def hist_chart(values, bins: int = 20, title: Optional[str] = None, savepath: Optional[str] = None):
	if plt is None:
		raise RuntimeError("matplotlib is required for charts")
	fig, ax = plt.subplots(figsize=(6, 4))
	ax.hist(values, bins=bins)
	if title:
		ax.set_title(title)
	fig.tight_layout()
	if savepath:
		fig.savefig(savepath)
	plt.close(fig)
	return fig


__all__ = ["bar_chart", "hist_chart"]

