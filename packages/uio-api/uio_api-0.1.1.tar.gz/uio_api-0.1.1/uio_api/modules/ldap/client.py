"""LDAP client for querying University of Oslo directory services.

This module provides a comprehensive LDAP client for querying UiO's directory
services, with support for anonymous binding and authenticated searches.
"""

import shlex
import types
from contextlib import contextmanager
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Callable, Iterator, Literal

import ldap3  # type: ignore[import-untyped]
from ldap3.core.exceptions import LDAPOperationResult  # type: ignore[import-untyped]

from ...core.enums import RetryDecision as RetryDecisionEnum
from ...core.retry.policy import default_retry_strategy
from ...core.tokens.scope import normalize_service_url
from ...logging import logger

# LDAP result descriptions for user-friendly error messages
LDAP_RESULT_DESCRIPTIONS = {
    0: "Success",
    3: "The search operation timed out.",
    4: "The search exceeded the server's size limit.",
    6: "A required LDAP extension is unavailable on the server.",
    10: "The server refers you to another LDAP server.",
    11: "Operation aborted: administrative limits were exceeded (try a more narrow search).",
    32: "No such object: the requested entry was not found.",
    49: "Invalid credentials: username or password is incorrect.",
    50: "Insufficient access rights to perform this operation.",
    65: "Object class violation: schema rules would be broken.",
    68: "Entry already exists with that name.",
    80: "Other error: see server logs for details.",
}


# LDAP-specific constants and result codes (module-scoped)
class LdapResultCode:
    SUCCESS = 0
    TIME_LIMIT_EXCEEDED = 3
    SIZE_LIMIT_EXCEEDED = 4
    REFERRAL = 10
    ADMIN_LIMIT_EXCEEDED = 11
    NO_SUCH_OBJECT = 32
    INVALID_CREDENTIALS = 49
    INSUFFICIENT_ACCESS_RIGHTS = 50
    ENTRY_ALREADY_EXISTS = 68
    OTHER = 80


class LdapConstants:
    DEFAULT_LDAP_URL = "ldap://ldap.uio.no"
    DEFAULT_DOMAIN_CONTROLLERS = ["uio", "no"]
    BASE_PEOPLE = "cn=people,dc=uio,dc=no"
    BASE_USERS = "cn=users,cn=system,dc=uio,dc=no"
    BASE_HOSTS = "cn=hosts,cn=system,dc=uio,dc=no"
    BASE_SERVICES = "cn=services,dc=uio,dc=no"
    BASE_ORGANIZATION = "cn=organization,dc=uio,dc=no"
    BASE_NETGROUPS = "cn=netgroups,cn=system,dc=uio,dc=no"
    BASE_FILEGROUPS = "cn=filegroups,cn=system,dc=uio,dc=no"
    BASE_AUTOMOUNT = "cn=automount,cn=system,dc=uio,dc=no"


