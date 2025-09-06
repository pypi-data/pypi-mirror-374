# UIO API Wrapper

A generic, modular API wrapper framework for UIO services with pluggable authentication, retry strategies, and pagination profiles.

## Features

- **🔧 Modular Design**: Add new API modules with minimal code
- **🔐 Flexible Authentication**: Static tokens, token files, or interactive login
- **⚡ Smart Retries**: Configurable retry strategies with exponential backoff
- **📄 Pagination Support**: Built-in support for DRF-style and custom pagination
- **🛡️ Secure Token Storage**: TOML files or OS keyring integration
- **🎯 Module Isolation**: Each API module has independent configuration
- **🧪 Test-Friendly**: Immutable settings with easy injection for testing

## Quick Start

```python
from uio_api import mreg_client
from uio_api.modules.mreg.endpoints import Endpoint

# Simple usage - loads configuration automatically
with mreg_client() as m:
    hosts = m.get_all(Endpoint.Hosts)
    print(f"Found {len(hosts)} hosts")
```

### Token helpers (per-client)

Store credentials/tokens via the client instances (URLs resolved automatically):

```python
from uio_api import mreg_client, nivlheim_client

# MREG: add system user (uses MREG_URL from config)
with mreg_client() as client:
    client.add_system_user(username="svc", password="secret")

# MREG: add token with knobs (uses MREG_URL from config)
with mreg_client() as client:
    client.add_token(
        username="bob",
        token="abc123",
        scheme="Token",
        timeout=60.0,
        retry_attempts=5,
        page_size=1000,
    )

# Nivlheim: add API key (uses https://nivlheim.uio.no default)
with nivlheim_client() as client:
    client.add_token(
        username="svc",
        token="apikey123",
        scheme="APIKEY",
    )

# Or use explicit URLs
with mreg_client() as client:
    client.add_token(
        username="bob",
        token="abc123",
        url="https://custom.mreg.uio.no"
    )
```

## Configuration Overview

| Parameter | Type | Default | Scope | Description |
|-----------|------|---------|-------|-------------|
| `url` | `str` | None | Client | API base URL |
| `timeout` | `float` | 30.0 | Client | Request timeout in seconds |
| `headers` | `dict` | None | Client | Additional HTTP headers |
| `token` | `str` | None | Client | Static authentication token |
| `token_file` | `str/Path` | None | Client | Path to token file |
| `username` | `str` | None | Client | Username for authentication |
| `scheme` | `str` | "Token" | Client | Auth scheme (Token/Bearer/Basic) |
| `system_user` | `str` | None | Client | System account authentication |
| `interactive` | `bool` | False | Client | Enable interactive login |
| `persist_token` | `bool` | True | Client | Save tokens to storage |
| `page_size` | `int` | None | Client | Pagination page size |
| `persist` | `bool` | True | Client | Logout tokens on exit |
| `refresh_on_401` | `bool` | True | Client | Auto-refresh tokens on 401 |
| `retry_strategy` | `Callable` | Default | Client | Custom retry strategy |
| `retry_attempts` | `int` | 3 | Client | Max retry attempts |
| `allow_non_idempotent_retries` | `bool` | False | Client | Retry POST/PUT requests |
| `issue_token` | `Callable` | None | Client | Custom token issuer function |
| `prompt_username` | `Callable` | None | Client | Custom username prompt |
| `prompt_password` | `Callable` | None | Client | Custom password prompt |
| `logout_func` | `Callable` | None | Client | Custom logout function |
| `secrets_backend` | `str` | "toml" | Client | Token storage backend |
 `logging_file_path` | `str/Path` | Platform-specific | Global | Custom log file path |

> 📖 **Advanced Usage**: For detailed architecture and internal implementation, see [INTERNAL.md](INTERNAL.md).

## Logging

The library uses Loguru for logging and is **silent by default** to avoid interfering with your application's logging. To enable logging:

