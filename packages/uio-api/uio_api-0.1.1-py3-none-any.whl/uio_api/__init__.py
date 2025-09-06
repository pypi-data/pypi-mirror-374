"""UIO API Wrapper Package.

A generic API wrapper framework with pluggable authentication, retry mechanisms,
and pagination profiles. Designed to support multiple UIO services with minimal
code duplication.

This package provides a robust, production-ready framework for API interactions with the
following key features:

- Generic API Client: Works with any REST API with configurable behavior
- Authentication Management: Multiple authentication strategies including interactive,
  static, and file-based token providers
- Token Storage: Secure token persistence using OS keyring or TOML files
- Retry Logic: Configurable retry strategies for handling transient failures
- HTTP Client: Built on httpx with automatic token refresh on 401 responses
- Context Management: Proper resource cleanup with context managers
- Profile System: API-specific behavior configuration (pagination, auth schemes, etc.)
- Configuration Management: Centralized configuration with environment variable and file support

Example:
    Basic usage with MREG client::

        from . import mreg_client

        with mreg_client() as m:
            print(m.request("GET", "/api/v1/hosts/?page_size=5"))

    All configuration parameters available per-client::

        with mreg_client(
            url="https://custom.mreg.uio.no",
            timeout=60.0,
            retry_attempts=5,
            secrets_backend="keyring"
        ) as m:
            hosts = m.get_all("/api/v1/hosts/")
"""

from importlib.metadata import PackageNotFoundError, version

# Imports at the top of the file (per E402)
from loguru import logger as _loguru_logger

from .__about__ import __version__
from .constants import APP, APPNAME
from .logging import logger, setup_logging
from .modules.example import example_client
from .modules.ldap import ldap_client
from .modules.mreg import mreg_client, normalize_drf_response
from .modules.nivlheim import nivlheim_client

# Silence the library by default
_loguru_logger.disable(APP)


try:
    __version__ = version("uio_api")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0+unknown"

# If you want opt-in via env/config, you can re-enable here, but do NOT add sinks here.
# Example (optional):
# import os
# if os.environ.get("UIO_API_LOGGING_ENABLED") in {"1","true","yes","on"}:
#     _loguru_logger.enable("uio_api")

__all__ = [
    "APP",
    "APPNAME",
    "__version__",
    "mreg_client",
    "normalize_drf_response",
    "example_client",
    "nivlheim_client",
    "ldap_client",
    "logger",
    "setup_logging",
]
