"""LDAP client module for University of Oslo directory services.

This module provides comprehensive LDAP client functionality for querying
UiO's directory services, including user accounts, organizational units,
hosts, and other directory objects.
"""

from .client import LdapClient, LdapError
from .endpoints import Endpoint
from .factory import client as ldap_client

__all__ = [
    "LdapClient",
    "LdapError",
    "Endpoint",
    "ldap_client",
]
