# Android and Kotlin diagnostic logging

Use the application's existing logger and its release policy. The examples are adapters for that abstraction, not a new logging dependency. Their fields are allowlisted and contain no request/response body, headers, credentials, tokens, personal content, or device identifier.

## Table of contents

1. [Android environment bootstrap](#android-environment-bootstrap)
2. [Build-time identity template](#build-time-identity-template)
3. [Once-per-process event template](#once-per-process-event-template)
4. [Typed, lazy event fields](#typed-lazy-event-fields)
5. [Immutable coroutine context and preserved dispatching](#immutable-coroutine-context-and-preserved-dispatching)
6. [Cancellation and responsibility boundaries](#cancellation-and-responsibility-boundaries)
7. [Retrofit/OkHttp and database checkpoints](#retrofitokhttp-and-database-checkpoints)
8. [WorkManager outcomes](#workmanager-outcomes)
9. [Hot paths, visibility, and limits](#hot-paths-visibility-and-limits)

## Android environment bootstrap

Before any mode-specific work, rebuild Android's process topology and inspect the application module and every process-start integration for `runtime.process_started` / `ENV-001`. Classify the implementation using the generic [environment-layer contract](environment-layer.md): reuse `complete`, upgrade `partial`, add `absent`, and consolidate `duplicate` implementations.

For every shipped variant, inspect the current **merged manifest** when build output is available; it is authoritative because source-set overlays, manifest placeholders, libraries, and manifest-merger rules can add, rename, or remove components. If it is unavailable, inspect every contributing source manifest and mark the merged result unverified. Enumerate the default application process plus every component with `android:process`; also record isolated processes and alternate application/startup initializers because their logger availability can differ.

Create an Android **process coverage matrix**:

```text
variant | applicationId | process | declaring component | isolated? | earliest logger-ready hook | reaches reporter? | runtime test
```

Prefer a central process-wide call after logger initialization. `Application.onCreate()` normally runs in each application process, so one wiring point can automatically cover a new process; prove that the same `Application` and logger initialization run in that process. Content providers and generated startup initializers may execute earlier, while an isolated process may not support the normal logger. If either can produce diagnostics before the application hook, move or additionally call the same once-guarded reporter at the earliest safe logger-ready owner—do not create a second reporter.

Do not infer coverage from a previous report or from finding the event string. Trace the current call path. A manual deletion of the startup call must classify the layer as `partial` or `absent`; an added or modified `android:process` must create or update a matrix row and be verified before `complete` is allowed.

The Android mapping is:

| Contract field | Android source |
| --- | --- |
| `app_name` | Packaged label from `ApplicationInfo.loadLabel`; do not duplicate a resource string in logging code |
| `app_id` | `BuildConfig.APPLICATION_ID` from the executable application module |
| `process_name` | `Application.getProcessName()` on API 28+, with a PID/`ActivityManager` compatibility fallback |
| `version_name` | `BuildConfig.VERSION_NAME` |
| `version_code` | `BuildConfig.VERSION_CODE.toString()` to retain the cross-platform string type |
| `build_flavor` | `BuildConfig.FLAVOR`, normalized to `default` when empty |
| `build_type` | `BuildConfig.BUILD_TYPE` |
| Repository fields | Generated `BuildConfig.VCS_COMMIT`, `BuildConfig.VCS_BRANCH`, and `BuildConfig.VCS_REPOSITORY` |

Use the application module's generated `BuildConfig`, not a library module's class with the same simple name. If the central reporter lives in a library, pass an immutable environment value object from the application module or expose it through the project's existing dependency boundary.

## Build-time identity template

Enable generated build config explicitly when the Android Gradle Plugin version requires it. Capture release properties first, then CI metadata, then a lazy Git query. This illustrative Kotlin DSL uses the Android Components API so the values remain `Provider`-backed build inputs instead of source constants:

```kotlin
import com.android.build.api.variant.BuildConfigField
import org.gradle.api.provider.Provider
import org.gradle.api.provider.ProviderFactory
import java.io.Serializable
import java.net.URI

android {
    buildFeatures {
        buildConfig = true
    }
}

fun ProviderFactory.gitText(vararg arguments: String): Provider<String> =
    exec {
        commandLine("git", *arguments)
        workingDir(rootProject.projectDir)
        isIgnoreExitValue = true
    }.standardOutput.asText.map { it.trim().ifBlank { "unknown" } }

fun buildConfigString(value: String): String =
    "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

fun sanitizeRepository(raw: String): String {
    val value = raw.trim()
    if (value.isBlank() || value.startsWith("/") || value.startsWith("file:") ||
        "\\" in value || Regex("^[A-Za-z]:[\\\\/]").containsMatchIn(value)
    ) return "unknown"

    val normalized = runCatching {
        when {
            Regex("^[^/@]+@[^:]+:.+").matches(value) -> {
                val match = Regex("^[^/@]+@([^:]+):(.+)$").matchEntire(value)!!
                "${match.groupValues[1]}/${match.groupValues[2]}"
            }
            "://" in value -> {
                val uri = URI(value)
                require(!uri.host.isNullOrBlank())
                require(uri.userInfo == null || uri.scheme.equals("ssh", ignoreCase = true))
                "${uri.host}/${uri.path.trimStart('/')}"
            }
            else -> value
        }
    }.getOrDefault("unknown")

    val result = normalized
        .substringBefore('?')
        .substringBefore('#')
        .removeSuffix(".git")
    val segments = result.split('/')
    return result.takeIf {
        it != "unknown" && "@" !in it && "://" !in it && !it.startsWith("/") &&
            segments.size >= 3 && segments.none { segment -> segment.isBlank() || segment == "." || segment == ".." } &&
            Regex("^[A-Za-z0-9.-]+/[A-Za-z0-9._/-]+$").matches(it)
    } ?: "unknown"
}

fun sanitizeCommit(raw: String): String = raw.trim().lowercase()
    .takeIf { Regex("^[0-9a-f]{12,64}$").matches(it) }
    ?: "unknown"

// Replace these examples with the repository's approved production branch patterns.
val approvedBranchPatterns = listOf(
    Regex("^(main|master|develop)$"),
    Regex("^(release|hotfix)/[A-Za-z0-9._-]+$"),
)

fun sanitizeBranch(raw: String): String {
    val branch = raw.trim()
    if (branch.isBlank()) return "detached"
    return branch.takeIf { candidate -> approvedBranchPatterns.any { it.matches(candidate) } }
        ?: "redacted"
}

val vcsCommit = providers.environmentVariable("RELEASE_VCS_COMMIT")
    .orElse(providers.environmentVariable("GITHUB_SHA"))
    .orElse(providers.environmentVariable("CI_COMMIT_SHA"))
    .orElse(providers.gitText("rev-parse", "HEAD"))
    .map(::sanitizeCommit)

val vcsBranch = providers.environmentVariable("RELEASE_VCS_BRANCH")
    .orElse(providers.environmentVariable("GITHUB_REF_NAME"))
    .orElse(providers.environmentVariable("CI_COMMIT_REF_NAME"))
    .orElse(providers.gitText("branch", "--show-current"))
    .map(::sanitizeBranch)

val githubRepository = providers.environmentVariable("GITHUB_REPOSITORY")
    .map { "github.com/$it" }
val gitlabRepository = providers.environmentVariable("CI_SERVER_HOST")
    .zip(providers.environmentVariable("CI_PROJECT_PATH")) { host, path -> "$host/$path" }

val vcsRepository = providers.environmentVariable("RELEASE_VCS_REPOSITORY")
    .orElse(githubRepository)
    .orElse(gitlabRepository)
    .orElse(providers.gitText("config", "--get", "remote.origin.url"))
    .map(::sanitizeRepository)

androidComponents.onVariants { variant ->
    fun putString(name: String, value: Provider<String>) {
        variant.buildConfigFields.put(
            name,
            value.map { BuildConfigField<Serializable>(buildConfigString(it), "Generated diagnostic identity") },
        )
    }
    putString("VCS_COMMIT", vcsCommit)
    putString("VCS_BRANCH", vcsBranch)
    putString("VCS_REPOSITORY", vcsRepository)
}
```

Adapt CI names to the project's release system. Common inputs include `GITHUB_SHA`, `GITHUB_REF_NAME`, `GITHUB_REPOSITORY`, `CI_COMMIT_SHA`, `CI_COMMIT_REF_NAME`, and `CI_PROJECT_PATH`; when the CI exposes a server host, combine it with the project path before sanitization. Register the final values as build inputs according to the project's caching and reproducibility policy.

The repository value is an identifier such as `host/org/repo`, never a local Git checkout path. Reject absolute paths and remove credentials, query strings, fragments, and `.git`. Apply the project's production allowlist/redaction policy to branch names because they may contain personal or ticket information. The example sanitizer is a starting point; add tests for every remote form used by the project.

## Once-per-process event template

Call one central reporter from the existing `Application.onCreate()` path after the production logger is ready when the current process coverage matrix proves that hook is valid for every process. Android starts an `Application` instance in each declared app process, and the static `AtomicBoolean` is process-local, so the same code emits once for the main process and once for each child process. Do not add a new startup framework or call the reporter from activities, services, workers, or features.

```kotlin
import android.app.ActivityManager
import android.app.Application
import android.content.Context
import android.os.Build
import android.os.Process
import java.util.concurrent.atomic.AtomicBoolean

object AndroidEnvironmentReporter {
    private val emitted = AtomicBoolean(false)

    fun emitOnce(application: Application, logger: DiagnosticLogger) {
        val enabled = try {
            logger.isEnabled(LogLevel.INFO)
        } catch (_: Exception) {
            false
        }
        if (!enabled || !emitted.compareAndSet(false, true)) return

        try {
            logger.emit(
                level = LogLevel.INFO,
                event = "runtime.process_started",
                fields = mapOf(
                    "checkpoint" to "ENV-001",
                    "module" to "runtime",
                    "stage" to "process_start",
                    "result" to "started",
                    "app_name" to application.applicationInfo
                        .loadLabel(application.packageManager).toString(),
                    "app_id" to BuildConfig.APPLICATION_ID,
                    "process_name" to currentProcessName(application),
                    "version_name" to BuildConfig.VERSION_NAME,
                    "version_code" to BuildConfig.VERSION_CODE.toString(),
                    "build_flavor" to BuildConfig.FLAVOR.ifBlank { "default" },
                    "build_type" to BuildConfig.BUILD_TYPE,
                    "vcs_commit" to BuildConfig.VCS_COMMIT,
                    "vcs_branch" to BuildConfig.VCS_BRANCH,
                    "vcs_repository" to BuildConfig.VCS_REPOSITORY,
                ),
            )
        } catch (_: Exception) {
            // Diagnostic logging must not crash startup; allow one later retry.
            emitted.set(false)
        }
    }

    private fun currentProcessName(context: Context): String {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return Application.getProcessName()
        }
        val pid = Process.myPid()
        val manager = context.getSystemService(Context.ACTIVITY_SERVICE) as? ActivityManager
        return manager?.runningAppProcesses
            ?.firstOrNull { it.pid == pid }
            ?.processName
            ?: "unknown"
    }
}
```

The selected level must be enabled and collected in production. If the existing logger can reject the event, define and test whether the once guard is consumed on attempted or successful emission; do not silently lose the only environment event. A project logger that automatically adds timestamp, PID, or level may retain those fields, but must not duplicate the contract fields.

Add a reporter contract test and a startup-wiring test using the project's existing test stack. Add a check that derives declared processes from the current merged manifest or equivalent packaged metadata and rejects uncovered rows; do not store yesterday's process list as the only expected value. This makes manual deletion of the call visible and forces a new process to enter verification.

Verify a main-process cold start, every configured child-process cold start, repeated reporter calls, and a real process restart. Confirm that later feature events contain no application/version/VCS fields and can be paired with the nearest preceding event for the same process lifetime.

## Typed, lazy event fields

Build fields inside the logger’s enabled branch so disabled logs avoid expensive argument construction. The map is immutable after construction.

```kotlin
enum class LogLevel { DEBUG, INFO, WARN, ERROR }

interface DiagnosticLogger {
    fun isEnabled(level: LogLevel): Boolean
    fun emit(level: LogLevel, event: String, fields: Map<String, Any?>, error: Throwable? = null)
}

inline fun DiagnosticLogger.safeEvent(
    level: LogLevel,
    name: String,
    error: Throwable? = null,
    fields: () -> Map<String, Any?>,
) {
    val enabled = try {
        isEnabled(level)
    } catch (_: Exception) {
        return
    }
    if (!enabled) return

    val safeFields = try {
        fields()
    } catch (_: Exception) {
        return
    }

    try {
        emit(level, name, safeFields, error)
    } catch (_: Exception) {
        // logger failure must not escape into or reclassify business behavior.
    }
}
```

Use one project-approved central adapter with this non-throwing contract. Do not add a fallback log inside the catch, and do not catch a business action together with `safeEvent`. The field supplier must contain only bounded, side-effect-free reads of already-computed scalar values; the adapter is not permission to call arbitrary object getters or serialization safely.

Call it only at a bounded checkpoint:

```kotlin
logger.safeEvent(LogLevel.INFO, "file_upload.finished") {
    mapOf(
        "checkpoint" to "UPLOAD-EXIT",
        "module" to "photo_upload",
        "trace_id" to traceId,
        "stage" to "exit",
        "result" to "success",
        "duration_ms" to elapsedMs,
    )
}
```

## Immutable coroutine context and preserved dispatching

Avoid global mutable trace state. Carry an immutable operation context in the coroutine context, and retain it when using `withContext`.

```kotlin
import kotlin.coroutines.AbstractCoroutineContextElement
import kotlin.coroutines.CoroutineContext
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext

class OperationContext(val traceId: String) : AbstractCoroutineContextElement(Key) {
    companion object Key : CoroutineContext.Key<OperationContext>
}

suspend fun <T> onIo(dispatcher: CoroutineDispatcher, block: suspend () -> T): T =
    withContext(dispatcher) { block() }
```

`withContext(dispatcher)` combines the current context with the dispatcher, so `OperationContext` is preserved unless deliberately replaced. Read `coroutineContext[OperationContext]?.traceId` at the checkpoint rather than using a mutable singleton.

## Cancellation and responsibility boundaries

Rethrow `CancellationException`; cancellation must retain its semantics and is not an error stack. The owning ViewModel or user-command boundary records the known cancellation classification before it cancels work: user action is `user`, while a ViewModel scope ending because its owner is cleared is `lifecycle`. The use case owns operation checkpoints and outcome classification but does not infer cancellation origin. The repository records dependency metadata and returns errors; one responsible boundary records an unexpected error stack once.

```kotlin
import kotlinx.coroutines.CancellationException
import java.util.concurrent.atomic.AtomicBoolean

enum class CancellationKind(val fieldValue: String) {
    USER("user"),
    LIFECYCLE("lifecycle"),
}

class UploadTerminal(
    private val logger: DiagnosticLogger,
    private val traceId: String,
) {
    private val emitted = AtomicBoolean(false)

    fun success() = emit(
        LogLevel.INFO,
        "file_upload.finished",
        fields = mapOf("result" to "success"),
    )

    fun failure(error: Throwable) = emit(
        LogLevel.ERROR,
        "file_upload.finished",
        error = error,
        fields = mapOf("result" to "failure", "error_code" to "dependency"),
    )

    fun cancelled(kind: CancellationKind) = emit(
        LogLevel.INFO,
        "file_upload.cancelled",
        fields = mapOf(
            "result" to "cancelled",
            "cancellation_kind" to kind.fieldValue,
        ),
    )

    private fun emit(
        level: LogLevel,
        event: String,
        error: Throwable? = null,
        fields: Map<String, Any?>,
    ) {
        if (!emitted.compareAndSet(false, true)) return
        logger.safeEvent(level, event, error) {
            mapOf(
                "checkpoint" to "UPLOAD-EXIT",
                "module" to "photo_upload",
                "trace_id" to traceId,
                "stage" to "exit",
            ) + fields
        }
    }
}

suspend fun uploadFile(terminal: UploadTerminal, upload: suspend () -> Unit) {
    try {
        upload()
        terminal.success()
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (failure: Throwable) {
        terminal.failure(failure)
        throw failure
    }
}
```

The owning boundary calls `terminal.cancelled(CancellationKind.USER)` for a user command or `terminal.cancelled(CancellationKind.LIFECYCLE)` for lifecycle cancellation. The shared `AtomicBoolean` is owned by one operation and prevents success, failure, cancellation, or teardown races from emitting multiple terminals. Do not guess, swallow, or convert either cancellation into a failure. If the owner cannot know the origin, emit no cancellation classification instead of an ambiguous value.

Use `CoroutineExceptionHandler` only for uncaught coroutine failures at a scope boundary. It is not routine flow control and cannot replace local `try`/`catch`, cancellation rethrowing, or normal result handling.

```kotlin
import kotlinx.coroutines.CoroutineExceptionHandler

val uncaughtHandler = CoroutineExceptionHandler { _, throwable ->
    logger.safeEvent(LogLevel.ERROR, "coroutine.uncaught", throwable) {
        mapOf("stage" to "scope", "result" to "failure", "error_code" to "unknown")
    }
}
```

## Retrofit/OkHttp and database checkpoints

For Retrofit/OkHttp, log a supported request method, route category, status class, duration, retry outcome, and `trace_id`; never log URL query content, headers, or request/response bodies. Use an existing interceptor or repository boundary only if it can retain the project’s semantics.

For a Room database operation, log database operation category, result, row count, and duration. Do not log SQL arguments, query text when it may contain content, or returned row content. Repository code should emit either the database failure stack or return it to the use case, never both.

```kotlin
logger.safeEvent(LogLevel.INFO, "profile_cache.write") {
    mapOf("trace_id" to traceId, "stage" to "database", "result" to "success", "row_count" to rows, "duration_ms" to elapsedMs)
}
```

## WorkManager outcomes

For WorkManager, record the existing work name/category, run attempt count, retry decision, terminal result, duration, and safe error classification. A worker must preserve its normal `Result.retry()` or terminal-result behavior; the log is evidence only. Never include input/output data content.

```kotlin
logger.safeEvent(LogLevel.INFO, "sync_worker.finished") {
    mapOf("trace_id" to traceId, "attempt" to runAttemptCount, "result" to "retry", "retry" to true)
}
```

## Hot paths, visibility, and limits

Do not log inside frame/render, sensor, media, polling, pointer, callback, or per-item loops. Aggregate a bounded counter, state-change report, sample, or rate-limit outside that loop at an owned checkpoint. If the rate cannot be proved safe, do not add the per-iteration event.

Verify whether each event is visible in a release build and captured by the target environment. Android/Logcat line-length and truncation behavior, plus project volume and retention limits, must be discovered from the application and its deployment settings; do not invent thresholds. Keep fields compact even when the configured logger suppresses a level.
