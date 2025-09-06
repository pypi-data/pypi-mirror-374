"""Token provider implementations for different authentication strategies.

This module provides token providers that handle different ways of obtaining
and managing authentication tokens, including static tokens, file-based tokens,
and interactive authentication with token issuance.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from ...logging import logger
from ..tokens.loader_abstract import AbstractTokenLoader
from ..tokens.scope import TokenScope


class SyncTokenProvider(Protocol):
    """Protocol for synchronous token providers.

    Token providers must implement this interface to work with the
    RefreshingTokenAuth authentication handler.
    """

    def get_token(self) -> str | None: ...
    def refresh(self) -> str: ...


@dataclass(slots=True)
class StaticProvider(SyncTokenProvider):
    """Token provider for static/pre-configured tokens.

    This provider simply returns a static token without any refresh capability.
    It's useful when you already have a valid token and don't need dynamic
    token management.

    Attributes:
        token: The static token string.
    """

    token: str | None = None

    def get_token(self) -> str | None:
        """Get the static token.

        Returns:
            The static token string, or None if not set.
        """
        return self.token

    def refresh(self) -> str:
        """Refresh the token (not supported for static tokens).

        Raises:
            RuntimeError: Always raised since static tokens cannot be refreshed.
        """
        raise RuntimeError("StaticProvider cannot refresh.")


IssueToken = Callable[[str, str | None, str], str]
PromptUsername = Callable[[], str]
PromptPassword = Callable[[str], str]


@dataclass(slots=True)
class InteractiveProvider(SyncTokenProvider):
    """Token provider for interactive authentication.

    This provider handles interactive authentication by:
    1. First trying to load an existing token from storage
    2. If no token exists or it's invalid, prompting for credentials
    3. Issuing a new token via the provided issuer function
    4. Optionally persisting the token to storage

    Attributes:
        store: Token loader for reading/writing tokens.
        scope: Token scope (username, URL) for this provider.
        issue: Function to issue new tokens.
        prompt_username: Function to prompt for username.
        prompt_password: Function to prompt for password.
        persist: Whether to persist tokens to storage.
        _cached: Cached token to avoid repeated storage lookups.
    """

    store: AbstractTokenLoader  # <- now typed against the abstract loader
    scope: TokenScope
    issue: IssueToken
    prompt_username: PromptUsername | None
    prompt_password: PromptPassword | None
    persist: bool = True

    _cached: str | None = None

    def get_token(self) -> str | None:
        """Get the current token.

        First checks the cache, then tries to load from storage.
        Uses the loader's resolve method which checks user-specific scope
        first, then falls back to default scope.

        Returns:
            The current token string, or None if not available.
        """
        if self._cached:
            return self._cached
        # loader.resolve() checks user scope first, then [default]
        self._cached = self.store.resolve(self.scope)
        return self._cached

    def refresh(self) -> str:
        """Refresh the token by prompting for credentials and issuing a new token.

        Prompts for username and password, then calls the issuer function
        to get a new token. Optionally persists the token to storage.

        Returns:
            The new authentication token.

        Raises:
            RuntimeError: If token issuance fails.
        """
        logger.debug(f"Refreshing token for {self.scope.url}")
        uid = self.scope.username or (
            self.prompt_username() if self.prompt_username is not None else ""
        )
        # Generic, consistent prompt format for all modules
        from ..tokens.scope import normalize_service_url

        base = normalize_service_url(self.scope.url)
        import getpass

        print(f"Connecting to {base}")
        if self.prompt_password is not None:
            pwd = self.prompt_password(uid)
        else:
            pwd = getpass.getpass(f"Password for {uid}: ")
        token = self.issue(uid, pwd, self.scope.url)
        if self.persist:
            logger.debug(f"Persisting token for {self.scope.url}")
            self.store.write(self.scope, token)
        self._cached = token
        return token


@dataclass(slots=True)
class FileProvider(SyncTokenProvider):
    """Token provider for file-based tokens.

    This provider reads tokens from a file and monitors the file for changes.
    It's useful for CI/CD environments or when tokens are managed externally.

    Attributes:
        path: Path to the token file.
        encoding: File encoding (default "utf-8").
        strip: Whether to strip whitespace from the token (default True).
        _cached: Cached token to avoid repeated file reads.
        _mtime: Last modification time of the token file.
    """

    path: str
    encoding: str = "utf-8"
    strip: bool = True

    _cached: str | None = None
    _mtime: float | None = None

    def _snap(self) -> None:
        """Take a snapshot of the token file if it has changed.

        Checks the file's modification time and reloads the token if the file
        has been modified since the last read.
        """
        from pathlib import Path

        p = Path(self.path)
        try:
            mtime = p.stat().st_mtime
        except FileNotFoundError:
            self._cached = None
            self._mtime = None
            return
        if mtime != self._mtime:
            text = p.read_text(encoding=self.encoding)
            self._cached = text.strip() if self.strip else text
            self._mtime = mtime

    def get_token(self) -> str | None:
        """Get the current token from the file.

        Returns:
            The token string from the file, or None if the file doesn't exist.
        """
        self._snap()
        return self._cached

    def refresh(self) -> str:
        """Refresh the token by re-reading the file.

        Returns:
            The token string from the file.

        Raises:
            RuntimeError: If the token file is missing or empty.
        """
        self._snap()
        if not self._cached:
            raise RuntimeError(f"Token file missing or empty: {self.path}")
        return self._cached


@dataclass(slots=True)
class SystemAccountProvider(SyncTokenProvider):
    """Token provider for system accounts using the secrets system.

    This provider reads username from a config file and password from the
    secrets system (TOML/keyring). It's useful for system accounts where
    credentials are managed externally (e.g., by configuration management).

    The username file should contain just the username on the first line.
    The password is stored in the secrets system using the module-aware scope.

    Attributes:
        username_file: Path to the username file.
        store: Token loader for reading passwords from secrets.
        scope: Token scope for password lookup.
        issue: Function to issue new tokens using username/password.
        encoding: File encoding (default "utf-8").
        strip: Whether to strip whitespace from username (default True).
        _cached: Cached token to avoid repeated authentication.
        _username: Cached username to avoid repeated file reads.
        _mtime: Last modification time of the username file.
    """

    username_file: str
    store: AbstractTokenLoader
    scope: TokenScope
    issue: IssueToken
    encoding: str = "utf-8"
    strip: bool = True

    _cached: str | None = None
    _username: str | None = None
    _mtime: float | None = None

    def set_username(self, username: str) -> None:
        """Override the username directly instead of reading from file.

        This allows setting the username programmatically without requiring
        a username file, which is useful for system accounts where the
        username is known in advance.

        Args:
            username: The username to use for authentication.
        """
        self._username = username
        # Clear cache to force re-authentication with new username
        self._cached = None

    def clear_cache(self) -> None:
        """Clear the cached token to force re-authentication.

        This is useful when credentials have changed or when you want to
        ensure a fresh token is obtained on the next request.
        """
        self._cached = None

    def _load_username(self) -> str:
        """Load username from the username file.

        Returns:
            The username string.

        Raises:
            RuntimeError: If the username file is missing or malformed.
        """

        p = Path(self.username_file)
        try:
            mtime = p.stat().st_mtime
        except FileNotFoundError:
            raise RuntimeError(f"Username file not found: {self.username_file}")

        # Reload if file has changed
        if mtime != self._mtime:
            try:
                text = p.read_text(encoding=self.encoding)
                username = (
                    text.strip().split("\n")[0].strip() if self.strip else text.split("\n")[0]
                )

                if not username:
                    raise RuntimeError(f"Username cannot be empty in: {self.username_file}")

                self._username = username
                self._mtime = mtime
            except Exception as e:
                raise RuntimeError(f"Failed to read username file {self.username_file}: {e}")
        if self._username is None:
            raise ValueError("Missing username")

        return self._username

    def get_token(self) -> str | None:
        """Get the current token.

        Returns:
            The cached token, or None if no token has been obtained yet.
        """
        return self._cached

    def refresh(self) -> str:
        """Refresh the token by authenticating with stored credentials.

        Loads username from the username file and password from the secrets
        system, then uses the issuer function to obtain a new token.

        Returns:
            The new authentication token.

        Raises:
            RuntimeError: If credentials cannot be loaded or token issuance fails.
        """
        username = self._load_username()

        # Get password from secrets system
        password = self.store.read(self.scope)
        if not password:
            raise RuntimeError(f"No password found in secrets for scope: {self.scope}")

        token = self.issue(username, password, self.scope.url)
        self._cached = token
        return token
