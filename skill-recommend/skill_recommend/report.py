"""推荐报告生成：模板 Markdown + 中文双结论叙述。

规则结论由 :mod:`skill_recommend.rules` 产生；本模块只负责把它们渲染为可读文本，
输出 ``security_recommendation`` 与 ``gain_recommendation`` 两个独立结论（P7）。
LLM 增强（可选）由 :mod:`skill_recommend.llm` 提供，失败时回退到这里的模板叙述。
"""

from __future__ import annotations

from datetime import datetime

from .models import Evidence, GainRecommendation, RecommendationReport, SecurityRecommendation


def _find_evidence(report: RecommendationReport, name: str | None) -> Evidence | None:
    if not name:
        return None
    for ev in report.evidence:
        if ev.skill_name == name:
            return ev
    return None


def _pair_names(report: RecommendationReport) -> str:
    names = [e.skill_name for e in report.evidence]
    return " 与 ".join(names) if names else "这两个 skill"


def _fmt(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.3f}"


def _other_name(report: RecommendationReport, name: str) -> str:
    for ev in report.evidence:
        if ev.skill_name != name:
            return ev.skill_name
    return "另一个 skill"


def security_narrative(report: RecommendationReport) -> str:
    """生成安全轨中文叙述（模板版，可被 LLM 覆盖）。"""
    sec = report.security_recommendation

    if sec.verdict == "both_safe":
        return (
            "两者均通过完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1），"
            "安全维度无差异，无需从安全角度二选一。"
        )

    if sec.verdict in ("recommend_a", "recommend_b"):
        winner = sec.winner
        loser = _other_name(report, winner) if winner else None
        winner_ev = _find_evidence(report, winner)
        loser_ev = _find_evidence(report, loser)
        if winner is None or loser is None or winner_ev is None or loser_ev is None:
            return "安全结论：一方更安全（但缺少明确的双方信息，请检查证据）。"

        loser_verdict = loser_ev.security.verdict if loser_ev.security else "missing"
        if loser_verdict == "unsafe":
            summary = _finding_summary(loser_ev)
            return (
                f"安全角度更推荐「{winner}」；「{loser}」存在高危安全 finding"
                f"{summary}，不建议采用。"
            )

        # 双方 unsafe → 推荐风险更低方
        w_summary = _finding_summary(winner_ev)
        l_summary = _finding_summary(loser_ev)
        return (
            f"双方均存在安全问题；相较而言安全角度更推荐「{winner}」。"
            f"「{winner}」{w_summary}；「{loser}」{l_summary}。"
        )

    # missing
    reasons = "；".join(sec.reasons) if sec.reasons else "无具体原因"
    return f"安全审查缺失，无法给出安全结论。原因：{reasons}"


def _finding_summary(ev: Evidence) -> str:
    if not ev.security or not ev.security.high_severity_findings:
        return ""
    parts = [
        f"[{f.get('source')}:{str(f.get('severity')).upper()}] {f.get('message', '')}"
        for f in ev.security.high_severity_findings[:3]
    ]
    return "（" + "；".join(parts) + "）"


def gain_narrative(report: RecommendationReport) -> str:
    """生成增益轨中文叙述（模板版，可被 LLM 覆盖）。"""
    gain = report.gain_recommendation
    winner = gain.winner

    if gain.verdict in ("clear_better", "conditional"):
        winner_ev = _find_evidence(report, winner)
        loser = _other_name(report, winner) if winner else None
        loser_ev = _find_evidence(report, loser)
        if winner is None or winner_ev is None or loser_ev is None:
            return "增益结论：一方更优（但缺少明确的双方信息，请检查证据）。"
        base = (
            f"推荐使用「{winner}」替代「{loser}」：在同一组用例上，"
            f"前者 goal_accuracy 为 {_fmt(winner_ev.goal_accuracy)}，"
            f"后者为 {_fmt(loser_ev.goal_accuracy)}"
            f"（差 {_fmt(gain.delta_goal_accuracy)}）。"
        )
        return base

    if gain.verdict == "efficiency_better":
        return (
            f"两者结果相当，但「{winner}」在效率维度综合领先"
            f"（token 输入 / token 输出 / 执行时间 / 执行轮数），综合增益更优。"
        )

    if gain.verdict == "both_acceptable":
        diff = _dimension_diff_lines(report)
        return (
            f"两者增益相当、均可。具体差异如下（不足以支撑明确的增益优劣，仅供参考，"
            f"最终由用户决定）：{diff}"
        )

    # insufficient
    reasons = "；".join(gain.reasons) if gain.reasons else "无具体原因"
    return f"证据不足，无法给出定量增益结论。原因：{reasons}"


def _dimension_diff_lines(report: RecommendationReport) -> str:
    dims = report.gain_recommendation.dimension_comparison
    if not dims:
        return ""
    names = [e.skill_name for e in report.evidence]
    lines = []
    for key, entry in dims.items():
        a = entry.get(names[0]) if len(names) > 0 else None
        b = entry.get(names[1]) if len(names) > 1 else None
        winner = entry.get("winner")
        if winner is None:
            lines.append(f"{key}: 相当")
        else:
            lines.append(f"{key}: {names[0]}={a} vs {names[1]}={b} → 更优 {winner}")
    return "；".join(lines)


def build_recommendation_text(report: RecommendationReport) -> str:
    """生成综合叙述（安全 + 增益两段，不合成单一结论）。"""
    return security_narrative(report) + "\n\n" + gain_narrative(report)


def _populate_narratives(report: RecommendationReport) -> None:
    if not report.security_recommendation.narrative:
        report.security_recommendation.narrative = security_narrative(report)
    if not report.gain_recommendation.narrative:
        report.gain_recommendation.narrative = gain_narrative(report)


