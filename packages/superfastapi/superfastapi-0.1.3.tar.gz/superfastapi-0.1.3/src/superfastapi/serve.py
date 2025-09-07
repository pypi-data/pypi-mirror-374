from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Callable, Dict, Optional, Tuple
import fnmatch
import time
import inspect

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel, create_model, ValidationError
from jose import jwt, JWTError
from starlette.concurrency import run_in_threadpool

from .lock import load_all_locks, DEFAULT_LOCK_DIR
from .resolver import REGISTRY, current_api_version
from .exceptions import (
    ApiVersionError,
    FunctionNotFoundError,
    ImmutableViolationError,
    TestFailureError,
    AuthError,
    ResolutionError,
)


def _error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiVersionError)
    async def _api_ver_handler(request: Request, exc: ApiVersionError):
        return JSONResponse(status_code=404, content={"error": str(exc), "type": "VERSION_NOT_FOUND"})

    @app.exception_handler(FunctionNotFoundError)
    async def _fnf_handler(request: Request, exc: FunctionNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc), "type": "FUNCTION_NOT_FOUND"})

    @app.exception_handler(ImmutableViolationError)
    async def _imm_handler(request: Request, exc: ImmutableViolationError):
        return JSONResponse(status_code=500, content={"error": str(exc), "type": "IMMUTABLE_VIOLATION"})

    @app.exception_handler(TestFailureError)
    async def _test_handler(request: Request, exc: TestFailureError):
        return JSONResponse(status_code=400, content={"error": str(exc), "type": "TEST_FAILURE"})

    @app.exception_handler(AuthError)
    async def _auth_handler(request: Request, exc: AuthError):
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc), "type": "AUTH_ERROR"})

    @app.exception_handler(ResolutionError)
    async def _res_handler(request: Request, exc: ResolutionError):
        return JSONResponse(status_code=500, content={"error": str(exc), "type": "RESOLUTION_ERROR"})

    @app.exception_handler(Exception)
    async def _general(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"error": "Internal server error", "type": "INTERNAL_ERROR"})


def _jwt_secret() -> str:
    return os.getenv("SUPERFASTAPI_SECRET", "change-me-superfastapi-secret")


def _make_auth_checker(requires_auth: bool, roles: list[str]):
    async def checker(request: Request) -> None:
        mode = os.getenv("SUPERFASTAPI_AUTH_MODE", "jwt").lower()
        if not requires_auth or mode == "none":
            return
        if mode == "apikey":
            key_header = os.getenv("SUPERFASTAPI_API_KEY_HEADER", "X-API-Key")
            expected = os.getenv("SUPERFASTAPI_API_KEY", "")
            provided = request.headers.get(key_header)
            if not expected:
                raise AuthError("Server misconfigured: API key not set", status_code=500)
            if not provided or provided != expected:
                raise AuthError("Authentication required", status_code=401)
            # roles ignored in apikey mode
            return
        # default: jwt
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise AuthError("Authentication required", status_code=401)
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        except JWTError:
            raise AuthError("Invalid token", status_code=401)
        if roles:
            user_roles = payload.get("roles", [])
            if not isinstance(user_roles, list) or not set(user_roles).intersection(set(roles)):
                raise AuthError("Forbidden: insufficient role", status_code=403)
        # Could attach user to request.state if needed
    return checker


def _build_request_model(func) -> Tuple[Optional[type[BaseModel]], Dict[str, Any]]:
    """Create a pydantic model from function signature for request validation.
    Returns (model or None, field_defaults)
    """
    sig = func.__signature__ if hasattr(func, "__signature__") else None
    if sig is None:
        try:
            sig = inspect.signature(func)  # type: ignore
        except Exception:
            sig = None
    if sig is None:
        return None, {}

    fields = {}
    defaults = {}
    for name, param in sig.parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue  # Skip *args/**kwargs in model
        annotation = param.annotation if param.annotation is not inspect._empty else (Any)
        default = param.default if param.default is not inspect._empty else ...
        fields[name] = (annotation, default)
        if default is not ...:
            defaults[name] = default
    if not fields:
        return None, {}
    model = create_model(f"{func.__name__}Request", **fields)  # type: ignore
    return model, defaults


