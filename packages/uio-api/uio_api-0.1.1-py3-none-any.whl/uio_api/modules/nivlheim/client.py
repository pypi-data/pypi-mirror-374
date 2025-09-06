"""Nivlheim-specific client with APIKEY authentication.

This module provides a Nivlheim-specific client that uses APIKEY authentication
and handles the specific requirements of the Nivlheim API.
"""

from collections.abc import Generator
from dataclasses import field
from typing import Callable

import httpx

from ...core.client import ApiClient
from ...core.retry.policy import RetryStrategy, default_retry_strategy


class NivlheimClient(ApiClient):
    """Nivlheim-specific client with APIKEY authentication.

    This client automatically adds the APIKEY Authorization header to all requests
    and handles the Nivlheim API's specific requirements.

    Note: Nivlheim tokens are ephemeral and cannot be refreshed through the API.
    Token refresh must be handled externally (e.g., by re-obtaining from the web interface).
    """

    _module: str = field(init=False, repr=False, default="nivlheim")

    @property
    def module(self) -> str:  # satisfies the abstract property
        return self._module

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        retry: RetryStrategy | None = None,
        persist: bool = True,
        logout_func: Callable[[str, str], None] | None = None,
        page_size: int | None = None,
    ) -> None:
        # Compose headers with API key (adjust header name if your API uses a different one)
        merged_headers: dict[str, str] = {"Authorization": f"APIKEY {api_key}"}
        if headers:
            merged_headers.update({str(k): str(v) for k, v in headers.items()})

        super().__init__(
            base_url=base_url,
            auth=None,  # using header auth, not httpx.Auth
            timeout=timeout,
            retry=retry or default_retry_strategy(),  # ensure a concrete RetryStrategy
            headers=merged_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size,
        )


class APIKeyAuth(httpx.Auth):
    """HTTP authentication using Nivlheim APIKEY.

    This authentication handler adds the "Authorization: APIKEY <token>"
    header to all requests.
    """

    def __init__(self, api_key: str):
        """Initialize the APIKEY authentication.

        Args:
            api_key: The API key to use for authentication
        """
        self.api_key = api_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """Add the APIKEY authorization header to the request."""
        request.headers["Authorization"] = f"APIKEY {self.api_key}"
        yield request
