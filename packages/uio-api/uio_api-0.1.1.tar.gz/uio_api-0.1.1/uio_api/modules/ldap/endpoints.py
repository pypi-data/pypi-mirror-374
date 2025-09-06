from enum import StrEnum


class Endpoint(StrEnum):
    """LDAP base DN shortcuts to mirror API Endpoint patterns.

    These are convenience constants for common UiO LDAP bases. They are not HTTP
    endpoints but provide a familiar API surface similar to REST modules.
    """

    People = "cn=people,dc=uio,dc=no"
    Users = "cn=users,cn=system,dc=uio,dc=no"
    Hosts = "cn=hosts,cn=system,dc=uio,dc=no"
    Services = "cn=services,dc=uio,dc=no"
    Organization = "cn=organization,dc=uio,dc=no"
    Netgroups = "cn=netgroups,cn=system,dc=uio,dc=no"
    Filegroups = "cn=filegroups,cn=system,dc=uio,dc=no"
    Automount = "cn=automount,cn=system,dc=uio,dc=no"
