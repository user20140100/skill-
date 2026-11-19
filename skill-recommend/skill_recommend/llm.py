"""可选 LLM 报告增强。

用 OpenAI 兼容网关（默认 token.cvte.com）生成一段中文推荐叙述。
任何失败（未配置 key、网络错误、HTTP 非 200、解析失败）都返回 ``None``，
由调用方回退到模板叙述。LLM 只负责叙述，不改变规则结论。
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from . import config
from .models import RecommendationReport


def _build_prompt(report: RecommendationReport) -> str:
    """构造给 LLM 的 prompt：只给证据与规则结论，要求引用字段、不新增事实。"""
    evidence = []
    for ev in report.evidence:
        sec = ev.security.verdict if ev.security else "N/A"
        evidence.append(
            f"- {ev.skill_name}: goal_accuracy={ev.goal_accuracy}, overall={ev.overall}, "
            f"pass_at_k={ev.pass_at_k}, lift(goal)={ev.lift_goal_accuracy}, "
            f"token={ev.token_cost}, 安全={sec}, 状态={ev.execution_status}"
        )
    sec_rec = report.security_recommendation
    gain_rec = report.gain_recommendation
    return (
        "你是 Agent Skill 评估系统的报告撰写助手。以下是两个冗余冲突 skill 在同一组"
        "评测用例上的证据和两条彼此独立的确定性规则结论（安全轨与增益轨）。"
        "请用中文写一段 3~5 句的推荐叙述，必须引用给出的具体字段数值，"
        "不得编造未提供的数字或事实，不得推翻或合并这两条结论。\n\n"
        f"安全结论：{sec_rec.verdict}，安全角度更推荐={sec_rec.winner or '无'}，"
        f"理由：{'；'.join(sec_rec.reasons) if sec_rec.reasons else '无'}\n"
        f"增益结论：{gain_rec.verdict}，增益更优={gain_rec.winner or '无'}，"
        f"goal_accuracy 差={gain_rec.delta_goal_accuracy}，"
        f"可比性={'满足' if gain_rec.comparable else '不满足'}，"
        f"理由：{'；'.join(gain_rec.reasons) if gain_rec.reasons else '无'}\n\n"
        "证据：\n" + "\n".join(evidence) + "\n\n"
        "请直接输出叙述正文，不要输出标题或 markdown 代码块。"
    )


def generate_narrative(
    report: RecommendationReport,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 60.0,
) -> str | None:
    """调用 LLM 生成推荐叙述；失败返回 ``None``。"""
    base_url = base_url or config.LLM_BASE_URL
    api_key = api_key or config.LLM_API_KEY
    model = model or config.LLM_MODEL
    if not api_key:
        return None

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个严谨的评估报告撰写助手。"},
            {"role": "user", "content": _build_prompt(report)},
        ],
        "temperature": 0.2,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError):
        return None

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    text = content.strip() if isinstance(content, str) else ""
    return text or None
