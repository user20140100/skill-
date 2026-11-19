#!/usr/bin/env python3
"""Prepare, update, finalize, and inspect a project-prd workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

from project_prd_lib import (
    FORMAT_VERSION,
    MANAGED_END,
    MANAGED_START,
    OWNER_FILE,
    ProjectPrdError,
    atomic_write_json,
    atomic_write_text,
    collect_prd_metadata,
    compute_control_hashes,
    compute_editable_hashes,
    compute_hashes,
    compute_prd_hashes,
    ensure_managed_path,
    ensure_no_symlink_path,
    ensure_safe_project_root,
    generate_index,
    parse_frontmatter,
    read_json,
    utc_now,
)


SKILL_NAMES = ("project-prd-edit", "project-prd-verify", "project-prd-clear", "project-prd-serve")
PROGRESS_SCHEMA_VERSION = 1
PROGRESS_STATES = {"pending", "running", "completed", "failed"}
ATTEMPT_STATES = {"running", "completed", "failed", "interrupted"}
TASK_PACKET_REQUIRED_FIELDS = {
    "task_id", "target_path", "prd_id", "product", "baseline_version", "date", "author",
    "category", "feature", "category_domain", "category_goal", "category_contract",
    "category_fit", "source_scope", "behavior_inventory", "complexity", "complexity_reasons",
    "decomposition_candidates", "decomposition_basis", "feature_points",
    "verification_evidence", "writer_path", "template_path", "acceptance_criteria",
}
TASK_PACKET_LIST_FIELDS = {
    "category_contract", "category_fit", "source_scope", "behavior_inventory",
    "complexity_reasons", "decomposition_candidates", "decomposition_basis", "feature_points",
    "verification_evidence", "acceptance_criteria",
}
AGENTS_RULES = f"""{MANAGED_START}
## Project PRD 产品需求基线保护规则

