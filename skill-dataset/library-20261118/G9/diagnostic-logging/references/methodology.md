# Diagnostic logging methodology

## Table of contents

1. [Environment prerequisite](#environment-prerequisite)
2. [Feature-boundary discovery](#feature-boundary-discovery)
3. [Observation scopes](#observation-scopes)
4. [Existing-log inventory](#existing-log-inventory)
5. [Structured event schema](#structured-event-schema)
6. [Trace propagation](#trace-propagation)
7. [Checkpoint selection](#checkpoint-selection)
8. [Instrumentation safety](#instrumentation-safety)
9. [Operation closure invariant](#operation-closure-invariant)
10. [Error taxonomy](#error-taxonomy)
11. [High-frequency paths](#high-frequency-paths)
12. [Sensitive-data matrix](#sensitive-data-matrix)
13. [Severity, visibility, and budgets](#severity-visibility-and-budgets)
14. [File-upload example](#file-upload-example)
15. [Required templates](#required-templates)
16. [Runtime infrastructure gaps](#runtime-infrastructure-gaps)

## Environment prerequisite

Before selecting a feature mode, complete the [Environment Layer Bootstrap](environment-layer.md). It owns application, version, build, and sanitized repository identity in one `runtime.process_started` / `ENV-001` event emitted once per process start. Later feature events must not repeat those environment fields; correlate them with the preceding process-start event from the same process lifetime.

This check is mandatory on every invocation. Derive its classification by reconciling the current executable/process inventory and source structure; never reuse an earlier classification as evidence. Reuse a currently complete implementation, upgrade a partial one, add an absent one, or consolidate duplicates. It is the only application-source change allowed in `review-only`; the requested feature remains read-only.

## Feature-boundary discovery

Read [the business-boundary discovery contract](business-boundary-discovery.md) before inventorying logs. Produce its **Business Capability Contract** and **End-to-End Journey Matrix** from product-facing and structural evidence. These artifacts define what the feature means; an existing package, class, request, route, analytics event, or log prefix does not.

For `new-development`, start at every user/system trigger and map prerequisites, phases, handoffs, sessions, inner operations, exits, dependencies, peer callbacks, and cancellation owners. For an `existing-feature`, also inventory current routes, UI actions, analytics, tests, state owners, async handoffs, protocol callbacks, cleanup, and logs. Walk backward from the initially matched narrow action to every upstream prerequisite and forward to the final product outcome. If the boundary remains materially ambiguous, ask the user before feature-code edits.

Every journey phase and critical handoff needs correlated evidence or an explicit, justified skip. Bound the eventual change to the confirmed capability and smallest necessary shared logging adapter. Logging cannot change control flow, ordering, timing semantics, cancellation/exception propagation, state, return values, or user-visible behavior.

## Observation scopes

Classify planned events as `feature_session`, `operation`, or dependency/item before selecting checkpoints. A feature session may span sequential business phases as well as screens, processes, devices, connections, or participants; an operation is one bounded action inside or outside that session; dependency/item events are intermediate evidence only.

When `feature_session` applies, read [the feature-session lifecycle contract](feature-session-lifecycle.md) and produce its **Feature-session Lifecycle Matrix** in addition to the per-operation Exit-path Matrix. An upload, display update, annotation, dependency result, or item completion cannot prove that the outer session exited.

## Existing-log inventory

List each existing event in the bounded path and decide one action: **retain**, **normalize**, **relocate**, **remove**, or **add**. Keep useful evidence; normalize unstable names or unsafe fields; relocate an exception stack to its responsible boundary; remove duplicate or unsafe logs; add only an uncovered operational question. Never duplicate blindly.

## Structured event schema

Use stable, lowercase, dot-separated names such as `file_upload.started`, `file_upload.retry_scheduled`, and `file_upload.finished`.

| Applicability | Fields and guidance |
| --- | --- |
| Required on every event | `event`, `checkpoint`, `module`, `stage`, `result`; timestamp and level supplied by the project logger |
| Required to distinguish nested lifecycles | `scope=feature_session|operation|dependency|item` when a feature has more than one lifecycle level |
| Required for a feature session | `feature_session_id`; create it at the session owner and keep it through the session terminal |
| Required for a correlated operation | `trace_id`; create it at the bounded entry and keep it on every event in that operation |
| Required when the outcome applies | `error_code`, `retry_count`, fallback, `cancellation_kind`, dependency, status class, count, size category, reason, `initiator`, and `duration_ms` |
| Required when runtime context can affect interpretation | The project's canonical execution-context fields |

Build identity is required when events from multiple builds may be aggregated or release behavior may differ, but it belongs in the process-start environment event rather than every feature event. If the existing logger automatically enriches every record, document and verify that behavior instead of adding duplicate source fields. Execution context is required when work crosses or runs on an asynchronous task, thread, coroutine, worker, process, or supported network boundary; use the project's canonical context fields rather than inventing identifiers, and attach it at the applicable feature event when the logger does not already attach it. Record automatic logger enrichment in the Observability Plan so its presence can be verified.

Fields describe the operation, not its content. Use a category or count rather than a payload, and omit conditional fields only when their stated applicability does not apply.

## Trace propagation

Create a `feature_session_id` at the long-lived session owner and a separate `trace_id` at each bounded inner operation's entry. Carry `feature_session_id` on child-operation events only when it is needed to establish parentage; do not reuse one identifier for both lifecycle levels. Pass identifiers explicitly or in the target platform's immutable context across async tasks and module boundaries. Preserve them across supported process and network boundaries only when the project's existing mechanism supports that boundary. Do not invent or add tracing infrastructure; record the propagation boundary and any unverified support in the plan.

## Checkpoint selection

Select checkpoints that answer a distinct question: entry, decision, state transition, dependency request/result, retry, fallback, exit, cancellation, and failure. Record stage and result at each relevant boundary; attach reason, `error_code`, classification, and duration when applicable. Emit an exception stack once, where the failure becomes responsibly handled, and do not restack it in callers.

## Instrumentation safety

Read [the instrumentation safety contract](instrumentation-safety.md) before editing. Produce its **Instrumentation Safety Contract** and **Behavior Preservation Matrix**. Keep logs observational: logger enablement, field construction, normalization, emit failures, sampling, and once guards must not change any business result, state, call ordering, callback, exception, cancellation, or user-visible effect.

Prefer one proven non-throwing logging adapter, lazy bounded scalar fields, and O(1) checkpoint work. Keep log calls outside business error boundaries when their failure could be misclassified. Add no logging-specific I/O, task/thread, wait, retry, unbounded computation, or high-frequency emission. Completion requires fault-injection evidence and applicable representative-load/performance evidence.

## Operation closure invariant

Treat operation closure as a hard completion gate, not a best-effort guideline. Before editing, create an **Exit-path Matrix** for the bounded operation:

```text
exit path | trigger/code location | outcome | terminal event | result/error/cancellation fields | trace owner | verification
```

Enumerate every application-owned exit path after entry: normal completion, validation or no-op early return, success callback, error callback, exception, timeout, user cancellation, lifecycle cancellation, retry exhaustion, and owner disposal or teardown when it ends the operation. Process death or other exits the application cannot observe are explicit limitations, not silently covered paths.

Once an entry event with `result=started` is emitted:

- emit exactly one terminal event on every application-owned exit path;
- set the terminal event to `stage=exit` and `result=success`, `failure`, or `cancelled`;
- retain the same `trace_id` from entry through terminal, including retries and asynchronous callbacks;
- keep item completions, dependency results, progress, and retry scheduling as intermediate events, even when their local result is successful or failed;
- either validate before emitting the entry event or close validation/no-op early returns with a terminal event; never emit `*.started` and then return silently;
- use a per-operation terminal once guard when completion, error, cancellation, or teardown callbacks can race, without changing business control flow.

Verify every Exit-path Matrix row with the project's existing test infrastructure. Assert that each observed started trace has one and only one `stage=exit` event with the same `trace_id`; exercise at least success, each owned early return, handled failure, timeout when applicable, cancellation, retry success, and retry exhaustion. Static inspection alone may support a path that cannot be executed locally, but record the limitation and must not report the task as complete while an application-owned exit remains uncovered.

## Error taxonomy

Assign a stable `error_code` and one category: validation, permission, local resource, dependency, timeout, user cancellation, lifecycle cancellation, conflict, capacity, or unknown failure. Cancellation is an expected outcome when requested; it is not a failure merely because work ended. Preserve the original propagation behavior and use the project’s error mapping rather than creating a parallel taxonomy.

## High-frequency paths

High-frequency execution includes per-occurrence loops, callbacks, polling, rendering or frame paths, media streams, sensors, pointer input, and per-item bulk processing. These are forbidden examples: logging every frame, sensor sample, callback, poll, packet, pointer move, or imported item.

If invocation frequency cannot be proven safe, add no per-occurrence log. Debug suppression does not make a high-frequency log safe: argument construction and dispatch still cost. When evidence is justified, aggregate a bounded count, report a state change, sample deliberately, or apply an explicit rate limit **outside** the hot body. Record the strategy and its owner in the Checkpoint Manifest.

## Sensitive-data matrix

| Never log | Safe replacement |
| --- | --- |
| Secrets, credentials, tokens, cookies, authorization headers | presence/state only, such as `credential_present=true` when approved |
| Request/response body, personal content | category, count, size bucket, or status class |
| Unique device identifier | approved non-reversible identifier, only if the project already provides one |
| File name, path, query, SQL arguments, returned content | file type, storage category, row count, or result category |
| Arbitrary object or exception serialization | allowlisted fields and one responsible stack trace |

Mask only an approved non-sensitive suffix when the project policy permits it. Do not treat hashing, debug builds, or a private logger as automatic authorization to log sensitive values.

## Severity, visibility, and budgets

Use the project's established severity and release-filtering policy: failures requiring attention usually belong at its error level, recoverable or expected outcomes at the appropriate lower level, and routine diagnostics only where release visibility permits. Verify release visibility rather than assuming debug output is collected.

Discover volume, retention, line-length, truncation, and rate budgets from the target project. If unavailable, list them as unverified assumptions; never invent values or use a fabricated budget to justify an event.

## File-upload example

Operation `file_upload` has a generated `trace_id` and no file name, path, bytes, headers, or response body in logs.

Every terminal event below uses `stage=exit`; per-item success and retry events remain intermediate even if their local `result` is successful.

| Outcome | Expected event sequence |
| --- | --- |
| Success | `file_upload.started` → `file_upload.dependency_requested` → `file_upload.finished { result=success, duration_ms }` |
| Retry | `file_upload.started` → `file_upload.dependency_requested` → `file_upload.dependency_failed { error_code=dependency }` → `file_upload.retry_scheduled { retry_count }` → `file_upload.dependency_requested` → `file_upload.finished { result=success, duration_ms }` |
| Timeout | `file_upload.started` → `file_upload.dependency_requested` → `file_upload.dependency_failed { error_code=timeout }` → `file_upload.finished { result=failure, duration_ms }` |
| User cancel | `file_upload.started` → `file_upload.cancelled { cancellation_kind=user, result=cancelled }` |
| Lifecycle cancel | `file_upload.started` → `file_upload.cancelled { cancellation_kind=lifecycle, result=cancelled }` |

The responsible boundary logs an unexpected exception stack once. Expected cancellation produces no failure stack and must continue to propagate according to the application’s cancellation contract.

## Required templates

### Observability Plan

```text
Feature boundary:
Business Capability Contract reference:
End-to-End Journey Matrix summary and critical handoffs:
Observation scopes: feature_session | operation | dependency/item
Mode: init | new-development | existing-feature | review-only
Environment Bootstrap Result reference:
Operational questions and expected outcomes:
Feature-session Lifecycle Matrix summary, when applicable:
Exit-path Matrix summary and application-owned exits:
Existing-log inventory and decisions:
Session/trace boundaries and identifier propagation:
High-frequency paths and skipped/aggregated strategy:
Allowed fields, sensitive-data controls, release visibility:
Instrumentation Safety Contract and Behavior Preservation Matrix reference:
Unverified assumptions and infrastructure gaps:
```

### Checkpoint Manifest

```text
checkpoint | stable event | stage/result | terminal? | fields | owner | stack responsibility | verification path
```

### Business boundary artifacts

Use the full templates in [business-boundary-discovery.md](business-boundary-discovery.md). Complete the Business Capability Contract and End-to-End Journey Matrix before the Observability Plan.

### Instrumentation safety artifacts

Use the full templates in [instrumentation-safety.md](instrumentation-safety.md). Complete the Instrumentation Safety Contract and Behavior Preservation Matrix before editing, then produce the Instrumentation Safety Report during verification.

### Exit-path Matrix

```text
exit path | trigger/code location | outcome | terminal event | result/error/cancellation fields | trace owner | verification
```

### Feature-session Lifecycle Matrix

Use the full contract in [feature-session-lifecycle.md](feature-session-lifecycle.md):

```text
path | initiator | trigger/code location | local state before/after | peer request/callback/result | session event | result/reason | feature_session_id owner | once guard | verification
```

### Verification Report

```text
Environment bootstrap classification and evidence:
Business Capability Contract evidence and unresolved assumptions:
End-to-End Journey Matrix phase/handoff coverage:
Implemented checkpoints:
Feature-session Lifecycle Matrix rows and session closure evidence:
Exit-path Matrix rows and terminal closure evidence:
Expected sequences and observed evidence:
Behavior and cancellation preservation:
Logging fault-injection and performance evidence:
Privacy, duplicate-stack, release-visibility, and volume checks:
Unverified assumptions, infrastructure gaps, and deliberately skipped hot paths:
```

## Runtime infrastructure gaps

Report gaps such as absent release capture, unsupported trace propagation, unknown retention, or unavailable masking helpers. Do not implement collection, rotation, encryption, upload, retention, dashboards, server-side tracing, or a new logging framework without separate authorization.
