"""Nivlheim API client module.

This module provides a Python client for the Nivlheim API with type-safe endpoints
and automatic APIKEY authentication.
"""

from .client import NivlheimClient
from .endpoints import Endpoint
from .factory import client as nivlheim_client

__all__ = [
    "NivlheimClient",
    "Endpoint",
    "nivlheim_client",
]
