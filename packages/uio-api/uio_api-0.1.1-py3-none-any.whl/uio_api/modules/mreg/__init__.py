"""MREG API module."""

from .factory import client as mreg_client
from .helpers import normalize_drf_response
from .client import MregClient

# Note: Token and system user management lives at package root to avoid duplication:
# from uio_api import add_system_user, add_token

__all__ = ["mreg_client", "normalize_drf_response", "MregClient"]
