from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import fnmatch
import time
import math
import importlib.util

from .resolver import REGISTRY, compute_hash
from .exceptions import ImmutableViolationError, TestFailureError, ApiVersionError
from .resolver import current_api_version


DEFAULT_LOCK_DIR = ".superfastapi/locks"


LIB_DIR = Path(__file__).resolve().parent
_ENV_INCLUDE = os.getenv("SUPERFASTAPI_INCLUDE")
_ENV_EXCLUDE = os.getenv("SUPERFASTAPI_EXCLUDE")


def _is_in_lib(path: Path) -> bool:
    try:
        Path(path).resolve().relative_to(LIB_DIR)
        return True
    except Exception:
        return False


def _iter_python_files(root: Path) -> Iterable[Path]:
    ignore_dirs = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored dirs
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
        # quick heuristic: only import files that reference our decorator
        with path.open("r", encoding="utf-8") as fh:
            head = fh.read()
        return "@api_function" in head
    except Exception:
        return False


def _safe_module_name(path: Path) -> str:
    stem = "superfastapi_user_" + "_".join(path.with_suffix("").parts)
    return stem


def _import_file(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(_safe_module_name(path), str(path))
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)


def _load_all_functions(scan_root: Path) -> None:
    for py in _iter_python_files(scan_root):
        if _file_might_have_api_functions(py):
            _import_file(py)


def _read_version_lock(lock_path: Path) -> Dict[str, Any]:
    with lock_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_version_lock(lock_path: Path, data: Dict[str, Any]) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _normalize_version(v: Optional[str]) -> str:
    if v is None:
        raise ApiVersionError("API version is required (e.g., v1)")
    v = v.strip()
    if not v.startswith("v"):
        v = "v" + v
    if not v[1:].isdigit():
        raise ApiVersionError(f"Invalid version: {v}")
    return v


def _list_existing_versions(lock_dir: Path) -> list[str]:
    versions: list[str] = []
    if lock_dir.exists():
        for p in lock_dir.glob("v*.lock.json"):
            name = p.stem  # e.g., 'v1.lock'
            # p.stem is 'v1.lock' for v1.lock.json; split once
            base = name.split(".lock", 1)[0]
            if base.startswith("v") and base[1:].isdigit():
                versions.append(base)
    return sorted(versions, key=lambda s: int(s[1:]))


def _next_version(lock_dir: Path) -> str:
    existing = _list_existing_versions(lock_dir)
    n = int(existing[-1][1:]) + 1 if existing else 1
    return f"v{n}"


def _api_version_number(api_version: str) -> int:
    # api_version like 'v1', 'v2'
    if not api_version.startswith("v"):
        raise ApiVersionError(f"Invalid API version: {api_version}")
    try:
        return int(api_version[1:])
    except ValueError:
        raise ApiVersionError(f"Invalid API version: {api_version}")


def _build_selection_for_api_version(api_version: str) -> Dict[str, int]:
    """For each function, choose the highest version <= api_version number."""
    cap = _api_version_number(api_version)
    selection: Dict[str, int] = {}
    for name in REGISTRY.list_names():
        eligible = [v for v in REGISTRY.versions_for(name) if v <= cap]
        if not eligible:
            # No version of this function is eligible for this API version; skip
            continue
        selection[name] = max(eligible)
    return selection


def compute_selection_for_api_version(api_version: str) -> Dict[str, int]:
    """Public wrapper for selection computation."""
    return _build_selection_for_api_version(api_version)


def _isclose(a: Any, b: Any, t: dict) -> bool:
    try:
        return math.isclose(float(a), float(b), rel_tol=float(t.get("rel_tol", t.get("tol", 0.0))), abs_tol=float(t.get("abs_tol", 0.0)))
    except Exception:
        return False


def run_inline_tests_for(api_version: str) -> None:
    token = current_api_version.set(api_version)
    try:
        verbose = os.getenv("SUPERFASTAPI_TEST_VERBOSE", "").lower() in {"1", "true", "yes"}
        for name in REGISTRY.list_names():
            version = REGISTRY.resolve_version_for(api_version, name)
            record = REGISTRY.get(name, version)
            for idx, t in enumerate(record.meta.tests or []):
                args = t.get("args", ())
                kwargs = t.get("kwargs", {})
                expected = t.get("expected", None)
                timeout = t.get("timeout")
                t0 = time.monotonic()
                result = record.func(*args, **kwargs)
                elapsed = time.monotonic() - t0
                if timeout is not None and elapsed > float(timeout):
                    raise TestFailureError(
                        f"Test {idx+1} timeout for {name} v{version}: elapsed {elapsed:.3f}s > {timeout}s"
                    )
                ok = False
                if t.get("approx"):
                    ok = _isclose(result, expected, t)
                else:
                    ok = (result == expected)
                if not ok:
                    msg = (
                        f"Test {idx+1} failed for {name} v{version}: expected {expected!r}, got {result!r}"
                    )
                    raise TestFailureError(msg)
                if verbose:
                    print(f"✓ {name} v{version} test {idx+1} ok in {elapsed:.3f}s")
    finally:
        current_api_version.reset(token)


