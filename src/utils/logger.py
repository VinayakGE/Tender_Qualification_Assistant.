"""Structured logging setup using structlog."""

import logging
import sys
from typing import Any

import structlog


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configure structlog and standard library logging.

    Call this once at application startup (e.g., in server.py or pipeline/runner.py).

    Args:
        level: Logging level string ("DEBUG", "INFO", "WARNING", "ERROR").
        fmt: Output format — "json" for machine-readable, "console" for human-readable.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure stdlib logging to feed into structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if fmt == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger for the given name.

    Usage:
        logger = get_logger(__name__)
        logger.info("pipeline_started", tender_id="T001", stage="parser")

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        A bound structlog logger with the name attached.
    """
    return structlog.get_logger(name)