async def _call_function(func, kwargs: Dict[str, Any]):
    if asyncio.iscoroutinefunction(func):
        return await func(**kwargs)
    return await run_in_threadpool(func, **kwargs)


class FixedWindowRateLimiter:
    def __init__(self, limit: int, period_seconds: float) -> None:
        self.limit = limit
        self.period = period_seconds
        self._store: Dict[str, tuple[float, int]] = {}

    def check(self, key: str) -> bool:
        now = time.monotonic()
        start, count = self._store.get(key, (now, 0))
        if now - start >= self.period:
            start, count = now, 0
        if count >= self.limit:
            self._store[key] = (start, count)
            return False
        count += 1
        self._store[key] = (start, count)
        return True


def _parse_rate_env() -> Optional[FixedWindowRateLimiter]:
    rate = os.getenv("SUPERFASTAPI_RATE_LIMIT")  # e.g., 60/min, 5/sec
    if not rate:
        return None
    rate = rate.strip().lower()
    try:
        if "/" in rate:
            n_str, unit = rate.split("/", 1)
            n = int(n_str)
            unit = unit.strip()
            if unit in {"s", "sec", "second", "seconds"}:
                period = 1.0
            elif unit in {"m", "min", "minute", "minutes"}:
                period = 60.0
            elif unit in {"h", "hour", "hours"}:
                period = 3600.0
            else:
                period = float(unit)
        else:
            # default to per minute
            n = int(rate)
            period = 60.0
        return FixedWindowRateLimiter(n, period)
    except Exception:
        return None


import os
from pathlib import Path
import importlib.util


LIB_DIR = Path(__file__).resolve().parent
_ENV_INCLUDE = os.getenv("SUPERFASTAPI_INCLUDE")
_ENV_EXCLUDE = os.getenv("SUPERFASTAPI_EXCLUDE")


def _is_in_lib(path: Path) -> bool:
    try:
        Path(path).resolve().relative_to(LIB_DIR)
        return True
    except Exception:
        return False


def _iter_python_files(root: Path):
    ignore_dirs = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and not d.startswith(".")]
        for f in filenames:
            if f.endswith(".py") and not f.startswith("."):
                full = Path(dirpath) / f
                if not _is_in_lib(full):
                    # include/exclude filters
                    if _ENV_INCLUDE:
                        inc = any(fnmatch.fnmatch(str(full), pat.strip()) for pat in _ENV_INCLUDE.split(",") if pat.strip())
                        if not inc:
                            continue
                    if _ENV_EXCLUDE:
                        exc = any(fnmatch.fnmatch(str(full), pat.strip()) for pat in _ENV_EXCLUDE.split(",") if pat.strip())
                        if exc:
                            continue
                    yield full


