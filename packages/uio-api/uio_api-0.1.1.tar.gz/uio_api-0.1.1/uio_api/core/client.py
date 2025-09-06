"""Generic HTTP Client Implementation.

This module provides the main ApiClient class for interacting with any REST API.
It includes automatic retry logic, token refresh handling, and robust pagination
that handles malformed API responses gracefully.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from http import HTTPStatus
from time import sleep
from types import TracebackType
from typing import Any, Callable, Self
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from ..config import load_settings
from ..logging import logger
from .enums import RetryDecision, SecretsBackend
from .retry.policy import RetryStrategy, default_retry_strategy
from .tokens.loader_abstract import AbstractTokenLoader
from .tokens.loader_keyring import KeyringTokenLoader
from .tokens.loader_toml import TomlTokenLoader
from .tokens.scope import TokenScope, normalize_service_url
from .factory_utils import normalize_secrets_backend


@dataclass(slots=True)
class ApiClient(ABC):
    """Generic HTTP client for API interactions.

    This client provides a high-level interface for making requests to any REST API
    with built-in retry logic, authentication, and robust pagination support.

    Note: This class is not thread-safe. Do not share instances across threads
    or make concurrent requests on the same instance.

    Attributes:
        base_url: The base URL for the API (e.g., "https://api.example.com").
        auth: Optional httpx.Auth instance for authentication.
        timeout: Request timeout in seconds. Defaults to 30.0.
        retry: Retry strategy for handling transient failures.
        headers: Optional default headers to include with all requests.
        persist: Whether to persist token on logout. Defaults to True.
        logout_func: Optional function to call for token logout/revocation.
        page_size: Default page size for paginated requests. None uses API default.
        _client: Internal httpx.Client instance. Created lazily.

    Example:
        Basic usage::

            client = ApiClient(base_url="https://api.example.com")
            with client:
                response = client.request("GET", "/api/v1/resources/")

        Using convenience methods::

            with client:
                # Get a specific resource
                resource = client.get("/api/v1/resources/123")

                # Get all resources with automatic pagination
                all_resources = client.get_all("/api/v1/resources/")
    """

    @property
    @abstractmethod
    def module(self) -> str:
        """Return the module name for this client (e.g., "mreg", "nivlheim").

        This property is used to determine which configuration and token storage
        to use for this client instance.

        Returns:
            The module name as a string.
        """
        pass

    base_url: str
    auth: httpx.Auth | None = None
    timeout: float = 30.0
    retry: RetryStrategy = field(default_factory=lambda: default_retry_strategy())
    headers: dict[str, str] | None = None
    persist: bool = True
    logout_func: Callable[[str, str], None] | None = None
    page_size: int | None = None
    _client: httpx.Client | None = field(default=None, init=False, repr=False)

    def open(self) -> Self:
        """Open the HTTP client connection.

        Creates the internal httpx.Client instance if it doesn't exist.
        This method is called automatically when using the client as a context manager.

        Returns:
            Self for method chaining.

        Example:
            client = ApiClient(base_url="https://api.example.com")
            client.open()  # Creates internal httpx.Client
        """
        if self._client is None:
            logger.bind(endpoint=self.base_url).debug("Opening HTTP client for {}", self.base_url)
            # Add default Accept header to avoid content-type surprises
            base_headers: dict[str, str] = {"Accept": "application/json"}
            merged: dict[str, str] = {**base_headers, **(self.headers or {})}
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                auth=self.auth,
                headers=merged,
            )
        else:
            # Ensure live client reflects any updated timeout/auth/headers since last open.
            # (no-op if unchanged)
            self._client.timeout = self.timeout
            if self.auth is not None:
                self._client.auth = self.auth
            if self.headers is not None:
                self._client.headers.update(self.headers)
        return self

    def close(self) -> None:
        """Close the HTTP client connection.

        Closes the internal httpx.Client instance and cleans up resources.
        This method is called automatically when exiting the context manager.

        Example:
            client = ApiClient(base_url="https://api.example.com")
            client.open()
            # ... make requests ...
            client.close()  # Clean up resources
        """
        if self._client is None:
            return
        logger.bind(endpoint=self.base_url).debug("Closing HTTP client for {}", self.base_url)
        self._client.close()
        self._client = None

    def _execute_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        json: dict[str, Any] | None,
        return_raw: bool,
    ) -> httpx.Response:
        """Execute HTTP request with retry logic. Internal method shared by request() and get_response()."""
        # Normalize path: ensure leading slash (preserve trailing slash semantics)
        if not path.startswith("/"):
            path = "/" + path

        attempt = 1
        last_response = None
        last_exception = None

        while True:
            try:
                client = self._client or httpx.Client(
                    base_url=self.base_url,
                    timeout=self.timeout,
                    auth=self.auth,
                    headers=self.headers,
                )
                own = client is not self._client
                try:
                    logger.bind(endpoint=path).debug(
                        "Making {} request to {}", method.upper(), path
                    )
                    r = client.request(method.upper(), path, params=params, json=json)
                    last_response = r

                    if return_raw:
                        return r

                    if 200 <= r.status_code < 300:
                        logger.bind(endpoint=path).success(
                            "Request successful: {} {}", r.status_code, r.reason_phrase
                        )
                        return r

                    logger.bind(endpoint=path).warning(
                        "Request failed: {} {}", r.status_code, r.reason_phrase
                    )
                    decision, delay = self.retry(
                        attempt, method, f"{self.base_url}{path}", r.status_code, None
                    )
                finally:
                    if own:
                        client.close()
            except Exception as e:
                last_exception = e
                logger.bind(endpoint=path).error("Request exception: {}", e)
                decision, delay = self.retry(attempt, method, f"{self.base_url}{path}", None, e)

            if decision == RetryDecision.RETRY and delay is not None:
                logger.bind(endpoint=path).info(
                    "Retrying request in {:.3f}s (attempt {}/{})",
                    delay,
                    attempt + 1,
                    self._get_max_attempts(),
                )
                sleep(delay)
                attempt += 1
                continue

            # No more retries - raise appropriate error
            self._raise_request_error(method, path, last_response, last_exception)

    def _process_response(self, response: httpx.Response, path: str) -> Any:
        """Process HTTP response, handling JSON parsing and fallbacks."""
        ctype = response.headers.get("content-type", "").lower()

        # Improved JSON detection: support application/*+json and charset suffixes
        if "application/json" in ctype or "application/" in ctype and "+json" in ctype:
            try:
                return response.json()
            except Exception:
                # If JSON parsing fails, fall back to text
                logger.bind(endpoint=path).warning(
                    "Failed to parse JSON response, returning as text"
                )
                return response.text

        return response.text

    def _get_max_attempts(self) -> int:
        """Get maximum retry attempts from retry strategy if available."""
        # This is a best-effort heuristic; not all retry strategies expose max_attempts
        try:
            if hasattr(self.retry, "__wrapped__"):
                # For functools.partial or similar
                return getattr(self.retry.__wrapped__, "max_attempts", 3)
            return getattr(self.retry, "max_attempts", 3)
        except Exception:
            return 3

    def _raise_request_error(
        self, method: str, path: str, response: httpx.Response | None, exception: Exception | None
    ) -> None:
        """Raise appropriate error with enhanced context."""
        request_info = f"{method.upper()} {self.base_url}{path}"

        # Handle HTTP errors with response
        if response is not None:
            error_msg = f"HTTP {response.status_code} {response.reason_phrase} for {request_info}"
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as http_err:
                # Re-raise with enhanced context
                raise httpx.HTTPStatusError(
                    error_msg, request=response.request, response=response
                ) from http_err

        # Handle network or other errors
        error_msg = f"Request failed for {request_info}: {exception}"
        if isinstance(exception, httpx.RequestError):
            # Re-raise network errors with more context
            raise httpx.RequestError(error_msg, request=exception.request) from exception
        else:
            # Wrap other exceptions
            raise RuntimeError(error_msg) from exception

    def logout(self) -> None:
        """Logout and revoke the current token if logout function is available.

        Attempts to revoke the current authentication token by calling the
        logout function. This is a best-effort operation - if the logout
        fails, it will be silently ignored.

        Example:
            client = ApiClient(base_url="https://api.example.com", persist=False)
            with client:
                # ... make requests ...
                client.logout()  # Manually revoke token
        """
        if self.logout_func and self.auth:
            if hasattr(self.auth, "_p") and hasattr(self.auth._p, "get_token"):
                token = self.auth._p.get_token()
                if token:
                    try:
                        self.logout_func(token, self.base_url)
                    except Exception:
                        pass  # Best effort logout

    def set_auth(self, auth: httpx.Auth) -> None:
        """Set the authentication method for this client.

        This provides a public API to change the authentication method
        after the client has been created, avoiding direct access to _client.

        Args:
            auth: The httpx.Auth instance to use for authentication.

        Example:
            from uio_api.core.auth.httpx_auth import RefreshingTokenAuth
            from uio_api.core.auth.provider import StaticProvider

            custom_auth = RefreshingTokenAuth(
                StaticProvider(token="new-token"),
                scheme="Bearer"
            )
            client.set_auth(custom_auth)
        """
        self.auth = auth
        if self._client:
            self._client.auth = auth

    def update_headers(self, headers: dict[str, str]) -> None:
        """Update the headers for this client.

        This allows updating headers after the client has been opened.
        Note: If the client hasn't been opened yet, headers will be merged
        when open() is called.

        Args:
            headers: Dictionary of headers to merge with existing headers.

        Example:
            client.update_headers({
                "X-API-Version": "v2",
                "X-Custom": "value"
            })
        """
        if self.headers is None:
            self.headers = {}
        self.headers.update(headers)

        # Update the live client if it's already opened
        if self._client:
            self._client.headers.update(headers)

    def add_system_user(
        self,
        username: str,
        password: str,
        *,
        url: str | None = None,
        secrets_backend: str | None = None,
    ) -> None:
        """Add a system user for this client's module with automatic URL resolution.

        This method stores system user credentials for this client's module and automatically
        resolves the URL using the module's configuration if not provided.

        Args:
            username: The username for the system account.
            password: The password for the system account.
            url: The API URL. If None, uses module's configured URL.
            secrets_backend: Override the secrets backend. If None, uses module config.

        Raises:
            ValueError: If no URL is available or secrets backend is unsupported.

        Example:
            # Add system user for this client's module
            client.add_system_user(username="service-account", password="secret-password")
        """
        # Resolve URL from module config if not provided
        if url is None:
            settings = load_settings(self.module)
            url = settings.URL
            if not url:
                raise ValueError(f"No URL provided and no {self.module.upper()}_URL configured")

        # Select secrets backend from argument or settings

        settings = load_settings(self.module)
        backend = secrets_backend or settings.SECRETS_BACKEND
        backend_name = normalize_secrets_backend(backend)

        # Create appropriate loader
        loader: AbstractTokenLoader
        if backend_name in {"toml", str(SecretsBackend.TOML).lower()}:
            from .tokens.loader_toml import TomlTokenLoader

            loader = TomlTokenLoader(path=settings.SECRETS_FILE)
        elif backend_name in {"keyring", str(SecretsBackend.KEYRING).lower()}:
            from .tokens.loader_keyring import KeyringTokenLoader

            loader = KeyringTokenLoader(index_path=settings.KEYRING_INDEX_FILE)
        else:
            raise ValueError(f"Unsupported secrets backend: {backend_name}")

        scope = TokenScope(module=self.module, url=normalize_service_url(url), username=username)

        # Transactional write
        try:
            with loader.transaction():
                loader.write(scope, password)
        except Exception:
            raise

    def add_token(
        self,
        username: str,
        token: str,
        *,
        url: str | None = None,
        scheme: str | None = None,
        secrets_backend: str | None = None,
        refresh_on_401: bool | None = None,
        timeout: float | None = None,
        retry_attempts: int | None = None,
        allow_non_idempotent_retries: bool | None = None,
        page_size: int | None = None,
        persist: bool = True,
    ) -> None:
        """Add a token for this client's module with automatic configuration.

        This method stores authentication tokens for this client's module with automatic
        URL resolution and module-appropriate defaults.

        Args:
            username: The username associated with this token.
            token: The authentication token to store.
            url: The API URL. If None, uses module's configured URL.
            scheme: Authentication scheme. If None, uses module default.
            secrets_backend: Override the secrets backend. If None, uses module config.
            refresh_on_401: Whether to refresh tokens on 401. If None, uses module default.
            timeout: Request timeout in seconds. If None, uses module default.
            retry_attempts: Maximum retry attempts. If None, uses module default.
            allow_non_idempotent_retries: Whether to retry non-idempotent methods.
            page_size: Default page size. If None, uses module default.
            persist: Whether to persist tokens to storage.

        Raises:
            ValueError: If no URL is available or secrets backend is unsupported.

        Example:
            # Add token for this client's module
            client.add_token(username="myuser", token="abc123token")
        """
        # Resolve URL from module config if not provided
        if url is None:
            from ..config import load_settings

            settings = load_settings(self.module)
            url = settings.URL
            if not url:
                if self.module == "nivlheim":
                    url = "https://nivlheim.uio.no"
                else:
                    raise ValueError(f"No URL provided and no {self.module.upper()}_URL configured")

        # Persist token using configured backend (other knobs are not stored here)

        settings = load_settings(self.module)
        backend = secrets_backend or settings.SECRETS_BACKEND
        backend_name = normalize_secrets_backend(backend)

        loader: AbstractTokenLoader
        if backend_name == "toml":
            loader = TomlTokenLoader(path=settings.SECRETS_FILE)
        elif backend_name == "keyring":
            loader = KeyringTokenLoader(index_path=settings.KEYRING_INDEX_FILE)
        else:
            raise ValueError(f"Unsupported secrets backend: {backend_name}")

        scope = TokenScope(module=self.module, url=normalize_service_url(url), username=username)

        try:
            with loader.transaction():
                loader.write(scope, token)
        except Exception:
            raise

    def get_response(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an HTTP request and return the raw httpx.Response.

        This is similar to request() but returns the raw httpx.Response
        instead of auto-parsing JSON, giving you full control over the response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: Request path (relative to base_url).
            params: Optional query parameters.
            json: Optional JSON payload for POST/PUT requests.

        Returns:
            The raw httpx.Response object.

        Raises:
            httpx.HTTPStatusError: For HTTP error responses.
            httpx.RequestError: For network/connection errors.

        Example:
            response = client.get_response("GET", "/api/v1/data/")
            if response.status_code == 200:
                data = response.json()  # Manual JSON parsing
                print(f"Content-Type: {response.headers.get('content-type')}")
        """
        return self._execute_request(method, path, params, json, return_raw=True)

    def __enter__(self) -> Self:
        """Enter the context manager.

        Opens the HTTP client connection and returns self for use in the context.

        Returns:
            Self for use in the with statement.
        """
        return self.open()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the context manager.

        Handles cleanup when exiting the context manager:
        - Calls logout if persist is False
        - Closes the HTTP client connection

        Args:
            exc_type: Exception type if an exception occurred.
            exc: Exception instance if an exception occurred.
            tb: Traceback if an exception occurred.
        """
        if not self.persist:
            self.logout()
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP request with automatic retry logic.

        This is the core method for making HTTP requests. It includes:
        - Automatic retry logic based on the configured retry strategy
        - Token refresh handling for 401 responses
        - JSON response parsing for application/json content types
        - Proper error handling and status code checking

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: Request path (relative to base_url).
            params: Optional query parameters.
            json: Optional JSON payload for POST/PUT requests.

        Returns:
            Parsed JSON response if content-type is application/json,
            otherwise the response text.

        Raises:
            httpx.HTTPStatusError: For HTTP error responses after retries are exhausted.
            httpx.RequestError: For network/connection errors after retries are exhausted.

        Example:
            # GET request
            resources = client.request("GET", "/api/v1/resources/")

            # POST request with JSON payload
            new_resource = client.request(
                "POST",
                "/api/v1/resources/",
                json={"name": "example", "type": "test"}
            )

            # GET request with query parameters
            filtered_resources = client.request(
                "GET",
                "/api/v1/resources/",
                params={"type": "active"}
            )
        """
        response = self._execute_request(method, path, params, json, return_raw=False)
        return self._process_response(response, path)

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        ok404: bool = False,
        post_process: Callable[[Any], Any] | None = None,
    ) -> Any:
        """Convenience method for GET requests.

        Args:
            path: Request path (relative to base_url).
            params: Optional query parameters.
            ok404: If True, return empty result for 404 errors instead of raising.
            post_process: Optional function to process the response.

        Returns:
            API response, optionally processed by post_process function.

        Example:
            # Get a specific resource
            resource = client.get("/api/v1/resources/123")

            # Get resources with filtering
            resources = client.get("/api/v1/resources/", params={"type": "active"})

            # Safe get - returns empty result if resource doesn't exist
            resource = client.get("/api/v1/resources/nonexistent", ok404=True)
        """
        try:
            payload = self.request("GET", path, params=params)
            return post_process(payload) if post_process else payload
        except Exception as e:
            if (
                ok404
                and hasattr(e, "response")
                and e.response is not None
                and e.response.status_code == HTTPStatus.NOT_FOUND
            ):
                empty: dict[str, Any] = {"count": 0, "next": None, "results": []}

                return post_process(empty) if post_process else empty
            raise

    def post(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Convenience method for POST requests.

        Args:
            path: Request path (relative to base_url).
            json: JSON data to send in the request body.
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("POST", path, json=json, params=params)

    def put(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Convenience method for PUT requests.

        Args:
            path: Request path (relative to base_url).
            json: JSON data to send in the request body.
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("PUT", path, json=json, params=params)

    def patch(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Convenience method for PATCH requests.

        Args:
            path: Request path (relative to base_url).
            json: JSON data to send in the request body.
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("PATCH", path, json=json, params=params)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Convenience method for DELETE requests.

        Args:
            path: Request path (relative to base_url).
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("DELETE", path, params=params)

    def head(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Convenience method for HEAD requests.

        Args:
            path: Request path (relative to base_url).
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("HEAD", path, params=params)

    def options(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Convenience method for OPTIONS requests.

        Args:
            path: Request path (relative to base_url).
            params: Optional query parameters.

        Returns:
            Raw API response.
        """
        return self.request("OPTIONS", path, params=params)

    def get_all(
        self,
        path: str,
        *,
        page_size: int | None = None,
        params: dict[str, Any] | None = None,
        max_pages: int = 10000,
    ) -> list[Any]:
        """Get all results from a paginated endpoint with robust error handling.

        Automatically handles pagination by following 'next' URLs and collecting
        all results across pages. This method is designed to handle malformed
        API responses gracefully and includes multiple safety guards.

        Key features:
        - Treats filters & page_size as sticky (re-applied if API drops them)
        - Uses server-provided next URLs as source of truth
        - Repairs next URLs if they drop required query parameters
        - Guards against infinite loops via seen-URL tracking and max_pages limit
        - Stops pagination when results are empty or no next URL is provided

        Args:
            path: The API endpoint path.
            page_size: Override the default page size. Use -1 for maximum.
            params: Additional query parameters that will be preserved across pages.
            max_pages: Maximum number of pages to fetch (safety guard).

        Returns:
            List of all results across all pages.

        Example:
            # Get all resources (handles pagination automatically)
            all_resources = client.get_all("/api/v1/resources/")

            # Get all resources with custom page size
            all_resources = client.get_all("/api/v1/resources/", page_size=500)

            # Get all resources with filtering
            active_resources = client.get_all(
                "/api/v1/resources/",
                params={"type": "active"}
            )

            # Use maximum page size
            all_items = client.get_all("/api/v1/items/", page_size=-1)
        """
        # Determine effective page size
        effective_page_size = page_size if page_size is not None else self.page_size
        if effective_page_size == -1:
            effective_page_size = 1000  # API maximum

        # Build initial params (sticky across all pages)
        sticky_params = dict(params or {})
        if effective_page_size is not None:
            sticky_params.setdefault("page_size", effective_page_size)

        all_results: list[Any] = []
        page_num = 1
        total_count: int | None = None
        total_pages: int | None = None
        seen: set[str] = set()

        logger.bind(endpoint=path).debug(
            "Starting paginated request to {} with page_size={}", path, effective_page_size
        )

        current_path = path
        current_params: dict[str, Any] | None = sticky_params

        while True:
            # Safety guard against infinite loops
            if page_num > max_pages:
                logger.bind(endpoint=current_path).warning(
                    "Pagination aborted after {} pages (safety guard).", max_pages
                )
                break

            logger.bind(endpoint=current_path).debug(
                "Fetching page {} from {}", page_num, current_path
            )
            page = self.request("GET", current_path, params=current_params)

            # Extract results from this page
            if isinstance(page, dict) and "results" in page:
                results = page.get("results") or []
            elif isinstance(page, list):
                results = page
            else:
                # Non-standard: treat as single page payload
                results = [page]

            if not isinstance(results, list):
                logger.debug("Unexpected page payload; stopping pagination.")
                break

                # Stop if we got no results (empty page)
                if not results:
                    logger.bind(endpoint=current_path).debug(
                        "Page {} returned no results. Stopping pagination.", page_num
                    )
                    break

            all_results.extend(results)

            # Capture total count for logging
            if total_count is None and isinstance(page, dict) and "count" in page:
                try:
                    total_count = int(page["count"])
                except Exception:
                    total_count = None
                if total_count and effective_page_size:
                    total_pages = (total_count + effective_page_size - 1) // effective_page_size
                    logger.bind(endpoint=current_path).debug(
                        "Total items: {}, estimated pages: {}", total_count, total_pages
                    )

            # Log progress
            if total_pages:
                logger.bind(endpoint=current_path).debug(
                    "Page {}/{}: {} results (total: {}/{})",
                    page_num,
                    total_pages,
                    len(results),
                    len(all_results),
                    total_count,
                )
            else:
                logger.bind(endpoint=current_path).debug(
                    "Page {}: {} results (total: {})", page_num, len(results), len(all_results)
                )

            # Check for next page
            next_url = page.get("next") if isinstance(page, dict) else None
            logger.bind(endpoint=current_path).debug("Next URL from payload: {}", next_url)

            if not next_url:
                logger.bind(endpoint=current_path).debug(
                    "Pagination complete. Total results: {}", len(all_results)
                )
                break

            # Normalize and repair next URL if needed
            norm_path, repaired = self._normalize_and_repair_next(
                next_url, sticky_params=sticky_params
            )
            if repaired:
                logger.bind(endpoint=norm_path).debug("Repaired next path: {}", norm_path)
            else:
                logger.bind(endpoint=norm_path).debug("Next path (verbatim): {}", norm_path)

            # Loop detection
            if norm_path in seen:
                logger.bind(endpoint=norm_path).warning(
                    "Detected pagination loop on {}; stopping.", norm_path
                )
                break
            seen.add(norm_path)

            # Setup for next iteration
            current_path = norm_path
            current_params = None  # Don't pass extra params after first request
            page_num += 1

        return all_results

    def _normalize_and_repair_next(
        self, next_url: str, *, sticky_params: dict[str, Any]
    ) -> tuple[str, bool]:
        """Normalize next URL and repair missing sticky parameters.

        Converts an absolute next URL to a relative path and ensures that
        sticky parameters (like filters and page_size) remain present even
        if the API dropped them in the next URL.

        Args:
            next_url: The absolute next URL from the API response.
            sticky_params: Parameters that should be preserved across pages.

        Returns:
            Tuple of (normalized_relative_path, was_repaired_flag).

        Example:
            # If API returns malformed next URL missing filters
            next_url = "https://api.example.com/resources/?page=2"
            sticky_params = {"type": "active", "page_size": 50}

            path, repaired = client._normalize_and_repair_next(next_url, sticky_params=sticky_params)
            # Returns: ("/resources/?page=2&type=active&page_size=50", True)
        """
        parsed = urlsplit(next_url)
        # Start from API's query as-is
        query_pairs = dict(parse_qsl(parsed.query, keep_blank_values=True))

        # Re-add any sticky params that the API dropped
        repaired = False
        for key, value in sticky_params.items():
            # Allow server to advance 'page'; only add missing keys
            if key == "page":
                continue
            if key not in query_pairs:
                query_pairs[key] = value
                repaired = True

        new_query = urlencode(query_pairs, doseq=True)
        # Keep path exactly as server provides; only swap in repaired query if needed
        normalized = urlunsplit(("", "", parsed.path, new_query, ""))  # relative path+query
        return normalized, repaired
