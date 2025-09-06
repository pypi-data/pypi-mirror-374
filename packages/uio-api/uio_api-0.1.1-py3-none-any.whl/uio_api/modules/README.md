# Creating API Modules

This guide explains how to create new API modules for the UIO API Wrapper framework. Each module provides a type-safe, configured client for a specific API service.

## Module Structure

A typical API module has this structure:

```
uio_api/modules/your_api/
├── __init__.py          # Export the client
├── profile.py           # API behavior profile
├── endpoints.py         # Type-safe endpoint definitions (optional)
└── factory.py           # Client factory function
```

## Step-by-Step Guide

### 1. Create Module Directory

```bash
mkdir uio_api/modules/your_api
```

### 2. Define API Profile

Create `uio_api/modules/your_api/profile.py`:

```python
"""API profile for Your API service."""

from ...profiles.base import ApiProfile, DrfPagination, NoPagination

YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Bearer",  # or "Token", "Basic", etc.
    login_path="/oauth/token",
    logout_path="/oauth/revoke",
    require_trailing_slash=False,  # API-specific behavior
    pagination=DrfPagination(),  # or NoPagination() for non-paginated APIs
    max_page_size=100,  # API-specific limit
)
```

**Profile Options:**
- `scheme`: Authentication scheme ("Bearer", "Token", "Basic", etc.)
- `login_path`: Path for token authentication
- `logout_path`: Path for token logout/revocation (None if not supported)
- `require_trailing_slash`: Whether API requires trailing slashes (True for DRF APIs)
- `pagination`: Pagination strategy (`DrfPagination()` or `NoPagination()`)
- `max_page_size`: Maximum page size for paginated requests

### 3. Define Endpoints (Optional but Recommended)

Create `uio_api/modules/your_api/endpoints.py`:

```python
"""Type-safe endpoint definitions for Your API."""

from __future__ import annotations

from enum import Enum, unique
from typing import Literal
from urllib.parse import quote, urljoin


@unique
class ApiPath(Enum):
    """Core API authentication endpoints."""
    LOGIN = "/oauth/token"
    LOGOUT = "/oauth/revoke"


class Endpoint(str, Enum):
    """API endpoints for Your API service.
    
    Provides type-safe access to all API endpoints with support for
    parameterized URLs and ID-based endpoints.
    """
    
    # Core Resources
    Users = "/api/v1/users/"
    Resources = "/api/v1/resources/"
    Projects = "/api/v1/projects/"
    
    # Parameterized endpoints
    UserProjects = "/api/v1/users/{}/projects/"
    ProjectResources = "/api/v1/projects/{}/resources/"
    
    # ID-based endpoints
    UserById = "/api/v1/users/{}/"
    ResourceById = "/api/v1/resources/{}/"
    
    def __str__(self):
        """Prevent direct usage without parameters where needed."""
        if "{}" in self.value:
            raise ValueError(f"Endpoint {self.name} requires parameters. Use `with_params`.")
        return self.value
    
    def with_id(self, identity: str | int) -> str:
        """Return the endpoint with an ID appended."""
        id_field = quote(str(identity))
        return urljoin(self.value, id_field)
    
    def with_params(self, *params: str | int) -> str:
        """Construct endpoint URL by inserting parameters."""
        placeholders_count = self.value.count("{}")
        if placeholders_count != len(params):
            raise ValueError(
                f"{self.name} endpoint expects {placeholders_count} parameters, got {len(params)}."
            )
        encoded_params = (quote(str(param)) for param in params)
        return self.value.format(*encoded_params)
```

### 4. Create Factory Function

Create `uio_api/modules/your_api/factory.py`:

