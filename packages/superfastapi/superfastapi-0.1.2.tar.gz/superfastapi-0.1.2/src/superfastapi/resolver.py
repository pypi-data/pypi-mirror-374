from __future__ import annotations

import inspect
import textwrap
import hashlib
from dataclasses import dataclass
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional

from .exceptions import FunctionNotFoundError, ResolutionError


# Context of the current API version during a request or test run
current_api_version: ContextVar[Optional[str]] = ContextVar("current_api_version", default=None)


@dataclass
class ApiFunctionMeta:
    name: str
    version: int
    external: bool
    description: str
    path: Optional[str]
    methods: list[str]
    requires_auth: bool
    roles: list[str]
    tests: list[dict]


@dataclass
class FunctionRecord:
    name: str
    version: int
    func: Callable[..., Any]
    module_name: str
    meta: ApiFunctionMeta
    source: str
    hash: str


class Registry:
    def __init__(self) -> None:
        # name -> version -> record
        self._functions: Dict[str, Dict[int, FunctionRecord]] = {}
        # version mapping chosen by API version from lock
        # api_version -> {name -> version}
        self._chosen: Dict[str, Dict[str, int]] = {}
        # name -> dispatcher callable
        self._dispatchers: Dict[str, Callable[..., Any]] = {}

    # Registration and lookup
    def register(self, record: FunctionRecord) -> None:
        versions = self._functions.setdefault(record.name, {})
        versions[record.version] = record

    def list_names(self) -> list[str]:
        return sorted(self._functions.keys())

    def versions_for(self, name: str) -> list[int]:
        return sorted(self._functions.get(name, {}).keys())

    def get(self, name: str, version: int) -> FunctionRecord:
        try:
            return self._functions[name][version]
        except KeyError:
            raise FunctionNotFoundError(f"Function {name} version {version} not found")

    def latest_version(self, name: str) -> int:
        versions = self.versions_for(name)
        if not versions:
            raise FunctionNotFoundError(f"Function {name} not registered")
        return versions[-1]

    # Lock selection
    def set_lock_selection(self, api_version: str, mapping: Dict[str, int]) -> None:
        self._chosen[api_version] = dict(mapping)

    def resolve_version_for(self, api_version: str, name: str) -> int:
        if api_version not in self._chosen:
            raise ResolutionError(f"API version {api_version} has no lock selection")
        try:
            return self._chosen[api_version][name]
        except KeyError:
            raise FunctionNotFoundError(
                f"Function {name} is not available under API version {api_version}"
            )

    # Dispatchers
    def get_dispatcher(self, name: str) -> Callable[..., Any]:
        if name in self._dispatchers:
            return self._dispatchers[name]

        def _dispatcher(*args, **kwargs):  # type: ignore[no-redef]
            api_ver = current_api_version.get()
            if not api_ver:
                # Default to latest if no API context set
                version = self.latest_version(name)
            else:
                version = self.resolve_version_for(api_ver, name)
            record = self.get(name, version)
            return record.func(*args, **kwargs)

        self._dispatchers[name] = _dispatcher
        return _dispatcher


REGISTRY = Registry()


def normalize_source_for_hash(func: Callable[..., Any]) -> str:
    try:
        src = inspect.getsource(func)
    except OSError:
        # Fallback: repr if source unavailable (e.g., interactive); this weakens immutability guarantees
        src = repr(func)
    # Include decorator lines above def; inspect.getsource already does when available
    src = textwrap.dedent(src).strip()
    return src


def compute_hash(func: Callable[..., Any]) -> str:
    src = normalize_source_for_hash(func)
    h = hashlib.sha256(src.encode("utf-8")).hexdigest()
    return h

