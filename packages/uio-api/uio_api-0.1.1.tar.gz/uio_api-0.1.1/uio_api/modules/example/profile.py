"""Example API profile configuration.

This demonstrates how to create a profile for a different API
that doesn't use DRF pagination.
"""

from ...profiles.base import ApiProfile, NoPagination

# Example API Profile (non-DRF, no pagination)
ExampleApiProfile = ApiProfile(
    name="example",
    scheme="Bearer",  # Different auth scheme
    login_path="/oauth/token",  # Different login path
    logout_path=None,  # No logout endpoint
    require_trailing_slash=False,  # No trailing slash requirement
    pagination=NoPagination(),  # No pagination
    max_page_size=None,  # No pagination limits
)
