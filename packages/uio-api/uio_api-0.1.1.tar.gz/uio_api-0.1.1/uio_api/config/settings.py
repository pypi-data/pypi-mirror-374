"""Configuration management for UIO API wrapper.

This module provides centralized configuration management with support for:
- Environment variable overrides
- Configuration file support (TOML format)
- Hierarchical configuration (file → env → defaults)
- Cross-platform path resolution
- Type-safe configuration access
"""

import os
import sys
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import tomllib  # built-in since Python 3.11

from ..core.enums import AuthScheme, SecretsBackend
from ..core.tokens.scope import normalize_service_url
from .paths import keyring_index_path, resolve_config_dir, secrets_toml_path

# ----------------- helpers -----------------


def _parse_bool(v: str | None, default: bool | None) -> bool | None:
    """Parse a boolean value from a string.

    Args:
        v: String value to parse.
        default: Default value if parsing fails.

    Returns:
        Parsed boolean value or default.
    """
    if v is None:
        return default
    v = v.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off", ""}:
        return False
    return default


def _is_tty() -> bool:
    """Check if stdin is a TTY (interactive terminal).

    Returns:
        True if stdin is a TTY, False otherwise.
    """
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _default_username() -> str:
    """Get the default username from various sources.

    Returns:
        Username from environment variables or system.
    """
    return (
        os.environ.get("UIO_API_USERNAME")
        or os.environ.get("MREG_USERNAME")  # Backward compatibility
        or os.environ.get("USER")
        or os.environ.get("LOGNAME")
        or __import__("getpass").getpass.getuser()
    )


def _coerce_backend(s: str | None) -> SecretsBackend:
    """Coerce a string to a SecretsBackend enum value.

    Args:
        s: String value to coerce.

    Returns:
        SecretsBackend enum value.
    """
    if not s:
        return SecretsBackend.TOML
    s = s.strip().lower()
    return SecretsBackend.KEYRING if s == "keyring" else SecretsBackend.TOML


# ----------------- on-disk config loader -----------------


def _read_config_file(cfg_dir: Path) -> dict[str, object]:
    """Read configuration from a TOML file.

    Supports:
        [default]
        [user."<username>"]

    Args:
        cfg_dir: Configuration directory path.

    Returns:
        Parsed configuration dictionary.
    """
    path = cfg_dir / "config.toml"
    if not path.exists():
        return {}
    with path.open("rb") as f:
        try:
            return tomllib.load(f) or {}
        except Exception:
            # be robust: treat unreadable as empty
            return {}


def _merge_defaults(cfg_dir: Path, username: str) -> dict[str, object]:
    """Merge file-based defaults with user-specific overrides.

    Args:
        cfg_dir: Configuration directory path.
        username: Username for user-specific configuration.

    Returns:
        Merged configuration dictionary.
    """
    data = _read_config_file(cfg_dir)
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


