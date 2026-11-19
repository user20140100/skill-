"""tier3 解析层测试：用真实 calculator 产物作为 golden fixture。"""

from __future__ import annotations

import unittest
from pathlib import Path

from skill_recommend.tier3 import load_evidence_from_run_dir

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadEvidence(unittest.TestCase):
    def test_load_completed_run(self):
        ev = load_evidence_from_run_dir("calculator", FIXTURES / "calculator", agent="opencode")
        self.assertEqual(ev.skill_name, "calculator")
        self.assertEqual(ev.execution_status, "succeeded")
        self.assertTrue(ev.is_complete)
        self.assertAlmostEqual(ev.goal_accuracy, 1.0)
        self.assertAlmostEqual(ev.overall, 1.0)
        self.assertAlmostEqual(ev.lift_goal_accuracy, 1.0)
        self.assertAlmostEqual(ev.pass_at_k, 1.0)
        self.assertTrue(ev.skill_activated)
        self.assertEqual(ev.token_cost, 23847)
        self.assertEqual(ev.agent, "opencode")
        self.assertTrue(ev.dataset_digest.startswith("sha256:"))
        self.assertNotEqual(ev.build_comparable_key(), "")
        # 多维增益（6.3）：流程 / token / 时间
        self.assertAlmostEqual(ev.skill_execution, 1.0)
        self.assertAlmostEqual(ev.skill_efficiency, 1.0)
        self.assertEqual(ev.prompt_tokens, 23766)
        self.assertEqual(ev.completion_tokens, 81)
        self.assertAlmostEqual(ev.duration_seconds, 400.082)
        # fixtures 无 trajectory.json → rounds 为 None（不抛异常）
        self.assertIsNone(ev.rounds)

    def test_load_failed_run(self):
        ev = load_evidence_from_run_dir("calculator", FIXTURES / "calculator-failed", agent="opencode")
        self.assertEqual(ev.execution_status, "failed")
        self.assertFalse(ev.is_complete)
        self.assertTrue(ev.notes, "失败运行必须有说明")

    def test_missing_run_dir(self):
        ev = load_evidence_from_run_dir("calculator", FIXTURES / "does-not-exist", agent="opencode")
        self.assertEqual(ev.execution_status, "")
        self.assertFalse(ev.is_complete)
        self.assertTrue(ev.notes, "缺失目录应产生说明")


if __name__ == "__main__":
    unittest.main()
