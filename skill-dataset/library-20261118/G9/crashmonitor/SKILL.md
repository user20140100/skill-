---
name: crashmonitor
description: >-
  Drive the CrashMonitor tool to monitor a local Windows program for crashes,
  hangs/deadlocks, or resource leaks, and to analyze crash dumps. Use this skill
  whenever the user wants to watch a Windows .exe for crashes, capture a dump
  when a program crashes or freezes, diagnose why a Windows process is hanging /
  eating CPU / leaking memory or handles, set up crash monitoring at login, or
  analyze an existing .dmp file - even if they don't say "CrashMonitor" by name.
  Triggers on phrases like "monitor crashes", "capture a dump", "program
  freezes", "deadlock", "memory leak", "analyze a dump", "why does this process
  hang". This skill only chooses and emits the correct CrashMonitor commands and
  reads its reports; it does not modify or fix the target program.
author: lixiang21514
version: 0.0.1
---

# CrashMonitor operator

CrashMonitor is a local, user-mode Windows crash monitor (.NET 8). It attaches
**only** to processes that are registered as targets **and** whose full EXE path
matches exactly, uses Sysinternals ProcDump to capture unhandled-exception
dumps, runs a native (`cdb.exe`) or .NET (`dotnet-dump.exe`) analyzer to extract
evidence, and then invokes the user's already-configured Codex CLI to write a
Chinese diagnostic report against the project source.

Your job with this skill is to pick the right workflow for the user's symptom
and emit the correct commands - not to reinvent monitoring or touch the target
program. The mechanics are deterministic; the value is choosing the right mode
and respecting the conventions below, because small mistakes (wrong path, Mini
instead of Full, forgetting `--pid`) silently produce *no* usable evidence.

## Prerequisites - CrashMonitor must already be installed

This skill only *drives* CrashMonitor; it does not ship it. Before anything else,
confirm the tool exists on this machine and learn where it lives - the paths below
are **defaults/examples, not fixed locations**. Never assume the author's machine
layout; ask the user or discover the real paths.

- **The CrashMonitor build.** It's a .NET 8 CLI that must be published to a
  `publish\CrashMonitor.exe` under its project directory. Ask the user for that
  install root (the author's is `D:\SoftWare\SysinternalsSuite\CrashMonitor`, but
  it can be anywhere). If the project source is present but not yet built, publish
  it from the project dir: `powershell -ExecutionPolicy Bypass -File .\scripts\Publish.ps1`.
  If the user doesn't have CrashMonitor at all, this skill can't run - they need to
  obtain the CrashMonitor project first; say so plainly.
  **GitLab repo:** `git@gitlab.gz.cvte.cn:lixiang21514/crashmonitor.git`
- **External tools it depends on.** Sysinternals **ProcDump**, a debugger
  (`cdb.exe` or `dotnet-dump.exe`), and a logged-in **Codex CLI**. These are the
  user's own installs; a skill can't bundle them.

### Discovering the install root

First prefer a path the user has already supplied. Otherwise, run these checks in
order and use the first matching executable:

```powershell
Get-Command CrashMonitor.exe -ErrorAction SilentlyContinue
Get-ChildItem -Path $env:USERPROFILE -Filter CrashMonitor.exe -Recurse -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match '\\publish\\CrashMonitor\.exe$' } |
  Select-Object -First 1 -ExpandProperty FullName
```

If neither finds it, ask the user for the CrashMonitor install root; do not search
every drive or assume the author-specific `D:` path.
Throughout this skill, `CrashMonitor.exe` means "the executable at the user's
install root" - run it from that directory as `.\publish\CrashMonitor.exe` or by
full path. **Always run `doctor` first** - it verifies ProcDump, the debuggers,
and Codex CLI, and tells you if anything is missing. Do not assume the environment
is ready.

## Default paths (overridable, per machine)

These are CrashMonitor's out-of-the-box defaults, set in its `config.json` - treat
them as where to *look first*, not as guaranteed locations, and read the actual
values from the install if in doubt:

