"""
Logging setup for the UIO API wrapper.

Behavior:
- Package is silent by default (make sure uio_api.__init__ disables the namespace).
- This module ONLY enables and configures logging when setup_logging() is called.
- Console and file sinks are configured SEPARATELY and have SEPARATE default levels:
    - console  : SUCCESS
    - file     : WARNING
- Repeated calls are idempotent: sinks added by this module are replaced.
"""

import re
import sys
from pathlib import Path
from typing import Any

from loguru import logger as _root_logger

from .core.enums import LogLevel

_PKG = "uio_api"


# Pre-compile regex patterns for better performance

_TOKEN_JSON_PATTERN = re.compile(r'("token"|"authorization")\s*:\s*"[^"]*"', re.IGNORECASE)
_TOKEN_URL_PATTERN = re.compile(r"[?&]token=[^&\s]+", re.IGNORECASE)
_BEARER_PATTERN = re.compile(r"Bearer\s+[^\s&]+", re.IGNORECASE)


# ---------- patch: endpoint prefix and security redaction ----------
def _endpoint_patcher(record: Any) -> None:
    ep = record["extra"].get("endpoint")
    record["extra"]["endpoint_prefix"] = f"{ep} | " if ep else ""

    # Redact sensitive information from log messages
    if "message" in record:
        msg = str(record["message"])
        # Redact Authorization headers
        msg = msg.replace("Authorization: Bearer ", "Authorization: Bearer [REDACTED]")
        msg = msg.replace("Authorization: Token ", "Authorization: Token [REDACTED]")

        # Use pre-compiled regex patterns for token redaction
        msg = _TOKEN_JSON_PATTERN.sub(r'\1: "[REDACTED]"', msg)
        msg = _TOKEN_URL_PATTERN.sub("?token=[REDACTED]", msg)
        msg = _BEARER_PATTERN.sub("Bearer [REDACTED]", msg)

        record["message"] = msg


# Public (patched) logger
logger = _root_logger.patch(_endpoint_patcher)

# Track only sinks we add here (so we don't touch host-app sinks)
_console_sink_id: int | None = None
_file_sink_id: int | None = None


def _default_log_file() -> Path:
    """Get default rotating log file path under the package config directory.

    Returns:
        Path: Path to the default log file.
    """
    from .config.paths import resolve_config_dir  # late import to avoid cycles

    cfg = resolve_config_dir()
    log_dir = cfg / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "uio_api.log"


def _console_format() -> str:
    """Get console log format string.

    Returns:
        str: Loguru format string for console output with colors.
    """
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )


def _file_format() -> str:
    """Get file log format string.

    Returns:
        str: Loguru format string for file output without colors.
    """
    return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"


def _remove_console_sink() -> None:
    """Remove the console sink if it exists."""
    global _console_sink_id
    if _console_sink_id is not None:
        try:
            logger.remove(_console_sink_id)
        except Exception:
            pass
        _console_sink_id = None


def _remove_file_sink() -> None:
    """Remove the file sink if it exists."""
    global _file_sink_id
    if _file_sink_id is not None:
        try:
            logger.remove(_file_sink_id)
        except Exception:
            pass
        _file_sink_id = None


def setup_logging(
    *,
    # explicit separation; defaults match your requested baseline
    enable_console: bool = True,
    enable_file: bool = True,
    console_level: LogLevel = LogLevel.SUCCESS,
    file_level: LogLevel = LogLevel.WARNING,
    log_file: Path | str | None = None,
    use_config_path: bool = False,
) -> None:
    """Configure Loguru for the `uio_api` package.

    Args:
        enable_console: Whether to enable console logging. Defaults to True.
        enable_file: Whether to enable file logging. Defaults to True.
        console_level: Log level for console output. Defaults to "SUCCESS".
        file_level: Log level for file output. Defaults to "WARNING".
        log_file: Path to log file. If None and use_config_path=False, uses default location.
        use_config_path: Whether to use the configured logging file path from settings.

    Note:
        - Enables the `uio_api` namespace.
        - Removes/replaces only the sinks previously added by this module.
        - Adds console and file sinks with independent levels.
        - When use_config_path=True, uses platformdirs-based path from configuration.
    """
    global _console_sink_id, _file_sink_id

    # Opt-in: enable this namespace
    _root_logger.enable(_PKG)

    # Replace only our own sinks
    _remove_console_sink()
    _remove_file_sink()

    # Console sink (stderr)
    if enable_console:
        _console_sink_id = logger.add(
            sys.stderr,
            level=console_level,
            format=_console_format(),
            colorize=True,
            backtrace=True,  # safe defaults; not exposed via config
            diagnose=False,  # keep noise down in prod
            enqueue=False,  # set True manually if you need multi-process
        )

    # File sink (rotating)
    if enable_file:
        if use_config_path and not log_file:
            # Use configured path from settings
            from .config.base import base_settings

            path = base_settings.LOGGING_FILE_PATH
        elif log_file:
            path = Path(log_file)
        else:
            path = _default_log_file()

        if path:
            _file_sink_id = logger.add(
                str(path),
                level=file_level,
                format=_file_format(),
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                backtrace=True,
                diagnose=False,
                enqueue=False,
            )


def reconfigure_logging(**kwargs: Any) -> None:
    """Idempotent reconfiguration wrapper.

    Args:
        **kwargs: Arguments to pass to setup_logging().
    """
    setup_logging(**kwargs)


def disable_logging() -> None:
    """Remove module-managed sinks and disable the namespace.

    This function removes all sinks added by this module and disables
    the uio_api logger namespace.
    """
    _remove_console_sink()
    _remove_file_sink()
    _root_logger.disable(_PKG)


__all__ = [
    "logger",
    "setup_logging",
    "reconfigure_logging",
    "disable_logging",
]
