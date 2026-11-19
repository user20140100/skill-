"""完整 Tier1 安全审查解析：SkillSpector + SkillEvaluator Tier1。

从阶段零预扫描落盘的报告中读取结构化安全证据，并按 6.2 的确定性评级规则
计算 ``safe`` / ``unsafe`` / ``missing``。

报告目录约定（与 :func:`skill_recommend.pipeline._output_subdir` 一致）：
``<security_dir>/<skill相对路径（/ → _）>/skillspector.json`` 与 ``skillevaluator-tier1.json``。
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import SecurityEvidence

SPECTOR_JSON = "skillspector.json"
TIER1_JSON = "skillevaluator-tier1.json"

# 严重度等级排序（越低越安全）
_SEVERITY_ORDER = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def _load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _parse_skillspector(data: dict) -> dict:
    risk = data.get("risk_assessment") if isinstance(data.get("risk_assessment"), dict) else {}
    issues = data.get("issues") if isinstance(data.get("issues"), list) else []
    return {
        "risk_score": risk.get("score"),
        "severity": str(risk.get("severity") or "NONE").upper(),
        "recommendation": str(risk.get("recommendation") or "").upper(),
        "max_issue_severity": str(risk.get("max_issue_severity") or "NONE").upper(),
        "issue_count": len(issues),
    }


def _parse_tier1(data: dict) -> dict:
    counts = data.get("severity_counts") if isinstance(data.get("severity_counts"), dict) else {}
    return {
        "overall_status": str(data.get("overall_status") or ""),
        "severity_counts": {
            "critical": int(counts.get("critical") or 0),
            "high": int(counts.get("high") or 0),
            "medium": int(counts.get("medium") or 0),
            "low": int(counts.get("low") or 0),
        },
    }


def _collect_high_findings(skillspector: dict, tier1: dict) -> list[dict]:
    """汇总 critical/high 级 finding 摘要（供 unsafe 话术引用）。"""
    findings: list[dict] = []
    sp = skillspector.get("issues") if isinstance(skillspector.get("issues"), list) else []
    for issue in sp:
        if not isinstance(issue, dict):
            continue
        sev = str(issue.get("severity") or "").upper()
        if sev in ("HIGH", "CRITICAL"):
            findings.append({"source": "skillspector", "severity": sev,
                             "message": str(
                                 issue.get("message") or issue.get("title")
                                 or issue.get("finding") or issue.get("explanation") or ""
                             ).strip()})
    t1_groups = tier1.get("finding_groups") if isinstance(tier1.get("finding_groups"), list) else []
    for group in t1_groups:
        if not isinstance(group, dict):
            continue
        sev = str(group.get("severity") or "").lower()
        if sev in ("high", "critical"):
            findings.append({"source": "tier1", "severity": sev,
                             "message": str(group.get("message") or "")})
    return findings


def compute_security_verdict(skillspector: dict, tier1: dict) -> str:
    """按 6.2 评级规则计算 safe / unsafe / missing。

    ``safe`` 要求 SkillSpector 无 critical/high（``max_issue_severity`` 为 NONE/LOW/MEDIUM
    或 ``recommendation == SAFE``）且 Tier1 ``critical == 0 && high == 0``。
    """
    if not skillspector or not tier1:
        return "missing"

    sp_max = str(skillspector.get("max_issue_severity") or "NONE").upper()
    sp_rec = str(skillspector.get("recommendation") or "").upper()
    sp_clean = sp_max in ("NONE", "LOW", "MEDIUM") or sp_rec == "SAFE"

    counts = tier1.get("severity_counts") or {}
    t1_clean = int(counts.get("critical") or 0) == 0 and int(counts.get("high") or 0) == 0

    if sp_clean and t1_clean:
        return "safe"
    return "unsafe"


def parse_security_dir(skillspector_data: dict | None, tier1_data: dict | None) -> SecurityEvidence:
    """由两份已加载的报告 JSON 构造 SecurityEvidence 并计算 verdict。"""
    sp = _parse_skillspector(skillspector_data) if skillspector_data else {}
    t1 = _parse_tier1(tier1_data) if tier1_data else {}

    # 汇总 high severity findings 需要原始 JSON 数据（含 issues/finding_groups）
    findings = _collect_high_findings(
        skillspector_data or {}, tier1_data or {}
    ) if sp or t1 else []

    return SecurityEvidence(
        skillspector=sp,
        tier1=t1,
        verdict=compute_security_verdict(sp, t1),
        high_severity_findings=findings,
    )


def _find_security_subdir(security_dir: Path, skill_name: str) -> Path | None:
    """在 security_dir 下定位某 skill 的安全报告子目录。

    优先精确名 ``<skill_name>``，其次回退到任何以 ``_<skill_name>`` 结尾的子目录
    （对应 ``<组>_<skill>`` 的落盘方式），要求目录内含任一报告文件。
    """
    if not security_dir.is_dir():
        return None

    def has_report(d: Path) -> bool:
        return (d / SPECTOR_JSON).is_file() or (d / TIER1_JSON).is_file()

    direct = security_dir / skill_name
    if has_report(direct):
        return direct

    matches = []
    for d in security_dir.iterdir():
        if not d.is_dir():
            continue
        if d.name == skill_name or d.name.endswith("_" + skill_name):
            if has_report(d):
                matches.append(d)
    if matches:
        return sorted(matches, key=lambda p: p.name)[0]
    return None


def load_security_from_report(skill_name: str, security_dir: Path | str | None) -> SecurityEvidence | None:
    """从安全报告目录读取某 skill 的完整 Tier1 安全证据。

    找不到任何报告文件时返回 ``None``（调用方据此标注"安全审查缺失"）。
    """
    if not security_dir:
        return None
    subdir = _find_security_subdir(Path(security_dir), skill_name)
    if subdir is None:
        return None

    spector = _load_json(subdir / SPECTOR_JSON)
    tier1 = _load_json(subdir / TIER1_JSON)
    if spector is None and tier1 is None:
        return None
    return parse_security_dir(spector, tier1)
