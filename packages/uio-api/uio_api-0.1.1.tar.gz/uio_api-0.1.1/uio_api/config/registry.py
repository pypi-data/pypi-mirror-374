"""Configuration registry for loading module-specific settings.

This module provides the ConfigRegistry that implements the configuration
precedence hierarchy and caches results per (module, username).
"""

import os
from pathlib import Path

import tomllib  # built-in since Python 3.11

from .base import BaseSettings, base_settings
from .module import ModuleSettings


class ConfigRegistry:
    """Configuration registry for loading module-specific settings.

    This registry implements the configuration precedence hierarchy:
    1. Per-client overrides (arguments passed to factory)
    2. Env (module-scoped): e.g. MREG_URL, MREG_TOKEN
    3. Env (generic): e.g. UIO_API_URL, UIO_API_TOKEN
    4. Config file (module-scoped): [module.mreg] and [module.mreg.user."bob"]
    5. Config file (generic): [default] and [user."bob"]
    6. Built-in defaults

    Results are cached per (module, username) for performance.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], ModuleSettings] = {}

    def load_settings(self, module: str) -> ModuleSettings:
        """Load settings for a specific module.

        Args:
            module: Module name (e.g., "mreg", "example").

        Returns:
            ModuleSettings instance with all configuration resolved.

        Example:
            registry = ConfigRegistry()
            mreg_settings = registry.load_settings("mreg")
        """
        # Get current username for caching
        username = base_settings.USER_NAME or "default"
        cache_key = (module, username)

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load and cache
        settings = self._load_module_settings(module)
        self._cache[cache_key] = settings
        return settings

    def reload(self, module: str | None = None) -> None:
        """Reload configuration and clear cache.

        Args:
            module: Specific module to reload, or None to reload all.

        Example:
            registry.reload("mreg")  # Reload just MREG settings
            registry.reload()        # Reload all settings
        """
        if module is None:
            self._cache.clear()
        else:
            # Clear all cache entries for this module
            keys_to_remove = [key for key in self._cache.keys() if key[0] == module]
            for key in keys_to_remove:
                del self._cache[key]

    def _load_module_settings(self, module: str) -> ModuleSettings:
        """Load module settings following the precedence hierarchy."""
        # Start with base settings
        base = base_settings

        # Read configuration file
        config_data = self._read_config_file(base.CONFIG_DIR)

        # Apply precedence hierarchy
        settings = self._apply_precedence(module, config_data, base)

        return settings

    def _read_config_file(self, cfg_dir: Path) -> dict[str, object]:
        """Read configuration from TOML file."""
        path = cfg_dir / "config.toml"
        if not path.exists():
            return {}
        with path.open("rb") as f:
            try:
                return tomllib.load(f) or {}
            except Exception:
                return {}

    def _apply_precedence(
        self, module: str, config_data: dict[str, object], base: BaseSettings
    ) -> ModuleSettings:
        """
        Resolve settings for a module by applying the precedence hierarchy.

        Precedence (lowest → highest):
          1) Built-in defaults
          2) Config file (generic): [default], [user.<username>]
          3) Config file (module-scoped): [module.<module>], [module.<module>.user.<username>]
          4) Environment (generic): UIO_API_*
          5) Environment (module-scoped): <MODULE>_*

        Later sources override earlier ones. The merged mapping is converted into a
        `ModuleSettings` instance with careful type-narrowing for each field.
        """
        username = base.USER_NAME or "default"

        # 1. Built-in defaults
        defaults = self._get_module_defaults(module)

        # 2. Config file (generic): [default], [user.<username>]
        file_generic = self._merge_file_sections(config_data, ["default", f"user.{username}"])

        # 3. Config file (module-scoped)
        file_module = self._merge_file_sections(
            config_data, [f"module.{module}", f"module.{module}.user.{username}"]
        )

        # 4. Environment (generic)
        env_generic = self._get_env_generic()

        # 5. Environment (module-scoped)
        env_module = self._get_env_module(module)

        # Merge in precedence order (later updates override earlier ones)
        merged: dict[str, object] = {}
        merged.update(defaults)
        merged.update(file_generic)
        merged.update(file_module)
        merged.update(env_generic)
        merged.update(env_module)

        # Local vars for type narrowing (so static checkers don't see plain `object`)
        url_v = merged.get("url")
        scheme_v = merged.get("scheme", "Token")
        ps_v = merged.get("page_size")
        lp_v = merged.get("login_path")
        lop_v = merged.get("logout_path")
        tok_v = merged.get("token")
        tf_v = merged.get("token_file")
        su_v = merged.get("system_user")
        dc_v = merged.get("domain_controllers")
        anon_v = merged.get("allow_anonymous")

        return ModuleSettings(
            base=base,
            module_name=module,
            url=str(url_v) if url_v is not None else None,
            scheme=str(scheme_v),
            page_size=int(ps_v) if isinstance(ps_v, (int, str)) else None,
            login_path=str(lp_v) if lp_v is not None else None,
            logout_path=str(lop_v) if lop_v is not None else None,
            token=str(tok_v) if tok_v is not None else None,
            token_file=Path(str(tf_v)) if tf_v is not None else None,
            system_user=str(su_v) if su_v is not None else None,
            domain_controllers=[str(x) for x in dc_v] if isinstance(dc_v, list) else None,
            allow_anonymous=(bool(anon_v) if anon_v is not None else None),
        )

    def _get_module_defaults(self, module: str) -> dict[str, object]:
        """Get built-in defaults for a module."""
        # Module-specific defaults
        defaults: dict[str, dict[str, object]] = {
            "mreg": {
                "url": "https://mreg.uio.no",
                "scheme": "Token",
                "page_size": 1000,
                "login_path": "/api/token-auth/",
                "logout_path": "/api/token-logout/",
            },
            "example": {
                "url": "https://api.example.com",
                "scheme": "Bearer",
                "page_size": None,
                "login_path": "/oauth/token",
                "logout_path": None,
            },
            "ldap": {
                "url": "ldap://ldap.uio.no",
                "scheme": None,  # LDAP doesn't use HTTP auth schemes
                "page_size": None,  # LDAP doesn't use pagination like REST APIs
                "login_path": None,
                "logout_path": None,
            },
        }
        v = defaults.get(module)
        return v if v is not None else {}

    def _merge_file_sections(
        self, config_data: dict[str, object], sections: list[str]
    ) -> dict[str, object]:
        """Merge configuration file sections."""
        merged: dict[str, object] = {}
        for section in sections:
            if section in config_data:
                section_data = config_data[section]
                if isinstance(section_data, dict):
                    merged.update(section_data)
        return merged

    def _get_env_generic(self) -> dict[str, object]:
        """Get generic environment variables (UIO_API_*)."""
        from ..constants import APPNAME

        env: dict[str, object] = {}
        prefix = f"{APPNAME}_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()  # Remove UIO_API_ prefix
                if config_key in [
                    "url",
                    "scheme",
                    "page_size",
                    "login_path",
                    "logout_path",
                    "token",
                    "token_file",
                    "system_user",
                    "domain_controllers",
                    "allow_anonymous",
                ]:
                    env[config_key] = value
        return env

    def _get_env_module(self, module: str) -> dict[str, object]:
        """Get module-scoped environment variables (<MODULE>_*)."""
        env: dict[str, object] = {}
        module_prefix = f"{module.upper()}_"
        for key, value in os.environ.items():
            if key.startswith(module_prefix):
                config_key = key[len(module_prefix) :].lower()  # Remove <MODULE>_ prefix
                if config_key in [
                    "url",
                    "scheme",
                    "page_size",
                    "login_path",
                    "logout_path",
                    "token",
                    "token_file",
                    "system_user",
                    "domain_controllers",
                    "allow_anonymous",
                ]:
                    env[config_key] = value
        return env


# Global registry instance
registry = ConfigRegistry()


def load_settings(module: str) -> ModuleSettings:
    """Load settings for a specific module.

    This is the main entry point for loading module-specific configuration.

    Args:
        module: Module name (e.g., "mreg", "example").

    Returns:
        ModuleSettings instance with all configuration resolved.

    Example:
        from . import load_settings

        mreg_settings = load_settings("mreg")
        example_settings = load_settings("example")
    """
    return registry.load_settings(module)


def reload_settings(module: str | None = None) -> None:
    """Reload configuration and clear cache.

    Args:
        module: Specific module to reload, or None to reload all.

    Example:
        from . import reload_settings

        reload_settings("mreg")  # Reload just MREG settings
        reload_settings()        # Reload all settings
    """
    registry.reload(module)
