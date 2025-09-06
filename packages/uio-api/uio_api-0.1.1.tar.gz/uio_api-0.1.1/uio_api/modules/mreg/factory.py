"""MREG client factory for creating configured ApiClient instances.

This module provides the main client factory function that creates ApiClient
instances with proper authentication, configuration, and retry strategies
specifically configured for MREG API.
"""

from pathlib import Path
from typing import Callable

import httpx

from ... import APP, __version__
from ...config import load_settings
from ...config.module import ModuleSettings
from ...core.auth.httpx_auth import RefreshingTokenAuth
from ...core.auth.provider import (
    FileProvider,
    InteractiveProvider,
    IssueToken,
    StaticProvider,
    SystemAccountProvider,
)
from ...core.client import ApiClient
from ...core.factory_utils import create_client_headers
from ...core.retry.policy import RetryStrategy, default_retry_strategy
from ...core.tokens.loader_abstract import AbstractTokenLoader
from ...core.tokens.loader_keyring import KeyringTokenLoader
from ...core.tokens.loader_toml import TomlTokenLoader
from ...core.tokens.scope import TokenScope, normalize_service_url
from .client import MregClient
from .endpoints import Endpoint
from .profile import MregApiProfile


def _issuer(timeout: float) -> IssueToken:
    """Create a MREG token issuer function.

    Creates a function that issues tokens by making a POST request to the
    MREG token authentication endpoint.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        A function that issues tokens for the given username/password/URL.

    Example:
        issuer = _issuer(30.0)
        token = issuer("username", "password", "https://mreg.uio.no")
    """

    def issue(username: str, password: str | None, url: str) -> str:
        """Issue a token by authenticating with MREG API.

        Args:
            username: Username for authentication.
            password: Password for authentication.
            url: Base URL of the MREG API.

        Returns:
            The authentication token string.

        Raises:
            httpx.HTTPStatusError: If authentication fails.
            RuntimeError: If the response doesn't contain a token.
        """
        base = normalize_service_url(url)
        headers = {"Content-Type": "application/json"}
        with httpx.Client(base_url=base, timeout=timeout, headers=headers) as c:
            r = c.post(Endpoint.Login, json={"username": username, "password": password})
            r.raise_for_status()
            data = r.json() or {}
            token = data.get("token")
            if not token or not isinstance(token, str):
                raise RuntimeError("Auth response missing 'token' or token is not a string.")
            return str(token)

    return issue


def _logout(timeout: float) -> Callable[[str, str], None]:
    """Create a MREG token logout function.

    Creates a function that revokes tokens by making a POST request to the
    MREG token logout endpoint.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        A function that revokes tokens for the given token/URL.

    Example:
        logout_func = _logout(30.0)
        logout_func("token-string", "https://mreg.uio.no")
    """

    def run(token: str, url: str) -> None:
        """Revoke a token by calling the MREG logout endpoint.

        Args:
            token: The token to revoke.
            url: Base URL of the MREG API.

        Raises:
            httpx.HTTPStatusError: If logout fails.
        """
        if not MregApiProfile.logout_path:
            return
        base = normalize_service_url(url)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{MregApiProfile.scheme} {token}",
        }
        with httpx.Client(base_url=base, timeout=timeout, headers=headers) as c:
            r = c.post(MregApiProfile.logout_path)
            r.raise_for_status()

    return run


def _choose_loader(
    url: str, username: str | None, settings: ModuleSettings
) -> tuple[AbstractTokenLoader, TokenScope]:
    """Choose the appropriate token loader based on configuration.

    Selects either the TOML or Keyring token loader based on the configured
    secrets backend and creates the appropriate token scope.

    Args:
        url: The MREG API URL.
        username: The username for token scoping.
        settings: The module settings instance to use.

    Returns:
        A tuple of (loader, scope) for token management.

    Example:
        loader, scope = _choose_loader("https://mreg.uio.no", "bob-drift", settings)
    """
    backend_name = settings.SECRETS_BACKEND
    if hasattr(backend_name, "name"):
        backend_name = backend_name.name.lower()
    else:
        backend_name = str(backend_name).lower()

    if backend_name == "keyring":
        loader: AbstractTokenLoader = KeyringTokenLoader(index_path=settings.KEYRING_INDEX_FILE)
    else:
        loader = TomlTokenLoader(path=settings.SECRETS_FILE)

    scope = TokenScope(module=settings.module_name, url=url, username=username)
    return loader, scope


