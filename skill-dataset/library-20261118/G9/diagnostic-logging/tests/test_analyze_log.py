import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "analyze_log.py"
SPEC = importlib.util.spec_from_file_location("diagnostic_logging_analyze_log", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeLogTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def write_log(self, contents: str, name: str = "app.log") -> Path:
        path = self.root / name
        path.write_text(contents, encoding="utf-8")
        return path

    def test_reconstructs_environment_session_and_trace_from_json_lines(self):
        path = self.write_log(
            "\n".join(
                (
                    json.dumps(
                        {
                            "timestamp": "2026-08-14T10:00:00Z",
                            "event": "runtime.process_started",
                            "checkpoint": "ENV-001",
                            "module": "runtime",
                            "stage": "process_start",
                            "result": "started",
                            "app_name": "Demo",
                            "app_id": "com.example.demo",
                            "process_name": "com.example.demo",
                            "version_name": "1.2.3",
                            "version_code": "123",
                            "build_flavor": "prod",
                            "build_type": "release",
                            "vcs_commit": "0123456789ab",
                            "vcs_branch": "main",
                            "vcs_repository": "example.com/team/demo",
                            "pid": 42,
                        }
                    ),
                    json.dumps(
                        {
                            "timestamp": "2026-08-14T10:00:01Z",
                            "event": "file_upload.started",
                            "checkpoint": "UP-001",
                            "module": "upload",
                            "stage": "entry",
                            "result": "started",
                            "trace_id": "trace-1",
                            "pid": 42,
                        }
                    ),
                    json.dumps(
                        {
                            "timestamp": "2026-08-14T10:00:02Z",
                            "event": "file_upload.finished",
                            "checkpoint": "UP-004",
                            "module": "upload",
                            "stage": "exit",
                            "result": "failure",
                            "error_code": "timeout",
                            "trace_id": "trace-1",
                            "pid": 42,
                        }
                    ),
                )
            )
        )

        bundle = MODULE.analyze_path(path)

        self.assertEqual(1, bundle["summary"]["environment_sessions"])
        self.assertEqual(1, bundle["summary"]["traces"])
        self.assertEqual("com.example.demo", bundle["traces"][0]["process_name"])
        self.assertEqual("failure", bundle["traces"][0]["terminal_result"])
        self.assertTrue(any(item["code"] == "operation_failure" for item in bundle["findings"]))

    def test_extracts_embedded_and_nested_structured_event(self):
        path = self.write_log(
            '08-14 10:00:00.123  42  43 I Demo: '
            '{"event":"sync.finished","fields":{"checkpoint":"S-2",'
            '"module":"sync","stage":"exit","result":"success","trace_id":"t-2"}}\n'
        )

        bundle = MODULE.analyze_path(path)

        event = bundle["uncorrelated_events"][0]
        self.assertEqual("sync.finished", event["event"])
        self.assertEqual("S-2", event["checkpoint"])
        self.assertEqual("08-14 10:00:00.123", event["timestamp"])
        self.assertEqual("42", event["pid"])

    def test_reports_missing_environment_and_schema_without_copying_raw_content(self):
        secret = "user@example.com token=do-not-copy"
        path = self.write_log(
            secret
            + "\n"
            + '{"event":"login.finished","result":"failure","trace_id":"t-3",'
            + '"error_code":"dependency","payload":"private body"}\n'
        )

        bundle = MODULE.analyze_path(path)
        serialized = json.dumps(bundle)

        self.assertTrue(any(item["code"] == "environment_missing" for item in bundle["findings"]))
        self.assertTrue(any(item["code"] == "schema_incomplete" for item in bundle["findings"]))
        self.assertNotIn(secret, serialized)
        self.assertNotIn("private body", serialized)

    def test_feature_filter_keeps_environment_and_matching_events(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"runtime.process_started","checkpoint":"ENV-001","module":"runtime",'
                    '"stage":"process_start","result":"started","app_name":"A","app_id":"a",'
                    '"process_name":"a","version_name":"1","version_code":"1","build_flavor":"default",'
                    '"build_type":"debug","vcs_commit":"0123456789ab","vcs_branch":"main",'
                    '"vcs_repository":"example.com/a/a"}',
                    '{"event":"upload.started","checkpoint":"U1","module":"upload","stage":"entry",'
                    '"result":"started","trace_id":"u"}',
                    '{"event":"login.started","checkpoint":"L1","module":"login","stage":"entry",'
                    '"result":"started","trace_id":"l"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path, feature="upload")

        self.assertEqual(2, bundle["summary"]["structured_events"])
        self.assertEqual(["u"], [trace["trace_id"] for trace in bundle["traces"]])

    def test_intermediate_success_does_not_close_a_started_trace(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"photo_upload.started","checkpoint":"U1","module":"upload",'
                    '"stage":"entry","result":"started","trace_id":"upload-1"}',
                    '{"event":"photo_upload.image_finished","checkpoint":"U2","module":"upload",'
                    '"stage":"item","result":"success","trace_id":"upload-1"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path, feature="photo_upload")
        trace = bundle["traces"][0]

        self.assertEqual("unknown", trace["terminal_result"])
        self.assertEqual(0, trace["terminal_event_count"])
        self.assertTrue(
            any(item["code"] == "trace_without_terminal_event" for item in bundle["findings"])
        )

    def test_finished_event_without_exit_stage_does_not_close_trace(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"photo_upload.started","checkpoint":"U1","module":"upload",'
                    '"stage":"entry","result":"started","trace_id":"upload-2"}',
                    '{"event":"photo_upload.finished","checkpoint":"U5","module":"upload",'
                    '"stage":"upload","result":"success","trace_id":"upload-2"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path, feature="photo_upload")
        trace = bundle["traces"][0]

        self.assertEqual(0, trace["terminal_event_count"])
        self.assertTrue(
            any(item["code"] == "trace_without_terminal_event" for item in bundle["findings"])
        )

    def test_reports_multiple_terminal_events_for_one_started_trace(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"sync.started","checkpoint":"S1","module":"sync",'
                    '"stage":"entry","result":"started","trace_id":"sync-1"}',
                    '{"event":"sync.finished","checkpoint":"S2","module":"sync",'
                    '"stage":"exit","result":"success","trace_id":"sync-1"}',
                    '{"event":"sync.cancelled","checkpoint":"S3","module":"sync",'
                    '"stage":"exit","result":"cancelled","trace_id":"sync-1"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path, feature="sync")
        trace = bundle["traces"][0]

        self.assertEqual(2, trace["terminal_event_count"])
        self.assertTrue(
            any(item["code"] == "trace_multiple_terminal_events" for item in bundle["findings"])
        )

    def test_inner_operation_terminal_does_not_close_outer_feature_session(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"image_live.session_started","checkpoint":"LIVE-001",'
                    '"module":"image_live","scope":"feature_session","stage":"entry",'
                    '"result":"started","feature_session_id":"session-1"}',
                    '{"event":"photo_upload.started","checkpoint":"UPLOAD-001",'
                    '"module":"photo_upload","scope":"operation","stage":"entry",'
                    '"result":"started","feature_session_id":"session-1","trace_id":"upload-1"}',
                    '{"event":"photo_upload.finished","checkpoint":"UPLOAD-EXIT",'
                    '"module":"photo_upload","scope":"operation","stage":"exit",'
                    '"result":"success","feature_session_id":"session-1","trace_id":"upload-1"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path)

        self.assertEqual(1, bundle["summary"]["feature_sessions"])
        self.assertEqual(0, bundle["feature_sessions"][0]["terminal_event_count"])
        self.assertEqual(1, bundle["traces"][0]["terminal_event_count"])
        self.assertTrue(
            any(item["code"] == "feature_session_without_terminal_event" for item in bundle["findings"])
        )

    def test_feature_session_accepts_app_or_peer_initiated_exit(self):
        for initiator in ("app", "peer"):
            with self.subTest(initiator=initiator):
                path = self.write_log(
                    "\n".join(
                        (
                            '{"event":"image_live.session_started","checkpoint":"LIVE-001",'
                            '"module":"image_live","scope":"feature_session","stage":"entry",'
                            f'"result":"started","feature_session_id":"session-{initiator}"}}',
                            '{"event":"image_live.session_finished","checkpoint":"LIVE-EXIT",'
                            '"module":"image_live","scope":"feature_session","stage":"exit",'
                            f'"result":"success","initiator":"{initiator}",'
                            f'"feature_session_id":"session-{initiator}"}}',
                        )
                    ),
                    name=f"{initiator}.log",
                )

                bundle = MODULE.analyze_path(path)
                session = bundle["feature_sessions"][0]

                self.assertEqual("success", session["terminal_result"])
                self.assertEqual(1, session["terminal_event_count"])
                self.assertFalse(
                    any(
                        item["code"] == "feature_session_without_terminal_event"
                        for item in bundle["findings"]
                    )
                )

    def test_reports_competing_feature_session_terminals(self):
        path = self.write_log(
            "\n".join(
                (
                    '{"event":"image_live.session_started","checkpoint":"LIVE-001",'
                    '"module":"image_live","scope":"feature_session","stage":"entry",'
                    '"result":"started","feature_session_id":"session-race"}',
                    '{"event":"image_live.session_finished","checkpoint":"LIVE-EXIT",'
                    '"module":"image_live","scope":"feature_session","stage":"exit",'
                    '"result":"success","initiator":"app","feature_session_id":"session-race"}',
                    '{"event":"image_live.session_finished","checkpoint":"LIVE-EXIT",'
                    '"module":"image_live","scope":"feature_session","stage":"exit",'
                    '"result":"success","initiator":"peer","feature_session_id":"session-race"}',
                )
            )
        )

        bundle = MODULE.analyze_path(path)

        self.assertEqual(2, bundle["feature_sessions"][0]["terminal_event_count"])
        self.assertTrue(
            any(
                item["code"] == "feature_session_multiple_terminal_events"
                for item in bundle["findings"]
            )
        )

    def test_reports_started_operation_without_trace_id(self):
        path = self.write_log(
            '{"event":"sync.started","checkpoint":"S1","module":"sync",'
            '"scope":"operation","stage":"entry","result":"started"}\n'
        )

        bundle = MODULE.analyze_path(path)

        self.assertTrue(
            any(item["code"] == "started_event_without_trace_id" for item in bundle["findings"])
        )

    def test_dependency_started_name_does_not_open_an_operation(self):
        path = self.write_log(
            '{"event":"sync.dependency.started","checkpoint":"S2","module":"sync",'
            '"scope":"dependency","stage":"dependency","result":"started","trace_id":"sync-2"}\n'
        )

        bundle = MODULE.analyze_path(path)

        self.assertFalse(
            any(item["code"] == "trace_without_terminal_event" for item in bundle["findings"])
        )

    def test_reports_invalid_started_event_contract(self):
        path = self.write_log(
            '{"event":"sync.started","checkpoint":"S1","module":"sync",'
            '"scope":"operation","stage":"work","result":"started","trace_id":"sync-3"}\n'
        )

        bundle = MODULE.analyze_path(path)

        self.assertTrue(
            any(item["code"] == "started_event_contract_violation" for item in bundle["findings"])
        )
        self.assertFalse(
            any(item["code"] == "trace_without_terminal_event" for item in bundle["findings"])
        )

    def test_merges_cross_process_trace_only_with_compatible_build_identity(self):
        environment_template = (
            '{{"event":"runtime.process_started","checkpoint":"ENV-001","module":"runtime",'
            '"stage":"process_start","result":"started","app_name":"Demo","app_id":"demo",'
            '"process_name":"{process}","version_name":"1","version_code":"1",'
            '"build_flavor":"prod","build_type":"release","vcs_commit":"abcdef123456",'
            '"vcs_branch":"main","vcs_repository":"example.com/demo","pid":{pid}}}'
        )
        self.write_log(
            "\n".join(
                (
                    environment_template.format(process="demo", pid=1),
                    '{"event":"sync.started","checkpoint":"S1","module":"sync",'
                    '"scope":"operation","stage":"entry","result":"started","trace_id":"cross-1",'
                    '"pid":1}',
                )
            ),
            name="a.log",
        )
        self.write_log(
            "\n".join(
                (
                    environment_template.format(process="demo:worker", pid=2),
                    '{"event":"sync.finished","checkpoint":"S2","module":"sync",'
                    '"scope":"operation","stage":"exit","result":"success","trace_id":"cross-1",'
                    '"pid":2}',
                )
            ),
            name="b.log",
        )

        bundle = MODULE.analyze_path(self.root)

        self.assertEqual(1, bundle["summary"]["traces"])
        self.assertEqual(2, len(bundle["traces"][0]["environment_session_ids"]))
        self.assertEqual(1, bundle["traces"][0]["terminal_event_count"])
        self.assertFalse(
            any(item["code"] == "trace_without_terminal_event" for item in bundle["findings"])
        )

    def test_cli_writes_json_and_rejects_missing_path(self):
        path = self.write_log(
            '{"event":"x","checkpoint":"C","module":"m","stage":"s","result":"success"}\n'
        )
        output = self.root / "evidence.json"

        success = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(path), "--output", str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
        failure = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(self.root / "missing.log")],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, success.returncode)
        self.assertEqual(str(output.resolve()), json.loads(success.stdout)["output"])
        self.assertIn("summary", json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual(2, failure.returncode)
        self.assertTrue(failure.stderr.strip())


if __name__ == "__main__":
    unittest.main()
