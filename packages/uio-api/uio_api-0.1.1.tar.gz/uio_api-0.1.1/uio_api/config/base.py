"""Base configuration settings for the UIO API wrapper framework.

This module provides the framework-level BaseSettings that contains
generic configuration knobs shared across all API modules.
"""

import getpass
import os
import sys
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import tomllib  # built-in since Python 3.11

from .. import APPNAME
from ..core.enums import LogLevel, SecretsBackend
from ..logging import setup_logging  # local import to avoid cycles
from .paths import keyring_index_path, resolve_config_dir, secrets_toml_path

# -------------------------------------------------------------------
# Parsing helpers
# -------------------------------------------------------------------


def parse_float(value: Any, *, default: float | None = None) -> float:
    """Parse a value into float with strict checks.

    Args:
        value: Input value; accepts str, int, float.
        default: Fallback used when value is None.

    Returns:
        Parsed float.

    Raises:
        TypeError: When value is None and default is None, or type unsupported.
        ValueError: When string parsing fails.
    """
    if value is None:
        if default is not None:
            return default
        raise TypeError("Expected float-compatible value, got None")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value.strip())
    raise TypeError(f"Expected str|int|float, got {type(value).__name__}")


def parse_int(value: Any, *, default: int | None = None, base: int = 10) -> int:
    """Parse a value into int with strict checks.

    Args:
        value: Input value; accepts str, int, bool.
        default: Fallback used when value is None.
        base: Base for string parsing.

    Returns:
        Parsed int.

    Raises:
        TypeError: When value is None and default is None, or type unsupported.
        ValueError: When string parsing fails.
    """
    if value is None:
        if default is not None:
            return default
        raise TypeError("Expected int-compatible value, got None")
    if isinstance(value, bool):  # bool is a subclass of int; handle explicitly
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.strip(), base)
    raise TypeError(f"Expected str|int|bool, got {type(value).__name__}")


def _parse_bool(v: str | None, default: bool | None) -> bool | None:
    """Parse a boolean-like string."""
    if v is None:
        return default
    v = v.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off", ""}:
        return False
    return default


def _is_tty() -> bool:
    """Check if stdin is a TTY."""
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _default_username() -> str:
    """Derive a default username from env or system."""

    return os.environ.get(f"{APPNAME}_USERNAME") or getpass.getuser()


def _coerce_backend(s: str | None) -> SecretsBackend:
    """Coerce string to SecretsBackend enum."""
    if not s:
        return SecretsBackend.TOML
    s = s.strip().lower()
    return SecretsBackend.KEYRING if s == "keyring" else SecretsBackend.TOML


def _coerce_log_level(s: str | None, default: LogLevel = LogLevel.INFO) -> LogLevel:
    """Coerce string to a LogLevel (case-insensitive)."""
    if not s:
        return default
    try:
        return LogLevel(s.strip().upper())
    except ValueError:
        return default


# -------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BaseSettings:
    """Base configuration settings for the UIO API wrapper framework.

    This class contains framework-level configuration that is shared
    across all API modules. Module-specific settings extend this base.

    Attributes:
        username: Default username for authentication.
        interactive: Whether to use interactive authentication by default.
        secrets_backend: Backend for storing secrets (TOML or keyring).
        config_dir: Configuration directory path.
        secrets_file: Path to secrets TOML file.
        keyring_index_file: Path to keyring index file.
        timeout: Request timeout in seconds.
        refresh_on_401: Whether to refresh tokens on 401 responses.
        retry_attempts: Number of retry attempts for failed requests.
        allow_non_idempotent_retries: Whether to retry non-idempotent requests.
        logging_enabled: Whether to enable logging by default.
        logging_level: Console log level as string (e.g., "INFO").
        logging_file_level: File log level as string.
        logging_file_enabled: Whether to enable file logging.
        logging_console_enabled: Whether to enable console logging.
        logging_include_endpoints: Whether to include endpoints in logs.
        logging_file_path: Path to the log file, if any.
    """

    # User identity
    username: str | None
    interactive: bool

    # Secrets management
    secrets_backend: SecretsBackend

    # Paths (resolved)
    config_dir: Path
    secrets_file: Path
    keyring_index_file: Path

    # HTTP behavior
    timeout: float
    refresh_on_401: bool

    # Retry behavior
    retry_attempts: int
    allow_non_idempotent_retries: bool

    # Logging behavior
    logging_enabled: bool
    logging_level: LogLevel
    logging_file_level: LogLevel
    logging_file_enabled: bool
    logging_console_enabled: bool
    logging_include_endpoints: bool
    logging_file_path: Path | None

    # --------- UPPERCASE conveniences ---------

    @property
    def USER_NAME(self) -> str | None:
        """Get the default username."""
        return self.username

    @property
    def INTERACTIVE(self) -> bool:
        """Get the interactive authentication setting."""
        return self.interactive

    @property
    def SECRETS_BACKEND(self) -> SecretsBackend:
        """Get the secrets backend setting."""
        return self.secrets_backend

    @property
    def CONFIG_DIR(self) -> Path:
        """Get the configuration directory path."""
        return self.config_dir

    @property
    def SECRETS_FILE(self) -> Path:
        """Get the secrets file path."""
        return self.secrets_file

    @property
    def KEYRING_INDEX_FILE(self) -> Path:
        """Get the keyring index file path."""
        return self.keyring_index_file

    @property
    def TIMEOUT(self) -> float:
        """Get the request timeout."""
        return self.timeout

    @property
    def REFRESH_ON_401(self) -> bool:
        """Get the refresh on 401 setting."""
        return self.refresh_on_401

    @property
    def RETRY_ATTEMPTS(self) -> int:
        """Get the number of retry attempts."""
        return self.retry_attempts

    @property
    def ALLOW_NON_IDEMPOTENT_RETRIES(self) -> bool:
        """Get the allow non-idempotent retries setting."""
        return self.allow_non_idempotent_retries

    @property
    def LOGGING_ENABLED(self) -> bool:
        """Get the logging enabled setting."""
        return self.logging_enabled

    @property
    def LOGGING_LEVEL(self) -> LogLevel:
        """Get the console logging level."""
        return self.logging_level

    @property
    def LOGGING_FILE_LEVEL(self) -> LogLevel:
        """Get the file logging level."""
        return self.logging_file_level

    @property
    def LOGGING_FILE_ENABLED(self) -> bool:
        """Get the file logging enabled setting."""
        return self.logging_file_enabled

    @property
    def LOGGING_CONSOLE_ENABLED(self) -> bool:
        """Get the console logging enabled setting."""
        return self.logging_console_enabled

    @property
    def LOGGING_INCLUDE_ENDPOINTS(self) -> bool:
        """Get the logging include endpoints setting."""
        return self.logging_include_endpoints

    @property
    def LOGGING_FILE_PATH(self) -> Path | None:
        """Get the logging file path."""
        return self.logging_file_path

    # --------- override API ---------

    def with_overrides(self, **kwargs: Any) -> Self:
        """Create a copy with selected fields changed."""
        return replace(self, **kwargs)


