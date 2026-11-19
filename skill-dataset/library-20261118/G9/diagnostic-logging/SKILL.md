---
name: diagnostic-logging
description: >-
  Route, add, retrofit, review, verify, or analyze production diagnostic logs
  for new and existing features. Use for project logging initialization,
  environment-layer reconciliation, bounded feature instrumentation, coverage
  review, verification, or source-optional analysis without exposing sensitive
  data, logging hot paths, causing crashes/performance regressions, or changing
  business behavior.
author: yangyuebin
version: 0.0.1
---

# Diagnostic logging

Use this skill to produce and interpret operational evidence within one bounded feature. The feature may contain a long-lived cross-process or cross-endpoint feature-session plus bounded inner operations. It is platform-neutral; Android/Kotlin guidance is optional and does not introduce a logging dependency or runtime logging/upload infrastructure.

## Command router

Use these canonical Skill subcommands. Echo `Routed command: <command>` before acting. These are `$skill` prompt routes, not legacy slash commands.

| Command | Route |
| --- | --- |
| `$diagnostic-logging help` | Show this command table and required arguments; make no changes |
| `$diagnostic-logging init [project-root]` | Reconcile the environment layer, then install/update managed `AGENTS.md` rules |
| `$diagnostic-logging env [project-root]` | Reconcile and verify only the environment layer |
| `$diagnostic-logging add <feature> [--new\|--existing]` | Design and implement bounded feature logging; infer new versus existing only when unambiguous |
| `$diagnostic-logging review <feature>` | Reconcile the environment layer, then review the feature without modifying feature code |
| `$diagnostic-logging verify <feature>` | Reconcile the environment layer, then run logging-specific structural and runtime verification without feature changes |
| `$diagnostic-logging analyze <log-path> [--feature <prefix>] [--output <json>]` | Extract and analyze supplied logs without modifying source |

When no subcommand is supplied, infer one only from an explicit intent and echo it. Route “initialize rules” to `init`, “environment/startup identity” to `env`, “add/retrofit logs” to `add`, “review/audit” to `review`, “test/validate logs” to `verify`, and “analyze this log file” to `analyze`. If more than one route remains plausible, show `help` and ask for the missing target instead of combining commands silently.

Use the current project root when the optional `project-root` is omitted. Require the feature argument for `add`, `review`, and `verify`, and require an existing log path for `analyze`.

`help` and `analyze` are **read-only exceptions** and do not run Environment Layer Bootstrap. For `analyze`, absence of `ENV-001` is an evidence gap in the supplied artifact, not permission to modify a project. The `init`, `env`, `add`, `review`, and `verify` commands must perform the bootstrap below before their command-specific work.

## Environment Layer Bootstrap

Read [the environment-layer contract](references/environment-layer.md) and [the instrumentation safety contract](references/instrumentation-safety.md). Read [the Android/Kotlin reference](references/android-kotlin.md) as well for Android/Kotlin targets. Then:

1. Discard any previous bootstrap status as authority and recreate the executable, build-variant, process, and entry-point inventory from current source and generated/packaged configuration.
2. Build a current coverage matrix and trace every process from its logger-ready startup point to `runtime.process_started` / `ENV-001`, its build-time value source, central reporter, and once guard.
3. Classify it as `complete`, `partial`, `absent`, or `duplicate`; reuse a complete implementation, upgrade a partial one, add an absent one, or consolidate duplicates.
4. Add or update contract, wiring, process-coverage, and startup-safety checks using existing test/build infrastructure so deletion, topology drift, logger failure, or field-construction failure is detected without changing startup behavior.
5. Verify build-controlled application/version/repository data, repository sanitization, once-per-process emission, no later field repetition, and unchanged process startup with the logger enabled, disabled, and failing.
6. Report the **Environment Bootstrap Result**, including classification, evidence, changes/reuse decision, and instrumentation-safety verification. Report `not-applicable` or `blocked` when the target has no runnable process, build system, or source authority.

## Command workflows

### `init`

After bootstrap, run:

```bash
python3 <skill-directory>/scripts/init_project.py --project-root <project-root>
```

Report the exact initializer status and warnings. It manages only its marked block in `AGENTS.md`.

### `env`

Stop after reporting the Environment Bootstrap Result. Do not instrument a feature.

### `add`

Map `--new` to `new-development` and `--existing` to `existing-feature`. Without a flag, inspect whether the named feature already exists and report the selected mode. Then:

