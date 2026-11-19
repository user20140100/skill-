#!/usr/bin/env python3
"""Extract privacy-bounded diagnostic evidence from structured application logs."""

from __future__ import annotations

import argparse
import gzip
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, TextIO


ENVIRONMENT_EVENT = "runtime.process_started"
ENVIRONMENT_CHECKPOINT = "ENV-001"
COMMON_REQUIRED_FIELDS = ("event", "checkpoint", "module", "stage", "result")
TERMINAL_RESULTS = frozenset(("success", "failure", "cancelled"))
FEATURE_SESSION_SCOPE = "feature_session"
OPERATION_SCOPE = "operation"
ENVIRONMENT_FIELDS = (
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
)
ALLOWED_FIELDS = frozenset(
    COMMON_REQUIRED_FIELDS
    + ENVIRONMENT_FIELDS
    + (
        "timestamp",
        "time",
        "ts",
        "pid",
        "tid",
        "level",
        "scope",
        "feature_session_id",
        "trace_id",
        "parent_trace_id",
        "initiator",
        "error_code",
        "retry_count",
        "retry",
        "fallback",
        "cancellation_kind",
        "dependency",
        "status_class",
        "count",
        "size_category",
        "reason",
        "duration_ms",
    )
)
SUPPORTED_SUFFIXES = frozenset((".log", ".txt", ".json", ".jsonl", ".out", ".gz"))
LOGCAT_PREFIX = re.compile(
    r"^(?P<timestamp>\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)"
    r"\s+(?P<pid>\d+)\s+(?P<tid>\d+)\s+[VDIWEF]\b"
)
ISO_PREFIX = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)")


class AnalysisError(ValueError):
    """Raised when analysis inputs or outputs are unsafe or unusable."""


