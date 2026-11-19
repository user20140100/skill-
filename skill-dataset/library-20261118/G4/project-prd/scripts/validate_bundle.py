#!/usr/bin/env python3
"""Validate the project-prd distribution without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "scripts/bootstrap.py",
    "scripts/project_prd_lib.py",
    "references/initialization-workflow.md",
    "references/feature-analysis.md",
    "references/prd-extraction.md",
    "references/prd-authoring.md",
    "references/gates.md",
    "assets/prd-template.md",
    "assets/internal-skills/project-prd-writer/SKILL.md",
    "assets/internal-skills/project-prd-writer/agents/openai.yaml",
    "assets/internal-skills/project-prd-writer/references/full-template-contract.md",
    "assets/internal-skills/project-prd-writer/references/prd-template.md",
    "assets/runtime/project_prd_guard.py",
    "assets/github/project-prd-guard.yml",
    "assets/project-skills/project-prd-edit/SKILL.md",
    "assets/project-skills/project-prd-edit/scripts/apply_prd_change.py",
    "assets/project-skills/project-prd-verify/SKILL.md",
    "assets/project-skills/project-prd-clear/SKILL.md",
    "assets/project-skills/project-prd-clear/scripts/clear_project_prd.py",
    "assets/project-skills/project-prd-serve/SKILL.md",
    "assets/project-skills/project-prd-serve/scripts/serve.py",
    "assets/project-skills/project-prd-serve/assets/web/index.html",
    "assets/project-skills/project-prd-serve/assets/web/app.js",
    "assets/project-skills/project-prd-serve/assets/web/markdown.js",
    "assets/project-skills/project-prd-serve/assets/web/style.css",
)


def _frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        raise ValueError(f"缺少有效 frontmatter：{path}")
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            data[key.strip()] = value.strip()
    return data


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"缺少文件：{relative}")
    expected_skills = {
        "SKILL.md": "project-prd",
        "assets/project-skills/project-prd-edit/SKILL.md": "project-prd-edit",
        "assets/project-skills/project-prd-verify/SKILL.md": "project-prd-verify",
        "assets/project-skills/project-prd-clear/SKILL.md": "project-prd-clear",
        "assets/project-skills/project-prd-serve/SKILL.md": "project-prd-serve",
        "assets/internal-skills/project-prd-writer/SKILL.md": "project-prd-writer",
    }
    for relative, expected_name in expected_skills.items():
        path = root / relative
        if not path.is_file():
            continue
        try:
            metadata = _frontmatter(path)
            if metadata.get("name") != expected_name:
                errors.append(f"skill name 不匹配：{relative}")
            if not metadata.get("description"):
                errors.append(f"skill description 为空：{relative}")
        except ValueError as exc:
            errors.append(str(exc))
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".yml", ".yaml"}:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".py" and re.search(r"(?m)^\s*#\s*TODO\b", text):
                errors.append(f"存在未完成占位符：{path.relative_to(root)}")
    workflow = root / "assets" / "github" / "project-prd-guard.yml"
    if workflow.is_file():
        workflow_text = workflow.read_text(encoding="utf-8")
        for required in (
            "pull_request_target:",
            "github.event.pull_request.head.sha",
            "git show",
            "project_prd_guard.py",
            "project_prd_lib.py",
            "trusted project-prd guard is absent from the base revision",
            "PROJECT_PRD_RULES_(START|END)",
        ):
            if required not in workflow_text:
                errors.append(f"GitHub 门禁缺少可信执行要素：{required}")
        if "python .project-prd/tools/project_prd_guard.py" in workflow_text:
            errors.append("GitHub 门禁不得在 pull_request_target 中执行 PR 分支脚本")
    canonical_template = root / "assets" / "prd-template.md"
    writer_template = (
        root / "assets" / "internal-skills" / "project-prd-writer" / "references" / "prd-template.md"
    )
    if canonical_template.is_file() and writer_template.is_file() and (
        canonical_template.read_text(encoding="utf-8") != writer_template.read_text(encoding="utf-8")
    ):
        errors.append("内部 project-prd-writer 模板与主模板不一致")
    if canonical_template.is_file():
        template_text = canonical_template.read_text(encoding="utf-8")
        for required in (
            "prd_schema: feature-points-v3",
            "decomposition_candidates:",
            "### 3.1 业务流程图",
            "```mermaid",
            "### 3.2 规则矩阵覆盖审计",
            "| 场景 | 提示内容 | 展示方式 | 源码证据 |",
        ):
            if required not in template_text:
                errors.append(f"v3 PRD 模板缺少：{required}")
    library = root / "scripts" / "project_prd_lib.py"
    if library.is_file() and "FORMAT_VERSION = 3" not in library.read_text(encoding="utf-8"):
        errors.append("project-prd runtime 未升级到 format version 3")
    delegation_contracts = {
        "SKILL.md": (
            "每份细分功能 PRD 必须委派给一个全新的独立子代理",
            "主代理不得亲自撰写 PRD 正文",
            ".project-prd/.analysis/progress.json",
        ),
        "references/initialization-workflow.md": (
            "一份 PRD = 一个全新子代理",
            "min(4, 可用子代理槽位, 未完成任务数)",
            "只有主代理可以生成 INDEX",
        ),
        "assets/internal-skills/project-prd-writer/SKILL.md": (
            "只写入任务包指定的唯一目标文件",
            "不得读取其他 PRD 正文",
            "不得运行 `finalize` 或 `integrity`",
        ),
    }
    for relative, required_items in delegation_contracts.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for required in required_items:
            if required not in text:
                errors.append(f"逐 PRD 子代理委派契约缺少：{relative} -> {required}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        print("project-prd bundle validation FAIL")
        for error in errors:
            print(f"- {error}")
        return 2
    print("project-prd bundle validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
