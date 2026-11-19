# Business capability boundary discovery

Use this contract before planning events for every `add`, `review`, or `verify` task. Code organization is not a product specification: a package, class, method, protocol, or analytics label may represent only one phase of the capability named by the user.

## Boundary rule

Work outside-in from the user-visible goal, not inside-out from the first matching symbol. The agent must not infer the boundary from a package, class, method, event prefix, or requested noun alone.

Treat the requested feature as a candidate label until source and product-facing evidence establish:

- the user-visible goal;
- each public entry and automatic trigger;
- every upstream prerequisite that must succeed before the narrow action can begin;
- each business phase and phase handoff;
- the success criterion and every terminal outcome;
- cleanup, cancellation, timeout, background/foreground, and re-entry behavior;
- each excluded adjacent capability and the evidence for excluding it.

If two materially different boundaries remain plausible, show the competing boundaries and ask the user before editing. Do not silently choose the smallest code module.

## Outside-in discovery workflow

1. Restate the capability as a user outcome: “When `<trigger>`, the user/system can `<goal>`, complete when `<criterion>`.”
2. Inspect product-facing evidence first: route/navigation declarations, UI labels and actions, analytics journeys, requirements or docs, tests, and public feature interfaces.
3. Find all public and automatic entries, including app startup, login/logout, foreground/background, scheduled work, callbacks, notifications, and deep links.
4. Walk backward from the initially matched narrow action through callers and state owners until reaching each user/system trigger and prerequisite.
5. Walk forward through success, failure, timeout, cancellation, cleanup, and downstream user-visible outcome.
6. Walk laterally across module, process, protocol, callback, and UI handoffs. Record who owns the correlation identifier and terminal.
7. Reconcile the resulting flow with existing logs. A log prefix or already-instrumented module is evidence about current coverage, never evidence that the business boundary ends there.

Prefer structural call-graph tools for callers, callees, traces, and state ownership. Use text search for routes, strings, event names, analytics, and tests. Record file/symbol evidence for every phase; mark product semantics that source cannot prove as assumptions.

## Business Capability Contract

Produce this before an Observability Plan:

```text
Capability name in user language:
User-visible goal:
Public entries and automatic triggers:
Start boundary:
Success criterion:
Terminal outcomes:
Upstream prerequisites:
Business phases in order:
Phase handoffs and owners:
Downstream outcomes and cleanup:
Excluded adjacent capability and reason:
Product-facing evidence:
Structural source evidence:
Ambiguities requiring user confirmation:
```

The contract is incomplete if it merely repeats a class/module name, describes only the network request, or lacks a product success criterion.

## End-to-End Journey Matrix

Build this matrix before selecting checkpoints:

```text
phase | user/system intent | trigger and owner | prerequisite/input | observable outcome | handoff to next phase | failure/cancel/timeout exits | correlation | current log coverage | planned evidence or explicit skip | verification
```

Every phase from the earliest in-scope trigger through the terminal outcome must have source evidence and either a planned checkpoint or a justified explicit skip. Every critical handoff must have correlated evidence on both sides: the sending phase outcome and the receiving phase entry/result. A terminal event in one phase does not close the outer capability unless the Business Capability Contract says the user goal is complete there.

The following are hard completion gates:

- all public and automatic entries are represented;
- prerequisite failures are represented without starting a trace that can never close;
- the first phase, final phase, and every critical handoff are observable;
- success means the stated product success criterion, not merely a transport/API success;
- failure, cancellation, timeout, lifecycle exit, and cleanup paths are assigned to an owner;
- high-frequency discovery, scan, polling, and callback bodies remain free of per-occurrence logs;
- verification exercises at least one path through every phase and each alternate terminal class.

If any matrix row or critical handoff lacks evidence, `add` must not begin feature-code edits, and `review`/`verify` must report the instrumentation as incomplete.

## Near-field login example

“Near-field login” is the business capability, not only its login communication API. A representative journey is:

```text
authenticated app / foreground trigger
→ near-field discovery prerequisites (permission, Wi-Fi, discovery availability)
→ discovery starts
→ device availability changes (bounded state change or aggregate only)
→ nearby-device surface opens
→ user selects a device
→ P2P/IM connection
→ login communication
→ login success, failure, cancellation, timeout, or disconnect cleanup
```

Model the discovery lifecycle as part of the outer capability and the connection/login actions as child operations. Use a shared `feature_session_id` when one discovery journey leads to selection and login, while keeping separate `trace_id` values for discovery and login operations when both need independent closure.

At minimum the matrix must expose the discovery-to-selection and selection-to-login critical handoffs. `login communication succeeded` is not sufficient evidence if the log cannot show whether discovery started, found an eligible device, presented the selection surface, or handed the selected target into the connection phase. Conversely, high-frequency scan callbacks must not be logged per occurrence; use start/stop, state transition, bounded count change, timeout, and selected-target category without device identity.
