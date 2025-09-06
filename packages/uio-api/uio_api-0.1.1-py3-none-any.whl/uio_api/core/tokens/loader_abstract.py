"""Abstract token loader interface.

This module defines the abstract interface for token loaders that handle
reading, writing, and managing authentication tokens with support for
transactional operations and scope-based token management.
"""

import abc
from contextlib import contextmanager
from typing import Iterable, Iterator

from .scope import TokenScope


class AbstractTokenLoader(abc.ABC):
    """Abstract base class for token loaders.

    Token loaders provide a unified interface for storing and retrieving
    authentication tokens with support for:
    - Scope-based token management (username, URL)
    - Transactional operations (backup/restore)
    - CRUD operations (create, read, update, delete)
    - Optional scope enumeration

    Attributes:
        name: Human-readable name for this loader.

    Example:
        class MyTokenLoader(AbstractTokenLoader):
            def backup(self) -> None: ...
            def restore(self) -> None: ...
            def read(self, scope: TokenScope) -> str | None: ...
            def write(self, scope: TokenScope, token: str) -> None: ...
            def delete(self, scope: TokenScope) -> None: ...
    """

    def __init__(self, name: str) -> None:
        """Initialize the token loader.

        Args:
            name: Human-readable name for this loader.
        """
        self.name = name

    # ----- transactional API -----
    @abc.abstractmethod
    def backup(self) -> None:
        """Create a backup of the current state.

        This method should create a backup that can be restored later
        using the restore() method. The backup should be atomic and
        consistent.

        Example:
            loader.backup()  # Create backup before making changes
            try:
                loader.write(scope, new_token)
            except Exception:
                loader.restore()  # Restore on failure
        """
        ...

    @abc.abstractmethod
    def restore(self) -> None:
        """Restore from the most recent backup.

        This method should restore the state from the most recent backup
        created by backup(). It should be safe to call even if no backup
        exists.

        Example:
            loader.backup()  # Create backup
            loader.write(scope, new_token)
            loader.restore()  # Restore original state
        """
        ...

    # ----- transactional helper -----
    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Best-effort transactional wrapper around write/delete sequences.

        Usage:
            with loader.transaction():
                loader.write(scope, token)
                ...
        On exception, calls restore().
        """
        self.backup()
        try:
            yield
        except Exception:
            try:
                self.restore()
            finally:
                raise

    # ----- CRUD -----
    @abc.abstractmethod
    def read(self, scope: TokenScope) -> str | None:
        """Read a token for the given scope.

        Args:
            scope: Token scope (username, URL) to read.

        Returns:
            Token string if found, None otherwise.

        Example:
            scope = TokenScope(module="example", url="https://api.example.com", username="bob")
            token = loader.read(scope)
        """
        ...

    @abc.abstractmethod
    def write(self, scope: TokenScope, token: str) -> None:
        """Write a token for the given scope.

        Args:
            scope: Token scope (username, URL) to write.
            token: Token string to store.

        Example:
            scope = TokenScope(module="example", url="https://api.example.com", username="bob")
            loader.write(scope, "abc123...")
        """
        ...

    @abc.abstractmethod
    def delete(self, scope: TokenScope) -> None:
        """Delete a token for the given scope.

        Args:
            scope: Token scope (username, URL) to delete.

        Note:
            This method should not raise an error if the token doesn't exist.

        Example:
            scope = TokenScope(module="example", url="https://api.example.com", username="bob")
            loader.delete(scope)  # Safe to call even if token doesn't exist
        """
        ...

    # ----- enumeration (optional) -----
    def list_scopes(self) -> Iterable[TokenScope]:
        """List all known token scopes.

        This is an optional method that can be implemented to enumerate
        all known token scopes. The default implementation returns an
        empty iterable.

        Returns:
            Iterable of known token scopes.

        Example:
            for scope in loader.list_scopes():
                print(f"Token for {scope.username} at {scope.url}")
        """
        return ()  # default: not supported

    # ----- convenience: resolve with default fallback -----
    def resolve(self, scope: TokenScope) -> str | None:
        """Resolve token with default fallback.

        This method implements a common resolution policy:
        1. Try to read the exact scope (username, URL)
        2. If not found and username is not None, try default scope (None, URL)

        Args:
            scope: Token scope to resolve.

        Returns:
            Token string if found, None otherwise.

        Example:
            # Try user-specific token first, then default
            scope = TokenScope(module="example", url="https://api.example.com", username="bob")
            token = loader.resolve(scope)
        """
        tok = self.read(scope)
        if tok is not None or scope.username is None:
            return tok
        return self.read(TokenScope(module=scope.module, url=scope.url, username=None))
