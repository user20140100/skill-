"""任务 B：自动化流水线包装（批处理扫描）。

把 SkillSpector / SkillEvaluator 的三层评估封装为「一键批量扫描 → 过滤高危 →
输出 Markdown/HTML 综合审计报告」。

纯编排 + 纯解析：本模块只负责命令生成与产物解析，不直接调用 skillevaluator，
复用 :mod:`skill_recommend.pipeline`（命令生成器）、:mod:`skill_recommend.security`
（Tier1 安全评级）、:mod:`skill_recommend.judge`（run 目录定位）。
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import PASS_AT_K_LIFT_JSON, RESULT_JSON
from .judge import find_latest_run
from .models import SecurityEvidence
from .pipeline import build_skillspector_scan_command, build_tier1_scan_command
from .security import load_security_from_report


def _load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


@dataclass
class SandboxComparison:
    """单个 skill 的 Tier3 A/B 对照数据（with_skill vs without_skill 双臂）。"""

    with_overall: float | None = None
    without_overall: float | None = None
    with_goal_accuracy: float | None = None
    without_goal_accuracy: float | None = None
    lift_goal_accuracy: float | None = None
    with_pass_at_k: float | None = None
    without_pass_at_k: float | None = None
    skill_activated: bool | None = None
    run_id: str = ""
    agent: str = ""
    model: str = ""
    execution_status: str = ""


@dataclass
class SkillScanRow:
    """单个 skill 的批量扫描结果行。"""

    skill_rel: str
    skill_name: str
    category: str
    security: SecurityEvidence | None = None
    sandbox: SandboxComparison | None = None


@dataclass
class BatchAuditReport:
    """批量扫描的综合审计报告（可序列化为 Markdown/HTML）。"""

    directory: str
    generated_at: str
    rows: list[SkillScanRow] = field(default_factory=list)

    @property
    def high_risk_rows(self) -> list[SkillScanRow]:
        """高危风险项：security.verdict == "unsafe" 的 skill。"""
        return [r for r in self.rows if r.security and r.security.verdict == "unsafe"]

    @property
    def summary(self) -> dict:
        total = len(self.rows)
        safe = sum(1 for r in self.rows if r.security and r.security.verdict == "safe")
        unsafe = sum(1 for r in self.rows if r.security and r.security.verdict == "unsafe")
        missing = total - safe - unsafe
        with_sandbox = sum(1 for r in self.rows if r.sandbox is not None)
        return {
            "total": total,
            "safe": safe,
            "unsafe": unsafe,
            "missing": missing,
            "with_sandbox": with_sandbox,
            "high_risk": len(self.high_risk_rows),
        }


def discover_skills(directory: Path, base: Path | None = None) -> list[str]:
    """返回 ``directory`` 下每个含 ``SKILL.md`` 的子目录相对 ``base`` 的路径。

    ``base`` 缺省为 ``directory``。跳过隐藏目录（``.`` / ``_`` 前缀）。
    """
    base = base or directory
    out: list[str] = []
    for skmd in directory.rglob("SKILL.md"):
        skill_dir = skmd.parent
        rel = skill_dir.relative_to(base)
        if any(p.startswith(".") or p.startswith("_") for p in rel.parts):
            continue
        out.append(rel.as_posix())
    return sorted(set(out))


def load_category(manifest_path: Path | str | None, skill_name: str) -> str:
    """从 manifest.json 读取 skill 的分类标签，缺失返回 ``unknown``。"""
    if not manifest_path:
        return "unknown"
    data = _load_json(Path(manifest_path))
    if not data:
        return "unknown"
    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    for s in skills:
        if isinstance(s, dict) and s.get("name") == skill_name:
            return str(s.get("category") or "unknown")
    return "unknown"


def build_batch_scan_commands(skills: list[str], use_llm: bool = False) -> list[list[str]]:
    """对每个 skill 依次生成 SkillSpector + Tier1 扫描命令。

    ``use_llm=False``（默认）为静态扫描（``--no-llm``）；``use_llm=True`` 启用 LLM 语义分析。
    """
    commands: list[list[str]] = []
    for skill in skills:
        commands.append(build_skillspector_scan_command(skill, use_llm=use_llm))
        commands.append(build_tier1_scan_command(skill, use_llm=use_llm))
    return commands


def _pick_agent(agents: dict, agent: str | None) -> str | None:
    if agent and agent in agents:
        return agent
    if agents:
        return next(iter(agents))
    return None


def _num(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def load_sandbox_comparison(
    skill_name: str,
    results_dir: Path | str | None,
    agent: str | None = None,
) -> SandboxComparison | None:
    """从 Tier3 run 目录提取 A/B 双臂对照数据，缺失时返回 ``None``（不抛异常）。"""
    if not results_dir:
        return None
    run_dir = find_latest_run(results_dir, skill_name)
    if run_dir is None:
        return None
    result = _load_json(run_dir / RESULT_JSON)
    if result is None:
        return None

    agents = result.get("agents") or {}
    if not isinstance(agents, dict) or not agents:
        return None
    agent_name = _pick_agent(agents, agent)
    if agent_name is None:
        return None
    ad = agents.get(agent_name) or {}

    with_pk = without_pk = None
    pkl = _load_json(run_dir / agent_name / PASS_AT_K_LIFT_JSON)
    if pkl is not None:
        with_pk = _num(pkl.get("with_skill"))
        without_pk = _num(pkl.get("without_skill"))
    else:
        pk = ad.get("pass_at_k") or {}
        with_pk = _num((pk.get("with_skill") or {}).get("rate"))
        without_pk = _num((pk.get("without_skill") or {}).get("rate"))

    lift = ad.get("lift") or {}
    goal = lift.get("goal_accuracy") or {}

    act = ad.get("skill_activation") or {}
    status = act.get("status")
    activated = None
    if status == "activated":
        activated = True
    elif status in ("inactive", "not_activated", "unknown"):
        activated = False

    return SandboxComparison(
        with_overall=_num(ad.get("overall_with_skill")),
        without_overall=_num(ad.get("overall_without_skill")),
        with_goal_accuracy=_num(goal.get("with_skill")),
        without_goal_accuracy=_num(goal.get("without_skill")),
        lift_goal_accuracy=_num(goal.get("delta")),
        with_pass_at_k=with_pk,
        without_pass_at_k=without_pk,
        skill_activated=activated,
        run_id=str(result.get("run_id") or ""),
        agent=agent_name,
        model=str(ad.get("model") or ""),
        execution_status=str(result.get("execution_status") or ""),
    )


def build_batch_report(
    skills: list[str],
    security_dir: Path | str | None,
    results_dir: Path | str | None,
    agent: str | None = None,
    manifest_path: Path | str | None = None,
    directory: str = "",
) -> BatchAuditReport:
    """对一批 skill 构建综合审计报告（安全评级 + 沙盒对照 + 高危过滤）。"""
    rows: list[SkillScanRow] = []
    for skill_rel in skills:
        skill_name = skill_rel.split("/")[-1]
        category = load_category(manifest_path, skill_name) if manifest_path else "unknown"
        security = load_security_from_report(skill_name, security_dir) if security_dir else None
        sandbox = load_sandbox_comparison(skill_name, results_dir, agent) if results_dir else None
        rows.append(SkillScanRow(
            skill_rel=skill_rel,
            skill_name=skill_name,
            category=category,
            security=security,
            sandbox=sandbox,
        ))
    return BatchAuditReport(
        directory=directory,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rows=rows,
    )


# --- 渲染辅助 ---

def _fmt(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def _esc(value: Any) -> str:
    """HTML 转义动态内容，避免扫描器输出（可能含代码片段）破坏报告或注入 HTML。"""
    return html.escape(str(value), quote=True)


def _verdict_label(security: SecurityEvidence | None) -> str:
    if not security:
        return "未评估"
    return {"safe": "安全", "unsafe": "高危", "missing": "未评估"}.get(
        security.verdict, security.verdict
    )


def _risk_score(security: SecurityEvidence | None) -> str:
    if not security or not security.skillspector:
        return "-"
    score = security.skillspector.get("risk_score")
    return "-" if score is None else str(score)


def _finding_count(security: SecurityEvidence | None) -> int:
    if not security:
        return 0
    return len(security.high_severity_findings)


def _category_label(category: str) -> str:
    return {"positive": "正向", "redundant": "冗余", "security": "安全"}.get(category, category)


def render_markdown(report: BatchAuditReport) -> str:
    s = report.summary
    lines: list[str] = []
    lines.append("# Agent Skill 批量安全审计报告")
    lines.append("")
    lines.append(f"> 扫描目录：`{report.directory or 'N/A'}`　生成时间：{report.generated_at}")
    lines.append("")

    lines.append("## 1. 总览")
    lines.append("")
    lines.append(
        f"- 扫描 Skill 数：**{s['total']}**；安全通过：**{s['safe']}**；"
        f"存在高危：**{s['unsafe']}**；未评估：{s['missing']}；含沙盒对照：{s['with_sandbox']}"
    )
    lines.append("")
    lines.append("| Skill | 分类 | 安全评级 | 风险分 | 高危 finding | 沙盒对照 |")
    lines.append("|---|---|---|---|---|---|")
    for r in report.rows:
        lines.append(
            f"| `{r.skill_name}` | {_category_label(r.category)} | {_verdict_label(r.security)} "
            f"| {_risk_score(r.security)} | {_finding_count(r.security)} "
            f"| {'有' if r.sandbox else '无'} |"
        )
    lines.append("")

    lines.append("## 2. 高危风险项（过滤）")
    lines.append("")
    if report.high_risk_rows:
        for r in report.high_risk_rows:
            findings = r.security.high_severity_findings if r.security else []
            lines.append(f"### `{r.skill_name}`")
            lines.append("")
            if findings:
                for f in findings:
                    lines.append(
                        f"- [{f.get('source', '?')}:{str(f.get('severity', '?')).upper()}] "
                        f"{f.get('message', '')}"
                    )
            else:
                lines.append("- 存在 critical/high 级 finding（详情见安全报告 JSON）。")
            lines.append("")
    else:
        lines.append("未发现高危风险项。")
        lines.append("")

    lines.append("## 3. 沙盒对比（Tier3 A/B）")
    lines.append("")
    with_sandbox = [r for r in report.rows if r.sandbox is not None]
    if with_sandbox:
        lines.append("| Skill | overall (with/without) | goal_acc (with/without) | lift(goal) | pass@k (with/without) | 状态 |")
        lines.append("|---|---|---|---|---|---|")
        for r in with_sandbox:
            sb = r.sandbox
            lines.append(
                f"| `{r.skill_name}` | {_fmt(sb.with_overall)} / {_fmt(sb.without_overall)} "
                f"| {_fmt(sb.with_goal_accuracy)} / {_fmt(sb.without_goal_accuracy)} "
                f"| {_fmt(sb.lift_goal_accuracy)} "
                f"| {_fmt(sb.with_pass_at_k)} / {_fmt(sb.without_pass_at_k)} "
                f"| {sb.execution_status or 'N/A'} |"
            )
        lines.append("")
    else:
        lines.append("无沙盒对照数据（未跑 Tier3 或结果缺失）。")
        lines.append("")

    lines.append("## 4. 明细")
    lines.append("")
    for r in report.rows:
        sec = r.security
        t1 = sec.tier1 if sec else {}
        counts = t1.get("severity_counts") or {}
        lines.append(
            f"- **{r.skill_name}**（{r.skill_rel}）：评级 {_verdict_label(sec)}，"
            f"风险分 {_risk_score(sec)}，"
            f"C/H/M/L = {counts.get('critical', 0)}/{counts.get('high', 0)}/"
            f"{counts.get('medium', 0)}/{counts.get('low', 0)}"
        )
    lines.append("")

    return "\n".join(lines)


def render_html(report: BatchAuditReport) -> str:
    s = report.summary
    parts: list[str] = []
    parts.append("<!DOCTYPE html><html lang=\"zh\"><head><meta charset=\"utf-8\">")
    parts.append("<title>Agent Skill 批量安全审计报告</title>")
    parts.append(
        "<style>body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
        "margin:2rem auto;max-width:960px;padding:0 1rem;color:#1a1a1a;line-height:1.6}"
        "h1{border-bottom:2px solid #333;padding-bottom:.4rem}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}"
        "th,td{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.9rem}"
        "th{background:#f5f5f5}.unsafe{color:#b00020;font-weight:600}.safe{color:#1e7e34}"
        ".card{border:1px solid #ddd;border-radius:6px;padding:.8rem 1rem;margin:.8rem 0;background:#fafafa}"
        "</style></head><body>"
    )
    parts.append("<h1>Agent Skill 批量安全审计报告</h1>")
    parts.append(
        f"<p>扫描目录：<code>{_esc(report.directory or 'N/A')}</code>　生成时间：{_esc(report.generated_at)}</p>"
    )

    parts.append("<h2>1. 总览</h2>")
    parts.append(
        f"<div class=\"card\">扫描 Skill 数 <b>{s['total']}</b>；安全通过 <b class=\"safe\">{s['safe']}</b>；"
        f"存在高危 <b class=\"unsafe\">{s['unsafe']}</b>；未评估 {s['missing']}；"
        f"含沙盒对照 {s['with_sandbox']}</div>"
    )
    parts.append("<table><tr><th>Skill</th><th>分类</th><th>安全评级</th><th>风险分</th><th>高危 finding</th><th>沙盒对照</th></tr>")
    for r in report.rows:
        cls = "unsafe" if (r.security and r.security.verdict == "unsafe") else (
            "safe" if (r.security and r.security.verdict == "safe") else ""
        )
        parts.append(
            f"<tr><td><code>{_esc(r.skill_name)}</code></td><td>{_esc(_category_label(r.category))}</td>"
            f"<td class=\"{cls}\">{_esc(_verdict_label(r.security))}</td>"
            f"<td>{_esc(_risk_score(r.security))}</td><td>{_finding_count(r.security)}</td>"
            f"<td>{'有' if r.sandbox else '无'}</td></tr>"
        )
    parts.append("</table>")

    parts.append("<h2>2. 高危风险项（过滤）</h2>")
    if report.high_risk_rows:
        for r in report.high_risk_rows:
            parts.append(f"<h3><code>{_esc(r.skill_name)}</code></h3><ul>")
            findings = r.security.high_severity_findings if r.security else []
            if findings:
                for f in findings:
                    parts.append(
                        f"<li class=\"unsafe\">[{_esc(f.get('source', '?'))}:"
                        f"{_esc(str(f.get('severity', '?')).upper())}] {_esc(f.get('message', ''))}</li>"
                    )
            else:
                parts.append("<li>存在 critical/high 级 finding（详情见安全报告 JSON）。</li>")
            parts.append("</ul>")
    else:
        parts.append("<p>未发现高危风险项。</p>")

    parts.append("<h2>3. 沙盒对比（Tier3 A/B）</h2>")
    with_sandbox = [r for r in report.rows if r.sandbox is not None]
    if with_sandbox:
        parts.append("<table><tr><th>Skill</th><th>overall (with/without)</th><th>goal_acc (with/without)</th>"
                     "<th>lift(goal)</th><th>pass@k (with/without)</th><th>状态</th></tr>")
        for r in with_sandbox:
            sb = r.sandbox
            parts.append(
                f"<tr><td><code>{_esc(r.skill_name)}</code></td>"
                f"<td>{_fmt(sb.with_overall)} / {_fmt(sb.without_overall)}</td>"
                f"<td>{_fmt(sb.with_goal_accuracy)} / {_fmt(sb.without_goal_accuracy)}</td>"
                f"<td>{_fmt(sb.lift_goal_accuracy)}</td>"
                f"<td>{_fmt(sb.with_pass_at_k)} / {_fmt(sb.without_pass_at_k)}</td>"
                f"<td>{_esc(sb.execution_status or 'N/A')}</td></tr>"
            )
        parts.append("</table>")
    else:
        parts.append("<p>无沙盒对照数据（未跑 Tier3 或结果缺失）。</p>")

    parts.append("</body></html>")
    return "\n".join(parts)