# -------------------------------------------------------------------
# Load / Merge
# -------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_base_settings() -> BaseSettings:
    """Load base framework settings from defaults, file, and environment.

    Load order:
        1. Built-in defaults
        2. Config file values ([default] and [user."<username>"])
        3. Environment variable overrides (UIO_API_*)
    """
    from .. import APPNAME

    # Resolve config dir
    cfg_dir_env = os.environ.get(f"{APPNAME}_CONFIG_DIR")
    cfg_dir = Path(cfg_dir_env) if cfg_dir_env else Path(resolve_config_dir())

    # Username
    username = os.environ.get(f"{APPNAME}_USERNAME") or _default_username()

    # Read configuration file and merge sections
    config_data = _read_config_file(cfg_dir)
    file_cfg = _merge_file_config(config_data, username=username)

    # Defaults (file values coerced safely)
    timeout = parse_float(file_cfg.get("timeout"), default=30.0)
    retry_attempts = parse_int(file_cfg.get("retry_attempts"), default=3)
    allow_non_idempotent = bool(file_cfg.get("allow_non_idempotent_retries", False))
    refresh_on_401 = bool(file_cfg.get("refresh_on_401", True))
    secrets_backend = _coerce_backend(
        str(file_cfg.get("secrets_backend"))
        if file_cfg.get("secrets_backend") is not None
        else None
    )

    # Logging defaults (opt-in)
    logging_enabled = bool(file_cfg.get("logging_enabled", False))
    logging_level = _coerce_log_level(
        str(file_cfg.get("logging_level")) if file_cfg.get("logging_level") is not None else None,
        default=LogLevel.INFO,
    )
    logging_file_level = _coerce_log_level(
        str(file_cfg.get("logging_file_level"))
        if file_cfg.get("logging_file_level") is not None
        else None,
        default=LogLevel.INFO,
    )
    logging_file_enabled = bool(file_cfg.get("logging_file_enabled", False))
    logging_console_enabled = bool(file_cfg.get("logging_console_enabled", False))
    logging_include_endpoints = bool(file_cfg.get("logging_include_endpoints", False))

    # ENV overrides (generic UIO_API_*)
    username = os.environ.get(f"{APPNAME}_USERNAME", username)

    env_timeout = os.environ.get(f"{APPNAME}_TIMEOUT")
    if env_timeout is not None:
        timeout = parse_float(env_timeout, default=timeout)

    env_ra = os.environ.get(f"{APPNAME}_RETRY_ATTEMPTS")
    if env_ra is not None:
        retry_attempts = parse_int(env_ra, default=retry_attempts)

    allow_non_idempotent = (
        _parse_bool(os.environ.get(f"{APPNAME}_ALLOW_NON_IDEMPOTENT_RETRIES"), allow_non_idempotent)
        or False
    )
    refresh_on_401 = (
        _parse_bool(os.environ.get(f"{APPNAME}_REFRESH_ON_401"), refresh_on_401) or False
    )
    secrets_backend = _coerce_backend(os.environ.get(f"{APPNAME}_SECRETS_BACKEND"))

    # Logging ENV overrides
    logging_enabled = (
        _parse_bool(os.environ.get(f"{APPNAME}_LOGGING_ENABLED"), logging_enabled) or False
    )
    logging_level = _coerce_log_level(
        os.environ.get(f"{APPNAME}_LOGGING_LEVEL"), default=logging_level
    )
    logging_file_level = _coerce_log_level(
        os.environ.get(f"{APPNAME}_LOGGING_FILE_LEVEL"), default=logging_file_level
    )
    logging_file_enabled = (
        _parse_bool(os.environ.get(f"{APPNAME}_LOGGING_FILE_ENABLED"), logging_file_enabled)
        or False
    )
    logging_console_enabled = (
        _parse_bool(
            os.environ.get(f"{APPNAME}_LOGGING_CONSOLE_ENABLED"),
            logging_console_enabled,
        )
        or False
    )
    logging_include_endpoints = (
        _parse_bool(
            os.environ.get(f"{APPNAME}_LOGGING_INCLUDE_ENDPOINTS"),
            logging_include_endpoints,
        )
        or False
    )

    # Logging file path
    logging_file_path: Path | None = None
    if file_cfg.get("logging_file_path"):
        logging_file_path = Path(str(file_cfg["logging_file_path"]))
    env_log_path = os.environ.get(f"{APPNAME}_LOGGING_FILE_PATH")
    if env_log_path:
        logging_file_path = Path(env_log_path)
    elif not logging_file_path:
        # Cross-platform default using platformdirs
        import platformdirs

        log_dir = Path(platformdirs.user_log_dir(APPNAME))
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        logging_file_path = log_dir / "uio_api.log"

    # Interactive policy (default: TTY)
    interactive = _parse_bool(os.environ.get(f"{APPNAME}_INTERACTIVE"), None)
    if interactive is None:
        interactive = _is_tty()

    # Secrets paths
    secrets_file_env = os.environ.get(f"{APPNAME}_SECRETS_FILE")
    secrets_file = Path(secrets_file_env) if secrets_file_env else Path(secrets_toml_path(cfg_dir))
    keyring_idx = keyring_index_path(cfg_dir)

    return BaseSettings(
        username=username,
        interactive=bool(interactive),
        secrets_backend=secrets_backend,
        config_dir=cfg_dir,
        secrets_file=secrets_file,
        keyring_index_file=keyring_idx,
        timeout=float(timeout),
        refresh_on_401=bool(refresh_on_401),
        retry_attempts=int(retry_attempts),
        allow_non_idempotent_retries=bool(allow_non_idempotent),
        logging_enabled=bool(logging_enabled),
        logging_level=logging_level,
        logging_file_level=logging_file_level,
        logging_file_enabled=bool(logging_file_enabled),
        logging_console_enabled=bool(logging_console_enabled),
        logging_include_endpoints=bool(logging_include_endpoints),
        logging_file_path=logging_file_path,
    )