```python
from uio_api import logger

# Enable logging (logs will appear in your application's configured sinks)
logger.enable("uio_api")

# Optional: Configure custom logging
from uio_api import setup_logging
setup_logging(
    enable_console=True,
    enable_file=False,
    console_level="INFO"
)
```

**Key Points:**
- Library is silent by default (OPT-IN logging)
- Uses Loguru, which integrates seamlessly with Python's standard logging
- Logs include endpoint information when enabled
- Configuration available via environment variables or `setup_logging()`

### Configuration Knobs

The `ApiClient` class supports extensive configuration through multiple mechanisms:

#### Core Parameters

```python
# All parameters can be set via:
# 1. Environment variables (UIO_API_*)
# 2. Config file (~/.config/uio_api/config.toml)
# 3. Per-client overrides in factory functions

with mreg_client(
    # Connection settings
    url="https://custom.mreg.uio.no",        # Override API URL
    timeout=60.0,                           # Request timeout in seconds
    headers={"X-Custom": "value"},          # Additional headers

    # Authentication - ALL methods available per-client
    token="your-token-here",                # Static token
    token_file="~/custom/token.txt",        # Token from file
    username="custom-user",                 # Override username
    scheme="Bearer",                        # Auth scheme (Token/Bearer/Basic)
    system_user="system-account",           # System account authentication
    interactive=True,                      # Force interactive login
    persist_token=True,                    # Persist tokens to storage

    # Behavior
    page_size=500,                          # Pagination page size
    persist=True,                           # Whether to logout on exit
    refresh_on_401=True,                    # Auto-refresh tokens on 401

    # Retry configuration - ALL available per-client
    retry_attempts=5,                       # Max retry attempts
    allow_non_idempotent_retries=False,     # Retry POST/PUT requests
    retry_strategy=custom_retry_strategy,   # Custom retry strategy

    # Secrets backend - Available per-client
    secrets_backend="keyring",              # "toml" or "keyring"

    # Advanced customization
    issue_token=custom_token_issuer,        # Custom token issuance function
    prompt_username=custom_username_prompt, # Custom username prompt
    prompt_password=custom_password_prompt, # Custom password prompt
    logout_func=custom_logout_function      # Custom logout function
) as m:
    hosts = m.get_all(Endpoint.Hosts)
```

#### Timeout Configuration

```bash
export UIO_API_TIMEOUT=45.0
```

```toml
[default]
timeout = 30.0

[user."bob-drift"]
timeout = 60.0
```

#### Retry Configuration

```python
# Custom retry strategy
def custom_retry(attempt: int, method: str, url: str, status: int | None, exc: Exception | None):
    """Custom retry logic."""
    if status == 429:  # Rate limited
        delay = min(2 ** attempt, 60)  # Exponential backoff, max 60s
        return RetryDecision.RETRY, delay
    if status and 500 <= status <= 504:  # Server errors
        return RetryDecision.RETRY, 1.0 * attempt
    return RetryDecision.STOP, None

with mreg_client(retry_strategy=custom_retry) as m:
    hosts = m.get_all("/api/v1/hosts/")
```

**Note:** When `allow_non_idempotent_retries=True`, the strategy will retry POST/PUT requests under your logic. Use with care as these operations may not be safe to repeat.

```toml
[default]
retry_attempts = 3
allow_non_idempotent_retries = false
```

#### Pagination Configuration

```python
# Override page size for large datasets
with mreg_client(page_size=1000) as m:
    hosts = m.get_all(Endpoint.Hosts)  # Fetches 1000 records per page
```

```toml
[module.mreg]
page_size = 1000

[module.mreg.user."bob-drift"]
page_size = 500  # User-specific override
```

#### Headers Configuration

```python
# Custom headers after opening the client
with mreg_client() as m:
    m.update_headers({
        "X-API-Version": "v2",
        "X-Custom-Header": "value"
    })
    data = m.get(Endpoint.Hosts)
```

#### Authentication Configuration

