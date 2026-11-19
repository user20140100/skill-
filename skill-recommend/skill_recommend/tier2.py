"""Tier2 相似度报告解析：提取冗余命中的 skill 对。

从 ``skillevaluator similarity-check`` 生成的 JSON 报告中读取
``INTER_SKILL`` 类 finding，映射为 :class:`SimilarityMatch` 列表。
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import SimilarityMatch


def parse_similarity_report(report_path: Path | str) -> list[SimilarityMatch]:
    """解析 similarity 报告 JSON，返回 INTER_SKILL 命中列表。

    读取失败或结构不符时返回空列表（判定层会据此输出「无冗余」或
    「报告缺失」），不抛异常。
    """
    report_path = Path(report_path)
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []

    matches: list[SimilarityMatch] = []
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []

    for result in results:
        if not isinstance(result, dict):
            continue
        findings = result.get("findings")
        if not isinstance(findings, list):
            continue
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            metadata = finding.get("metadata") if isinstance(finding.get("metadata"), dict) else {}
            category = finding.get("category")
            if category == "SIMILARITY":
                # similarity-check 真实输出：entry_a 为目标 skill，entry_b 为 catalog 命中项。
                candidate = metadata.get("entry_a")
                catalog = metadata.get("entry_b")
                catalog_path = metadata.get("path_b")
            elif category == "INTER_SKILL":
                # plugin dedup 输出（bundled_skill 为相对路径，catalog_skill 为名字）。
                candidate = metadata.get("bundled_skill") or finding.get("file_path")
                catalog = metadata.get("catalog_skill")
                catalog_path = metadata.get("catalog_path")
            else:
                continue
            candidate = candidate or ""
            catalog = catalog or ""
            similarity = metadata.get("score")
            classification = metadata.get("classification") or finding.get("check_name") or ""
            if not candidate or not catalog:
                continue
            matches.append(
                SimilarityMatch(
                    candidate_skill=str(candidate),
                    catalog_skill=str(catalog),
                    similarity=float(similarity) if isinstance(similarity, (int, float)) else 0.0,
                    classification=str(classification),
                    catalog_path=str(catalog_path) or "",
                )
            )
    return matches


def matches_above_threshold(matches: list[SimilarityMatch], threshold: float) -> list[SimilarityMatch]:
    """返回相似度 >= threshold 的命中，按相似度降序。"""
    return sorted(
        (m for m in matches if m.similarity >= threshold),
        key=lambda m: m.similarity,
        reverse=True,
    )
