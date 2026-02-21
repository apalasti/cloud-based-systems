import logging
import sys

from app.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    format_str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root = logging.getLogger("app")
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format_str))
        root.addHandler(handler)
