import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "init_project.py"
SPEC = importlib.util.spec_from_file_location("diagnostic_logging_init_project", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class InitProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.skill_root = self.root / "skill"
        self.rules_path = self.skill_root / "assets" / "agents-rules.md"
        self.rules_path.parent.mkdir(parents=True)
        self.rules = "Rule one.\nRule two."
        self.rules_path.write_text(self.rules, encoding="utf-8")

    def initialize(self):
        return MODULE.initialize_project(str(self.project), self.skill_root)

    def test_creates_missing_agents_file_with_one_managed_block_and_rules(self):
        result = self.initialize()
        text = (self.project / "AGENTS.md").read_text(encoding="utf-8")

        self.assertEqual("created", result.status)
        self.assertEqual(1, text.count(MODULE.MANAGED_START))
        self.assertEqual(1, text.count(MODULE.MANAGED_END))
        self.assertIn(self.rules, text)

    def test_identical_second_run_is_unchanged_and_preserves_bytes(self):
        self.initialize()
        target = self.project / "AGENTS.md"
        original = target.read_bytes()

        result = self.initialize()

        self.assertEqual("unchanged", result.status)
        self.assertEqual(original, target.read_bytes())

    def test_existing_file_preserves_prefix_and_suffix_while_replacing_block(self):
        target = self.project / "AGENTS.md"
        old_block = MODULE.MANAGED_START + "\nold rules\n" + MODULE.MANAGED_END + "\n"
        target.write_text("prefix\n" + old_block + "suffix\n", encoding="utf-8")

        result = self.initialize()
        text = target.read_text(encoding="utf-8")

        self.assertEqual("updated", result.status)
        self.assertTrue(text.startswith("prefix\n"))
        self.assertTrue(text.endswith("\nsuffix\n"))
        self.assertNotIn("old rules", text)
        self.assertIn(self.rules, text)

    def test_singular_agent_file_is_preserved_and_warned_about(self):
        singular = self.project / "AGENT.md"
        singular.write_text("keep singular", encoding="utf-8")

        result = self.initialize()

        self.assertEqual("keep singular", singular.read_text(encoding="utf-8"))
        self.assertTrue((self.project / "AGENTS.md").is_file())
        self.assertTrue(any("AGENT.md" in warning for warning in result.warnings))

    def test_existing_singular_agent_file_is_warned_about_when_plural_also_exists(self):
        singular = self.project / "AGENT.md"
        plural = self.project / "AGENTS.md"
        singular.write_text("keep singular", encoding="utf-8")
        plural.write_text("existing plural", encoding="utf-8")

        result = self.initialize()

        self.assertEqual("keep singular", singular.read_text(encoding="utf-8"))
        self.assertTrue(any("AGENT.md" in warning for warning in result.warnings))
        self.assertFalse(any("created standard plural" in warning for warning in result.warnings))

    def test_invalid_marker_arrangements_raise_without_changing_bytes(self):
        cases = (
            MODULE.MANAGED_START + "\n",
            MODULE.MANAGED_START + "\n" + MODULE.MANAGED_START + "\n" + MODULE.MANAGED_END,
            MODULE.MANAGED_END + "\n" + MODULE.MANAGED_START,
        )
        target = self.project / "AGENTS.md"
        for contents in cases:
            with self.subTest(contents=contents):
                target.write_text(contents, encoding="utf-8")
                original = target.read_bytes()
                with self.assertRaises(MODULE.InitializationError):
                    self.initialize()
                self.assertEqual(original, target.read_bytes())

    def test_unsafe_project_roots_are_rejected(self):
        missing = self.root / "missing"
        symlink = self.root / "symlink"
        symlink.symlink_to(self.project, target_is_directory=True)
        unsafe_roots = (missing, symlink, Path(self.project.anchor), Path.home())

        for unsafe_root in unsafe_roots:
            with self.subTest(root=unsafe_root):
                with self.assertRaises(MODULE.InitializationError):
                    MODULE.validate_project_root(str(unsafe_root))

    def test_empty_existing_agents_file_is_initialized(self):
        target = self.project / "AGENTS.md"
        target.touch()

        result = self.initialize()

        self.assertEqual("updated", result.status)
        self.assertIn(self.rules, target.read_text(encoding="utf-8"))

    def test_missing_or_blank_rules_fail_without_touching_agents_file(self):
        target = self.project / "AGENTS.md"
        target.write_text("original", encoding="utf-8")
        original = target.read_bytes()

        self.rules_path.unlink()
        with self.assertRaises(MODULE.InitializationError):
            self.initialize()
        self.assertEqual(original, target.read_bytes())

        self.rules_path.write_text(" \n\t", encoding="utf-8")
        with self.assertRaises(MODULE.InitializationError):
            self.initialize()
        self.assertEqual(original, target.read_bytes())

    def test_cli_emits_json_on_success_and_stderr_on_validation_failure(self):
        command = [sys.executable, str(SCRIPT_PATH), "--project-root", str(self.project)]
        success = subprocess.run(command, capture_output=True, text=True, check=False)

        self.assertEqual(0, success.returncode)
        payload = json.loads(success.stdout)
        self.assertEqual("created", payload["status"])
        self.assertEqual(str((self.project / "AGENTS.md").resolve()), payload["target"])

        failure = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--project-root", str(self.root / "nope")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, failure.returncode)
        self.assertEqual("", failure.stdout)
        self.assertTrue(failure.stderr.strip())

    def test_main_returns_json_or_stderr_for_in_process_callers(self):
        output = io.StringIO()
        errors = io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            success_code = MODULE.main(["--project-root", str(self.project)])
            failure_code = MODULE.main(["--project-root", str(self.root / "missing")])

        self.assertEqual(0, success_code)
        self.assertEqual("created", json.loads(output.getvalue())["status"])
        self.assertEqual(2, failure_code)
        self.assertTrue(errors.getvalue().strip())

    def test_existing_file_mode_is_preserved(self):
        target = self.project / "AGENTS.md"
        target.write_text("existing", encoding="utf-8")
        os.chmod(target, 0o640)

        self.initialize()

        self.assertEqual(0o640, stat.S_IMODE(target.stat().st_mode))

    def test_atomic_replace_failure_preserves_original_file_and_removes_temporary_artifact(self):
        target = self.project / "AGENTS.md"
        original_bytes = b"existing content\n"
        target.write_bytes(original_bytes)
        os.chmod(target, 0o640)
        original_mode = stat.S_IMODE(target.stat().st_mode)

        with patch.object(MODULE.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaisesRegex(MODULE.InitializationError, "could not write"):
                self.initialize()

        self.assertEqual(original_bytes, target.read_bytes())
        self.assertEqual(original_mode, stat.S_IMODE(target.stat().st_mode))
        self.assertEqual([], list(self.project.glob(".diagnostic-logging-*")))

    def test_render_managed_block_has_exact_format(self):
        self.assertEqual(
            MODULE.MANAGED_START + "\ntrimmed\n" + MODULE.MANAGED_END + "\n",
            MODULE.render_managed_block("\n trimmed \n"),
        )


if __name__ == "__main__":
    unittest.main()
