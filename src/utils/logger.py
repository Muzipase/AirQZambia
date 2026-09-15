"""Centralised logging configuration for the AirQ Zambia pipeline.

Creates and returns pre-configured ``logging.Logger`` instances with consistent
formatting, optional rotating file output, and console streaming.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def get_logger(name: str = "air_quality", level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
	"""Return a module-level logger with console output and optional rotating file handler.

	Parameters
	----------
	name : str
		Logger namespace (default ``"air_quality"``).
	level : int
		Minimum severity to propagate (default ``INFO``).
	log_file : str, optional
		If provided, a ``RotatingFileHandler`` is attached (5 MB, 3 backups).

	Returns
	-------
	logging.Logger
		A logger that is reused on subsequent calls with the same *name*.
	"""
	logger = logging.getLogger(name)
	if logger.handlers:
		return logger
	logger.setLevel(level)

	fmt = logging.Formatter("%(asctime)s %(levelname)-8s [%(name)s] %(message)s")

	sh = logging.StreamHandler()
	sh.setFormatter(fmt)
	logger.addHandler(sh)

	if log_file:
		p = Path(log_file)
		if not p.parent.exists():
			p.parent.mkdir(parents=True, exist_ok=True)
		fh = RotatingFileHandler(p, maxBytes=5 * 1024 * 1024, backupCount=3)
		fh.setFormatter(fmt)
		logger.addHandler(fh)

	logger.propagate = False
	return logger


__all__ = ["get_logger"]

