import logging
import os

_LOGGER: logging.Logger | None = None


def get_logger(name: str = "qnty") -> logging.Logger:
    """Return a module-level configured logger.

    Log level resolves in order:
    1. Explicit environment variable QNTY_LOG_LEVEL
    2. Existing logger level if already configured
    3. Defaults to INFO
    """
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(name)
    if not logger.handlers:
        # Basic handler (stdout)
        handler = logging.StreamHandler()
        fmt = os.getenv("QNTY_LOG_FORMAT", "%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)

    # Resolve level
    level_str = os.getenv("QNTY_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    _LOGGER = logger
    return logger


def set_log_level(level: str):
    """Dynamically adjust log level at runtime."""
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