```python
# Static token (highest priority)
with mreg_client(token="your-static-token") as m:
    data = m.get(Endpoint.Hosts)

# Token from file
with mreg_client(token_file="~/tokens/mreg.token") as m:
    data = m.get(Endpoint.Hosts)

# Force interactive login (ignore cached tokens)
with mreg_client(interactive=True) as m:
    data = m.get(Endpoint.Hosts)
```

Note: Tokens and credentials are scoped per `(module, username|default, normalized_url)`
in both TOML and Keyring backends in this POC.

#### Custom Authentication Providers

The framework supports custom authentication providers for advanced auth scenarios:

```python
from uio_api.core.auth.provider import SyncTokenProvider
from uio_api.core.auth.httpx_auth import RefreshingTokenAuth
from uio_api.core.tokens.scope import TokenScope
import httpx

# Custom provider for OAuth2 with automatic refresh
class OAuth2Provider(SyncTokenProvider):
    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self._token = None

    def get_token(self, scope: TokenScope) -> str | None:
        if self._token and self._is_token_valid():
            return self._token

        # Refresh token
        response = httpx.post(self.token_url, data={
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        response.raise_for_status()
        self._token = response.json()['access_token']
        return self._token

    def _is_token_valid(self) -> bool:
        # Implement token validation logic
        return True  # Simplified

# Use custom OAuth2 provider
oauth_provider = OAuth2Provider(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://api.example.com/oauth/token"
)

auth = RefreshingTokenAuth(
    oauth_provider,
    scheme="Bearer",
    refresh_on_401=True
)

with mreg_client() as m:
    m._client.auth = auth  # Override the default auth
    data = m.get(Endpoint.Hosts)
```

#### Custom Token Storage Provider

```python
from uio_api.core.auth.provider import SyncTokenProvider
from uio_api.core.tokens.scope import TokenScope
import redis

# Redis-based token provider
class RedisTokenProvider(SyncTokenProvider):
    def __init__(self, redis_client: redis.Redis, prefix: str = "uio_api:token"):
        self.redis = redis_client
        self.prefix = prefix

    def get_token(self, scope: TokenScope) -> str | None:
        key = f"{self.prefix}:{scope.identity()}"
        return self.redis.get(key)

    def store_token(self, scope: TokenScope, token: str) -> None:
        key = f"{self.prefix}:{scope.identity()}"
        self.redis.setex(key, 3600, token)  # 1 hour expiry

# Database-backed token provider
class DatabaseTokenProvider(SyncTokenProvider):
    def __init__(self, db_connection):
        self.db = db_connection

    def get_token(self, scope: TokenScope) -> str | None:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT token FROM tokens WHERE module = ? AND username = ? AND url_key = ?",
            (scope.module, scope.username, scope.url_key())
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def store_token(self, scope: TokenScope, token: str) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO tokens (module, username, url_key, token, updated) VALUES (?, ?, ?, ?, datetime('now'))",
            (scope.module, scope.username, scope.url_key(), token)
        )
        self.db.commit()
```

#### Advanced Authentication Scenarios

```python
# Multi-tenant authentication with tenant switching
class MultiTenantProvider(SyncTokenProvider):
    def __init__(self, tenant_tokens: dict[str, str]):
        self.tenant_tokens = tenant_tokens
        self.current_tenant = None

    def set_tenant(self, tenant_id: str):
        self.current_tenant = tenant_id

    def get_token(self, scope: TokenScope) -> str | None:
        if not self.current_tenant:
            return None
        return self.tenant_tokens.get(self.current_tenant)

# Usage
multi_tenant_auth = MultiTenantProvider({
    "tenant1": "token1",
    "tenant2": "token2"
})

auth = RefreshingTokenAuth(multi_tenant_auth, scheme="Bearer")

with mreg_client() as m:
    m._client.auth = auth

    # Switch to tenant 1
    multi_tenant_auth.set_tenant("tenant1")
    tenant1_data = m.get(Endpoint.Hosts)

    # Switch to tenant 2
    multi_tenant_auth.set_tenant("tenant2")
    tenant2_data = m.get(Endpoint.Hosts)
```

