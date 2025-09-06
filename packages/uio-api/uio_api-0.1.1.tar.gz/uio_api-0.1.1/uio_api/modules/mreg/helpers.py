"""MREG-specific helper functions for DRF response normalization."""

from typing import Any


def normalize_drf_response(response: Any) -> dict[str, Any]:
    """Normalize a response to DRF pagination format.

    If the response is already a dict with exactly the keys 'count', 'next',
    'previous', 'results', return it as-is. Otherwise, wrap it in DRF format.

    Args:
        response: The API response to normalize.

    Returns:
        DRF-style paginated response: {count: int, next: str|None, previous: str|None, results: [...]}
    """
    # Check if it's already a DRF response
    if isinstance(response, dict) and set(response.keys()) == {
        "count",
        "next",
        "previous",
        "results",
    }:
        return response

    # Wrap in DRF format
    return {"count": 1, "next": None, "previous": None, "results": [response]}
