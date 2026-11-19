#!/usr/bin/env python3
"""Shared, dependency-free helpers for project-prd workspace management."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FORMAT_VERSION = 3
OWNER_FILE = ".project-prd-owner.json"
MANAGED_START = "<!-- PROJECT_PRD_RULES_START -->"
MANAGED_END = "<!-- PROJECT_PRD_RULES_END -->"
PRD_REQUIRED_SECTIONS = (
    "## 一、文档说明",
    "## 二、功能模块与功能点",
    "## 三、功能关联与闭环关系",
    "## 四、行为覆盖与代码追溯",
    "## 五、验证依据",
    "## 六、已知缺口与待确认项",
)
COMPLEXITY_LIMITS = {
    "simple": {"feature_points": 1, "interaction": 1, "positive": 1, "negative": 1, "behavior": 1},
    "standard": {"feature_points": 1, "interaction": 3, "positive": 2, "negative": 2, "behavior": 3},
    "complex": {"feature_points": 2, "interaction": 5, "positive": 3, "negative": 3, "behavior": 6},
}
EXCEPTION_CATEGORIES = ("空态", "操作失败", "网络异常", "权限不足", "边界超限")
FEATURE_POINT_SECTIONS = (
    (1, "功能描述"),
    (2, "交互逻辑"),
    (3, "跳转逻辑"),
    (4, "跳转过程逻辑"),
    (5, "正向限制"),
    (6, "反向限制"),
    (7, "异常/空态/错误提示"),
)
ANCHOR_CANDIDATE_KINDS = (
    "trigger", "stage", "decision", "interaction", "external_wait", "terminal", "lifecycle"
)
CANDIDATE_KINDS = (*ANCHOR_CANDIDATE_KINDS, "cleanup")
MATRIX_TYPES = ("mapping", "state", "priority", "copy", "policy", "permission", "none")
CATEGORY_DIMENSIONS = ("actor", "outcome", "object", "journey", "lifecycle", "permission")
CATEGORY_VAGUE_VALUES = {
    "outcome": {"完成操作", "使用功能", "提升体验", "满足需求", "提供能力", "帮助用户完成操作"},
    "object": {"系统", "功能", "能力", "技术能力", "通用技术能力", "业务能力", "操作"},
    "journey": {"流程", "操作流程", "业务流程"},
    "lifecycle": {"生命周期", "流程", "业务流程"},
    "permission": {"权限", "权限控制"},
}
CONTROL_PLANE_FILES = {
    "manifest.json", "INDEX.md", OWNER_FILE, ".initializing.json", ".gitignore",
}
CONTROL_PLANE_DIRECTORIES = {"tools", ".history", ".analysis", "output"}


class ProjectPrdError(RuntimeError):
    """A user-actionable project-prd validation error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProjectPrdError(f"缺少文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ProjectPrdError(f"JSON 无效：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectPrdError(f"JSON 顶层必须是对象：{path}")
    return value


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def ensure_safe_project_root(root: Path) -> Path:
    resolved = root.expanduser().resolve()
    home = Path.home().resolve()
    broad_home_children = {"Desktop", "Documents", "Downloads", "Movies", "Music", "Pictures"}
    if (
        resolved == Path(resolved.anchor)
        or resolved == home
        or (resolved.parent == home and resolved.name in broad_home_children)
    ):
        raise ProjectPrdError(f"拒绝使用过宽的项目根目录：{resolved}")
    if not resolved.is_dir():
        raise ProjectPrdError(f"项目根目录不存在：{resolved}")
    strong_markers = (
        ".git", "package.json", "build.gradle", "build.gradle.kts", "settings.gradle",
        "settings.gradle.kts", "pyproject.toml", "Cargo.toml", "go.mod", "oh-package.json5",
        "Package.swift", "pubspec.yaml",
    )
    if not any((resolved / marker).exists() for marker in strong_markers):
        raise ProjectPrdError("项目根目录缺少版本库或构建清单标识")
    return resolved


def ensure_managed_path(project_root: Path, target: Path) -> Path:
    """Reject managed paths whose existing symlink parents escape the project root."""
    root = project_root.resolve()
    resolved = target.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ProjectPrdError(f"受管路径通过符号链接越出项目：{target}")
    return target


def ensure_no_symlink_path(project_root: Path, target: Path) -> Path:
    """Reject a managed path if it escapes the root or any component is a symlink."""
    root = project_root.absolute()
    ensure_managed_path(root, target)
    try:
        relative = target.absolute().relative_to(root)
    except ValueError as exc:
        raise ProjectPrdError(f"受管路径不在项目内：{target}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProjectPrdError(f"受管路径不得包含符号链接：{target}")
    return target


def find_project_root(start: Path) -> Path:
    markers = (
        ".project-prd", ".git", "AGENTS.md", "package.json", "build.gradle",
        "build.gradle.kts", "pyproject.toml", "Cargo.toml", "go.mod", "oh-package.json5",
    )
    current = start.expanduser().resolve()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in markers):
            return ensure_safe_project_root(candidate)
    raise ProjectPrdError("无法定位项目根目录；请显式传入 --project-root")


def parse_frontmatter(content: str) -> dict[str, Any]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ProjectPrdError("PRD 必须以 YAML frontmatter 开头")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ProjectPrdError("PRD frontmatter 缺少结束分隔符 ---") from exc
    metadata: dict[str, Any] = {}
    active_list: str | None = None
    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - ") and active_list:
            metadata.setdefault(active_list, []).append(raw_line[4:].strip())
            continue
        match = re.match(r"^([a-z_]+):\s*(.*)$", raw_line)
        if not match:
            raise ProjectPrdError(f"无法解析 frontmatter 行：{raw_line}")
        key, value = match.groups()
        if value:
            metadata[key] = value.strip().strip('"').strip("'")
            active_list = None
        else:
            metadata[key] = []
            active_list = key
    return metadata


def _path_parts(relative_path: Path) -> tuple[str, str]:
    if relative_path.is_absolute() or len(relative_path.parts) != 2:
        raise ProjectPrdError("PRD 路径必须恰好为 <功能分类>/<细分功能>.md")
    category, filename = relative_path.parts
    if category.startswith(".") or filename.startswith(".") or relative_path.suffix.lower() != ".md":
        raise ProjectPrdError(f"PRD 路径无效：{relative_path}")
    if any(part in {"", ".", ".."} for part in relative_path.parts):
        raise ProjectPrdError(f"PRD 路径无效：{relative_path}")
    return category, relative_path.stem


def _section(content: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^##\s|\Z)", content)
    if match is None:
        raise ProjectPrdError(f"PRD 缺少或无法解析章节：{heading}")
    return match.group(1).strip()


def _table_rows(section: str, expected_headers: tuple[str, ...]) -> list[list[str]]:
    rows: list[list[str]] = []
    header_found = False
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells == list(expected_headers):
            header_found = True
            continue
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if header_found and any(cells):
            rows.append(cells)
    if not header_found:
        raise ProjectPrdError("表格缺少标准表头：" + " | ".join(expected_headers))
    if any(len(row) != len(expected_headers) or any(not cell for cell in row) for row in rows):
        raise ProjectPrdError("表格数据行必须列数一致且每列非空：" + " | ".join(expected_headers))
    return rows


def _any_table_rows(section: str, *, label: str) -> list[list[str]]:
    table_lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 3:
        raise ProjectPrdError(f"{label}必须提供包含表头和数据行的 Markdown 表格")
    parsed = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in table_lines
    ]
    if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in parsed[1]):
        raise ProjectPrdError(f"{label}表格缺少分隔行")
    column_count = len(parsed[0])
    rows = parsed[2:]
    if column_count < 2 or any(
        len(row) != column_count or any(not cell for cell in row) for row in rows
    ):
        raise ProjectPrdError(f"{label}表格列数必须一致且每列非空")
    if not rows:
        raise ProjectPrdError(f"{label}表格至少需要一条数据")
    return rows


def _feature_points(content: str) -> list[tuple[str, str, str]]:
    section = _section(content, "## 二、功能模块与功能点")
    section = re.sub(r"(?ms)```.*?```", "", section)
    section = re.sub(r"(?ms)<!--.*?-->", "", section)
    if not re.search(r"(?m)^###\s+模块\s*[A-Z0-9一二三四五六七八九十]*[：:]\s*\S+", section):
        raise ProjectPrdError("功能模块与功能点必须至少包含一个‘### 模块 A：名称’模块标题")
    matches = list(
        re.finditer(
            r"(?ms)^####\s+(FP-\d{2,})\s+(.+?)\s*$\n"
            r"(.*?)(?=^####\s+FP-\d{2,}\s+|^###\s+模块|\Z)",
            section,
        )
    )
    if not matches:
        raise ProjectPrdError("功能模块与功能点至少需要一个‘#### FP-01 功能点名称’")
    points = [(match.group(1), match.group(2).strip(), match.group(3).strip()) for match in matches]
    ids = [item[0] for item in points]
    titles = [item[1] for item in points]
    if len(ids) != len(set(ids)):
        raise ProjectPrdError("Feature Point ID 必须唯一")
    if len(titles) != len(set(titles)):
        raise ProjectPrdError("Feature Point 名称必须唯一")
    expected_ids = [f"FP-{index:02d}" for index in range(1, len(points) + 1)]
    if ids != expected_ids:
        raise ProjectPrdError("Feature Point ID 必须从 FP-01 开始连续编号")
    return points


def _feature_subsection(block: str, index: int, name: str, feature_point_id: str) -> str:
    match = re.search(
        rf"(?ms)^\*\*{index}\.\s*{re.escape(name)}\*\*\s*$\n"
        rf"(.*?)(?=^\*\*\d+\.\s*|\Z)",
        block,
    )
    if match is None:
        raise ProjectPrdError(f"{feature_point_id} 缺少‘{index}. {name}’")
    value = match.group(1).strip()
    if not value:
        raise ProjectPrdError(f"{feature_point_id} 的‘{name}’不能为空")
    return value