#### Custom httpx.Auth Integration

```python
import httpx
from typing import Any

# Custom httpx.Auth for API key authentication
class APIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def auth_flow(self, request: httpx.Request) -> None:
        request.headers[self.header_name] = self.api_key

# Custom auth for AWS Signature Version 4
class AWSSigV4Auth(httpx.Auth):
    def __init__(self, access_key: str, secret_key: str, region: str, service: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service

    def auth_flow(self, request: httpx.Request) -> None:
        # Implement AWS SigV4 signing logic here
        # This is a simplified example
        import hashlib
        import hmac
        import datetime

        now = datetime.datetime.utcnow()
        date_stamp = now.strftime('%Y%m%d')
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')

        # Add required headers
        request.headers['X-Amz-Date'] = amz_date
        request.headers['Authorization'] = f"AWS4-HMAC-SHA256 Credential={self.access_key}/{date_stamp}/{self.region}/{self.service}/aws4_request"

# Usage with custom auth
api_key_auth = APIKeyAuth("your-api-key-here")

with mreg_client() as m:
    m._client.auth = api_key_auth
    data = m.get(Endpoint.Hosts)

# AWS auth example (requires full SigV4 implementation)
aws_auth = AWSSigV4Auth(
    access_key="your-access-key",
    secret_key="your-secret-key",
    region="us-east-1",
    service="mreg"
)

with mreg_client() as m:
    m._client.auth = aws_auth
    data = m.get(Endpoint.Hosts)
```

#### Custom Refresh Logic

```python
# Provider with custom refresh logic
class CustomRefreshProvider(SyncTokenProvider):
    def __init__(self, initial_token: str, refresh_url: str):
        self.token = initial_token
        self.refresh_url = refresh_url
        self.last_refresh = None

    def _should_refresh(self) -> bool:
        if not self.last_refresh:
            return True
        import datetime
        return (datetime.datetime.now() - self.last_refresh).total_seconds() > 300

    def get_token(self, scope: TokenScope) -> str | None:
        # Refresh token if it's been more than 5 minutes
        if self._should_refresh():
            self._refresh_token()
        return self.token

    def _refresh_token(self) -> None:
        response = httpx.post(self.refresh_url, json={
            "token": self.token
        })
        response.raise_for_status()
        self.token = response.json()["new_token"]
        self.last_refresh = datetime.now()

# Use with refresh auth
refresh_provider = CustomRefreshProvider(
    initial_token="initial-token",
    refresh_url="https://api.example.com/auth/refresh"
)

auth = RefreshingTokenAuth(
    refresh_provider,
    scheme="Bearer",
    refresh_on_401=True
)

with mreg_client() as m:
    m._client.auth = auth
    data = m.get(Endpoint.Hosts)
```

#### System Account Authentication

```python
# Use a pre-configured system account
with mreg_client(system_user="my-system-account") as m:
    hosts = m.get_all(Endpoint.Hosts)
```

```toml
[module.mreg]
system_user = "my-system-account"
```

#### Token Persistence Control

```python
# Don't persist tokens to storage (session-only)
with mreg_client(persist_token=False) as m:
    hosts = m.get_all(Endpoint.Hosts)
    # Tokens won't be saved to disk/keyring

# Note: persist_token controls token storage, while persist controls
# whether to logout tokens on client close. Set persist=False to
# keep tokens valid after the client session ends.
```

#### SSL/TLS Configuration

SSL configuration can be controlled by overriding the internal httpx.Client:

```python
# Disable SSL verification (not recommended for production)
with mreg_client() as m:
    m._client.verify = False  # Advanced: direct httpx.Client access
    data = m.get(Endpoint.Hosts)

# Use custom SSL certificates
import ssl
ssl_context = ssl.create_default_context()
ssl_context.load_cert_chain(certfile="client.crt", keyfile="client.key")

with mreg_client() as m:
    m._client.verify = ssl_context  # Advanced: direct httpx.Client access
    data = m.get(Endpoint.Hosts)
```

#### Redirect Handling