@dataclass(slots=True)
class LdapClient:
    """LDAP client for querying UiO directory services.

    This class provides a comprehensive interface for querying UiO's LDAP directory
    services, with support for both anonymous and authenticated access.

    Attributes:
        url: LDAP server URL (e.g., "ldap://ldap.uio.no")
        domain_controllers: Domain components for base DN construction (default: ["uio", "no"])
        service: Whether to treat users as service accounts by default
        bind_user: Default username for binding (optional)
        bind_password: Default password for binding (optional)
        allow_anonymous: Whether anonymous binding is allowed (default: True)
        _persistent_conn: Internal persistent LDAP connection (None when not in context)
    """

    url: str
    domain_controllers: list[str] = field(default_factory=list)
    service: bool = False
    bind_user: str | None = None
    bind_password: str | None = None
    allow_anonymous: bool = True
    _persistent_conn: ldap3.Connection | None = None
    # Client-level knobs
    _retry_attempts: int = 1
    _interactive: bool = False
    _prompt_username: Callable[[], str] | None = None
    _prompt_password: Callable[[str], str] | None = None

    def __post_init__(self) -> None:
        """Set default domain controllers if not provided."""
        if self.domain_controllers is None:
            self.domain_controllers = LdapConstants.DEFAULT_DOMAIN_CONTROLLERS

    @property
    def module(self) -> str:
        return "ldap"

    def open_persistent_connection(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        retry_attempts: int | None = None,
    ) -> None:
        """Establish a persistent LDAP connection for the session.

        Args:
            username: Username for binding (uses instance default if None)
            password: Password for binding (uses instance default if None)

        Raises:
            LdapError: If binding fails
        """
        if self._persistent_conn is not None:
            return  # Already connected

        user = username or self.bind_user
        pw = password or self.bind_password

        # Check if anonymous binding is allowed
        if user is None and not self.allow_anonymous:
            raise ValueError("Anonymous binding not allowed for this LDAP source")

        # Convert username to DN if needed
        dn = None
        if user:
            dn = user if "," in user else self.username(user, service=self.service)

        attempts = retry_attempts or 1
        strategy = default_retry_strategy(max_attempts=attempts)
        last_exc: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                logger.bind(endpoint=self.url).debug("Establishing persistent LDAP connection")
                self._persistent_conn = ldap3.Connection(
                    ldap3.Server(self.url, get_info=ldap3.NONE),
                    user=dn,
                    password=pw,
                    client_strategy=ldap3.SAFE_SYNC,
                    raise_exceptions=True,
                    auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND,
                )

                if dn:
                    logger.bind(endpoint=self.url).debug(
                        "Persistent LDAP bind successful for user: {}", dn
                    )
                else:
                    logger.bind(endpoint=self.url).debug(
                        "Persistent LDAP anonymous bind successful"
                    )

                return

            except ldap3.core.exceptions.LDAPOperationResult as exc:
                code = exc.result
                desc = exc.description or ""
                friendly = LDAP_RESULT_DESCRIPTIONS.get(code, desc)

                # Map LDAP codes to retryable HTTP statuses for shared strategy
                mapped_status = None
                if code == LdapResultCode.INVALID_CREDENTIALS:
                    mapped_status = HTTPStatus.SERVICE_UNAVAILABLE

                decision = strategy(attempt, "GET", self.url, mapped_status, exc)
                if decision.decision == RetryDecisionEnum.RETRY and attempt < attempts:
                    if decision.delay_seconds:
                        import time

                        logger.bind(endpoint=self.url).info(
                            "Retrying LDAP bind in {:.3f}s (attempt {}/{})",
                            decision.delay_seconds,
                            attempt + 1,
                            attempts,
                        )
                        time.sleep(decision.delay_seconds)
                    last_exc = LdapError(e=exc, msg=friendly, code=code)
                    continue
                raise LdapError(e=exc, msg=friendly, code=code) from exc

            except Exception as exc:
                decision = strategy(attempt, "GET", self.url, None, exc)
                if decision.decision == RetryDecisionEnum.RETRY and attempt < attempts:
                    if decision.delay_seconds:
                        import time

                        logger.bind(endpoint=self.url).info(
                            "Retrying LDAP bind in {:.3f}s (attempt {}/{})",
                            decision.delay_seconds,
                            attempt + 1,
                            attempts,
                        )
                        time.sleep(decision.delay_seconds)
                    last_exc = exc
                    continue
                raise LdapError(e=exc, msg=str(exc)) from exc

        if last_exc:
            raise last_exc

    def close_persistent_connection(self) -> None:
        """Close the persistent LDAP connection."""
        if self._persistent_conn is not None:
            try:
                self._persistent_conn.unbind()
                logger.bind(endpoint=self.url).debug("Persistent LDAP connection closed")
            except Exception as e:
                logger.bind(endpoint=self.url).warning(
                    "Error closing persistent LDAP connection: {}", e
                )
            finally:
                self._persistent_conn = None

    # Context manager with interactive re-prompt support
    def __enter__(self) -> "LdapClient":
        attempts = self._retry_attempts if self._retry_attempts and self._retry_attempts > 0 else 1
        for attempt in range(1, attempts + 1):
            try:
                self.open_persistent_connection(retry_attempts=1)
                return self
            except LdapError as e:
                if e.code == LdapResultCode.INVALID_CREDENTIALS and self._interactive:
                    if not self.bind_user:
                        if self._prompt_username:
                            user = self._prompt_username()
                        else:
                            import getpass

                            user = getpass.getuser()
                        self.bind_user = user
                    base = normalize_service_url(self.url)
                    print(f"Connecting to {base}")
                    if self._prompt_password:
                        pw = self._prompt_password(self.bind_user or "")
                    else:
                        import getpass

                        pw = getpass.getpass(f"Password for {self.bind_user}: ")
                    self.bind_password = pw
                    if attempt < attempts:
                        continue
                    raise
                if attempt < attempts:
                    strategy = default_retry_strategy(max_attempts=attempts)
                    decision = strategy(attempt, "GET", self.url, None, e)
                    if decision.decision == RetryDecisionEnum.RETRY and decision.delay_seconds:
                        import time

                        logger.bind(endpoint=self.url).info(
                            "Retrying LDAP connect in {:.3f}s (attempt {}/{})",
                            decision.delay_seconds,
                            attempt + 1,
                            attempts,
                        )
                        time.sleep(decision.delay_seconds)
                        continue
                logger.bind(endpoint=self.url).error(
                    "Failed to establish persistent LDAP connection: {}", e
                )
                raise
        # This should never be reached, but add it for type safety
        raise RuntimeError("Failed to establish LDAP connection after all attempts")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None:
        self.close_persistent_connection()

    def username(self, username: str, service: bool | None = None) -> str:
        """Generate a valid LDAP distinguished name for a username.

        Args:
            username: The username to convert to DN
            service: Whether this is a service account (overrides instance default)

        Returns:
            A properly formatted LDAP distinguished name

        Examples:
            >>> ldap = LdapSource("ldap://ldap.uio.no")
            >>> ldap.username("radius", service=False)
            'uid=radius,cn=people,dc=uio,dc=no'
            >>> ldap.username("radius", service=True)
            'cn=radius,cn=services,dc=uio,dc=no'
        """
        if "," in username:
            return username  # Already a DN
        if service is None:
            service = self.service
        if service:
            return self.base(cn=[username, "services"])
        return self.base(uid=[username], cn=["people"])

    def build_ldapsearch_cmd(
        self,
        conn: ldap3.Connection,
        base: str,
        filter_: str,
        attributes: list[str] | str | None,
        leading: str = "",
    ) -> list[str]:
        """Build a copy-and-pasteable ldapsearch command for debugging.

        Args:
            conn: A bound ldap3.Connection
            base: The search base DN
            filter_: The LDAP filter string
            attributes: List of attribute names to request
            leading: Leading string for each line (e.g., indentation)

        Returns:
            List of command lines for an equivalent ldapsearch command
        """
        simple_bind = conn.authentication == ldap3.SIMPLE

        lines = ["ldapsearch"]

        if simple_bind:
            lines.append(f"{leading}-x -W -D {shlex.quote(conn.user or '')}")
        else:
            lines.append(f"{leading}-Y GSSAPI")

        lines.extend(
            [
                f"{leading}-H {shlex.quote(self.url)}",
                f"{leading}-b {shlex.quote(base)}",
                f"{leading}-s subtree",
                f"{leading}{shlex.quote(filter_)}",
            ]
        )

        # Normalize attributes to a list
        if attributes is None:
            attr_list = ["*"]
        elif isinstance(attributes, str):
            attr_list = [attributes]
        else:
            attr_list = attributes

        for attr in attr_list:
            lines.append(f"{leading}{shlex.quote(attr)}")

        return lines

    @contextmanager
    def bind(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        service: bool | None = None,
    ) -> Iterator[ldap3.Connection]:
        """Context manager for LDAP binding with automatic unbinding.

        Args:
            username: Username for binding (uses instance default if None)
            password: Password for binding (uses instance default if None)
            service: Whether this is a service account bind

        Yields:
            A bound ldap3.Connection object

        Raises:
            LdapError: On binding or connection failures
        """
        service = self.service if service is None else service
        user = username or self.bind_user

        # Check if anonymous binding is allowed
        if user is None and not self.allow_anonymous:
            raise ValueError("Anonymous binding not allowed for this LDAP source")

        # Convert username to DN if needed
        dn = None
        if user:
            dn = user if "," in user else self.username(user, service=service)

        conn = None
        try:
            logger.bind(endpoint=self.url).debug("Attempting LDAP bind to {}", self.url)
            conn = ldap3.Connection(
                ldap3.Server(self.url, get_info=ldap3.NONE),
                user=dn,
                password=password or self.bind_password,
                client_strategy=ldap3.SAFE_SYNC,
                raise_exceptions=True,
                auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND,
            )

            if dn:
                logger.bind(endpoint=self.url).debug("LDAP bind successful for user: {}", dn)
            else:
                logger.bind(endpoint=self.url).debug("LDAP anonymous bind successful")

            yield conn

        except ldap3.core.exceptions.LDAPOperationResult as exc:
            code = exc.result
            desc = exc.description or ""
            friendly = LDAP_RESULT_DESCRIPTIONS.get(code, desc)

            cmd = ["ldapwhoami", f"-H {shlex.quote(self.url)}"]
            if dn:
                cmd.append("-x -W -D " + shlex.quote(dn))
            else:
                cmd.append("-x")

            payload = {
                "phase": "bind",
                "request": cmd,
                "bind_dn": dn or "anonymous",
            }
            raise LdapError(e=exc, msg=friendly, info=payload, code=code) from exc

        except ldap3.core.exceptions.LDAPExceptionError as exc:
            code = getattr(exc, "result", None)
            desc = getattr(exc, "description", "") or ""
            friendly = LDAP_RESULT_DESCRIPTIONS.get(code, desc) if code else str(exc)

            cmd = ["ldapwhoami", f"-H {shlex.quote(self.url)}"]
            if dn:
                cmd.append("-x -W -D " + shlex.quote(dn))
            else:
                cmd.append("-x")

            payload = {
                "phase": "bind",
                "request": cmd,
                "bind_dn": dn or "anonymous",
            }
            raise LdapError(e=exc, msg=friendly, info=payload, code=code) from exc

        finally:
            if conn:
                try:
                    conn.unbind()
                    logger.bind(endpoint=self.url).debug("LDAP unbind successful")
                except Exception as e:
                    logger.bind(endpoint=self.url).warning("LDAP unbind failed: {}", e)

    def search(
        self,
        base: str,
        filter_: str,
        url: str | None = None,
        attributes: list[str] | str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        retry_attempts: int | None = None,
    ) -> list[dict[str, Any]]:
        """Search LDAP directory and return results as a list.

        Args:
            base: The base DN for the search
            filter_: LDAP filter string
            url: Override the LDAP server URL
            attributes: Attributes to return (default: ALL_ATTRIBUTES)
            username: Username for binding
            password: Password for binding

        Returns:
            List of dictionaries containing search results

        Raises:
            LdapError: On search operation failures
        """
        if attributes is None:
            attributes = ldap3.ALL_ATTRIBUTES
        elif isinstance(attributes, str):
            attributes = attributes.split(",")

        url = self.url if url is None else url
        username = username or self.bind_user
        password = password or self.bind_password

        attempts = retry_attempts or 1
        strategy = default_retry_strategy(max_attempts=attempts)

        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            # Use persistent connection if available, otherwise create new one
            if self._persistent_conn is not None:
                conn = self._persistent_conn
                logger.bind(endpoint=base).debug(
                    "LDAP search (persistent): base={}, filter={}, attributes={}",
                    base,
                    filter_,
                    attributes,
                )
            else:
                # Fallback to per-operation binding
                conn_context = self.bind(username, password, service=self.service)
                conn = conn_context.__enter__()
                logger.bind(endpoint=base).debug(
                    "LDAP search (per-op): base={}, filter={}, attributes={}",
                    base,
                    filter_,
                    attributes,
                )

            try:
                _, _, response, _ = conn.search(
                    search_base=base,
                    search_scope=ldap3.SUBTREE,
                    search_filter=filter_,
                    attributes=attributes,
                )

                results = []
                for entry in response:
                    results.append(dict(entry["attributes"]))

                if results:
                    logger.bind(endpoint=base).success(
                        "LDAP search successful: {} results", len(results)
                    )
                else:
                    logger.bind(endpoint=base).info("LDAP search completed: no results found")

                # Clean up per-operation connection if we created one
                if self._persistent_conn is None:
                    conn_context.__exit__(None, None, None)

                return results

            except LDAPOperationResult as exc:
                # Clean up per-operation connection on error
                if self._persistent_conn is None:
                    try:
                        conn_context.__exit__(type(exc), exc, exc.__traceback__)
                    except Exception:
                        pass

                code = exc.result
                desc = exc.description or ""
                friendly_message = LDAP_RESULT_DESCRIPTIONS.get(code, desc)

                payload = {
                    "phase": "search",
                    "request": self.build_ldapsearch_cmd(
                        conn=conn, base=base, filter_=filter_, attributes=attributes
                    ),
                    "details": {
                        "base": base,
                        "filter": filter_,
                        "attributes": attributes,
                    },
                }

                logger.bind(endpoint=base).error(
                    "LDAP search failed: {} (code: {})", friendly_message, code
                )

                # decide retry based on strategy (map LDAP codes where needed)
                mapped_status = None
                if code == LdapResultCode.INVALID_CREDENTIALS:
                    mapped_status = HTTPStatus.SERVICE_UNAVAILABLE
                decision = strategy(attempt, "GET", self.url, mapped_status, exc)
                if decision.decision == RetryDecisionEnum.RETRY and attempt < attempts:
                    if decision.delay_seconds:
                        import time

                        logger.bind(endpoint=base).info(
                            "Retrying LDAP search in {:.3f}s (attempt {}/{})",
                            decision.delay_seconds,
                            attempt + 1,
                            attempts,
                        )
                        time.sleep(decision.delay_seconds)
                    last_exc = LdapError(e=exc, msg=friendly_message, code=code, info=payload)
                    continue

                raise LdapError(e=exc, msg=friendly_message, code=code, info=payload) from exc

            except Exception as exc:
                # Clean up per-operation connection on error
                if self._persistent_conn is None:
                    try:
                        conn_context.__exit__(type(exc), exc, exc.__traceback__)
                    except Exception:
                        pass

                # network/protocol errors → treat like exceptions for retry
                decision = strategy(attempt, "LDAP", self.url, None, exc)
                if decision.decision == RetryDecisionEnum.RETRY and attempt < attempts:
                    if decision.delay_seconds:
                        import time

                        logger.bind(endpoint=base).info(
                            "Retrying LDAP search in {:.3f}s (attempt {}/{})",
                            decision.delay_seconds,
                            attempt + 1,
                            attempts,
                        )
                        time.sleep(decision.delay_seconds)
                    last_exc = exc
                    continue
                raise

        if last_exc:
            raise last_exc
        return []

    def users(
        self,
        user: str | None = None,
        uid: str | None = None,
        attributes: list[str] | str | None = None,
        filter_: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for user accounts and return as list.

        Args:
            user: Username to search for
            uid: User ID to search for
            attributes: Attributes to return
            filter_: Custom LDAP filter
            username: Bind username
            password: Bind password

        Returns:
            List of user entries
        """
        if filter_ is None:
            filter_ = self.filter(uid=user, uidNumber=uid)

        results = []
        for entry in self.search(
            base=self.base(cn=["users", "system"]),
            filter_=filter_,
            attributes=attributes,
            username=username,
            password=password,
        ):
            # Process membership information
            if "uioMemberOf" in entry:
                memberships = entry.pop("uioMemberOf", [])
                netgroups = []
                filegroups = []
                for dn in memberships:
                    group = dn.split(",", maxsplit=1)[0].split("=")[1]
                    if ",cn=netgroups," in dn:
                        netgroups.append(group)
                    elif ",cn=filegroups," in dn:
                        filegroups.append(group)
                entry["netgroups"] = sorted(netgroups)
                entry["filegroups"] = sorted(filegroups)
            results.append(entry)

        return results

    def people(
        self,
        name: str | None = None,
        surname: str | None = None,
        given_name: str | None = None,
        mail: str | None = None,
        phone: str | None = None,
        object_class: str | None = None,
        affiliation: str | None = None,
        uid: str | None = None,
        filter_: str | None = None,
        attributes: list[str] | str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for people (students/employees) and return as list.

        Args:
            name: Common name to search for
            surname: Family name
            given_name: First name
            mail: Email address
            phone: Telephone number
            object_class: LDAP object class
            affiliation: Educational affiliation
            uid: User ID
            filter_: Custom LDAP filter
            attributes: Attributes to return
            username: Bind username
            password: Bind password

        Returns:
            List of people entries
        """
        if isinstance(attributes, str):
            attributes = [a.strip() for a in attributes.split(",") if a.strip()]

        seen_dns = set()

        def _search(_name: str | None, _uid: str | None) -> list[dict[str, Any]]:
            indexed = {
                "cn": _name,
                "sn": surname,
                "givenName": given_name,
                "mail": mail,
                "uid": _uid,
                "objectClass": object_class,
                "telephoneNumber": phone,
                "eduPersonAffiliation": affiliation,
            }
            flt = filter_ or self.filter(sep="&", **indexed)

            results = []
            for person in self.search(
                base=self.base(cn=["people"]),
                filter_=flt,
                attributes=attributes,
                username=username,
                password=password,
            ):
                dn = person.get("dn") or person.get("cn", [""])[0]
                if dn and dn not in seen_dns:
                    seen_dns.add(dn)
                    results.append(person)
            return results

        # Primary search
        results = []
        if name or uid:
            results.extend(_search(name, uid))

        # Fallback: if no results and searching by uid, try searching by cn
        if not results and uid and not name:
            cn_list: list[str] = []
            for user_entry in self.users(
                user=uid, attributes=["cn"], username=username, password=password
            ):
                cn_list.extend(c for c in user_entry.get("cn", []) if c not in cn_list)

            for cn_value in cn_list:
                results.extend(_search(cn_value, None))

        return results

    def hosts(
        self,
        host: str | None = None,
        contact: str | None = None,
        comment: str | None = None,
        mac: str | None = None,
        filter_: str | None = None,
        attributes: list[str] | str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for host entries and return as list.

        Args:
            host: Hostname pattern
            contact: Host contact person
            comment: Host comment
            mac: MAC address
            filter_: Custom LDAP filter
            attributes: Attributes to return
            username: Bind username
            password: Bind password

        Returns:
            List of host entries
        """
        indexed = {
            "host": host,
            "uioHostContact": contact,
            "uioHostComment": comment,
            "uioHostMacAddr": mac,
        }

        return self.search(
            base=self.base(cn=["hosts", "system"]),
            filter_=self.filter(sep="&", **indexed) if filter_ is None else filter_,
            attributes=attributes,
            username=username,
            password=password,
        )

    def organization(
        self,
        organization: str | None = None,
        mail: str | None = None,
        phone: str | None = None,
        org_number: str | None = None,
        *,
        attributes: list[str] | str | None = None,
        filter_: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for organizational units and return as list.

        Args:
            organization: Organization name (ou)
            mail: Email address
            phone: Telephone number
            org_number: Organization number
            attributes: Attributes to return
            filter_: Custom LDAP filter
            username: Bind username
            password: Bind password

        Returns:
            List of organization entries
        """
        indexed = {
            "ou": organization,
            "mail": mail,
            "telephoneNumber": phone,
            "norEduOrgUnitUniqueNumber": org_number,
        }
        return self.search(
            base=self.base(cn=["organization"]),
            filter_=self.filter(sep="&", **indexed) if filter_ is None else filter_,
            attributes=attributes,
            username=username,
            password=password,
        )

    def netgroups(
        self,
        cn: str | None = None,
        object_class: str | list[str] | None = None,
        *,
        attributes: list[str] | str | None = None,
        filter_: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for NIS netgroups and return as list.

        Args:
            cn: Common name of netgroup
            object_class: LDAP object class filter
            attributes: Attributes to return
            filter_: Custom LDAP filter
            username: Bind username
            password: Bind password

        Returns:
            List of netgroup entries with processed member information
        """
        indexed = {"cn": cn, "objectClass": object_class}

        results = []
        for entry in self.search(
            base=self.base(cn=["netgroups", "system"]),
            filter_=self.filter(sep="&", **indexed) if filter_ is None else filter_,
            attributes=attributes,
            username=username,
            password=password,
        ):
            # Process NIS netgroup triples
            if "nisNetgroupTriple" in entry:
                triples = entry.pop("nisNetgroupTriple", [])
                members = []
                for triplet in triples:
                    if isinstance(triplet, (list, tuple)) and len(triplet) >= 1:
                        hostname = triplet[0]
                        if hostname and hostname != "-":
                            members.append(hostname)
                entry["members"] = members
            results.append(entry)

        return results

    def filegroups(
        self,
        cn: str | None = None,
        gid: int | None = None,
        uid: str | None = None,
        object_class: str | list[str] | None = None,
        *,
        attributes: list[str] | str | None = None,
        filter_: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for POSIX file groups and return as list.

        Args:
            cn: Common name of filegroup
            gid: Group ID number
            uid: Member user ID
            object_class: LDAP object class filter
            attributes: Attributes to return
            filter_: Custom LDAP filter
            username: Bind username
            password: Bind password

        Returns:
            List of filegroup entries with normalized member lists
        """
        indexed = {
            "cn": cn,
            "gidNumber": gid,
            "memberUid": uid,
            "objectClass": object_class,
        }

        results = []
        for entry in self.search(
            base=self.base(cn=["filegroups", "system"]),
            filter_=self.filter(sep="&", **indexed) if filter_ is None else filter_,
            attributes=attributes,
            username=username,
            password=password,
        ):
            # Normalize memberUid to sorted unique list
            if "memberUid" in entry and isinstance(entry["memberUid"], list):
                entry["memberUid"] = sorted(set(entry["memberUid"]))
            results.append(entry)

        return results

    def automount(
        self,
        cn: str | None = None,
        ou: str | list[str] = "auto.master",
        information: str | None = None,
        *,
        attributes: list[str] | str | None = None,
        filter_: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for automount entries and return as list.

        Args:
            cn: Common name
            ou: Organizational unit path (default: "auto.master")
            information: Automount information string
            attributes: Attributes to return
            filter_: Custom LDAP filter
            username: Bind username
            password: Bind password

        Returns:
            List of automount entries with resolved symlinks
        """
        if isinstance(ou, str):
            ou = ou.split(",")

        indexed = {"cn": cn, "automountInformation": information}
        base = self.base(ou=ou, cn=["automount", "system"])

        results = []
        for entry in self.search(
            base=base,
            filter_=self.filter(sep="&", **indexed) if filter_ is None else filter_,
            attributes=attributes,
            username=username,
            password=password,
        ):
            # Follow ldap: symlinks one level
            info = entry.get("automountInformation", "")
            if isinstance(info, str) and info.startswith("ldap:"):
                link_dn = info.split("ldap:", 1)[1]
                link_ou = [
                    seg.split("=", 1)[1]
                    for seg in link_dn.split(",")
                    if seg.lower().startswith("ou=")
                ]
                if link_ou:
                    # Get the linked entries
                    linked_entries = self.search(
                        base=self.base(ou=link_ou, cn=["automount", "system"]),
                        filter_="(cn=/)",
                        attributes=attributes,
                        username=username,
                        password=password,
                    )
                    if linked_entries:
                        entry["/"] = linked_entries[0]
            results.append(entry)

        return results

    def base(self, **bases: Any) -> str:
        """Construct an LDAP base DN from components.

        Args:
            **bases: Keyword arguments for DN components (cn, ou, dc, uid, etc.)

        Returns:
            A properly formatted LDAP distinguished name

        Examples:
            >>> ldap = LdapSource("ldap://ldap.uio.no")
            >>> ldap.base(cn="organization")
            'cn=organization,dc=uio,dc=no'

            >>> ldap.base(cn=["hosts", "system"])
            'cn=hosts,cn=system,dc=uio,dc=no'
        """
        parts: list[str] = []
        dc_vals = bases.get("dc", self.domain_controllers)
        dc_list = [dc_vals] if isinstance(dc_vals, str) else list(dc_vals)
        for root, values in bases.items():
            if root == "dc":
                continue
            vals = [values] if isinstance(values, str) else list(values)
            for value in vals:
                parts.append(f"{root}={value}")
        for dc in dc_list:
            parts.append(f"dc={dc}")
        return ",".join(parts)

    def filter(
        self,
        *filters: str,
        sep: Literal["&", "|"] = "&",
        **kwargs: Any,
    ) -> str:
        """Construct an LDAP filter string from components.

        Args:
            *filters: Pre-constructed filter strings to include
            sep: Separator for combining filters ('&' for AND, '|' for OR)
            **kwargs: Attribute-value pairs to convert to filter components

        Returns:
            A properly formatted LDAP filter string

        Examples:
            >>> ldap = LdapSource("ldap://ldap.uio.no")
            >>> ldap.filter(objectClass='user')
            '(objectClass=user)'

            >>> ldap.filter(objectClass=['person', 'user'])
            '(&(objectClass=person)(objectClass=user))'
        """
        result = list(filters)
        for root, leaf in kwargs.items():
            if leaf is None:
                continue
            if isinstance(leaf, str):
                result.append(f"({root}={leaf})")
            elif isinstance(leaf, list):
                result.extend(f"({root}={node})" for node in leaf)
        if len(result) < 1:
            return ""
        joined = "".join(result)
        return joined if len(result) == 1 else f"({sep}{joined})"


class LdapError(Exception):
    """LDAP operation error with detailed context.

    This exception provides comprehensive error information for LDAP operations,
    including diagnostic commands and error context.
    """

    def __init__(
        self,
        e: Exception,
        msg: str,
        code: int | None = None,
        info: dict[str, Any] | None = None,
    ):
        """Initialize LDAP error.

        Args:
            e: The original exception that caused this error
            msg: User-friendly error message
            code: LDAP result code
            info: Additional diagnostic information
        """
        super().__init__(msg)
        self.original_exception = e
        self.code = code
        self.info = info or {}