def _split_evidence_reference(raw_reference: str) -> tuple[str, str | None]:
    reference = raw_reference.strip().strip("`").strip()
    source_path, separator, locator = reference.partition(":")
    parsed_source = Path(source_path)
    if (
        not reference
        or "\\" in reference
        or parsed_source.is_absolute()
        or ".." in parsed_source.parts
        or ("/" not in source_path and "." not in parsed_source.name)
    ):
        raise ProjectPrdError(f"证据必须使用项目内相对路径：{raw_reference}")
    if separator and not locator.strip():
        raise ProjectPrdError(f"证据冒号后必须提供 Symbol 或行号：{raw_reference}")
    return source_path, locator.strip() if separator else None


def _validate_evidence_reference(
    raw_reference: str,
    project_root: Path | None,
    *,
    require_locator: bool,
    evidence_label: str,
) -> None:
    source_path, locator = _split_evidence_reference(raw_reference)
    if require_locator and locator is None:
        raise ProjectPrdError(f"{evidence_label} 必须使用 path:Symbol 或 path:行号：{raw_reference}")
    if project_root is None:
        return
    candidate = ensure_managed_path(project_root, project_root / source_path)
    if not candidate.is_file():
        raise ProjectPrdError(f"{evidence_label} 指向的文件不存在：{raw_reference}")
    if locator is None:
        return
    try:
        source_text = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectPrdError(f"{evidence_label} 无法按 UTF-8 读取：{raw_reference}") from exc
    line_match = re.fullmatch(r"L?(\d+)(?:-L?(\d+))?", locator)
    if line_match:
        start = int(line_match.group(1))
        end = int(line_match.group(2) or start)
        line_count = len(source_text.splitlines())
        if start < 1 or end < start or end > line_count:
            raise ProjectPrdError(f"{evidence_label} 行号越界：{raw_reference}")
        return
    symbol_pattern = re.compile(
        r"[A-Za-z_$\u0080-\uffff][\w$\u0080-\uffff]*(?:\(\))?"
    )
    if not symbol_pattern.fullmatch(locator):
        raise ProjectPrdError(
            f"{evidence_label} 的 Symbol 必须是单一名称；限定名或不支持的格式请改用行号："
            f"{raw_reference}"
        )
    symbol = locator.removesuffix("()")
    escaped = re.escape(symbol)
    suffix = candidate.suffix.lower()
    definition_patterns: dict[str, tuple[str, ...]] = {
        ".py": (
            rf"(?m)^\s*(?:async\s+)?def\s+{escaped}\b",
            rf"(?m)^\s*class\s+{escaped}\b",
            rf"(?m)^\s*{escaped}\s*(?::[^=\n]+)?=",
        ),
        ".rb": (rf"(?m)^\s*def\s+(?:self\.)?{escaped}\b", rf"(?m)^\s*class\s+{escaped}\b"),
        ".go": (rf"(?m)^\s*func\s+(?:\([^)]*\)\s*)?{escaped}\b", rf"(?m)^\s*type\s+{escaped}\b"),
        ".rs": (rf"(?m)^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+{escaped}\b", rf"(?m)^\s*(?:pub\s+)?(?:struct|enum|trait|type)\s+{escaped}\b"),
    }
    c_family = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".java", ".kt", ".kts", ".cs", ".swift"}
    script_family = {".js", ".jsx", ".ts", ".tsx", ".ets"}
    if suffix in c_family:
        patterns = (
            rf"(?m)^\s*(?:(?:public|private|protected|internal|static|final|open|override|virtual|abstract|async|suspend|inline|constexpr|const|extern|pub|mut)\s+)*(?:class|interface|enum|struct|typealias|fun|func)\s+{escaped}\b",
            rf"(?m)^\s*(?:(?:public|private|protected|internal|static|final|open|override|virtual|abstract|async|suspend|inline|constexpr|const|extern|pub|mut)\s+)*(?:[\w$<>\[\],.?*&:]+\s+)+{escaped}\s*(?:<[^>]+>\s*)?\(",
        )
    elif suffix in script_family:
        patterns = (
            rf"(?m)^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|interface|enum|type)\s+{escaped}\b",
            rf"(?m)^\s*(?:export\s+)?(?:const|let|var)\s+{escaped}\b",
            rf"(?m)^\s*(?:(?:public|private|protected|static|readonly|async|override|abstract|get|set)\s+)*{escaped}\s*(?:<[^>]+>\s*)?\(",
        )
    else:
        patterns = definition_patterns.get(suffix, ())
    if not patterns:
        raise ProjectPrdError(
            f"{evidence_label} 暂不支持校验 {suffix or '无扩展名'} 文件的 Symbol，请改用行号："
            f"{raw_reference}"
        )
    if not any(re.search(pattern, source_text) for pattern in patterns):
        raise ProjectPrdError(
            f"{evidence_label} 的 Symbol 定义不存在于文件中：{raw_reference}"
        )


def _is_test_evidence_path(source_path: str) -> bool:
    path = Path(source_path)
    parts = {part.lower() for part in path.parts[:-1]}
    stem = path.stem.lower()
    original_stem = path.stem
    return bool(
        parts.intersection({"test", "tests", "__tests__", "spec", "specs"})
        or stem.startswith(("test_", "test-"))
        or stem.endswith(("_test", "-test", ".test", ".spec"))
        or original_stem.endswith(("Test", "Tests", "Spec", "Specs"))
    )


def _code_references(cell: str, *, evidence_label: str) -> list[str]:
    references = re.findall(r"`([^`]+)`", cell)
    residual = re.sub(r"`[^`]+`", "", cell)
    residual = re.sub(r"(?i)<br\s*/?>|[、,，;；\s]", "", residual)
    if not references or residual:
        raise ProjectPrdError(
            f"{evidence_label} 必须仅由反引号包裹的证据组成，多项使用 <br> 分隔：{cell}"
        )
    return references


def _parse_category_contract(items: list[Any]) -> dict[str, str]:
    contract: dict[str, str] = {}
    dimensions: list[str] = []
    for raw_item in items:
        match = re.fullmatch(r"(actor|outcome|object|journey|lifecycle|permission)=(.+)", str(raw_item).strip())
        if match is None:
            raise ProjectPrdError(
                "category_contract 必须使用 dimension=value；dimension 只能是 "
                + "、".join(CATEGORY_DIMENSIONS)
            )
        dimension, value = match.group(1), match.group(2).strip()
        if dimension in contract:
            raise ProjectPrdError(f"category_contract 维度重复：{dimension}")
        normalized_value = re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()
        if not normalized_value or normalized_value in CATEGORY_VAGUE_VALUES.get(dimension, set()):
            raise ProjectPrdError(f"category_contract.{dimension} 过于泛化：{value}")
        contract[dimension] = value
        dimensions.append(dimension)
    expected_order = [item for item in CATEGORY_DIMENSIONS if item in contract]
    if dimensions != expected_order:
        raise ProjectPrdError("category_contract 必须按 actor、outcome、object、journey、lifecycle、permission 顺序书写")
    if len(contract) < 2:
        raise ProjectPrdError("category_contract 至少需要两个共享维度；单成员分类也必须说明聚合依据")
    return contract


def _parse_category_fit(
    items: list[Any],
    contract: dict[str, str],
    source_entries: set[str],
    project_root: Path | None,
) -> dict[str, str]:
    fit: dict[str, str] = {}
    for raw_item in items:
        match = re.fullmatch(
            r"(actor|outcome|object|journey|lifecycle|permission)=(.+?)\s+@\s+(.+)",
            str(raw_item).strip(),
        )
        if match is None:
            raise ProjectPrdError("category_fit 必须使用 dimension=value @ path:Symbol 格式")
        dimension, value, reference = match.group(1), match.group(2).strip(), match.group(3).strip()
        if dimension in fit:
            raise ProjectPrdError(f"category_fit 维度重复：{dimension}")
        if contract.get(dimension) != value:
            raise ProjectPrdError(
                f"category_fit.{dimension} 必须精确引用 category_contract 中的同维度值"
            )
        if reference not in source_entries:
            raise ProjectPrdError(
                f"category_fit 证据必须同时登记在 source_entries：{reference}"
            )
        _validate_evidence_reference(
            reference,
            project_root,
            require_locator=True,
            evidence_label=f"category_fit.{dimension}",
        )
        fit[dimension] = reference
    if len(fit) < 2:
        raise ProjectPrdError("category_fit 至少需要两个共享维度及源码证据")
    return fit


def _split_plain_references(cell: str, *, evidence_label: str) -> list[str]:
    references = [item.strip().strip("`") for item in re.split(r"(?i)<br\s*/?>", cell)]
    if not references or any(not item for item in references):
        raise ProjectPrdError(f"{evidence_label} 必须使用 path:Symbol，多项以 <br> 分隔")
    return references


def _strip_source_comments(text: str) -> str:
    text = re.sub(r"(?s)/\*.*?\*/", "", text)
    text = re.sub(r"(?m)//.*$", "", text)
    text = re.sub(r"(?m)#.*$", "", text)
    return text


def _source_reference_text(
    reference: str, project_root: Path | None, *, full_file: bool = False
) -> str:
    if project_root is None:
        return ""
    source_path, locator = _split_evidence_reference(reference)
    path = project_root / source_path
    source_text = path.read_text(encoding="utf-8")
    if full_file or locator is None:
        return _strip_source_comments(source_text)
    lines = source_text.splitlines()
    line_match = re.fullmatch(r"L?(\d+)(?:-L?(\d+))?", locator)
    if line_match:
        start = int(line_match.group(1)) - 1
        end = int(line_match.group(2) or line_match.group(1))
        return _strip_source_comments("\n".join(lines[start:end]))

    suffix = path.suffix.lower()
    symbol = locator.removesuffix("()")
    if suffix == ".py":
        definition_pattern = re.compile(
            rf"^\s*(?:(?:async\s+)?def|class)\s+{re.escape(symbol)}\b|"
            rf"^\s*{re.escape(symbol)}\s*(?::[^=\n]+)?="
        )
    else:
        definition_pattern = re.compile(
            rf"^\s*(?:(?:export|default|public|private|protected|internal|static|final|"
            rf"open|override|abstract|async|suspend|readonly)\s+)*"
            rf"(?:(?:function|class|interface|enum|type|fun|func)\s+)?{re.escape(symbol)}\b"
        )
    start_index = next(
        (index for index, line in enumerate(lines) if definition_pattern.search(line)), None
    )
    if start_index is None:
        return ""
    if suffix == ".py":
        start_line = lines[start_index]
        indentation = len(start_line) - len(start_line.lstrip())
        end_index = start_index + 1
        while end_index < len(lines):
            line = lines[end_index]
            if line.strip():
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indentation:
                    break
            end_index += 1
        return _strip_source_comments("\n".join(lines[start_index:end_index]))

    tail = "\n".join(lines[start_index:])
    opening = tail.find("{")
    if opening < 0:
        return _strip_source_comments(lines[start_index])
    depth = 0
    end_offset = len(tail)
    for index, character in enumerate(tail[opening:], start=opening):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                end_offset = index + 1
                break
    return _strip_source_comments(tail[:end_offset])


