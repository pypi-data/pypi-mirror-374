"""Configuration factory for creating API-specific configurations.

This module provides a factory for creating configuration instances
that can be customized per API module while inheriting from the base
framework configuration.
"""

from dataclasses import replace
from pathlib import Path
from typing import Any

from .settings import Settings, config as base_config


def create_config(
    *,
    url: str | None = None,
    username: str | None = None,
    scheme: str | None = None,
    timeout: float | None = None,
    page_size: int | None = None,
    retry_attempts: int | None = None,
    allow_non_idempotent_retries: bool | None = None,
    refresh_on_401: bool | None = None,
    secrets_backend: str | None = None,
    token: str | None = None,
    token_file: Path | str | None = None,
    interactive: bool | None = None,
    **kwargs: Any,
) -> Settings:
    """Create a configuration instance with API-specific overrides.

    This factory creates a new Settings instance based on the base configuration
    with the provided overrides. This allows each API module to have its own
    configuration while inheriting sensible defaults from the framework.

    Args:
        url: API base URL (required for most APIs).
        username: Default username for authentication.
        scheme: Authentication scheme (e.g., "Token", "Bearer").
        timeout: Request timeout in seconds.
        page_size: Default page size for paginated requests.
        retry_attempts: Number of retry attempts for failed requests.
        allow_non_idempotent_retries: Whether to retry non-idempotent requests.
        refresh_on_401: Whether to refresh tokens on 401 responses.
        secrets_backend: Backend for storing secrets ("toml" or "keyring").
        token: Static token for authentication.
        token_file: Path to token file.
        interactive: Whether to use interactive authentication.
        **kwargs: Additional configuration overrides.

    Returns:
        New Settings instance with the specified overrides.

    Example:
        # Create MREG-specific configuration
        mreg_config = create_config(
            url="https://mreg.uio.no",
            scheme="Token",
            page_size=1000,
        )

        # Create another API configuration
        other_config = create_config(
            url="https://api.example.com",
            scheme="Bearer",
            timeout=60.0,
        )
    """
    # Start with base configuration
    # Start with base configuration (Settings instance)
    new_config = base_config

    # Apply overrides
    overrides: dict[str, Any] = {}
    if url is not None:
        overrides["url"] = url
    if username is not None:
        overrides["username"] = username
    if scheme is not None:
        overrides["scheme"] = scheme
    if timeout is not None:
        overrides["timeout"] = timeout
    if page_size is not None:
        overrides["page_size"] = page_size
    if retry_attempts is not None:
        overrides["retry_attempts"] = retry_attempts
    if allow_non_idempotent_retries is not None:
        overrides["allow_non_idempotent_retries"] = allow_non_idempotent_retries
    if refresh_on_401 is not None:
        overrides["refresh_on_401"] = refresh_on_401
    if secrets_backend is not None:
        from ..core.enums import SecretsBackend

        overrides["secrets_backend"] = (
            SecretsBackend.TOML if secrets_backend.lower() == "toml" else SecretsBackend.KEYRING
        )
    if token is not None:
        overrides["token"] = token
    if token_file is not None:
        overrides["token_file"] = Path(token_file) if isinstance(token_file, str) else token_file
    if interactive is not None:
        overrides["interactive"] = interactive

    # Add any additional kwargs
    overrides.update(kwargs)

    # Create new instance with overrides
    return replace(new_config, **overrides)
