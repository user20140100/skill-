#!/usr/bin/env python3
"""Validate requirement-analysis-pro packaging and cross-file conventions."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = SKILL_ROOT / "SKILL.md"
REFERENCES_DIR = SKILL_ROOT / "references"
VALIDATION_CASES = REFERENCES_DIR / "validation-cases.md"

RUNTIME_REFERENCES = [
    "doc-structure-common.md",
    "doc-structure-project.md",
    "doc-structure-special.md",
    "doc-structure-ad-hoc.md",
    "chart-selection.md",
    "visual-style.md",
    "prototype-spec.md",
    "sdd-specification.md",
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add(checks: list[Check], name: str, passed: bool, detail: str) -> None:
    checks.append(Check(name=name, passed=passed, detail=detail))


def extract_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    name_match = re.search(r"^name:\s*(.+)$", block, re.MULTILINE)
    desc_match = re.search(
        r"^description:\s*>-\s*\n((?:^[ \t]+.*\n?)+)", block, re.MULTILINE
    )
    description = ""
    if desc_match:
        description = " ".join(line.strip() for line in desc_match.group(1).splitlines())
    return {
        "name": name_match.group(1).strip() if name_match else "",
        "description": description,
    }


def local_markdown_links(path: Path, text: str) -> list[tuple[str, Path]]:
    links: list[tuple[str, Path]] = []
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0]
        if not target or re.match(r"^[a-z]+://", target):
            continue
        links.append((target, (path.parent / target).resolve()))
    return links


def main() -> int:
    checks: list[Check] = []

    required_files = [SKILL_FILE]
    required_files.extend(REFERENCES_DIR / name for name in RUNTIME_REFERENCES)
    required_files.append(VALIDATION_CASES)
    missing = [str(path.relative_to(SKILL_ROOT)) for path in required_files if not path.exists()]
    add(checks, "required files", not missing, "missing: " + ", ".join(missing) if missing else "all present")

    if missing:
        return report(checks)

    skill_text = read(SKILL_FILE)
    reference_texts = {name: read(REFERENCES_DIR / name) for name in RUNTIME_REFERENCES}
    runtime_text = "\n".join([skill_text, *reference_texts.values()])
    cases_text = read(VALIDATION_CASES)

    frontmatter = extract_frontmatter(skill_text)
    skill_name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    add(
        checks,
        "frontmatter name",
        bool(re.fullmatch(r"[a-z0-9-]{1,64}", skill_name)),
        skill_name or "missing",
    )
    add(
        checks,
        "description length",
        1 <= len(description) <= 1024,
        f"{len(description)} characters",
    )
    description_terms = [
        "需求分析",
        "规格设计",
        "项目型",
        "专项",
        "变更型",
        "Markdown",
        "SDD-ready",
        "AI Agent",
    ]
    absent_terms = [term for term in description_terms if term not in description]
    add(
        checks,
        "description discovery terms",
        not absent_terms,
        "missing: " + ", ".join(absent_terms) if absent_terms else "complete",
    )
    add(
        checks,
        "SKILL.md size",
        len(skill_text.splitlines()) < 500,
        f"{len(skill_text.splitlines())} lines",
    )

    long_without_toc = []
    for path in [REFERENCES_DIR / name for name in RUNTIME_REFERENCES] + [VALIDATION_CASES]:
        text = read(path)
        if len(text.splitlines()) > 100 and "## 目录" not in text:
            long_without_toc.append(path.name)
    add(
        checks,
        "long references have TOC",
        not long_without_toc,
        "missing TOC: " + ", ".join(long_without_toc) if long_without_toc else "complete",
    )

    broken_links: list[str] = []
    for path in required_files:
        for target, resolved in local_markdown_links(path, read(path)):
            if not resolved.exists():
                broken_links.append(f"{path.name} -> {target}")
    add(
        checks,
        "local links",
        not broken_links,
        "; ".join(broken_links) if broken_links else "all valid",
    )

    unbalanced_fences = []
    for path in required_files:
        if len(re.findall(r"^```", read(path), re.MULTILINE)) % 2:
            unbalanced_fences.append(path.name)
    add(
        checks,
        "Markdown code fences",
        not unbalanced_fences,
        "unbalanced: " + ", ".join(unbalanced_fences) if unbalanced_fences else "balanced",
    )

    forbidden_runtime = {
        "removed modeling terminology": ["六色", "six_color", "PROCESS_STAGE", "PHYSICAL_ENTITY"],
        "direct Feishu dependencies": ["lark-shared", "../lark-doc/", "lark-cli"],
        "legacy scenario ID": ["<S-xx>", "S-xx / BR", "S-xxx"],
        "legacy requirement type": ["零散需求文档结构", "| 零散需求 |", "判定为零散"],
        "second process hierarchy": ["四级流程", "流程与功能分级"],
    }
    for name, terms in forbidden_runtime.items():
        found = [term for term in terms if term in runtime_text]
        add(
            checks,
            name,
            not found,
            "found: " + ", ".join(found) if found else "clean",
        )

    mandatory_ascii_patterns = [
        r"必须[^\n]{0,40}(?:使用|绘制)[^\n]{0,20}ASCII",
        r"每张入选图[^\n]{0,80}ASCII",
        r"入选图[^\n]{0,40}必须[^\n]{0,40}ASCII",
    ]
    mandatory_ascii = [
        pattern for pattern in mandatory_ascii_patterns if re.search(pattern, runtime_text)
    ]
    add(
        checks,
        "ASCII is conditional",
        not mandatory_ascii,
        "mandatory rule detected" if mandatory_ascii else "conditional only",
    )

    required_id_terms = [
        "OBJ-xxx",
        "SCN-xxx",
        "BR-xxx",
        "FR-xxx",
        "PAGE-xxx",
        "DATA-xxx",
        "INT-xxx",
        "NFR-xxx",
        "AGT-xxx",
        "TOOL-xxx",
        "KNW-xxx",
        "AC-xxx",
        "TC-xxx",
        "EVAL-xxx",
    ]
    missing_ids = [term for term in required_id_terms if term not in skill_text]
    add(
        checks,
        "canonical IDs",
        not missing_ids,
        "missing: " + ", ".join(missing_ids) if missing_ids else "complete",
    )

    boundary_phrases = [
        "L1～L6 仅用于业务流程",
        "页面是功能的交互载体",
        "无页面",
        "确定性优先",
        "运行闭环优先",
    ]
    missing_boundaries = [phrase for phrase in boundary_phrases if phrase not in skill_text]
    add(
        checks,
        "core boundaries",
        not missing_boundaries,
        "missing: " + ", ".join(missing_boundaries) if missing_boundaries else "complete",
    )

    unconditional_visual = "写文档和绘图前" in skill_text or "所有任务读取 visual-style" in runtime_text
    add(
        checks,
        "progressive visual loading",
        not unconditional_visual and "普通 Markdown 不加载" in runtime_text,
        "conditional" if not unconditional_visual else "unconditional load found",
    )

    chart_text = reference_texts["chart-selection.md"]
    generic_terms = ["图表语义模型", "问题到图表类型", "表达载体选择", "专业构图规则", "需求类型裁剪"]
    missing_generic_terms = [term for term in generic_terms if term not in chart_text]
    add(checks, "generic diagram routing", not missing_generic_terms, "missing: " + ", ".join(missing_generic_terms) if missing_generic_terms else "complete")
    fixed_template_refs = list(REFERENCES_DIR.glob("*diagram*template*.md"))
    add(checks, "no fixed diagram template layer", not fixed_template_refs, "clean" if not fixed_template_refs else "template reference remains")

    add(
        checks,
        "removed files",
        not (REFERENCES_DIR / "six-color-modeling.md").exists()
        and not (SKILL_ROOT / ".DS_Store").exists(),
        "clean" if not (REFERENCES_DIR / "six-color-modeling.md").exists() and not (SKILL_ROOT / ".DS_Store").exists() else "obsolete file remains",
    )
    add(
        checks,
        "change log excluded from runtime",
        "修改日志" not in skill_text and "修改日志.md" not in runtime_text,
        "not routed",
    )

    case_ids = re.findall(r"^### (VAL-\d{3})\b", cases_text, re.MULTILINE)
    add(
        checks,
        "validation case count",
        len(case_ids) >= 15 and len(case_ids) == len(set(case_ids)),
        f"{len(case_ids)} unique cases",
    )
    case_terms = ["ERP", "SCM", "MES", "BOM", "工单", "库存", "Agent", "`trigger`: no"]
    missing_case_terms = [term for term in case_terms if term not in cases_text]
    add(
        checks,
        "manufacturing case coverage",
        not missing_case_terms,
        "missing: " + ", ".join(missing_case_terms) if missing_case_terms else "complete",
    )

    case_blocks = re.split(r"(?=^### VAL-\d{3}\b)", cases_text, flags=re.MULTILINE)[1:]
    incomplete_cases = []
    valid_types = {
        "project",
        "special",
        "ad_hoc",
        "special_by_risk",
        "pending_classification",
        "special_sdd",
        "same_as_source",
        "not_applicable",
    }
    invalid_types = []
    invalid_routes = []
    for block in case_blocks:
        case_match = re.match(r"### (VAL-\d{3})", block)
        case_id = case_match.group(1) if case_match else "unknown"
        required_markers = [
            "**测试提问**",
            "- `trigger`:",
            "- `type`:",
            "- `load`:",
            "- `must`:",
            "- `must_not`:",
        ]
        if any(marker not in block for marker in required_markers):
            incomplete_cases.append(case_id)
        type_match = re.search(r"- `type`:\s*([a-z_]+)", block)
        if not type_match or type_match.group(1) not in valid_types:
            invalid_types.append(case_id)
        load_match = re.search(r"- `load`:\s*(.+)", block)
        if load_match:
            for filename in re.findall(r"`([^`]+\.md)`", load_match.group(1)):
                if filename not in RUNTIME_REFERENCES:
                    invalid_routes.append(f"{case_id}:{filename}")
    add(
        checks,
        "validation case schema",
        not incomplete_cases,
        "incomplete: " + ", ".join(incomplete_cases) if incomplete_cases else "complete",
    )
    add(
        checks,
        "validation case types",
        not invalid_types,
        "invalid: " + ", ".join(invalid_types) if invalid_types else "valid",
    )
    add(
        checks,
        "validation case routes",
        not invalid_routes,
        "invalid: " + ", ".join(invalid_routes) if invalid_routes else "valid",
    )

    return report(checks)


def report(checks: list[Check]) -> int:
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status:<4}  {check.name:<34} {check.detail}")
    passed = sum(check.passed for check in checks)
    print(f"\nSUMMARY: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
