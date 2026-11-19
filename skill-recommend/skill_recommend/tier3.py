"""Tier3 结果解析：从 SkillEvaluator 的 run 目录提取归一化证据。

解析目标字段（对应真实产物结构，见 fixtures/calculator）：

- ``result.json``：``execution_status`` / ``run_id`` / ``skill_name`` /
  ``dataset_digest`` / ``agents.<agent>.overall_with_skill`` /
  ``agents.<agent>.lift.goal_accuracy`` / ``agents.<agent>.skill_activation`` /
  ``agents.<agent>.with_skill.skill_execution`` / ``.skill_efficiency`` /
  ``token_usage.agents.<agent>.with_skill.totals``（prompt/completion/total）/
  顶层 ``duration_seconds``
- ``<agent>/pass_at_k_lift.json``：``with_skill`` / ``without_skill`` / ``delta``
- ``<agent>/with-skill/trials/*/trajectory.json``：``steps`` 数量汇总为 ``rounds``

解析过程只读，不做任何网络或沙盒调用。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import PASS_AT_K_LIFT_JSON, RESULT_JSON
from .models import Evidence


def _load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _first_agent(result: dict, agent: str | None) -> str | None:
    """返回要解析的 agent 名：显式指定优先，否则取 agents 的第一个 key。"""
    agents = result.get("agents") or {}
    if not isinstance(agents, dict):
        return None
    if agent and agent in agents:
        return agent
    if agents:
        return next(iter(agents))
    return None


def _goal_accuracy_from_lift(agent_data: dict) -> float | None:
    lift = agent_data.get("lift")
    if not isinstance(lift, dict):
        return None
    ga = lift.get("goal_accuracy")
    if isinstance(ga, dict):
        value = ga.get("with_skill")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def _lift_goal_accuracy(agent_data: dict) -> float | None:
    lift = agent_data.get("lift")
    if not isinstance(lift, dict):
        return None
    ga = lift.get("goal_accuracy")
    if isinstance(ga, dict):
        value = ga.get("delta")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def _pass_at_k(result: dict, agent_name: str, run_dir: Path) -> float | None:
    # 优先读 <agent>/pass_at_k_lift.json 的 with_skill 率。
    pk = _load_json(run_dir / agent_name / PASS_AT_K_LIFT_JSON)
    if pk is not None:
        value = pk.get("with_skill")
        if isinstance(value, (int, float)):
            return float(value)
    # fallback：从 result.json 的 agents.<agent>.pass_at_k 计算。
    agent_data = (result.get("agents") or {}).get(agent_name) or {}
    pk = agent_data.get("pass_at_k")
    if isinstance(pk, dict):
        ws = pk.get("with_skill")
        if isinstance(ws, dict):
            passed = ws.get("passed_cases")
            total = ws.get("total_cases")
            if isinstance(passed, (int, float)) and isinstance(total, (int, float)) and total > 0:
                return float(passed) / float(total)
    return None


def _token_totals(result: dict, agent_name: str) -> dict:
    usage = result.get("token_usage")
    if not isinstance(usage, dict):
        return {}
    agents = usage.get("agents")
    if not isinstance(agents, dict):
        return {}
    arm = (agents.get(agent_name) or {}).get("with_skill") or {}
    totals = arm.get("totals")
    return totals if isinstance(totals, dict) else {}


def _token_cost(result: dict, agent_name: str) -> int | None:
    value = _token_totals(result, agent_name).get("total_tokens")
    return value if isinstance(value, int) else None


def _token_breakdown(result: dict, agent_name: str) -> tuple[int | None, int | None, int | None]:
    """返回 (prompt_tokens, completion_tokens, total_tokens)。"""
    totals = _token_totals(result, agent_name)
    prompt = totals.get("prompt_tokens")
    completion = totals.get("completion_tokens")
    total = totals.get("total_tokens")
    return (
        prompt if isinstance(prompt, int) else None,
        completion if isinstance(completion, int) else None,
        total if isinstance(total, int) else None,
    )


def _with_skill_metric(agent_data: dict, key: str) -> float | None:
    ws = agent_data.get("with_skill")
    if not isinstance(ws, dict):
        return None
    value = ws.get(key)
    return float(value) if isinstance(value, (int, float)) else None


def _duration_seconds(result: dict) -> float | None:
    value = result.get("duration_seconds")
    return float(value) if isinstance(value, (int, float)) else None


def _rounds(run_dir: Path, agent_name: str) -> int | None:
    """从 with-skill 各 trial 的 trajectory.json 汇总执行轮数（len(steps) 之和）。

    优先扫描 ``<agent>/with-skill/trials/*/trajectory.json``；缺失时返回 None。
    """
    trials_dir = run_dir / agent_name / "with-skill" / "trials"
    total = 0
    found = False
    if trials_dir.is_dir():
        for traj in trials_dir.rglob("trajectory.json"):
            data = _load_json(traj)
            if not data:
                continue
            steps = data.get("steps")
            if isinstance(steps, list):
                total += len(steps)
                found = True
    if found:
        return total
    # fallback：单个 trajectory.json（若 run 目录直接暴露）
    traj = _load_json(run_dir / agent_name / "trajectory.json")
    if traj and isinstance(traj.get("steps"), list):
        return len(traj["steps"])
    return None


def _activation(agent_data: dict) -> bool | None:
    act = agent_data.get("skill_activation")
    if isinstance(act, dict):
        status = act.get("status")
        if status == "activated":
            return True
        if status in ("inactive", "unknown", "not_activated"):
            return False
    return None


def load_evidence_from_run_dir(skill_name: str, run_dir: Path, agent: str | None = None) -> Evidence:
    """从 SkillEvaluator 的 run 目录构造 Evidence。

    任何缺失/损坏的产物都会落入一个 ``notes`` 说明，而不会抛异常，
    以保证判定层可以继续输出「证据不足」而非崩溃。
    """
    ev = Evidence(skill_name=skill_name)
    if run_dir is None:
        ev.notes.append("Tier3 结果缺失或损坏（未找到可解析的 result.json）")
        return ev
    run_dir = Path(run_dir)
    result = _load_json(run_dir / RESULT_JSON)

    if result is None:
        ev.notes.append("Tier3 结果缺失或损坏（未找到可解析的 result.json）")
        return ev

    ev.execution_status = str(result.get("execution_status") or "")
    ev.run_id = str(result.get("run_id") or "")
    ev.dataset_digest = str(result.get("dataset_digest") or "")
    if result.get("skill_name"):
        ev.skill_name = str(result["skill_name"])

    agent_name = _first_agent(result, agent)
    if agent_name is None:
        ev.notes.append("result.json 中无 agent 结果")
        return ev
    ev.agent = agent_name

    agent_data = (result.get("agents") or {}).get(agent_name) or {}

    # model：agent 级 model 字段。
    if isinstance(agent_data.get("model"), str):
        ev.model = agent_data["model"]

    ev.overall = _number(agent_data.get("overall_with_skill"))
    ev.goal_accuracy = _goal_accuracy_from_lift(agent_data)
    ev.lift_goal_accuracy = _lift_goal_accuracy(agent_data)
    ev.skill_activated = _activation(agent_data)
    ev.pass_at_k = _pass_at_k(result, agent_name, run_dir)
    ev.token_cost = _token_cost(result, agent_name)
    ev.n_attempts = _n_attempts(result)

    # 多维增益（6.3）：流程 / token / 时间 / 轮数
    ev.skill_execution = _with_skill_metric(agent_data, "skill_execution")
    ev.skill_efficiency = _with_skill_metric(agent_data, "skill_efficiency")
    ev.prompt_tokens, ev.completion_tokens, _ = _token_breakdown(result, agent_name)
    ev.duration_seconds = _duration_seconds(result)
    ev.rounds = _rounds(run_dir, agent_name)

    if ev.execution_status != "succeeded":
        ev.notes.append(f"Tier3 运行未成功（execution_status={ev.execution_status or 'unknown'}）")
    if ev.goal_accuracy is None:
        ev.notes.append("缺少 goal_accuracy 证据")
    if ev.skill_activated is False:
        ev.notes.append("skill 在 with-skill 试验中未被激活（INCONCLUSIVE）")

    return ev


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _n_attempts(result: dict) -> int | None:
    rc = result.get("run_config")
    if isinstance(rc, dict):
        harbor = rc.get("harbor")
        if isinstance(harbor, dict):
            n = harbor.get("n_attempts")
            if isinstance(n, int):
                return n
    return None
