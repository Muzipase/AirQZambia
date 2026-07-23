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
	def wrapper(*args, **kwargs):
		t0 = time.perf_counter()
		res = fn(*args, **kwargs)
		t1 = time.perf_counter()
		print(f"{fn.__name__} took {t1 - t0:.6f}s")
		return res

	wrapper.__name__ = fn.__name__
	return wrapper


__all__ = ["Timer", "time_func"]

