"""联网搜索补充候选：调用公司库 cskills CLI。

仅依赖 ``cskills`` 命令（需已登录）。解析 ``cskills find`` 的文本输出；
``cskills info`` 返回原文供报告展示，不做结构化解析。
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from .models import ExternalCandidate
from .tier2 import parse_similarity_report

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
_NAME_BLACKLIST = {"by", "tags", "v", "install"}


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _run_cskills(*args: str, timeout: float = 60.0) -> str | None:
    if shutil.which("cskills") is None:
        return None
    try:
        proc = subprocess.run(
            ["cskills", *args], capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout or ""


def _parse_find_output(clean_text: str) -> list[tuple[str, str]]:
    """从去色后的 ``cskills find`` 输出提取 (name, description) 列表。"""
    results: list[tuple[str, str]] = []
    for line in clean_text.splitlines():
        s = line.strip()
        if not s or s.startswith(("Found", "Install:", "tags:")):
            continue
        parts = s.split(None, 1)
        name = parts[0]
        if name in _NAME_BLACKLIST or not _NAME_RE.match(name):
            continue
        desc = parts[1].strip() if len(parts) > 1 else ""
        results.append((name, desc))
    return results


def search_skills(keyword: str) -> list[ExternalCandidate]:
    """搜索公司库，返回候选 skill（默认未实测）。"""
    out = _run_cskills("find", keyword)
    if out is None:
        return []
    candidates = []
    for name, desc in _parse_find_output(strip_ansi(out)):
        candidates.append(
            ExternalCandidate(name=name, source="cskills", description=desc, evaluated=False)
        )
    return candidates


def skill_info(name: str) -> str | None:
    """返回 ``cskills info <name>`` 的去色原文；失败返回 None。"""
    out = _run_cskills("info", name)
    if out is None:
        return None
    return strip_ansi(out)


def semantic_candidates_from_report(report_path: Path | str) -> list[ExternalCandidate]:
    """从公司库语义匹配的 similarity 报告解析候选（带 embedding 分数）。

    复用 :func:`skill_recommend.tier2.parse_similarity_report`，把每条命中映射为
    ``evaluated=True`` 的 ``ExternalCandidate``（name=catalog_skill，source=company-library）。
    """
    matches = parse_similarity_report(report_path)
    candidates: list[ExternalCandidate] = []
    for m in matches:
        candidates.append(
            ExternalCandidate(
                name=m.catalog_skill,
                source="company-library",
                similarity=m.similarity,
                evaluated=True,
            )
        )
    return candidates


def merge_candidates(
    keyword_cands: list[ExternalCandidate],
    semantic_cands: list[ExternalCandidate],
) -> list[ExternalCandidate]:
    """合并关键词候选与语义候选：语义候选（带分数）排前，同名去重。

    同名时保留带分数的语义候选，并把关键词候选的描述附上；纯关键词候选排后。
    """
    merged: dict[str, ExternalCandidate] = {}
    for c in semantic_cands:
        merged[c.name] = c
    for c in keyword_cands:
        existing = merged.get(c.name)
        if existing is None:
            merged[c.name] = c
        elif c.description and c.description not in existing.description:
            existing.description = (
                f"{existing.description}；{c.description}" if existing.description else c.description
            )

    semantic = sorted(
        (c for c in merged.values() if c.similarity is not None),
        key=lambda c: c.similarity if c.similarity is not None else -1.0,
        reverse=True,
    )
    keyword = [c for c in merged.values() if c.similarity is None]
    return semantic + keyword
