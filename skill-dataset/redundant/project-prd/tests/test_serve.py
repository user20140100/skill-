from __future__ import annotations

import importlib.util
import json
import socket
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Optional, Tuple
from urllib.parse import quote


SKILL_ROOT = Path(__file__).resolve().parents[1]
SERVE_SCRIPT = (
    SKILL_ROOT
    / "assets"
    / "project-skills"
    / "project-prd-serve"
    / "scripts"
    / "serve.py"
)
STATIC_ROOT = SERVE_SCRIPT.parent.parent / "assets" / "web"

SPEC = importlib.util.spec_from_file_location("project_prd_serve", SERVE_SCRIPT)
assert SPEC and SPEC.loader
serve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve)


class ProjectPrdServeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_project(self, parent: Path, name: str, product: str) -> Path:
        project = parent / name
        workspace = project / ".project-prd"
        prd_dir = workspace / "功能"
        prd_dir.mkdir(parents=True)
        resource_dir = workspace / "res"
        resource_dir.mkdir()
        (resource_dir / "diagram.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><title>diagram</title></svg>',
            encoding="utf-8",
        )
        (resource_dir / "notes.txt").write_text("not an image", encoding="utf-8")
        analysis_dir = workspace / ".analysis"
        analysis_dir.mkdir()
        (analysis_dir / "hidden.svg").write_text("<svg></svg>", encoding="utf-8")
        private_dir = workspace / ".private"
        private_dir.mkdir()
        (private_dir / "hidden.svg").write_text("<svg></svg>", encoding="utf-8")
        (project / "outside.svg").write_text("<svg></svg>", encoding="utf-8")
        (workspace / "manifest.json").write_text(
            json.dumps({
                "status": "active",
                "prd_count": 1,
                "function_point_count": 1,
                "format_version": 3,
            }, ensure_ascii=False),
            encoding="utf-8",
        )
        (workspace / "INDEX.md").write_text(f"# {product} PRD\n", encoding="utf-8")
        (prd_dir / "功能一.md").write_text(
            f"---\nproduct: {product}\n---\n\n# {product} 功能一\n",
            encoding="utf-8",
        )
        return project

    def resolve(self, mounts: list[object], path: str) -> Tuple[Optional[object], Optional[str]]:
        handler = serve.create_handler(mounts, STATIC_ROOT)
        instance = handler.__new__(handler)
        return instance._resolve_mount(path)

    def request_response(
        self, mounts: list[object], target: str
    ) -> tuple[int, dict[str, str], bytes]:
        handler = serve.create_handler(mounts, STATIC_ROOT)
        client, server = socket.socketpair()
        try:
            client.settimeout(2)
            client.sendall(
                f"GET {target} HTTP/1.1\r\nHost: project-prd.test\r\nConnection: close\r\n\r\n".encode()
            )
            client.shutdown(socket.SHUT_WR)
            handler(server, ("local", 0), SimpleNamespace())
            server.shutdown(socket.SHUT_WR)
            response = bytearray()
            while True:
                chunk = client.recv(65536)
                if not chunk:
                    break
                response.extend(chunk)
        finally:
            client.close()
            server.close()
        header, body = bytes(response).split(b"\r\n\r\n", 1)
        header_lines = header.split(b"\r\n")
        status = int(header_lines[0].split()[1])
        headers = {
            key.decode("ascii").lower(): value.decode("ascii").strip()
            for line in header_lines[1:]
            for key, value in [line.split(b":", 1)]
        }
        return status, headers, body

    def request(self, mounts: list[object], target: str) -> tuple[int, str]:
        status, _, body = self.request_response(mounts, target)
        return status, body.decode("utf-8")

    def test_single_project_keeps_legacy_root_urls(self) -> None:
        project = self.create_project(self.root, "demo", "Demo")
        mounts = serve.build_project_mounts([str(project)], [])
        mount, local_path = self.resolve(mounts, "/api/summary")

        self.assertEqual(project.resolve(), mount.project_root)
        self.assertEqual("/api/summary", local_path)
        status, summary_body = self.request(mounts, "/api/summary")
        self.assertEqual(200, status)
        self.assertEqual("Demo", json.loads(summary_body)["project_name"])
        self.assertIn('href="./style.css"', (STATIC_ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertIn("const apiUrl", (STATIC_ROOT / "app.js").read_text(encoding="utf-8"))
        script_status, script_headers, script_body = self.request_response(
            mounts, "/demo/markdown.js"
        )
        self.assertEqual(200, script_status)
        self.assertEqual("text/javascript; charset=utf-8", script_headers["content-type"])
        self.assertIn(b"resolveImageSource", script_body)

    def test_multiple_projects_share_port_and_route_by_project_name(self) -> None:
        first = self.create_project(self.root, "alpha", "Alpha")
        second = self.create_project(self.root, "项目乙", "项目乙")
        mounts = serve.build_project_mounts([str(first), str(second)], [])

        landing = serve.project_index_html(mounts)
        self.assertIn('href="/alpha/"', landing)
        self.assertIn(f'href="/{quote("项目乙")}/"', landing)
        landing_status, landing_body = self.request(mounts, "/")
        self.assertEqual(200, landing_status)
        self.assertIn('href="/alpha/"', landing_body)
        alpha, alpha_path = self.resolve(mounts, "/alpha/api/summary")
        project_b, project_b_path = self.resolve(mounts, f"/{quote('项目乙')}/api/summary")
        self.assertEqual(first.resolve(), alpha.project_root)
        self.assertEqual("/api/summary", alpha_path)
        self.assertEqual(second.resolve(), project_b.project_root)
        self.assertEqual("/api/summary", project_b_path)
        self.assertEqual((None, None), self.resolve(mounts, "/api/summary"))
        self.assertEqual((alpha, None), self.resolve(mounts, "/alpha"))
        status, alpha_body = self.request(mounts, "/alpha/api/summary")
        self.assertEqual(200, status)
        self.assertEqual("Alpha", json.loads(alpha_body)["project_name"])
        project_b_status, project_b_body = self.request(
            mounts, f"/{quote('项目乙')}/api/summary"
        )
        self.assertEqual(200, project_b_status)
        self.assertEqual("项目乙", json.loads(project_b_body)["project_name"])
        missing_status, _ = self.request(mounts, "/api/summary")
        self.assertEqual(404, missing_status)
        redirect_status, _ = self.request(mounts, "/alpha")
        self.assertEqual(308, redirect_status)
        self.assertIn('src="./app.js"', (STATIC_ROOT / "index.html").read_text(encoding="utf-8"))

    def test_project_image_asset_is_served_with_content_type(self) -> None:
        project = self.create_project(self.root, "demo", "Demo")
        mounts = serve.build_project_mounts([str(project)], [])

        status, headers, body = self.request_response(
            mounts, "/demo/api/asset?path=res%2Fdiagram.svg"
        )

        self.assertEqual(200, status)
        self.assertEqual("image/svg+xml", headers["content-type"])
        self.assertEqual("nosniff", headers.get("x-content-type-options"))
        self.assertEqual(
            "default-src 'none'; img-src data:; style-src 'unsafe-inline'; sandbox",
            headers.get("content-security-policy"),
        )
        self.assertEqual(
            b'<svg xmlns="http://www.w3.org/2000/svg"><title>diagram</title></svg>',
            body,
        )
        hidden_status, hidden_headers, hidden_body = self.request_response(
            mounts, "/demo/api/asset?path=.private%2Fhidden.svg"
        )
        self.assertEqual(200, hidden_status)
        self.assertEqual("image/svg+xml", hidden_headers["content-type"])
        self.assertEqual(b"<svg></svg>", hidden_body)

    def test_project_image_asset_rejects_unsafe_or_unsupported_paths(self) -> None:
        project = self.create_project(self.root, "demo", "Demo")
        resource_link = project / ".project-prd" / "res" / "linked.svg"
        resource_link.symlink_to(project / "outside.svg")
        mounts = serve.build_project_mounts([str(project)], [])

        invalid_paths = (
            "../outside.svg",
            ".analysis/hidden.svg",
            "res/notes.txt",
            "res/linked.svg",
            "res/missing.svg",
        )
        for path in invalid_paths:
            with self.subTest(path=path):
                status, _ = self.request(mounts, f"/demo/api/asset?path={quote(path, safe='')}")
                self.assertEqual(404, status)

    def test_duplicate_directory_names_require_explicit_aliases(self) -> None:
        first = self.create_project(self.root / "one", "demo", "Demo One")
        second = self.create_project(self.root / "two", "demo", "Demo Two")

        with self.assertRaisesRegex(ValueError, "项目入口名称重复"):
            serve.build_project_mounts([str(first), str(second)], [])

        mounts = serve.build_project_mounts(
            [],
            [f"demo-one={first}", f"demo-two={second}"],
        )
        self.assertEqual(["demo-one", "demo-two"], [mount.route_name for mount in mounts])


if __name__ == "__main__":
    unittest.main()
