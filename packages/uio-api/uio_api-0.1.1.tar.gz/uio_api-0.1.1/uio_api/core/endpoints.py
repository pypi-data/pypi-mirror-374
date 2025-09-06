"""Generic endpoint utilities for API modules.

This module provides base classes and utilities for defining API endpoints
with parameter substitution and ID-based endpoints. This allows modules like
MREG and Nivlheim to define their endpoints using a common, reusable pattern.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal
from urllib.parse import quote, urljoin


class BaseEndpoint(StrEnum):
    """Base class for API endpoints with parameter substitution support.

    This class provides the foundation for defining API endpoints that support:
    - Parameterized URLs (e.g., /api/v1/hosts/{hostname})
    - ID-based endpoints
    - Type-safe endpoint definitions

    Subclasses should define their endpoint URLs as class attributes.
    """

    def requires_search_for_id(self) -> bool:
        """Return True if this endpoint requires a search for an ID.

        Some endpoints use names, networks, or hosts as identifiers instead
        of numeric IDs. This method helps determine the appropriate ID field
        for lookups.

        Returns:
            True if the endpoint requires searching for an ID (not using numeric ID).
        """
        return self.external_id_field() != "id"

    def external_id_field(self) -> Literal["id", "name", "network", "host"]:
        """Return the name of the field that holds the external ID.

        Different endpoints use different fields as their primary identifier:
        - "id": Numeric ID (default)
        - "name": String name (hosts, zones, host groups, etc.)
        - "network": Network CIDR (networks)
        - "host": Host name (HINFO, LOC records)

        Returns:
            The name of the field that holds the external ID for this endpoint.
        """
        return "id"

    def __str__(self) -> str:
        """Prevent direct usage without parameters where needed.

        Raises:
            ValueError: If the endpoint requires parameters and none are provided.

        Example:
            str(Endpoint.HostGroupsAddHosts)  # Raises ValueError
        """
        if "{}" in self.value:
            raise ValueError(f"Endpoint {self.name} requires parameters. Use `with_params`.")
        return str(self.value)

    def with_id(self, identity: str | int) -> str:
        """Return the endpoint with an ID appended.

        Appends the provided ID to the endpoint URL, properly URL-encoding
        the ID value.

        Args:
            identity: The ID to append (string or integer).

        Returns:
            The endpoint URL with the ID appended.

        Example:
            endpoint.with_id("callisto.uio.no")
            # → "/api/v1/hosts/callisto.uio.no"

            endpoint.with_id(123)
            # → "/api/v1/networks/123"
        """
        id_field = quote(str(identity))
        return str(urljoin(str(self.value), id_field))

    def with_params(self, *params: str | int) -> str:
        """Construct and return an endpoint URL by inserting parameters.

        Replaces {} placeholders in the endpoint URL with the provided parameters.
        All parameters are URL-encoded automatically.

        Args:
            *params: A sequence of parameters to be inserted into the URL.

        Returns:
            A fully constructed endpoint URL with parameters.

        Raises:
            ValueError: If the number of provided parameters does not match the
                        number of placeholders in the URL.

        Example:
            endpoint.with_params("web-servers")
            # → "/api/v1/hostgroups/web-servers/hosts/"

            endpoint.with_params("web-servers", "web1")
            # → "/api/v1/hostgroups/web-servers/hosts/web1"
        """
        placeholders_count = self.value.count("{}")
        if placeholders_count != len(params):
            raise ValueError(
                f"{self.name} endpoint expects {placeholders_count} parameters, got {len(params)}."
            )
        encoded_params = (quote(str(param)) for param in params)
        return str(self.value).format(*encoded_params)
