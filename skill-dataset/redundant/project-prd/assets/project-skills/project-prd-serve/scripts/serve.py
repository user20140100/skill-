#!/usr/bin/env python3
"""Serve a read-only project-prd viewer without generating per-PRD pages."""

from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import NamedTuple, Optional, Sequence, Tuple, Type
from urllib.parse import parse_qs, quote, unquote, urlparse


MIN_PYTHON = (3, 9)
WORKSPACE_NAME = ".project-prd"
STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/markdown.js": "markdown.js",
    "/style.css": "style.css",
}
CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}
IMAGE_CONTENT_TYPES = {
    ".avif": "image/avif",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}
PRIVATE_WORKSPACE_PARTS = {"tools", ".history", ".analysis", "output"}
ASSET_RESPONSE_HEADERS = (
    ("X-Content-Type-Options", "nosniff"),
    (
        "Content-Security-Policy",
        "default-src 'none'; img-src data:; style-src 'unsafe-inline'; sandbox",
    ),
)
RESERVED_ROUTE_NAMES = {"api", "app.js", "index.html", "markdown.js", "style.css"}


class ProjectMount(NamedTuple):
    route_name: str
    project_root: Path


def _ensure_python() -> None:
    import sys

    if sys.version_info < MIN_PYTHON:
        required = ".".join(str(part) for part in MIN_PYTHON)
        current = ".".join(str(part) for part in sys.version_info[:3])
        raise SystemExit(f"project-prd-serve requires Python {required}+; current version is {current}")


def _safe_project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"项目根目录不存在：{root}")
    workspace = root / WORKSPACE_NAME
    manifest = workspace / "manifest.json"
    if not workspace.is_dir() or not manifest.is_file():
        raise ValueError("当前项目尚未完成 project-prd 初始化，缺少 .project-prd/manifest.json")
    return root


def _safe_route_name(raw: str) -> str:
    name = unicodedata.normalize("NFKC", raw.strip())
    if (
        not name
        or name in {".", ".."}
        or name.casefold() in RESERVED_ROUTE_NAMES
        or any(character in name for character in "/\\?#")
        or any(ord(character) < 32 or ord(character) == 127 for character in name)
    ):
        raise ValueError(f"无效的项目入口名称：{raw!r}")
    return name


def build_project_mounts(
    project_roots: list[str], named_projects: list[str]
) -> list[ProjectMount]:
    mounts: list[ProjectMount] = []
    for raw_root in project_roots:
        root = _safe_project_root(raw_root)
        mounts.append(ProjectMount(_safe_route_name(root.name), root))
    for spec in named_projects:
        route_name, separator, raw_root = spec.partition("=")
        if not separator or not route_name.strip() or not raw_root.strip():
            raise ValueError("--project 必须使用 <项目名>=<项目根目录> 格式")
        mounts.append(ProjectMount(_safe_route_name(route_name), _safe_project_root(raw_root)))
    if not mounts:
        raise ValueError("至少需要一个 --project-root 或 --project")

    seen: dict[str, str] = {}
    for mount in mounts:
        normalized = mount.route_name.casefold()
        if normalized in seen:
            raise ValueError(
                f"项目入口名称重复：{mount.route_name}；请使用 --project <别名>=<路径> 显式区分"
            )
        seen[normalized] = mount.route_name
    return mounts


def _within(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _has_private_workspace_part(parts: Sequence[str]) -> bool:
    return bool(parts) and parts[0] in PRIVATE_WORKSPACE_PARTS


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象：{path.name}")
    return value


def _frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)$", text[:4000])
    return match.group(1).strip().strip("`") if match else ""


