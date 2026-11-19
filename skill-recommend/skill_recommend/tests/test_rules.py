"""双轨推荐规则测试（安全轨 + 增益轨，TDD 核心）。"""

from __future__ import annotations

import unittest

from skill_recommend.models import Evidence, SecurityEvidence
from skill_recommend.rules import evaluate_pair, gain_recommendation, security_recommendation


def make_evidence(
    name: str,
    goal: float = 0.8,
    *,
    status: str = "succeeded",
    activated: bool = True,
    prompt: int | None = 1000,
    completion: int | None = 500,
    duration: float | None = 10.0,
    rounds: int | None = 3,
    skill_execution: float | None = 0.9,
    skill_efficiency: float | None = 0.9,
    digest: str = "sha256:same",
    security: SecurityEvidence | None = None,
    overall: float | None = None,
) -> Evidence:
    ev = Evidence(
        skill_name=name,
        execution_status=status,
        goal_accuracy=goal,
        overall=overall if overall is not None else goal,
        skill_activated=activated,
        dataset_digest=digest,
        agent="opencode",
        model="openai/qwen3.8-flash",
        n_attempts=1,
        prompt_tokens=prompt,
        completion_tokens=completion,
        duration_seconds=duration,
        rounds=rounds,
        skill_execution=skill_execution,
        skill_efficiency=skill_efficiency,
        security=security,
    )
    ev.comparable_key = ev.build_comparable_key()
    return ev


def sec(verdict="safe", *, risk_score=None, severity="NONE", sp_high=0, t1_high=0) -> SecurityEvidence:
    return SecurityEvidence(
        skillspector={"risk_score": risk_score, "severity": severity},
        tier1={"severity_counts": {"critical": 0, "high": t1_high}},
        verdict=verdict,
        high_severity_findings=[{"source": "skillspector", "severity": "HIGH", "message": "x"}] * sp_high,
    )


SAFE = sec("safe")
UNSAFE = sec("unsafe", risk_score=80, severity="HIGH", sp_high=2, t1_high=1)


class TestSecurityTrack(unittest.TestCase):
    def test_both_safe(self):
        r = security_recommendation(make_evidence("A", security=SAFE),
                                    make_evidence("B", security=SAFE))
        self.assertEqual(r.verdict, "both_safe")
        self.assertIsNone(r.winner)

    def test_a_safe_b_unsafe(self):
        r = security_recommendation(make_evidence("A", security=SAFE),
                                    make_evidence("B", security=UNSAFE))
        self.assertEqual(r.verdict, "recommend_a")
        self.assertEqual(r.winner, "A")

    def test_a_unsafe_b_safe(self):
        r = security_recommendation(make_evidence("A", security=UNSAFE),
                                    make_evidence("B", security=SAFE))
        self.assertEqual(r.verdict, "recommend_b")
        self.assertEqual(r.winner, "B")

    def test_both_unsafe_picks_lower_risk(self):
        a = sec("unsafe", risk_score=20, severity="LOW", sp_high=1, t1_high=1)
        b = sec("unsafe", risk_score=90, severity="HIGH", sp_high=3, t1_high=2)
        r = security_recommendation(make_evidence("A", security=a),
                                    make_evidence("B", security=b))
        self.assertIn(r.verdict, ("recommend_a", "recommend_b"))
        self.assertEqual(r.winner, "A")  # 风险更低

    def test_missing_security(self):
        r = security_recommendation(make_evidence("A", security=SAFE),
                                    make_evidence("B", security=None))
        self.assertEqual(r.verdict, "missing")
        self.assertIsNone(r.winner)


class TestGainTrack(unittest.TestCase):
    def test_clear_better(self):
        a = make_evidence("A", goal=1.0)
        b = make_evidence("B", goal=0.7)
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "clear_better")
        self.assertEqual(r.winner, "A")
        self.assertAlmostEqual(r.delta_goal_accuracy, 0.3)

    def test_conditional_better(self):
        a = make_evidence("A", goal=0.85)
        b = make_evidence("B", goal=0.78)
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "conditional")
        self.assertEqual(r.winner, "A")

    def test_efficiency_better_on_result_tie(self):
        # 结果相当，A 在 token 输入/输出、时间、轮数 4 个效率维度全部领先 → 综合领先
        a = make_evidence("A", goal=0.90, prompt=100, completion=50,
                          duration=5.0, rounds=2)
        b = make_evidence("B", goal=0.90, prompt=1000, completion=500,
                          duration=20.0, rounds=8)
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "efficiency_better")
        self.assertEqual(r.winner, "A")
        # 不再输出 process（流程准确性）维度
        self.assertNotIn("process", r.dimension_comparison)

    def test_both_acceptable_on_tie(self):
        a = make_evidence("A", goal=0.90)
        b = make_evidence("B", goal=0.90)
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "both_acceptable")
        self.assertIsNone(r.winner)
        # 仍输出多维对比供参考
        self.assertIn("result", r.dimension_comparison)

    def test_insufficient_on_failed_run(self):
        a = make_evidence("A", goal=1.0)
        b = make_evidence("B", goal=0.9, status="failed")
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "insufficient")

    def test_insufficient_on_not_activated(self):
        a = make_evidence("A", goal=1.0)
        b = make_evidence("B", goal=0.9, activated=False)
        r = gain_recommendation(a, b)
        self.assertEqual(r.verdict, "insufficient")

    def test_incomparable_marks_not_comparable(self):
        a = make_evidence("A", goal=1.0, digest="sha256:aaa")
        b = make_evidence("B", goal=0.7, digest="sha256:bbb")
        r = gain_recommendation(a, b)
        self.assertFalse(r.comparable)
        self.assertEqual(r.verdict, "clear_better")  # 结论仍给出，但标注仅供参考


class TestEvaluatePair(unittest.TestCase):
    def test_returns_both_tracks(self):
        a = make_evidence("A", goal=1.0, security=SAFE)
        b = make_evidence("B", goal=0.7, security=UNSAFE)
        sec_r, gain_r = evaluate_pair(a, b)
        self.assertEqual(sec_r.verdict, "recommend_a")
        self.assertEqual(sec_r.winner, "A")
        self.assertEqual(gain_r.verdict, "clear_better")
        self.assertEqual(gain_r.winner, "A")


if __name__ == "__main__":
    unittest.main()
