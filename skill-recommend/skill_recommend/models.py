"""数据模型：冗余推荐功能的证据与结论结构。

本模块只定义纯数据结构，不包含任何 I/O 或外部调用，便于单元测试。

v1.2 双结论方案：删除单一 ``RuleResult.verdict``，改为
``SecurityRecommendation``（安全结论）与 ``GainRecommendation``（增益结论）
两个独立结论（P7：决策权交用户，不合成单一 verdict）。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimilarityMatch:
    """Tier2 报告中的一条相似命中。

    字段对应 SkillEvaluator Tier2 ``INTER_SKILL`` finding 的 metadata：
    ``bundled_skill`` 是当前候选 skill，``catalog_skill`` 是 catalog 中命中的 skill。
    """

    candidate_skill: str
    catalog_skill: str
    similarity: float
    classification: str
    catalog_path: str = ""


@dataclass
class SecurityEvidence:
    """单个 skill 的完整 Tier1 安全审查证据（SkillSpector + SkillEvaluator Tier1）。

    ``verdict`` 取值：``safe`` / ``unsafe`` / ``missing``，由 :mod:`skill_recommend.security`
    依据 6.2 评级规则确定性计算。
    """

    skillspector: dict = field(default_factory=dict)
    tier1: dict = field(default_factory=dict)
    verdict: str = "missing"
    high_severity_findings: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "skillspector": dict(self.skillspector),
            "tier1": dict(self.tier1),
            "verdict": self.verdict,
            "high_severity_findings": [dict(f) for f in self.high_severity_findings],
        }


@dataclass
class Evidence:
    """单个 skill 的归一化评估证据。

    ``comparable_key`` 由数据集摘要 + agent + model + attempts 拼接而成，
    用于判断两个 skill 的 Tier3 结果是否在同一条实验条件下可比。
    """

    skill_name: str
    run_id: str = ""
    execution_status: str = ""
    goal_accuracy: float | None = None
    overall: float | None = None
    pass_at_k: float | None = None
    lift_goal_accuracy: float | None = None
    skill_activated: bool | None = None
    # 多维增益（6.3）：流程 / token / 时间 / 轮数
    skill_execution: float | None = None
    skill_efficiency: float | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    duration_seconds: float | None = None
    rounds: int | None = None
    dataset_digest: str = ""
    agent: str = ""
    model: str = ""
    n_attempts: int | None = None
    tier1_quality: float | None = None
    token_cost: int | None = None
    security: SecurityEvidence | None = None
    comparable_key: str = ""
    # 可读的失败/不足原因，供报告引用
    notes: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.execution_status == "succeeded" and self.goal_accuracy is not None

    def build_comparable_key(self) -> str:
        if self.comparable_key:
            return self.comparable_key
        parts = [
            self.dataset_digest or "?",
            self.agent or "?",
            self.model or "?",
            str(self.n_attempts) if self.n_attempts is not None else "?",
        ]
        return "|".join(parts)


@dataclass
class SecurityRecommendation:
    """安全轨结论（6.2）。

    ``verdict`` 取值：``both_safe`` / ``recommend_a`` / ``recommend_b`` / ``missing``。
    ``winner`` 为安全角度更推荐的 skill 名（``both_safe`` / ``missing`` 时为 None）。
    """

    verdict: str = "missing"
    winner: str | None = None
    narrative: str = ""
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "winner": self.winner,
            "narrative": self.narrative,
            "reasons": list(self.reasons),
        }


@dataclass
class GainRecommendation:
    """增益轨结论（6.3，多维增益）。

    ``verdict`` 取值：``clear_better`` / ``conditional`` / ``efficiency_better`` /
    ``both_acceptable`` / ``insufficient``。
    """

    verdict: str = "insufficient"
    winner: str | None = None
    delta_goal_accuracy: float | None = None
    comparable: bool = True
    dimension_comparison: dict = field(default_factory=dict)
    efficiency_wins: dict = field(default_factory=dict)
    narrative: str = ""
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "winner": self.winner,
            "delta_goal_accuracy": self.delta_goal_accuracy,
            "comparable": self.comparable,
            "dimension_comparison": self.dimension_comparison,
            "efficiency_wins": self.efficiency_wins,
            "narrative": self.narrative,
            "reasons": list(self.reasons),
        }


@dataclass
class ExternalCandidate:
    """联网搜索得到的外部候选 skill（默认未实测）。

    ``similarity`` 仅在语义复核（embedding 比对）后非空；关键词候选保持 ``None``。
    """

    name: str
    source: str  # cskills / company-library / agentskills.io / github
    description: str = ""
    evaluated: bool = False
    similarity: float | None = None


@dataclass
class RecommendationReport:
    """推荐报告的整体结构（可序列化为 JSON，双结论）。"""

    redundant_pair: list[SimilarityMatch]
    evidence: list[Evidence]
    security_recommendation: SecurityRecommendation
    gain_recommendation: GainRecommendation
    external_candidates: list[ExternalCandidate] = field(default_factory=list)
    comparable: bool = True
    # 可选 LLM 润色综合叙述（仅当 --llm 成功时填充；不得覆盖双结论）
    recommendation: str = ""
    report_markdown: str = ""

    def to_dict(self) -> dict:
        return {
            "redundant_pair": [
                {
                    "candidate_skill": m.candidate_skill,
                    "catalog_skill": m.catalog_skill,
                    "similarity": m.similarity,
                    "classification": m.classification,
                    "catalog_path": m.catalog_path,
                }
                for m in self.redundant_pair
            ],
            "evidence": [
                {
                    "skill": e.skill_name,
                    "run_id": e.run_id,
                    "execution_status": e.execution_status,
                    "goal_accuracy": e.goal_accuracy,
                    "overall": e.overall,
                    "pass_at_k": e.pass_at_k,
                    "lift_goal_accuracy": e.lift_goal_accuracy,
                    "skill_activated": e.skill_activated,
                    "skill_execution": e.skill_execution,
                    "skill_efficiency": e.skill_efficiency,
                    "prompt_tokens": e.prompt_tokens,
                    "completion_tokens": e.completion_tokens,
                    "duration_seconds": e.duration_seconds,
                    "rounds": e.rounds,
                    "dataset_digest": e.dataset_digest,
                    "agent": e.agent,
                    "model": e.model,
                    "n_attempts": e.n_attempts,
                    "tier1_quality": e.tier1_quality,
                    "token_cost": e.token_cost,
                    "security": e.security.to_dict() if e.security else None,
                    "comparable_key": e.build_comparable_key(),
                    "notes": list(e.notes),
                }
                for e in self.evidence
            ],
            "comparable": self.comparable,
            "security_recommendation": self.security_recommendation.to_dict(),
            "gain_recommendation": self.gain_recommendation.to_dict(),
            "external_candidates": [
                {
                    "name": c.name,
                    "source": c.source,
                    "description": c.description,
                    "evaluated": c.evaluated,
                    "similarity": c.similarity,
                }
                for c in self.external_candidates
            ],
            "recommendation": self.recommendation,
        }