def _prd_entries(workspace: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in sorted(workspace.rglob("*.md")):
        relative = path.relative_to(workspace)
        if (
            len(relative.parts) != 2
            or _has_private_workspace_part(relative.parts)
            or not path.is_file()
        ):
            continue
        text = path.read_text(encoding="utf-8")
        heading = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        entries.append({
            "path": relative.as_posix(),
            "name": path.stem,
            "title": heading,
            "category": relative.parent.as_posix() if relative.parent != Path(".") else "未分类",
            "complexity": _frontmatter_value(text, "complexity"),
            "prd_id": _frontmatter_value(text, "prd_id"),
            "product": _frontmatter_value(text, "product"),
        })
    return entries


def _project_name(root: Path, entries: list[dict[str, str]]) -> str:
    for entry in entries:
        product = entry.get("product", "").strip()
        if product:
            return product
    return root.name


def project_index_html(mounts: Sequence[ProjectMount]) -> str:
    items = "".join(
        f'<li><a href="/{quote(mount.route_name, safe="")}/">'
        f"{html.escape(mount.route_name)}</a></li>"
        for mount in mounts
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project PRD Viewer</title><style>
body{{font-family:system-ui,sans-serif;max-width:760px;margin:64px auto;padding:0 24px;color:#20284a;background:#f7f8fc}}
h1{{font-size:32px}}p{{color:#68708c}}ul{{list-style:none;padding:0;display:grid;gap:12px}}
a{{display:block;padding:18px 20px;border-radius:12px;background:#fff;color:#4145a5;text-decoration:none;box-shadow:0 8px 28px #25265b12}}
a:hover{{background:#eef0ff}}
</style></head><body><p>PROJECT PRD</p><h1>选择项目</h1><p>以下项目共享当前服务地址和端口。</p><ul>{items}</ul></body></html>"""


class ViewerHandler(BaseHTTPRequestHandler):
    projects: dict[str, ProjectMount]
    mounts: tuple[ProjectMount, ...]
    legacy_mount: Optional[ProjectMount]
    static_root: Path

    def _send(
        self,
        status: int,
        body: bytes,
        content_type: str,
        extra_headers: Sequence[Tuple[str, str]] = (),
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in extra_headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, value: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.PERMANENT_REDIRECT)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/" and self.legacy_mount is None:
                self._serve_project_index()
                return

            mount, local_path = self._resolve_mount(parsed.path)
            if mount is None:
                self._json({"error": "项目入口不存在"}, HTTPStatus.NOT_FOUND)
                return
            if local_path is None:
                self._redirect(f"/{quote(mount.route_name, safe='')}/")
                return
            self._serve_project(mount.project_root, local_path, parsed.query)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _resolve_mount(self, path: str) -> Tuple[Optional[ProjectMount], Optional[str]]:
        stripped = path.lstrip("/")
        first, separator, remainder = stripped.partition("/")
        mount = self.projects.get(unquote(first)) if first else None
        if mount is not None:
            return mount, f"/{remainder}" if separator else None
        if self.legacy_mount is not None:
            return self.legacy_mount, path
        return None, None

    def _serve_project(self, root: Path, path: str, query: str) -> None:
        workspace = root / WORKSPACE_NAME
        if path == "/api/summary":
            manifest = _read_json(workspace / "manifest.json")
            entries = _prd_entries(workspace)
            self._json({
                "project_name": _project_name(root, entries),
                "status": manifest.get("status"),
                "updated_at": manifest.get("updated_at"),
                "prd_count": manifest.get("prd_count", len(entries)),
                "function_point_count": manifest.get("function_point_count", 0),
                "format_version": manifest.get("format_version"),
            })
            return
        if path == "/api/prds":
            self._json({"items": _prd_entries(workspace)})
            return
        if path == "/api/index":
            index_path = workspace / "INDEX.md"
            if not index_path.is_file():
                self._json({"error": "INDEX.md 不存在"}, HTTPStatus.NOT_FOUND)
                return
            self._send(HTTPStatus.OK, index_path.read_bytes(), "text/markdown; charset=utf-8")
            return
        if path == "/api/prd":
            self._serve_prd(root, parse_qs(query).get("path", [""])[0])
            return
        if path == "/api/asset":
            self._serve_asset(root, parse_qs(query).get("path", [""])[0])
            return
        self._serve_static(path)

    def _serve_prd(self, project_root: Path, raw_path: str) -> None:
        workspace = project_root / WORKSPACE_NAME
        relative = Path(unquote(raw_path))
        candidate = (workspace / relative).resolve()
        if (
            not raw_path
            or relative.is_absolute()
            or not _within(workspace, candidate)
            or _has_private_workspace_part(candidate.relative_to(workspace).parts)
            or len(candidate.relative_to(workspace).parts) != 2
            or candidate.suffix != ".md"
            or not candidate.is_file()
        ):
            self._json({"error": "无效的 PRD 路径"}, HTTPStatus.NOT_FOUND)
            return
        self._send(HTTPStatus.OK, candidate.read_bytes(), "text/markdown; charset=utf-8")

    def _serve_asset(self, project_root: Path, raw_path: str) -> None:
        workspace = project_root / WORKSPACE_NAME
        relative = Path(unquote(raw_path))
        candidate = (workspace / relative).resolve()
        if (
            not raw_path
            or relative.is_absolute()
            or not _within(workspace, candidate)
            or _has_private_workspace_part(candidate.relative_to(workspace).parts)
            or candidate.suffix.lower() not in IMAGE_CONTENT_TYPES
            or not candidate.is_file()
        ):
            self._json({"error": "无效的图片资源路径"}, HTTPStatus.NOT_FOUND)
            return
        self._send(
            HTTPStatus.OK,
            candidate.read_bytes(),
            IMAGE_CONTENT_TYPES[candidate.suffix.lower()],
            ASSET_RESPONSE_HEADERS,
        )

    def _serve_project_index(self) -> None:
        page = project_index_html(self.mounts)
        self._send(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")

    def _serve_static(self, path: str) -> None:
        name = STATIC_FILES.get(path)
        if not name:
            self._json({"error": "资源不存在"}, HTTPStatus.NOT_FOUND)
            return
        candidate = (self.static_root / name).resolve()
        if not _within(self.static_root, candidate) or not candidate.is_file():
            self._json({"error": "Viewer 资源不存在"}, HTTPStatus.NOT_FOUND)
            return
        self._send(HTTPStatus.OK, candidate.read_bytes(), CONTENT_TYPES[candidate.suffix])

    def log_message(self, format: str, *args: object) -> None:
        print(f"[project-prd-serve] {format % args}")


def create_handler(mounts: list[ProjectMount], static_root: Path) -> Type[ViewerHandler]:
    legacy_mount = mounts[0] if len(mounts) == 1 else None
    return type("ProjectPrdViewerHandler", (ViewerHandler,), {
        "projects": {mount.route_name: mount for mount in mounts},
        "mounts": tuple(mounts),
        "legacy_mount": legacy_mount,
        "static_root": static_root.resolve(),
    })


def main() -> int:
    _ensure_python()
    parser = argparse.ArgumentParser(description="Serve a read-only project-prd viewer")
    parser.add_argument(
        "--project-root",
        action="append",
        default=[],
        help="项目根目录；可重复传入以在同一端口托管多个项目",
    )
    parser.add_argument(
        "--project",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="使用显式入口名称挂载项目；可重复传入",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        mounts = build_project_mounts(args.project_root, args.project)
        static_root = Path(__file__).resolve().parent.parent / "assets" / "web"
        handler = create_handler(mounts, static_root)
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except (OSError, ValueError) as exc:
        print(f"project-prd-serve: {exc}")
        return 2
    base_url = f"http://{args.host}:{args.port}"
    if len(mounts) == 1:
        print(f"project-prd viewer: {base_url}/")
        print(f"project route: {base_url}/{quote(mounts[0].route_name, safe='')}/")
    else:
        print(f"project-prd viewer: {base_url}/")
        for mount in mounts:
            print(f"project route [{mount.route_name}]: {base_url}/{quote(mount.route_name, safe='')}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nproject-prd viewer stopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
