"""编排模式命令生成与共享用例复制测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_recommend.pipeline import (
    build_company_catalog_command,
    build_company_match_commands,
    build_company_query_command,
    build_security_scan_commands,
    build_skillspector_scan_command,
    build_tier1_scan_command,
    build_tier3_command,
    copy_shared_evals,
    run_pipeline,
)


class TestPipelineCommands(unittest.TestCase):
    def test_build_company_catalog_command(self):
        cmd = build_company_catalog_command("library-20261118")
        self.assertIn("similarity-check", cmd)
        self.assertIn("/skills/library-20261118", cmd)
        self.assertIn("--save-catalog", cmd)
        self.assertIn("/app/reports/company-catalog.json", cmd)
        self.assertIn("--full-body", cmd)

    def test_build_company_query_command(self):
        cmd = build_company_query_command("redundant/git-commit-msg", output_subdir="redundant_git-commit-msg")
        self.assertIn("--catalog", cmd)
        self.assertIn("/app/reports/company-catalog.json", cmd)
        self.assertIn("--output-dir", cmd)
        self.assertIn("/app/reports/company-match/redundant_git-commit-msg", cmd)
        self.assertIn("--report", cmd)
        self.assertIn("json", cmd)

    def test_build_company_query_command_default_subdir(self):
        cmd = build_company_query_command("positive/json-format")
        self.assertIn("/app/reports/company-match/positive_json-format", cmd)

    def test_build_company_match_commands(self):
        cmds = build_company_match_commands(["a", "b"], "lib")
        self.assertEqual(len(cmds), 3)
        self.assertIn("--save-catalog", cmds[0])
        self.assertIn("--catalog", cmds[1])
        self.assertIn("--catalog", cmds[2])

    def test_build_tier3_command(self):
        cmd = build_tier3_command("positive/json-format", model="qwen3.8-flash")
        self.assertIn("tier3", cmd)
        self.assertIn("--agents", cmd)
        self.assertIn("opencode", cmd)
        self.assertIn("openai/qwen3.8-flash", cmd)
        self.assertIn("--max-cases", cmd)
        # 默认带上统一结果目录，供 judge 稳定定位
        self.assertIn("--results-dir", cmd)
        self.assertIn("/app/reports/reco-results", cmd)


class TestCopySharedEvals(unittest.TestCase):
    def _make_dataset(self) -> Path:
        root = Path(tempfile.mkdtemp())
        src = root / "positive" / "changelog" / "evals"
        src.mkdir(parents=True)
        (src / "evals.json").write_text('{"skill_name": "changelog"}', encoding="utf-8")
        (src / "files").mkdir()
        (src / "files" / "a.txt").write_text("data", encoding="utf-8")
        # 模拟历史运行产物：不应被复制
        (src / "results").mkdir()
        (src / "results" / "stale.json").write_text("{}", encoding="utf-8")
        return root

    def test_copy_shared_evals_copies(self):
        root = self._make_dataset()
        ops = copy_shared_evals(
            "positive/changelog",
            ["a/skill1", "b/skill2"],
            dataset_root=root,
        )
        self.assertEqual(len(ops), 2)
        for op in ops:
            self.assertTrue(op["copied"], op)
            self.assertTrue((Path(op["target"]) / "evals.json").exists())
            self.assertTrue((Path(op["target"]) / "files" / "a.txt").exists())
            # 运行产物 results/ 不应被复制
            self.assertFalse((Path(op["target"]) / "results").exists())

    def test_copy_shared_evals_dry_run_no_copy(self):
        root = self._make_dataset()
        ops = copy_shared_evals(
            "positive/changelog", ["a/skill1"], dataset_root=root, dry_run=True
        )
        self.assertEqual(len(ops), 1)
        self.assertFalse(ops[0]["copied"])
        self.assertFalse((Path(ops[0]["target"]) / "evals.json").exists())

    def test_copy_shared_evals_missing_source(self):
        root = self._make_dataset()
        ops = copy_shared_evals("positive/nope", ["a/skill1"], dataset_root=root)
        self.assertEqual(len(ops), 1)
        self.assertFalse(ops[0]["copied"])
        self.assertIn("error", ops[0])


class TestSecurityScanCommands(unittest.TestCase):
    def test_build_skillspector_scan_command(self):
        cmd = build_skillspector_scan_command("positive/calc-pro")
        self.assertIn("skillspector", cmd)
        self.assertIn("scan", cmd)
        self.assertIn("/scan/positive/calc-pro", cmd)
        self.assertIn("--format", cmd)
        self.assertIn("json", cmd)
        self.assertIn("--no-llm", cmd)
        self.assertIn("/app/reports/security/positive_calc-pro/skillspector.json", cmd)

    def test_build_tier1_scan_command(self):
        cmd = build_tier1_scan_command("positive/calc-pro")
        self.assertIn("skillevaluator", cmd)
        self.assertIn("tier1", cmd)
        self.assertIn("/skills/positive/calc-pro", cmd)
        self.assertIn("-r", cmd)
        self.assertIn("json", cmd)
        self.assertIn("--no-llm", cmd)
        self.assertIn("/app/reports/security/positive_calc-pro", cmd)

    def test_build_security_scan_commands(self):
        cmds = build_security_scan_commands(["a", "b"])
        self.assertEqual(len(cmds), 4)
        # 每个 skill 依次跑 skillspector → tier1
        self.assertIn("skillspector", cmds[0])
        self.assertIn("tier1", cmds[1])
        self.assertIn("skillspector", cmds[2])
        self.assertIn("tier1", cmds[3])

    def test_build_skillspector_scan_command_use_llm(self):
        cmd = build_skillspector_scan_command("positive/calc-pro", use_llm=True)
        self.assertIn("skillspector", cmd)
        self.assertNotIn("--no-llm", cmd)
        self.assertIn("/scan/positive/calc-pro", cmd)

    def test_build_tier1_scan_command_use_llm(self):
        cmd = build_tier1_scan_command("positive/calc-pro", use_llm=True)
        self.assertIn("tier1", cmd)
        self.assertNotIn("--no-llm", cmd)
        self.assertIn("/skills/positive/calc-pro", cmd)


class TestRunPipeline(unittest.TestCase):
    def test_run_pipeline_dry_run(self):
        result = run_pipeline("positive/json-format", "library-20261118/G9/git-commit-msg")
        self.assertFalse(result["executed"])
        # 阶段零安全预扫描（base+candidate 各 2 条）+ 阶段一 2 条 + 阶段二 2 条 = 8
        self.assertEqual(len(result["commands"]), 8)
        # 阶段零：skillspector(base) → tier1(base) → skillspector(cand) → tier1(cand)
        self.assertIn("skillspector", result["commands"][0])
        self.assertIn("tier1", result["commands"][1])
        self.assertIn("skillspector", result["commands"][2])
        self.assertIn("tier1", result["commands"][3])
        # 阶段一：建 catalog → 正向 query
        self.assertIn("--save-catalog", result["commands"][4])
        self.assertIn("--catalog", result["commands"][5])
        # 阶段二：tier3(base) → tier3(candidate)
        self.assertIn("tier3", result["commands"][6])
        self.assertIn("positive/json-format", " ".join(result["commands"][6]))
        self.assertIn("library-20261118/G9/git-commit-msg", " ".join(result["commands"][7]))
        # 无 eval_source 时无宿主操作
        self.assertEqual(result["host_ops"], [])

    def test_run_pipeline_without_security(self):
        result = run_pipeline("a", "b", include_security=False)
        self.assertEqual(len(result["commands"]), 4)
        self.assertIn("--save-catalog", result["commands"][0])

    def test_run_pipeline_executes(self):
        calls = []

        def fake_executor(cmd):
            calls.append(cmd)
            return 0

        result = run_pipeline("a", "b", run=True, executor=fake_executor)
        self.assertTrue(result["executed"])
        self.assertEqual(len(calls), 8)

    def test_run_pipeline_with_eval_source(self):
        fake_ops = [{"source": "s", "target": "t1", "copied": False},
                    {"source": "s", "target": "t2", "copied": False}]
        with mock.patch("skill_recommend.pipeline.copy_shared_evals", return_value=fake_ops) as cp:
            result = run_pipeline("base", "cand", eval_source="positive/changelog")
        # dry-run（默认 run=False）时 copy_shared_evals 以 dry_run=True 调用，不落地
        cp.assert_called_once_with("positive/changelog", ["base", "cand"], dry_run=True)
        self.assertEqual(result["host_ops"], fake_ops)


if __name__ == "__main__":
    unittest.main()