def _normalized_rule_token(value: str) -> str:
    return re.sub(r"[^\w\u0080-\uffff]+", "", value).casefold()


def _extract_rule_tokens(source_text: str) -> set[str]:
    tokens: set[str] = set()
    for body in re.findall(r"(?is)\benum\s+\w+[^\{]*\{(.*?)\}", source_text):
        for item in body.split(","):
            match = re.match(r"\s*([A-Za-z_$][\w$]*)", item)
            if match:
                tokens.add(_normalized_rule_token(match.group(1)))
    for item in re.findall(r"(?m)\bcase\s+([^:]+):", source_text):
        normalized = _normalized_rule_token(item)
        if normalized:
            tokens.add(normalized)
    collection_pattern = re.compile(
        r"(?is)\b\w*(?:states?|types?|origins?|modes?|polic(?:y|ies)|strategies|"
        r"interceptors?|options?|mappings?)\w*\s*(?::[^=\n]+)?=\s*[\[(](.*?)[\])]"
    )
    for body in collection_pattern.findall(source_text):
        values = re.findall(r"[\"']([^\"']+)[\"']|\b([A-Z][A-Z0-9_]{1,}|[A-Z][A-Za-z0-9_]+)(?=\s*\()", body)
        for string_value, identifier in values:
            normalized = _normalized_rule_token(string_value or identifier)
            if normalized:
                tokens.add(normalized)
    return tokens


def _declared_rule_tokens(items: list[str]) -> set[str]:
    tokens: set[str] = set()
    for item in items:
        normalized = _normalized_rule_token(item)
        if normalized:
            tokens.add(normalized)
        for part in re.split(r"(?:→|=>|=|:|：|/|、|\s+)", item):
            normalized_part = _normalized_rule_token(part)
            if len(normalized_part) >= 2:
                tokens.add(normalized_part)
    return tokens