- Config + logs: `D:\CrashMonitor` (`config.json`, `monitor.log`).
- Reports: `D:\CrashReports\<targetId>\<time-PID>\`.

## Pick the workflow by symptom

Read the user's symptom and map it to one path. When unsure which category
applies, ask one clarifying question rather than guessing - the modes capture
different evidence.

| User symptom | What to do |
|---|---|
| Program crashes / closes unexpectedly / throws unhandled exception | Register the target, then `run`. ProcDump `-e` captures the dump automatically on the next crash. |
| Program freezes / hangs / "stops responding" / deadlock | Register the target (deadlock detection is **on by default**). CrashMonitor confirms a real thread wait-cycle (WCT, then CDB `!cs -l -o`) before dumping - a briefly-busy app won't trigger a false dump. |
| High CPU / memory / handle / thread growth, suspected leak | Runtime diagnostics is on by default. For an immediate snapshot use `diagnose --target <id> --seconds <N> --reason <text>`. Note the caveats: this is sampling/snapshots, not proof of a leak root cause. |
| User already has a `.dmp` file | Resolve or register a target, then run `analyze <dmp> --target <id>` - no live process needed. |
| Wants monitoring to survive reboot | Run `scripts\Install-Autostart.ps1` (see Autostart caveat). |

For the full command surface (every flag, defaults, `target` subcommands,
diagnostics thresholds), read `references/cli.md`. For what each file in a report
directory means, read `references/report-layout.md`.

## Analyze an existing dump without a target

`analyze` requires a target ID but does not require the live monitor to run.
After discovering CrashMonitor and running `doctor`, use this decision path:

1. Run `target list`. If an existing target matches the dump's executable, use its ID:
   `.\publish\CrashMonitor.exe analyze '<path to .dmp>' --target <targetId>`.
2. If no target matches, ask for the exact executable path and project source root.
   Register that target, run `target list` to obtain its ID, then run `analyze`.
3. If the executable path or source root is unavailable, explain that this command
   cannot be run as documented. Do not invent a target path or start `run`.
## The standard setup sequence

1. `.\publish\CrashMonitor.exe doctor` - confirm prerequisites.
2. Register the target with its **full EXE path** and project source root:
   ```powershell
   .\publish\CrashMonitor.exe target add `
     --exe 'D:\Work\MyProject\bin\Debug\net8.0\MyProject.exe' `
     --project 'D:\Work\MyProject' `
     --name 'MyProject' `
     --dump Full `
     --diagnostics true
   ```
3. `.\publish\CrashMonitor.exe target list` - confirm it registered and get the target ID.
4. Foreground-verify before trusting it: `.\publish\CrashMonitor.exe run --seconds 60`.
5. For persistent monitoring, either leave `run` going or install autostart.

## Conventions that must be respected (the guardrails)

These are the mistakes that quietly waste the whole exercise. They matter more
than the command syntax itself.

- **Full EXE path, exact match only.** A process with the same name in a
  different directory is *not* monitored. Always get the real path the user is
  launching (from Task Manager, the shortcut, or the build output dir) - don't
  register `MyProject.exe` by bare name.
- **Keep `--dump Full` (the default).** Full dumps carry local variables and
  heap objects, which is the whole point of the later analysis. Only suggest
  `Mini` if the user explicitly accepts losing variable/object inspection (e.g.
  disk pressure).
- **Multiple instances of the same path need `--pid`.** When `target list`
  or the situation implies several processes share one EXE path, `diagnose`
  requires `--pid <PID>` to disambiguate.
- **Analysis is read-only and diagnostic.** The background Codex runs with a
  read-only sandbox and `-a never`; it will not kill the process, edit source,
  touch the registry/services, or apply a fix. Don't promise CrashMonitor will
  *repair* anything - it explains, you (or the user) fix.
- **Reports may contain secrets.** Full dumps can hold passwords/tokens in
  memory. Treat `D:\CrashReports` as sensitive; don't paste raw dump contents
  around, and keep the directory access-restricted.
- **Live target list reloads; global config does not.** `target add/disable/
  remove` take effect without restarting the monitor. Changing global sampling
  thresholds in `config.json` requires restarting the monitor process.
- **Autostart is login-triggered, not a boot service.** `Install-Autostart.ps1`
  registers an *at-logon* scheduled task for the current user, so it cannot
  catch crashes that happen before the user logs in, and (unless installed from
  an elevated shell) cannot monitor elevated apps or services. Say so plainly if
  the user's scenario is a pre-login / service crash rather than overstating
  coverage.

## Reading and reporting results

After a capture, the report directory contains `report.md` (the final Codex
diagnosis), `metadata.json`, the debugger output, and (for deadlocks)
`wait-chain.json`. Point the user at `report.md` first, then summarize the
trigger type and the debugger's key finding. If `report.md` only shows the local
placeholder ("analysis in progress") the Codex step hasn't finished or Codex
isn't logged in - check `codex-cli.log` and `codex.cmd doctor`. See
`references/report-layout.md` for the meaning of every file.




