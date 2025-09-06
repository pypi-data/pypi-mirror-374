"""Token scope definition and URL normalization.

This module provides token scoping functionality that allows tokens to be
scoped to specific users and URLs, enabling multi-user and multi-instance
token management.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit


def normalize_service_url(url: str) -> str:
    """Normalize a service URL for stable keying.

    Normalizes URLs by:
    - Converting to lowercase
    - Keeping only scheme and netloc (host[:port])
    - Dropping path, query, and fragment

    Args:
        url: URL to normalize.

    Returns:
        Normalized URL string.

    Example:
        normalize_service_url("https://API.EXAMPLE.COM/api/v1/")
        # Returns: "https://api.example.com"

        normalize_service_url("https://api.example.com:8443/path?query=1#fragment")
        # Returns: "https://api.example.com:8443"
    """
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), "", "", ""))


@dataclass(frozen=True, slots=True)
class TokenScope:
    """Token scope definition for multi-user, multi-instance, multi-module token management.

    Token scopes allow tokens to be associated with specific modules, users and URLs,
    enabling secure multi-user environments and support for multiple API
    instances and modules without token collisions.

    When username is None, the scope represents a 'default' scope for that module/URL,
    which can be used as a fallback when user-specific tokens are not available.

    Attributes:
        module: The API module name (e.g., "mreg", "example").
        url: The API URL for this scope.
        username: Username for this scope, or None for default scope.

    Example:
        # User-specific scope
        scope = TokenScope(module="mreg", url="https://mreg.uio.no", username="bob-drift")

        # Default scope (fallback)
        default_scope = TokenScope(module="mreg", url="https://mreg.uio.no", username=None)

        # Different module, same URL - no collision
        other_scope = TokenScope(module="example", url="https://mreg.uio.no", username="bob-drift")
    """

    module: str
    url: str
    username: str | None = None

    def url_key(self) -> str:
        """Get the normalized URL key for this scope.

        Returns:
            Normalized URL string for consistent keying.

        Example:
            scope = TokenScope(module="example", url="https://API.EXAMPLE.COM/api/", username="bob")
            scope.url_key()  # Returns: "https://api.example.com"
        """
        return normalize_service_url(self.url)

    def identity(self) -> str:
        """Get a unique identity string for this scope.

        Returns:
            Unique identity string in format "module|username|url_key".

        Example:
            scope = TokenScope(module="mreg", url="https://mreg.uio.no", username="bob-drift")
            scope.identity()  # Returns: "mreg|bob-drift|https://mreg.uio.no"

            default_scope = TokenScope(module="mreg", url="https://mreg.uio.no", username=None)
            default_scope.identity()  # Returns: "mreg|default|https://mreg.uio.no"
        """
        return f"{self.module}|{self.username or 'default'}|{self.url_key()}"
