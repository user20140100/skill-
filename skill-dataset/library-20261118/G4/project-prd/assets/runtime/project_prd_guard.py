#!/usr/bin/env python3
"""Integrity and CI guard installed into .project-prd/tools."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from project_prd_lib import (
    ProjectPrdError,
    check_integrity,
    classify_workspace_path,
    ensure_safe_project_root,
)


def _changed_files(root: Path, base_ref: str) -> list[str]:
    commands = (
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        ["git", "diff", "--name-only", base_ref, "HEAD"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    raise ProjectPrdError("无法计算 Git 变更范围：" + result.stderr.strip())


def _run_integrity(root: Path) -> None:
    valid, errors = check_integrity(root)
    if not valid:
        raise ProjectPrdError("\n".join(f"- {error}" for error in errors))


def _base_has_workspace(root: Path, base_ref: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{base_ref}:.project-prd/manifest.json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _changed_receipts(root: Path, changed: list[str]) -> list[dict]:
    receipts: list[dict] = []
    for raw_path in changed:
        if not raw_path.startswith(".project-prd/.history/") or not raw_path.endswith(".json"):
            continue
        path = root / raw_path
        if not path.is_file():
            raise ProjectPrdError(f"审计记录被删除或不存在：{raw_path}")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ProjectPrdError(f"审记记录 JSON 无效：{raw_path}") from exc
        if not isinstance(value, dict):
            raise ProjectPrdError(f"审记记录顶层必须是对象：{raw_path}")
        receipts.append(value)
    return receipts


def _run_ci(root: Path, base_ref: str) -> None:
    _run_integrity(root)
    changed = _changed_files(root, base_ref)
    protected_changes = [
        path for path in changed
        if path == ".project-prd/INDEX.md"
        or path == ".project-prd/manifest.json"
        or (
            path.startswith(".project-prd/")
            and classify_workspace_path(Path(path.removeprefix(".project-prd/")))
            in {"prd", "resource"}
        )
        or path.startswith(".agents/skills/project-prd-")
    ]
    runtime_changes = [
        path for path in changed
        if (
            path.startswith(".project-prd/")
            and classify_workspace_path(Path(path.removeprefix(".project-prd/"))) == "control"
            and path not in {".project-prd/manifest.json", ".project-prd/INDEX.md"}
            and not path.startswith(".project-prd/.history/")
        )
        or path.startswith(".agents/skills/project-prd-")
        or path == ".github/workflows/project-prd-guard.yml"
    ]
    base_has_workspace = _base_has_workspace(root, base_ref)
    if base_has_workspace and runtime_changes:
        raise ProjectPrdError(
            "已初始化项目不得在普通 PR 修改 project-prd 运行时/工作流："
            + ", ".join(runtime_changes)
        )
    receipts = _changed_receipts(root, changed)
    if protected_changes and not receipts:
        raise ProjectPrdError(
            "受保护文件发生变化，但没有 project-prd-edit/初始化审计记录："
            + ", ".join(protected_changes)
        )
    if base_has_workspace:
        authorized = [item for item in receipts if item.get("type") == "authorized-prd-edit"]
        if receipts and len(authorized) != len(receipts):
            raise ProjectPrdError("已初始化项目的变更只允许 authorized-prd-edit 审计记录")
        authorized_targets: set[str] = set()
        for item in authorized:
            changes = item.get("changes")
            receipt_changes = changes if isinstance(changes, list) else [item]
            for change in receipt_changes:
                if isinstance(change, dict) and isinstance(change.get("target"), str):
                    authorized_targets.add(f".project-prd/{change['target']}")
        changed_contents = [
            path for path in changed
            if path.startswith(".project-prd/")
            and classify_workspace_path(Path(path.removeprefix(".project-prd/")))
            in {"prd", "resource"}
        ]
        unmatched = [path for path in changed_contents if path not in authorized_targets]
        if unmatched:
            raise ProjectPrdError(
                "PRD/资源变更没有对应 target 的审计记录：" + ", ".join(unmatched)
            )
    elif protected_changes and not any(item.get("type") == "initialization" for item in receipts):
        raise ProjectPrdError("首次初始化必须包含 initialization 审计记录")
    print(f"project-prd CI guard PASS：检查 {len(changed)} 个变更文件")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("integrity", "ci"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--base-ref")
    args = parser.parse_args()
    try:
        root = ensure_safe_project_root(Path(args.project_root))
        if args.command == "integrity":
            _run_integrity(root)
            print("project-prd integrity PASS")
        else:
            if not args.base_ref:
                raise ProjectPrdError("ci 命令必须提供 --base-ref")
            _run_ci(root, args.base_ref)
        return 0
    except ProjectPrdError as exc:
        print(f"project-prd guard FAIL:\n{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
