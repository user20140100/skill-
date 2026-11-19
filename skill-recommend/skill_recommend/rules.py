"""确定性双轨推荐判定规则。

v1.2 起删除单一 ``RuleResult.verdict``，改为两条彼此独立的结论（P7）：

- **安全轨**（6.2）：完整 Tier1（SkillSpector + SkillEvaluator Tier1）评级 + 三情形；
- **增益轨**（6.3）：多维增益（结果优先，再综合 token 输入 / token 输出 / 时间 / 轮数）。

两条结论互不污染：安全结论与用例无关，增益结论与安全评级无关。
本模块不调用大模型，结果完全可复现。
"""

from __future__ import annotations

from .config import CLEAR_BETTER_DELTA, CONDITIONAL_DELTA
from .models import Evidence, GainRecommendation, SecurityRecommendation

# 安全严重度排序（越低越安全）
_SEVERITY_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


# ---------------------------------------------------------------------------
# 安全轨（6.2）
# ---------------------------------------------------------------------------

def _sp_rank(ev: Evidence) -> int:
    sev = (ev.security.skillspector.get("severity") or "NONE") if ev.security else "NONE"
    return _SEVERITY_RANK.get(str(sev).upper(), 0)


def _sp_high_issue_count(ev: Evidence) -> int:
    """SkillSpector critical/high issue 计数。"""
    if not ev.security:
        return 0
    return sum(
        1 for f in ev.security.high_severity_findings
        if f.get("source") == "skillspector"
    )


def _t1_high_count(ev: Evidence) -> int:
    """Tier1 critical/high 计数。"""
    if not ev.security:
        return 0
    counts = ev.security.tier1.get("severity_counts") or {}
    return int(counts.get("critical") or 0) + int(counts.get("high") or 0)


def _risk_key(ev: Evidence) -> tuple:
    """双方 unsafe 时的风险比较键（越小越安全），按 6.2 优先级：

    SkillSpector risk_score 低者 > severity 等级低者 >
    SkillSpector critical/high 计数少者 > Tier1 critical/high 计数少者。
    """
    score = ev.security.skillspector.get("risk_score") if ev.security else None
    score = score if isinstance(score, (int, float)) else float("inf")
    return (score, _sp_rank(ev), _sp_high_issue_count(ev), _t1_high_count(ev))


def security_recommendation(a: Evidence, b: Evidence) -> SecurityRecommendation:
    """安全轨结论（三情形，6.2）。"""
    reasons: list[str] = []

    va = a.security.verdict if a.security else "missing"
    vb = b.security.verdict if b.security else "missing"

    if va == "missing" or vb == "missing":
        missing = [e.skill_name for e, v in ((a, va), (b, vb)) if v == "missing"]
        reasons.append(f"安全审查缺失：{', '.join(missing)}（需先补完整 Tier1 扫描）")
        return SecurityRecommendation(verdict="missing", winner=None, reasons=reasons)

    if va == "safe" and vb == "safe":
        reasons.append("双方均通过完整 Tier1 安全审查（SkillSpector + SkillEvaluator Tier1）")
        return SecurityRecommendation(verdict="both_safe", winner=None, reasons=reasons)

    if va == "safe" and vb == "unsafe":
        reasons.append(f"{b.skill_name} 存在高危安全 finding，不建议采用")
        return SecurityRecommendation(verdict="recommend_a", winner=a.skill_name, reasons=reasons)

    if va == "unsafe" and vb == "safe":
        reasons.append(f"{a.skill_name} 存在高危安全 finding，不建议采用")
        return SecurityRecommendation(verdict="recommend_b", winner=b.skill_name, reasons=reasons)

    # 双方 unsafe → 推荐风险更低方
    winner = a if _risk_key(a) <= _risk_key(b) else b
    reasons.append("双方均存在安全问题，按风险比较优先级推荐风险更低方")
    return SecurityRecommendation(verdict="recommend_a" if winner is a else "recommend_b",
                                 winner=winner.skill_name, reasons=reasons)


# ---------------------------------------------------------------------------
# 增益轨（6.3，多维）
# ---------------------------------------------------------------------------

def _dim_entry(a_name: str, b_name: str, a_val, b_val, winner: str | None) -> dict:
    return {a_name: a_val, b_name: b_val, "winner": winner}


def _compare(a_val, b_val, higher_better: bool) -> str | None:
    """返回更优方（a_name 或 b_name），无法比较或相等返回 None。"""
    if a_val is None or b_val is None:
        return None
    if a_val == b_val:
        return None
    a_better = a_val > b_val if higher_better else a_val < b_val
    return "a" if a_better else "b"


