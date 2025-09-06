"""MREG API endpoints with type-safe parameter handling.

This module provides comprehensive endpoint definitions for the MREG API
with support for parameterized URLs and ID-based endpoints.
"""

from enum import StrEnum
from typing import Literal
from urllib.parse import quote, urljoin


class Endpoint(StrEnum):
    """Comprehensive API endpoints for MREG.

    This enum provides type-safe access to all MREG API endpoints with support
    for parameterized URLs and ID-based endpoints. It includes 64+ endpoints
    covering all major MREG functionality.

    The enum supports three types of endpoints:
    1. Simple endpoints (e.g., Endpoint.Hosts)
    2. Parameterized endpoints (e.g., Endpoint.HostGroupsAddHosts.with_params("group1"))
    3. ID-based endpoints (e.g., Endpoint.Hosts.with_id("host1.uio.no"))

    Example:
        # Simple endpoints
        Endpoint.Hosts                    # "/api/v1/hosts/"
        Endpoint.Networks                 # "/api/v1/networks/"

        # Parameterized endpoints
        Endpoint.HostGroupsAddHosts.with_params("web-servers")
        # → "/api/v1/hostgroups/web-servers/hosts/"

        # ID-based endpoints
        Endpoint.Hosts.with_id("callisto.uio.no")
        # → "/api/v1/hosts/callisto.uio.no"

        # Error prevention for parameterized endpoints
        str(Endpoint.HostGroupsAddHosts)  # Raises ValueError with helpful message
    """

    # Authentication
    Login = "/api/token-auth/"
    Logout = "/api/token-logout/"

    # Core Resources
    Hosts = "/api/v1/hosts/"
    Ipaddresses = "/api/v1/ipaddresses/"
    Naptrs = "/api/v1/naptrs/"
    Srvs = "/api/v1/srvs/"
    Hinfos = "/api/v1/hinfos/"
    Cnames = "/api/v1/cnames/"
    Sshfps = "/api/v1/sshfps/"
    Zones = "/api/v1/zones/"
    History = "/api/v1/history/"
    Txts = "/api/v1/txts/"
    PTR_overrides = "/api/v1/ptroverrides/"
    Locs = "/api/v1/locs/"
    Mxs = "/api/v1/mxs/"
    NAPTRs = "/api/v1/naptrs/"
    Nameservers = "/api/v1/nameservers/"

    # Host Groups
    HostGroups = "/api/v1/hostgroups/"
    HostGroupsAddHostGroups = "/api/v1/hostgroups/{}/groups/"
    HostGroupsRemoveHostGroups = "/api/v1/hostgroups/{}/groups/{}"
    HostGroupsAddHosts = "/api/v1/hostgroups/{}/hosts/"
    HostGroupsRemoveHosts = "/api/v1/hostgroups/{}/hosts/{}"
    HostGroupsAddOwner = "/api/v1/hostgroups/{}/owners/"
    HostGroupsRemoveOwner = "/api/v1/hostgroups/{}/owners/{}"

    # Specialized Resources
    BacnetID = "/api/v1/bacnet/ids/"
    Labels = "/api/v1/labels/"
    LabelsByName = "/api/v1/labels/name/"

    # Networks
    Networks = "/api/v1/networks/"
    NetworksByIP = "/api/v1/networks/ip/"
    NetworksUsedCount = "/api/v1/networks/{}/used_count"
    NetworksUsedList = "/api/v1/networks/{}/used_list"
    NetworksUnusedCount = "/api/v1/networks/{}/unused_count"
    NetworksUnusedList = "/api/v1/networks/{}/unused_list"
    NetworksFirstUnused = "/api/v1/networks/{}/first_unused"
    NetworksReservedList = "/api/v1/networks/{}/reserved_list"
    NetworksUsedHostList = "/api/v1/networks/{}/used_host_list"
    NetworksPTROverrideHostList = "/api/v1/networks/{}/ptroverride_host_list"
    NetworksAddExcludedRanges = "/api/v1/networks/{}/excluded_ranges/"
    NetworksRemoveExcludedRanges = "/api/v1/networks/{}/excluded_ranges/{}"

    # Network policies, attributes, and communities
    NetworkCommunities = "/api/v1/networks/{}/communities/"
    NetworkCommunity = "/api/v1/networks/{}/communities/{}"
    NetworkCommunityHosts = "/api/v1/networks/{}/communities/{}/hosts/"
    NetworkCommunityHost = "/api/v1/networks/{}/communities/{}/hosts/{}"
    NetworkPolicies = "/api/v1/networkpolicies/"
    NetworkPolicyAttributes = "/api/v1/networkpolicyattributes/"

    # Host Policy
    HostPolicyRoles = "/api/v1/hostpolicy/roles/"
    HostPolicyRolesAddAtom = "/api/v1/hostpolicy/roles/{}/atoms/"
    HostPolicyRolesRemoveAtom = "/api/v1/hostpolicy/roles/{}/atoms/{}"
    HostPolicyRolesAddHost = "/api/v1/hostpolicy/roles/{}/hosts/"
    HostPolicyRolesRemoveHost = "/api/v1/hostpolicy/roles/{}/hosts/{}"
    HostPolicyAtoms = "/api/v1/hostpolicy/atoms/"

    # Permissions
    PermissionNetgroupRegex = "/api/v1/permissions/netgroupregex/"

    # Zones (constructed from base Zones endpoint)
    ForwardZones = f"{Zones}forward/"
    ReverseZones = f"{Zones}reverse/"

    # Zone Delegations (MUST have trailing slash)
    ForwardZonesDelegations = f"{ForwardZones}{{}}/delegations/"
    ReverseZonesDelegations = f"{ReverseZones}{{}}/delegations/"

    ForwardZonesDelegationsZone = f"{ForwardZones}{{}}/delegations/{{}}"
    ReverseZonesDelegationsZone = f"{ReverseZones}{{}}/delegations/{{}}"

    # Zone Nameservers (must NOT have trailing slash)
    ForwardZonesNameservers = f"{ForwardZones}{{}}/nameservers"
    ReverseZonesNameservers = f"{ReverseZones}{{}}/nameservers"

    # Special Zone Operations
    ForwardZoneForHost = f"{ForwardZones}hostname/"

    # Token Management
    TokenIsValid = "/api/token-is-valid/"

    # Meta Endpoints
    MetaUser = "/api/meta/user"
    MetaVersion = "/api/meta/version"
    MetaLibraries = "/api/meta/libraries"

    # Health Checks
    HealthHeartbeat = "/api/meta/health/heartbeat"
    HealthLDAP = "/api/meta/health/ldap"

    def __str__(self) -> str:
        """Prevent direct usage without parameters where needed.

        Raises:
            ValueError: If the endpoint requires parameters and none are provided.

        Example:
            str(Endpoint.HostGroupsAddHosts)  # Raises ValueError
        """
        if "{}" in self.value:
            raise ValueError(f"Endpoint {self.name} requires parameters. Use `with_params`.")
        return self.value

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
        if self in (
            Endpoint.Hosts,
            Endpoint.HostGroups,
            Endpoint.Cnames,
            Endpoint.ForwardZones,
            Endpoint.ReverseZones,
            Endpoint.ForwardZonesDelegations,
            Endpoint.ReverseZonesDelegations,
            Endpoint.HostPolicyRoles,
            Endpoint.HostPolicyAtoms,
            Endpoint.Nameservers,
        ):
            return "name"
        if self in (Endpoint.Networks,):
            return "network"
        if self in (Endpoint.Hinfos, Endpoint.Locs):
            return "host"
        return "id"

    def with_id(self, identity: str | int) -> str:
        """Return the endpoint with an ID appended.

        Appends the provided ID to the endpoint URL, properly URL-encoding
        the ID value.

        Args:
            identity: The ID to append (string or integer).

        Returns:
            The endpoint URL with the ID appended.

        Example:
            Endpoint.Hosts.with_id("callisto.uio.no")
            # → "/api/v1/hosts/callisto.uio.no"

            Endpoint.Networks.with_id(123)
            # → "/api/v1/networks/123"
        """
        id_field = quote(str(identity))
        return urljoin(self.value, id_field)

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
            Endpoint.HostGroupsAddHosts.with_params("web-servers")
            # → "/api/v1/hostgroups/web-servers/hosts/"

            Endpoint.HostGroupsRemoveHosts.with_params("web-servers", "web1")
            # → "/api/v1/hostgroups/web-servers/hosts/web1"
        """
        placeholders_count = self.value.count("{}")
        if placeholders_count != len(params):
            raise ValueError(
                f"{self.name} endpoint expects {placeholders_count} parameters, got {len(params)}."
            )
        encoded_params = (quote(str(param)) for param in params)
        return self.value.format(*encoded_params)
