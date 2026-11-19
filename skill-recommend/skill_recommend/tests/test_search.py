"""联网搜索模块测试（用 mock 输出，不实际调用 cskills）。"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from skill_recommend.models import ExternalCandidate
from skill_recommend.search import (
    _parse_find_output,
    merge_candidates,
    search_skills,
    semantic_candidates_from_report,
    strip_ansi,
)

FIXTURES = Path(__file__).parent / "fixtures"

_SAMPLE = (
    "  Found 2 skills matching \"commit\":\n"
    "\n"
    "  \x1b[1;36mgit-commit   \x1b[0m \x1b[2mGit Commit Skill\x1b[0m\n"
    "    tags: \x1b[2m\x1b[0m    by \x1b[2mzhangfan3427\x1b[0m    \x1b[2mv1.0.15\x1b[0m\n"
    "\n"
    "  \x1b[1;36mcommit-message   \x1b[0m \x1b[2m结构化提交信息\x1b[0m\n"
    "    tags: \x1b[2m\x1b[0m    by \x1b[2mchenhaibing\x1b[0m    \x1b[2mv0.0.1\x1b[0m\n"
    "\n"
    "  Install: cskills add <name> [<name>...]\n"
)


class TestSearch(unittest.TestCase):
    def test_strip_ansi(self):
        self.assertEqual(strip_ansi("\x1b[1;36mfoo\x1b[0m"), "foo")

    def test_parse_find_output(self):
        clean = strip_ansi(_SAMPLE)
        parsed = _parse_find_output(clean)
        names = [n for n, _ in parsed]
        self.assertEqual(names, ["git-commit", "commit-message"])
        self.assertIn("Git Commit Skill", parsed[0][1])

    def test_search_skills_mock(self):
        with mock.patch("skill_recommend.search._run_cskills", return_value=_SAMPLE):
            candidates = search_skills("commit")
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].name, "git-commit")
        self.assertEqual(candidates[0].source, "cskills")
        self.assertFalse(candidates[0].evaluated)

    def test_search_skills_no_cskills(self):
        with mock.patch("skill_recommend.search._run_cskills", return_value=None):
            self.assertEqual(search_skills("commit"), [])


class TestSemanticCandidates(unittest.TestCase):
    def test_semantic_candidates_from_report(self):
        candidates = semantic_candidates_from_report(FIXTURES / "company-similarity-report.json")
        self.assertEqual(len(candidates), 2)
        first = candidates[0]
        self.assertEqual(first.name, "git-commit-msg")
        self.assertEqual(first.source, "company-library")
        self.assertAlmostEqual(first.similarity, 0.82)
        self.assertTrue(first.evaluated)

    def test_merge_candidates_dedup_and_order(self):
        semantic = [
            ExternalCandidate(name="git-commit-msg", source="company-library", similarity=0.82, evaluated=True),
            ExternalCandidate(name="commit-message", source="company-library", similarity=0.76, evaluated=True),
        ]
        keyword = [
            ExternalCandidate(name="git-commit-msg", source="cskills", description="结构化提交信息"),
            ExternalCandidate(name="commit-helper", source="cskills", description="提交辅助"),
        ]
        merged = merge_candidates(keyword, semantic)
        # 语义候选在前、按相似度降序；关键词候选排后
        self.assertEqual([c.name for c in merged], ["git-commit-msg", "commit-message", "commit-helper"])
        # 同名去重：保留语义候选，附上关键词描述
        self.assertEqual(merged[0].similarity, 0.82)
        self.assertIn("结构化提交信息", merged[0].description)
        # 纯关键词候选无分数
        self.assertIsNone(merged[2].similarity)


if __name__ == "__main__":
    unittest.main()