Redirect behavior can be controlled by overriding the internal httpx.Client:

```python
# Control redirect following behavior
with mreg_client() as m:
    # Follow redirects (default httpx behavior)
    data = m.get(Endpoint.Hosts)

    # Don't follow redirects (advanced usage)
    import httpx
    m._client.follow_redirects = False
    response = m.request("GET", Endpoint.Hosts)
```

#### Custom Token Issuance

```python
def custom_token_issuer(username: str, password: str, url: str) -> str:
    """Custom token issuance logic."""
    # Implement your custom authentication flow
    response = httpx.post(f"{url}/oauth/token", data={
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": "my-client"
    })
    response.raise_for_status()
    return response.json()["access_token"]

with mreg_client(issue_token=custom_token_issuer) as m:
    data = m.get("/api/v1/resource/")
```

#### Custom Prompt Functions

```python
def custom_username_prompt() -> str:
    """Custom username input prompt."""
    return input("Enter your API username: ")

def custom_password_prompt(username: str) -> str:
    """Custom password input prompt."""
    import getpass
    return getpass.getpass(f"Password for {username}: ")

with mreg_client(
    prompt_username=custom_username_prompt,
    prompt_password=custom_password_prompt
) as m:
    data = m.get("/api/v1/resource/")
```

#### Custom Logout Function

```python
def custom_logout(token: str, url: str) -> None:
    """Custom token revocation logic."""
    try:
        httpx.post(f"{url}/oauth/revoke", json={"token": token})
    except Exception:
        # Ignore logout errors
        pass

with mreg_client(logout_func=custom_logout) as m:
    data = m.get("/api/v1/resource/")
    # Custom logout will be called when exiting context
```

#### Secrets Backend Configuration

```bash
# Use OS keyring for secure token storage
export UIO_API_SECRETS_BACKEND=keyring

# Use TOML files (default)
export UIO_API_SECRETS_BACKEND=toml
```

```toml
[default]
secrets_backend = "keyring"  # or "toml"
```

#### Connection Management

```python
# Auto-cleanup (recommended)
with mreg_client() as m:
    data = m.get("/api/v1/resource/")
    # Connection closed, token logged out automatically

# Manual management
m = mreg_client()
try:
    m.open()
    data = m.get("/api/v1/resource/")
finally:
    m.close()  # Explicit cleanup

# Disable logout on exit
with mreg_client(persist=False) as m:
    data = m.get("/api/v1/resource/")
    # Connection closed but token remains valid
```

#### Module-Specific Overrides

```python
# Override settings for specific modules
from uio_api.modules.mreg import client as mreg_client
from uio_api.modules.example import client as example_client

# Different timeouts for different services
with mreg_client(timeout=30.0) as m, example_client(timeout=60.0) as e:
    mreg_data = m.get("/api/v1/hosts/")
    example_data = e.get("/v1/resources/")
```

## Configuration

The framework uses a hierarchical configuration system with clear precedence:

1. **Per-client overrides** (highest priority)
2. **Module-scoped environment variables** (e.g., `MREG_URL`, `MREG_TOKEN`)
3. **Generic environment variables** (e.g., `UIO_API_TIMEOUT`)
4. **Module-scoped config file sections** (e.g., `[module.mreg]`)
5. **Generic config file sections** (e.g., `[default]`, `[user."bob"]`)
6. **Built-in defaults** (lowest priority)

### Environment Variables

```bash
# Generic settings (apply to all modules)
export UIO_API_TIMEOUT=45
export UIO_API_SECRETS_BACKEND=keyring
export UIO_API_USERNAME=bob-drift
export UIO_API_LOGGING_FILE_PATH=/path/to/custom/logfile.log

# Module-specific settings (override generic)
export MREG_URL=https://mreg.uio.no
export MREG_TOKEN=your-mreg-token
export MREG_PAGE_SIZE=1000

export EXAMPLE_URL=https://api.example.com
export EXAMPLE_SCHEME=Bearer
```

### Configuration File