def _file_might_have_api_functions(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as fh:
            head = fh.read()
        return "@api_function" in head
    except Exception:
        return False


def _safe_module_name(path: Path) -> str:
    return "superfastapi_user_" + "_".join(path.with_suffix("").parts)


def _import_file(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(_safe_module_name(path), str(path))
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # type: ignore[name-defined]
        spec.loader.exec_module(module)


def _load_all_functions(scan_root: Path) -> None:
    for py in _iter_python_files(scan_root):
        if _file_might_have_api_functions(py):
            _import_file(py)


def build_app(lock_versions: Optional[Dict[str, Dict[str, Any]]] = None, *, root: Optional[Path] = None, lock_dir: Optional[Path] = None) -> FastAPI:
    app = FastAPI(title="SuperFastAPI")
    _error_handlers(app)

    # Import all user code to populate registry before wiring routes
    scan_root = root or Path.cwd()
    _load_all_functions(scan_root)

    lock_dir = lock_dir or (scan_root / DEFAULT_LOCK_DIR)
    versions = lock_versions or load_all_locks(lock_dir)
    if not versions:
        # No lock yet => empty app but 404s will be clear
        return app

    # Optional CORS and GZip
    cors_mode = os.getenv("SUPERFASTAPI_CORS", "open").lower()
    if cors_mode == "open":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    if os.getenv("SUPERFASTAPI_GZIP", "").lower() in {"1", "true", "yes"}:
        app.add_middleware(GZipMiddleware)

    rate_limiter = _parse_rate_env()

    # For each API version in lock, prepare chosen mapping and routes
    for api_ver, info in versions.items():
        chosen = {name: int(meta["version"]) for name, meta in info.get("functions", {}).items()}
        REGISTRY.set_lock_selection(api_ver, chosen)

        router = APIRouter(prefix=f"/{api_ver}")

        # Add routes for external functions only
        for name, version in chosen.items():
            record = REGISTRY.get(name, version)
            if not record.meta.external:
                continue

            requires_auth = record.meta.requires_auth
            roles = record.meta.roles
            description = record.meta.description or f"{name} v{version}"
            methods = record.meta.methods or ["POST"]
            rel_path = record.meta.path or f"/{name}"
            if not rel_path.startswith("/"):
                rel_path = "/" + rel_path

            RequestModel, _defaults = _build_request_model(record.func)
            response_model = getattr(record.func, "__annotations__", {}).get("return", None)

            async def endpoint(
                request: Request,
                __name=name,
                __api_ver=api_ver,
                __record=record,
                __requires_auth=requires_auth,
                __roles=roles,
                __RequestModel=RequestModel,
            ):
                # Set API version context for internal dispatchers
                token = current_api_version.set(__api_ver)
                try:
                    # Validate auth
                    await _make_auth_checker(__requires_auth, __roles)(request)

                    data = {}
                    if __RequestModel is not None:
                        if request.method in {"POST", "PUT", "PATCH"}:
                            body = await request.json()
                            try:
                                # pydantic v2
                                model = __RequestModel.model_validate(body)  # type: ignore[attr-defined]
                                data = model.model_dump()
                            except AttributeError:
                                # pydantic v1
                                model = __RequestModel.parse_obj(body)  # type: ignore[attr-defined]
                                data = model.dict()
                            except ValidationError as e:  # type: ignore[no-redef]
                                raise HTTPException(status_code=422, detail=getattr(e, 'errors', lambda: str(e))())
                        else:
                            # GET/DELETE from query params
                            qp = dict(request.query_params)
                            try:
                                model = __RequestModel.model_validate(qp)  # type: ignore[attr-defined]
                                data = model.model_dump()
                            except AttributeError:
                                model = __RequestModel.parse_obj(qp)  # type: ignore[attr-defined]
                                data = model.dict()
                            except ValidationError as e:  # type: ignore[no-redef]
                                raise HTTPException(status_code=422, detail=getattr(e, 'errors', lambda: str(e))())

                    # Rate limiting (global, optional)
                    if rate_limiter is not None:
                        key = f"{__api_ver}:{rel_path}:{request.client.host if request.client else 'client'}"
                        if not rate_limiter.check(key):
                            raise HTTPException(status_code=429, detail="Rate limit exceeded")

                    # Execute function
                    result = await _call_function(__record.func, data)
                    return result
                except AuthError as e:
                    raise HTTPException(status_code=e.status_code, detail=str(e))
                except HTTPException:
                    raise
                except Exception as e:
                    # Hide internal details
                    raise HTTPException(status_code=500, detail="Internal server error") from e
                finally:
                    current_api_version.reset(token)

            # Register route
            # OpenAPI examples from tests
            examples_rb: Dict[str, Any] = {}
            for i, t in enumerate(record.meta.tests or []):
                ex_name = f"t{i+1}"
                if __RequestModel is not None and methods and set(methods) & {"POST", "PUT", "PATCH"}:
                    payload = {}
                    if isinstance(t.get("args"), (list, tuple)) and __RequestModel is not None:
                        # Can't map positional args reliably; prefer kwargs
                        pass
                    payload.update(t.get("kwargs", {}))
                    if payload:
                        examples_rb[ex_name] = {"value": payload}

            openapi_extra = None
            responses = None
            if examples_rb:
                openapi_extra = {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "examples": examples_rb
                            }
                        }
                    }
                }

            router.add_api_route(
                rel_path,
                endpoint,
                name=name,
                methods=methods,
                description=description,
                response_model=response_model,
                openapi_extra=openapi_extra,
            )

        app.include_router(router)

    # Health and versions endpoints (not prefixed)
    @app.get("/__health")
    async def __health():
        return {"status": "ok"}

    @app.get("/__versions")
    async def __versions():
        out = {}
        for api_ver, info in versions.items():
            out[api_ver] = sorted(info.get("functions", {}).keys())
        return out

    return app
