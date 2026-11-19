from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).parents[1]
SKILL_PATH = SKILL_ROOT / "SKILL.md"
README_PATH = SKILL_ROOT / "README.md"
MANAGED_RULES_PATH = SKILL_ROOT / "assets" / "agents-rules.md"
METHODOLOGY_PATH = SKILL_ROOT / "references" / "methodology.md"
ANDROID_PATH = SKILL_ROOT / "references" / "android-kotlin.md"
ENVIRONMENT_PATH = SKILL_ROOT / "references" / "environment-layer.md"
ANALYSIS_PATH = SKILL_ROOT / "references" / "log-analysis.md"
FEATURE_SESSION_PATH = SKILL_ROOT / "references" / "feature-session-lifecycle.md"
BUSINESS_BOUNDARY_PATH = SKILL_ROOT / "references" / "business-boundary-discovery.md"
INSTRUMENTATION_SAFETY_PATH = SKILL_ROOT / "references" / "instrumentation-safety.md"

REQUIRED_MANAGED_RULES = (
    "high-frequency",
    "trace_id",
    "error_code",
    "request/response body",
    "business behavior",
)

REQUIRED_WORKFLOW_TERMS = (
    "Observability Plan",
    "Checkpoint Manifest",
    "new-development",
    "existing-feature",
    "Verification Report",
)


class DiagnosticLoggingSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.readme = README_PATH.read_text(encoding="utf-8")
        cls.managed_rules = MANAGED_RULES_PATH.read_text(encoding="utf-8")
        cls.methodology = METHODOLOGY_PATH.read_text(encoding="utf-8")
        cls.android = ANDROID_PATH.read_text(encoding="utf-8")
        cls.environment = ENVIRONMENT_PATH.read_text(encoding="utf-8")
        cls.analysis = ANALYSIS_PATH.read_text(encoding="utf-8")
        cls.feature_session = FEATURE_SESSION_PATH.read_text(encoding="utf-8")
        cls.business_boundary = BUSINESS_BOUNDARY_PATH.read_text(encoding="utf-8")
        cls.instrumentation_safety = INSTRUMENTATION_SAFETY_PATH.read_text(encoding="utf-8")

    def test_managed_rules_include_required_guardrails(self):
        for required_text in REQUIRED_MANAGED_RULES:
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

    def test_managed_rules_require_idempotent_environment_bootstrap(self):
        for required_text in (
            "Environment Layer Bootstrap",
            "runtime.process_started",
            "ENV-001",
            "complete",
            "partial",
            "absent",
            "duplicate",
            "once per process start",
            "local absolute paths",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

    def test_skill_contains_required_workflow_terms(self):
        for required_text in REQUIRED_WORKFLOW_TERMS:
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.skill)

    def test_skill_links_to_references_and_initializer(self):
        self.assertIn("references/methodology.md", self.skill)
        self.assertIn("references/environment-layer.md", self.skill)
        self.assertIn("references/android-kotlin.md", self.skill)
        self.assertIn("references/log-analysis.md", self.skill)
        self.assertIn("references/feature-session-lifecycle.md", self.skill)
        self.assertIn("references/business-boundary-discovery.md", self.skill)
        self.assertIn("references/instrumentation-safety.md", self.skill)
        self.assertIn("scripts/init_project.py", self.skill)
        self.assertIn("scripts/analyze_log.py", self.skill)

    def test_commands_route_all_supported_workflows(self):
        for command in ("help", "init", "env", "add", "review", "verify", "analyze"):
            with self.subTest(command=command):
                self.assertIn(f"`$diagnostic-logging {command}", self.skill)
        self.assertIn("--new", self.skill)
        self.assertIn("--existing", self.skill)

    def test_environment_bootstrap_applies_to_source_commands_only(self):
        self.assertIn("Environment Layer Bootstrap", self.skill)
        self.assertIn("`init`, `env`, `add`, `review`, and `verify`", self.skill)
        self.assertIn("`help` and `analyze`", self.skill)
        self.assertIn("read-only exceptions", self.skill)
        self.assertIn("complete", self.skill)
        self.assertIn("partial", self.skill)
        self.assertIn("absent", self.skill)
        self.assertIn("duplicate", self.skill)

    def test_analysis_contract_separates_evidence_from_inference(self):
        for required_text in (
            "Observed facts",
            "Inferences",
            "Unknowns",
            "confidence",
            "runtime.process_started",
            "trace_id",
            "Checkpoint Manifest",
            "must not modify source",
            "must not invent",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.analysis)

    def test_environment_bootstrap_reconciles_current_structure_not_saved_state(self):
        for required_text in (
            "desired-state reconciliation",
            "Never use a previous classification",
            "current source",
            "entry-point inventory",
            "coverage matrix",
            "classification is output",
            "drift",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.environment)

    def test_environment_contract_is_complete_and_safe(self):
        for required_text in (
            "runtime.process_started",
            "ENV-001",
            "once per process start",
            "app_name",
            "app_id",
            "process_name",
            "version_name",
            "version_code",
            "build_flavor",
            "build_type",
            "vcs_commit",
            "vcs_branch",
            "vcs_repository",
            "build time",
            "local absolute path",
            "credentials",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.environment)

    def test_android_environment_template_uses_build_and_process_apis(self):
        for required_text in (
            "buildFeatures",
            "buildConfigField",
            "BuildConfig.APPLICATION_ID",
            "BuildConfig.VERSION_NAME",
            "BuildConfig.VERSION_CODE",
            "BuildConfig.FLAVOR",
            "BuildConfig.BUILD_TYPE",
            "BuildConfig.VCS_COMMIT",
            "BuildConfig.VCS_BRANCH",
            "BuildConfig.VCS_REPOSITORY",
            "Application.getProcessName()",
            "AtomicBoolean",
            "runtime.process_started",
            "ENV-001",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.android)

    def test_android_bootstrap_rediscovers_process_topology(self):
        for required_text in (
            "merged manifest",
            "android:process",
            "Application.onCreate()",
            "new process",
            "process coverage matrix",
            "manual deletion",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.android)

    def test_android_reference_covers_required_android_topics(self):
        for required_text in (
            "CoroutineExceptionHandler",
            "CancellationException",
            "withContext",
            "lifecycle cancellation",
            "Retrofit/OkHttp",
            "database",
            "WorkManager",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.android)

    def test_android_cancellation_uses_owner_supplied_known_classification(self):
        self.assertNotIn("user_or_lifecycle", self.android)
        self.assertIn("enum class CancellationKind", self.android)
        self.assertIn("CancellationKind.USER", self.android)
        self.assertIn("CancellationKind.LIFECYCLE", self.android)

    def test_file_upload_failure_sequences_include_requests_and_terminal_results(self):
        self.assertIn(
            "`file_upload.started` → `file_upload.dependency_requested` → "
            "`file_upload.dependency_failed { error_code=dependency }` → "
            "`file_upload.retry_scheduled { retry_count }` → "
            "`file_upload.dependency_requested` → "
            "`file_upload.finished { result=success, duration_ms }`",
            self.methodology,
        )
        self.assertIn(
            "`file_upload.started` → `file_upload.dependency_requested` → "
            "`file_upload.dependency_failed { error_code=timeout }` → "
            "`file_upload.finished { result=failure, duration_ms }`",
            self.methodology,
        )

    def test_operation_closure_is_a_hard_completion_gate(self):
        for required_text in (
            "Exit-path Matrix",
            "every application-owned exit path",
            "exactly one terminal event",
            "`stage=exit`",
            "must not report the task as complete",
        ):
            with self.subTest(document="skill", required_text=required_text):
                self.assertIn(required_text, self.skill)

        for required_text in (
            "early return",
            "success callback",
            "error callback",
            "exception",
            "timeout",
            "user cancellation",
            "lifecycle cancellation",
            "retry exhaustion",
            "terminal once guard",
        ):
            with self.subTest(document="methodology", required_text=required_text):
                self.assertIn(required_text, self.methodology)

        for required_text in (
            "Exit-path Matrix",
            "exactly one terminal event",
            "same `trace_id`",
            "entry-only instrumentation",
        ):
            with self.subTest(document="managed rules", required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

    def test_cross_endpoint_feature_session_is_a_separate_completion_gate(self):
        for required_text in (
            "feature-session",
            "Feature-session Lifecycle Matrix",
            "feature_session_id",
            "inner operation",
            "peer-initiated exit",
        ):
            with self.subTest(document="skill", required_text=required_text):
                self.assertIn(required_text, self.skill)

        for required_text in (
            "local entry",
            "peer entry notification",
            "session active",
            "local exit",
            "peer exit notification",
            "peer-initiated exit",
            "disconnect",
            "lifecycle teardown",
            "terminal once guard",
            "must not close the outer feature session",
        ):
            with self.subTest(document="feature session", required_text=required_text):
                self.assertIn(required_text, self.feature_session)

        for required_text in (
            "Feature-session Lifecycle Matrix",
            "feature_session_id",
            "App-initiated",
            "peer-initiated",
            "inner operation",
        ):
            with self.subTest(document="managed rules", required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

    def test_business_capability_boundary_is_discovered_before_instrumentation(self):
        for required_text in (
            "Business Capability Contract",
            "End-to-End Journey Matrix",
            "outside-in",
            "upstream prerequisite",
            "downstream outcome",
            "must not edit feature code",
        ):
            with self.subTest(document="skill", required_text=required_text):
                self.assertIn(required_text, self.skill)

        for required_text in (
            "user-visible goal",
            "public entry",
            "automatic trigger",
            "prerequisite",
            "phase handoff",
            "success criterion",
            "terminal outcome",
            "excluded adjacent capability",
            "route",
            "analytics",
            "tests",
            "ask the user",
            "must not infer the boundary from a package, class, method, event prefix, or requested noun alone",
            "Every phase",
            "Every critical handoff",
        ):
            with self.subTest(document="business boundary", required_text=required_text):
                self.assertIn(required_text, self.business_boundary)

        for required_text in (
            "Business Capability Contract",
            "End-to-End Journey Matrix",
            "module name",
            "critical handoff",
            "discovery",
            "login communication",
        ):
            with self.subTest(document="managed rules", required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

        for required_text in (
            "近场发现",
            "登录通信",
            "业务能力契约",
            "端到端旅程矩阵",
        ):
            with self.subTest(document="readme", required_text=required_text):
                self.assertIn(required_text, self.readme)

    def test_android_terminal_templates_match_the_closure_contract(self):
        for required_text in (
            '"checkpoint" to "UPLOAD-EXIT"',
            '"module" to "photo_upload"',
            '"stage" to "exit"',
            '"result" to "success"',
            '"result" to "failure"',
            '"result" to "cancelled"',
            "AtomicBoolean",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, self.android)

    def test_instrumentation_safety_is_a_hard_completion_gate(self):
        for required_text in (
            "Instrumentation Safety Contract",
            "Behavior Preservation Matrix",
            "logger enabled, disabled, and failing",
            "fault-injection logger",
            "must not report the task as complete",
        ):
            with self.subTest(document="skill", required_text=required_text):
                self.assertIn(required_text, self.skill)

        for required_text in (
            "return value",
            "state mutation",
            "call ordering",
            "exception type",
            "cancellation propagation",
            "field supplier",
            "logger failure",
            "business `try`/`runCatching`",
            "logger return value",
            "new thread, coroutine, timer, network, file, database, or IPC work",
            "arbitrary `toString()`",
            "reflection",
            "collection traversal",
            "O(1)",
            "bounded",
            "fault injection",
        ):
            with self.subTest(document="safety", required_text=required_text):
                self.assertIn(required_text, self.instrumentation_safety)

        for required_text in (
            "Instrumentation Safety Contract",
            "Behavior Preservation Matrix",
            "logging failure",
            "field construction",
            "control flow",
            "performance",
        ):
            with self.subTest(document="managed rules", required_text=required_text):
                self.assertIn(required_text, self.managed_rules)

        for required_text in (
            "safeEvent",
            "logger failure must not escape",
            "fields()",
            "isEnabled",
        ):
            with self.subTest(document="android", required_text=required_text):
                self.assertIn(required_text, self.android)

        for required_text in (
            "插桩安全门禁",
            "故障注入",
            "业务行为",
            "性能风险",
        ):
            with self.subTest(document="readme", required_text=required_text):
                self.assertIn(required_text, self.readme)

    def test_methodology_schema_covers_approved_context_fields_and_applicability(self):
        required_row = (
            "| Required on every event | `event`, `checkpoint`, `module`, `stage`, `result`; "
            "timestamp and level supplied by the project logger |"
        )
        self.assertIn(required_row, self.methodology)
        self.assertIn("Build identity is required", self.methodology)
        self.assertIn("Execution context is required", self.methodology)
        self.assertIn("when the logger does not already attach it", self.methodology)

    def test_managed_rules_stay_compact(self):
        self.assertLess(len(self.managed_rules.splitlines()), 100)

    def test_skill_frontmatter_has_only_name_and_description(self):
        lines = self.skill.splitlines()
        self.assertGreaterEqual(len(lines), 4)
        self.assertEqual("---", lines[0])
        closing_index = lines.index("---", 1)
        frontmatter = lines[1:closing_index]
        keys = [line.split(":", 1)[0] for line in frontmatter if line.strip()]
        self.assertEqual(["name", "description"], keys)
        self.assertEqual("name: diagnostic-logging", frontmatter[0])


if __name__ == "__main__":
    unittest.main()