def lock_command(
    version: Optional[str] = None,
    scan_root: Optional[Path] = None,
    lock_dir: Optional[Path] = None,
) -> str:
    scan_root = scan_root or Path.cwd()
    lock_dir = lock_dir or (scan_root / DEFAULT_LOCK_DIR)

    # Import all user .py files to populate registry
    _load_all_functions(scan_root)

    # Validate immutability across all existing version lock files
    existing_versions = _list_existing_versions(lock_dir)
    for api_ver in existing_versions:
        lock_path = lock_dir / f"{api_ver}.lock.json"
        data = _read_version_lock(lock_path)
        functions: Dict[str, Dict[str, Any]] = data.get("functions", {})
        for name, fmeta in functions.items():
            v = int(fmeta["version"])
            old_hash = fmeta["hash"]
            rec = REGISTRY.get(name, v)
            new_hash = compute_hash(rec.func)
            if new_hash != old_hash:
                raise ImmutableViolationError(
                    f"Immutable violation: {name} v{v} changed (expected {old_hash}, got {new_hash})"
                )

    # Determine target version to write
    target_ver = _normalize_version(version) if version else _next_version(lock_dir)

    # Build selection (highest version <= api version) and save as chosen for target api version
    selection = _build_selection_for_api_version(target_ver)
    REGISTRY.set_lock_selection(target_ver, selection)

    # Run inline tests under this selection
    run_inline_tests_for(target_ver)

    # Write per-version lock file
    functions_block: Dict[str, Dict[str, Any]] = {}
    for name, ver in selection.items():
        rec = REGISTRY.get(name, ver)
        functions_block[name] = {"version": ver, "hash": rec.hash}

    out_path = lock_dir / f"{target_ver}.lock.json"
    _write_version_lock(out_path, {"functions": functions_block})
    return target_ver


def load_all_locks(lock_dir: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    lock_dir = lock_dir or (Path.cwd() / DEFAULT_LOCK_DIR)
    versions = _list_existing_versions(lock_dir)
    result: Dict[str, Dict[str, Any]] = {}
    for api_ver in versions:
        p = lock_dir / f"{api_ver}.lock.json"
        try:
            result[api_ver] = _read_version_lock(p)
        except FileNotFoundError:
            continue
    return result


def list_versions(lock_dir: Optional[Path] = None) -> list[str]:
    lock_dir = lock_dir or (Path.cwd() / DEFAULT_LOCK_DIR)
    return _list_existing_versions(lock_dir)


def read_version_lock(version: str, lock_dir: Optional[Path] = None) -> Dict[str, Any]:
    lock_dir = lock_dir or (Path.cwd() / DEFAULT_LOCK_DIR)
    v = _normalize_version(version)
    p = lock_dir / f"{v}.lock.json"
    if not p.exists():
        raise ApiVersionError(f"Lock for {v} not found in {lock_dir}")
    return _read_version_lock(p)


def verify_version(
    version: str,
    *,
    scan_root: Optional[Path] = None,
    lock_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Verify that all functions in the lock exist and hash-match current code.

    Returns a report: { 'version': vX, 'ok': bool, 'results': [ {name, locked_version, locked_hash, status, current_hash?} ] }
    status in {'ok','missing','hash_mismatch'}
    """
    scan_root = scan_root or Path.cwd()
    lock_dir = lock_dir or (scan_root / DEFAULT_LOCK_DIR)
    v = _normalize_version(version)

    # Import current code
    _load_all_functions(scan_root)

    # Load lock
    p = lock_dir / f"{v}.lock.json"
    if not p.exists():
        raise ApiVersionError(f"Lock for {v} not found in {lock_dir}")
    data = _read_version_lock(p)
    functions: Dict[str, Dict[str, Any]] = data.get("functions", {})

    results = []
    ok = True
    for name, meta in functions.items():
        locked_ver = int(meta["version"]) if isinstance(meta.get("version"), int) else int(str(meta.get("version")))
        locked_hash = str(meta["hash"]) if "hash" in meta else ""
        try:
            rec = REGISTRY.get(name, locked_ver)
        except Exception:
            results.append({
                "name": name,
                "locked_version": locked_ver,
                "locked_hash": locked_hash,
                "status": "missing",
            })
            ok = False
            continue
        current_hash = compute_hash(rec.func)
        if current_hash != locked_hash:
            results.append({
                "name": name,
                "locked_version": locked_ver,
                "locked_hash": locked_hash,
                "current_hash": current_hash,
                "status": "hash_mismatch",
            })
            ok = False
        else:
            results.append({
                "name": name,
                "locked_version": locked_ver,
                "locked_hash": locked_hash,
                "status": "ok",
            })

    return {"version": v, "ok": ok, "results": results}


def build_preview_lock_for_version(
    api_version: str,
    *,
    scan_root: Optional[Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """Build an in-memory lock mapping for a preview of api_version.

    Does not write any files. Uses current code to compute selection and hashes.
    """
    scan_root = scan_root or Path.cwd()
    v = _normalize_version(api_version)
    _load_all_functions(scan_root)
    selection = _build_selection_for_api_version(v)
    REGISTRY.set_lock_selection(v, selection)
    functions_block: Dict[str, Dict[str, Any]] = {}
    for name, ver in selection.items():
        rec = REGISTRY.get(name, ver)
        functions_block[name] = {"version": ver, "hash": rec.hash}
    return {v: {"functions": functions_block}}
