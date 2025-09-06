"""Cross-platform path resolution for configuration and secrets.

This module provides robust path resolution for configuration directories,
secrets files, and keyring index files with fallbacks for different platforms
and environments.
"""

import os
import tempfile
from pathlib import Path

from platformdirs import user_config_dir

from ..core.enums import DirPerm
from .. import APP


def _username_fallback() -> str:
    """Get username with robust fallbacks.

    Tries to get username from config first, then falls back to system sources.

    Returns:
        Username string.
    """
    # Try to get from config first, then fallback to system
    # use loaded settings to avoid a non-existent `config` attribute
    try:
        from .settings import config as _cfg

        if _cfg.USER_NAME:
            return _cfg.USER_NAME
    except Exception:
        pass

    for env in ("USER", "LOGNAME"):
        v = os.environ.get(env)
        if v:
            return v
    try:
        import getpass

        return getpass.getuser()
    except Exception:
        pass
    if hasattr(os, "getuid"):
        try:
            import pwd

            return pwd.getpwuid(os.getuid()).pw_name
        except Exception:
            return str(os.getuid())
    return "unknown"


def _safe_tmp_base(appname: str) -> Path:
    """Create a safe temporary base directory.

    Args:
        appname: Application name for the directory.

    Returns:
        Path to the temporary base directory.
    """
    # Cross-platform, always writable temp base
    tmp = Path(tempfile.gettempdir())
    user = _username_fallback()
    # Optional: sanitize user to a simple folder name
    safe_user = "".join(c for c in user if c.isalnum() or c in ("-", "_")) or "user"
    return tmp / safe_user / appname


def resolve_config_dir(
    *,
    appname: str = APP,
    override: str | os.PathLike[str] | None = None,
    create: bool = True,
) -> Path:
    """Resolve the configuration directory with robust fallbacks.

    Resolves configuration directory in the following order:
    1. Explicit override or UIO_API_CONFIG_DIR environment variable
    2. platformdirs.user_config_dir() (XDG on Linux, Library/Application Support on macOS, %APPDATA% on Windows)
    3. <tempdir>/<username>/<appname> as final fallback

    Args:
        appname: Application name for the directory.
        override: Explicit override path.
        create: Whether to create the directory if it doesn't exist.

    Returns:
        Path to the configuration directory.

    Example:
        # Get default config directory
        config_dir = resolve_config_dir()

        # Get config directory with custom app name
        config_dir = resolve_config_dir(appname="myapp")

        # Override with custom path
        config_dir = resolve_config_dir(override="/custom/path")
    """
    # 1) explicit override or config
    if override:
        base = Path(override).expanduser()
    else:
        # Try to get from config first, then fallback to env
        try:
            from .settings import config as _cfg

            base = _cfg.CONFIG_DIR
        except Exception:
            base = None

        # Fallback to environment variable if config not available
        if base is None and (env := os.environ.get(f"{APP.upper()}_CONFIG_DIR")):
            base = Path(env).expanduser()

    # 2) platformdirs default
    if base is None:
        # Ensure path is absolute; platformdirs guarantees this
        base = Path(user_config_dir(appname=appname))

    # 3) If base is unusable (e.g., is a file), fallback to temp
    if base.exists() and not base.is_dir():
        base = _safe_tmp_base(appname)
    elif not base.is_absolute():
        # Be defensive if someone passed a relative override/env
        base = base.expanduser().resolve()

    if create:
        base.mkdir(parents=True, exist_ok=True)
        # On POSIX, tighten permissions to 0700; on Windows, skip chmod
        if os.name == "posix":
            try:
                base.chmod(int(DirPerm.OWNER_RWX))  # typically 0o700
            except Exception:
                pass

    return base


def secrets_toml_path(config_dir: Path | None = None) -> Path:
    """Get the path to the secrets TOML file.

    Args:
        config_dir: Configuration directory. If None, uses default.

    Returns:
        Path to the secrets TOML file.

    Example:
        secrets_path = secrets_toml_path()
        # Returns: ~/.config/uio_api/secrets.toml (on Linux)
    """
    cfg = config_dir or resolve_config_dir()
    return cfg / "secrets.toml"


def keyring_index_path(config_dir: Path | None = None) -> Path:
    """Get the path to the keyring index file.

    Args:
        config_dir: Configuration directory. If None, uses default.

    Returns:
        Path to the keyring index file.

    Example:
        index_path = keyring_index_path()
        # Returns: ~/.config/uio_api/secrets.index.toml (on Linux)
    """
    cfg = config_dir or resolve_config_dir()
    return cfg / "secrets.index.toml"
