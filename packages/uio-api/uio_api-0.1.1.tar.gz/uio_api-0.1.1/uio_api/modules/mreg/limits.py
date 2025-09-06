"""MREG-specific limit constants.

This module contains limit constants specific to the MREG API,
including pagination limits and safety guards.
"""


class Limits:
    """MREG-specific limit constants.

    Attributes:
        DEFAULT_PAGE_SIZE: Default pagination page size for MREG.
        MAX_PAGE_SIZE: Maximum page size for MREG API.
        MAX_PAGES: Maximum number of pages to fetch as safety guard.
    """

    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    MAX_PAGES = 10000
