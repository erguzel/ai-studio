"""Logging setup for ai-studio.

A single loguru logger is shared across the package. Import it as:

    from aistudio.common.log import logger
"""
import sys

from loguru import logger

__all__ = ["configure", "logger"]


def configure(sink=sys.stderr, level="INFO", serialize=False, diagnose=False):
    """Replace the default handler with one configured for this application.

    Args:
        sink: file path or stream to write to.
        level: minimum record level to emit.
        serialize: emit one JSON object per record instead of plain text.
            Useful when the logs are shipped to a collector.
        diagnose: include the values of local variables in tracebacks. Kept
            off by default because those values can contain the data being
            processed, which must not end up in a log file.

    Returns:
        The handler id returned by loguru, so callers can remove it again.
    """
    logger.remove()
    return logger.add(sink, level=level, serialize=serialize, diagnose=diagnose)
