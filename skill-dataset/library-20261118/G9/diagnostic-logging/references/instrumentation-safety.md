# Instrumentation safety

Diagnostic logging is observational and expendable. The business path always wins: losing a diagnostic event is preferable to changing an application result, crashing, blocking, delaying a critical path, or altering cancellation/error behavior.

## Instrumentation Safety Contract

Produce this contract before editing:

```text
Business invariants: return value, state mutation, call ordering, callbacks, user-visible effects
Error invariants: exception type/message/ownership and cancellation propagation
Logging failure boundary and non-throwing evidence:
Field construction cost and failure containment:
Hot paths and maximum event frequency:
Per-event field count/size and computation class:
Existing release logger behavior and performance limits:
Behavior-preservation tests:
Fault-injection and representative-load tests:
Unverified risks:
```

The implementation must satisfy all of these rules:

- Logging and field construction are side-effect free. They cannot mutate business objects, consume streams/iterators, advance cursors, trigger lazy loads, or call getters with business effects.
- No logger return value, enabled state, once guard, sampling decision, or logging exception may control a business branch, return, retry, callback, state transition, or user-visible result.
- Keep logging outside a business `try`/`runCatching` block when a logging failure could be mistaken for a business failure. Do not place logging in `finally` when it could mask the original exception.
- Preserve the exact business return value, state mutation, call ordering, callback count, exception type, exception ownership, and cancellation propagation with logging enabled, disabled, and failing.
- Contain ordinary field supplier and logger failure at one proven non-throwing logging boundary. Never recursively log a logging failure. Do not swallow or reclassify the business exception being observed.
- Do not add new thread, coroutine, timer, network, file, database, or IPC work for feature events. Do not add sleeps, blocking locks, waits, retries, or synchronous flushing.
- Construct only allowlisted, immutable, bounded scalar fields. Do not use arbitrary `toString()`, unrestricted JSON/object serialization, reflection, stack capture for routine events, collection traversal, regex over unbounded input, file metadata reads, or content hashing.
- Gate lazy field construction behind the existing logger's enabled check. The check, field supplier, and emit call must all obey the non-throwing adapter contract.
- Keep routine checkpoint work O(1) in input size with a bounded field count and bounded string lengths. Use an already-available count/category rather than iterating a collection to calculate one for logging.
- Keep all per-occurrence logs out of high-frequency loops, callbacks, polling, rendering, media, sensors, pointer input, and bulk-item paths. Enabled and disabled logging both count when evaluating argument-construction cost.
- Do not move, duplicate, delay, or wrap a business call merely to create a checkpoint. Capture already-computed safe values after the business decision at its owning boundary.

Do not promise recovery from process death or VM-fatal conditions such as resource exhaustion. Instead, ensure instrumentation performs no unbounded allocation or dangerous work that could introduce those conditions.

## Failure containment pattern

Prefer a central adapter whose contract is already proven non-throwing. If the project logger and field adapter are not non-throwing, add the smallest local/shared adapter allowed by the task; do not wrap every call differently.

Bad—the logger is inside the business failure boundary:

```text
runCatching {
  result = performBusinessAction()
  logger.emit(successEvent)  // a logger failure now turns success into failure
}
```

Required shape:

```text
result = performBusinessAction()  // existing business semantics
safeDiagnosticEvent { successFieldsFromAlreadyComputedValues }
return result
```

The safe adapter may drop the diagnostic event when `isEnabled`, the field supplier, normalization, or `emit` fails. It must not start fallback I/O, call the same logger recursively, or affect the business result. Keep VM-fatal error policy aligned with the platform/project; avoid catching cancellation together with business work.

## Behavior Preservation Matrix

Build and verify this matrix for each modified responsibility boundary:

```text
scenario | baseline return/state/calls | instrumented return/state/calls | expected exception/cancellation | logger mode/fault | performance evidence | verdict
```

Cover at least:

1. logger disabled;
2. logger enabled and successful;
3. `isEnabled` throws or returns false;
4. field supplier throws or receives null/malformed optional data;
5. logger emit throws;
6. original business success;
7. each original business failure and cancellation path;
8. concurrent/racing terminal callbacks;
9. representative maximum-volume execution outside forbidden hot paths.

Use fault injection with a fault-injection logger to fail `isEnabled`, field construction, and emit independently. Assert exact business output, state, dependency invocation count/order, callback behavior, exception identity/type, and cancellation semantics against the pre-instrumentation baseline. Tests must not merely assert that “no crash occurred.”

For performance, use project release thresholds and existing benchmark/profiling facilities when available. Otherwise perform structural hot-path inspection plus a representative-load comparison, report the limit as unverified, and do not invent a threshold. Verify both enabled and disabled modes because eager interpolation and object construction can cost time even when emit is suppressed.

## Completion gate

Produce an **Instrumentation Safety Report** containing the contract, matrix evidence, privacy review, hot-path/event-volume review, and remaining assumptions. `add` and `verify` must not report completion when:

- a logging or field-construction failure can escape into business code;
- a logger call shares a business error boundary and can reclassify its outcome;
- any baseline return, state, order, callback, exception, or cancellation behavior changes;
- a new unbounded allocation, serialization, I/O, thread/coroutine, wait, retry, or high-frequency emission exists;
- performance evidence is missing for a touched risk-sensitive path.
