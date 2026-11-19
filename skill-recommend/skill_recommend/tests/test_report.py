"""报告模板测试（双结论渲染）。"""

from __future__ import annotations

import unittest

from skill_recommend.models import (
    Evidence,
    ExternalCandidate,
    GainRecommendation,
    RecommendationReport,
    SecurityRecommendation,
    SimilarityMatch,
)
from skill_recommend.report import build_recommendation_text, render_markdown


def _report() -> RecommendationReport:
    match = SimilarityMatch(
        candidate_skill="git-commit-msg",
        catalog_skill="git-commit",
        similarity=0.764,
        classification="SIMILAR",
        catalog_path="git-commit",
    )
    a = Evidence(skill_name="git-commit", goal_accuracy=1.0, overall=1.0,
                 pass_at_k=1.0, lift_goal_accuracy=0.3, token_cost=23847,
                 execution_status="succeeded", dataset_digest="sha256:same",
                 agent="opencode", model="openai/qwen3.8-flash", n_attempts=1, run_id="r1")
    b = Evidence(skill_name="git-commit-msg", goal_accuracy=0.7, overall=0.72,
                 pass_at_k=0.5, lift_goal_accuracy=0.0, token_cost=30000,
                 execution_status="succeeded", dataset_digest="sha256:same",
                 agent="opencode", model="openai/qwen3.8-flash", n_attempts=1, run_id="r2")
    sec = SecurityRecommendation(verdict="both_safe")
    gain = GainRecommendation(verdict="clear_better", winner="git-commit",
                              delta_goal_accuracy=0.3, comparable=True,
                              reasons=["goal_accuracy 差 0.300 ≥ 0.10，明确更优"])
    return RecommendationReport(redundant_pair=[match], evidence=[a, b],
                                security_recommendation=sec, gain_recommendation=gain)


class TestReport(unittest.TestCase):
    def test_recommendation_text_dual_conclusion(self):
        report = _report()
        text = build_recommendation_text(report)
        self.assertIn("git-commit", text)
        self.assertIn("git-commit-msg", text)
        self.assertIn("替代", text)            # 增益轨 clear_better 叙述
        self.assertIn("安全", text)            # 安全轨叙述

    def test_render_markdown_contains_evidence(self):
        report = _report()
        report.recommendation = build_recommendation_text(report)
        md = render_markdown(report)
        self.assertIn("git-commit", md)
        self.assertIn("0.764", md)          # 相似度
        self.assertIn("sha256:same", md)    # 复现信息
        self.assertIn("opencode", md)
        self.assertIn("替代", md)
        self.assertIn("安全结论", md)       # 双结论分节
        self.assertIn("增益结论", md)

    def test_render_markdown_external_candidates_similarity(self):
        report = _report()
        report.recommendation = build_recommendation_text(report)
        report.external_candidates = [
            ExternalCandidate(name="git-commit-msg", source="company-library", similarity=0.82, evaluated=True),
            ExternalCandidate(name="commit-helper", source="cskills", description="提交辅助"),
        ]
        md = render_markdown(report)
        self.assertIn("0.820", md)           # 语义候选相似度列
        self.assertIn("company-library", md)
        self.assertIn("commit-helper", md)


if __name__ == "__main__":
    unittest.main()
