# UIO API Wrapper - Developer Documentation

This document provides technical details for developers working on the UIO API Wrapper framework. For user-facing documentation, see [README.md](README.md).

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Implementation Details](#core-implementation-details)
- [Configuration System Internals](#configuration-system-internals)
- [Authentication Flow](#authentication-flow)
- [Token Management](#token-management)
- [Module Development](#module-development)
- [Testing & Debugging](#testing--debugging)
- [Performance Considerations](#performance-considerations)

## Architecture Overview

The framework follows a layered architecture with clear separation of concerns:

### Key Design Patterns

- **Factory Pattern**: Each API module provides a factory function for client creation
- **Strategy Pattern**: Pluggable authentication, retry, and pagination strategies
- **Registry Pattern**: Configuration registry with precedence hierarchy
- **Provider Pattern**: Token providers for different storage backends
- **Composition over Inheritance**: Settings composed through dataclasses

### Component Relationships

```
ApiClientFactory → ApiClient → httpx.Client
                      ↓
                 Authentication
                 (TokenProvider → RefreshingTokenAuth)
                      ↓
                 Token Storage
                 (AbstractTokenLoader → TOML/Keyring)
                      ↓
                 Configuration
                 (ConfigRegistry → Settings hierarchy)
```

## Core Implementation Details

### ApiClient Request Flow

The `ApiClient` uses a shared internal method `_execute_request()` for both `request()` and `get_response()`:

```python
def _execute_request(self, method, path, params, json, return_raw):
    # 1. Normalize path (leading slash, no trailing slash)
    # 2. Execute with retry logic
    # 3. Return raw response if requested
    # 4. Process JSON if not raw
```

### Retry Strategy Implementation

The default retry strategy caps delays at 60 seconds and validates inputs:

```python
def default_retry_strategy(max_attempts=3, base_delay=0.25, allow_non_idempotent=False):
    # Input validation
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if base_delay <= 0:
        raise ValueError("base_delay must be > 0")

    # Delay calculation with 60s cap
    delay = min(base_delay * (2 ** (attempt - 1)), 60.0)
```

### Configuration System Internals

#### Settings Loading Flow

```python
def load_settings(module: str) -> ModuleSettings:
    # 1. Load base settings with caching
    base = _load_base_settings()
    # 2. Load module-specific overrides
    # 3. Apply environment variables
    # 4. Apply config file settings
    # 5. Return composed ModuleSettings
```

#### Precedence Hierarchy Implementation

The registry implements the precedence through a series of `dict.update()` operations:

```python
def _merge_settings(self, module: str) -> dict:
    settings = {}
    # Start with defaults
    settings.update(self._defaults)
    # Apply base config
    settings.update(self._base_config)
    # Apply module config
    settings.update(self._module_configs.get(module, {}))
    # Apply environment variables
    settings.update(self._env_vars)
    # Apply per-client overrides (highest priority)
    settings.update(self._overrides)
    return settings
```

## Authentication Flow

### Token Provider Chain

1. **Token Resolution**: Check static token → file → system account → interactive
2. **Provider Selection**: Based on available configuration
3. **Token Caching**: In-memory during client session
4. **Refresh Logic**: Automatic on 401 responses

### RefreshingTokenAuth Implementation

```python
class RefreshingTokenAuth(httpx.Auth):
    def auth_flow(self, request):
        # 1. Get token from provider
        token = self.provider.get_token()
        # 2. Add to request headers
        request.headers[self.header] = f"{self.scheme} {token}"
        # 3. Send request
        response = yield request
        # 4. Refresh on 401 if enabled
        if response.status_code == 401 and self.refresh_on_401:
            self.provider.refresh()
            # Retry with new token
```

## Token Management

### Storage Backend Selection

```python
def _choose_loader(url: str, username: str | None, settings: ModuleSettings):
    backend = settings.SECRETS_BACKEND
    name = backend.name.lower() if hasattr(backend, "name") else str(backend).lower()
    if name == "keyring":
        return KeyringTokenLoader(index_path=settings.KEYRING_INDEX_FILE)
    return TomlTokenLoader(path=settings.SECRETS_FILE)
```

### Module-Aware Keyring Index

Keyring values live in the OS keychain. To support scope enumeration and
transactional backup/restore, we maintain a compact TOML index that mirrors the
TOML loader’s semantics and is module-aware:

```toml
[module."mreg".default]
urls = ["https://mreg.uio.no"]

[module."mreg".user."alice"]
urls = ["https://mreg.uio.no"]

[module."ldap".default]
urls = ["https://ldap.example.com"]
```

- Service key: `f"{service_prefix}:{module}:{username or 'default'}"`
- Username (keyring field): normalized service URL
- Value: token string

Enumeration yields `TokenScope(module, url, username)` for each entry under
`default` and `user` per module. Backups snapshot tokens using
`scope.identity()` (`module|username_or_default|url`) and restore them best-effort.

Both TOML and Keyring loaders enumerate only module-aware scopes in this POC
(no legacy generic sections).

### Atomic TOML Writes

```python
def _save(self, doc):
    # Atomic write pattern
    temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
    temp_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
    os.chmod(temp_path, self.perms)  # Set permissions before move
    temp_path.replace(self.path)     # Atomic replace
```

## Module Development

### Factory Function Template

```python
def client(
    *,
    settings: ModuleSettings | None = None,
    # Per-client overrides
    url: str | None = None,
    token: str | None = None,
    # ... module-specific parameters
) -> ApiClient:
    # 1. Load or use provided settings
    if settings is None:
        settings = load_settings("module_name")

    # 2. Apply overrides
    if url is not None:
        settings = settings.with_overrides(url=url)
    if token is not None:
        settings = settings.with_overrides(token=token)

    # 3. Create authentication
    auth = build_auth_for_module(settings)

    # 4. Return configured client
    return ApiClient(
        base_url=settings.url,
        auth=auth,
        timeout=settings.timeout,
        # ... other config
    )
```

### Profile Definition

```python
YourApiProfile = ApiProfile(
    name="your_api",
    scheme="Bearer",
    login_path="/oauth/token",
    logout_path=None,  # No logout endpoint
    require_trailing_slash=False,
    pagination=DrfPagination(),
    max_page_size=500,
)
```

## Testing & Debugging

### Unit Test Structure

```python
# test_client.py
def test_request_success():
    with patch('httpx.Client') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_client.return_value.request.return_value = mock_response

        client = ApiClient(base_url="https://api.example.com")
        result = client.request("GET", "/test")

        assert result == {"data": "test"}

def test_retry_on_failure():
    # Test retry logic with mocked failures
    pass
```

### Integration Test Pattern

```python
def test_mreg_client_integration():
    # Use real httpx but mock the server
    with HTTPXMock() as mock:
        mock.add_response(
            url="https://mreg.uio.no/api/v1/hosts/",
            json={"results": [], "next": None}
        )

        with mreg_client() as client:
            hosts = client.get_all("/api/v1/hosts/")
            assert hosts == []
```

### Debug Logging Setup

```python
# Enable all debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable httpx debug
import httpx
httpx.logger.setLevel(logging.DEBUG)

# Enable uio_api debug
from uio_api import logger
logger.enable("uio_api")
```

## Performance Considerations

### Memory Usage Optimization

- **Immutable Settings**: Prevents accidental mutation and memory leaks
- **Lazy Loading**: Clients created only when needed
- **Connection Pooling**: httpx handles efficient connection reuse
- **Token Caching**: In-memory during session, persistent storage as needed

### Network Efficiency

- **Path Normalization**: Consistent URL construction
- **Connection Reuse**: Single httpx.Client instance per ApiClient
- **Exponential Backoff**: Prevents thundering herd on failures
- **Pagination Batching**: Efficient handling of large result sets

### Caching Strategy

```python
@lru_cache(maxsize=32)
def _load_base_settings():
    # Cached base configuration loading
    return BaseSettings(...)
```

### Profiling Hotspots

```python
# Profile request timing
import time
start = time.perf_counter()
result = client.request("GET", "/api/v1/large-dataset/")
elapsed = time.perf_counter() - start
print(f"Request took {elapsed:.3f}s")
```

## Security Implementation

### Token Redaction in Logs

```python
# Pre-compiled patterns for performance
_TOKEN_JSON_PATTERN = re.compile(r'("token"|"authorization")\s*:\s*"[^"]*"', re.IGNORECASE)
_TOKEN_URL_PATTERN = re.compile(r'[?&]token=[^&\s]+', re.IGNORECASE)
_BEARER_PATTERN = re.compile(r'Bearer\s+[^\s&]+', re.IGNORECASE)

def _redact_message(msg: str) -> str:
    msg = _TOKEN_JSON_PATTERN.sub(r'\1: "[REDACTED]"', msg)
    msg = _TOKEN_URL_PATTERN.sub('?token=[REDACTED]', msg)
    msg = _BEARER_PATTERN.sub('Bearer [REDACTED]', msg)
    return msg
```

### File Permissions

```python
# Ensure secrets file has restrictive permissions
os.chmod(secrets_file, 0o600)  # Owner read/write only
```

### Input Validation

```python
def validate_url(url: str) -> bool:
    """Validate URL format and scheme."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('https', 'http') and bool(parsed.netloc)
    except Exception:
        return False
```

This developer documentation focuses on implementation details, design patterns, and development workflows while avoiding duplication with the user-facing README.
