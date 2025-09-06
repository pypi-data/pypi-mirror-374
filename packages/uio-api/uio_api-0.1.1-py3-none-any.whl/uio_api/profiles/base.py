"""Base profile system for API-specific behavior configuration.

This module provides the foundation for configuring API-specific behavior
including pagination strategies, authentication schemes, and path normalization.
"""

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlsplit, urlunsplit


class Pagination(Protocol):
    """Protocol for pagination strategy implementations.

    Different APIs use different pagination formats. This protocol allows
    each API module to define its own pagination behavior.
    """

    def is_page(self, payload: Any) -> bool: ...
    def extract_results(self, payload: Any) -> list[Any]: ...
    def next_path(self, payload: Any) -> str | None: ...


@dataclass(frozen=True, slots=True)
class DrfPagination:
    """Django REST Framework pagination strategy.

    Handles DRF-style pagination with 'results', 'next', 'previous', and 'count' fields.
    """

    def is_page(self, payload: Any) -> bool:
        """Check if the payload is a paginated response.

        Args:
            payload: The response payload to check. Should be a dict for DRF pagination.

        Returns:
            True if the payload contains pagination fields.

        Note:
            This method includes defensive type checking to handle unexpected payload types.
        """
        # Defensive check: ensure payload is a dict before checking keys
        if not isinstance(payload, dict):
            return False
        return "results" in payload

    def extract_results(self, payload: Any) -> list[Any]:
        """Extract the results list from a paginated response.

        Args:
            payload: The paginated response payload.

        Returns:
            List of results, or empty list if not paginated.
        """
        return payload.get("results", []) if isinstance(payload, dict) else []

    def next_path(self, payload: Any) -> str | None:
        """Extract the next page path from a paginated response.

        Args:
            payload: The paginated response payload.

        Returns:
            Relative path for the next page, or None if no next page.
        """
        if not isinstance(payload, dict):
            return None
        next_url = payload.get("next")
        if not next_url:
            return None
        # Convert absolute URL to relative path
        parsed = urlsplit(next_url)
        return parsed.path + (("?" + parsed.query) if parsed.query else "")


@dataclass(frozen=True, slots=True)
class NoPagination:
    """No pagination strategy for APIs that don't use pagination.

    Treats all responses as single-page responses.
    """

    def is_page(self, payload: Any) -> bool:
        """Always returns False since there's no pagination.

        Args:
            payload: The response payload (ignored).

        Returns:
            Always False.
        """
        return False

    def extract_results(self, payload: Any) -> list[Any]:
        """Wrap the payload in a list.

        Args:
            payload: The response payload.

        Returns:
            List containing the single payload item.
        """
        return [payload]

    def next_path(self, payload: Any) -> str | None:
        """Always returns None since there's no pagination.

        Args:
            payload: The response payload (ignored).

        Returns:
            Always None.
        """
        return None


@dataclass(frozen=True, slots=True)
class ApiProfile:
    """API profile defining behavior for a specific API.

    This class encapsulates all the API-specific behavior including
    authentication schemes, pagination strategies, and path normalization rules.

    Attributes:
        name: Human-readable name for this API (e.g., "mreg", "foo").
        scheme: Authentication scheme (e.g., "Token", "Bearer").
        login_path: Path for token authentication (e.g., "/api/token-auth/").
        logout_path: Path for token logout/revocation (e.g., "/api/token-logout/").
        require_trailing_slash: Whether endpoints require trailing slashes.
        pagination: Pagination strategy for this API.
        max_page_size: Maximum page size allowed by the API (None if unknown).
    """

    name: str
    scheme: str
    login_path: str | None
    logout_path: str | None
    require_trailing_slash: bool
    pagination: Pagination
    max_page_size: int | None

    def normalize_path(self, path: str) -> str:
        """Normalize a path according to this API's rules.

        Applies trailing slash rules and other path normalization
        specific to this API.

        Args:
            path: The path to normalize.

        Returns:
            Normalized path string.

        Example:
            profile = ApiProfile(..., require_trailing_slash=True, ...)
            profile.normalize_path("/api/v1/hosts")  # Returns "/api/v1/hosts/"
            profile.normalize_path("/api/v1/hosts/")  # Returns "/api/v1/hosts/"
        """
        if not path:
            return "/"

        if self.require_trailing_slash and not path.endswith("/"):
            # Let callers pass query strings; keep them
            parts = urlsplit(path)
            p = parts.path + ("" if parts.path.endswith("/") else "/")
            return urlunsplit((parts.scheme, parts.netloc, p, parts.query, parts.fragment))

        return path
