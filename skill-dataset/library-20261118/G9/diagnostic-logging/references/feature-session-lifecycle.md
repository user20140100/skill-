# Feature-session lifecycle

Use this contract when a named feature remains active across screens, processes, devices, connections, or participants. A feature session is not the same thing as one bounded operation inside it.

## Choose the observation level first

Classify every planned event as one of these scopes:

| Scope | Meaning | Correlation |
| --- | --- | --- |
| `feature_session` | The complete user-visible capability from local entry until all locally owned cleanup and required peer coordination finish | `feature_session_id` |
| `operation` | A bounded action inside the session, such as one upload or save | its own `trace_id`, plus `feature_session_id` when it belongs to a session |
| `dependency` or `item` | An intermediate request, callback, retry, image, or annotation action | inherit the owning operation/session identifiers; never act as their terminal |

The terminal event of an inner operation must not close the outer feature session. For example, one image upload can finish successfully while collaborative display and annotation remain active.

Do not add distributed tracing infrastructure merely to create `feature_session_id`. Create it at the local session owner and propagate it across an existing supported process or protocol boundary only when the project already permits that metadata. If the peer cannot receive it, keep the local ID and record peer notifications as local evidence; state that peer-side correlation is unverified.

## Discover the real session boundary

Start from the user-visible local entry and continue until the owning session state and UI are released. Inspect all of the following, even when they live in different classes or modules:

- local entry and peer entry notification/request/result;
- the point at which the session active state is established;
- child uploads, display changes, annotations, and other inner operations;
- local exit triggers such as back, close, logout, conflict, replacement, or explicit stop;
- peer exit notification request/result for an App-initiated exit;
- peer-initiated exit callbacks and the resulting local cleanup;
- disconnect, timeout, reconnect exhaustion, process/lifecycle cancellation, and lifecycle teardown;
- simultaneous local and peer exits, repeated callbacks, and destroy-after-finish races.

A remote trigger is still an application-owned path once this application receives its callback. Do not omit peer-initiated exit merely because the peer originated it.

## Feature-session Lifecycle Matrix

Build this matrix before editing:

```text
path | initiator | trigger/code location | local state before/after | peer request/callback/result | session event | result/reason | feature_session_id owner | once guard | verification
```

The matrix must contain, where applicable:

1. local entry;
2. peer entry notification and its success, failure, or unverified dispatch result;
3. session active;
4. App-initiated local exit and peer exit notification;
5. peer-initiated exit and local cleanup without an accidental echo request unless the protocol requires one;
6. disconnect, timeout, conflict, replacement, and lifecycle teardown;
7. simultaneous or repeated exit signals.

Use an explicit `initiator` such as `app`, `peer`, or `system`, plus a bounded `reason`. Do not infer the exit reason only from a generic destroy callback. Preserve an immutable exit context at the session owner when the explicit trigger and final cleanup occur at different times.

## Session closure invariant

Once `scope=feature_session`, `stage=entry`, and `result=started` is emitted for a `feature_session_id`:

- emit exactly one session terminal event with the same `feature_session_id`, `scope=feature_session`, `stage=exit`, and `result=success|failure|cancelled`;
- emit the terminal only after locally owned cleanup has completed and the required peer-exit request has a known result, or is explicitly classified as dispatched-but-unverified by an existing fire-and-forget protocol;
- keep upload completion, image display, annotation, peer request results, and callbacks as intermediate events;
- place a terminal once guard at the session owner so App exit, peer exit, disconnect, and lifecycle teardown cannot produce duplicate terminals;
- preserve the winning `initiator` and `reason`; later racing signals may be aggregated or ignored, but must not emit another terminal;
- do not change whether the application sends a peer notification, echoes a remote exit, retries, closes UI, or propagates an error.

An App-initiated exit normally records the local exit request, peer exit notification request/result, local cleanup, then the session terminal. A peer-initiated exit records receipt of the peer request, local cleanup, then the session terminal. If protocol acknowledgement does not exist, say so; a local “request dispatched” event is not proof that the peer exited.

## Collaborative photo example

```text
App entry:
image_live.session_started { scope=feature_session, stage=entry, result=started, feature_session_id }
→ image_live.peer_entry_requested
→ image_live.peer_entry_result { result=success|failure }
→ image_live.session_active

Child upload while the session remains active:
photo_upload.started { scope=operation, trace_id, feature_session_id }
→ photo_upload.finished { scope=operation, stage=exit, result=success|failure|cancelled, trace_id, feature_session_id }

App exit:
image_live.exit_requested { initiator=app }
→ image_live.peer_exit_requested
→ image_live.peer_exit_result { result=success|failure }
→ image_live.session_finished { scope=feature_session, stage=exit, initiator=app, feature_session_id }

PC exit:
image_live.peer_exit_received { initiator=peer }
→ local cleanup
→ image_live.session_finished { scope=feature_session, stage=exit, initiator=peer, feature_session_id }
```

## Verification gate

Execute or structurally prove every matrix row using the project's existing test facilities. Verify App-initiated exit, peer-initiated exit, disconnect/lifecycle teardown when applicable, and a racing App/peer exit. The race must still emit one terminal. A completed child operation is not closure evidence for the feature session.

If any received exit trigger does not reach local cleanup, an App exit omits its required peer notification, or a started session has zero or multiple terminal events, report the feature instrumentation as incomplete. Do not report completion based only on entry/start logs or inner-operation terminals.