def _read_config_file(cfg_dir: Path) -> dict[str, object]:
    """Read configuration from config.toml."""
    path = cfg_dir / "config.toml"
    if not path.exists():
        return {}
    with path.open("rb") as f:
        try:
            data = tomllib.load(f)
        except Exception:
            return {}
    return data or {}


def _merge_file_config(data: dict[str, object], username: str) -> dict[str, object]:
    """Merge [default] and [user.<username>] sections."""
    merged: dict[str, object] = {}
    default_tbl = data.get("default") or {}
    if isinstance(default_tbl, dict):
        merged.update(default_tbl)
    users_tbl = data.get("user") or {}
    if isinstance(users_tbl, dict):
        user_tbl = users_tbl.get(username) or {}
        if isinstance(user_tbl, dict):
            merged.update(user_tbl)
    return merged


# -------------------------------------------------------------------
# Logging initialization
# -------------------------------------------------------------------


def _init_logging() -> None:
    """Apply logging policy based on BaseSettings."""

    s = _load_base_settings()
    if not s.logging_enabled:
        return

    # setup_logging likely accepts strings; pass str values
    setup_logging(
        enable_console=s.logging_console_enabled,
        enable_file=s.logging_file_enabled,
        console_level=s.logging_level or LogLevel.SUCCESS,
        file_level=s.logging_file_level or LogLevel.WARNING,
        log_file=s.logging_file_path,
    )


# Public base settings instance (cached)
base_settings: BaseSettings = _load_base_settings()

# Initialize logging once at import
_init_logging()


def reload_base_settings() -> BaseSettings:
    """Reload settings and re-apply logging policy safely.

    Returns:
        BaseSettings: The reloaded base settings instance.
    """
    _load_base_settings.cache_clear()
    global base_settings
    base_settings = _load_base_settings()
    try:
        _init_logging()
    except Exception:
        # Never allow logging configuration to crash host apps
        pass
    return base_settings
