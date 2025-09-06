"""Example API client factory.

This demonstrates how to create a client factory for a different API
using the configuration factory pattern.
"""

from pathlib import Path
from typing import Callable

import httpx

from ...core.auth.httpx_auth import RefreshingTokenAuth
from ...core.auth.provider import (
    FileProvider,
    InteractiveProvider,
    IssueToken,
    StaticProvider,
)
from ...core.client import ApiClient
from ...core.retry.policy import RetryStrategy, default_retry_strategy
from ...core.tokens.loader_abstract import AbstractTokenLoader
from ...core.tokens.loader_keyring import KeyringTokenLoader
from ...core.tokens.loader_toml import TomlTokenLoader
from ...core.tokens.scope import TokenScope, normalize_service_url
from ...config import create_config
from ...config.settings import Settings
from .profile import ExampleApiProfile


class ExampleClient(ApiClient):
    """Example concrete client implementation."""

    @property
    def module(self) -> str:
        return "example"


def _issuer(timeout: float) -> IssueToken:
    """Create an example token issuer function."""

    def issue(username: str, password: str | None, url: str) -> str:
        """Issue a token by authenticating with Example API."""
        base = normalize_service_url(url)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if ExampleApiProfile.login_path is None:
            raise RuntimeError("Example API login path not configured")

        with httpx.Client(base_url=base, timeout=timeout, headers=headers) as c:
            r = c.post(
                ExampleApiProfile.login_path,
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                },
            )
            r.raise_for_status()
            data = r.json() or {}
            token_val = data.get("access_token")
            if not token_val:
                raise RuntimeError("Auth response missing 'access_token'.")
            return str(token_val)

    return issue


def _choose_loader(
    url: str, username: str | None, config: Settings
) -> tuple[AbstractTokenLoader, TokenScope]:
    """Choose the appropriate token loader based on configuration."""
    if config.SECRETS_BACKEND.name.lower() == "keyring":
        loader: AbstractTokenLoader = KeyringTokenLoader(index_path=config.KEYRING_INDEX_FILE)
    else:
        loader = TomlTokenLoader(path=config.SECRETS_FILE)

    scope = TokenScope(module="example", url=url, username=username)
    return loader, scope


def client(
    *,
    url: str | None = None,
    username: str | None = None,
    token: str | None = None,
    token_file: Path | str | None = None,
    interactive: bool | None = None,
    persist_token: bool | None = None,
    headers: dict[str, str] | None = None,
    scheme: str | None = None,
    timeout: float | None = None,
    refresh_on_401: bool | None = None,
    page_size: int | None = None,
    retry_strategy: RetryStrategy | None = None,
    issue_token: IssueToken | None = None,
    prompt_username: Callable[[], str] | None = None,
    prompt_password: Callable[[str], str] | None = None,
    persist: bool = True,
) -> ExampleClient:
    """Build a ready-to-use ApiClient configured for Example API."""

    # Create Example-specific configuration
    example_config = create_config(
        url=url or "https://api.example.com",  # Example-specific default
        username=username,
        scheme=scheme or ExampleApiProfile.scheme,
        timeout=timeout,
        page_size=page_size,
        refresh_on_401=refresh_on_401,
        interactive=interactive,
        token=token,
        token_file=token_file,
    )

    # Create headers (User-Agent + extra)
    from ... import APP, __version__
    from ...core.factory_utils import create_client_headers

    base_headers = create_client_headers(APP, "example", __version__)
    if headers:
        base_headers.update(headers)

    # Resolve configuration
    base_url = normalize_service_url(example_config.URL or "")
    if not base_url:
        raise ValueError("Missing URL. Provide url= or set UIO_API_URL.")

    username = example_config.USER_NAME
    scheme = example_config.SCHEME
    timeout = example_config.TIMEOUT
    page_size = example_config.PAGE_SIZE
    refresh_on_401 = example_config.REFRESH_ON_401
    interactive = example_config.INTERACTIVE
    persist_token = True if persist_token is None else persist_token

    token = example_config.TOKEN
    token_file = example_config.TOKEN_FILE

    # Retry strategy
    if retry_strategy is None:
        retry_strategy = default_retry_strategy(
            max_attempts=example_config.RETRY_ATTEMPTS,
            allow_non_idempotent=example_config.ALLOW_NON_IDEMPOTENT_RETRIES,
        )

    # Static token path
    if token:
        auth = RefreshingTokenAuth(
            StaticProvider(token=token),
            scheme=scheme,
            refresh_on_401=False,
        )
        return ExampleClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            page_size=page_size,
        )

    # Token file path
    if token_file:
        auth = RefreshingTokenAuth(
            FileProvider(path=str(token_file)),
            scheme=scheme,
            refresh_on_401=refresh_on_401,
        )
        return ExampleClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            page_size=page_size,
        )

    # Interactive path
    if interactive:
        loader, scope = _choose_loader(url=base_url, username=username, config=example_config)
        issue = issue_token or _issuer(timeout or 30.0)

        if prompt_username is None:

            def _default_prompt_username() -> str:
                return scope.username or __import__("getpass").getpass.getuser()

            prompt_username = _default_prompt_username
        if prompt_password is None:
            import getpass

            def _default_prompt_password(u: str) -> str:
                return getpass.getpass(f"Password for {u}: ")

            prompt_password = _default_prompt_password

        provider = InteractiveProvider(
            store=loader,
            scope=scope,
            issue=issue,
            prompt_username=prompt_username,
            prompt_password=prompt_password,
            persist=persist_token,
        )
        auth = RefreshingTokenAuth(provider, scheme=scheme, refresh_on_401=refresh_on_401)
        return ExampleClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            page_size=page_size,
        )

    raise RuntimeError(
        "No token in non-interactive mode. Provide token, token_file, or enable interactive=True."
    )
