from __future__ import annotations

import sys
import click
import uvicorn
from pathlib import Path

from .lock import (
    lock_command,
    list_versions as list_versions_fn,
    read_version_lock,
    verify_version,
    load_all_locks,
    DEFAULT_LOCK_DIR,
    compute_selection_for_api_version,
    build_preview_lock_for_version,
)
from .serve import build_app
from .resolver import REGISTRY
import re
import json
from textwrap import dedent
from .exceptions import SuperFastAPIError


@click.group()
def main() -> None:
    """SuperFastAPI CLI."""


@main.command()
@click.argument("version", required=False)
@click.option("--root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option("--lock-dir", "lock_dir_opt", type=click.Path(file_okay=False, path_type=Path), default=None, help="Directory to store/read per-version lock files; defaults to .superfastapi/locks under root")
def lock(version: str | None, root: Path, lock_dir_opt: Path | None) -> None:
    """Generate or update the lock for VERSION (e.g., v2). If omitted, auto-increment."""
    try:
        v = lock_command(version, scan_root=root, lock_dir=lock_dir_opt)
        click.echo(f"Wrote lock for {v}")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, type=int, show_default=True)
@click.option("--reload/--no-reload", default=True, show_default=True)
@click.option("--root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option("--lock-dir", "lock_dir_opt", type=click.Path(file_okay=False, path_type=Path), default=None, help="Directory to read per-version lock files; defaults to .superfastapi/locks under root")
def serve(host: str, port: int, reload: bool, root: Path, lock_dir_opt: Path | None) -> None:
    """Serve the API using the current lock."""
    # Build app to validate before starting uvicorn
    app = build_app(root=root, lock_dir=lock_dir_opt)
    uvicorn.run(app, host=host, port=port, reload=reload)


@main.command(name="versions")
@click.option("--root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option("--lock-dir", "lock_dir_opt", type=click.Path(file_okay=False, path_type=Path), default=None)
def versions_cmd(root: Path, lock_dir_opt: Path | None) -> None:
    """List API versions that have lock files."""
    try:
        lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
        versions = list_versions_fn(lock_dir)
        for v in versions:
            click.echo(v)
        if not versions:
            click.echo("(no versions)")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="list")
@click.argument("version", required=False)
@click.option("--root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option("--lock-dir", "lock_dir_opt", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option("--verify/--no-verify", default=False, show_default=True)
def list_cmd(version: str | None, root: Path, lock_dir_opt: Path | None, verify: bool) -> None:
    """List functions in a version lock. If VERSION omitted, list all with counts."""
    try:
        lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
        if version:
            v = version
            if verify:
                report = verify_version(v, scan_root=root, lock_dir=lock_dir)
                click.echo(f"{report['version']} | ok={report['ok']}")
                for r in report["results"]:
                    line = f" - {r['name']} v{r['locked_version']} [{r['status']}]"
                    if r["status"] == "hash_mismatch":
                        line += " (hash mismatch)"
                    click.echo(line)
            else:
                data = read_version_lock(v, lock_dir)
                fns = data.get("functions", {})
                click.echo(f"{v} | {len(fns)} functions")
                for name, meta in fns.items():
                    click.echo(f" - {name} v{meta['version']}")
        else:
            versions = list_versions_fn(lock_dir)
            for v in versions:
                data = read_version_lock(v, lock_dir)
                fns = data.get("functions", {})
                click.echo(f"{v} | {len(fns)} functions")
            if not versions:
                click.echo("(no versions)")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="prune")
@click.argument("version", required=False)
@click.option("--root", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option("--lock-dir", "lock_dir_opt", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option("--all", "prune_all", is_flag=True, help="Prune all versions that fail verification")
@click.option("--dry-run/--no-dry-run", default=True, show_default=True)
@click.option("--force", is_flag=True, help="Do not prompt for confirmation when deleting")
def prune_cmd(version: str | None, root: Path, lock_dir_opt: Path | None, prune_all: bool, dry_run: bool, force: bool) -> None:
    """Prune version locks. By default removes versions that fail verification.

    If VERSION is provided, only consider that version. With --all, consider all versions.
    """
    lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
    to_check = []
    try:
        if version and prune_all:
            click.echo("Specify either VERSION or --all, not both", err=True)
            sys.exit(2)
        if version:
            to_check = [version]
        else:
            to_check = list_versions_fn(lock_dir)
        if not to_check:
            click.echo("Nothing to prune: no versions found")
            return
        deletions = []
        for v in to_check:
            report = verify_version(v, scan_root=root, lock_dir=lock_dir)
            if not report["ok"]:
                deletions.append((v, report))
        if not deletions:
            click.echo("No failing versions to prune")
            return
        for v, report in deletions:
            click.echo(f"Would remove {v} (dry-run)" if dry_run else f"Remove {v}")
            for r in report["results"]:
                if r["status"] != "ok":
                    click.echo(f" - {r['name']} v{r['locked_version']}: {r['status']}")
        if dry_run:
            click.echo("Dry run: no files deleted. Re-run with --no-dry-run to apply.")
            return
        # Confirm
        if not force:
            if not click.confirm(f"Proceed to delete {len(deletions)} lock file(s)?"):
                click.echo("Aborted")
                return
        # Delete files
        for v, _ in deletions:
            p = lock_dir / (f"{v}.lock.json")
            try:
                p.unlink()
                click.echo(f"Deleted {p}")
            except FileNotFoundError:
                pass
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _load_user_code(root: Path) -> None:
    # Reuse loader from lock module
    from .lock import _load_all_functions as _load
    _load(root)


def _find_latest_record(func_name: str):
    versions = REGISTRY.versions_for(func_name)
    if not versions:
        raise SuperFastAPIError(f"Function {func_name} not found")
    v = versions[-1]
    return REGISTRY.get(func_name, v)


def _bump_source_block(src: str, new_version: int) -> str:
    # Replace version=... inside @api_function decorator or inject if missing
    dec_start = src.find('@api_function')
    if dec_start == -1:
        return src
    # Find position of 'def '
    def_idx = src.find('\ndef ')
    if def_idx == -1:
        # Sometimes decorator and def on same line
        def_idx = src.find('def ')
    if def_idx == -1:
        return src
    decorator_text = src[:def_idx]
    if 'version' in decorator_text:
        new_dec = re.sub(r'version\s*=\s*\d+', f'version={new_version}', decorator_text, count=1)
    else:
        new_dec = decorator_text.replace('@api_function(', f'@api_function(version={new_version}, ')
    return new_dec + src[def_idx:]


@main.command()
@click.argument('function_name', required=True)
@click.option('--to', 'to_version', required=False, help='Target version (e.g., v2 or 2). Defaults to latest+1')
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--dry-run', is_flag=True, help='Print the bumped block to stdout instead of writing')
@click.option('--append/--no-append', default=True, show_default=True, help='Append to the source file when writing')
def bump(function_name: str, to_version: str | None, root: Path, dry_run: bool, append: bool) -> None:
    """Clone a function block with incremented version and write it next to the original.

    This keeps the single-code-block workflow: code + metadata + tests.
    """
    try:
        _load_user_code(root)
        rec = _find_latest_record(function_name)
        old_v = rec.version
        if to_version:
            v = to_version.strip()
            if v.startswith('v'): v = v[1:]
            new_v = int(v)
        else:
            new_v = old_v + 1
        # Build bumped block
        block = rec.source
        # Ensure decorator exists in source. If not, we can synthesize one, but prefer to error.
        if '@api_function' not in block:
            raise SuperFastAPIError('Cannot bump: source missing @api_function decorator in captured block')
        bumped = _bump_source_block(block, new_v)
        header = f"\n\n# ---- Bumped by apikit: {function_name} v{old_v} -> v{new_v} ----\n"
        out = header + bumped + "\n"
        if dry_run:
            click.echo(out)
            return
        # Locate file to write
        import sys as _sys
        mod = _sys.modules.get(rec.module_name)
        if not mod or not getattr(mod, '__file__', None):
            raise SuperFastAPIError('Could not locate original source file to write to')
        dest = Path(mod.__file__)
        mode = 'a' if append else 'w'
        with dest.open(mode, encoding='utf-8') as fh:
            fh.write(out)
        click.echo(f"Wrote bumped function to {dest} (v{new_v})")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _selection_from_lock(version: str, root: Path, lock_dir: Path):
    from .lock import read_version_lock
    data = read_version_lock(version, lock_dir)
    return {name: int(meta['version']) for name, meta in data.get('functions', {}).items()}


def _collect_routes(api_version: str, selection: dict[str, int]):
    routes = set()
    for name, ver in selection.items():
        try:
            rec = REGISTRY.get(name, ver)
        except Exception:
            continue
        if not rec.meta.external:
            continue
        rel_path = rec.meta.path or f"/{name}"
        if not rel_path.startswith('/'):
            rel_path = '/' + rel_path
        for m in (rec.meta.methods or ['POST']):
            routes.add((f"/v{api_version[1:]}{rel_path}", m))
    return routes


@main.command()
@click.argument('old_version', required=True)
@click.argument('new_version', required=True)
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--lock-dir', 'lock_dir_opt', type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option('--json', 'as_json', is_flag=True, help='Output machine-readable JSON')
def diff(old_version: str, new_version: str, root: Path, lock_dir_opt: Path | None, as_json: bool) -> None:
    """Show differences between two locked API versions (functions and routes)."""
    try:
        lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
        _load_user_code(root)
        sel_old = _selection_from_lock(old_version, root, lock_dir)
        sel_new = _selection_from_lock(new_version, root, lock_dir)
        names = set(sel_old) | set(sel_new)
        added = sorted(n for n in names if n not in sel_old and n in sel_new)
        removed = sorted(n for n in names if n in sel_old and n not in sel_new)
        changed = sorted(n for n in names if n in sel_old and n in sel_new and sel_old[n] != sel_new[n])
        unchanged_count = sum(1 for n in names if n in sel_old and n in sel_new and sel_old[n] == sel_new[n])

        routes_old = _collect_routes(_normalize_version_cli(old_version), sel_old)
        routes_new = _collect_routes(_normalize_version_cli(new_version), sel_new)
        routes_added = sorted(routes_new - routes_old)
        routes_removed = sorted(routes_old - routes_new)

        if as_json:
            click.echo(json.dumps({
                'old': _normalize_version_cli(old_version),
                'new': _normalize_version_cli(new_version),
                'functions': {
                    'added': added,
                    'removed': removed,
                    'changed': [{ 'name': n, 'from': sel_old.get(n), 'to': sel_new.get(n)} for n in changed],
                    'unchanged_count': unchanged_count,
                },
                'routes': {
                    'added': routes_added,
                    'removed': routes_removed,
                }
            }, indent=2))
            return
        click.echo(f"Diff {old_version} -> {new_version}")
        if added:
            click.echo("Added functions:")
            for n in added:
                click.echo(f" - {n} v{sel_new[n]}")
        if removed:
            click.echo("Removed functions:")
            for n in removed:
                click.echo(f" - {n} v{sel_old[n]}")
        if changed:
            click.echo("Changed versions:")
            for n in changed:
                click.echo(f" - {n}: v{sel_old[n]} -> v{sel_new[n]}")
        click.echo(f"Unchanged functions: {unchanged_count}")
        if routes_added:
            click.echo("Added routes:")
            for p, m in routes_added:
                click.echo(f" - {m} {p}")
        if routes_removed:
            click.echo("Removed routes:")
            for p, m in routes_removed:
                click.echo(f" - {m} {p}")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _normalize_version_cli(v: str) -> str:
    v = v.strip()
    if not v.startswith('v'):
        v = 'v' + v
    return v


@main.command()
@click.argument('old_version', required=True)
@click.argument('new_version', required=True)
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--lock-dir', 'lock_dir_opt', type=click.Path(file_okay=False, path_type=Path), default=None)
def changelog(old_version: str, new_version: str, root: Path, lock_dir_opt: Path | None) -> None:
    """Human-readable change notes between two versions."""
    try:
        # Reuse diff logic
        ctx = click.get_current_context()
        ctx.invoke(diff, old_version=old_version, new_version=new_version, root=root, lock_dir_opt=lock_dir_opt, as_json=False)
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('version', required=True)
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8001, type=int)
@click.option('--reload/--no-reload', default=True)
def preview(version: str, root: Path, host: str, port: int, reload: bool) -> None:
    """Serve a development preview for VERSION (does not write lock files)."""
    try:
        # Build in-memory locks
        locks = build_preview_lock_for_version(version, scan_root=root)
        app = build_app(lock_versions=locks, root=root)
        click.echo(f"Serving DEV preview for { _normalize_version_cli(version) } (no lock written)")
        uvicorn.run(app, host=host, port=port, reload=reload)
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def client():
    """Generate minimal client stubs."""
    pass


def _collect_external_endpoints(version: str, root: Path, lock_dir: Path):
    _load_user_code(root)
    sel = _selection_from_lock(version, root, lock_dir)
    eps = []
    v = _normalize_version_cli(version)
    for name, ver in sel.items():
        rec = REGISTRY.get(name, ver)
        if not rec.meta.external:
            continue
        path = rec.meta.path or f"/{name}"
        if not path.startswith('/'):
            path = '/' + path
        eps.append({
            'name': name,
            'path': f"/{v}{path}",
            'methods': rec.meta.methods or ['POST']
        })
    return eps


@client.command('ts')
@click.argument('version', required=True)
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--lock-dir', 'lock_dir_opt', type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option('--out', type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option('--base-url', default='http://localhost:8000')
def client_ts(version: str, root: Path, lock_dir_opt: Path | None, out: Path, base_url: str) -> None:
    """Generate a minimal TypeScript client for a locked version."""
    try:
        lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
        eps = _collect_external_endpoints(version, root, lock_dir)
        lines = [
            f"export const apiBase = '{base_url}';",
            "async function handle(resp: Response) { if (!resp.ok) throw new Error(`HTTP ${resp.status}`); return resp.json(); }",
        ]
        for ep in eps:
            name = ep['name']
            path = ep['path']
            methods = ep['methods']
            m = methods[0] if methods else 'POST'
            if m.upper() == 'GET':
                lines.append(
                    f"export async function {name}(params: Record<string, any> = {{}}): Promise<any> {{\n  const qs = new URLSearchParams(params as any).toString();\n  const url = `${{apiBase}}{path}?${{qs}}`;\n  const resp = await fetch(url, {{ method: 'GET' }});\n  return handle(resp);\n}}".replace('{path}', path)
                )
            else:
                lines.append(
                    f"export async function {name}(payload: any): Promise<any> {{\n  const resp = await fetch(`${{apiBase}}{path}`, {{ method: '{m.upper()}', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(payload) }});\n  return handle(resp);\n}}".replace('{path}', path)
                )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n\n".join(lines) + "\n", encoding='utf-8')
        click.echo(f"Wrote TypeScript client to {out}")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@client.command('py')
@click.argument('version', required=True)
@click.option('--root', type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path.cwd())
@click.option('--lock-dir', 'lock_dir_opt', type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option('--out', type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option('--base-url', default='http://localhost:8000')
def client_py(version: str, root: Path, lock_dir_opt: Path | None, out: Path, base_url: str) -> None:
    """Generate a minimal Python client for a locked version (requires requests)."""
    try:
        lock_dir = lock_dir_opt or (root / DEFAULT_LOCK_DIR)
        eps = _collect_external_endpoints(version, root, lock_dir)
        lines = [
            "import requests",
            f"API_BASE = '{base_url}'",
        ]
        for ep in eps:
            name = ep['name']
            path = ep['path']
            methods = ep['methods']
            m = (methods[0] if methods else 'POST').upper()
            if m == 'GET':
                lines.append(
                    f"def {name}(**params):\n    r = requests.get(API_BASE + '{path}', params=params)\n    r.raise_for_status()\n    return r.json()"
                )
            else:
                lines.append(
                    f"def {name}(payload):\n    r = requests.request('{m}', API_BASE + '{path}', json=payload)\n    r.raise_for_status()\n    return r.json()"
                )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n\n".join(lines) + "\n", encoding='utf-8')
        click.echo(f"Wrote Python client to {out}")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def init():
    """Scaffold new SuperFastAPI projects."""
    pass


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


@init.command('vercel')
@click.option('--dir', 'out_dir', type=click.Path(path_type=Path), default=Path.cwd()/"superfastapi-vercel-app")
@click.option('--lock-version', 'lock_ver', default='v1', help='Initial API version lock to generate (or empty to skip)')
def init_vercel(out_dir: Path, lock_ver: str) -> None:
    """Create a minimal project ready to deploy on Vercel (Python runtime)."""
    try:
        # Basic layout
        app_py = dedent('''
            from superfastapi import api_function

            @api_function(version=1, external=True, description="Hello", methods=["GET"], path="/")
            def hello(name: str = "world") -> dict:
                return {"message": f"Hello, {name}!"}

            @api_function(version=1, external=True, description="Add", methods=["POST"],
                          tests=[{"args": (1,2), "kwargs": {}, "expected": 3}])
            def add(a: int, b: int) -> int:
                return a + b
        ''').strip()+"\n"

        index_py = dedent('''
            # Vercel entrypoint: exposes FastAPI app as a Serverless Function
            from pathlib import Path
            from superfastapi.serve import build_app

            # Build app from project root (one level up from this file)
            app = build_app(root=Path(__file__).resolve().parents[1])
        ''').strip()+"\n"

        vercel_json = dedent('''
            {
              "functions": {
                "api/index.py": {
                  "runtime": "python3.11"
                }
              },
              "routes": [
                { "src": "/(.*)", "dest": "api/index.py" }
              ]
            }
        ''').strip()+"\n"

        reqs = dedent('''
            fastapi>=0.111
            pydantic>=2.6
            python-jose[cryptography]>=3.3
            uvicorn>=0.22
            superfastapi>=0.1.0
        ''').strip()+"\n"

        readme = dedent('''
            # SuperFastAPI Vercel App

            Quick start:
            1) Install deps: `pip install -r requirements.txt`
            2) Create lock: `apikit lock v1`
            3) Serve locally: `apikit serve`
               - Try: GET http://127.0.0.1:8000/v1/?name=Vercel
               - Try: POST http://127.0.0.1:8000/v1/add {"a":1,"b":2}

            Deploy on Vercel:
            - Commit `.superfastapi/locks/v1.lock.json` to git
            - `vercel` (CLI) or connect the repo in Vercel dashboard
            - Vercel uses `api/index.py` as the Serverless Function entrypoint
        ''').strip()+"\n"

        gitignore = dedent('''
            __pycache__/
            .venv/
            venv/
            .pytest_cache/
            .mypy_cache/
        ''').strip()+"\n"

        # Write files
        _write(out_dir/"app"/"api.py", app_py)
        _write(out_dir/"api"/"index.py", index_py)
        _write(out_dir/"vercel.json", vercel_json)
        _write(out_dir/"requirements.txt", reqs)
        _write(out_dir/"README.md", readme)
        _write(out_dir/".gitignore", gitignore)

        # Optional initial lock
        if lock_ver:
            v = lock_ver
            if not v.startswith('v'):
                v = 'v' + v
            from .lock import lock_command
            v_written = lock_command(v, scan_root=out_dir)
            lock_dir_path = out_dir/".superfastapi"/"locks"
            click.echo(f"Wrote initial lock {v_written} to {lock_dir_path}")

        click.echo(f"Scaffolded Vercel app at {out_dir}")
    except SuperFastAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