def _parse_decomposition_candidates(
    items: list[Any],
    feature_point_ids: list[str],
    source_entries: set[str],
    project_root: Path | None,
    complexity: str,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for raw_item in items:
        parts = [part.strip() for part in str(raw_item).split("|")]
        if len(parts) != 5:
            raise ProjectPrdError(
                "decomposition_candidates 必须使用 DC-01|kind|候选名称|源码证据|FP-01 格式"
            )
        candidate_id, kind, title, evidence_cell, feature_point_id = parts
        if not re.fullmatch(r"DC-\d{2,}", candidate_id):
            raise ProjectPrdError(f"拆解候选 ID 无效：{candidate_id}")
        if kind not in CANDIDATE_KINDS:
            raise ProjectPrdError(
                f"拆解候选 kind 无效：{kind}；允许值为 " + "、".join(CANDIDATE_KINDS)
            )
        if len(title) < 4:
            raise ProjectPrdError(f"拆解候选名称必须具体：{candidate_id}")
        if feature_point_id not in feature_point_ids:
            raise ProjectPrdError(f"拆解候选 {candidate_id} 引用未知 FP：{feature_point_id}")
        references = _split_plain_references(
            evidence_cell, evidence_label=f"拆解候选 {candidate_id} 源码证据"
        )
        if complexity == "complex" and kind in {"trigger", "external_wait", "lifecycle"} and len(references) < 2:
            raise ProjectPrdError(
                f"complex PRD 的 {kind} 候选 {candidate_id} 必须同时给出上游入口和核心/下游证据"
            )
        for reference in references:
            if reference not in source_entries:
                raise ProjectPrdError(
                    f"拆解候选 {candidate_id} 的证据必须同时登记在 source_entries：{reference}"
                )
            _validate_evidence_reference(
                reference,
                project_root,
                require_locator=True,
                evidence_label=f"拆解候选 {candidate_id}",
            )
        candidates.append({
            "id": candidate_id,
            "kind": kind,
            "title": title,
            "references": references,
            "feature_point_id": feature_point_id,
        })
    ids = [item["id"] for item in candidates]
    expected_ids = [f"DC-{index:02d}" for index in range(1, len(candidates) + 1)]
    if ids != expected_ids:
        raise ProjectPrdError("拆解候选 ID 必须从 DC-01 开始连续编号")
    titles = [item["title"] for item in candidates]
    if len(titles) != len(set(titles)):
        raise ProjectPrdError("拆解候选名称不得重复")
    anchor_signatures: dict[tuple[str, tuple[str, ...]], str] = {}
    for item in candidates:
        if item["kind"] not in ANCHOR_CANDIDATE_KINDS:
            continue
        signature = (item["kind"], tuple(sorted(set(item["references"]))))
        previous = anchor_signatures.get(signature)
        if previous is not None:
            raise ProjectPrdError(
                f"锚点候选 {previous} 与 {item['id']} 使用相同 kind 和源码范围；"
                "同一锚点不得重复膨胀为多个 FP"
            )
        anchor_signatures[signature] = item["id"]
    for feature_point_id in feature_point_ids:
        anchors = [
            item for item in candidates
            if item["feature_point_id"] == feature_point_id and item["kind"] in ANCHOR_CANDIDATE_KINDS
        ]
        if len(anchors) != 1:
            raise ProjectPrdError(
                f"{feature_point_id} 必须恰好映射一个独立锚点候选；多个触发、阶段、外部等待或终态不得合并"
            )
    return candidates


def _normalized_matrix_items(cell: str, *, label: str) -> list[str]:
    items = [
        re.sub(r"\s+", " ", item.strip().strip("`"))
        for item in re.split(r"(?i)<br\s*/?>", cell)
    ]
    if len(items) < 2 or any(not item for item in items):
        raise ProjectPrdError(f"{label} 至少需要两个以 <br> 分隔的具体项")
    if len(items) != len(set(items)):
        raise ProjectPrdError(f"{label} 不得包含重复项")
    return items


def _source_has_signal(
    references: list[str], project_root: Path | None, pattern: re.Pattern[str]
) -> bool:
    if project_root is None:
        return True
    for reference in references:
        try:
            if pattern.search(_source_reference_text(reference, project_root)):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def _parse_rule_matrices(
    relationship: str,
    feature_point_ids: list[str],
    source_entries: set[str],
    project_root: Path | None,
    complexity_text: str,
) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    structure_pattern = re.compile(
        r"(?i)\benum\b|\bswitch\s*\(|\bcase\b|\bwhen\s*\(|"
        r"\b\w*(?:states?|types?|origins?|modes?|policies|strategies|interceptors?|mappings?)\w*\s*="
    )
    source_rule_inventory: dict[str, set[str]] = {}
    source_structure_inventory: dict[str, bool] = {}
    for reference in source_entries:
        source_scope = _source_reference_text(reference, project_root)
        source_rule_inventory[reference] = _extract_rule_tokens(source_scope)
        source_structure_inventory[reference] = bool(structure_pattern.search(source_scope))
    match = re.search(
        r"(?ms)^###\s+3\.2\s+规则矩阵覆盖审计\s*$\n(.*?)(?=^###\s|\Z)",
        relationship,
    )
    if match is None:
        raise ProjectPrdError("功能关联与闭环关系缺少‘### 3.2 规则矩阵覆盖审计’")
    rows = _table_rows(
        match.group(1),
        ("Matrix ID", "功能点", "规则类型", "源码证据", "代码项", "PRD 覆盖项"),
    )
    if not rows:
        raise ProjectPrdError("规则矩阵覆盖审计至少需要一条 MX-## 或 MX-NONE 记录")
    none_rows = [row for row in rows if row[0] == "MX-NONE"]
    matrix_signal = re.compile(r"枚举|映射|矩阵|优先级|拦截器|策略分支|状态转换")
    if none_rows:
        if len(rows) != 1 or len(none_rows) != 1:
            raise ProjectPrdError("MX-NONE 必须单独出现，不得与真实矩阵记录混用")
        row = none_rows[0]
        if row[1] not in feature_point_ids or row[2] != "none":
            raise ProjectPrdError("MX-NONE 必须引用当前 FP，且规则类型必须是 none")
        if row[4:] != ["无可枚举矩阵", "无可枚举矩阵"]:
            raise ProjectPrdError("MX-NONE 的代码项和 PRD 覆盖项必须均为‘无可枚举矩阵’")
        positive_complexity_text = re.sub(
            r"(?:无|没有|不含|不存在)(?:任何)?(?:可枚举)?(?:的)?"
            r"(?:枚举|映射|矩阵|优先级|拦截器|策略分支|状态转换)",
            "",
            complexity_text,
        )
        source_rule_tokens: set[str] = set()
        source_has_structure = False
        for reference in source_entries:
            source_text = _source_reference_text(reference, project_root, full_file=True)
            source_rule_tokens.update(_extract_rule_tokens(source_text))
            if structure_pattern.search(source_text):
                source_has_structure = True
        if matrix_signal.search(positive_complexity_text) or source_rule_tokens or source_has_structure:
            raise ProjectPrdError("复杂度证据包含矩阵/映射/状态信号，不得使用 MX-NONE")
        references = _code_references(row[3], evidence_label="MX-NONE 源码证据")
        for reference in references:
            if reference not in source_entries:
                raise ProjectPrdError(f"MX-NONE 证据必须同时登记在 source_entries：{reference}")
            _validate_evidence_reference(
                reference,
                project_root,
                require_locator=True,
                evidence_label="MX-NONE 源码证据",
            )
        return [], {row[1]: set(references)}

    ids = [row[0] for row in rows]
    expected_ids = [f"MX-{index:02d}" for index in range(1, len(rows) + 1)]
    if ids != expected_ids:
        raise ProjectPrdError("Matrix ID 必须从 MX-01 开始连续编号，或仅使用 MX-NONE")
    matrices: list[dict[str, Any]] = []
    sources_by_point: dict[str, set[str]] = {}
    covered_matrix_sources: set[str] = set()
    for row in rows:
        matrix_id, feature_point_id, matrix_type, evidence_cell, code_cell, prd_cell = row
        if feature_point_id not in feature_point_ids:
            raise ProjectPrdError(f"{matrix_id} 引用未知 FP：{feature_point_id}")
        if matrix_type not in MATRIX_TYPES or matrix_type == "none":
            raise ProjectPrdError(
                f"{matrix_id} 规则类型无效；真实矩阵只能使用 "
                + "、".join(item for item in MATRIX_TYPES if item != "none")
            )
        references = _code_references(
            evidence_cell, evidence_label=f"{matrix_id} 源码证据"
        )
        for reference in references:
            if reference not in source_entries:
                raise ProjectPrdError(
                    f"{matrix_id} 证据必须同时登记在 source_entries：{reference}"
                )
            _validate_evidence_reference(
                reference,
                project_root,
                require_locator=True,
                evidence_label=f"{matrix_id} 源码证据",
            )
            covered_matrix_sources.add(reference)
        code_items = _normalized_matrix_items(code_cell, label=f"{matrix_id} 代码项")
        prd_items = _normalized_matrix_items(prd_cell, label=f"{matrix_id} PRD 覆盖项")
        source_scope = "\n".join(
            _source_reference_text(reference, project_root) for reference in references
        )
        normalized_scope = _normalized_rule_token(source_scope)
        ungrounded_items: list[str] = []
        for item in code_items:
            normalized_item = _normalized_rule_token(item)
            parts = [
                _normalized_rule_token(part)
                for part in re.split(r"(?:→|=>|=|:|：|/|、)", item)
                if len(_normalized_rule_token(part)) >= 2
            ]
            if normalized_item not in normalized_scope and (
                not parts or not all(part in normalized_scope for part in parts)
            ):
                ungrounded_items.append(item)
        if ungrounded_items:
            raise ProjectPrdError(
                f"{matrix_id} 代码项必须使用源码证据范围内可定位的真实 token/表达式："
                + "、".join(ungrounded_items)
            )
        extracted_tokens = _extract_rule_tokens(source_scope)
        declared_tokens = _declared_rule_tokens(code_items)
        omitted_tokens = sorted(extracted_tokens - declared_tokens)
        if omitted_tokens:
            raise ProjectPrdError(
                f"{matrix_id} 漏写源码证据中的规则项：" + "、".join(omitted_tokens)
            )
        ordered_matrix = matrix_type in {"state", "priority", "policy"}
        if (ordered_matrix and code_items != prd_items) or (
            not ordered_matrix and set(code_items) != set(prd_items)
        ):
            missing = sorted(set(code_items) - set(prd_items))
            extra = sorted(set(prd_items) - set(code_items))
            details: list[str] = []
            if missing:
                details.append("漏写=" + "、".join(missing))
            if extra:
                details.append("无源码项=" + "、".join(extra))
            if ordered_matrix and not details:
                details.append("顺序不一致")
            raise ProjectPrdError(f"{matrix_id} PRD 覆盖项必须与代码项精确一致：" + "；".join(details))
        sources_by_point.setdefault(feature_point_id, set()).update(references)
        matrices.append({
            "id": matrix_id,
            "feature_point_id": feature_point_id,
            "type": matrix_type,
            "references": references,
            "items": code_items,
        })
    uncovered_sources = sorted(
        reference for reference in source_entries
        if (source_rule_inventory[reference] or source_structure_inventory[reference])
        and reference not in covered_matrix_sources
    )
    if uncovered_sources:
        raise ProjectPrdError(
            "以下 source_entries 含规则集合/分支但未被任何 Matrix 覆盖："
            + "、".join(uncovered_sources)
        )
    return matrices, sources_by_point


def _validate_business_flow_diagram(
    relationship: str,
    feature_point_ids: list[str],
    decomposition_candidates: list[dict[str, Any]],
    complexity: str,
) -> int:
    match = re.search(
        r"(?ms)^###\s+3\.1\s+业务流程图\s*$\n(.*?)(?=^###\s|\Z)", relationship
    )
    if match is None:
        raise ProjectPrdError("功能关联与闭环关系缺少‘### 3.1 业务流程图’")
    section = match.group(1).strip()
    diagrams = re.findall(
        r"(?ms)```mermaid\s*\n\s*flowchart\s+(?:TD|TB|BT|LR|RL)\b(.*?)```",
        section,
    )
    if complexity != "complex":
        return len(diagrams)
    if len(diagrams) != 1:
        raise ProjectPrdError("complex PRD 必须恰好提供一张 Mermaid flowchart 业务流程图")
    diagram = re.sub(r"(?m)^\s*%%.*$", "", diagrams[0])
    node_pattern = re.compile(
        r"(?P<id>[A-Za-z_][\w-]*)\s*(?:"
        r"\[\s*[\"']?(?P<bracket>.*?)[\"']?\s*\]|"
        r"\(\s*[\"']?(?P<round>.*?)[\"']?\s*\)|"
        r"\{\s*[\"']?(?P<brace>.*?)[\"']?\s*\})"
    )
    node_labels: dict[str, str] = {}
    for node_match in node_pattern.finditer(diagram):
        node_labels[node_match.group("id")] = (
            node_match.group("bracket")
            or node_match.group("round")
            or node_match.group("brace")
            or ""
        ).strip(" \"'")
    fp_to_node: dict[str, str] = {}
    for node_id, label in node_labels.items():
        node_points = re.findall(r"FP-\d{2,}", label)
        if len(node_points) > 1:
            raise ProjectPrdError("Mermaid 每个节点只能表示一个 Feature Point")
        if node_points:
            feature_point_id = node_points[0]
            if feature_point_id in fp_to_node:
                raise ProjectPrdError(f"Mermaid 中 {feature_point_id} 只能定义一个独立节点")
            fp_to_node[feature_point_id] = node_id
    missing_points = [item for item in feature_point_ids if item not in fp_to_node]
    if missing_points:
        raise ProjectPrdError(
            "complex PRD 业务流程图必须覆盖全部 Feature Point：" + "、".join(missing_points)
        )
    node_ref = r"([A-Za-z_][\w-]*)(?:\s*(?:\[[^\]\n]*\]|\([^\)\n]*\)|\{[^\}\n]*\}))?"
    edge_pattern = re.compile(
        node_ref + r"\s*(-->|-.->|==>)\s*(?:\|([^|\n]+)\|\s*)?" + node_ref
    )
    edges: list[tuple[str, str, str]] = []
    for line in diagram.splitlines():
        edge_match = edge_pattern.search(line)
        if edge_match:
            edges.append((edge_match.group(1), edge_match.group(4), (edge_match.group(3) or "").strip()))
    if not edges:
        raise ProjectPrdError("complex PRD 业务流程图至少需要一条真实流转边")
    if len(edges) != len(set(edges)):
        raise ProjectPrdError("Mermaid 不得用完全重复的边伪造流程分支")
    participating_nodes = {node for left, right, _ in edges for node in (left, right)}
    inactive_points = [
        item for item, node_id in fp_to_node.items() if node_id not in participating_nodes
    ]
    if inactive_points:
        raise ProjectPrdError(
            "Mermaid 中每个 FP 节点都必须参与真实流转：" + "、".join(inactive_points)
        )
    adjacency: dict[str, set[str]] = {}
    for left, right, _ in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    reachable = {fp_to_node[feature_point_ids[0]]}
    frontier = list(reachable)
    while frontier:
        current = frontier.pop()
        for neighbor in adjacency.get(current, set()) - reachable:
            reachable.add(neighbor)
            frontier.append(neighbor)
    disconnected = [
        item for item, node_id in fp_to_node.items() if node_id not in reachable
    ]
    if disconnected:
        raise ProjectPrdError(
            "Mermaid 的 FP 流程必须位于同一连通业务闭环：" + "、".join(disconnected)
        )
    for candidate in decomposition_candidates:
        if candidate["kind"] != "decision":
            continue
        node_id = fp_to_node[candidate["feature_point_id"]]
        outgoing = [edge for edge in edges if edge[0] == node_id]
        labels = {edge[2] for edge in outgoing if edge[2]}
        if len(outgoing) < 2 or len(labels) < 2:
            raise ProjectPrdError(
                f"Mermaid 中 decision 候选 {candidate['id']} 必须至少有两条不同条件标签的出边"
            )
    return 1


def validate_prd(
    content: str,
    relative_path: Path | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    metadata = parse_frontmatter(content)
    required_meta = (
        "prd_schema", "prd_id", "product", "baseline_version", "date", "author",
        "category", "category_domain", "category_goal", "category_contract", "category_fit",
        "feature", "status",
        "complexity", "complexity_reasons", "decomposition_candidates", "decomposition_basis",
        "source_entries",
    )
    missing = [key for key in required_meta if not metadata.get(key)]
    if missing:
        raise ProjectPrdError(f"PRD 元数据缺失：{', '.join(missing)}")
    if metadata["prd_schema"] != "feature-points-v3":
        raise ProjectPrdError("prd_schema 必须是 feature-points-v3")
    if metadata["status"] not in {"active", "deprecated"}:
        raise ProjectPrdError("status 只能是 active 或 deprecated")
    complexity = str(metadata["complexity"])
    if complexity not in COMPLEXITY_LIMITS:
        raise ProjectPrdError("complexity 只能是 simple、standard 或 complex")
    for list_key in (
        "category_contract", "category_fit", "complexity_reasons", "decomposition_candidates",
        "decomposition_basis", "source_entries"
    ):
        if not isinstance(metadata[list_key], list) or not metadata[list_key]:
            raise ProjectPrdError(f"{list_key} 必须是非空列表")
        if len(metadata[list_key]) != len(set(str(item) for item in metadata[list_key])):
            raise ProjectPrdError(f"{list_key} 不得包含重复项")
    min_reasons = 2 if complexity == "complex" else 1
    if len(metadata["complexity_reasons"]) < min_reasons:
        raise ProjectPrdError(f"{complexity} PRD 至少需要 {min_reasons} 条 complexity_reasons")
    if not re.fullmatch(r"PRD-[A-Z0-9][A-Z0-9-]{2,123}", str(metadata["prd_id"])):
        raise ProjectPrdError("prd_id 必须以 PRD- 开头，并仅使用大写字母、数字和连字符")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(metadata["date"])):
        raise ProjectPrdError("date 必须是 YYYY-MM-DD")
    category = str(metadata["category"])
    normalized_category = re.sub(r"\s+", "", unicodedata.normalize("NFKC", category)).casefold()
    generic_categories = {"工具", "其他", "其它", "杂项", "综合", "通用", "辅助", "未分类", "临时"}
    if normalized_category in generic_categories or re.fullmatch(
        r"(?:模块|分类|功能|功能组)[-_]?(?:0*\d+|[一二三四五六七八九十]+)|"
        r"(?:少量|多个|若干)功能",
        normalized_category,
    ):
        raise ProjectPrdError(
            f"一级分类‘{category}’是无业务语义的兜底名称；请按单一业务域命名，单成员分类也允许"
        )
    if not str(metadata["category_domain"]).strip():
        raise ProjectPrdError("category_domain 必须给出明确的核心业务对象或状态域")
    if not str(metadata["category_goal"]).strip():
        raise ProjectPrdError("category_goal 必须给出该分类共同服务的用户结果")

    category_contract = _parse_category_contract(metadata["category_contract"])

    for section_name in PRD_REQUIRED_SECTIONS:
        if section_name not in content:
            raise ProjectPrdError(f"PRD 缺少章节：{section_name}")
    known_gaps = _section(content, "## 六、已知缺口与待确认项")
    content_without_known_gaps = content.replace(known_gaps, "", 1)
    incomplete_marker = re.compile(
        r"(?i)\b(?:TBD|TODO|FIXME|UNKNOWN|N/?A|PLACEHOLDER)\b|"
        r"待补充|待完善|待定|占位符|暂缺|"
        r"(?:^|[\s|：])(?:\.{3,}|…{2,})(?:$|[\s|])"
    )
    if incomplete_marker.search(content_without_known_gaps):
        raise ProjectPrdError("PRD 正文包含未归档的 TBD/TODO/待补充；已知缺口必须集中到第六章")
    placeholder_pattern = re.compile(
        r"\[(?:项目或产品名称|项目版本或代码基线|YYYY-MM-DD|作者|"
        r"功能聚合分类|细分功能名称|例如：|场景|操作|结果|"
        r"用户/|角色|目标页面|限制项|实际文案|相对路径|"
        r"现有单元测试|验证入口|已知证据)[^\]]*\]"
    )
    if placeholder_pattern.search(content):
        raise ProjectPrdError("PRD 仍包含未替换的模板占位符")
    for source in metadata["source_entries"]:
        _validate_evidence_reference(
            str(source), project_root, require_locator=True, evidence_label="source_entries"
        )
    metadata_sources = {str(source) for source in metadata["source_entries"]}
    category_fit = _parse_category_fit(
        metadata["category_fit"],
        category_contract,
        metadata_sources,
        project_root,
    )
    complexity_text = "\n".join(str(item) for item in metadata["complexity_reasons"])
    complex_signals = re.compile(
        r"多阶段|状态机|异步|回调|超时|优先级|拦截器|"
        r"并发|重入|取消|回滚|恢复|清理|跨进程"
    )
    if complexity == "simple" and complex_signals.search(complexity_text):
        raise ProjectPrdError("complexity_reasons 包含复杂流程信号，不得标记为 simple")
    if complexity == "simple" and len(metadata["source_entries"]) >= 3:
        raise ProjectPrdError("三个及以上 source_entries 不得直接标记为 simple")
    if not re.search(r"(?m)^#\s+.+产品需求文档\s*$", content):
        raise ProjectPrdError("PRD 标题必须以‘产品需求文档’结尾")
    header = re.search(
        r"(?m)^>\s*版本：(.+?)\s*\|\s*日期：(\d{4}-\d{2}-\d{2})\s*\|\s*作者：(.+?)\s*$",
        content,
    )
    if header is None:
        raise ProjectPrdError("PRD 缺少标准版本/日期/作者头")
    if header.group(1).strip() != metadata["baseline_version"]:
        raise ProjectPrdError("PRD 文档头版本与 frontmatter.baseline_version 不一致")
    if header.group(2) != metadata["date"]:
        raise ProjectPrdError("PRD 文档头日期与 frontmatter.date 不一致")
    if header.group(3).strip() != metadata["author"]:
        raise ProjectPrdError("PRD 文档头作者与 frontmatter.author 不一致")
    title = re.search(r"(?m)^#\s+(.+)产品需求文档\s*$", content)
    if title is not None and (
        str(metadata["product"]) not in title.group(1)
        or str(metadata["feature"]) not in title.group(1)
    ):
        raise ProjectPrdError("PRD 标题必须同时包含 product 和 feature")

    feature_points = _feature_points(content)
    minimum_feature_points = COMPLEXITY_LIMITS[complexity]["feature_points"]
    if len(feature_points) < minimum_feature_points:
        raise ProjectPrdError(
            f"{complexity} PRD 至少需要 {minimum_feature_points} 个Feature Point项，"
            f"当前只有 {len(feature_points)} 个"
        )
    if len(metadata["decomposition_basis"]) != len(feature_points):
        raise ProjectPrdError(
            "decomposition_basis 必须与 Feature Point 一一对应；每个独立触发、阶段、"
            "策略、外部协作或清理闭环都要先形成拆解依据，再形成一个 FP"
        )
    expected_basis_prefixes = [f"{feature_point_id}:" for feature_point_id, _, _ in feature_points]
    actual_basis = [str(item).strip() for item in metadata["decomposition_basis"]]
    if any(
        re.fullmatch(rf"{re.escape(prefix)}\s*\S.{{3,}}", basis) is None
        for basis, prefix in zip(actual_basis, expected_basis_prefixes)
    ):
        raise ProjectPrdError(
            "decomposition_basis 必须按 FP 顺序使用‘FP-01: 实质拆解理由’格式逐项映射"
        )
    document = _section(content, "## 一、文档说明")
    for heading in ("### 1.1 文档目的", "### 1.3 现有功能概览"):
        if heading not in document:
            raise ProjectPrdError(f"文档说明缺少：{heading}")
    if complexity == "complex":
        for heading in ("### 1.2 产品定位", "### 1.4 术语表"):
            if heading not in document:
                raise ProjectPrdError(f"complex PRD 文档说明缺少：{heading}")
        glossary = document.split("### 1.4 术语表", 1)[1]
        if not re.search(r"(?m)^-\s+\*\*.+?\*\*：\s*\S+", glossary):
            raise ProjectPrdError("complex PRD 术语表至少需要 1 个真实领域术语")
    overview_rows = _table_rows(document, ("模块", "功能点", "已有能力"))

    feature_point_ids = [item[0] for item in feature_points]
    decomposition_candidates = _parse_decomposition_candidates(
        metadata["decomposition_candidates"],
        feature_point_ids,
        metadata_sources,
        project_root,
        complexity,
    )
    if len(overview_rows) != len(feature_points):
        raise ProjectPrdError("现有功能概览必须与 Feature Point 一一对应")
    overview_ids = []
    for row in overview_rows:
        match = re.match(r"^(FP-\d{2,})\b", row[1])
        overview_ids.append(match.group(1) if match else "")
    if overview_ids != feature_point_ids:
        raise ProjectPrdError("现有功能概览的‘功能点’列必须按顺序与 FP 一一对应")

    interaction_steps: list[str] = []
    positive_rows: list[list[str]] = []
    negative_rows: list[list[str]] = []
    exception_rows: list[list[str]] = []
    exception_sources_by_point: dict[str, set[str]] = {}
    per_point_interactions: dict[str, int] = {}
    for feature_point_id, _, block in feature_points:
        actual_markers = re.findall(r"(?m)^\*\*(\d+)\.\s*([^*]+?)\*\*\s*$", block)
        expected_markers = [(str(index), name) for index, name in FEATURE_POINT_SECTIONS]
        if actual_markers != expected_markers:
            raise ProjectPrdError(
                f"{feature_point_id} 必须按固定顺序且恰好一次包含 prd-writer 完整 7 章节"
            )
        subsections = {
            name: _feature_subsection(block, index, name, feature_point_id)
            for index, name in FEATURE_POINT_SECTIONS
        }
        description = subsections["功能描述"]
        for label in ("是什么", "用户痛点", "业务价值"):
            if not re.search(rf"\*\*{label}\*\*：\s*\S+", description):
                raise ProjectPrdError(f"{feature_point_id} 功能描述缺少非空的‘{label}’")
        if "**为什么**：" not in description:
            raise ProjectPrdError(f"{feature_point_id} 功能描述缺少‘为什么’")

        point_steps = re.findall(r"(?m)^\d+\.\s+(.+)$", subsections["交互逻辑"])
        minimum_steps = 1
        if len(point_steps) < minimum_steps:
            raise ProjectPrdError(
                f"{feature_point_id} 至少需要 {minimum_steps} 个具体交互步骤，"
                "不得只用一句话概括完整子流程"
            )
        if any(len(step.strip()) < 10 for step in point_steps):
            raise ProjectPrdError(f"{feature_point_id} 交互步骤必须描述具体动作和系统响应")
        per_point_interactions[feature_point_id] = len(point_steps)
        interaction_steps.extend(point_steps)

        jump = subsections["跳转逻辑"]
        if "无页面跳转" not in jump:
            _any_table_rows(jump, label=f"{feature_point_id} 跳转逻辑")
        jump_process = subsections["跳转过程逻辑"]
        if len(jump_process) < 12 or ("→" not in jump_process and "不涉及" not in jump_process and "- " not in jump_process):
            raise ProjectPrdError(
                f"{feature_point_id} 跳转过程逻辑必须展开中间处理，或明确写‘不涉及页面跳转’"
            )

        point_positive = _table_rows(subsections["正向限制"], ("项目", "限制"))
        point_negative = _table_rows(subsections["反向限制"], ("项目", "说明"))
        point_exceptions = _table_rows(
            subsections["异常/空态/错误提示"], ("场景", "提示内容", "展示方式", "源码证据")
        )
        if not point_positive or not point_negative or not point_exceptions:
            raise ProjectPrdError(f"{feature_point_id} 的正向限制、反向限制和异常表均不得为空")
        positive_rows.extend(point_positive)
        negative_rows.extend(point_negative)
        exception_rows.extend(point_exceptions)
        point_exception_sources: set[str] = set()
        for row in point_exceptions:
            references = _code_references(
                row[3], evidence_label=f"{feature_point_id} 异常项源码证据"
            )
            point_exception_sources.update(references)
            for reference in references:
                if reference not in metadata_sources:
                    raise ProjectPrdError(
                        f"{feature_point_id} 异常项证据必须同时登记在 source_entries：{reference}"
                    )
                _validate_evidence_reference(
                    reference,
                    project_root,
                    require_locator=True,
                    evidence_label=f"{feature_point_id} 异常项",
                )
            row_text = " ".join(row[:3])
            if "超时" in row_text and not re.search(r"不适用|无超时", row_text) and not _source_has_signal(
                references,
                project_root,
                re.compile(r"(?i)timeout|setTimeout|setInterval|timer|countdown|超时|倒计时"),
            ):
                raise ProjectPrdError(f"{feature_point_id} 的超时声明缺少真实计时/超时源码证据")
            if "权限不足" in row[0] and "不适用" not in row_text and not _source_has_signal(
                references,
                project_root,
                re.compile(r"(?i)permission|authorization|authorisation|\bauth\b|\brole\b|acl|权限|鉴权"),
            ):
                raise ProjectPrdError(f"{feature_point_id} 的权限不足声明缺少真实权限判断源码证据")
            if re.search(r"(?i)toast", row[2]) and not _source_has_signal(
                references, project_root, re.compile(r"(?i)toast")
            ):
                raise ProjectPrdError(f"{feature_point_id} 声明 Toast，但源码证据没有 Toast 行为")
            if re.search(r"(?i)dialog|弹窗", row[2]) and not _source_has_signal(
                references, project_root, re.compile(r"(?i)dialog|弹窗")
            ):
                raise ProjectPrdError(f"{feature_point_id} 声明弹窗，但源码证据没有弹窗行为")
            if project_root is not None and not re.search(r"不适用", row_text):
                source_scope = "\n".join(
                    _source_reference_text(reference, project_root) for reference in references
                )
                category_patterns = {
                    "空态": re.compile(r"(?i)\bnone\b|\bnull\b|empty|isEmpty|!\s*\w+|空"),
                    "操作失败": re.compile(r"(?i)\btry\b|\bcatch\b|\bexcept\b|error|fail|throw|reject|失败|异常"),
                    "网络异常": re.compile(r"(?i)network|http|socket|request|response|网络"),
                    "边界超限": re.compile(r"(?i)\bif\b|\bwhen\b|\bcase\b|>=|<=|==|!=|invalid|limit|重复|边界"),
                }
                for category, pattern in category_patterns.items():
                    if category in row[0] and not pattern.search(source_scope):
                        raise ProjectPrdError(
                            f"{feature_point_id} 的{category}声明缺少同一 Symbol/行号范围内的分支证据"
                        )
                display_patterns = {
                    "空态页": re.compile(r"(?i)empty|空态"),
                    "状态条": re.compile(r"(?i)status|state|状态"),
                    "内联": re.compile(r"(?i)inline|state|status|内联"),
                    "接口返回": re.compile(r"(?i)\breturn\b|resolve|reject"),
                    "系统事件": re.compile(r"(?i)event|emit|notify|callback|\breturn\b|事件|通知"),
                    "日志": re.compile(r"(?i)\blog\w*\b|logger|hilog|日志"),
                }
                for display, pattern in display_patterns.items():
                    if display in row[2] and not pattern.search(source_scope):
                        raise ProjectPrdError(
                            f"{feature_point_id} 的展示方式‘{row[2]}’缺少同一 Symbol/行号范围内的源码证据"
                        )
        exception_sources_by_point[feature_point_id] = point_exception_sources

    missing_categories = [
        item for item in EXCEPTION_CATEGORIES
        if not any(row and item in row[0] for row in exception_rows)
    ]
    if missing_categories:
        raise ProjectPrdError("异常提示表缺少类别：" + "、".join(missing_categories))
    vague_displays = [row for row in exception_rows if len(row) >= 3 and row[2].strip() == "提示"]
    if vague_displays:
        raise ProjectPrdError("异常展示方式不能只写‘提示’")
    content_rows = [*positive_rows, *negative_rows, *exception_rows]
    if any(any(cell.strip() in {"-", "--", "同上", "略"} for cell in row) for row in content_rows):
        raise ProjectPrdError("PRD 表格不得使用‘-’、‘同上’或‘略’代替具体内容")
    for label, rows in (
        ("正向限制", positive_rows),
        ("反向限制", negative_rows),
        ("异常提示", exception_rows),
    ):
        if len({tuple(row) for row in rows}) != len(rows):
            raise ProjectPrdError(f"{label}表存在重复的占位内容")

    relationship = _section(content, "## 三、功能关联与闭环关系")
    if "关键闭环链路" not in relationship or not re.search(r"(?m)^\d+\.\s+.+→.+", relationship):
        raise ProjectPrdError("功能关联与闭环关系必须包含至少一条关键闭环链路")
    for feature_point_id in feature_point_ids:
        if feature_point_id not in relationship:
            raise ProjectPrdError(f"功能关联与闭环关系未纳入 {feature_point_id}")
    diagram_count = _validate_business_flow_diagram(
        relationship, feature_point_ids, decomposition_candidates, complexity
    )
    rule_matrices, matrix_sources_by_point = _parse_rule_matrices(
        relationship,
        feature_point_ids,
        metadata_sources,
        project_root,
        complexity_text,
    )

    coverage = _section(content, "## 四、行为覆盖与代码追溯")
    behavior_rows = _table_rows(
        coverage, ("Behavior ID", "功能点", "源码证据", "用户可感知行为", "PRD 章节")
    )
    behavior_ids = [row[0] for row in behavior_rows if row and re.fullmatch(r"B\d{3,}", row[0])]
    if len(behavior_ids) != len(behavior_rows):
        raise ProjectPrdError("行为覆盖表每行必须使用唯一 B### Behavior ID")
    if len(behavior_ids) != len(set(behavior_ids)):
        raise ProjectPrdError("行为覆盖表的 Behavior ID 必须唯一")
    if any(row[1] not in feature_point_ids for row in behavior_rows):
        raise ProjectPrdError("行为覆盖表的功能点必须引用当前 PRD 中的 FP-##")
    if any(len(row[2].strip("` ")) < 4 or len(row[3].strip()) < 4 for row in behavior_rows):
        raise ProjectPrdError("行为覆盖表的源码证据和可感知行为必须具体")
    behavior_source_references: set[str] = set()
    behavior_sources_by_point: dict[str, set[str]] = {
        feature_point_id: set() for feature_point_id in feature_point_ids
    }
    for row in behavior_rows:
        for reference in _code_references(row[2], evidence_label=f"Behavior {row[0]} 源码证据"):
            behavior_source_references.add(reference)
            behavior_sources_by_point[row[1]].add(reference)
            _validate_evidence_reference(
                reference,
                project_root,
                require_locator=True,
                evidence_label=f"Behavior {row[0]} 源码证据",
            )
    valid_mappings = {
        "功能描述", "交互逻辑", "跳转逻辑", "跳转过程逻辑", "正向限制",
        "反向限制", "异常提示", "功能关联与闭环关系",
    }
    invalid_mappings = [row[4] for row in behavior_rows if row[4] not in valid_mappings]
    if invalid_mappings:
        raise ProjectPrdError("行为覆盖表包含无效 PRD 章节：" + "、".join(invalid_mappings))
    main_mappings = {"功能描述", "交互逻辑", "跳转逻辑", "跳转过程逻辑", "功能关联与闭环关系"}
    boundary_mappings = {"正向限制", "反向限制", "异常提示"}
    for feature_point_id in feature_point_ids:
        point_mappings = {row[4] for row in behavior_rows if row[1] == feature_point_id}
        if not point_mappings:
            raise ProjectPrdError(
                f"{feature_point_id} 至少需要 1 个独立 Behavior"
            )
        if complexity in {"standard", "complex"} and (
            not point_mappings.intersection(main_mappings)
            or not point_mappings.intersection(boundary_mappings)
        ):
            raise ProjectPrdError(
                f"{feature_point_id} 必须同时映射主路径 Behavior 和限制/异常 Behavior"
            )
    for candidate in decomposition_candidates:
        missing_references = set(candidate["references"]) - behavior_sources_by_point[
            candidate["feature_point_id"]
        ]
        if missing_references:
            raise ProjectPrdError(
                f"拆解候选 {candidate['id']} 的源码证据必须由同一 FP 的 Behavior 覆盖："
                + "、".join(sorted(missing_references))
            )
    for feature_point_id, references in exception_sources_by_point.items():
        missing_references = references - behavior_sources_by_point[feature_point_id]
        if missing_references:
            raise ProjectPrdError(
                f"{feature_point_id} 异常项源码证据必须由同一 FP 的 Behavior 覆盖："
                + "、".join(sorted(missing_references))
            )
    for feature_point_id, references in matrix_sources_by_point.items():
        missing_references = references - behavior_sources_by_point[feature_point_id]
        if missing_references:
            raise ProjectPrdError(
                f"{feature_point_id} 规则矩阵源码证据必须由同一 FP 的 Behavior 覆盖："
                + "、".join(sorted(missing_references))
            )
    if metadata_sources != behavior_source_references:
        missing_sources = sorted(metadata_sources - behavior_source_references)
        extra_sources = sorted(behavior_source_references - metadata_sources)
        details: list[str] = []
        if missing_sources:
            details.append("未映射=" + "、".join(missing_sources))
        if extra_sources:
            details.append("未登记=" + "、".join(extra_sources))
        raise ProjectPrdError("source_entries 必须与 Behavior 源码证据集合精确一致：" + "；".join(details))
    verification = _section(content, "## 五、验证依据")
    for behavior_id in behavior_ids:
        mapping = re.search(
            rf"(?m)^\s*-\s*{re.escape(behavior_id)}\s*→\s*(.+?)\s*$", verification
        )
        if mapping is None:
            raise ProjectPrdError(f"验证依据未映射 Behavior ID：{behavior_id}")
        evidence = mapping.group(1).strip()
        if re.fullmatch(r"缺少自动化验证(?:：.+)?", evidence):
            continue
        references = _code_references(evidence, evidence_label=f"{behavior_id} 验证依据")
        for reference in references:
            source_path, _ = _split_evidence_reference(reference)
            if not _is_test_evidence_path(source_path):
                raise ProjectPrdError(
                    f"{behavior_id} 验证依据必须指向测试目录或测试命名文件：{reference}"
                )
            _validate_evidence_reference(
                reference,
                project_root,
                require_locator=False,
                evidence_label=f"{behavior_id} 验证依据",
            )

    if not re.search(r"无已知(?:未实现项|缺口|待确认项)", known_gaps):
        _table_rows(known_gaps, ("项目", "证据位置", "当前表现", "影响"))

    counts = {
        "function_point_count": len(feature_points),
        "candidate_count": len(decomposition_candidates),
        "matrix_count": len(rule_matrices),
        "diagram_count": diagram_count,
        "interaction_count": len(interaction_steps),
        "positive_constraint_count": len(positive_rows),
        "negative_constraint_count": len(negative_rows),
        "exception_count": len(exception_rows),
        "behavior_count": len(behavior_rows),
    }
    limits = COMPLEXITY_LIMITS[complexity]
    checks = (
        ("function_point_count", "Feature Point", limits["feature_points"]),
        ("interaction_count", "交互步骤", limits["interaction"]),
        ("positive_constraint_count", "正向限制", limits["positive"]),
        ("negative_constraint_count", "反向限制", limits["negative"]),
        ("behavior_count", "行为覆盖", limits["behavior"]),
    )
    for key, label, minimum in checks:
        if counts[key] < minimum:
            raise ProjectPrdError(
                f"{complexity} PRD 至少需要 {minimum} 个{label}项，当前只有 {counts[key]} 个"
            )

    if relative_path is not None:
        path_category, feature = _path_parts(relative_path)
        if metadata["category"] != path_category:
            raise ProjectPrdError(f"category 元数据 {metadata['category']} 与目录 {path_category} 不一致")
        if metadata["feature"] != feature:
            raise ProjectPrdError(f"feature 元数据 {metadata['feature']} 与文件名 {feature} 不一致")
    metadata["_category_contract"] = category_contract
    metadata["_category_fit_dimensions"] = sorted(category_fit)
    metadata.update(counts)
    return metadata


def classify_workspace_path(relative: Path) -> str:
    """Classify a relative .project-prd path as prd, resource, control, or ignored."""
    if relative.is_absolute() or not relative.parts or any(
        part in {"", ".", ".."}
        or any(ord(character) < 32 or ord(character) == 127 for character in part)
        for part in relative.parts
    ):
        raise ProjectPrdError(f".project-prd 相对路径无效：{relative}")
    relative_text = relative.as_posix()
    if relative_text in CONTROL_PLANE_FILES or relative.parts[0] in CONTROL_PLANE_DIRECTORIES:
        return "control"
    if "__pycache__" in relative.parts or relative.suffix == ".pyc":
        return "ignored"
    if len(relative.parts) == 2 and relative.suffix == ".md":
        return "prd"
    return "resource"


def list_prd_files(workspace: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in workspace.rglob("*.md"):
        ensure_no_symlink_path(workspace, path)
        relative = path.relative_to(workspace)
        if not path.is_file() or classify_workspace_path(relative) != "prd":
            continue
        _path_parts(relative)
        candidates.append(path)
    return sorted(candidates, key=lambda item: item.as_posix())


def collect_prd_metadata(workspace: Path) -> list[tuple[Path, dict[str, Any]]]:
    results: list[tuple[Path, dict[str, Any]]] = []
    prd_ids: set[str] = set()
    for path in list_prd_files(workspace):
        relative = path.relative_to(workspace)
        metadata = validate_prd(path.read_text(encoding="utf-8"), relative, workspace.parent)
        prd_id = str(metadata["prd_id"])
        if prd_id in prd_ids:
            raise ProjectPrdError(f"prd_id 重复：{prd_id}")
        prd_ids.add(prd_id)
        results.append((relative, metadata))
    if not results:
        raise ProjectPrdError("没有发现任何两级功能 PRD")
    category_contracts: dict[str, tuple[str, str, tuple[tuple[str, str], ...]]] = {}
    category_shared_dimensions: dict[str, set[str]] = {}
    for _, metadata in results:
        category = str(metadata["category"])
        contract = (
            str(metadata["category_domain"]).strip(),
            str(metadata["category_goal"]).strip(),
            tuple(metadata["_category_contract"].items()),
        )
        previous = category_contracts.setdefault(category, contract)
        if previous != contract:
            raise ProjectPrdError(
                f"一级分类‘{category}’成员的 category_domain/category_goal/category_contract 不一致；"
                "不共享同一业务对象和用户结果的功能必须拆分分类"
            )
        fit_dimensions = set(metadata["_category_fit_dimensions"])
        if category not in category_shared_dimensions:
            category_shared_dimensions[category] = fit_dimensions
        else:
            category_shared_dimensions[category].intersection_update(fit_dimensions)
    for category, dimensions in category_shared_dimensions.items():
        if len(dimensions) < 2:
            raise ProjectPrdError(
                f"一级分类‘{category}’所有成员共同有源码证据的聚合维度少于两个；请拆分分类"
            )
    return results


def generate_index(workspace: Path) -> str:
    rows: list[str] = []
    for relative, metadata in collect_prd_metadata(workspace):
        source_text = "<br>".join(str(item) for item in metadata["source_entries"])
        rows.append(
            f"| {metadata['category']} | [{metadata['feature']}]({relative.as_posix()}) | "
            f"`{metadata['prd_id']}` | {metadata['complexity']} | "
            f"{metadata['function_point_count']} | {metadata['candidate_count']} | {metadata['matrix_count']} | {metadata['diagram_count']} | "
            f"{metadata['interaction_count']} | {metadata['positive_constraint_count']} | "
            f"{metadata['negative_constraint_count']} | {metadata['exception_count']} | "
            f"{metadata['behavior_count']} | {metadata['status']} | {source_text} |"
        )
    return (
        "# Project PRD Index\n\n"
        "> 本文件由 project-prd 生成。不得直接修改；PRD 变更请使用 project-prd-edit。\n\n"
        "| 功能分类 | 细分功能 | PRD ID | 复杂度 | Feature Points | Candidates | Matrices | Diagrams | 交互步骤 | 正向限制 | 反向限制 | 异常项 | Behaviors | 状态 | 代码入口 |\n"
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|\n"
        + "\n".join(rows) + "\n"
    )


def compute_prd_hashes(workspace: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in list_prd_files(workspace):
        relative = path.relative_to(workspace).as_posix()
        hashes[relative] = sha256_text(path.read_text(encoding="utf-8"))
    return dict(sorted(hashes.items()))


def list_resource_files(workspace: Path) -> list[Path]:
    resources: list[Path] = []
    for path in sorted(workspace.rglob("*")):
        ensure_no_symlink_path(workspace, path)
        if path.is_file() and classify_workspace_path(path.relative_to(workspace)) == "resource":
            resources.append(path)
    return resources


def compute_editable_hashes(
    workspace: Path,
    excluded_resources: set[str] | None = None,
) -> dict[str, str]:
    excluded = set(excluded_resources or set())
    hashes = compute_prd_hashes(workspace)
    for path in list_resource_files(workspace):
        relative = path.relative_to(workspace).as_posix()
        if relative in excluded:
            continue
        try:
            hashes[relative] = sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise ProjectPrdError(f"无法读取 PRD 资源文件：{path}: {exc}") from exc
    return dict(sorted(hashes.items()))


def compute_hashes(
    workspace: Path,
    excluded_resources: set[str] | None = None,
) -> dict[str, str]:
    excluded = set(excluded_resources or set())
    resource_paths = list_resource_files(workspace)
    hashes = compute_control_hashes(workspace)
    hashes.update(compute_prd_hashes(workspace))
    for path in resource_paths:
        relative = path.relative_to(workspace).as_posix()
        if relative in excluded:
            continue
        try:
            hashes[relative] = sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise ProjectPrdError(f"无法读取 PRD 资源文件：{path}: {exc}") from exc
    return dict(sorted(hashes.items()))


def compute_control_hashes(workspace: Path) -> dict[str, str]:
    paths = [
        workspace / "INDEX.md",
        workspace / OWNER_FILE,
        workspace / "tools" / "project_prd_lib.py",
        workspace / "tools" / "project_prd_guard.py",
        *sorted((workspace / ".history").glob("*.json")),
    ]
    hashes: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            raise ProjectPrdError(f"PRD 基线文件不存在：{path}")
        relative = path.relative_to(workspace).as_posix()
        try:
            hashes[relative] = sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise ProjectPrdError(f"无法读取 PRD 基线文件：{path}: {exc}") from exc
    return dict(sorted(hashes.items()))


def _receipt_changes(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    changes = receipt.get("changes")
    if changes is None:
        return [{
            "operation": receipt.get("operation"),
            "target": receipt.get("target"),
            "before_sha256": receipt.get("before_sha256"),
            "after_sha256": receipt.get("after_sha256"),
        }]
    if not isinstance(changes, list) or not changes or any(not isinstance(item, dict) for item in changes):
        raise ProjectPrdError("authorized-prd-edit.changes 必须是非空对象数组")
    targets = [item.get("target") for item in changes]
    if any(not isinstance(target, str) for target in targets) or len(targets) != len(set(targets)):
        raise ProjectPrdError("authorized-prd-edit.changes 的 target 必须是唯一字符串")
    return changes


def check_integrity(
    project_root: Path,
    allowed_untracked_resources: set[str] | None = None,
) -> tuple[bool, list[str]]:
    workspace = project_root / ".project-prd"
    errors: list[str] = []
    try:
        requested_untracked_resources = set(allowed_untracked_resources or set())
        for raw_target in requested_untracked_resources:
            target = Path(raw_target)
            if target.is_absolute() or classify_workspace_path(target) != "resource":
                raise ProjectPrdError(f"不允许忽略非资源目标：{raw_target}")
        manifest = read_json(workspace / "manifest.json")
        owner = read_json(workspace / OWNER_FILE)
        if owner != {
            "owner": "project-prd",
            "format_version": FORMAT_VERSION,
            "installed_skills": ["project-prd-edit", "project-prd-verify", "project-prd-clear", "project-prd-serve"],
        }:
            errors.append("project-prd 工作区归属标记无效")
        if manifest.get("format_version") != FORMAT_VERSION:
            errors.append("manifest format_version 不匹配")
        if manifest.get("status") != "complete":
            errors.append("manifest 状态不是 complete")
        expected = manifest.get("files")
        if not isinstance(expected, dict):
            errors.append("manifest.files 无效")
            expected = {}
        ignored_resources = requested_untracked_resources - set(expected)
        comparable_actual = compute_hashes(workspace, ignored_resources)
        metadata = collect_prd_metadata(workspace)
        canonical_index = generate_index(workspace)
        index_path = workspace / "INDEX.md"
        if index_path.read_text(encoding="utf-8") != canonical_index:
            errors.append("INDEX.md 与当前 PRD 元数据生成结果不一致")
        expected_summary = {
            "prd_count": len(metadata),
            "function_point_count": sum(int(item[1]["function_point_count"]) for item in metadata),
            "candidate_count": sum(int(item[1]["candidate_count"]) for item in metadata),
            "matrix_count": sum(int(item[1]["matrix_count"]) for item in metadata),
            "diagram_count": sum(int(item[1]["diagram_count"]) for item in metadata),
            "interaction_count": sum(int(item[1]["interaction_count"]) for item in metadata),
            "positive_constraint_count": sum(int(item[1]["positive_constraint_count"]) for item in metadata),
            "negative_constraint_count": sum(int(item[1]["negative_constraint_count"]) for item in metadata),
            "exception_count": sum(int(item[1]["exception_count"]) for item in metadata),
            "behavior_count": sum(int(item[1]["behavior_count"]) for item in metadata),
            "complexity_counts": {
                level: sum(1 for item in metadata if item[1]["complexity"] == level)
                for level in ("simple", "standard", "complex")
            },
        }
        for key, value in expected_summary.items():
            if manifest.get(key) != value:
                errors.append(f"manifest.{key} 与 PRD 实际统计不一致")
        generation = manifest.get("edit_generation")
        if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
            errors.append("manifest.edit_generation 必须是非负整数")
            generation = -1
        receipt_raw = manifest.get("last_authorized_edit")
        receipt_relative = Path(str(receipt_raw)) if receipt_raw else Path()
        receipt: dict[str, Any] = {}
        if (
            not receipt_raw
            or receipt_relative.is_absolute()
            or len(receipt_relative.parts) != 2
            or receipt_relative.parts[0] != ".history"
            or receipt_relative.suffix != ".json"
            or any(part in {"", ".", ".."} for part in receipt_relative.parts)
        ):
            errors.append("manifest.last_authorized_edit 必须指向 .history/<receipt>.json")
        else:
            try:
                receipt = read_json(workspace / receipt_relative)
            except ProjectPrdError as exc:
                errors.append(str(exc))
        if receipt:
            if receipt.get("format_version") != FORMAT_VERSION:
                errors.append("最后审计记录 format_version 不匹配")
            if generation == 0:
                if receipt.get("type") != "initialization" or receipt_relative != Path(".history/initialization.json"):
                    errors.append("初始基线必须指向 initialization 审计记录")
                for key, value in expected_summary.items():
                    if receipt.get(key) != value:
                        errors.append(f"初始化审计记录.{key} 与 PRD 实际统计不一致")
            else:
                if receipt.get("type") != "authorized-prd-edit":
                    errors.append("最后审计记录不是 authorized-prd-edit")
                if receipt.get("generation") != generation:
                    errors.append("审计记录 generation 与 manifest.edit_generation 不一致")
                if receipt.get("timestamp") != manifest.get("updated_at"):
                    errors.append("审计记录 timestamp 与 manifest.updated_at 不一致")
                for change in _receipt_changes(receipt):
                    target = change.get("target")
                    operation = change.get("operation")
                    after_hash = change.get("after_sha256")
                    if operation in {"create", "update"} and (
                        not isinstance(target, str) or expected.get(target) != after_hash
                    ):
                        errors.append("审计记录的目标哈希与 manifest.files 不一致")
                    if operation == "delete" and (
                        not isinstance(target, str) or target in comparable_actual or after_hash is not None
                    ):
                        errors.append("删除审计记录与当前 PRD 集不一致")
        history_paths = sorted((workspace / ".history").glob("*.json"))
        receipts_by_generation: dict[int, tuple[Path, dict[str, Any]]] = {}
        for history_path in history_paths:
            try:
                history_item = read_json(history_path)
            except ProjectPrdError as exc:
                errors.append(str(exc))
                continue
            if history_item.get("format_version") != FORMAT_VERSION:
                errors.append(f"审计记录 format_version 不匹配：{history_path.name}")
            if history_item.get("type") == "skill-update":
                installed_skills = history_item.get("installed_skills")
                if not isinstance(installed_skills, list) or any(
                    not isinstance(item, str) for item in installed_skills
                ):
                    errors.append(f"skill-update 审计记录 installed_skills 无效：{history_path.name}")
                install_dir = history_item.get("skill_install_dir")
                install_path = Path(str(install_dir)) if isinstance(install_dir, str) else Path()
                if (
                    not isinstance(install_dir, str)
                    or not install_dir
                    or install_path.is_absolute()
                    or any(part in {"", ".", ".."} for part in install_path.parts)
                ):
                    errors.append(f"skill-update 审计记录 skill_install_dir 无效：{history_path.name}")
                continue
            item_generation = history_item.get("generation")
            if isinstance(item_generation, bool) or not isinstance(item_generation, int):
                errors.append(f"审计记录缺少有效 generation：{history_path.name}")
                continue
            if item_generation in receipts_by_generation:
                errors.append(f"审计 generation 重复：{item_generation}")
                continue
            receipts_by_generation[item_generation] = (history_path, history_item)
        if generation >= 0 and set(receipts_by_generation) != set(range(generation + 1)):
            errors.append("审计记录 generation 必须从 0 到 edit_generation 连续")
        ledger: dict[str, str] = {}
        previous_path: str | None = None
        for item_generation in sorted(receipts_by_generation):
            history_path, history_item = receipts_by_generation[item_generation]
            relative_history = history_path.relative_to(workspace).as_posix()
            if item_generation == 0:
                if history_item.get("type") != "initialization":
                    errors.append("generation 0 必须是 initialization")
                initial_files = history_item.get("editable_files", history_item.get("prd_files"))
                if not isinstance(initial_files, dict):
                    errors.append("初始化审计记录缺少 editable_files/prd_files")
                else:
                    ledger = {str(key): str(value) for key, value in initial_files.items()}
            else:
                if history_item.get("type") != "authorized-prd-edit":
                    errors.append(f"generation {item_generation} 不是 authorized-prd-edit")
                if history_item.get("previous_receipt") != previous_path:
                    errors.append(f"generation {item_generation} 的 previous_receipt 链接无效")
                for change in _receipt_changes(history_item):
                    target = change.get("target")
                    operation = change.get("operation")
                    before_hash = change.get("before_sha256")
                    after_hash = change.get("after_sha256")
                    if not isinstance(target, str):
                        errors.append(f"generation {item_generation} 缺少 target")
                    elif operation == "create":
                        if target in ledger or before_hash is not None or not isinstance(after_hash, str):
                            errors.append(f"generation {item_generation} create 哈希链无效")
                        else:
                            ledger[target] = after_hash
                    elif operation == "update":
                        if ledger.get(target) != before_hash or not isinstance(after_hash, str):
                            errors.append(f"generation {item_generation} update 前后哈希链无效")
                        else:
                            ledger[target] = after_hash
                    elif operation == "delete":
                        tracked_delete = target in ledger
                        if (
                            after_hash is not None
                            or (tracked_delete and ledger.get(target) != before_hash)
                            or (not tracked_delete and before_hash is not None)
                        ):
                            errors.append(f"generation {item_generation} delete 前后哈希链无效")
                        else:
                            ledger.pop(target, None)
                    else:
                        errors.append(f"generation {item_generation} operation 无效")
            previous_path = relative_history
        current_editable = {
            path: digest
            for path, digest in compute_editable_hashes(workspace, ignored_resources).items()
            if path not in ignored_resources
        }
        if receipts_by_generation and ledger != current_editable:
            errors.append("审计链重建的 PRD/资源哈希与当前文件不一致")
        if previous_path is not None and previous_path != receipt_raw:
            errors.append("manifest.last_authorized_edit 不是审计链最后一条")
        for path in sorted(set(expected) - set(comparable_actual)):
            errors.append(f"PRD 基线文件缺失：{path}")
        for path in sorted(set(comparable_actual) - set(expected)):
            errors.append(f"发现未登记 PRD/资源文件：{path}")
        for path in sorted(set(comparable_actual).intersection(expected)):
            if comparable_actual[path] != expected[path]:
                errors.append(f"PRD/资源文件未经受控入口修改：{path}")
        agents_path = project_root / "AGENTS.md"
        agents_content = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
        if agents_content.count(MANAGED_START) != 1 or agents_content.count(MANAGED_END) != 1:
            errors.append("AGENTS.md 缺少 project-prd 受管规则")
    except ProjectPrdError as exc:
        errors.append(str(exc))
    return not errors, errors
