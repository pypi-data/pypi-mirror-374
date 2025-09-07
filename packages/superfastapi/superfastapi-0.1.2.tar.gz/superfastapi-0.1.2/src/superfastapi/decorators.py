from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

from .resolver import REGISTRY, ApiFunctionMeta, FunctionRecord, compute_hash, normalize_source_for_hash


def api_function(
    *,
    version: int = 1,
    external: bool = False,
    description: str = "",
    path: Optional[str] = None,
    methods: list[str] = None,
    requires_auth: bool = False,
    roles: list[str] = None,
    tests: list[dict] = None,
):
    """Decorator to declare a versioned API function.

    All metadata remains attached to the function (not stored in the lock).
    The code is hashed using the full decorated source to enforce immutability.
    """

    if methods is None:
        methods = ["POST"]
    if roles is None:
        roles = []
    if tests is None:
        tests = []

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        name = func.__name__
        module_name = func.__module__

        meta = ApiFunctionMeta(
            name=name,
            version=version,
            external=external,
            description=description,
            path=path,
            methods=methods,
            requires_auth=requires_auth,
            roles=roles,
            tests=tests,
        )

        src = normalize_source_for_hash(func)
        h = compute_hash(func)

        record = FunctionRecord(
            name=name,
            version=version,
            func=func,
            module_name=module_name,
            meta=meta,
            source=src,
            hash=h,
        )
        REGISTRY.register(record)

        # Install a dispatcher into the module globals so that calls like foo() resolve dynamically
        try:
            module = inspect.getmodule(func)
            if module is not None:
                setattr(module, name, REGISTRY.get_dispatcher(name))
        except Exception:
            # Non-fatal; fallback to direct function object
            pass

        # Attach metadata for later use (serving, docs)
        setattr(func, "__superfastapi_meta__", meta)

        return func

    return decorator

