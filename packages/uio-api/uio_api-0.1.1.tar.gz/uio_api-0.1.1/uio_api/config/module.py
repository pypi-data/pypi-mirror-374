"""Module-specific configuration settings.

This module provides ModuleSettings that extends BaseSettings with
module-specific configuration fields like URL, scheme, and pagination settings.
"""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .base import BaseSettings


@dataclass(frozen=True, slots=True)
class ModuleSettings:
    """Module-specific configuration settings.

    This class extends BaseSettings with module-specific fields like
    URL, authentication scheme, and pagination settings. Each API module
    can have its own ModuleSettings instance with appropriate defaults.

    Attributes:
        base: Base framework settings.
        module_name: Name of the API module (e.g., "mreg", "example").
        url: API base URL.
        scheme: Authentication scheme (e.g., "Token", "Bearer").
        page_size: Default page size for paginated requests.
        login_path: Path for token authentication.
        logout_path: Path for token logout/revocation.
        token: Static token (if provided).
        token_file: Path to token file (if provided).
        system_user: System account username (password stored in secrets).
    """

    base: BaseSettings
    module_name: str
    url: str | None
    scheme: str
    page_size: int | None
    login_path: str | None
    logout_path: str | None
    token: str | None
    token_file: Path | None
    system_user: str | None
    # LDAP-specific knobs (optional, per-module)
    domain_controllers: list[str] | None = None
    allow_anonymous: bool | None = None

    # --------- uppercase conveniences (delegate to base) ---------

    @property
    def USER_NAME(self) -> str | None:
        """Get the default username."""
        return self.base.USER_NAME

    @property
    def INTERACTIVE(self) -> bool:
        """Get the interactive authentication setting."""
        return self.base.INTERACTIVE

    @property
    def SECRETS_BACKEND(self) -> str:
        """Get the secrets backend setting."""
        return self.base.SECRETS_BACKEND

    @property
    def CONFIG_DIR(self) -> Path:
        """Get the configuration directory path."""
        return self.base.CONFIG_DIR

    @property
    def SECRETS_FILE(self) -> Path:
        """Get the secrets file path."""
        return self.base.SECRETS_FILE

    @property
    def KEYRING_INDEX_FILE(self) -> Path:
        """Get the keyring index file path."""
        return self.base.KEYRING_INDEX_FILE

    @property
    def TIMEOUT(self) -> float:
        """Get the request timeout."""
        return self.base.TIMEOUT

    @property
    def REFRESH_ON_401(self) -> bool:
        """Get the refresh on 401 setting."""
        return self.base.REFRESH_ON_401

    @property
    def RETRY_ATTEMPTS(self) -> int:
        """Get the number of retry attempts."""
        return self.base.RETRY_ATTEMPTS

    @property
    def ALLOW_NON_IDEMPOTENT_RETRIES(self) -> bool:
        """Get the allow non-idempotent retries setting."""
        return self.base.ALLOW_NON_IDEMPOTENT_RETRIES

    # --------- module-specific properties ---------

    @property
    def URL(self) -> str | None:
        """Get the API base URL."""
        return self.url

    @property
    def SCHEME(self) -> str:
        """Get the authentication scheme."""
        return self.scheme

    @property
    def PAGE_SIZE(self) -> int | None:
        """Get the default page size."""
        return self.page_size

    @property
    def TOKEN(self) -> str | None:
        """Get the static token."""
        return self.token

    @property
    def TOKEN_FILE(self) -> Path | None:
        """Get the token file path."""
        return self.token_file

    @property
    def SYSTEM_USER(self) -> str | None:
        """Get the system user."""
        return self.system_user

    @property
    def LOGGING_FILE_PATH(self) -> Path | None:
        """Get the logging file path."""
        return self.base.LOGGING_FILE_PATH

    # --------- override API ---------

    def with_overrides(self, **kwargs: Any) -> "ModuleSettings":
        """Create a copy with selected fields changed."""
        # Handle base settings overrides
        base_kwargs = {}
        module_kwargs = {}

        base_fields = {
            "username",
            "interactive",
            "secrets_backend",
            "config_dir",
            "secrets_file",
            "keyring_index_file",
            "timeout",
            "refresh_on_401",
            "retry_attempts",
            "allow_non_idempotent_retries",
            "logging_file_path",
        }

        for key, value in kwargs.items():
            if key in base_fields:
                base_kwargs[key] = value
            else:
                module_kwargs[key] = value

        # Create new base settings if needed
        if base_kwargs:
            new_base = self.base.with_overrides(**base_kwargs)
            module_kwargs["base"] = new_base

        return replace(self, **module_kwargs)
