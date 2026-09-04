"""
KIR AI Document Intelligence — Structured Logging.

Uses structlog for structured, context-bound logging.
Every log entry carries job_id and step context automatically
when the bound logger is used inside a pipeline step.

Usage
-----
    from app.core.logging import get_logger

    log = get_logger(__name__)
    log.info("stage.complete", stage="normalization", unit_count=12)

    # Inside a pipeline step, bind context:
    step_log = log.bind(job_id="abc123", step="segmentation")
    step_log.warning("low_unit_count", unit_count=2)
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Configure structlog processors and standard library integration.

    Call once at application startup before creating any loggers.

    Parameters
    ----------
    level:
        Standard logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    json_output:
        If True, output JSON lines. If False, output human-readable console format.
        Set to True in production / CI. Set to False for local development.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_output:
        processors: list[structlog.types.Processor] = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
        formatter = logging.Formatter("%(message)s")
    else:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
        formatter = logging.Formatter("%(message)s")

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging for third-party libraries.
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog bound logger for the given module name.

    Parameters
    ----------
    name:
        Typically __name__ of the calling module.

    Returns
    -------
    structlog.stdlib.BoundLogger
        A logger instance ready for structured logging.
    """
    return structlog.get_logger(name)  # type: ignore[return-value]
