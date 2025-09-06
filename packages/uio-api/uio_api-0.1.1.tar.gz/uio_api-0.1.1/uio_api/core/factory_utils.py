"""Shared utilities for client factories to reduce code duplication.

This module provides common patterns and utilities used across different
API module factories to promote DRY principles.
"""

from pathlib import Path
from typing import Any

from .tokens.scope import TokenScope, normalize_service_url


def read_token_file(file_path: str | Path) -> str:
    """Read a token or API key from a file.

    Provides consistent error handling and file reading for token files
    used across different API modules.

    Args:
        file_path: Path to the token file.

    Returns:
        The token/key content as a string.

    Raises:
        ValueError: If file not found or cannot be read.

    Example:
        token = read_token_file("~/.mreg-token")
        api_key = read_token_file("~/.nivlheim-key")
    """
    path = Path(file_path).expanduser()
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        raise ValueError(f"Token file not found: {path}")
    except Exception as e:
        raise ValueError(f"Error reading token file {path}: {e}")


def apply_config_overrides(
    base_config: dict[str, Any], overrides: dict[str, Any]
) -> dict[str, Any]:
    """Apply configuration overrides to a base configuration.

    Creates a new configuration dict with overrides applied, preserving
    the original base_config dict.

    Args:
        base_config: The base configuration dictionary.
        overrides: Dictionary of override values (None values are ignored).

    Returns:
        A new dictionary with overrides applied.

    Example:
        base = {"url": "https://api.example.com", "timeout": 30.0}
        overrides = {"timeout": 60.0, "debug": None}  # None ignored
        result = apply_config_overrides(base, overrides)
        # result = {"url": "https://api.example.com", "timeout": 60.0}
    """
    result = base_config.copy()
    for key, value in overrides.items():
        if value is not None:
            result[key] = value
    return result


def normalize_secrets_backend(value: Any) -> str:
    """Normalize secrets backend to a lowercase string.

    Accepts enum-like objects with `.name`, plain strings, or other objects
    convertible to string. Returns one of: "toml", "keyring".
    """
    if value is None:
        return "toml"
    try:
        name = getattr(value, "name")
        if name:
            return str(name).lower()
    except Exception:
        pass
    return str(value).lower()


def validate_auth_method(*auth_methods: Any, method_names: list[str]) -> None:
    """Validate that at least one authentication method is provided.

    Args:
        *auth_methods: Authentication method values to check.
        method_names: Human-readable names for the methods.

    Raises:
        ValueError: If no authentication method is provided.

    Example:
        validate_auth_method(
            token, token_file, interactive,
            method_names=["token", "token_file", "interactive"]
        )
    """
    if not any(auth_methods):
        method_list = "\n".join(f"  - {name}" for name in method_names)
        raise ValueError(f"No authentication method provided. Choose one:\n{method_list}")


def create_client_headers(app_name: str, module_name: str, version: str) -> dict[str, str]:
    """Create standard HTTP headers for API clients.

    Args:
        app_name: The application name (e.g., "uio_api").
        module_name: The module name (e.g., "mreg", "nivlheim").
        version: The version string.

    Returns:
        Dictionary of HTTP headers.

    Example:
        headers = create_client_headers("uio_api", "mreg", "1.0.0")
        # {"User-Agent": "uio_api/1.0.0 (mreg)"}
    """
    return {"User-Agent": f"{app_name}/{version} ({module_name})"}


def normalize_url(url: str) -> str:
    """Normalize a service URL for consistent handling.

    Wrapper around the core URL normalization function for consistency
    across modules.

    Args:
        url: The URL to normalize.

    Returns:
        The normalized URL.
    """
    return normalize_service_url(url)


def get_config_value(config: dict[str, Any], key: str, default: Any = None) -> Any:
    """Get a value from configuration with consistent fallback.

    Args:
        config: Configuration dictionary.
        key: The key to look up.
        default: Default value if key not found or value is None.

    Returns:
        The configuration value or default.
    """
    value = config.get(key)
    return value if value is not None else default


def load_system_user_password(
    *,
    module: str,
    url: str,
    username: str,
    backend: str | Any | None,
    secrets_file: Path,
    keyring_index_file: Path,
) -> str:
    """Load a system user's stored password using the configured backend.

    This helper centralizes how we derive the token scope and which loader to use
    (TOML vs keyring), so modules can stay DRY.

    Args:
        module: Module name (e.g., "mreg", "ldap").
        url: Service base URL for scoping.
        username: System username.
        backend: Secrets backend ("toml"/"keyring" or enum-like with .name).
        secrets_file: Path to TOML secrets file.
        keyring_index_file: Path to keyring index file.

    Returns:
        The stored password as a string.

    Raises:
        ValueError: If the backend is unsupported or the secret cannot be loaded.
    """
    norm_url = normalize_service_url(url)
    scope = TokenScope(module=module, url=norm_url, username=username)

    backend_name: str
    if backend is None:
        backend_name = "toml"
    else:
        try:
            backend_name = str(getattr(backend, "name")).lower()
        except Exception:
            backend_name = str(backend).lower()

    if backend_name == "toml":
        # Late import to avoid heavy deps at module import time
        from .tokens.loader_toml import TomlTokenLoader

        toml_loader = TomlTokenLoader(path=secrets_file)
        token = toml_loader.read(scope)
        if token is None:
            raise ValueError(f"No password found for {username} in {secrets_file}")
        return token

    if backend_name == "keyring":
        from .tokens.loader_keyring import KeyringTokenLoader

        keyring_loader = KeyringTokenLoader(index_path=keyring_index_file)
        token = keyring_loader.read(scope)
        if token is None:
            raise ValueError(f"No password found for {username} in keyring")
        return token

    raise ValueError(f"Unsupported secrets backend: {backend_name}")
