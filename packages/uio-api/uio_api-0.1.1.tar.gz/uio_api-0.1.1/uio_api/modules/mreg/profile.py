"""MREG API profile configuration.

This module defines the MREG-specific API profile including authentication
scheme, pagination strategy, and path normalization rules.
"""

from .endpoints import Endpoint
from .limits import Limits
from ...profiles.base import ApiProfile, DrfPagination

# MREG API Profile
MregApiProfile = ApiProfile(
    name="mreg",
    scheme="Token",
    login_path=Endpoint.Login,
    logout_path=Endpoint.Logout,
    require_trailing_slash=True,  # DRF likes trailing slashes
    pagination=DrfPagination(),
    max_page_size=Limits.MAX_PAGE_SIZE,
)