Create `~/.config/uio_api/config.toml`:

```toml
[default]
timeout = 30.0
retry_attempts = 3
secrets_backend = "toml"
interactive = true
logging_file_path = "/path/to/custom/logfile.log"

[user."bob-drift"]
page_size = 500
timeout = 60.0

# Module-specific defaults
[module.mreg]
url = "https://mreg.uio.no"
scheme = "Token"
page_size = 1000
login_path = "/api/token-auth/"
logout_path = "/api/token-logout/"

[module.mreg.user."bob-drift"]
page_size = 1000

[module.example]
url = "https://api.example.com"
scheme = "Bearer"
page_size = 50
login_path = "/oauth/token"
```

## Usage Patterns

### Context Manager vs Manual Management

**Context Manager (Recommended):**
```python
# Automatic connection management and cleanup
with mreg_client() as m:
    hosts = m.get_all("/api/v1/hosts/")
    # Connection automatically closed and token logged out
```

**Manual Management:**
```python
# Full control over lifecycle
m = mreg_client()
try:
    m.open()
    hosts = m.get_all("/api/v1/hosts/")
finally:
    m.close()
```

### Authentication Methods

**Interactive Login (Default):**
```python
# Prompts for username/password, stores token securely
with mreg_client() as m:
    hosts = m.get_all("/api/v1/hosts/")
```

**Static Token:**
```python
# Use a pre-obtained token
with mreg_client(token="your-token-here") as m:
    hosts = m.get_all("/api/v1/hosts/")
```

**Token File:**
```python
# Read token from file
with mreg_client(token_file="~/.mreg/token.txt") as m:
    hosts = m.get_all("/api/v1/hosts/")
```

**Custom Authentication:**
```python
from uio_api.core.auth.provider import StaticProvider
from uio_api.core.auth.httpx_auth import RefreshingTokenAuth

# Custom auth provider
auth = RefreshingTokenAuth(
    StaticProvider(token="custom-token"),
    scheme="Bearer",
    refresh_on_401=False
)

with mreg_client() as m:
    m._client.auth = auth  # Override auth
    hosts = m.get_all("/api/v1/hosts/")
```

### Custom Retry Strategy

```python
from uio_api.core.retry.policy import RetryStrategy, RetryDecision
from uio_api.core.enums import RetryDecision

def custom_retry(attempt: int, method: str, url: str, status: int | None, exc: Exception | None):
    """Custom retry logic - retry on 429, 500-504, but not on 4xx."""
    if status == 429:  # Rate limited
        return RetryDecision.RETRY, min(2 ** attempt, 60)  # Max 60s delay
    if status and 500 <= status <= 504:  # Server errors
        return RetryDecision.RETRY, 1.0 * attempt
    return RetryDecision.STOP, None

with mreg_client(retry_strategy=custom_retry) as m:
    hosts = m.get_all("/api/v1/hosts/")
```

### Per-Client Overrides

```python
# Override any setting for this specific client
with mreg_client(
    url="https://test.mreg.uio.no",
    timeout=60.0,
    page_size=500,
    persist=False  # Don't logout on exit
) as m:
    hosts = m.get_all("/api/v1/hosts/")
```

### Multi-Module Usage

```python
from uio_api.modules.mreg import client as mreg_client
from uio_api.modules.example import client as example_client

# Each module loads its own configuration independently
with mreg_client() as m1, example_client() as e1:
    mreg_hosts = m1.get_all("/api/v1/hosts/")
    example_data = e1.get_all("/v1/resources/")
```

## Creating Your Own API Module

Adding a new API module is straightforward:

### 1. Create Module Structure

```
uio_api/modules/your_api/
├── __init__.py
├── profile.py
├── endpoints.py  # Optional
└── factory.py
```

### 2. Define API Profile

```python
# uio_api/modules/your_api/profile.py
from ...profiles.base import ApiProfile, DrfPagination

YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Bearer",  # or "Token", "Basic", etc.
    login_path="/oauth/token",
    logout_path="/oauth/revoke",
    require_trailing_slash=False,  # API-specific
    pagination=DrfPagination(),  # or NoPagination()
    max_page_size=100,  # API-specific limit
)
```