```python
"""Factory function for creating Your API clients."""

from __future__ import annotations

import httpx
from pathlib import Path
from typing import Callable, Optional

from ...core.client import ApiClient
from ...core.auth.httpx_auth import RefreshingTokenAuth
from ...core.auth.provider import (
    StaticProvider, FileProvider, InteractiveProvider, IssueToken
)
from ...core.retry.policy import RetryStrategy, default_retry_strategy
from ...core.tokens.loader_abstract import AbstractTokenLoader
from ...core.tokens.loader_toml import TomlTokenLoader
from ...core.tokens.loader_keyring import KeyringTokenLoader
from ...core.tokens.scope import TokenScope, normalize_service_url
from ...config import load_settings
from ...config.module import ModuleSettings
from .profile import YourApiProfile


def _issuer(timeout: float) -> IssueToken:
    """Create a token issuer for Your API."""
    def issue(username: str, password: Optional[str], url: str) -> str:
        base = normalize_service_url(url)
        with httpx.Client(base_url=base, timeout=timeout, headers={"Content-Type": "application/json"}) as c:
            r = c.post(YourApiProfile.login_path, json={
                "username": username, 
                "password": password
            })
            r.raise_for_status()
            token = (r.json() or {}).get("access_token")  # Adjust field name as needed
            if not token:
                raise RuntimeError("Auth response missing 'access_token'.")
            return token
    return issue


def _logout(timeout: float) -> Callable[[str, str], None]:
    """Create a logout function for Your API."""
    def run(token: str, url: str) -> None:
        if not YourApiProfile.logout_path:
            return
        base = normalize_service_url(url)
        with httpx.Client(base_url=base, timeout=timeout, headers={
            "Content-Type": "application/json",
            "Authorization": f"{YourApiProfile.scheme} {token}"
        }) as c:
            r = c.post(YourApiProfile.logout_path)
            r.raise_for_status()
    return run


def _choose_loader(url: str, username: str | None, settings: ModuleSettings) -> tuple[AbstractTokenLoader, TokenScope]:
    """Choose the appropriate token loader based on configuration."""
    if settings.SECRETS_BACKEND.name.lower() == "keyring":
        loader: AbstractTokenLoader = KeyringTokenLoader(index_path=settings.KEYRING_INDEX_FILE)
    else:
        loader = TomlTokenLoader(path=settings.SECRETS_FILE)
    
    scope = TokenScope(module=settings.module_name, url=url, username=username)
    return loader, scope


def client(
    *,
    settings: ModuleSettings | None = None,
    # Per-client overrides
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
    retry_strategy: RetryStrategy | None = None,
    issue_token: IssueToken | None = None,
    prompt_username: Callable[[], str] | None = None,
    prompt_password: Callable[[str], str] | None = None,
    persist: bool = True,
) -> ApiClient:
    """Build a ready-to-use ApiClient configured for Your API.

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
        retry_strategy: Custom retry strategy.
        issue_token: Custom token issuer function.
        prompt_username: Custom username prompt function.
        prompt_password: Custom password prompt function.
        persist: Whether to persist token on logout.

    Returns:
        A configured ApiClient instance ready for use with Your API.

    Example:
        # Default use (loads from registry)
        with client() as api:
            users = api.get_all(Endpoint.Users)

        # With overrides
        with client(url="https://api.yourservice.com") as api:
            users = api.get_all(Endpoint.Users)
    """
    # Load settings if not provided
    if settings is None:
        settings = load_settings("your_api")
    
    # Apply per-client overrides
    overrides = {}
    if url is not None:
        overrides["url"] = url
    if username is not None:
        overrides["username"] = username
    if token is not None:
        overrides["token"] = token
    if token_file is not None:
        overrides["token_file"] = Path(token_file) if isinstance(token_file, str) else token_file
    if system_user is not None:
        overrides["system_user"] = system_user
    if interactive is not None:
        overrides["interactive"] = interactive
    if persist_token is not None:
        overrides["persist_token"] = persist_token
    if scheme is not None:
        overrides["scheme"] = scheme
    if timeout is not None:
        overrides["timeout"] = timeout
    if refresh_on_401 is not None:
        overrides["refresh_on_401"] = refresh_on_401
    if page_size is not None:
        overrides["page_size"] = page_size
    
    if overrides:
        settings = settings.with_overrides(**overrides)

    # Create headers (User-Agent + extra)
    from ... import APP, __version__
    from ...core.factory_utils import create_client_headers
    base_headers = create_client_headers(APP, "your_api", __version__)
    if headers:
        base_headers.update(headers)

    # Resolve configuration
    base_url = normalize_service_url(settings.URL or "")
    if not base_url:
        raise ValueError("Missing URL. Provide url= or configure YOUR_API_URL.")

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

    # Build authentication
    logout_func = _logout(timeout)

    # Path 1: Static token
    if token:
        auth = RefreshingTokenAuth(
            StaticProvider(token=token),
            scheme=scheme,
            refresh_on_401=False
        )
        return ApiClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size
        )

    # Path 2: Token file
    if token_file:
        auth = RefreshingTokenAuth(
            FileProvider(path=str(token_file)),
            scheme=scheme,
            refresh_on_401=refresh_on_401
        )
        return ApiClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size
        )

    # Path 3: System account
    if system_user:
        from ...core.auth.provider import SystemAccountProvider
        loader, scope = _choose_loader(url=base_url, username=system_user, settings=settings)
        provider = SystemAccountProvider(
            username_file="",  # Not used - we have username directly
            store=loader,
            scope=scope,
            issue=_issuer(timeout)
        )
        # Override the username loading since we have it directly
        provider._username = system_user
        auth = RefreshingTokenAuth(
            provider,
            scheme=scheme,
            refresh_on_401=refresh_on_401
        )
        return ApiClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size
        )

    # Path 4: Interactive
    if interactive:
        loader, scope = _choose_loader(url=base_url, username=username, settings=settings)
        
        # Default issuer if not provided
        issue = issue_token or _issuer(timeout)
        
        # Default prompts if not provided
        if prompt_username is None:
            # Use OS username when scope has no username yet
            prompt_username = (lambda: scope.username or __import__("getpass").getuser())
        if prompt_password is None:
            import getpass
            prompt_password = (lambda u: getpass.getpass(f"Password for {u}: "))
        
        provider = InteractiveProvider(
            store=loader,
            scope=scope,
            issue=issue,
            prompt_username=prompt_username,
            prompt_password=prompt_password,
            persist=persist_token
        )
        auth = RefreshingTokenAuth(provider, scheme=scheme, refresh_on_401=refresh_on_401)
        return ApiClient(
            base_url=base_url,
            auth=auth,
            timeout=timeout,
            retry=retry_strategy,
            headers=base_headers,
            persist=persist,
            logout_func=logout_func,
            page_size=page_size
        )

    raise RuntimeError(
        "No authentication method available. Provide one of: token, token_file, system_user, or enable interactive=True."
    )
```

