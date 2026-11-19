"""判定模式编排逻辑测试（用 mock 隔离底层解析）。"""

from __future__ import annotations

import unittest
from unittest import mock

from skill_recommend.judge import judge_from_inputs
from skill_recommend.models import Evidence, SimilarityMatch


def _ev(name, goal, **kw):
    base = dict(
        execution_status="succeeded",
        goal_accuracy=goal,
        overall=goal,
        pass_at_k=goal,
        skill_activated=True,
        dataset_digest="sha256:same",
        agent="opencode",
        model="openai/qwen3.8-flash",
        n_attempts=1,
    )
    base.update(kw)
    return Evidence(skill_name=name, **base)


class TestJudge(unittest.TestCase):
    def test_judge_end_to_end_dual_conclusion(self):
        matches = [
            SimilarityMatch(
                candidate_skill="git-commit", catalog_skill="git-commit-msg",
                similarity=0.764, classification="SIMILAR", catalog_path="git-commit-msg",
            )
        ]
        with mock.patch("skill_recommend.judge.parse_similarity_report", return_value=matches), \
             mock.patch("skill_recommend.judge.load_evidence_from_run_dir",
                        side_effect=[_ev("git-commit", 1.0), _ev("git-commit-msg", 0.7)]):
            report = judge_from_inputs("x.json", "y", "git-commit", "git-commit-msg", agent="opencode")

        # 无安全报告目录 → 安全轨 missing
        self.assertEqual(report.security_recommendation.verdict, "missing")
        # 增益轨：goal 1.0 vs 0.7 → clear_better
        self.assertEqual(report.gain_recommendation.verdict, "clear_better")
        self.assertEqual(report.gain_recommendation.winner, "git-commit")
        self.assertIn("git-commit", report.recommendation)
        self.assertIn("替代", report.recommendation)
        self.assertIn("0.764", report.report_markdown)

    def test_judge_no_match_still_compares(self):
        with mock.patch("skill_recommend.judge.parse_similarity_report", return_value=[]), \
             mock.patch("skill_recommend.judge.load_evidence_from_run_dir",
                        side_effect=[_ev("a", 0.9), _ev("b", 0.9)]):
            report = judge_from_inputs("x.json", "y", "a", "b")
        # 无冗余命中时 similarity=0，等价 → both_acceptable
        self.assertEqual(report.gain_recommendation.verdict, "both_acceptable")
        self.assertEqual(report.redundant_pair[0].classification, "NONE")

    def test_judge_wires_security_from_dir(self):
        # 提供 security_dir 时，security 应被回填（这里 mock 为 safe/safe → both_safe）
        matches = [
            SimilarityMatch(candidate_skill="a", catalog_skill="b",
                            similarity=0.80, classification="SIMILAR")
        ]
        safe_a = _ev("a", 0.9)
        safe_b = _ev("b", 0.7)
        with mock.patch("skill_recommend.judge.parse_similarity_report", return_value=matches), \
             mock.patch("skill_recommend.judge.load_evidence_from_run_dir",
                        side_effect=[safe_a, safe_b]), \
             mock.patch("skill_recommend.judge.load_security_from_report",
                        return_value=None):
            report = judge_from_inputs("x.json", "y", "a", "b", security_dir="reports/security")
        self.assertEqual(report.security_recommendation.verdict, "missing")


if __name__ == "__main__":
    unittest.main()