### 3. Create Factory Function

```python
# uio_api/modules/your_api/factory.py
from ...config import load_settings
from ...config.module import ModuleSettings
from ...core.client import ApiClient
from ...core.auth.httpx_auth import RefreshingTokenAuth
from ...core.auth.provider import StaticProvider, FileProvider, InteractiveProvider
from .profile import YourApiProfile

def client(
    *,
    settings: ModuleSettings | None = None,
    # Per-client overrides
    url: str | None = None,
    token: str | None = None,
    # ... other parameters
) -> ApiClient:
    """Build a ready-to-use ApiClient for Your API."""
    
    # Load settings if not provided
    if settings is None:
        settings = load_settings("your_api")
    
    # Apply overrides
    if url is not None:
        settings = settings.with_overrides(url=url)
    if token is not None:
        settings = settings.with_overrides(token=token)
    
    # Create User-Agent header
    from ... import APP, __version__
    headers = {"User-Agent": f"{APP}/{__version__} (your_api)"}
    
    # Build authentication
    if settings.TOKEN:
        auth = RefreshingTokenAuth(
            StaticProvider(token=settings.TOKEN),
            scheme=settings.SCHEME,
            refresh_on_401=False
        )
    # ... handle other auth methods
    
    return ApiClient(
        base_url=settings.URL,
        auth=auth,
        headers=headers,
        timeout=settings.TIMEOUT,
        # ... other settings
    )
```

### 4. Export Client

```python
# uio_api/modules/your_api/__init__.py
from .factory import client as your_api_client

__all__ = ["your_api_client"]
```

### 5. Add to Top-Level Package

```python
# uio_api/__init__.py
from .modules.your_api import your_api_client

__all__ = ["APP", "client", "example_client", "your_api_client"]
```

### 6. Configure Module Defaults

Add to `~/.config/uio_api/config.toml`:

```toml
[module.your_api]
url = "https://api.yourservice.com"
scheme = "Bearer"
page_size = 100
login_path = "/oauth/token"
logout_path = "/oauth/revoke"
```

### 7. Use Your Module

```python
from uio_api import your_api_client

with your_api_client() as api:
    data = api.get_all("/v1/resources/")
```

## Token Storage

### TOML Storage (Default)

Tokens are stored in `~/.config/uio_api/secrets.toml`:

```toml
[module.mreg.user."bob-drift".urls."https://mreg.uio.no"]
token = "mreg-token-abc123..."
updated = "2025-01-02T10:10:00Z"

[module.example.user."bob-drift".urls."https://api.example.com"]
token = "example-token-def456..."
updated = "2025-01-02T10:15:00Z"
```

### Keyring Storage

Set `UIO_API_SECRETS_BACKEND=keyring` to use OS keyring:

```bash
export UIO_API_SECRETS_BACKEND=keyring
```

Tokens are stored with service names like:
- `uio_api:mreg:bob-drift:https://mreg.uio.no`
- `uio_api:example:bob-drift:https://api.example.com`

## Testing

The framework is designed for easy testing with immutable settings:

```python
from uio_api.config import load_settings
from uio_api.modules.mreg import client as mreg_client

def test_client():
    # Create test settings without env mutation
    settings = load_settings("mreg").with_overrides(
        url="https://mock.mreg.test",
        token="test-token"
    )
    
    with mreg_client(settings=settings) as m:
        # Uses mock URL and test token
        assert m.base_url == "https://mock.mreg.test"
```

## Installation

```bash
pip install uio-api
```

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
hatch run dev:test

# Format code
hatch run dev:format

# Lint code
hatch run dev:lint
```

## Documentation

- **[INTERNAL.md](INTERNAL.md)**: Detailed internal architecture and implementation
- **[modules/README.md](modules/README.md)**: Creating new API modules guide

## License

MIT License - see LICENSE file for details.