def client(
    *,
    settings: ModuleSettings | None = None,
    # Per-client overrides - ALL configuration knobs available
    url: str | None = None,
    username: str | None = None,
    token: str | None = None,
    token_file: Path | str | None = None,
    system_user: str | None = None,
    interactive: bool | None = None,
    persist_token: bool | None = None,
    headers: dict[str, str] | None = None,
    scheme: str | None = None,
    timeout: float | None = None,
    refresh_on_401: bool | None = None,
    page_size: int | None = None,
    retry_attempts: int | None = None,
    allow_non_idempotent_retries: bool | None = None,
    secrets_backend: str | None = None,
    retry_strategy: RetryStrategy | None = None,
    issue_token: IssueToken | None = None,
    prompt_username: Callable[[], str] | None = None,
    prompt_password: Callable[[str], str] | None = None,
    persist: bool = True,
) -> ApiClient:
    """Build a ready-to-use ApiClient configured for MREG API.

    This factory function creates ApiClient instances with proper authentication,
    token storage, and client configuration using the settings injection pattern.
    ALL configuration knobs are available for per-client override.

    Args:
        settings: Module settings instance. If None, loads from registry.
        url: Override the API URL.
        username: Override the username.
        token: Use a static token for authentication.
        token_file: Read token from a file.
        system_user: Use system account with username (password from secrets).
        interactive: Enable interactive authentication prompts.
        persist_token: Whether to persist tokens to storage.
        scheme: Authentication scheme.
        timeout: Request timeout in seconds.
        refresh_on_401: Whether to refresh tokens on 401 responses.
        page_size: Default page size for paginated requests.
        retry_attempts: Maximum number of retry attempts.
        allow_non_idempotent_retries: Whether to retry non-idempotent methods (POST/PUT).
        secrets_backend: Token storage backend ("toml" or "keyring").
        retry_strategy: Custom retry strategy.
        issue_token: Custom token issuer function.
        prompt_username: Custom username prompt function.
        prompt_password: Custom password prompt function.
        persist: Whether to logout tokens on client exit. Note: This controls logout
            behavior, while persist_token controls whether tokens are saved to storage
            for future use. Set persist=False to keep tokens valid after client session.

    Returns:
        A configured ApiClient instance ready for use with MREG API.

    Example:
        # Default use (loads from registry)
        with client() as m:
            hosts = m.get_all("/api/v1/hosts/")

        # With overrides - ALL parameters available per-client
        with client(
            url="https://test.mreg.uio.no",
            timeout=60.0,
            retry_attempts=5,
            secrets_backend="keyring",
            system_user="my-service-account"
        ) as m:
            hosts = m.get_all("/api/v1/hosts/")

        # With custom settings
        settings = load_settings("mreg").with_overrides(timeout=60.0)
        with client(settings=settings) as m:
            hosts = m.get_all("/api/v1/hosts/")
    """
    # Load settings if not provided
    if settings is None:
        settings = load_settings("mreg")

    # Apply per-client overrides - ALL configuration knobs available
    if url is not None:
        settings = settings.with_overrides(url=url)
    if username is not None:
        settings = settings.with_overrides(username=username)
    if token is not None:
        settings = settings.with_overrides(token=token)
    if token_file is not None:
        token_file_path = Path(token_file) if isinstance(token_file, str) else token_file
        settings = settings.with_overrides(token_file=token_file_path)
    if system_user is not None:
        settings = settings.with_overrides(system_user=system_user)
    if interactive is not None:
        settings = settings.with_overrides(interactive=interactive)
    if persist_token is not None:
        settings = settings.with_overrides(persist_token=persist_token)
    if scheme is not None:
        settings = settings.with_overrides(scheme=scheme)
    if timeout is not None:
        settings = settings.with_overrides(timeout=timeout)
    if refresh_on_401 is not None:
        settings = settings.with_overrides(refresh_on_401=refresh_on_401)
    if page_size is not None:
        settings = settings.with_overrides(page_size=page_size)
    if retry_attempts is not None:
        settings = settings.with_overrides(retry_attempts=retry_attempts)
    if allow_non_idempotent_retries is not None:
        settings = settings.with_overrides(
            allow_non_idempotent_retries=allow_non_idempotent_retries
        )
    if secrets_backend is not None:
        settings = settings.with_overrides(secrets_backend=secrets_backend)

    # Create headers (User-Agent + extra)
    base_headers = create_client_headers(APP, "mreg", __version__)
    if headers:
        base_headers.update(headers)

    # Resolve configuration with validation
    base_url = normalize_service_url(settings.URL or "")
    if not base_url:
        raise ValueError(
            "Missing MREG URL. Provide url= parameter or configure MREG_URL environment variable. "
            "Example: export MREG_URL=https://mreg.uio.no"
        )

    # Validate that we have some authentication method
    if not (token or token_file or system_user or interactive):
        raise ValueError(
            "No authentication method provided. Choose one:\n"
            "  - token='your-token' (static token)\n"
            "  - token_file='path/to/token.txt' (read from file)\n"
            "  - system_user='account-name' (system account)\n"
            "  - interactive=True (prompt for credentials)\n"
            "Or set MREG_TOKEN, MREG_TOKEN_FILE, or MREG_SYSTEM_USER environment variables."
        )

    username = settings.USER_NAME
    scheme = settings.SCHEME
    timeout = settings.TIMEOUT
    page_size = settings.PAGE_SIZE
    refresh_on_401 = settings.REFRESH_ON_401
    interactive = settings.INTERACTIVE
    persist_token = True if persist_token is None else persist_token

    token = settings.TOKEN
    token_file = settings.TOKEN_FILE
    system_user = settings.SYSTEM_USER

    # Retry strategy
    if retry_strategy is None:
        retry_strategy = default_retry_strategy(
            max_attempts=settings.RETRY_ATTEMPTS,
            allow_non_idempotent=settings.ALLOW_NON_IDEMPOTENT_RETRIES,
        )

    # ----- path 1: explicit token -----
    if token:
        auth = RefreshingTokenAuth(
            StaticProvider(token=token),
            scheme=scheme,
            refresh_on_401=False,  # static token → don't try to refresh
        )
        logout_func = _logout(timeout)
        client = MregClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size,
        )
        return client

    # ----- path 2: token file -----
    if token_file:
        auth = RefreshingTokenAuth(
            FileProvider(path=str(token_file)),
            scheme=scheme,
            refresh_on_401=refresh_on_401,
        )
        logout_func = _logout(timeout)
        client = MregClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size,
        )
        return client

    # ----- path 3: system account -----
    if system_user:
        loader, scope = _choose_loader(url=base_url, username=system_user, settings=settings)
        sys_provider = SystemAccountProvider(
            username_file="",  # Not used - we have username directly
            store=loader,
            scope=scope,
            issue=_issuer(timeout),
        )
        # Override the username directly since we have it from the parameter
        sys_provider.set_username(system_user)
        auth = RefreshingTokenAuth(sys_provider, scheme=scheme, refresh_on_401=refresh_on_401)
        logout_func = _logout(timeout)
        client = MregClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size,
        )
        return client

    # ----- path 4: interactive -----
    if interactive:
        loader, scope = _choose_loader(url=base_url, username=username, settings=settings)

        # default issuer if not provided
        issue = issue_token or _issuer(timeout)

        # default prompts if not provided
        if prompt_username is None:

            def default_username_prompt() -> str:
                if scope.username:
                    return scope.username
                import getpass

                return getpass.getuser()

            prompt_username = default_username_prompt
        if prompt_password is None:
            import getpass

            def _default_prompt_password(u: str) -> str:
                return getpass.getpass(f"Password for {u}: ")

            prompt_password = _default_prompt_password

        int_provider = InteractiveProvider(
            store=loader,
            scope=scope,
            issue=issue,
            prompt_username=prompt_username,
            prompt_password=prompt_password,
            persist=persist_token,
        )
        auth = RefreshingTokenAuth(int_provider, scheme=scheme, refresh_on_401=refresh_on_401)
        logout_func = _logout(timeout)
        client = MregClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size,
        )
        return client

    # ----- path 5: fail fast -----
    raise RuntimeError(
        "Failed to create MREG client: no valid authentication method found.\n\n"
        "Available authentication methods:\n"
        "1. Static token: client(token='your-token')\n"
        "2. Token file: client(token_file='path/to/token.txt')\n"
        "3. System account: client(system_user='account-name')\n"
        "4. Interactive: client(interactive=True)\n\n"
        "Or set environment variables: MREG_TOKEN, MREG_TOKEN_FILE, or MREG_SYSTEM_USER\n\n"
        "For help, see: https://github.com/your-org/uio-api#authentication"
    )
