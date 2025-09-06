"""Nivlheim client factory with configuration support.

This module provides a factory function for creating Nivlheim API clients
with proper authentication and configuration support.
"""

from pathlib import Path
from typing import Any

from ...core.factory_utils import (
    apply_config_overrides,
    create_client_headers,
    get_config_value,
    read_token_file,
    validate_auth_method,
)
from ... import APP, __version__
from .client import NivlheimClient


def client(
    *,
    settings: dict[str, Any] | None = None,
    # Per-client overrides
    url: str | None = None,
    api_key: str | None = None,
    api_key_file: Path | str | None = None,
    timeout: float | None = None,
    **kwargs: Any,
) -> NivlheimClient:
    """Build a ready-to-use Nivlheim API client.

    This factory function creates NivlheimClient instances with proper authentication
    and client configuration. Nivlheim uses APIKEY authentication which is ephemeral
    and cannot be refreshed through the API.

    Args:
        settings: Optional settings dict to override defaults
        url: Nivlheim API base URL (e.g., "https://nivlheim.uio.no")
        api_key: API key for authentication (mutually exclusive with api_key_file)
        api_key_file: Path to file containing API key (mutually exclusive with api_key)
        timeout: Request timeout in seconds
        **kwargs: Additional arguments passed to NivlheimClient

    Returns:
        A configured NivlheimClient instance ready for use.

    Raises:
        ValueError: If neither api_key nor api_key_file is provided, or if both are provided.

    Example:
        # Using API key directly
        client = nivlheim_client(
            url="https://nivlheim.uio.no",
            api_key="your-api-key-here"
        )

        # Using API key from file
        client = nivlheim_client(
            url="https://nivlheim.uio.no",
            api_key_file="~/nivlheim-api-key.txt"
        )

        # Basic usage
        with client as c:
            hosts = c.get("/api/v2/hostlist", params={"fields": "hostname,lastseen"})
    """
    # Load base configuration
    base_config = {
        "url": "https://nivlheim.uio.no",
        "timeout": 30.0,
    }

    # Apply any provided settings
    if settings:
        base_config = apply_config_overrides(base_config, settings)

    # Apply per-client overrides
    overrides: dict[str, Any] = {}
    if url is not None:
        overrides["url"] = url
    if timeout is not None:
        overrides["timeout"] = timeout

    final_config = apply_config_overrides(base_config, overrides)

    # Extract final values
    final_url = str(get_config_value(final_config, "url"))
    final_timeout_obj = get_config_value(final_config, "timeout")
    final_timeout: float = (
        float(final_timeout_obj) if not isinstance(final_timeout_obj, float) else final_timeout_obj
    )

    # Validate authentication method
    if api_key is not None and api_key_file is not None:
        raise ValueError("Cannot specify both api_key and api_key_file")

    validate_auth_method(
        api_key,
        api_key_file,
        method_names=["api_key='your-key'", "api_key_file='path/to/key.txt'"],
    )

    # Resolve API key from file if needed
    if api_key_file is not None:
        api_key = read_token_file(api_key_file)

    # Create standard headers
    headers = create_client_headers(APP, "nivlheim", __version__)

    # Apply headers to kwargs if not already present
    if "headers" not in kwargs:
        kwargs["headers"] = headers
    else:
        # Merge with existing headers
        kwargs["headers"] = {**headers, **kwargs["headers"]}

    # Create client with APIKEY authentication
    if api_key is None:
        raise ValueError("api_key must be provided via api_key or api_key_file")
    return NivlheimClient(base_url=final_url, api_key=str(api_key), timeout=final_timeout, **kwargs)