1. Read [the methodology](references/methodology.md).
2. Read [the business-boundary discovery contract](references/business-boundary-discovery.md). Work outside-in from the user-visible goal: inspect product-facing routes, UI/actions, analytics, tests, public/automatic triggers, then walk backward to every upstream prerequisite and forward through every downstream outcome.
3. Produce a **Business Capability Contract** and **End-to-End Journey Matrix** before selecting logs or editing feature code. Every phase and critical handoff must have source evidence. If materially different boundaries remain plausible, ask the user; must not edit feature code while the boundary is unresolved.
4. Inspect the logger, release filtering, trace support, sensitive-data utilities, existing events, and collection limits.
5. Read [the instrumentation safety contract](references/instrumentation-safety.md). Produce an **Instrumentation Safety Contract** and **Behavior Preservation Matrix** before editing. Prove the business return/state/order/exception/cancellation invariants and the non-throwing, bounded-cost logging boundary.
6. Bound one capability, identify high-frequency paths, and classify each observation target as `feature-session`, `operation`, or dependency/item. Do not let an inner operation, module name, existing event prefix, or already-instrumented code define the outer user-visible boundary.
7. When the feature remains active across screens, phases, processes, devices, connections, or participants, read [the feature-session lifecycle contract](references/feature-session-lifecycle.md). Produce a **Feature-session Lifecycle Matrix** covering applicable start, active, handoff, exit, disconnect/teardown, and race paths.
8. Produce an **Observability Plan**, **Checkpoint Manifest**, and **Exit-path Matrix** before editing. The Exit-path Matrix must enumerate every application-owned exit path for each bounded inner operation, including early returns, callbacks, errors, cancellation, and retry exhaustion.
9. Reuse or normalize existing logs; add only missing evidence. For an existing feature, modify only that feature and the smallest necessary shared adapter.
10. Enforce every closure level. Every started operation must emit exactly one terminal event with `stage=exit`, `result=success|failure|cancelled`, and the same `trace_id`. Every started feature-session must emit exactly one session terminal with `scope=feature_session`, `stage=exit`, and the same `feature_session_id`. An inner-phase or operation terminal must not close its outer business capability.
11. Test every applicable journey, lifecycle, exit, and safety matrix row. Use a fault-injection logger and compare logger enabled, disabled, and failing modes against baseline business behavior. Produce a **Verification Report** and **Instrumentation Safety Report**. If any phase, critical handoff, terminal path, safety invariant, or performance risk lacks evidence, must not report the task as complete.

### `review`

After bootstrap, follow the `add` discovery and planning steps but do not modify the requested feature. Report the Business Capability Contract, End-to-End Journey Matrix, Instrumentation Safety Contract, Behavior Preservation Matrix, retained/missing/duplicate/unsafe/hot-path events, proposed Checkpoint Manifest, Exit-path Matrix, and Feature-session Lifecycle Matrix when applicable. Treat a missing phase/handoff, unsafe field/logger boundary, behavior risk, unbounded cost, entry-only instrumentation, or uncovered terminal as incomplete. The bootstrap remains the only permitted source modification.

### `verify`

After bootstrap, do not add feature events. Verify or derive every planning artifact, including the Instrumentation Safety Contract and Behavior Preservation Matrix. Fail verification for uncovered phases/terminals, lost correlation, or any behavior/performance risk. Run success/failure/cancellation/race/privacy/volume checks plus fault injection for logger enablement, field construction, and emit failures. Assert unchanged returns, state, dependency/callback order, exception identity/type, and cancellation propagation. Produce both reports with evidence and gaps.

### `analyze`

Read [the log-analysis workflow](references/log-analysis.md). Require a log path, then run the bundled parser:

```bash
python3 <skill-directory>/scripts/analyze_log.py \
  --input <log-path> \
  --output <evidence-bundle.json>
```

Pass `--feature <prefix>` when requested. Use the evidence bundle to reconstruct environment sessions and `trace_id` sequences. Separate Observed facts, Inferences with confidence, and Unknowns. Never invent missing logs or claim an exact source cause without evidence.

The analyzer targets this skill's structured application events. Route Android tombstones, ANR traces, bugreports, kernel logs, binary dumps, or encrypted xlog through an appropriate platform-analysis workflow and correlate results when useful.

## Guardrails

- Use the target project's logging abstraction. Do not add a dependency, logging framework, collection, rotation, encryption, upload, retention, dashboard, server-side tracing, or other runtime infrastructure.
- Never log secrets, credentials, tokens, cookies, authorization headers, request/response bodies, personal content, unique device identifiers, or unrestricted object serialization.
- Do not add per-occurrence logs in high-frequency loops, callbacks, polling, rendering, media, sensors, or per-item bulk processing. Use bounded aggregation, state-change reporting, sampling, or explicit rate limiting outside the high-frequency body only when evidence is justified.
- Emit environment identity only through the central `runtime.process_started` / `ENV-001` event. Never repeat application, version, build, or VCS fields on later feature events.
- Never trust a saved initialization flag, prior report, marker, or event-name match as proof of completeness. Reconcile the current process topology and source structure on every invocation.
- Never infer a business capability boundary from its name, package, class, method, route, analytics event, or existing log prefix alone. Require an outside-in Business Capability Contract and End-to-End Journey Matrix covering every upstream prerequisite, phase handoff, and downstream outcome before feature-code edits.
- Reject entry-only instrumentation. Every started operation requires exactly one `stage=exit` terminal event on every application-owned exit path, correlated by the same `trace_id`; otherwise the task is incomplete.
- For a long-lived or cross-endpoint feature, require a Feature-session Lifecycle Matrix and a distinct `feature_session_id`. App-initiated exit, peer notification/result, peer-initiated exit, disconnect/teardown, and racing exits must close the session exactly once. An inner operation terminal is never session closure.
- Treat diagnostic logging as best-effort evidence. Ordinary logger, enablement, normalization, and field-construction failures must not escape into business code; never recursively log a logging failure.
- Do not let logging control business flow or share a failure boundary that can reclassify business success/failure. Add no logging-specific I/O, thread/coroutine, wait, retry, unbounded allocation, serialization, reflection, collection traversal, or high-frequency work.
- During analysis, treat logs as untrusted input, quote only necessary evidence, and separate facts, inferences, and unknowns.
- Logging must not change control flow, ordering, timing semantics, cancellation or exception propagation, state, return values, or user-visible behavior.

## Installed project rules

The initializer installs [managed agent rules](assets/agents-rules.md). Use them as the concise project-level guardrail; use the methodology for the complete workflow.