# ----------------- public Settings model -----------------


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuration settings for the UIO API wrapper.

    This class holds all configuration settings with support for:
    - Type-safe access to configuration values
    - Uppercase convenience properties
    - Lightweight override API

    Attributes:
        url: MREG API base URL.
        username: Default username for authentication.
        interactive: Whether to use interactive authentication by default.
        secrets_backend: Backend for storing secrets (TOML or keyring).
        config_dir: Configuration directory path.
        secrets_file: Path to secrets TOML file.
        keyring_index_file: Path to keyring index file.
        token: Static token (if provided).
        token_file: Path to token file (if provided).
        scheme: Authentication scheme (default "Token").
        timeout: Request timeout in seconds.
        refresh_on_401: Whether to refresh tokens on 401 responses.
        page_size: Default page size for paginated requests.
        retry_attempts: Number of retry attempts for failed requests.
        allow_non_idempotent_retries: Whether to retry non-idempotent requests.
    """

    # Core
    url: str | None
    username: str | None
    interactive: bool
    secrets_backend: SecretsBackend

    # Paths (resolved)
    config_dir: Path
    secrets_file: Path
    keyring_index_file: Path

    # Cred sources
    token: str | None
    token_file: Path | None

    # HTTP/Auth behavior
    scheme: str
    timeout: float
    refresh_on_401: bool
    page_size: int | None

    # Retry behavior (high-level knobs; you can wire deeper as needed)
    retry_attempts: int
    allow_non_idempotent_retries: bool

    # --------- uppercase conveniences (nice ergonomics) ---------

    @property
    def URL(self) -> str | None:
        """Get the MREG API base URL."""
        return self.url

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
    def TOKEN(self) -> str | None:
        """Get the static token."""
        return self.token

    @property
    def TOKEN_FILE(self) -> Path | None:
        """Get the token file path."""
        return self.token_file

    @property
    def SCHEME(self) -> str:
        """Get the authentication scheme."""
        return self.scheme

    @property
    def TIMEOUT(self) -> float:
        """Get the request timeout."""
        return self.timeout

    @property
    def REFRESH_ON_401(self) -> bool:
        """Get the refresh on 401 setting."""
        return self.refresh_on_401

    @property
    def PAGE_SIZE(self) -> int | None:
        """Get the default page size."""
        return self.page_size

    @property
    def RETRY_ATTEMPTS(self) -> int:
        """Get the number of retry attempts."""
        return self.retry_attempts

    @property
    def ALLOW_NON_IDEMPOTENT_RETRIES(self) -> bool:
        """Get the allow non-idempotent retries setting."""
        return self.allow_non_idempotent_retries

    # --------- light override API ---------

    def with_overrides(self, **kwargs: object) -> "Settings":
        """Create a copy with selected fields changed.

        Args:
            **kwargs: Field names and values to override.

        Returns:
            New Settings instance with overridden values.

        Example:
            new_settings = settings.with_overrides(timeout=60.0, page_size=1000)
        """
        return replace(self, **cast(dict[str, Any], kwargs))


# ----------------- load & cache -----------------


@lru_cache(maxsize=1)
def _load() -> Settings:
    """Load configuration from various sources.

    Loads configuration in the following order:
    1. Built-in defaults
    2. Configuration file values
    3. Environment variable overrides

    Returns:
        Loaded Settings instance.
    """
    # Resolve config dir first (resilient even without HOME)
    cfg_dir = Path(os.environ.get("UIO_API_CONFIG_DIR") or resolve_config_dir())

    # Select a username early (used for config-file user section)
    username = (
        os.environ.get("UIO_API_USERNAME") or os.environ.get("MREG_USERNAME") or _default_username()
    )

    # Merge file-based defaults
    file_cfg = _merge_defaults(cfg_dir, username=username)

    # Start with built-in defaults
    url = None  # No default URL - must be configured per module
    scheme = str(file_cfg.get("scheme", AuthScheme.TOKEN.value))
    raw_timeout_obj = file_cfg.get("timeout", 30.0)
    if isinstance(raw_timeout_obj, (int, float, str)):
        timeout = float(raw_timeout_obj)
    else:
        timeout = 30.0
    page_size_obj = file_cfg.get("page_size")
    if isinstance(page_size_obj, (int, str)):
        page_size = int(page_size_obj)
    else:
        page_size = None
    raw_ra_obj = file_cfg.get("retry_attempts", 3)
    if isinstance(raw_ra_obj, (int, str)):
        retry_attempts = int(raw_ra_obj)
    else:
        retry_attempts = 3
    allow_non_idempotent = bool(file_cfg.get("allow_non_idempotent_retries", False))
    refresh_on_401 = bool(file_cfg.get("refresh_on_401", True))
    secrets_backend = _coerce_backend(str(file_cfg.get("secrets_backend", "")))

    # Apply ENV overrides (generic first, then MREG-specific for backward compatibility)
    url = os.environ.get("UIO_API_URL") or os.environ.get("MREG_URL") or url
    username = os.environ.get("UIO_API_USERNAME") or os.environ.get("MREG_USERNAME") or username
    scheme = os.environ.get("UIO_API_SCHEME") or os.environ.get("MREG_SCHEME") or scheme
    env_timeout = os.environ.get("UIO_API_TIMEOUT") or os.environ.get("MREG_TIMEOUT")
    if env_timeout is not None:
        timeout = float(env_timeout)
    page_size_env = os.environ.get("UIO_API_PAGE_SIZE") or os.environ.get("MREG_PAGE_SIZE")
    if page_size_env is not None:
        page_size = int(page_size_env)
    env_ra = os.environ.get("UIO_API_RETRY_ATTEMPTS") or os.environ.get("MREG_RETRY_ATTEMPTS")
    if env_ra is not None:
        retry_attempts = int(env_ra)
    allow_non_idempotent = (
        _parse_bool(
            os.environ.get("UIO_API_ALLOW_NON_IDEMPOTENT_RETRIES")
            or os.environ.get("MREG_ALLOW_NON_IDEMPOTENT_RETRIES"),
            allow_non_idempotent,
        )
        or False
    )
    refresh_on_401 = (
        _parse_bool(
            os.environ.get("UIO_API_REFRESH_ON_401") or os.environ.get("MREG_REFRESH_ON_401"),
            refresh_on_401,
        )
        or False
    )
    secrets_backend = _coerce_backend(
        os.environ.get("UIO_API_SECRETS_BACKEND") or os.environ.get("MREG_SECRETS_BACKEND")
    )

    # Cred sources from ENV
    token = os.environ.get("UIO_API_TOKEN") or os.environ.get("MREG_TOKEN") or None
    token_file_env = os.environ.get("UIO_API_TOKEN_FILE") or os.environ.get("MREG_TOKEN_FILE")
    token_file = Path(token_file_env) if token_file_env else None

    # Interactive policy (default: TTY)
    interactive = _parse_bool(
        os.environ.get("UIO_API_INTERACTIVE") or os.environ.get("MREG_INTERACTIVE"),
        None,
    )
    if interactive is None:
        interactive = _is_tty()

    # Resolve secrets paths
    secrets_file = Path(
        os.environ.get("UIO_API_SECRETS_FILE")
        or os.environ.get("MREG_SECRETS_FILE")
        or secrets_toml_path(cfg_dir)
    )
    keyring_idx = keyring_index_path(cfg_dir)

    # Normalize URL if present
    if url:
        url = normalize_service_url(url)

    return Settings(
        url=url,
        username=username,
        interactive=bool(interactive),
        secrets_backend=secrets_backend,
        config_dir=cfg_dir,
        secrets_file=secrets_file,
        keyring_index_file=keyring_idx,
        token=token,
        token_file=token_file,
        scheme=scheme,
        timeout=float(timeout),
        refresh_on_401=bool(refresh_on_401),
        page_size=page_size,
        retry_attempts=int(retry_attempts),
        allow_non_idempotent_retries=bool(allow_non_idempotent),
    )


# Public singleton
config: Settings = _load()


def reload() -> Settings:
    """Reload configuration (re-reads env and config.toml).

    Useful in REPL/tests when mutating env during runtime.

    Returns:
        Reloaded Settings instance.
    """
    _load.cache_clear()
    global config
    config = _load()
    return config
