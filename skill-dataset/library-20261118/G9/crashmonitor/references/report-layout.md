# CrashMonitor report directory layout

Reports live under `D:\CrashReports\<targetId>\`. Each event gets its own
subdirectory. Point the user at `report.md` first.

## Crash / deadlock event: `<time>-pid<PID>\`
| File | Meaning |
|---|---|
| `report.md` | Final diagnosis. Local placeholder first, then Codex CLI appends the Chinese root-cause analysis against project source. **Read this first.** |
| `*.dmp` | The captured dump (Full unless target set to Mini). |
| `metadata.json` | Event info: trigger type (`UnhandledException` / `Deadlock` / `ApplicationCrashDump` / `Manual`), target, PID, versions, dump size. |
| `procdump.log` | ProcDump capture log, including the `Trigger:` line. |
| `analysis-status.txt` | Debugger analysis progress/status. |
| debugger output (e.g. `cdb-*.txt`, `dotnet-dump-*.txt`) | Stacks, `!analyze -v`, locals/objects. |
| `wait-chain.json` | Deadlock only: the confirmed thread/lock wait-graph. |
| `codex-cli.log` | Codex CLI invocation log check here if `report.md` never fills in. |

## Diagnostic snapshot: `diagnostic-<time>-pid<PID>\`
| File | Meaning |
|---|---|
| `report.md` | Local conclusion; Codex read-only analysis appended when `AnalysisMode=CodexCli`. |
| `metadata.json` | Trigger thresholds and target info. |
| `timeline.json` | Rolling timeline of CPU, memory, I/O, handles, threads. |
| `process-snapshot.json` | Modules, threads, handles, network endpoints, direct children, system resources. |
| `handles.txt`, `listdlls.txt`, `tcpvcon.txt`, `pslist.txt` | Raw Sysinternals output scoped to the target PID only. |

## Interpreting `report.md` state
- **Filled diagnosis** done; summarize trigger type + key finding.
- **Only local placeholder ("analysis in progress")** the debugger
  or Codex step hasn't completed, or Codex isn't logged in. Check
  `analysis-status.txt` and `codex-cli.log`, and run `codex.cmd doctor`.

## Analyzer selection
- Native processes `cdb.exe` (`!analyze -v`, `.ecxr`, `kn`, `dv /t /v`, `dx`).
- .NET processes `dotnet-dump.exe` (`pe`, `clrstack -a`, `dumpstackobjects`,
  `dumpheap -stat`).
Reliable variables require: a Full dump, PDBs matching the exact build, and the
debugger being able to find those PDBs (EXE dir by default; extra dirs via
`SymbolPaths` in `config.json`).