def _scalar(value: Any) -> str | None:
    if value is None or isinstance(value, (dict, list, tuple, set)):
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _extract_object(line: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", line):
        try:
            candidate, _ = decoder.raw_decode(line[match.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            fields = candidate.get("fields")
            merged = dict(fields) if isinstance(fields, dict) else {}
            merged.update({key: value for key, value in candidate.items() if key != "fields"})
            if isinstance(merged.get("event"), str):
                return merged
    return None


def _normalize_event(raw: dict[str, Any], line: str, source: str, line_number: int) -> dict[str, str]:
    event: dict[str, str] = {"source": source, "line": str(line_number)}
    for key in ALLOWED_FIELDS:
        value = _scalar(raw.get(key))
        if value is not None:
            event[key] = value

    if "timestamp" not in event:
        for alias in ("time", "ts"):
            if alias in event:
                event["timestamp"] = event.pop(alias)
                break

    logcat_match = LOGCAT_PREFIX.match(line)
    if logcat_match:
        event.setdefault("timestamp", logcat_match.group("timestamp"))
        event.setdefault("pid", logcat_match.group("pid"))
        event.setdefault("tid", logcat_match.group("tid"))
    else:
        iso_match = ISO_PREFIX.match(line)
        if iso_match:
            event.setdefault("timestamp", iso_match.group("timestamp"))
    return event


def _discover_files(input_path: Path) -> list[Path]:
    if not input_path.exists():
        raise AnalysisError(f"input path does not exist: {input_path}")
    if input_path.is_file():
        return [input_path]
    if not input_path.is_dir():
        raise AnalysisError(f"input path is not a file or directory: {input_path}")
    files = sorted(
        path
        for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        raise AnalysisError(f"no supported log files found under: {input_path}")
    return files


def _source_name(path: Path, input_path: Path) -> str:
    if input_path.is_file():
        return path.name
    return path.relative_to(input_path).as_posix()


def _open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", errors="replace")
    return path.open(mode="rt", encoding="utf-8", errors="replace")


def _matches_feature(event_name: str, feature: str | None) -> bool:
    if event_name == ENVIRONMENT_EVENT or feature is None:
        return True
    normalized = feature.strip().rstrip(".")
    return bool(normalized) and (event_name == normalized or event_name.startswith(normalized + "."))


def _finding(severity: str, code: str, message: str, evidence: str | None = None) -> dict[str, str]:
    result = {"severity": severity, "code": code, "message": message}
    if evidence is not None:
        result["evidence"] = evidence
    return result


def _event_reference(event: dict[str, str]) -> str:
    return f"{event['source']}:{event['line']}"


def _terminal_events(
    events: list[dict[str, str]], expected_scope: str = OPERATION_SCOPE
) -> list[dict[str, str]]:
    """Return exits for one lifecycle scope, excluding child/intermediate checkpoints."""
    return [
        event
        for event in events
        if event.get("stage") == "exit"
        and event.get("result") in TERMINAL_RESULTS
        and (
            event.get("scope") == expected_scope
            or (expected_scope == OPERATION_SCOPE and not event.get("scope"))
        )
    ]


def _is_started(event: dict[str, str], expected_scope: str = OPERATION_SCOPE) -> bool:
    scope_matches = event.get("scope") == expected_scope or (
        expected_scope == OPERATION_SCOPE and not event.get("scope")
    )
    return scope_matches and event.get("stage") == "entry" and event.get("result") == "started"


def _trace_summary(
    trace_id: str,
    feature_session_id: str | None,
    events: list[dict[str, str]],
    environment_session_ids: set[str],
    session_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    terminal_events = _terminal_events(events)
    sorted_session_ids = sorted(environment_session_ids)
    sessions = [session_by_id[item] for item in sorted_session_ids if item in session_by_id]
    process_names = sorted(
        {
            name
            for name in (
                *(event.get("process_name") for event in events),
                *(session.get("process_name") for session in sessions),
            )
            if name and name != "unknown"
        }
    )
    return {
        "trace_id": trace_id,
        "feature_session_id": feature_session_id or "unknown",
        "process_name": process_names[0] if len(process_names) == 1 else (
            ",".join(process_names) if process_names else "unknown"
        ),
        "session_id": sorted_session_ids[0] if len(sorted_session_ids) == 1 else (
            "multiple" if sorted_session_ids else "unknown"
        ),
        "environment_session_ids": sorted_session_ids,
        "first_timestamp": next((event["timestamp"] for event in events if event.get("timestamp")), "unknown"),
        "terminal_result": terminal_events[0]["result"] if len(terminal_events) == 1 else (
            "ambiguous" if terminal_events else "unknown"
        ),
        "terminal_event_count": len(terminal_events),
        "events": events,
    }


def _feature_session_summary(
    feature_session_id: str,
    events: list[dict[str, str]],
    environment_session_ids: set[str],
    build_identity: tuple[str, ...],
) -> dict[str, Any]:
    terminal_events = _terminal_events(events, FEATURE_SESSION_SCOPE)
    return {
        "feature_session_id": feature_session_id,
        "build_identity": list(build_identity),
        "environment_session_ids": sorted(environment_session_ids),
        "first_timestamp": next((event["timestamp"] for event in events if event.get("timestamp")), "unknown"),
        "terminal_result": terminal_events[0]["result"] if len(terminal_events) == 1 else (
            "ambiguous" if terminal_events else "unknown"
        ),
        "terminal_event_count": len(terminal_events),
        "events": events,
    }


def _build_identity(
    environment_session_id: str | None,
    session_by_id: dict[str, dict[str, Any]],
) -> tuple[str, ...]:
    if not environment_session_id or environment_session_id not in session_by_id:
        return ("unknown",)
    environment = session_by_id[environment_session_id]["environment"]
    return tuple(
        environment.get(field, "unknown")
        for field in ("app_id", "version_code", "build_flavor", "build_type", "vcs_commit")
    )


def analyze_path(input_path: str | Path, feature: str | None = None) -> dict[str, Any]:
    root = Path(input_path).expanduser().resolve()
    files = _discover_files(root)
    events: list[dict[str, str]] = []
    lines_scanned = 0
    parse_errors: list[str] = []

    for path in files:
        source = _source_name(path, root)
        try:
            with _open_text(path) as handle:
                for line_number, line in enumerate(handle, start=1):
                    lines_scanned += 1
                    raw = _extract_object(line)
                    if raw is None:
                        continue
                    event = _normalize_event(raw, line, source, line_number)
                    if _matches_feature(event["event"], feature):
                        events.append(event)
        except (OSError, EOFError) as error:
            parse_errors.append(f"{source}: unreadable ({error.__class__.__name__})")

    findings: list[dict[str, str]] = []
    sessions: list[dict[str, Any]] = []
    session_by_id: dict[str, dict[str, Any]] = {}
    session_by_source_pid: dict[tuple[str, str], str] = {}
    source_sessions: dict[str, list[str]] = {}
    event_sessions: dict[int, str | None] = {}

    for index, event in enumerate(events):
        missing_common = [field for field in COMMON_REQUIRED_FIELDS if not event.get(field)]
        if missing_common:
            findings.append(
                _finding(
                    "warning",
                    "schema_incomplete",
                    "Structured event is missing required fields: " + ", ".join(missing_common),
                    _event_reference(event),
                )
            )

        event_scope = event.get("scope", OPERATION_SCOPE)
        if event_scope == FEATURE_SESSION_SCOPE and _is_started(event, FEATURE_SESSION_SCOPE):
            if not event.get("feature_session_id"):
                findings.append(
                    _finding(
                        "error",
                        "feature_session_started_without_id",
                        "A started feature session has no feature_session_id, so closure cannot be verified.",
                        _event_reference(event),
                    )
                )
        elif event_scope == OPERATION_SCOPE and _is_started(event, OPERATION_SCOPE):
            if not event.get("trace_id"):
                findings.append(
                    _finding(
                        "error",
                        "started_event_without_trace_id",
                        "A started operation has no trace_id, so closure cannot be verified.",
                        _event_reference(event),
                    )
                )

        if event.get("event", "").endswith(".started") and event_scope in (
            FEATURE_SESSION_SCOPE,
            OPERATION_SCOPE,
        ):
            expected_scope = FEATURE_SESSION_SCOPE if event_scope == FEATURE_SESSION_SCOPE else OPERATION_SCOPE
            if not _is_started(event, expected_scope):
                findings.append(
                    _finding(
                        "warning",
                        "started_event_contract_violation",
                        "A lifecycle started event must use stage=entry and result=started for its declared scope.",
                        _event_reference(event),
                    )
                )

        if event.get("event") == ENVIRONMENT_EVENT:
            session_id = _event_reference(event)
            missing_environment = [field for field in ENVIRONMENT_FIELDS if not event.get(field)]
            session = {
                "session_id": session_id,
                "source": event["source"],
                "line": event["line"],
                "timestamp": event.get("timestamp", "unknown"),
                "pid": event.get("pid", "unknown"),
                "process_name": event.get("process_name", "unknown"),
                "environment": {field: event.get(field, "unknown") for field in ENVIRONMENT_FIELDS},
                "missing_fields": missing_environment,
            }
            sessions.append(session)
            session_by_id[session_id] = session
            source_sessions.setdefault(event["source"], []).append(session_id)
            if event.get("pid"):
                session_by_source_pid[(event["source"], event["pid"])] = session_id
            event_sessions[index] = session_id
            if event.get("checkpoint") != ENVIRONMENT_CHECKPOINT:
                findings.append(
                    _finding(
                        "warning",
                        "environment_checkpoint_mismatch",
                        f"Process-start event does not use {ENVIRONMENT_CHECKPOINT}.",
                        session_id,
                    )
                )
            if missing_environment:
                findings.append(
                    _finding(
                        "warning",
                        "environment_incomplete",
                        "Environment event is missing fields: " + ", ".join(missing_environment),
                        session_id,
                    )
                )
            continue

        session_id = None
        if event.get("pid"):
            session_id = session_by_source_pid.get((event["source"], event["pid"]))
        if session_id is None and len(source_sessions.get(event["source"], ())) == 1:
            session_id = source_sessions[event["source"]][0]
        event_sessions[index] = session_id
        if session_id is None:
            findings.append(
                _finding(
                    "info",
                    "event_without_environment",
                    "Event cannot be paired with a process-start environment session.",
                    _event_reference(event),
                )
            )

        if event.get("result") == "failure" or event.get("error_code"):
            findings.append(
                _finding(
                    "error",
                    "operation_failure",
                    "A structured event reports a failure or error classification.",
                    _event_reference(event),
                )
            )
        elif event.get("result") == "cancelled":
            findings.append(
                _finding(
                    "info",
                    "operation_cancelled",
                    "A structured event reports cancellation.",
                    _event_reference(event),
                )
            )

    if not sessions:
        findings.insert(
            0,
            _finding(
                "warning",
                "environment_missing",
                f"No {ENVIRONMENT_EVENT} / {ENVIRONMENT_CHECKPOINT} evidence was found.",
            ),
        )

    trace_groups: dict[tuple[str, str | None, tuple[str, ...]], list[dict[str, str]]] = {}
    trace_environment_sessions: dict[
        tuple[str, str | None, tuple[str, ...]], set[str]
    ] = {}
    feature_session_groups: dict[tuple[str, tuple[str, ...]], list[dict[str, str]]] = {}
    feature_environment_sessions: dict[tuple[str, tuple[str, ...]], set[str]] = {}
    uncorrelated: list[dict[str, str]] = []
    for index, event in enumerate(events):
        if event.get("event") == ENVIRONMENT_EVENT:
            continue
        session_id = event_sessions.get(index)
        trace_id = event.get("trace_id")
        feature_session_id = event.get("feature_session_id")
        build_identity = _build_identity(session_id, session_by_id)
        if trace_id and event.get("scope") != FEATURE_SESSION_SCOPE:
            trace_key = (trace_id, feature_session_id, build_identity)
            trace_groups.setdefault(trace_key, []).append(event)
            if session_id:
                trace_environment_sessions.setdefault(trace_key, set()).add(session_id)
        if feature_session_id:
            feature_key = (feature_session_id, build_identity)
            feature_session_groups.setdefault(feature_key, []).append(event)
            if session_id:
                feature_environment_sessions.setdefault(feature_key, set()).add(session_id)
        if session_id is None or (not trace_id and not feature_session_id):
            uncorrelated.append(event)

    traces = [
        _trace_summary(
            trace_id,
            feature_session_id,
            grouped_events,
            trace_environment_sessions.get((trace_id, feature_session_id, build_identity), set()),
            session_by_id,
        )
        for (trace_id, feature_session_id, build_identity), grouped_events in trace_groups.items()
    ]
    traces.sort(key=lambda trace: (trace["first_timestamp"], trace["trace_id"], trace["session_id"]))
    for trace in traces:
        has_started_event = any(_is_started(event, OPERATION_SCOPE) for event in trace["events"])
        if has_started_event and trace["terminal_event_count"] == 0:
            findings.append(
                _finding(
                    "warning",
                    "trace_without_terminal_event",
                    "A started trace has no observed stage=exit success, failure, or cancellation event.",
                    trace["trace_id"],
                )
            )
        elif has_started_event and trace["terminal_event_count"] > 1:
            findings.append(
                _finding(
                    "error",
                    "trace_multiple_terminal_events",
                    "A started trace has more than one stage=exit terminal event.",
                    trace["trace_id"],
                )
            )

    feature_sessions = [
        _feature_session_summary(
            feature_session_id,
            grouped_events,
            feature_environment_sessions.get((feature_session_id, build_identity), set()),
            build_identity,
        )
        for (feature_session_id, build_identity), grouped_events in feature_session_groups.items()
    ]
    feature_sessions.sort(
        key=lambda session: (session["first_timestamp"], session["feature_session_id"])
    )
    for feature_session in feature_sessions:
        has_started_event = any(
            _is_started(event, FEATURE_SESSION_SCOPE) for event in feature_session["events"]
        )
        if has_started_event and feature_session["terminal_event_count"] == 0:
            findings.append(
                _finding(
                    "warning",
                    "feature_session_without_terminal_event",
                    "A started feature session has no observed feature-session stage=exit terminal event.",
                    feature_session["feature_session_id"],
                )
            )
        elif has_started_event and feature_session["terminal_event_count"] > 1:
            findings.append(
                _finding(
                    "error",
                    "feature_session_multiple_terminal_events",
                    "A started feature session has more than one feature-session stage=exit terminal event.",
                    feature_session["feature_session_id"],
                )
            )
    limitations = [
        "The parser reports structured evidence and does not claim a root cause.",
        "An absent event may mean an unexecuted path, filtering, truncation, collection loss, or missing instrumentation.",
        "Expected checkpoint order requires the feature Checkpoint Manifest or source-assisted analysis.",
    ]
    limitations.extend(parse_errors)
    return {
        "schema_version": "2",
        "input": {"kind": "file" if root.is_file() else "directory", "feature": feature or "all"},
        "summary": {
            "files_scanned": len(files),
            "lines_scanned": lines_scanned,
            "structured_events": len(events),
            "environment_sessions": len(sessions),
            "feature_sessions": len(feature_sessions),
            "traces": len(traces),
            "findings": len(findings),
        },
        "environment_sessions": sessions,
        "feature_sessions": feature_sessions,
        "traces": traces,
        "uncorrelated_events": uncorrelated,
        "findings": findings,
        "limitations": limitations,
    }


def _atomic_write_json(output: Path, bundle: dict[str, Any]) -> None:
    if output.exists() and output.is_symlink():
        raise AnalysisError("output must not be a symlink")
    if not output.parent.is_dir():
        raise AnalysisError(f"output parent does not exist: {output.parent}")
    payload = (json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output.parent, prefix=".diagnostic-log-analysis-", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, output)
        temporary_name = None
    except OSError as error:
        raise AnalysisError(f"could not write output: {error}") from error
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Structured log file or directory")
    parser.add_argument("--feature", help="Optional stable event prefix, for example file_upload")
    parser.add_argument("--output", help="Write the JSON evidence bundle to this file")
    arguments = parser.parse_args(argv)
    try:
        bundle = analyze_path(arguments.input, feature=arguments.feature)
        if arguments.output:
            output = Path(arguments.output).expanduser().resolve()
            if output == Path(arguments.input).expanduser().resolve():
                raise AnalysisError("output must not overwrite the input")
            _atomic_write_json(output, bundle)
            print(json.dumps({"output": str(output), "summary": bundle["summary"]}, ensure_ascii=False))
        else:
            print(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True))
    except AnalysisError as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
