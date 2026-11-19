"""tier2 相似度报告解析层测试。"""

from __future__ import annotations

import unittest
from pathlib import Path

from skill_recommend.config import SIMILAR_THRESHOLD
from skill_recommend.tier2 import matches_above_threshold, parse_similarity_report

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseSimilarityReport(unittest.TestCase):
    def test_parse_findings(self):
        matches = parse_similarity_report(FIXTURES / "similarity-report.json")
        # 只提取 INTER_SKILL 类 finding，忽略 SCHEMA 等无关项
        self.assertEqual(len(matches), 2)
        first = matches[0]
        self.assertEqual(first.candidate_skill, "git-commit-msg")
        self.assertEqual(first.catalog_skill, "git-commit")
        self.assertAlmostEqual(first.similarity, 0.764)
        self.assertEqual(first.classification, "SIMILAR")
        self.assertEqual(first.catalog_path, "git-commit")

    def test_parse_missing_file(self):
        matches = parse_similarity_report(FIXTURES / "nope.json")
        self.assertEqual(matches, [])

    def test_parse_similarity_findings(self):
        # similarity-check 真实输出 category 为 SIMILARITY，metadata 用 entry_a/entry_b
        matches = parse_similarity_report(FIXTURES / "company-similarity-report.json")
        self.assertEqual(len(matches), 2)
        first = matches[0]
        self.assertEqual(first.candidate_skill, "git-commit")
        self.assertEqual(first.catalog_skill, "git-commit-msg")
        self.assertAlmostEqual(first.similarity, 0.82)
        self.assertEqual(first.classification, "SIMILAR")
        self.assertEqual(first.catalog_path, "G9/git-commit-msg")

    def test_matches_above_threshold(self):
        matches = parse_similarity_report(FIXTURES / "similarity-report.json")
        above = matches_above_threshold(matches, SIMILAR_THRESHOLD)
        # 0.764 >= 0.75 命中；0.901 >= 0.75 也命中
        self.assertEqual(len(above), 2)
        below = matches_above_threshold(matches, 0.90)
        # 只有 0.901 >= 0.90
        self.assertEqual(len(below), 1)
        self.assertEqual(below[0].catalog_skill, "git-commit-msg")


if __name__ == "__main__":
    unittest.main()
