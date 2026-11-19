"""相似检测：正向 skill 对公司库 catalog 语义比对，产出相似 skill 列表。

复用 :func:`skill_recommend.pipeline.build_company_match_commands` 生成命令，
执行后读取公司库比对报告，经 :func:`skill_recommend.tier2.parse_similarity_report`
与阈值过滤，返回候选列表供用户选择。
"""

from __future__ import annotations

from pathlib import Path

from .config import SIMILAR_THRESHOLD, project_root
from .pipeline import (
    COMPANY_MATCH_DIR,
    SIMILARITY_REPORT,
    Executor,
    _output_subdir,
    _shell_executor,
    build_company_match_commands,
)
from .tier2 import matches_above_threshold, parse_similarity_report


def detect_report_path(base_rel: str) -> Path:
    """公司库比对报告（宿主机路径）。"""
    return project_root() / "reports" / COMPANY_MATCH_DIR / _output_subdir(base_rel) / SIMILARITY_REPORT


def detect_similar(
    base_rel: str,
    *,
    library_rel: str = "library-20261118",
    threshold: float = SIMILAR_THRESHOLD,
    run: bool = False,
    executor: Executor | None = None,
) -> dict:
    """建公司库 catalog + 正向 skill 比对，返回命中（相似度 >= threshold）。

    dry-run 只打印命令；``run=True`` 时顺序执行并在成功后解析报告。
    """
    commands = build_company_match_commands([base_rel], library_rel)
    report_path = detect_report_path(base_rel)

    if not run:
        for c in commands:
            print(" ".join(c))
        return {
            "commands": commands,
            "report_path": str(report_path),
            "matches": [],
            "executed": False,
        }

    run_executor = executor or _shell_executor
    for c in commands:
        rc = run_executor(c)
        if rc != 0:
            return {
                "commands": commands,
                "report_path": str(report_path),
                "matches": [],
                "executed": False,
                "failed_command": c,
                "returncode": rc,
            }

    matches = matches_above_threshold(parse_similarity_report(report_path), threshold)
    return {
        "commands": commands,
        "report_path": str(report_path),
        "matches": matches,
        "executed": True,
    }
