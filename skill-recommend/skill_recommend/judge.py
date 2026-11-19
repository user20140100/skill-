"""判定模式：输入已有 Tier2 报告 + Tier3 结果目录，产出推荐报告。

纯编排逻辑，不直接调用 skillevaluator，便于复用已跑好的产物（答辩场景）。
"""

from __future__ import annotations

from pathlib import Path

from .config import RESULT_JSON
from .models import RecommendationReport, SimilarityMatch
from .report import build_recommendation_text, render_markdown
from .rules import evaluate_pair
from .security import load_security_from_report
from .tier2 import parse_similarity_report
from .tier3 import load_evidence_from_run_dir


def find_latest_run(root: Path | str, skill_name: str) -> Path | None:
    """在 ``<root>/<skill_name>/`` 下定位最新的完整 run 目录。

    优先 ``latest`` 目录/软链，否则按目录名（时间戳）倒序取第一个含
    ``result.json`` 的目录，跳过 ``_`` 开头的目录（如 ``_failed-runs``）。
    """
    skill_dir = Path(root) / skill_name
    if not skill_dir.is_dir():
        return None

    latest = skill_dir / "latest"
    if (latest / RESULT_JSON).exists():
        return latest

    runs = [
        p for p in skill_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_") and (p / RESULT_JSON).exists()
    ]
    if not runs:
        return None
    return sorted(runs, key=lambda p: p.name, reverse=True)[0]


def _pair_matches(m: SimilarityMatch, a: str, b: str) -> bool:
    return {m.candidate_skill, m.catalog_skill} == {a, b}


def judge_from_inputs(
    similarity_report: Path | str,
    results_dir: Path | str,
    skill_a: str,
    skill_b: str,
    agent: str | None = None,
    security_dir: Path | str | None = None,
) -> RecommendationReport:
    """编排判定流程并返回报告（双结论：安全 + 增益）。"""
    matches = parse_similarity_report(similarity_report)
    pair_matches = [m for m in matches if _pair_matches(m, skill_a, skill_b)]

    if pair_matches:
        best = max(pair_matches, key=lambda m: m.similarity)
        pair = [best]
    else:
        pair = [
            SimilarityMatch(
                candidate_skill=skill_a,
                catalog_skill=skill_b,
                similarity=0.0,
                classification="NONE",
            )
        ]

    ev_a = load_evidence_from_run_dir(skill_a, find_latest_run(results_dir, skill_a), agent=agent)
    ev_b = load_evidence_from_run_dir(skill_b, find_latest_run(results_dir, skill_b), agent=agent)

    # 完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1），缺失时 security 为 None。
    ev_a.security = load_security_from_report(skill_a, security_dir)
    ev_b.security = load_security_from_report(skill_b, security_dir)

    security_rec, gain_rec = evaluate_pair(ev_a, ev_b)

    report = RecommendationReport(
        redundant_pair=pair,
        evidence=[ev_a, ev_b],
        security_recommendation=security_rec,
        gain_recommendation=gain_rec,
        comparable=gain_rec.comparable,
    )
    report.recommendation = build_recommendation_text(report)
    report.report_markdown = render_markdown(report)
    return report