- `.project-prd/INDEX.md` 是项目逐功能 PRD 索引；执行代码修改、测试设计和 Review 前，必须读取相关 PRD。
- 所有生产代码修改和单元测试不得改变、削弱或违背 `.project-prd` 中逐 Feature Point 定义的功能描述、交互逻辑、正反向限制、异常处理与闭环关系，除非用户明确要求变更 PRD。
- `complex` PRD 必须维护覆盖全部 Feature Point 的 Mermaid 业务流程图；代码修改不得让流程图、规则矩阵与实际行为失配。
- 除全局 `project-prd` 首次初始化的 PRD 生成阶段，以及 project-prd 受控脚本对索引、清单和审计记录的写入外，Agent 不得直接增删改 `.project-prd` 中的任何内容。初始化完成后的 PRD 与普通资源文件新增、修改、删除只能调用项目级 skill `project-prd-edit`。
- 不得为了让实现通过而删除、放宽或改写 PRD 对应测试。发现实现与 PRD 冲突时，应修改实现或报告阻塞。
- 所有 Code Review 必须调用 `project-prd-verify`；完整性、语义映射或相关测试任一失败时，Review 结论不得为通过。
- `project-prd-clear` 是唯一允许清理 PRD 工作区与四个项目级 skill 的入口，执行前必须获得用户明确确认。
{MANAGED_END}"""


def _assets_root() -> Path:
    return Path(__file__).resolve().parent.parent / "assets"


def _state(root: Path) -> tuple[str, str]:
    workspace = root / ".project-prd"
    manifest_path = workspace / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = read_json(manifest_path)
        except ProjectPrdError as exc:
            return "partial", str(exc)
        if manifest.get("status") == "complete":
            return "initialized", "project-prd 已完成初始化"
        return "partial", "manifest 存在但状态不是 complete"

    managed_paths = [workspace]
    managed_paths.extend(root / ".agents" / "skills" / name for name in SKILL_NAMES)
    agents_path = root / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text(encoding="utf-8")
        if MANAGED_START in content or MANAGED_END in content:
            managed_paths.append(agents_path)
    workflow = root / ".github" / "workflows" / "project-prd-guard.yml"
    if workflow.exists():
        managed_paths.append(workflow)
    existing = [str(path.relative_to(root)) for path in managed_paths if path.exists()]
    if existing:
        return "partial", "发现残留受管路径：" + ", ".join(existing)
    return "clean", "项目尚未初始化"


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _managed_rules_block(content: str) -> str:
    start = content.find(MANAGED_START)
    end = content.find(MANAGED_END, start + len(MANAGED_START))
    if start < 0 or end < 0:
        raise ProjectPrdError("AGENTS.md 缺少完整 project-prd 受管块")
    if content.find(MANAGED_START, start + len(MANAGED_START)) >= 0:
        raise ProjectPrdError("AGENTS.md 存在重复 project-prd 受管块")
    if content.find(MANAGED_END, end + len(MANAGED_END)) >= 0:
        raise ProjectPrdError("AGENTS.md 存在重复 project-prd 受管块")
    return content[start : end + len(MANAGED_END)]


def _managed_resume_hashes(root: Path, github_workflow_installed: bool) -> dict[str, str]:
    workspace = root / ".project-prd"
    managed_roots = [
        workspace / "tools" / "project_prd_lib.py",
        workspace / "tools" / "project_prd_guard.py",
        workspace / "tools" / "project-prd-writer",
        *(root / ".agents" / "skills" / name for name in SKILL_NAMES),
    ]
    if github_workflow_installed:
        managed_roots.append(root / ".github" / "workflows" / "project-prd-guard.yml")
    hashes: dict[str, str] = {}
    for managed_root in managed_roots:
        if managed_root.is_symlink():
            raise ProjectPrdError(f"受管初始化资产不得是符号链接：{managed_root}")
        paths = [managed_root] if managed_root.is_file() else sorted(managed_root.rglob("*"))
        if not paths or (not managed_root.is_file() and not managed_root.is_dir()):
            raise ProjectPrdError(f"受管初始化资产缺失：{managed_root}")
        for path in paths:
            if path.is_symlink():
                raise ProjectPrdError(f"受管初始化资产不得包含符号链接：{path}")
            if path.is_file():
                if "__pycache__" in path.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
                    continue
                relative = path.relative_to(root).as_posix()
                hashes[relative] = _sha256_bytes(path.read_bytes())
    agents_path = root / "AGENTS.md"
    block = _managed_rules_block(agents_path.read_text(encoding="utf-8"))
    hashes["AGENTS.md#project-prd"] = _sha256_bytes(block.encode("utf-8"))
    return dict(sorted(hashes.items()))


def _validate_progress_shape(progress: object) -> list[dict[str, object]]:
    if not isinstance(progress, dict) or progress.get("schema_version") != PROGRESS_SCHEMA_VERSION:
        raise ProjectPrdError("progress.json schema_version 无效")
    raw_tasks = progress.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ProjectPrdError("progress.json.tasks 必须是数组")
    tasks: list[dict[str, object]] = []
    task_ids: set[str] = set()
    normalized_targets: set[str] = set()
    for index, raw_task in enumerate(raw_tasks, start=1):
        if not isinstance(raw_task, dict):
            raise ProjectPrdError(f"progress.json 第 {index} 个任务不是对象")
        required = {"task_id", "target_path", "agent_id", "status", "attempt", "error", "attempts"}
        if not required.issubset(raw_task):
            missing = ", ".join(sorted(required - set(raw_task)))
            raise ProjectPrdError(f"progress.json 第 {index} 个任务缺少字段：{missing}")
        task_id = raw_task["task_id"]
        target_path = raw_task["target_path"]
        status = raw_task["status"]
        attempt = raw_task["attempt"]
        attempts = raw_task["attempts"]
        if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", task_id):
            raise ProjectPrdError(f"progress.json 第 {index} 个 task_id 无效")
        if task_id in task_ids:
            raise ProjectPrdError(f"progress.json task_id 重复：{task_id}")
        task_ids.add(task_id)
        if not isinstance(target_path, str):
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 target_path 无效")
        relative = Path(target_path)
        if (
            relative.is_absolute()
            or len(relative.parts) != 2
            or relative.suffix.lower() != ".md"
            or any(part in {"", ".", ".."} or part.startswith(".") for part in relative.parts)
        ):
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 target_path 必须是两级 PRD 路径")
        normalized_target = unicodedata.normalize("NFKC", relative.as_posix()).casefold()
        if normalized_target in normalized_targets:
            raise ProjectPrdError(f"progress.json target_path 重复：{target_path}")
        normalized_targets.add(normalized_target)
        if status not in PROGRESS_STATES:
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 status 无效")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 0:
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 attempt 无效")
        if raw_task["error"] is not None and not isinstance(raw_task["error"], str):
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 error 无效")
        if not isinstance(attempts, list) or len(attempts) != attempt:
            raise ProjectPrdError(f"progress.json 任务 {task_id} 的 attempts 与 attempt 不一致")
        attempt_agents: set[str] = set()
        for attempt_index, raw_attempt in enumerate(attempts, start=1):
            if not isinstance(raw_attempt, dict):
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的第 {attempt_index} 次尝试无效")
            if set(raw_attempt) != {"attempt", "agent_id", "status", "error"}:
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的尝试字段无效")
            attempt_agent = raw_attempt["agent_id"]
            if (
                raw_attempt["attempt"] != attempt_index
                or not isinstance(attempt_agent, str)
                or not attempt_agent.strip()
                or raw_attempt["status"] not in ATTEMPT_STATES
                or (raw_attempt["error"] is not None and not isinstance(raw_attempt["error"], str))
            ):
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的第 {attempt_index} 次尝试无效")
            if attempt_agent in attempt_agents:
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的重试必须使用全新子代理")
            if attempt_index < len(attempts) and raw_attempt["status"] == "running":
                raise ProjectPrdError(f"progress.json 任务 {task_id} 存在未关闭的历史 running 尝试")
            attempt_agents.add(attempt_agent)
        if status == "pending":
            if attempt != 0 or raw_task["agent_id"] is not None:
                raise ProjectPrdError(f"pending 任务 {task_id} 不得绑定子代理")
        else:
            if not attempts or raw_task["agent_id"] != attempts[-1]["agent_id"]:
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的当前 agent_id 无效")
            expected_status = "failed" if attempts[-1]["status"] == "interrupted" else attempts[-1]["status"]
            if status != expected_status:
                raise ProjectPrdError(f"progress.json 任务 {task_id} 的状态与最后一次尝试不一致")
            if status == "completed" and (
                raw_task["error"] is not None or attempts[-1]["error"] is not None
            ):
                raise ProjectPrdError(f"completed 任务 {task_id} 不得保留错误")
        tasks.append(raw_task)
    return tasks


def _load_task_packet(workspace: Path, task: dict[str, object]) -> dict[str, object]:
    task_id = str(task["task_id"])
    target = str(task["target_path"])
    target_file = workspace / target
    ensure_no_symlink_path(workspace, target_file)
    if task["status"] == "completed" and not target_file.is_file():
        raise ProjectPrdError(f"completed 子代理任务缺少目标 PRD：{target}")
    task_root = workspace / ".analysis" / "tasks"
    ensure_no_symlink_path(workspace, task_root)
    if not task_root.is_dir():
        raise ProjectPrdError("逐 PRD 子代理任务包目录不存在")
    packet = task_root / f"{task_id}.md"
    ensure_no_symlink_path(workspace, packet)
    if not packet.is_file():
        raise ProjectPrdError(f"子代理任务包不存在或不安全：{packet}")
    packet_metadata = parse_frontmatter(packet.read_text(encoding="utf-8"))
    missing_fields = sorted(TASK_PACKET_REQUIRED_FIELDS - set(packet_metadata))
    if missing_fields:
        raise ProjectPrdError(f"子代理任务包 {task_id} 缺少字段：{', '.join(missing_fields)}")
    for field in TASK_PACKET_REQUIRED_FIELDS:
        value = packet_metadata[field]
        if field in TASK_PACKET_LIST_FIELDS:
            if not isinstance(value, list) or not value or any(not str(item).strip() for item in value):
                raise ProjectPrdError(f"子代理任务包 {task_id} 的 {field} 必须是非空列表")
        elif not isinstance(value, str) or not value.strip():
            raise ProjectPrdError(f"子代理任务包 {task_id} 的 {field} 不能为空")
    fixed_values = {
        "task_id": task_id,
        "target_path": target,
        "writer_path": ".project-prd/tools/project-prd-writer/SKILL.md",
        "template_path": ".project-prd/tools/project-prd-writer/references/prd-template.md",
    }
    for field, expected in fixed_values.items():
        if packet_metadata[field] != expected:
            raise ProjectPrdError(f"子代理任务包 {task_id} 的 {field} 与任务进度不一致")
    for source_entry in packet_metadata["source_scope"]:
        source_text = str(source_entry).split(":", 1)[0].strip()
        source_relative = Path(source_text)
        if (
            not source_text
            or source_relative.is_absolute()
            or any(part in {"", ".", ".."} or part.startswith(".") for part in source_relative.parts)
        ):
            raise ProjectPrdError(f"子代理任务包 {task_id} 的 source_scope 路径无效")
        source_path = workspace.parent / source_relative
        ensure_no_symlink_path(workspace.parent, source_path)
        if not source_path.exists():
            raise ProjectPrdError(f"子代理任务包 {task_id} 的 source_scope 不存在：{source_text}")
    return packet_metadata


def _validate_completed_prd_tasks(
    workspace: Path, prd_metadata: list[tuple[Path, dict[str, object]]]
) -> dict[str, object]:
    progress = read_json(workspace / ".analysis" / "progress.json")
    tasks = _validate_progress_shape(progress)
    if not tasks:
        raise ProjectPrdError("没有逐 PRD 子代理任务，禁止 finalize")
    incomplete = [str(task["task_id"]) for task in tasks if task["status"] != "completed"]
    if incomplete:
        raise ProjectPrdError("存在未完成的逐 PRD 子代理任务，禁止 finalize：" + ", ".join(incomplete))
    metadata_by_target = {relative.as_posix(): metadata for relative, metadata in prd_metadata}
    task_targets = {str(task["target_path"]) for task in tasks}
    if task_targets != set(metadata_by_target):
        missing = sorted(set(metadata_by_target) - task_targets)
        extra = sorted(task_targets - set(metadata_by_target))
        raise ProjectPrdError(f"子代理任务与 PRD 文件不一致；缺少={missing}，多余={extra}")
    all_agents: set[str] = set()
    for task in tasks:
        task_id = str(task["task_id"])
        for attempt in task["attempts"]:  # type: ignore[union-attr]
            agent_id = str(attempt["agent_id"])
            if agent_id in all_agents:
                raise ProjectPrdError(f"同一子代理不得处理多份 PRD 或重复重试：{agent_id}")
            all_agents.add(agent_id)
        packet_metadata = _load_task_packet(workspace, task)
        target = str(task["target_path"])
        prd = metadata_by_target[target]
        expected_values = {
            "task_id": task_id,
            "target_path": target,
            "prd_id": str(prd["prd_id"]),
            "product": str(prd["product"]),
            "baseline_version": str(prd["baseline_version"]),
            "date": str(prd["date"]),
            "author": str(prd["author"]),
            "category": str(prd["category"]),
            "feature": str(prd["feature"]),
            "category_domain": str(prd["category_domain"]),
            "category_goal": str(prd["category_goal"]),
            "complexity": str(prd["complexity"]),
        }
        for field, expected in expected_values.items():
            if packet_metadata[field] != expected:
                raise ProjectPrdError(f"子代理任务包 {task_id} 的 {field} 与目标 PRD 不一致")
    covered_targets = sorted(task_targets & set(metadata_by_target))
    uncovered_targets = sorted(task_targets - set(covered_targets))
    total = len(tasks)
    covered = len(covered_targets)
    return {
        "covered": covered,
        "total": total,
        "uncovered": uncovered_targets,
        "rate_percent": round((covered / total) * 100, 2),
    }


def _validate_resumable_initialization(root: Path) -> None:
    workspace = root / ".project-prd"
    if not workspace.is_dir() or workspace.is_symlink() or (workspace / "manifest.json").exists():
        raise ProjectPrdError("初始化工作区缺失、是符号链接或已存在 manifest")
    required_files = (
        workspace / OWNER_FILE,
        workspace / ".initializing.json",
        workspace / "tools" / "project_prd_lib.py",
        workspace / "tools" / "project_prd_guard.py",
        workspace / "tools" / "project-prd-writer" / "SKILL.md",
    )
    required_skills = tuple(root / ".agents" / "skills" / name for name in SKILL_NAMES)
    if any(not path.is_file() or path.is_symlink() for path in required_files):
        raise ProjectPrdError("初始化现场缺少安全的 owner、状态或 runtime 文件")
    if any(not path.is_dir() or path.is_symlink() for path in required_skills):
        raise ProjectPrdError("初始化现场缺少安全的项目级 skill")
    agents_path = root / "AGENTS.md"
    if not agents_path.is_file() or agents_path.is_symlink():
        raise ProjectPrdError("初始化现场缺少安全的 AGENTS.md")
    agents_text = agents_path.read_text(encoding="utf-8")
    if agents_text.count(MANAGED_START) != 1 or agents_text.count(MANAGED_END) != 1:
        raise ProjectPrdError("AGENTS.md 的 project-prd 受管标记缺失或重复")
    owner = read_json(workspace / OWNER_FILE)
    initializing = read_json(workspace / ".initializing.json")
    analysis_path = workspace / ".analysis"
    if not analysis_path.is_dir() or analysis_path.is_symlink():
        raise ProjectPrdError("初始化分析目录缺失或不安全")
    tasks_path = analysis_path / "tasks"
    ensure_no_symlink_path(workspace, tasks_path)
    if not tasks_path.is_dir():
        raise ProjectPrdError("逐 PRD 子代理任务包目录不存在")
    progress_path = analysis_path / "progress.json"
    ensure_no_symlink_path(workspace, progress_path)
    if not progress_path.is_file():
        raise ProjectPrdError("逐 PRD 子代理进度文件不存在")
    tasks = _validate_progress_shape(read_json(progress_path))
    for task in tasks:
        _load_task_packet(workspace, task)
    if not isinstance(owner, dict) or set(owner) != {"owner", "format_version", "installed_skills"}:
        raise ProjectPrdError("project-prd owner 结构无效")
    required_initializing = {
        "format_version", "status", "prepared_at", "agents_file_created",
        "github_workflow_installed", "installed_skills", "managed_resume_hashes",
    }
    if not isinstance(initializing, dict) or set(initializing) != required_initializing:
        raise ProjectPrdError("project-prd initializing 结构无效")
    if (
        owner.get("owner") != "project-prd"
        or owner.get("format_version") != FORMAT_VERSION
        or owner.get("installed_skills") != list(SKILL_NAMES)
        or initializing.get("status") != "initializing"
        or initializing.get("format_version") != FORMAT_VERSION
        or not isinstance(initializing.get("prepared_at"), str)
        or not isinstance(initializing.get("agents_file_created"), bool)
        or not isinstance(initializing.get("github_workflow_installed"), bool)
        or initializing.get("installed_skills") != list(SKILL_NAMES)
        or not isinstance(initializing.get("managed_resume_hashes"), dict)
    ):
        raise ProjectPrdError("project-prd owner 或 initializing 字段无效")
    current_hashes = _managed_resume_hashes(
        root, bool(initializing["github_workflow_installed"])
    )
    if current_hashes != initializing["managed_resume_hashes"]:
        raise ProjectPrdError("受管初始化资产指纹不一致")


def _is_resumable_initialization(root: Path) -> bool:
    try:
        _validate_resumable_initialization(root)
        return True
    except (OSError, UnicodeError, ProjectPrdError):
        return False


def _status_payload(root: Path) -> dict[str, object]:
    status, message = _state(root)
    resumable = status == "partial" and _is_resumable_initialization(root)
    recovery_action = "resume"
    if not resumable:
        recovery_action = {"clean": "prepare", "initialized": "none"}.get(status, "clear")
    return {
        "status": status,
        "message": message,
        "resumable": resumable,
        "recovery_action": recovery_action,
    }


def _is_github_repository(root: Path) -> bool:
    if (root / ".github").exists():
        return True
    config = root / ".git" / "config"
    if config.is_file():
        return "github.com" in config.read_text(encoding="utf-8", errors="ignore")
    return False


def _install_agents_rules(root: Path) -> bool:
    path = root / "AGENTS.md"
    created = not path.exists()
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if MANAGED_START in current or MANAGED_END in current:
        raise ProjectPrdError("AGENTS.md 已有不完整或重复的 project-prd 受管块")
    prefix = current.rstrip()
    combined = f"{prefix}\n\n{AGENTS_RULES}\n" if prefix else f"{AGENTS_RULES}\n"
    atomic_write_text(path, combined)
    return created


def prepare(root: Path) -> None:
    status, message = _state(root)
    if status != "clean":
        raise ProjectPrdError(f"不能初始化：{message}。请先使用 project-prd-clear。")

    workspace = root / ".project-prd"
    skills_root = root / ".agents" / "skills"
    assets = _assets_root()
    created_paths: list[Path] = []
    agents_created = False
    workflow_installed = False
    workflow = root / ".github" / "workflows" / "project-prd-guard.yml"
    managed_targets = [workspace, root / "AGENTS.md", workflow]
    managed_targets.extend(skills_root / name for name in SKILL_NAMES)
    for target in managed_targets:
        ensure_managed_path(root, target)
    try:
        workspace.mkdir(parents=True, exist_ok=False)
        created_paths.append(workspace)
        (workspace / ".history").mkdir()
        (workspace / "tools").mkdir()
        (workspace / ".analysis" / "tasks").mkdir(parents=True)
        atomic_write_json(
            workspace / ".analysis" / "progress.json",
            {"schema_version": PROGRESS_SCHEMA_VERSION, "tasks": []},
        )
        atomic_write_json(workspace / OWNER_FILE, {
            "owner": "project-prd",
            "format_version": FORMAT_VERSION,
            "installed_skills": list(SKILL_NAMES),
        })
        initializing = {
            "format_version": FORMAT_VERSION,
            "status": "initializing",
            "prepared_at": utc_now(),
            "agents_file_created": False,
            "github_workflow_installed": False,
            "installed_skills": list(SKILL_NAMES),
        }
        atomic_write_json(workspace / ".initializing.json", initializing)

        for name in SKILL_NAMES:
            source = assets / "project-skills" / name
            target = skills_root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
            created_paths.append(target)

        shutil.copy2(Path(__file__).resolve().parent / "project_prd_lib.py", workspace / "tools")
        shutil.copy2(assets / "runtime" / "project_prd_guard.py", workspace / "tools")
        shutil.copytree(
            assets / "internal-skills" / "project-prd-writer",
            workspace / "tools" / "project-prd-writer",
        )
        atomic_write_text(workspace / ".gitignore", ".analysis/\noutput/\n__pycache__/\n*.pyc\n")

        agents_created = _install_agents_rules(root)
        if agents_created:
            created_paths.append(root / "AGENTS.md")

        if _is_github_repository(root):
            workflow.parent.mkdir(parents=True, exist_ok=True)
            if workflow.exists():
                raise ProjectPrdError(f"拒绝覆盖已有 workflow：{workflow}")
            shutil.copy2(assets / "github" / "project-prd-guard.yml", workflow)
            created_paths.append(workflow)
            workflow_installed = True

        initializing.update({
            "agents_file_created": agents_created,
            "github_workflow_installed": workflow_installed,
            "managed_resume_hashes": _managed_resume_hashes(root, workflow_installed),
        })
        atomic_write_json(workspace / ".initializing.json", initializing)
    except Exception:
        for path in reversed(created_paths):
            if path.is_symlink() or path.is_file():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                shutil.rmtree(path)
        if not agents_created:
            agents_path = root / "AGENTS.md"
            if agents_path.exists():
                content = agents_path.read_text(encoding="utf-8")
                start = content.find(MANAGED_START)
                end = content.find(MANAGED_END)
                if start >= 0 and end >= start:
                    cleaned = (content[:start] + content[end + len(MANAGED_END):]).strip()
                    atomic_write_text(agents_path, cleaned + "\n" if cleaned else "")
        raise

    print(json.dumps({
        "status": "prepared",
        "project_root": str(root),
        "installed_skills": list(SKILL_NAMES),
        "github_workflow_installed": workflow_installed,
    }, ensure_ascii=False, indent=2))


def _update_skill_install_dir(root: Path, owner: dict, manifest: dict) -> tuple[str, Path]:
    relative = owner.get("skill_install_dir") or manifest.get("skill_install_dir") or ".agents/skills"
    relative_path = Path(str(relative)) if isinstance(relative, str) else Path()
    if (
        not isinstance(relative, str)
        or not relative
        or relative_path.is_absolute()
        or any(part in {"", ".", ".."} for part in relative_path.parts)
    ):
        raise ProjectPrdError("skill_install_dir 无效，拒绝 update")
    target = root / relative_path
    ensure_no_symlink_path(root, target)
    return relative, target


def _validate_update_owner(owner: dict) -> None:
    installed = owner.get("installed_skills")
    allowed = {*SKILL_NAMES, "project-prd-add"}
    required = {"project-prd-edit", "project-prd-verify", "project-prd-clear"}
    if (
        owner.get("owner") != "project-prd"
        or owner.get("format_version") != FORMAT_VERSION
        or not isinstance(installed, list)
        or any(not isinstance(name, str) for name in installed)
        or not required.issubset(installed)
        or not set(installed).issubset(allowed)
    ):
        raise ProjectPrdError("project-prd 工作区归属标记无效，拒绝 update")


def _ensure_copy_target_safe(root: Path, source: Path, target: Path) -> None:
    ensure_no_symlink_path(root, target)
    if not target.exists():
        return
    for source_path in source.rglob("*"):
        ensure_no_symlink_path(root, target / source_path.relative_to(source))


def update_project_skills(root: Path) -> None:
    """Upgrade managed project skills/runtime without regenerating PRDs."""
    workspace = root / ".project-prd"
    ensure_no_symlink_path(root, workspace)
    manifest_path = workspace / "manifest.json"
    if not manifest_path.is_file():
        status, message = _state(root)
        raise ProjectPrdError(f"不能 update；当前状态 {status}：{message}")
    manifest = read_json(manifest_path)
    if manifest.get("status") != "complete":
        raise ProjectPrdError("只能在已完成初始化的项目中执行 update")
    tracked_files = manifest.get("files")
    if not isinstance(tracked_files, dict):
        raise ProjectPrdError("manifest.files 无效，拒绝 update")
    current_update_generation = manifest.get("skill_update_generation", 0)
    if (
        isinstance(current_update_generation, bool)
        or not isinstance(current_update_generation, int)
        or current_update_generation < 0
    ):
        raise ProjectPrdError("manifest.skill_update_generation 必须是非负整数")

    owner_path = workspace / OWNER_FILE
    owner = read_json(owner_path)
    _validate_update_owner(owner)
    relative_skill_dir, skill_dir = _update_skill_install_dir(root, owner, manifest)
    assets = _assets_root()
    for name in SKILL_NAMES:
        source = assets / "project-skills" / name
        target = skill_dir / name
        _ensure_copy_target_safe(root, source, target)
    runtime_targets = (
        (Path(__file__).resolve().parent / "project_prd_lib.py", workspace / "tools" / "project_prd_lib.py"),
        (assets / "runtime" / "project_prd_guard.py", workspace / "tools" / "project_prd_guard.py"),
    )
    for _, target in runtime_targets:
        ensure_no_symlink_path(root, target)

    for name in SKILL_NAMES:
        shutil.copytree(assets / "project-skills" / name, skill_dir / name, dirs_exist_ok=True)
    for source, target in runtime_targets:
        shutil.copy2(source, target)
    atomic_write_json(owner_path, {
        "owner": "project-prd",
        "format_version": FORMAT_VERSION,
        "installed_skills": list(SKILL_NAMES),
    })

    now = utc_now()
    update_generation = current_update_generation + 1
    audit_name = now.replace(":", "").replace("+00:00", "Z") + f"-{update_generation:04d}.json"
    history_path = workspace / ".history" / f"skill-update-{audit_name}"
    ensure_no_symlink_path(root, history_path)
    atomic_write_json(history_path, {
        "type": "skill-update",
        "format_version": FORMAT_VERSION,
        "timestamp": now,
        "installed_skills": list(SKILL_NAMES),
        "skill_install_dir": relative_skill_dir,
    })

    last_edit = manifest.get("last_authorized_edit")
    if isinstance(last_edit, str):
        last_edit_path = workspace / last_edit
        if last_edit_path.is_file():
            last_edit_receipt = read_json(last_edit_path)
            if last_edit_receipt.get("type") in {"initialization", "authorized-prd-edit"}:
                timestamp = last_edit_receipt.get("timestamp")
                if isinstance(timestamp, str):
                    manifest["updated_at"] = timestamp
    control_hashes = compute_control_hashes(workspace)
    preserved_hashes = {
        path: digest for path, digest in tracked_files.items() if path not in control_hashes
    }
    manifest.update({
        "format_version": FORMAT_VERSION,
        "installed_skills": list(SKILL_NAMES),
        "skill_install_dir": relative_skill_dir,
        "skill_updated_at": now,
        "skill_update_generation": update_generation,
        "last_authorized_skill_update": history_path.relative_to(root).as_posix(),
        "files": dict(sorted({**preserved_hashes, **control_hashes}.items())),
    })
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({
        "status": "updated",
        "project_root": str(root),
        "installed_skills": list(SKILL_NAMES),
        "skill_install_dir": relative_skill_dir,
        "runtime_updated": True,
        "audit_record": history_path.relative_to(root).as_posix(),
    }, ensure_ascii=False, indent=2))


def finalize(root: Path) -> None:
    workspace = root / ".project-prd"
    initializing_path = workspace / ".initializing.json"
    if not initializing_path.exists():
        status, message = _state(root)
        raise ProjectPrdError(f"不能 finalize；当前状态 {status}：{message}")
    initializing = read_json(initializing_path)
    if not isinstance(initializing, dict) or initializing.get("status") != "initializing":
        raise ProjectPrdError("初始化状态文件无效")
    _validate_resumable_initialization(root)

    metadata = collect_prd_metadata(workspace)
    feature_coverage = _validate_completed_prd_tasks(workspace, metadata)
    atomic_write_text(workspace / "INDEX.md", generate_index(workspace))
    now = utc_now()
    function_point_count = sum(int(item[1]["function_point_count"]) for item in metadata)
    candidate_count = sum(int(item[1]["candidate_count"]) for item in metadata)
    matrix_count = sum(int(item[1]["matrix_count"]) for item in metadata)
    diagram_count = sum(int(item[1]["diagram_count"]) for item in metadata)
    interaction_count = sum(int(item[1]["interaction_count"]) for item in metadata)
    positive_constraint_count = sum(int(item[1]["positive_constraint_count"]) for item in metadata)
    negative_constraint_count = sum(int(item[1]["negative_constraint_count"]) for item in metadata)
    exception_count = sum(int(item[1]["exception_count"]) for item in metadata)
    behavior_count = sum(int(item[1]["behavior_count"]) for item in metadata)
    complexity_counts = {
        level: sum(1 for item in metadata if item[1]["complexity"] == level)
        for level in ("simple", "standard", "complex")
    }
    history_path = workspace / ".history" / "initialization.json"
    history = {
        "type": "initialization",
        "format_version": FORMAT_VERSION,
        "generation": 0,
        "timestamp": now,
        "prd_count": len(metadata),
        "function_point_count": function_point_count,
        "candidate_count": candidate_count,
        "matrix_count": matrix_count,
        "diagram_count": diagram_count,
        "interaction_count": interaction_count,
        "positive_constraint_count": positive_constraint_count,
        "negative_constraint_count": negative_constraint_count,
        "exception_count": exception_count,
        "behavior_count": behavior_count,
        "complexity_counts": complexity_counts,
        "feature_coverage": feature_coverage,
        "prd_ids": [item[1]["prd_id"] for item in metadata],
        "prd_files": compute_prd_hashes(workspace),
        "editable_files": compute_editable_hashes(workspace),
    }
    atomic_write_json(history_path, history)
    manifest = {
        "format_version": FORMAT_VERSION,
        "status": "complete",
        "initialized_at": now,
        "updated_at": now,
        "edit_generation": 0,
        "agents_file_created": bool(initializing.get("agents_file_created")),
        "github_workflow_installed": bool(initializing.get("github_workflow_installed")),
        "installed_skills": list(SKILL_NAMES),
        "prd_count": len(metadata),
        "function_point_count": function_point_count,
        "candidate_count": candidate_count,
        "matrix_count": matrix_count,
        "diagram_count": diagram_count,
        "interaction_count": interaction_count,
        "positive_constraint_count": positive_constraint_count,
        "negative_constraint_count": negative_constraint_count,
        "exception_count": exception_count,
        "behavior_count": behavior_count,
        "complexity_counts": complexity_counts,
        "files": compute_hashes(workspace),
        "last_authorized_edit": ".history/initialization.json",
    }
    atomic_write_json(workspace / "manifest.json", manifest)
    initializing_path.unlink()
    print(json.dumps({
        "status": "initialized",
        "project_root": str(root),
        "prd_count": len(metadata),
        "category_count": len({item[1]["category"] for item in metadata}),
        "function_point_count": function_point_count,
        "candidate_count": candidate_count,
        "matrix_count": matrix_count,
        "diagram_count": diagram_count,
        "interaction_count": interaction_count,
        "positive_constraint_count": positive_constraint_count,
        "negative_constraint_count": negative_constraint_count,
        "exception_count": exception_count,
        "behavior_count": behavior_count,
        "complexity_counts": complexity_counts,
        "feature_coverage": feature_coverage,
    }, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("status", "prepare", "update", "finalize"))
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    try:
        root = ensure_safe_project_root(Path(args.project_root))
        if args.command == "status":
            print(json.dumps(_status_payload(root), ensure_ascii=False, indent=2))
            return 0
        if args.command == "prepare":
            prepare(root)
        elif args.command == "update":
            update_project_skills(root)
        else:
            finalize(root)
        return 0
    except ProjectPrdError as exc:
        print(f"project-prd: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
