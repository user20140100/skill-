"""常量与配置加载。

判定阈值集中在此，便于调整与测试。所有阈值均为确定性规则的一部分，
LLM 不得覆盖。
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Tier2 相似度阈值（与 SkillEvaluator 默认一致） ---
SIMILAR_THRESHOLD = 0.75          # 触发冗余推荐的相似度下限
EXACT_DUPLICATE = 0.95
HIGH_SIMILARITY = 0.90

# --- 增益差值阈值（同一 case 集上的 goal_accuracy 差） ---
CLEAR_BETTER_DELTA = 0.10          # Δ >= 0.10 判为「明确更优」
CONDITIONAL_DELTA = 0.05           # 0.05 <= Δ < 0.10 判为「有条件更优」

# --- 硬门槛 ---
MIN_TIER1_QUALITY = 70.0           # 质量分低于此值则降级

# --- Tier3 结果文件相对 run 目录的名称 ---
RESULT_JSON = "result.json"
LIFT_JSON = "lift.json"
PASS_AT_K_LIFT_JSON = "pass_at_k_lift.json"
RUN_CONFIG_JSON = "run_config.json"

# --- LLM 网关（可选报告增强） ---
# 从环境变量读取；未配置时回退到模板报告。
LLM_BASE_URL = os.environ.get("SKILL_EVAL_LLM_BASE_URL", "https://token.cvte.com/v1")
LLM_API_KEY = os.environ.get("SKILL_EVAL_LLM_API_KEY", os.environ.get("LLM_API_KEY", ""))
LLM_MODEL = os.environ.get("SKILL_EVAL_LLM_MODEL", "qwen3.8-flash")


def project_root() -> Path:
    """返回仓库根目录（skill-recommend 的上级）。"""
    return Path(__file__).resolve().parent.parent.parent