def render_markdown(report: RecommendationReport) -> str:
    """渲染完整 Markdown 报告（双结论）。"""
    _populate_narratives(report)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = []
    lines.append("# 冗余 Skill 推荐报告")
    lines.append("")
    lines.append(f"> 生成时间：{now}")
    lines.append("")

    # 冗余对
    lines.append("## 1. 冗余检测")
    lines.append("")
    if report.redundant_pair:
        lines.append("| 候选 skill | 命中 catalog skill | 相似度 | 分类 |")
        lines.append("|---|---|---|---|")
        for m in report.redundant_pair:
            lines.append(f"| {m.candidate_skill} | {m.catalog_skill} | {m.similarity:.3f} | {m.classification} |")
    else:
        lines.append("未提供冗余对信息。")
    lines.append("")

    # 证据
    lines.append("## 2. 评估证据")
    lines.append("")
    lines.append("| Skill | goal_acc | overall | pass@k | lift(goal) | prompt_tok | completion_tok | 时间(s) | 轮数 | 安全 | 状态 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for ev in report.evidence:
        sec = ev.security.verdict if ev.security else "N/A"
        lines.append(
            f"| {ev.skill_name} | {_fmt(ev.goal_accuracy)} | {_fmt(ev.overall)} | {_fmt(ev.pass_at_k)} "
            f"| {_fmt(ev.lift_goal_accuracy)} | {_int(ev.prompt_tokens)} | {_int(ev.completion_tokens)} "
            f"| {_num(ev.duration_seconds)} | {_int(ev.rounds)} | {sec} | {ev.execution_status or 'N/A'} |"
        )
    lines.append("")

    # 安全结论
    lines.append("## 3. 安全结论（完整 Tier1）")
    lines.append("")
    lines.append(f"- **结论**：{_SEC_VERDICT_LABEL.get(report.security_recommendation.verdict, report.security_recommendation.verdict)}")
    if report.security_recommendation.winner:
        lines.append(f"- **安全角度更推荐**：{report.security_recommendation.winner}")
    lines.append("")
    lines.append(report.security_recommendation.narrative)
    lines.append("")

    # 增益结论
    lines.append("## 4. 增益结论（共享用例）")
    lines.append("")
    lines.append(f"- **结论**：{_GAIN_VERDICT_LABEL.get(report.gain_recommendation.verdict, report.gain_recommendation.verdict)}")
    if report.gain_recommendation.winner:
        lines.append(f"- **增益更优**：{report.gain_recommendation.winner}")
    lines.append(f"- **可比性**：{'满足' if report.gain_recommendation.comparable else '不满足（结论仅供参考）'}")
    lines.append("")
    lines.append(report.gain_recommendation.narrative)
    lines.append("")

    dims = report.gain_recommendation.dimension_comparison
    if dims:
        names = [e.skill_name for e in report.evidence]
        lines.append("### 多维增益对比")
        lines.append("")
        lines.append("| 维度 | " + " | ".join(names) + " | 更优 |")
        lines.append("|---|" + "---|" * len(names) + "---|")
        for key, entry in dims.items():
            cols = [str(entry.get(n) if entry.get(n) is not None else "N/A") for n in names]
            lines.append(f"| {key} | " + " | ".join(cols) + f" | {entry.get('winner') or '—'} |")
        lines.append("")

    # 决策说明
    lines.append("## 5. 决策说明")
    lines.append("")
    lines.append("> 以上安全结论与增益结论彼此独立，系统**不合成单一最终推荐**。")
    lines.append("> 请结合自身使用场景，在两个维度间自行权衡选择（P7）。")
    lines.append("")

    # LLM 润色（可选）
    if report.recommendation:
        lines.append("## 6. 综合叙述（LLM 润色）")
        lines.append("")
        lines.append(report.recommendation)
        lines.append("")

    # 外部候选
    if report.external_candidates:
        lines.append("## 7. 联网搜索候选")
        lines.append("")
        lines.append("| Skill | 来源 | 相似度 | 描述 |")
        lines.append("|---|---|---|---|")
        for c in report.external_candidates:
            desc = (c.description or "").replace("|", "\\|")[:120]
            sim = f"{c.similarity:.3f}" if c.similarity is not None else "-"
            lines.append(f"| {c.name} | {c.source} | {sim} | {desc} |")
        lines.append("")

    # 复现信息
    lines.append("## 8. 复现信息")
    lines.append("")
    for ev in report.evidence:
        lines.append(
            f"- **{ev.skill_name}**：run_id={ev.run_id or 'N/A'}，agent={ev.agent or 'N/A'}，"
            f"model={ev.model or 'N/A'}，attempts={ev.n_attempts if ev.n_attempts is not None else 'N/A'}，"
            f"dataset_digest={ev.dataset_digest or 'N/A'}"
        )
    lines.append("")

    return "\n".join(lines)


def _int(value: int | None) -> str:
    return str(value) if value is not None else "N/A"


def _num(value: float | None) -> str:
    return f"{value:.1f}" if value is not None else "N/A"


_SEC_VERDICT_LABEL = {
    "both_safe": "两者均安全",
    "recommend_a": "安全角度推荐一方",
    "recommend_b": "安全角度推荐一方",
    "missing": "安全审查缺失",
}

_GAIN_VERDICT_LABEL = {
    "clear_better": "明确更优",
    "conditional": "有条件更优",
    "efficiency_better": "结果相当、效率更优",
    "both_acceptable": "两者增益相当、均可",
    "insufficient": "证据不足",
}
