#!/usr/bin/env python3
"""Remove only artifacts whose project-prd ownership can be proven."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


FORMAT_VERSION = 3
OWNER_FILE = ".project-prd-owner.json"
MANAGED_START = "<!-- PROJECT_PRD_RULES_START -->"
MANAGED_END = "<!-- PROJECT_PRD_RULES_END -->"
SKILL_NAMES = ("project-prd-edit", "project-prd-verify", "project-prd-clear", "project-prd-serve")
EXPECTED_OWNER = {
    "owner": "project-prd",
    "format_version": FORMAT_VERSION,
    "installed_skills": list(SKILL_NAMES),
}


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法验证 project-prd 归属文件：{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"project-prd 归属文件格式无效：{path}")
    return value


def _ensure_within(root: Path, path: Path) -> None:
    resolved = path.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"受管路径通过符号链接越出项目：{path}")


def _safe_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    home = Path.home().resolve()
    broad_home_children = {"Desktop", "Documents", "Downloads", "Movies", "Music", "Pictures"}
    if (
        root == Path(root.anchor)
        or root == home
        or (root.parent == home and root.name in broad_home_children)
        or not root.is_dir()
    ):
        raise RuntimeError(f"拒绝使用不安全的项目根目录：{root}")
    workspace = root / ".project-prd"
    _ensure_within(root, workspace)
    if workspace.is_symlink() or not workspace.is_dir():
        raise RuntimeError("缺少可证明归属的 .project-prd 工作区")
    if _read_json(workspace / OWNER_FILE) != EXPECTED_OWNER:
        raise RuntimeError(".project-prd 工作区归属标记无效，拒绝删除")
    manifest_path = workspace / "manifest.json"
    initializing_path = workspace / ".initializing.json"
    if manifest_path.exists() == initializing_path.exists():
        raise RuntimeError("project-prd 必须恰好存在 manifest 或 initializing 状态之一")
    state = _read_json(manifest_path if manifest_path.exists() else initializing_path)
    expected_status = "complete" if manifest_path.exists() else "initializing"
    if state.get("format_version") != FORMAT_VERSION or state.get("status") != expected_status:
        raise RuntimeError("project-prd 状态文件不能证明工作区归属")
    return root


def _read_creation_flag(root: Path) -> bool:
    workspace = root / ".project-prd"
    path = workspace / "manifest.json"
    if not path.exists():
        path = workspace / ".initializing.json"
    return bool(_read_json(path).get("agents_file_created"))


def _preflight(root: Path) -> None:
    managed_paths = [
        root / ".project-prd",
        root / "AGENTS.md",
        root / ".github" / "workflows" / "project-prd-guard.yml",
        *(root / ".agents" / "skills" / name for name in SKILL_NAMES),
    ]
    for path in managed_paths:
        _ensure_within(root, path)
        if path.is_symlink():
            raise RuntimeError(f"受管路径不得是符号链接：{path}")

    agents_path = root / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text(encoding="utf-8")
        start_count = content.count(MANAGED_START)
        end_count = content.count(MANAGED_END)
        if start_count != end_count or start_count not in {0, 1}:
            raise RuntimeError("AGENTS.md 的 project-prd 受管标记缺失或重复，未执行任何删除")
        if start_count == 1 and content.find(MANAGED_START) > content.find(MANAGED_END):
            raise RuntimeError("AGENTS.md 的 project-prd 受管标记顺序无效，未执行任何删除")

    workflow = root / ".github" / "workflows" / "project-prd-guard.yml"
    if workflow.exists():
        first_line = workflow.read_text(encoding="utf-8").splitlines()[:1]
        if first_line != ["# Managed by project-prd. Remove only through project-prd-clear."]:
            raise RuntimeError("受管 GitHub workflow 标记无效，未执行任何删除")


def _atomic_write(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def _remove_exact(path: Path, root: Path) -> bool:
    _ensure_within(root, path)
    if path.is_file():
        path.unlink()
        return True
    if path.is_dir():
        shutil.rmtree(path)
        return True
    return False


def clear(root: Path) -> dict:
    _preflight(root)
    removed: list[str] = []
    preserved: list[str] = []
    agents_created = _read_creation_flag(root)

    agents_path = root / "AGENTS.md"
    if agents_path.is_file():
        content = agents_path.read_text(encoding="utf-8")
        pattern = re.compile(
            r"\n*" + re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END) + r"\n*",
            re.DOTALL,
        )
        if pattern.search(content):
            cleaned = pattern.sub("\n", content, count=1).strip()
            if agents_created and not cleaned:
                agents_path.unlink()
                removed.append("AGENTS.md（由 project-prd 创建）")
            else:
                _atomic_write(agents_path, cleaned + "\n" if cleaned else "")
                removed.append("AGENTS.md 中的 project-prd 受管块")
        else:
            preserved.append("AGENTS.md（未发现受管块）")

    workflow = root / ".github" / "workflows" / "project-prd-guard.yml"
    if _remove_exact(workflow, root):
        removed.append(str(workflow.relative_to(root)))

    for name in SKILL_NAMES:
        path = root / ".agents" / "skills" / name
        if _remove_exact(path, root):
            removed.append(str(path.relative_to(root)) + "/")

    workspace = root / ".project-prd"
    if _remove_exact(workspace, root):
        removed.append(".project-prd/")

    return {"status": "cleared", "removed": removed, "preserved": preserved}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    try:
        if args.confirm != "PROJECT-PRD-CLEAR":
            raise RuntimeError("确认令牌无效；必须是 PROJECT-PRD-CLEAR")
        root = _safe_root(args.project_root)
        print(json.dumps(clear(root), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"project-prd-clear: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