def _multi_dimension_comparison(a: Evidence, b: Evidence) -> tuple[dict, dict]:
    """对 4 个效率维度逐项比较，返回 (dimension_comparison, efficiency_wins)。

    结果维度（goal_accuracy）单独参与结果优先判定，不计入 efficiency_wins。
    efficiency_wins 统计 4 个效率维度：token 输入 / token 输出 / 时间 / 轮数。
    不再评估流程准确性（skill_execution/skill_efficiency）与工具调用准确性。
    """
    a_name, b_name = a.skill_name, b.skill_name

    result_winner = _compare(a.goal_accuracy, b.goal_accuracy, higher_better=True)
    prompt_winner = _compare(a.prompt_tokens, b.prompt_tokens, higher_better=False)
    completion_winner = _compare(a.completion_tokens, b.completion_tokens, higher_better=False)
    duration_winner = _compare(a.duration_seconds, b.duration_seconds, higher_better=False)
    rounds_winner = _compare(a.rounds, b.rounds, higher_better=False)

    dimension_comparison = {
        "result": _dim_entry(a_name, b_name, a.goal_accuracy, b.goal_accuracy, result_winner),
        "prompt_tokens": _dim_entry(a_name, b_name, a.prompt_tokens, b.prompt_tokens, prompt_winner),
        "completion_tokens": _dim_entry(a_name, b_name, a.completion_tokens, b.completion_tokens, completion_winner),
        "duration_seconds": _dim_entry(a_name, b_name, a.duration_seconds, b.duration_seconds, duration_winner),
        "rounds": _dim_entry(a_name, b_name, a.rounds, b.rounds, rounds_winner),
    }

    wins = {a_name: 0, b_name: 0}
    for w in (prompt_winner, completion_winner, duration_winner, rounds_winner):
        if w == "a":
            wins[a_name] += 1
        elif w == "b":
            wins[b_name] += 1
    return dimension_comparison, wins


def gain_recommendation(a: Evidence, b: Evidence) -> GainRecommendation:
    """增益轨结论（结果优先，多维综合，6.3）。"""
    reasons: list[str] = []
    comparable = a.build_comparable_key() == b.build_comparable_key()

    # 1. 证据完整性
    if not a.is_complete or not b.is_complete:
        missing = [e.skill_name for e in (a, b) if not e.is_complete]
        reasons.append(f"证据不足：{', '.join(missing)} 的 Tier3 结果不完整")
        return GainRecommendation(verdict="insufficient", comparable=comparable, reasons=reasons)

    # 2. skill 激活
    for ev in (a, b):
        if ev.skill_activated is False:
            reasons.append(f"{ev.skill_name} 在 with-skill 试验中未被激活（INCONCLUSIVE），无法参与增益比较")
            return GainRecommendation(verdict="insufficient", comparable=comparable, reasons=reasons)

    if not comparable:
        reasons.append("两 skill 的 Tier3 结果不在同一条实验条件下（dataset/agent/model/attempts 不一致），结论仅供参考")

    ga_a, ga_b = a.goal_accuracy, b.goal_accuracy
    if ga_a is None or ga_b is None:
        reasons.append("缺少 goal_accuracy 证据，无法定量比较")
        return GainRecommendation(verdict="insufficient", comparable=comparable, reasons=reasons)

    delta = ga_a - ga_b
    adelta = abs(delta)
    winner = a.skill_name if delta > 0 else b.skill_name if delta < 0 else None

    # 3. 结果优先
    if adelta >= CLEAR_BETTER_DELTA:
        reasons.append(f"goal_accuracy 差 {adelta:.3f} ≥ {CLEAR_BETTER_DELTA}，明确更优")
        return GainRecommendation(verdict="clear_better", winner=winner,
                                  delta_goal_accuracy=round(delta, 4),
                                  comparable=comparable, reasons=reasons)

    if adelta >= CONDITIONAL_DELTA:
        reasons.append(f"goal_accuracy 差 {adelta:.3f} 在 [{CONDITIONAL_DELTA}, {CLEAR_BETTER_DELTA})，有条件更优")
        return GainRecommendation(verdict="conditional", winner=winner,
                                  delta_goal_accuracy=round(delta, 4),
                                  comparable=comparable, reasons=reasons)

    # 4. 多维综合（结果相当）
    dims, wins = _multi_dimension_comparison(a, b)
    better = None
    for name, count in wins.items():
        if count >= 3:
            better = name

    if better is not None:
        reasons.append(f"结果相当，但 {better} 在效率维度综合领先（≥3 项）")
        return GainRecommendation(verdict="efficiency_better", winner=better,
                                  delta_goal_accuracy=round(delta, 4),
                                  comparable=comparable,
                                  dimension_comparison=dims, efficiency_wins=wins,
                                  reasons=reasons)

    reasons.append("结果相当且效率维度未分出明显优劣，两者增益相当")
    return GainRecommendation(verdict="both_acceptable", winner=None,
                              delta_goal_accuracy=round(delta, 4),
                              comparable=comparable,
                              dimension_comparison=dims, efficiency_wins=wins,
                              reasons=reasons)


def evaluate_pair(a: Evidence, b: Evidence) -> tuple[SecurityRecommendation, GainRecommendation]:
    """对一对 skill 做双轨判定，返回 (安全结论, 增益结论)。"""
    return security_recommendation(a, b), gain_recommendation(a, b)
