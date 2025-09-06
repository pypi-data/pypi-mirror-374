"""MREG-specific client with DRF normalization and system user management."""

from typing import Any

from ...core.client import ApiClient
from .helpers import normalize_drf_response


class MregClient(ApiClient):
    """MREG-specific client with DRF normalization and system user management.

    This client automatically applies DRF normalization to GET requests and
    provides methods for managing system accounts.
    """

    @property
    def module(self) -> str:
        """Return the module name for this client."""
        return "mreg"

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        ok404: bool = False,
        post_process: Any = None,
    ) -> Any:
        """GET request with automatic DRF normalization.

        If no post_process is provided, defaults to normalize_drf_response.
        """
        if post_process is None:
            post_process = normalize_drf_response
        return super().get(path, params=params, ok404=ok404, post_process=post_process)

    def get_all(
        self,
        path: str,
        *,
        page_size: int | None = -1,
        params: dict[str, Any] | None = None,
        max_pages: int = 10000,
    ) -> list[Any]:
        """Get all results from a paginated endpoint with MREG-optimized defaults.

        For MREG, defaults to using maximum page size to get maximum
        results per page, reducing the number of API calls needed.

        Args:
            path: The API endpoint path.
            page_size: Override the default page size. Defaults to maximum page size for MREG.
            params: Additional query parameters.

        Returns:
            List of all results across all pages.
        """
        # Use maximum page size as default for MREG to minimize API calls
        return super().get_all(
            path,
            page_size=page_size or -1,
            params=params,
            max_pages=max_pages,
        )
