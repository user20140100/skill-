#!/usr/bin/env python3
"""Install the Diagnostic Logging managed rules block in a project AGENTS.md."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import stat
import sys
import tempfile


MANAGED_START = "<!-- DIAGNOSTIC_LOGGING_RULES_START schema=1 -->"
MANAGED_END = "<!-- DIAGNOSTIC_LOGGING_RULES_END -->"


@dataclass(frozen=True)
class InitResult:
    status: str
    target: Path
    warnings: tuple[str, ...]


class InitializationError(RuntimeError):
    """Raised when initialization cannot safely modify a project."""


def validate_project_root(raw_path: str) -> Path:
    """Return a safe, resolved project directory or raise InitializationError."""
    candidate = Path(raw_path).expanduser()
    if candidate.is_symlink():
        raise InitializationError("project root must not be a symlink")
    if not candidate.exists():
        raise InitializationError("project root does not exist")

    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise InitializationError("project root must be a directory")
    if resolved == Path(resolved.anchor):
        raise InitializationError("filesystem root is not a valid project root")
    if resolved == Path.home().resolve():
        raise InitializationError("home directory is not a valid project root")
    return resolved


def render_managed_block(rules_text: str) -> str:
    """Render the complete, newline-terminated block owned by this skill."""
    return f"{MANAGED_START}\n{rules_text.strip()}\n{MANAGED_END}\n"


def _read_rules(skill_root: Path) -> str:
    rules_path = skill_root / "assets" / "agents-rules.md"
    try:
        rules_text = rules_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise InitializationError("bundled diagnostic logging rules are missing") from error
    except OSError as error:
        raise InitializationError(f"could not read bundled rules: {error}") from error
    if not rules_text.strip():
        raise InitializationError("bundled diagnostic logging rules are blank")
    return rules_text


def _replace_or_append(existing: str, block: str) -> str:
    start_count = existing.count(MANAGED_START)
    end_count = existing.count(MANAGED_END)
    if start_count == 0 and end_count == 0:
        if not existing:
            return block
        return existing.rstrip("\n") + "\n\n" + block
    if start_count != 1 or end_count != 1:
        raise InitializationError("managed markers must appear zero times or once each")

    start_index = existing.index(MANAGED_START)
    end_index = existing.index(MANAGED_END)
    if start_index > end_index:
        raise InitializationError("managed start marker must precede the end marker")
    end_index += len(MANAGED_END)
    if existing[end_index : end_index + 1] == "\n":
        end_index += 1
    return existing[:start_index] + block + existing[end_index:]


def _atomic_write(target: Path, content: bytes, existing_mode: int | None) -> None:
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=".diagnostic-logging-", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        if existing_mode is not None:
            os.chmod(temporary_name, existing_mode)
        os.replace(temporary_name, target)
        temporary_name = None
    except OSError as error:
        raise InitializationError(f"could not write {target}: {error}") from error
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


def initialize_project(project_root: str, skill_root: Path | None = None) -> InitResult:
    """Create or update only this skill's managed block in project AGENTS.md."""
    root = validate_project_root(project_root)
    package_root = skill_root if skill_root is not None else Path(__file__).resolve().parents[1]
    block = render_managed_block(_read_rules(package_root))
    target = root / "AGENTS.md"
    warnings: tuple[str, ...] = ()
    if (root / "AGENT.md").exists():
        warnings = (
            "Preserved singular AGENT.md; standard plural AGENTS.md already exists."
            if target.exists()
            else "Preserved singular AGENT.md; created standard plural AGENTS.md.",
        )
    if target.is_symlink():
        raise InitializationError("AGENTS.md must not be a symlink")

    existed = target.exists()
    try:
        existing_bytes = target.read_bytes() if existed else b""
        existing = existing_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InitializationError("AGENTS.md must be UTF-8 text") from error
    except OSError as error:
        raise InitializationError(f"could not read {target}: {error}") from error

    desired_bytes = _replace_or_append(existing, block).encode("utf-8")
    if existed and desired_bytes == existing_bytes:
        return InitResult("unchanged", target, warnings)

    existing_mode = stat.S_IMODE(target.stat().st_mode) if existed else None
    _atomic_write(target, desired_bytes, existing_mode)
    return InitResult("updated" if existed else "created", target, warnings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Path to the target project root")
    arguments = parser.parse_args(argv)
    try:
        result = initialize_project(arguments.project_root)
    except InitializationError as error:
        print(error, file=sys.stderr)
        return 2
    payload = asdict(result)
    payload["target"] = str(result.target)
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
