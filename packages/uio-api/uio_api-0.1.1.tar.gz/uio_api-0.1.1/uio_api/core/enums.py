"""Core enums and constants for the UIO API wrapper framework.

This module contains all enum definitions used throughout the framework,
including authentication schemes, retry decisions, HTTP methods,
and file permissions.
"""

from enum import Enum, IntEnum, StrEnum, unique


@unique
class LogLevel(StrEnum):
    """Strongly-typed logging levels (compatible with str)."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@unique
class SecretsBackend(StrEnum):
    """Backend storage options for secrets/tokens.

    Attributes:
        TOML: Store secrets in TOML files.
        KEYRING: Store secrets in OS keyring (macOS Keychain, Windows Credential Manager, etc.).
    """

    TOML = "toml"
    KEYRING = "keyring"


@unique
class FilePerm(IntEnum):
    """File permission constants.

    Attributes:
        OWNER_RW: Owner read/write permissions (0o600).
    """

    OWNER_RW = 0o600


@unique
class DirPerm(IntEnum):
    """Directory permission constants.

    Attributes:
        OWNER_RWX: Owner read/write/execute permissions (0o700).
    """

    OWNER_RWX = 0o700


@unique
class RetryDecision(Enum):
    """Retry decision options for retry strategies.

    Attributes:
        RETRY: Retry the request after a delay.
        GIVE_UP: Stop retrying and raise the error.
    """

    RETRY = "retry"
    GIVE_UP = "give_up"


@unique
class HttpMethod(Enum):
    """HTTP method constants.

    Attributes:
        GET: HTTP GET method.
        POST: HTTP POST method.
        PUT: HTTP PUT method.
        DELETE: HTTP DELETE method.
        HEAD: HTTP HEAD method.
        OPTIONS: HTTP OPTIONS method.
        PATCH: HTTP PATCH method.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


@unique
class AuthScheme(Enum):
    """Authentication scheme constants.

    Attributes:
        TOKEN: Token-based authentication scheme.
        BEARER: Bearer token authentication scheme.
    """

    TOKEN = "Token"
    BEARER = "Bearer"
