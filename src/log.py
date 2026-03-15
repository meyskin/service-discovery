"""Unified logging for every component in the service-discovery demo."""

import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(component)s] %(message)s"
DATE_FORMAT = "%H:%M:%S"


class _ComponentFilter(logging.Filter):
    """Inject a fixed *component* field into every log record."""

    def __init__(self, component: str):
        super().__init__()
        self.component = component

    def filter(self, record):
        record.component = self.component
        return True


def get_logger(component: str) -> logging.Logger:
    """Return a logger that always includes *component* in the output.

    Usage:
        log = get_logger("REGISTRY")
        log.info("Started on port %d", port)
        # => 12:34:56 INFO  [REGISTRY] Started on port 8000
    """
    logger = logging.getLogger(f"sd.{component}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(handler)
        logger.addFilter(_ComponentFilter(component))
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

    return logger
