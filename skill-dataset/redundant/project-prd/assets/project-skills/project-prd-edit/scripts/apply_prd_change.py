#!/usr/bin/env python3
"""The exclusive controlled writer for an initialized .project-prd baseline."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


def _find_root(start: Path) -> Path:
    current = start.expanduser().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".project-prd" / "manifest.json").is_file():
            return candidate
    raise RuntimeError("找不到包含 .project-prd/manifest.json 的项目根目录")


def _load_library(root: Path):
    tools_dir = root / ".project-prd" / "tools"
    sys.path.insert(0, str(tools_dir))
    import project_prd_lib  # pylint: disable=import-outside-toplevel
    return project_prd_lib


def _target_path(root: Path, raw_target: str, lib) -> tuple[Path, Path, str]:
    relative = Path(raw_target)
    if relative.is_absolute() or not relative.parts or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise lib.ProjectPrdError("target 包含不安全路径")
    target_kind = lib.classify_workspace_path(relative)
    if target_kind in {"control", "ignored"}:
        raise lib.ProjectPrdError(f"project-prd 功能或运行时文件不允许作为资源编辑：{relative}")
    workspace = (root / ".project-prd").resolve()
    unresolved_target = workspace / relative
    lib.ensure_no_symlink_path(root, unresolved_target)
    target = unresolved_target.resolve()
    if workspace not in target.parents:
        raise lib.ProjectPrdError("target 越出 .project-prd")
    return relative, target, target_kind


def _restore(path: Path, content: bytes | None) -> None:
    if content is None:
        path.unlink(missing_ok=True)
        parent = path.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def _load_changes(
    args: argparse.Namespace,
    root: Path,
    workspace: Path,
    tracked_files: set[str],
    lib,
) -> list[dict]:
    if args.changes:
        if any((args.operation, args.target, args.source, args.confirm_delete)):
            raise lib.ProjectPrdError("--changes 不得与单文件参数混用")
        changes_path = Path(args.changes).expanduser().resolve()
        if workspace.resolve() == changes_path or workspace.resolve() in changes_path.parents:
            raise lib.ProjectPrdError("变更清单必须位于 .project-prd 之外")
        try:
            raw_changes = json.loads(changes_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise lib.ProjectPrdError(f"无法读取变更清单：{exc}") from exc
        if not isinstance(raw_changes, list) or not raw_changes:
            raise lib.ProjectPrdError("变更清单必须是非空 JSON 数组")
    else:
        if not args.operation or not args.target:
            raise lib.ProjectPrdError("单文件模式必须提供 --operation 和 --target")
        raw_changes = [{
            "operation": args.operation,
            "target": args.target,
            "source": args.source,
            "confirm_delete": args.confirm_delete,
        }]

    changes: list[dict] = []
    seen_targets: set[str] = set()
    for index, raw_change in enumerate(raw_changes, start=1):
        if not isinstance(raw_change, dict):
            raise lib.ProjectPrdError(f"变更清单第 {index} 项必须是对象")
        operation = raw_change.get("operation")
        if operation not in {"create", "update", "delete"}:
            raise lib.ProjectPrdError(f"变更清单第 {index} 项 operation 无效")
        target_value = raw_change.get("target")
        if not isinstance(target_value, str):
            raise lib.ProjectPrdError(f"变更清单第 {index} 项缺少 target")
        relative, target, target_kind = _target_path(root, target_value, lib)
        relative_text = relative.as_posix()
        if relative_text in seen_targets:
            raise lib.ProjectPrdError(f"同一事务不得重复目标：{relative_text}")
        seen_targets.add(relative_text)
        if target.exists() and not target.is_file():
            raise lib.ProjectPrdError(f"目标不是普通文件：{relative}")
        before_content = target.read_bytes() if target.exists() else None
        untracked_resource = (
            target_kind == "resource"
            and before_content is not None
            and relative_text not in tracked_files
        )
        resource_adoption = untracked_resource and operation == "update"
        if operation == "create" and before_content is not None:
            raise lib.ProjectPrdError(f"create 目标已存在：{relative}")
        if operation in {"update", "delete"} and before_content is None:
            raise lib.ProjectPrdError(f"{operation} 目标不存在：{relative}")

        source_value = raw_change.get("source")
        if operation == "delete":
            if raw_change.get("confirm_delete") != "DELETE-PRD":
                raise lib.ProjectPrdError("删除 PRD/资源必须提供 confirm_delete=DELETE-PRD")
            if source_value:
                raise lib.ProjectPrdError("delete 不接受 source")
            new_content = None
        else:
            if not isinstance(source_value, str) or not source_value:
                raise lib.ProjectPrdError("create/update 必须提供 source 完整草稿")
            source = Path(source_value).expanduser().resolve()
            if workspace.resolve() == source or workspace.resolve() in source.parents:
                raise lib.ProjectPrdError("草稿必须位于 .project-prd 之外")
            if not source.is_file():
                raise lib.ProjectPrdError(f"草稿不存在：{source}")
            try:
                new_content = source.read_bytes()
            except OSError as exc:
                raise lib.ProjectPrdError(f"无法读取资源/PRD 草稿：{exc}") from exc
            new_text = None
            if target_kind == "prd":
                try:
                    new_text = new_content.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise lib.ProjectPrdError(f"PRD 草稿必须是 UTF-8 文本：{exc}") from exc
            new_metadata = (
                lib.validate_prd(new_text, relative, root)
                if target_kind == "prd" else None
            )
            if operation == "update" and before_content is not None and target_kind == "prd":
                old_metadata = lib.validate_prd(before_content.decode("utf-8"), relative, root)
                if new_metadata is not None and new_metadata["prd_id"] != old_metadata["prd_id"]:
                    raise lib.ProjectPrdError(
                        "update 必须保持 prd_id 稳定；替换功能身份请使用删除后新建"
                    )
            if before_content == new_content:
                raise lib.ProjectPrdError(f"PRD/资源内容没有变化：{relative}")
        changes.append({
            "operation": operation,
            "receipt_operation": "create" if resource_adoption else operation,
            "relative": relative,
            "target": target,
            "target_kind": target_kind,
            "before_content": before_content,
            "receipt_before_content": None if untracked_resource else before_content,
            "new_content": new_content,
        })
    return changes


def apply_change(args: argparse.Namespace) -> dict:
    root = _find_root(Path(args.project_root)) if args.project_root else _find_root(Path.cwd())
    lib = _load_library(root)
    root = lib.ensure_safe_project_root(root)
    workspace = root / ".project-prd"
    manifest_path = workspace / "manifest.json"
    manifest = lib.read_json(manifest_path)
    tracked_raw = manifest.get("files")
    tracked_files = set(tracked_raw) if isinstance(tracked_raw, dict) else set()
    if len(args.reason.strip()) < 4:
        raise lib.ProjectPrdError("reason 必须明确说明 PRD/资源变更原因")
    changes = _load_changes(
        args, root, workspace, tracked_files, lib
    )
    untracked_resources = {
        change["relative"].as_posix()
        for change in changes
        if change["target_kind"] == "resource"
        and change["before_content"] is not None
        and change["relative"].as_posix() not in tracked_files
    }
    valid, integrity_errors = lib.check_integrity(root, untracked_resources)
    if not valid:
        raise lib.ProjectPrdError(
            "编辑前完整性检查失败；拒绝把未知直接修改纳入新基线：\n"
            + "\n".join(f"- {error}" for error in integrity_errors)
        )
    index_path = workspace / "INDEX.md"
    index_before = index_path.read_bytes() if index_path.exists() else None
    manifest_before = manifest_path.read_bytes()

    history_path: Path | None = None
    try:
        for change in changes:
            if change["operation"] == "delete":
                change["target"].unlink()
                if not any(change["target"].parent.iterdir()):
                    change["target"].parent.rmdir()
            else:
                lib.atomic_write_bytes(change["target"], change["new_content"])

        lib.atomic_write_text(index_path, lib.generate_index(workspace))
        now = lib.utc_now()
        generation = int(manifest.get("edit_generation", 0)) + 1
        receipt_name = now.replace(":", "").replace("+00:00", "Z") + f"-{uuid.uuid4().hex[:8]}.json"
        history_path = workspace / ".history" / receipt_name
        receipt_changes = [{
            "operation": change["receipt_operation"],
            "target": change["relative"].as_posix(),
            "before_sha256": (
                lib.sha256_bytes(change["receipt_before_content"])
                if change["receipt_before_content"] is not None else None
            ),
            "after_sha256": (
                lib.sha256_bytes(change["new_content"])
                if change["new_content"] is not None else None
            ),
        } for change in changes]
        receipt = {
            "type": "authorized-prd-edit",
            "format_version": lib.FORMAT_VERSION,
            "generation": generation,
            "previous_receipt": manifest.get("last_authorized_edit"),
            "timestamp": now,
            "reason": args.reason.strip(),
            "changes": receipt_changes,
        }
        if len(receipt_changes) == 1:
            receipt.update(receipt_changes[0])
        lib.atomic_write_json(history_path, receipt)
        current_metadata = lib.collect_prd_metadata(workspace)
        complexity_counts = {
            level: sum(1 for item in current_metadata if item[1]["complexity"] == level)
            for level in ("simple", "standard", "complex")
        }
        updated_manifest = dict(manifest)
        updated_manifest.update({
            "updated_at": now,
            "edit_generation": generation,
            "prd_count": len(current_metadata),
            "function_point_count": sum(int(item[1]["function_point_count"]) for item in current_metadata),
            "candidate_count": sum(int(item[1]["candidate_count"]) for item in current_metadata),
            "matrix_count": sum(int(item[1]["matrix_count"]) for item in current_metadata),
            "diagram_count": sum(int(item[1]["diagram_count"]) for item in current_metadata),
            "interaction_count": sum(int(item[1]["interaction_count"]) for item in current_metadata),
            "positive_constraint_count": sum(int(item[1]["positive_constraint_count"]) for item in current_metadata),
            "negative_constraint_count": sum(int(item[1]["negative_constraint_count"]) for item in current_metadata),
            "exception_count": sum(int(item[1]["exception_count"]) for item in current_metadata),
            "behavior_count": sum(int(item[1]["behavior_count"]) for item in current_metadata),
            "complexity_counts": complexity_counts,
            "files": lib.compute_hashes(workspace),
            "last_authorized_edit": history_path.relative_to(workspace).as_posix(),
        })
        lib.atomic_write_json(manifest_path, updated_manifest)
        valid, integrity_errors = lib.check_integrity(root)
        if not valid:
            raise lib.ProjectPrdError("编辑后完整性失败：" + "; ".join(integrity_errors))
    except Exception:
        for change in reversed(changes):
            _restore(change["target"], change["before_content"])
        _restore(index_path, index_before)
        _restore(manifest_path, manifest_before)
        if history_path is not None:
            history_path.unlink(missing_ok=True)
        raise

    return {
        "status": "updated",
        "change_count": len(changes),
        "changes": [
            {"operation": change["operation"], "target": change["relative"].as_posix()}
            for change in changes
        ],
        "generation": generation,
        "audit_record": history_path.relative_to(root).as_posix() if history_path else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root")
    parser.add_argument("--operation", choices=("create", "update", "delete"))
    parser.add_argument("--target")
    parser.add_argument("--source")
    parser.add_argument("--changes")
    parser.add_argument("--reason", required=True)
    parser.add_argument("--confirm-delete")
    args = parser.parse_args()
    try:
        print(json.dumps(apply_change(args), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # Keep child skill usable even before library import.
        print(f"project-prd-edit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
