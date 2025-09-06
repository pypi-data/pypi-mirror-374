import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, ClassVar

try:
    import keyring
except Exception as e:
    raise ImportError("Keyring loader requires `keyring`.") from e

try:
    import tomlkit
except Exception as e:
    raise ImportError("Keyring loader needs `tomlkit` for its index.") from e

from .loader_abstract import AbstractTokenLoader
from .scope import TokenScope, normalize_service_url
from ... import APP


@dataclass(slots=True)
class KeyringTokenLoader(AbstractTokenLoader):
    """
    Keyring-backed tokens, plus a small TOML *index* so we can enumerate scopes.

    Keyring layout:
      service = f"{service_prefix}:{module}:{username or 'default'}"
      username(key) = normalize_service_url(url)
      value = token

    Index file (TOML), module-aware (mirrors TOML loader semantics):
      [module."mreg".default]
      urls = ["https://mreg.uio.no", ...]

      [module."mreg".user."bob-drift"]
      urls = ["https://mreg.uio.no", ...]

      [module."ldap".default]
      urls = ["https://ldap.example.com", ...]
    """

    index_path: Path
    service_prefix: str = APP
    name: str = "keyring"
    _bak: Path | None = None
    _snapshot: dict[str, str | None] | None = None

    # Index table/key constants
    _module_tbl: ClassVar[str] = "module"
    _default_tbl: ClassVar[str] = "default"
    _user_tbl: ClassVar[str] = "user"
    _urls_key: ClassVar[str] = "urls"
    _default_user_label: ClassVar[str] = "default"

    def __init__(
        self, *, index_path: Path, service_prefix: str = APP, name: str = "keyring"
    ) -> None:
        self.name = name
        self.index_path = index_path
        self.service_prefix = service_prefix
        self._bak = self.index_path.with_suffix(self.index_path.suffix + ".bak")

    # ---------- transactional ----------

    def backup(self) -> None:
        if self.index_path.exists() and self._bak is not None:
            shutil.copy2(self.index_path, self._bak)
        # snapshot current tokens in memory for restore (best-effort)
        self._snapshot = {}
        for scope in self.list_scopes():
            self._snapshot[scope.identity()] = self._keyring_read(scope)

    def restore(self) -> None:
        if self._bak is not None and self._bak.exists():
            shutil.move(str(self._bak), str(self.index_path))
        # restore keyring values from snapshot (best-effort)
        snap = self._snapshot
        if snap is not None:
            for ident, token in snap.items():
                # identity format: module|username_or_default|url
                try:
                    module, uname, url = ident.split("|", 2)
                except ValueError:
                    # Fallback for old 2-part snapshot (uname|url) if encountered
                    uname, url = ident.split("|", 1)
                    module = "default"
                scope = TokenScope(
                    module=module,
                    url=url,
                    username=None if uname == self._default_user_label else uname,
                )
                if token is None:
                    self._keyring_delete(scope)
                else:
                    self._keyring_write(scope, token)

    # ---------- key helpers ----------

    def _service(self, module: str, username: str | None) -> str:
        return f"{self.service_prefix}:{module}:{username or self._default_user_label}"

    # ---------- index helpers ----------

    def _empty_index(self) -> tomlkit.TOMLDocument:
        doc = tomlkit.document()
        # Root contains a single top-level "module" table
        doc[self._module_tbl] = tomlkit.table()
        return doc

    def _read_index(self) -> tomlkit.TOMLDocument:
        if self.index_path.exists():
            return tomlkit.parse(self.index_path.read_text(encoding="utf-8"))
        return self._empty_index()

    def _write_index(self, doc: tomlkit.TOMLDocument) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(tomlkit.dumps(doc), encoding="utf-8")

    # ---------- keyring raw ops ----------

    def _keyring_read(self, scope: TokenScope) -> str | None:
        return keyring.get_password(
            self._service(scope.module, scope.username),
            normalize_service_url(scope.url),
        )

    def _keyring_write(self, scope: TokenScope, token: str) -> None:
        keyring.set_password(
            self._service(scope.module, scope.username),
            normalize_service_url(scope.url),
            token,
        )

    def _keyring_delete(self, scope: TokenScope) -> None:
        try:
            keyring.delete_password(
                self._service(scope.module, scope.username),
                normalize_service_url(scope.url),
            )
        except Exception:
            pass

    # ---------- CRUD ----------

    def read(self, scope: TokenScope) -> str | None:
        return self._keyring_read(scope)

    def write(self, scope: TokenScope, token: str) -> None:
        self._keyring_write(scope, token)
        # update index
        doc = self._read_index()
        modules = doc.setdefault(self._module_tbl, {})
        mod_tbl = modules.setdefault(scope.module, {})
        if scope.username is None:
            sect = mod_tbl.setdefault(self._default_tbl, {})
            urls = sect.setdefault(self._urls_key, [])
            if normalize_service_url(scope.url) not in urls:
                urls.append(normalize_service_url(scope.url))
        else:
            user_tbl = mod_tbl.setdefault(self._user_tbl, {})
            sect = user_tbl.setdefault(scope.username, {})
            urls = sect.setdefault(self._urls_key, [])
            if normalize_service_url(scope.url) not in urls:
                urls.append(normalize_service_url(scope.url))
        self._write_index(doc)

    def delete(self, scope: TokenScope) -> None:
        self._keyring_delete(scope)
        # update index
        doc = self._read_index()
        url = normalize_service_url(scope.url)
        modules = doc.setdefault(self._module_tbl, {})
        mod_tbl = modules.setdefault(scope.module, {})
        if scope.username is None:
            sect = mod_tbl.setdefault(self._default_tbl, {})
            urls = sect.setdefault(self._urls_key, [])
            if url in urls:
                urls.remove(url)
        else:
            user_tbl = mod_tbl.setdefault(self._user_tbl, {})
            sect = user_tbl.setdefault(scope.username, {})
            urls = sect.setdefault(self._urls_key, [])
            if url in urls:
                urls.remove(url)
        self._write_index(doc)

    def list_scopes(self) -> Iterable[TokenScope]:
        doc = self._read_index()
        # Iterate per-module
        modules = doc.get(self._module_tbl) or {}
        for module, mod_tbl in modules.items():
            if not isinstance(mod_tbl, dict):
                continue
            # default
            for url in (mod_tbl.get(self._default_tbl) or {}).get(self._urls_key) or []:
                yield TokenScope(module=module, url=url, username=None)
            # users
            for uname, sect in (mod_tbl.get(self._user_tbl) or {}).items():
                for url in (sect or {}).get(self._urls_key) or []:
                    yield TokenScope(module=module, url=url, username=uname)