### 5. Export Client

Create `uio_api/modules/your_api/__init__.py`:

```python
"""Your API client module."""

from .factory import client as your_api_client

__all__ = ["your_api_client"]
```

### 6. Add to Top-Level Package

Update `uio_api/__init__.py`:

```python
# Import existing constants and add your module export
from .constants import APP, APPNAME
from .modules.mreg import mreg_client
from .modules.example import example_client
from .modules.your_api import your_api_client

__all__ = ["APP", "APPNAME", "mreg_client", "example_client", "your_api_client"]

```

### 7. Configure Module Defaults

Add to `~/.config/uio_api/config.toml`:

```toml
[module.your_api]
url = "https://api.yourservice.com"
scheme = "Bearer"
page_size = 100
login_path = "/oauth/token"
logout_path = "/oauth/revoke"
```

### 7.1 Secrets Layout (TOML)

Tokens and credentials are stored per module and user, keyed by normalized URL:

```toml
[module.your_api.default.urls."https://api.yourservice.com"]
token = "abc..."
updated = "2025-09-02T10:00:00Z"

[module.your_api.user."alice".urls."https://api.yourservice.com"]
token = "def..."
updated = "2025-09-02T10:05:00Z"
```

The Keyring backend mirrors this structure using a small local index file for
enumeration and backup/restore.

### 8. Use Your Module

```python
from uio_api import your_api_client
from uio_api.modules.your_api.endpoints import Endpoint

# Default use (loads from registry)
with your_api_client() as api:
    users = api.get_all(Endpoint.Users)
    print(f"Found {len(users)} users")

# With overrides
with your_api_client(url="https://test.api.yourservice.com") as api:
    users = api.get_all(Endpoint.Users)
```

## Best Practices

Note on token scoping: Tokens and credentials are stored per `(module, username|default, normalized_url)`
for both TOML and Keyring backends. Enumeration and backup/restore operate on these
module-aware scopes.

### 1. Use Type-Safe Endpoints

Always define endpoints as enums with proper parameter handling:

```python
class Endpoint(str, Enum):
    Users = "/api/v1/users/"
    UserById = "/api/v1/users/{}/"
    
    def with_id(self, identity: str | int) -> str:
        return urljoin(self.value, quote(str(identity)))
```

### 2. Handle Authentication Properly

- Use the profile's `scheme` for consistent auth headers
- Implement proper token refresh logic
- Handle both interactive and non-interactive modes

### 3. Follow Configuration Patterns

- Use the settings injection pattern
- Support per-client overrides
- Provide sensible defaults in the profile

### 4. Error Handling

- Validate required parameters early
- Provide clear error messages
- Handle missing configuration gracefully

### 5. Testing

```python
def test_your_api_client():
    # Create test settings without env mutation
    settings = load_settings("your_api").with_overrides(
        url="https://mock.api.test",
        token="test-token"
    )
    
    with your_api_client(settings=settings) as api:
        assert api.base_url == "https://mock.api.test"
```

## Common Patterns

### DRF-Style APIs

For Django REST Framework APIs:

```python
YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Token",  # or "Bearer"
    login_path="/api/token-auth/",
    logout_path="/api/token-logout/",
    require_trailing_slash=True,  # DRF requires trailing slashes
    pagination=DrfPagination(),
    max_page_size=1000,
)
```

### OAuth2 APIs

For OAuth2 APIs:

```python
YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Bearer",
    login_path="/oauth/token",
    logout_path="/oauth/revoke",
    require_trailing_slash=False,
    pagination=DrfPagination(),
    max_page_size=100,
)
```

### Non-Paginated APIs

For APIs without pagination:

```python
YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Bearer",
    login_path="/auth/login",
    logout_path=None,  # No logout endpoint
    require_trailing_slash=False,
    pagination=NoPagination(),
    max_page_size=None,
)
```

This guide should help you create robust, type-safe API modules that integrate seamlessly with the UIO API Wrapper framework.
