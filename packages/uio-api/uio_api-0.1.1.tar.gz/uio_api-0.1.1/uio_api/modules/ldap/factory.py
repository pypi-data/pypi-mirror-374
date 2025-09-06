"""LDAP client factory with configuration support.

This module provides a factory function for creating LDAP clients
with proper configuration support and system user management.
"""

from typing import Any, Callable

from ...core.factory_utils import apply_config_overrides, get_config_value
from ...config import load_settings
from ...core.tokens.scope import TokenScope, normalize_service_url
from ...core.tokens.loader_abstract import AbstractTokenLoader
from .client import LdapClient


def client(
    *,
    settings: dict[str, Any] | None = None,
    # LDAP-specific configuration
    url: str | None = None,
    domain_controllers: list[str] | None = None,
    allow_anonymous: bool | None = None,
    # Auth knobs (no tokens for LDAP)
    username: str | None = None,
    system_user: str | None = None,
    interactive: bool | None = None,
    prompt_username: Callable[[], str] | None = None,
    prompt_password: Callable[[str], str] | None = None,
    # Retry-like knob (kept for parity; used by client for prompting)
    retry_attempts: int | None = None,
    **kwargs: Any,
) -> LdapClient:
    """Create a configured LDAP client.

    This factory function creates LdapClient instances with proper configuration
    and authentication support. Mirrors other modules: supports system_user,
    interactive prompts, and backend selection for credential storage.

    Args:
        settings: Optional settings dict to override defaults
        url: LDAP server URL (default: "ldap://ldap.uio.no")
        domain_controllers: Domain components for base DN (default: ["uio", "no"])
        allow_anonymous: Whether anonymous binding is allowed (default: True)
        username: Bind username (short name or DN)
        system_user: Name of stored system account to use (password loaded from storage)
        interactive: Prompt for credentials if needed
        prompt_username: Custom function to obtain username
        prompt_password: Custom function to obtain password (receives username)
        secrets_backend: "toml" or "keyring" to choose credential storage
        **kwargs: Additional arguments (currently unused)

    Returns:
        A configured LdapClient instance ready for use.

    Example:
        # Anonymous access (default)
        client = ldap_client()

        # Authenticated access with prompt
        client = ldap_client(username="myuser", interactive=True)

        # Basic usage
        users = client.users(user="radius")
        people = client.people(name="Oistein")
        hosts = client.hosts(host="*.uio.no")
    """
    # Load module settings (registry) and apply overrides
    mod = load_settings("ldap")
    base_config = {
        "url": mod.URL or "ldap://ldap.uio.no",
        "domain_controllers": mod.domain_controllers or ["uio", "no"],
        "allow_anonymous": True if mod.allow_anonymous is None else mod.allow_anonymous,
    }
    if settings:
        base_config = apply_config_overrides(base_config, settings)

    overrides: dict[str, Any] = {}
    if url is not None:
        overrides["url"] = url
    if domain_controllers is not None:
        overrides["domain_controllers"] = domain_controllers
    if allow_anonymous is not None:
        overrides["allow_anonymous"] = allow_anonymous
    final_config = apply_config_overrides(base_config, overrides)

    final_url = str(get_config_value(final_config, "url"))
    final_domain_controllers = list(get_config_value(final_config, "domain_controllers"))
    final_allow_anonymous = bool(get_config_value(final_config, "allow_anonymous"))
    # Create client (set credentials below)
    client = LdapClient(
        url=final_url,
        domain_controllers=final_domain_controllers,
        allow_anonymous=final_allow_anonymous,
    )
    client._retry_attempts = retry_attempts or getattr(mod, "RETRY_ATTEMPTS", None) or 1
    client._interactive = bool(interactive)
    client._prompt_username = prompt_username
    client._prompt_password = prompt_password

    # Resolve credentials precedence:
    # 1) system_user → load from storage
    # 2) interactive with username/prompt
    # 3) default anonymous

    def _load_system_user_password(u: str) -> str:
        """Load only stored system-user password from configured backend."""
        backend = getattr(mod, "SECRETS_BACKEND", None)
        backend_name = (getattr(backend, "name", backend) or "toml").lower()
        scope_url = normalize_service_url(final_url)
        scope = TokenScope(module="ldap", url=scope_url, username=u)
        loader: AbstractTokenLoader
        if backend_name == "toml":
            from ...core.tokens.loader_toml import TomlTokenLoader

            loader = TomlTokenLoader(path=mod.SECRETS_FILE)
            pw = loader.read(scope)
            if pw is None:
                raise ValueError(f"No stored password for {u} in {mod.SECRETS_FILE}")
            return pw
        if backend_name == "keyring":
            from ...core.tokens.loader_keyring import KeyringTokenLoader

            loader = KeyringTokenLoader(index_path=mod.KEYRING_INDEX_FILE)
            pw = loader.read(scope)
            if pw is None:
                raise ValueError("No stored password for system user in keyring")
            return pw
        raise ValueError(f"Unsupported secrets backend: {backend_name}")

    if system_user:
        pw = _load_system_user_password(system_user)
        client.bind_user = system_user
        client.bind_password = pw
        return client

    if interactive:
        user_value = username
        if user_value is None:
            if prompt_username is None:

                def _default_user() -> str:
                    import getpass

                    return getpass.getuser()

                get_user = _default_user
            else:
                get_user = prompt_username
            user_value = get_user()

        # Defer password prompting to the client's context manager so that
        # retry_attempts count represents total prompts (not 1 + retries).
        client.bind_user = user_value
        client._interactive = True
        client._prompt_username = prompt_username
        client._prompt_password = prompt_password
        return client

    return client
