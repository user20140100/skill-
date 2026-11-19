---
name: ios-crash-analysis
description: >-
  Use when receiving iOS/Mac crash reports (.crash or .txt files) that need
  symbolication and root cause analysis. Triggers when user mentions crash,崩溃,
  crash log, crash report, or provides a crash file to analyze.
author: hejiangshan
version: 0.0.1
---

# iOS Crash Analysis

Symbolicate iOS/Mac crash reports and analyze root cause with project code context.

## Checklist

Follow these steps in order. Each step MUST be completed before proceeding.

1. **Collect crash file path** — ask user for the .crash/.txt file path
2. **Collect dSYM path** — ask user for the dSYM file path
3. **Parse crash report** — extract crash thread, exception type, and stack frames
4. **Identify binary and load address** — find the app binary name and load address from the Binary Images section
5. **Symbolicate** — use `atos` to resolve symbol addresses
6. **Analyze root cause** — read relevant source files and identify the crash cause
7. **Output results** — present analysis in terminal AND write a markdown report file

## Step 1: Collect Inputs

Ask user for two paths (one at a time):

1. **Crash report file** — `.crash` or `.txt` file from tester
2. **dSYM file** — `.dSYM` bundle path (the `.app.dSYM` directory)

Validate both paths exist before proceeding.

## Step 2: Parse Crash Report

Read the crash file and extract:

- **Exception Type** (e.g., `EXC_BAD_ACCESS`, `SIGABRT`)
- **Exception Codes**
- **Termination Reason** (if present)
- **Crashed Thread** number and its full stack trace
- **Binary Images** section — find the app binary entry to get:
  - Binary name
  - Load address (e.g., `0x100abc000`)
  - Architecture (arm64)
  - UUID

Key parsing rules:
- The crashed thread is marked with `(crashed)` or is the thread listed after `Triggered by Thread:`
- Stack frames look like: `N  BinaryName  0xADDRESS  0xLOADADDR + offset`
- Only symbolicate frames belonging to the app binary (not system frameworks)

## Step 3: Symbolicate with atos

For each unsymbolicated app frame, run:

```bash
xcrun atos -o <path-to-dSYM>/Contents/Resources/DWARF/<binary-name> -arch arm64 -l <load-address> <frame-address>
```

Example:
```bash
xcrun atos -o /path/to/App.app.dSYM/Contents/Resources/DWARF/App -arch arm64 -l 0x100abc000 0x100abcdef
```

Batch multiple addresses in one call for efficiency:
```bash
xcrun atos -o <DWARF-path> -arch arm64 -l <load-address> <addr1> <addr2> <addr3> ...
```

If symbolication fails:
- Verify dSYM UUID matches crash report UUID: `dwarfdump --uuid <dSYM-path>`
- Check architecture matches
- Report mismatch to user

## Step 4: Analyze Root Cause

After symbolication:

1. **Identify the crash point** — the top app frame in the crashed thread
2. **Read source code** — use grep/view to find and read the relevant source files
3. **Trace the call chain** — follow the symbolicated stack to understand the execution flow
4. **Identify the bug** — determine why the crash occurred:
   - Null pointer / released object access (EXC_BAD_ACCESS)
   - Unrecognized selector (SIGABRT + NSInvalidArgumentException)
   - Array/dictionary out of bounds
   - Threading issue (accessing UI from background thread, race condition)
   - Stack overflow (deep recursion)
   - Other
5. **Propose fix** — suggest specific code changes with file paths and line references

## Step 5: Output Results

### Terminal Output

Present a concise summary:
- Exception type and crash location
- Root cause explanation
- Suggested fix

### Report File

Write a markdown report to the project's docs directory:

**Path**: `docs/crash-analysis/YYYY-MM-DD-<brief-description>.md`

**Report structure**:
```markdown
# Crash Analysis Report

## Summary
- **Date**: YYYY-MM-DD
- **Exception Type**: ...
- **Crash Location**: File:Line — Method

## Symbolicated Stack Trace
(Crashed thread only, with symbolicated frames)

## Root Cause Analysis
(Detailed explanation of why the crash occurred)

## Relevant Code
(Key code snippets from the crash location)

## Suggested Fix
(Specific code changes to resolve the issue)
```

## Common Pitfalls

- **Wrong dSYM**: Always verify UUID match between crash report and dSYM
- **Wrong architecture**: Use `arm64` for device crashes, `x86_64` for simulator
- **Load address**: Must use the load address from the specific crash report, not a hardcoded value
- **Multiple binaries**: App extensions have separate dSYMs — check which binary crashed
- **Stripped frames**: Some frames may show `<redacted>` in system frameworks — focus on app frames
