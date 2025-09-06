"""HTTP authentication integration with automatic token refresh.

This module provides httpx.Auth integration that automatically adds
Authorization headers and handles token refresh on 401 responses.
"""

import threading
from http import HTTPStatus
from collections.abc import Generator

import httpx

from ..enums import AuthScheme
from .provider import SyncTokenProvider


class RefreshingTokenAuth(httpx.Auth):
    """HTTP authentication with automatic token refresh.

    This authentication handler automatically adds Authorization headers
    to requests and handles 401 Unauthorized responses by refreshing tokens
    and retrying the request once.

    The class is thread-safe and uses locking to prevent concurrent token
    refresh attempts.

    Attributes:
        _p: The token provider for getting and refreshing tokens.
        _scheme: The authentication scheme (default "Token").
        _lock: Thread lock for safe token refresh.
        _refresh_on_401: Whether to refresh tokens on 401 responses.

    Example:
        provider = InteractiveProvider(...)
        auth = RefreshingTokenAuth(provider, scheme="Token")
        client = httpx.Client(auth=auth)
    """

    requires_request_body = True
    requires_response_body = True

    def __init__(
        self,
        provider: SyncTokenProvider,
        *,
        scheme: str = AuthScheme.TOKEN.value,
        refresh_on_401: bool = True,
    ) -> None:
        """Initialize the authentication handler.

        Args:
            provider: Token provider for getting and refreshing tokens.
            scheme: Authentication scheme (default "Token").
            refresh_on_401: Whether to refresh tokens on 401 responses.
        """
        self._p = provider
        self._scheme = scheme
        self._lock = threading.Lock()
        self._refresh_on_401 = refresh_on_401

    def _apply(self, request: httpx.Request, token: str | None) -> None:
        """Apply the authorization header to a request.

        Args:
            request: The HTTP request to modify.
            token: The token to add to the Authorization header.
        """
        if token:
            request.headers["Authorization"] = f"{self._scheme} {token}"

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """Handle the authentication flow for a request.

        This method is called by httpx for each request. It:
        1. Gets the current token and adds it to the request
        2. Sends the request
        3. If the response is 401 and refresh is enabled, refreshes the token
        4. Retries the request with the new token

        Args:
            request: The HTTP request to authenticate.

        Yields:
            httpx.Request: The request with authentication headers applied.
        """

        token = self._p.get_token()
        self._apply(request, token)
        response = yield request

        if self._refresh_on_401 and response.status_code == HTTPStatus.UNAUTHORIZED:
            with self._lock:
                new_token = self._p.get_token()
                if not new_token or new_token == token:
                    new_token = self._p.refresh()
            req = httpx.Request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                content=request.content,
            )
            self._apply(req, new_token)
            response = yield req
        return
