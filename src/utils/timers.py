"""Wall-clock timing utilities for profiling pipeline stages.

Exposes the ``Timer`` context manager/decorator and the ``time_func`` decorator
for measuring and reporting execution time of data-fetching and training steps.
"""

import time
from contextlib import ContextDecorator
from typing import Optional


class Timer(ContextDecorator):
	"""Simple timer usable as a context manager or decorator.

	Usage:
		with Timer() as t:
			...
		print(t.elapsed)

		@Timer()
		def fn(...):
			...
	"""

	def __init__(self, name: Optional[str] = None, verbose: bool = False):
		"""Initialise the timer with an optional label and verbose reporting flag."""
		self.name = name
		self.verbose = verbose
		self.start: Optional[float] = None
		self.end: Optional[float] = None
		self.elapsed: Optional[float] = None

	def __enter__(self):
		self.start = time.perf_counter()
		return self

	def __exit__(self, *exc):
		self.end = time.perf_counter()
		self.elapsed = self.end - self.start if (self.start and self.end) else None
		if self.verbose:
			name = f" '{self.name}'" if self.name else ""
			print(f"Timer{name}: {self.elapsed:.6f}s")
		return False


def time_func(fn):
	"""Decorator that prints the wall-clock duration of the wrapped function."""
	def wrapper(*args, **kwargs):
		"""Invoke *fn* and print its wall-clock duration to stdout."""
		t0 = time.perf_counter()
		res = fn(*args, **kwargs)
		t1 = time.perf_counter()
		print(f"{fn.__name__} took {t1 - t0:.6f}s")
		return res

	wrapper.__name__ = fn.__name__
	return wrapper


__all__ = ["Timer", "time_func"]

