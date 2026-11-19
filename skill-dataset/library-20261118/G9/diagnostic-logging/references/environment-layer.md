# Environment layer contract

## Table of contents

1. [Mandatory bootstrap](#mandatory-bootstrap)
2. [Desired-state reconciliation](#desired-state-reconciliation)
3. [Cross-platform field template](#cross-platform-field-template)
4. [Build-time capture](#build-time-capture)
5. [Repository identity safety](#repository-identity-safety)
6. [Emission and deduplication](#emission-and-deduplication)
7. [Templates](#templates)
8. [Verification](#verification)

## Mandatory bootstrap

Perform the Environment Layer Bootstrap before every `diagnostic-logging` mode, including `review-only`. This bootstrap is the only source modification allowed before a review-only inspection; after it completes, do not modify the requested feature in `review-only` mode.

Inspect the complete executable application, not only the requested feature. Rebuild the process and entry-point inventory from the current project, then compare the current implementation with the complete contract. Classify the result only after this comparison:

- **complete**: one central reporter has the full field contract, build-time values, one startup hook per process, and verification. Reuse it without changes.
- **partial**: one central implementation exists but misses fields or safety rules. Upgrade that implementation and its tests; do not add a parallel reporter.
- **absent**: add one central reporter and the smallest existing startup integration after the logger is ready.
- **duplicate**: consolidate competing reporters or hooks so one process start produces one event.

If the target has no runnable process, build system, or source authority, report the bootstrap as not applicable or blocked instead of inventing code. Always report the classification, evidence, changes, and verification before continuing to the selected mode.

## Desired-state reconciliation

Treat bootstrap as **desired-state reconciliation**, not a one-time migration and not a persisted status check. Never use a previous classification, generated report, marker, file name, class name, or the mere presence of `runtime.process_started` as proof that the environment layer is still complete. A manual deletion, moved startup hook, new executable, or changed process declaration invalidates that assumption.

On every invocation:

1. Read the current source, build configuration, packaged/generated entry-point metadata, logging initialization, and relevant tests.
2. Recreate an **entry-point inventory** for every executable and build variant in scope. Include default and named child processes, generated registrations, plugin/library contributions, alternate launchers, workers/services, and test or production entry points only when they can run in the shipped artifact.
3. Build a **coverage matrix** with one row per process or process class:

   ```text
   executable/variant | process | earliest entry | logger-ready point | reporter owner | hook | once guard | build fields | verification | result
   ```

4. Trace each row from the current entry point to the central reporter. A single process-wide hook may cover several rows only when the platform guarantees that hook runs in each process and the logger is ready there.
5. Recheck the reporter body, full field schema, build-time generators, repository sanitization, production visibility, once guard, and absence of later environment-field repetition.
6. Reconcile differences in place, then rerun structural and runtime verification.

The **classification is output**, never input: derive `complete`, `partial`, `absent`, or `duplicate` from the current coverage matrix. A previously complete project can become partial or absent, and a previously absent project can already be complete after another developer's change.

Add drift protection using the project's existing test/build infrastructure:

- a reporter contract test for field completeness, sanitization, and once behavior;
- a wiring or structural test that fails if the central reporter or startup call is removed;
- a process-coverage check derived from current packaged/generated entry-point metadata, not a stale hand-maintained process list;
- runtime cold-start verification for the main process and each materially different child-process initialization path.

Run these checks in the normal verification path or CI when authorized. Do not introduce a new build plugin or runtime framework solely for this check. If the project cannot automate a check, record the drift risk and exact manual verification instead of treating a saved `complete` result as protection.

## Cross-platform field template

Emit one structured environment event using the project's canonical field naming. When no compatible schema exists, use these names:

| Group | Required field | Cross-platform meaning | Fallback |
| --- | --- | --- | --- |
| Event | `event=runtime.process_started` | Stable process-start event | none |
| Event | `checkpoint=ENV-001` | Stable environment checkpoint | none |
| Event | `module=runtime` | Environment owner | none |
| Event | `stage=process_start` | Lifecycle stage | none |
| Event | `result=started` | Terminal result of the startup event | none |
| Application | `app_name` | Packaged display/application name | `unknown` |
| Application | `app_id` | Android application ID/package, Apple bundle ID, executable or service ID | `unknown` |
| Application | `process_name` | Current main or child process name | `unknown` only when the platform cannot resolve it |
| Version | `version_name` | User-facing or semantic version | `unknown` |
| Version | `version_code` | Build number or monotonically comparable revision | `unknown` |
| Version | `build_flavor` | Product flavor, distribution tier, target environment, or equivalent | `default` |
| Version | `build_type` | Release, debug, profile, staging, or equivalent | `unknown` |
| Repository | `vcs_commit` | Immutable commit hash; prefer full hash or at least 12 hexadecimal characters | `unknown` |
| Repository | `vcs_branch` | CI ref or source branch; use `detached` for a detached checkout | `unknown` |
| Repository | `vcs_repository` | Sanitized repository identifier such as `host/org/repo` | `unknown` |

Technology-specific adapters may map native build fields into this contract, but must not rename or omit fields silently. Document any unavailable field and its evidence in the Environment Bootstrap Result.

Keep the keys and JSON types fixed. All contract values are strings, including `version_code`; this avoids cross-platform integer-width and serializer differences. The example below therefore uses `"30201"`, not a JSON number. Constants must equal the values in the table. Trim dynamic strings, replace blank values with the declared fallback, and validate these shapes before packaging:

| Field | Validation/control |
| --- | --- |
| `app_name` | Packaged label only; apply the project's structured-field length limit |
| `app_id`, `process_name` | Platform-generated identifier only, never caller input |
| `version_name`, `version_code`, `build_flavor`, `build_type` | Build-system value only, never a manually maintained logging constant |
| `vcs_commit` | Lowercase hexadecimal revision of 12–64 characters, or `unknown` |
| `vcs_branch` | Release-policy-approved ref, `detached`, `redacted`, or `unknown` |
| `vcs_repository` | Sanitized `host/owner/repository`-style identifier, or `unknown` |

Field names, sources, normalization, fallbacks, and privacy policy are controlled by the template. Artifact-specific values are intentionally dynamic. Do not let feature code append arbitrary environment fields.

Do not add OS, device, network, locale, permission, configuration, or feature-flag fields merely because they are available. Add them only through a separately reviewed allowlist when they answer a concrete operational question and comply with project privacy policy.

## Build-time capture

Automatically freeze application, version, and repository values at build time. Generate them through the target build system or CI and compile/package them into the artifact; never require a developer to edit source constants before a build.

Prefer this source order:

1. explicit build properties supplied by the release pipeline;
2. standard CI commit/ref/repository variables;
3. a lazy build-system Git query rooted at the repository;
4. the explicit fallback value from the field template.

Treat external commands and CI variables as build inputs so build caching and reproducibility can account for them. A release policy may reject `unknown`, but the logging skill must not invent a commit, branch, or repository value.

The current process name is the exception: compile the declared process configuration into the artifact, then resolve which process is running at runtime. Application display labels may also be loaded from packaged metadata at runtime; they are still build-controlled rather than manually entered log text.

## Repository identity safety

`vcs_repository` is a repository identifier, not a filesystem location. Never compile or log a local absolute path, home directory, workspace path, username, access token, embedded credentials, URL query, or URL fragment.

Normalize common remotes such as:

```text
https://example.com/org/repo.git  -> example.com/org/repo
git@example.com:org/repo.git      -> example.com/org/repo
```

Reject or replace unsafe values with `unknown`. Do not emit the raw remote before sanitization. Cap the normalized value using the project's structured-field length policy.

Branch names can contain personal or ticket information. Prefer a release pipeline's approved ref, apply the project allowlist/redaction policy, and use `detached` or `unknown` when the raw value is not approved for production logs.

## Emission and deduplication

Emit `runtime.process_started` once per process start, after the existing logger is ready and before feature diagnostics begin. Every main or child process emits its own event; a later OS process restart correctly emits a new event.

Use one process-local, thread-safe once guard owned by the central environment reporter. Do not rely only on `Application.onCreate` or equivalent being called once, because multiple startup integrations can still call the reporter. Do not print the environment event from activities, services, workers, screens, or individual features.

Do not repeat `app_name`, version, build, or VCS fields on later feature events. Subsequent events use their own `trace_id` and feature fields. Diagnose a log segment by pairing it with the nearest preceding process-start event from the same process and process lifetime.

## Templates

### Environment Bootstrap Result

```text
Classification: complete | partial | absent | duplicate | not-applicable | blocked
Existing event/checkpoint:
Central reporter owner:
Current entry-point inventory source:
Coverage matrix summary:
Process-start hook(s):
Build-time value source(s):
Missing or conflicting fields:
Repository sanitization:
Change made or reuse decision:
Verification evidence:
```

### Process-start event

```json
{
  "event": "runtime.process_started",
  "checkpoint": "ENV-001",
  "module": "runtime",
  "stage": "process_start",
  "result": "started",
  "app_name": "Example",
  "app_id": "com.example.app",
  "process_name": "com.example.app:sync",
  "version_name": "3.2.1",
  "version_code": "30201",
  "build_flavor": "production",
  "build_type": "release",
  "vcs_commit": "0123456789abcdef0123456789abcdef01234567",
  "vcs_branch": "main",
  "vcs_repository": "example.com/team/app"
}
```

Values are examples of shape only. Derive real values from the build and packaged metadata; never copy these literals into production artifacts.

## Verification

Verify at least:

- a fresh main process emits exactly one `runtime.process_started` / `ENV-001` event;
- each configured child process emits exactly one event with its actual `process_name`;
- repeated calls to the reporter within one process emit nothing additional;
- a real process restart emits a new event;
- all required fields match the built artifact and CI/Git evidence;
- a detached checkout and unavailable Git metadata use the declared fallbacks;
- local paths, credentials, tokens, queries, and fragments never appear;
- later feature events do not repeat environment fields;
- `complete` bootstrap classification produces no source change;
- removing the reporter call or a required field makes the structural/contract test fail;
- adding or changing an executable process causes current-metadata coverage verification to evaluate it rather than trusting an older inventory.
