"""Nivlheim API endpoints with type-safe parameter handling.

This module provides comprehensive endpoint definitions for the Nivlheim API
with support for parameterized URLs and ID-based endpoints.
"""

from typing import Literal

from ...core.endpoints import BaseEndpoint


class Endpoint(BaseEndpoint):
    """Comprehensive API endpoints for Nivlheim.

    This enum provides type-safe access to all Nivlheim API endpoints with support
    for parameterized URLs and ID-based endpoints. It includes all endpoints
    from the Nivlheim API documentation.

    The enum supports three types of endpoints:
    1. Simple endpoints (e.g., Endpoint.Hostlist)
    2. Parameterized endpoints (e.g., Endpoint.Host.with_params("hostname"))
    3. Query-based endpoints (e.g., Endpoint.File for various parameters)

    Example:
        # Simple endpoints
        Endpoint.Hostlist                    # "/api/v2/hostlist"
        Endpoint.Status                      # "/api/v2/status"

        # Parameterized endpoints
        Endpoint.Host.with_id("hostname.example.com")
        # → "/api/v2/host/hostname.example.com"

        Endpoint.File.with_params("filename", "hostname")
        # → "/api/v2/file?filename=filename&hostname=hostname"
    """

    # Core endpoints
    File = "/api/v2/file"
    Hostlist = "/api/v2/hostlist"
    Search = "/api/v2/search"
    Msearch = "/api/v2/msearch"
    Grep = "/api/v2/grep"
    Status = "/api/v2/status"

    # Host endpoint with parameter (hostname or certfp)
    Host = "/api/v2/host/{}"

    def external_id_field(self) -> Literal["id", "name", "network", "host"]:
        """Return the name of the field that holds the external ID.

        For Nivlheim, hosts are identified by hostname or certfp.
        Files are identified by fileId, filename+hostname, or filename+certfp.

        Returns:
            The name of the field that holds the external ID for this endpoint.
        """
        if self == Endpoint.Host:
            return "name"  # hostname or certfp mapped to "name"
        if self == Endpoint.File:
            return "name"  # fileId or filename+hostname/certfp combo mapped to "name"
        return "id"
