"""相似检测（detect）测试：命令生成与报告解析，用 mock 隔离底层执行。"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from skill_recommend.detect import detect_report_path, detect_similar
from skill_recommend.models import SimilarityMatch


class TestDetectReportPath(unittest.TestCase):
    def test_report_path_subdir(self):
        p = detect_report_path("positive/json-format")
        self.assertTrue(p.as_posix().endswith("company-match/positive_json-format/skillevaluator-similarity.json"))


class TestDetectSimilar(unittest.TestCase):
    def test_dry_run_prints_commands(self):
        result = detect_similar("positive/json-format")
        self.assertFalse(result["executed"])
        self.assertEqual(len(result["commands"]), 2)
        self.assertEqual(result["matches"], [])
        # 首条建 catalog，次条 query
        self.assertIn("--save-catalog", result["commands"][0])
        self.assertIn("--catalog", result["commands"][1])

    def test_run_parses_and_filters(self):
        matches = [
            SimilarityMatch(candidate_skill="json-format", catalog_skill="git-commit-msg",
                            similarity=0.82, classification="SIMILAR", catalog_path="G9/git-commit-msg"),
            SimilarityMatch(candidate_skill="json-format", catalog_skill="commit-message",
                            similarity=0.60, classification="LOOSELY_RELATED", catalog_path="G2/commit-message"),
        ]
        calls = []

        def fake_executor(cmd):
            calls.append(cmd)
            return 0

        with mock.patch("skill_recommend.detect.parse_similarity_report", return_value=matches):
            result = detect_similar(
                "positive/json-format",
                threshold=0.75,
                run=True,
                executor=fake_executor,
            )
        self.assertTrue(result["executed"])
        self.assertEqual(len(calls), 2)
        # 只有 0.82 >= 0.75 命中
        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0].catalog_skill, "git-commit-msg")
        self.assertIn("skillevaluator-similarity.json", result["report_path"])

    def test_run_failure_short_circuits(self):
        def failing_executor(cmd):
            return 1

        result = detect_similar("positive/json-format", run=True, executor=failing_executor)
        self.assertFalse(result["executed"])
        self.assertIn("failed_command", result)


if __name__ == "__main__":
    unittest.main()
