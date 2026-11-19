"""任务 B 批处理扫描：discover / 命令生成 / 分类 / 沙盒 A/B 提取 / 报告构建与渲染。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_recommend.batch import (
    BatchAuditReport,
    SandboxComparison,
    SkillScanRow,
    build_batch_report,
    build_batch_scan_commands,
    discover_skills,
    load_category,
    load_sandbox_comparison,
    render_html,
    render_markdown,
)
from skill_recommend.models import SecurityEvidence


def _write_skill(root: Path, rel: str) -> None:
    d = root / rel
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("# skill\n", encoding="utf-8")


class TestDiscoverSkills(unittest.TestCase):
    def test_finds_skill_dirs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, "a/calculator")
            _write_skill(root, "a/requirement-spec")
            (root / "a" / "no-skill").mkdir(parents=True)  # 无 SKILL.md，不算 skill
            (root / "a" / "no-skill" / "README.md").write_text("x", encoding="utf-8")
            _write_skill(root, "b/es-log-query")
            skills = discover_skills(root / "a")
            self.assertEqual(skills, ["calculator", "requirement-spec"])

    def test_skips_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, "_hidden/skill")
            _write_skill(root, "normal/skill")
            skills = discover_skills(root)
            self.assertEqual(skills, ["normal/skill"])

    def test_base_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, "ds/library-demo/calculator")
            _write_skill(root, "ds/library-demo/requirement-spec")
            skills = discover_skills(root / "ds" / "library-demo", base=root / "ds")
            self.assertEqual(skills, ["library-demo/calculator", "library-demo/requirement-spec"])


class TestBuildBatchScanCommands(unittest.TestCase):
    def test_one_skill_two_commands(self):
        cmds = build_batch_scan_commands(["library-demo/calculator"])
        self.assertEqual(len(cmds), 2)
        self.assertIn("skillspector", cmds[0])
        self.assertIn("/scan/library-demo/calculator", cmds[0])
        self.assertIn("--no-llm", cmds[0])
        self.assertIn("tier1", cmds[1])
        self.assertIn("/skills/library-demo/calculator", cmds[1])
        self.assertIn("--no-llm", cmds[1])

    def test_multiple_skills_interleaved(self):
        cmds = build_batch_scan_commands(["a", "b"])
        self.assertEqual(len(cmds), 4)
        self.assertIn("skillspector", cmds[0])
        self.assertIn("tier1", cmds[1])
        self.assertIn("skillspector", cmds[2])
        self.assertIn("tier1", cmds[3])

    def test_use_llm_omits_no_llm(self):
        cmds = build_batch_scan_commands(["library-demo/calculator"], use_llm=True)
        self.assertEqual(len(cmds), 2)
        self.assertNotIn("--no-llm", cmds[0])
        self.assertNotIn("--no-llm", cmds[1])
        self.assertIn("/scan/library-demo/calculator", cmds[0])
        self.assertIn("/skills/library-demo/calculator", cmds[1])


class TestLoadCategory(unittest.TestCase):
    def _manifest(self, path: Path) -> Path:
        m = {"skills": [
            {"name": "calculator", "category": "positive"},
            {"name": "requirement-spec", "category": "redundant"},
            {"name": "es-log-query", "category": "security"},
        ]}
        path.write_text(json.dumps(m), encoding="utf-8")
        return path

    def test_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._manifest(Path(tmp) / "manifest.json")
            self.assertEqual(load_category(p, "requirement-spec"), "redundant")

    def test_miss_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._manifest(Path(tmp) / "manifest.json")
            self.assertEqual(load_category(p, "nope"), "unknown")

    def test_missing_file(self):
        self.assertEqual(load_category(Path("/nonexistent.json"), "x"), "unknown")


class TestLoadSandboxComparison(unittest.TestCase):
    def _write_result(self, run_dir: Path) -> None:
        result = {
            "execution_status": "succeeded",
            "run_id": "test-run",
            "agents": {
                "opencode": {
                    "model": "openai/qwen3.8-flash",
                    "overall_with_skill": 0.9,
                    "overall_without_skill": 0.7,
                    "lift": {"goal_accuracy": {"with_skill": 1.0, "without_skill": 0.5, "delta": 0.5}},
                    "pass_at_k": {"with_skill": {"rate": 1.0}, "without_skill": {"rate": 0.5}},
                    "skill_activation": {"status": "activated"},
                }
            },
        }
        run_dir.mkdir(parents=True)
        (run_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")

    def test_parses_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_result(root / "calculator" / "20260101_000000_1_abc")
            sc = load_sandbox_comparison("calculator", root)
            self.assertIsNotNone(sc)
            self.assertEqual(sc.with_overall, 0.9)
            self.assertEqual(sc.without_overall, 0.7)
            self.assertEqual(sc.with_goal_accuracy, 1.0)
            self.assertEqual(sc.without_goal_accuracy, 0.5)
            self.assertEqual(sc.lift_goal_accuracy, 0.5)
            self.assertEqual(sc.with_pass_at_k, 1.0)
            self.assertEqual(sc.without_pass_at_k, 0.5)
            self.assertTrue(sc.skill_activated)
            self.assertEqual(sc.run_id, "test-run")

    def test_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_sandbox_comparison("calculator", Path(tmp)))


class TestBuildBatchReport(unittest.TestCase):
    def _sec(self, root: Path, skill: str, unsafe: bool = False) -> None:
        sub = root / f"library-demo_{skill}"
        sub.mkdir(parents=True)
        if unsafe:
            sp = {
                "risk_assessment": {"score": 36, "severity": "MEDIUM",
                                    "recommendation": "CAUTION", "max_issue_severity": "HIGH"},
                "issues": [{"severity": "HIGH", "message": "danger"}],
            }
            t1 = {"overall_status": "failed",
                  "severity_counts": {"critical": 0, "high": 6, "medium": 8, "low": 10},
                  "finding_groups": [{"severity": "high", "message": "t1 danger"}]}
        else:
            sp = {"risk_assessment": {"score": 0, "severity": "NONE",
                                      "recommendation": "SAFE", "max_issue_severity": "NONE"},
                  "issues": []}
            t1 = {"overall_status": "pass",
                  "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                  "finding_groups": []}
        (sub / "skillspector.json").write_text(json.dumps(sp), encoding="utf-8")
        (sub / "skillevaluator-tier1.json").write_text(json.dumps(t1), encoding="utf-8")

    def test_filters_high_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sec = root / "security"
            self._sec(sec, "es-log-query", unsafe=True)
            self._sec(sec, "calculator")
            self._sec(sec, "requirement-spec")
            report = build_batch_report(
                ["library-demo/calculator", "library-demo/requirement-spec", "library-demo/es-log-query"],
                security_dir=sec,
                results_dir=None,
            )
            self.assertEqual(len(report.rows), 3)
            self.assertEqual([r.skill_name for r in report.high_risk_rows], ["es-log-query"])
            self.assertEqual(report.summary["total"], 3)
            self.assertEqual(report.summary["unsafe"], 1)
            self.assertEqual(report.summary["safe"], 2)

    def test_missing_security_graceful(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = build_batch_report(
                ["library-demo/calculator"], security_dir=root / "nope", results_dir=None
            )
            self.assertEqual(len(report.rows), 1)
            self.assertIsNone(report.rows[0].security)


class TestRender(unittest.TestCase):
    def _report(self) -> BatchAuditReport:
        sec_safe = SecurityEvidence(
            skillspector={"risk_score": 0, "max_issue_severity": "NONE"},
            tier1={"severity_counts": {"critical": 0, "high": 0}},
            verdict="safe",
        )
        sec_unsafe = SecurityEvidence(
            skillspector={"risk_score": 36, "max_issue_severity": "HIGH"},
            tier1={"severity_counts": {"critical": 0, "high": 6}},
            verdict="unsafe",
            high_severity_findings=[{"source": "skillspector", "severity": "HIGH", "message": "danger"}],
        )
        sandbox = SandboxComparison(
            with_overall=0.9, without_overall=0.7,
            with_goal_accuracy=1.0, without_goal_accuracy=0.5, lift_goal_accuracy=0.5,
            with_pass_at_k=1.0, without_pass_at_k=0.5,
            skill_activated=True, run_id="r", agent="opencode", model="m",
            execution_status="succeeded",
        )
        rows = [
            SkillScanRow("library-demo/calculator", "calculator", "positive", sec_safe, sandbox),
            SkillScanRow("library-demo/es-log-query", "es-log-query", "security", sec_unsafe, None),
        ]
        return BatchAuditReport(directory="ds", generated_at="2026-01-01", rows=rows)

    def test_render_markdown_sections(self):
        md = render_markdown(self._report())
        self.assertIn("高危风险项", md)
        self.assertIn("es-log-query", md)
        self.assertIn("沙盒对比", md)
        self.assertIn("calculator", md)

    def test_render_html_sections(self):
        html = render_html(self._report())
        self.assertIn("高危风险项", html)
        self.assertIn("es-log-query", html)
        self.assertIn("沙盒对比", html)
        self.assertIn("calculator", html)


if __name__ == "__main__":
    unittest.main()
