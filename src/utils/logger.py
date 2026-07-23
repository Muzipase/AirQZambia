import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def get_logger(name: str = "air_quality", level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
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

