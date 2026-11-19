# CrashMonitor CLI reference

All commands run from `D:\SoftWare\SysinternalsSuite\CrashMonitor` as
`.\publish\CrashMonitor.exe <command>`, or by full path to the exe.

## Table of contents
- [doctor](#doctor)
- [target add](#target-add)
- [target list / disable / remove](#target-management)
- [run](#run)
- [diagnose](#diagnose)
- [analyze](#analyze)
- [Autostart scripts](#autostart-scripts)
- [Diagnostics thresholds](#diagnostics-thresholds)
- [Deadlock vs leak triggering](#deadlock-vs-leak-triggering)

## doctor
Environment self-check: locates `procdump64.exe`, `cdb.exe` / `dotnet-dump.exe`,
and verifies Codex CLI availability. Run before first use and after installing
Debugging Tools for Windows.
```powershell
.\publish\CrashMonitor.exe doctor
codex.cmd doctor   # separately confirm Codex CLI is logged in
```

## target add
Register a process to monitor. The EXE path must be the **full** path of the
actually-running executable; same-named processes elsewhere are ignored.
```powershell
.\publish\CrashMonitor.exe target add `
  --exe '<full path to .exe>' `
  --project '<source root>' `
  --name '<display name>' `
  --dump Full `
  --diagnostics true
```
Flags:
- `--exe` (required): full EXE path, exact-match.
- `--project`: source root Codex reads for analysis.
- `--name`: display name for the target.
- `--dump Full|Mini`: **Full is default**; needed for variables/heap objects.
- `--diagnostics true|false`: runtime resource sampling (default true).
- `--deadlock true|false`: deadlock detection (default true).
- `--deadlock-poll <seconds>` / `--deadlock-confirmations <n>`: tune deadlock
  confirmation frequency/count.

## target management
```powershell
.\publish\CrashMonitor.exe target list                 # show targets + IDs
.\publish\CrashMonitor.exe target disable <targetId>   # stop monitoring, keep reports
.\publish\CrashMonitor.exe target remove  <targetId>   # remove target, keep reports
```
Target list reloads live no monitor restart needed.

## run
Start the monitor in the foreground. It only acts when a registered target
process is actually present.
```powershell
.\publish\CrashMonitor.exe run                # runs until stopped
.\publish\CrashMonitor.exe run --seconds 60   # runs 60s then exits good for verification
```

## diagnose
Take an immediate short forensic snapshot of a running target.
```powershell
.\publish\CrashMonitor.exe diagnose --target <targetId> --seconds 10 --reason manual-check
# add --pid <PID> when multiple processes share the same EXE path
```
Output: `D:\CrashReports\<targetId>\diagnostic-<time>-pid<PID>\report.md` plus
`timeline.json`, `process-snapshot.json`, and raw tool outputs
(`handles.txt`, `listdlls.txt`, `tcpvcon.txt`, `pslist.txt`).

## analyze
Analyze an existing dump without a live process.
```powershell
.\publish\CrashMonitor.exe analyze '<path to .dmp>' --target <targetId>
```

## Autostart scripts
```powershell
# elevated PowerShell recommended for elevated apps/services
powershell -ExecutionPolicy Bypass -File .\scripts\Install-Autostart.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\Uninstall-Autostart.ps1
```
Registers/removes an **at-logon** scheduled task named `CrashMonitor` for the
current user, RestartCount 3. Login-triggered not a boot-time service. Admin
install Highest run level (can monitor elevated apps); non-admin Limited
(current-user apps only). Uninstall keeps config and reports. For pre-login or
service monitoring, a dedicated Windows Service deployment is required instead.

## Diagnostics thresholds
Defaults live in `D:\CrashMonitor\config.json` under `Diagnostics`. Set any
threshold to `0` to disable that trigger; `Diagnostics.Enabled=false` disables
all; per-target `MonitorDiagnostics` toggles one target. **Changing global
sampling config requires restarting the monitor process** (the target list
itself still reloads dynamically).

| Config | Default | Meaning |
|---|---:|---|
| `SampleSeconds` / `DeepSampleSeconds` | 2 / 30 s | light / deep sampling period |
| `ToolTimeoutSeconds` | 10 s | max time per Sysinternals helper |
| `RollingWindowSeconds` / `AlertCooldownSeconds` | 60 / 300 s | growth window / alert cooldown |
| `CpuPercentThreshold` | 90% | CPU normalized across logical processors |
| `WorkingSetMbThreshold` / `PrivateMemoryMbThreshold` | 2048 / 2048 MB | working set / private memory |
| `HandleCountThreshold` / `HandleGrowthThreshold` | 2000 / 300 | handle total / window growth |
| `FileHandleCountThreshold` / `RegistryHandleCountThreshold` | 1000 / 500 | file / registry-key handles |
| `ThreadCountThreshold` / `ThreadGrowthThreshold` | 200 / 50 | thread total / window growth |
| `ModuleCountThreshold` / `ModuleGrowthThreshold` | 400 / 25 | module total / growth |
| `ChildProcessCountThreshold` | 5 | direct child processes |
| `NetworkEndpointCountThreshold` / `NetworkEndpointGrowthThreshold` | 200 / 100 | TCP/UDP endpoints total / growth |
| `IoBytesPerSecondThreshold` | 100 MB/s | process I/O throughput |
| `MaximumEvidenceItems` | 500 | max evidence items per category |

## Deadlock vs leak triggering
- **Unhandled exceptions** captured by ProcDump `-e`.
- **Native critical-section deadlock** WCT first checks whether threads stay
  blocked; if WCT can't expand owners, a non-invasive CDB `!cs -l -o` builds a
  lock wait-graph. A dump is captured **only** when a cycle is confirmed.
- **Leaks** a single allocation followed by normal exit is not a crash and is
  never reported as a fake crash. Handle/thread growth is a *lead*, not a root
  cause; confirming a memory leak still needs UMDH / Application Verifier / CRT
  heap evidence.



