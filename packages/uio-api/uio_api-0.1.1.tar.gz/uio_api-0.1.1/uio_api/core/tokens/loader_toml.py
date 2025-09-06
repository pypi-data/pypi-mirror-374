import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, ClassVar

try:
    import tomlkit
except Exception as e:
    raise ImportError("TOML loader requires `tomlkit`.") from e

from ..enums import FilePerm
from .loader_abstract import AbstractTokenLoader
from .scope import TokenScope, normalize_service_url


@dataclass(slots=True)
class TomlTokenLoader(AbstractTokenLoader):
    """
    Layout (human-friendly; comments preserved by tomlkit):

    [default.urls."https://api.example.com"]
    token = "abc..."
    updated = "2025-09-02T10:00:00Z"

    [user."bob-drift".urls."https://api.example.com"]
    token = "def..."
    updated = "2025-09-02T10:05:00Z"

    [module.mreg.user."bob-drift".urls."https://mreg.uio.no"]
    token = "mreg-token..."
    updated = "2025-09-02T10:10:00Z"

    [module.example.user."bob-drift".urls."https://api.example.com"]
    token = "example-token..."
    updated = "2025-09-02T10:15:00Z"
    """

    name: str
    path: Path
    perms: int = int(FilePerm.OWNER_RW)
    _bak: Path | None = None

    # Table name constants as class attributes
    _default_tbl: ClassVar[str] = "default"
    _user_tbl: ClassVar[str] = "user"
    _module_tbl: ClassVar[str] = "module"
    _urls_tbl: ClassVar[str] = "urls"
    _token_key: ClassVar[str] = "token"
    _updated_key: ClassVar[str] = "updated"

    def __init__(
        self, *, path: Path, perms: int = int(FilePerm.OWNER_RW), name: str = "toml"
    ) -> None:
        self.name = name
        self.path = path
        self.perms = perms
        # Note: dataclass with slots doesn't include dynamic attributes; keep within __init__ scope
        self._bak = self.path.with_suffix(self.path.suffix + ".bak")

    # ---------- transactional ----------

    def backup(self) -> None:
        if self.path.exists():
            dst = (
                self._bak
                if self._bak is not None
                else self.path.with_suffix(self.path.suffix + ".bak")
            )
            shutil.copy2(self.path, dst)

    def restore(self) -> None:
        if self._bak is not None and self._bak.exists():
            shutil.move(str(self._bak), str(self.path))

    # ---------- helpers ----------

    def _load(self) -> tomlkit.TOMLDocument:
        if self.path.exists():
            return tomlkit.parse(self.path.read_text(encoding="utf-8"))
        return tomlkit.document()

    def _save(self, doc: tomlkit.TOMLDocument) -> None:
        """Save the TOML document using atomic writes for safety.

        Args:
            doc: The TOML document to save.

        Raises:
            PermissionError: If unable to write to the secrets file.
            OSError: If file system errors occur during atomic write.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write: write to temp file then replace
            temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
            temp_path.write_text(tomlkit.dumps(doc), encoding="utf-8")

            # Set secure permissions before replacing
            import os

            os.chmod(temp_path, self.perms)

            # Atomic replace
            temp_path.replace(self.path)

        except PermissionError as e:
            raise PermissionError(
                f"Permission denied writing to secrets file {self.path}. Check file permissions."
            ) from e
        except OSError as e:
            raise OSError(f"File system error writing to {self.path}: {e}") from e

    # ---------- CRUD ----------

    def read(self, scope: TokenScope) -> str | None:
        """Read a token for the given scope.

        Args:
            scope: The token scope to read from.

        Returns:
            The token string if found, None otherwise.

        Raises:
            RuntimeError: If the secrets file cannot be read or parsed.
        """
        try:
            doc = self._load()
        except Exception as e:
            raise RuntimeError(f"Failed to read secrets file {self.path}: {e}") from e

        norm_url = normalize_service_url(scope.url)

        # Try module-specific scope first
        if scope.module:
            # [module.<module>.user."<username>".urls."<url>"]
            if scope.username:
                modules = doc.get(self._module_tbl)
                module_tbl = isinstance(modules, dict) and modules.get(scope.module)
                users = isinstance(module_tbl, dict) and module_tbl.get(self._user_tbl)
                user_tbl = isinstance(users, dict) and users.get(scope.username)
                urls = isinstance(user_tbl, dict) and user_tbl.get(self._urls_tbl) or {}
                entry = isinstance(urls, dict) and urls.get(norm_url)
                if isinstance(entry, dict):
                    tok = entry.get(self._token_key)
                    if tok:
                        return str(tok)

            # [module.<module>.urls."<url>"] (module default)
            modules = doc.get(self._module_tbl)
            module_tbl = isinstance(modules, dict) and modules.get(scope.module)
            urls = isinstance(module_tbl, dict) and module_tbl.get(self._urls_tbl) or {}
            entry = isinstance(urls, dict) and urls.get(norm_url)
            if isinstance(entry, dict):
                tok = entry.get(self._token_key)
                if tok:
                    return str(tok)

        # Fall back to generic scope
        if scope.username is None:
            sect = doc.get(self._default_tbl)
            urls = isinstance(sect, dict) and sect.get(self._urls_tbl) or {}
            entry = isinstance(urls, dict) and urls.get(norm_url)
            if isinstance(entry, dict):
                tok = entry.get(self._token_key)
                return str(tok) if tok else None
            return None

        # user section
        users = doc.get(self._user_tbl)
        user_tbl = isinstance(users, dict) and users.get(scope.username)
        urls = isinstance(user_tbl, dict) and user_tbl.get(self._urls_tbl) or {}
        entry = isinstance(urls, dict) and urls.get(norm_url)
        if isinstance(entry, dict):
            tok = entry.get(self._token_key)
            return str(tok) if tok else None
        return None

    def write(self, scope: TokenScope, token: str) -> None:
        doc = self._load()
        norm_url = normalize_service_url(scope.url)

        if scope.module:
            # Write to module-specific section
            modules = doc.setdefault(self._module_tbl, tomlkit.table())
            module_tbl = modules.setdefault(scope.module, tomlkit.table())

            if scope.username is None:
                sect = module_tbl
            else:
                users = module_tbl.setdefault(self._user_tbl, tomlkit.table())
                sect = users.setdefault(scope.username, tomlkit.table())
        else:
            # Write to generic section
            if scope.username is None:
                sect = doc.setdefault(self._default_tbl, tomlkit.table())
            else:
                user_tbl = doc.setdefault(self._user_tbl, tomlkit.table())
                sect = user_tbl.setdefault(scope.username, tomlkit.table())

        urls = sect.setdefault(self._urls_tbl, tomlkit.table())
        entry = urls.setdefault(norm_url, tomlkit.table())
        entry[self._token_key] = token
        entry[self._updated_key] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self._save(doc)

    def delete(self, scope: TokenScope) -> None:
        doc = self._load()
        norm_url = normalize_service_url(scope.url)

        if scope.module:
            # Delete from module-specific section
            modules = doc.get(self._module_tbl)
            module_tbl = isinstance(modules, dict) and modules.get(scope.module)
            if module_tbl:
                if scope.username is None:
                    urls = isinstance(module_tbl, dict) and module_tbl.get(self._urls_tbl)
                    if isinstance(urls, dict):
                        urls.pop(norm_url, None)
                        self._save(doc)
                else:
                    users = isinstance(module_tbl, dict) and module_tbl.get(self._user_tbl)
                    user_tbl = isinstance(users, dict) and users.get(scope.username)
                    urls = isinstance(user_tbl, dict) and user_tbl.get(self._urls_tbl)
                    if isinstance(urls, dict):
                        urls.pop(norm_url, None)
                        self._save(doc)
            return

        # Delete from generic section
        if scope.username is None:
            sect = doc.get(self._default_tbl)
            urls = isinstance(sect, dict) and sect.get(self._urls_tbl)
            if isinstance(urls, dict):
                urls.pop(norm_url, None)
                self._save(doc)
            return

        users = doc.get(self._user_tbl)
        user_tbl = isinstance(users, dict) and users.get(scope.username)
        urls = isinstance(user_tbl, dict) and user_tbl.get(self._urls_tbl)
        if isinstance(urls, dict):
            urls.pop(norm_url, None)
            self._save(doc)

    def list_scopes(self) -> Iterable[TokenScope]:
        doc = self._load()
        # module-aware scopes
        modules = doc.get(self._module_tbl)
        if isinstance(modules, dict):
            for module_name, mod_tbl in modules.items():
                if not isinstance(mod_tbl, dict):
                    continue
                # module default
                urls = isinstance(mod_tbl.get(self._urls_tbl), dict) and mod_tbl.get(self._urls_tbl)
                if isinstance(urls, dict):
                    for url in urls.keys():
                        yield TokenScope(module=module_name, url=url, username=None)
                # module users
                users = mod_tbl.get(self._user_tbl)
                if isinstance(users, dict):
                    for uname, sect in users.items():
                        urls = isinstance(sect, dict) and sect.get(self._urls_tbl)
                        if isinstance(urls, dict):
                            for url in urls.keys():
                                yield TokenScope(module=module_name, url=url, username=uname)

        # No legacy generic sections in POC
