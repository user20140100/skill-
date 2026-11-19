# 公司 Skill 库 Tier1 静态扫描汇总（--no-llm）

- 对象：G2 代码审查 / G4 需求 PRD / G9 日志诊断，共 37 个 skill
- 命令：`skillevaluator tier1 <path> --no-llm`（静态；LLM 语义安全扫描未开启）
- 说明：`安全` 只统计 Security/Code Risk/Secrets/Code Integrity 四类；PII 单独列出。

## G2（8 个）

- 总体通过：1/8；安全类通过：3/8

| Skill | 总体 | 安全 | PII | 依赖 | 质量分 | C/H/M/L | 关键 finding |
|---|---|---|---|---|---:|---|---|
| `bug-commit-analyzer` | failed | FAIL | passed | passed | 89.0 (B) | 0/1/7/8 | [high] Security Scan: Supply Chain: curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.gz.cvte.cn/api/v4/groups?search=%24GROUP" |  |
| `code-review` | failed | pass | failed | passed | 86.5 (B) | 0/1/5/10 | [high] PII Scan: Non-placeholder email address: git@gitlab.gz.cvte.cn |
| `code-review-and-teach` | failed | FAIL | failed | passed | 86.5 (B) | 0/5/6/13 | [high] Security Scan: Privilege Escalation: .env"; [high] PII Scan: Personal macOS user path: /Users/[^/ — 2 occurrences (SKILL.md line 111; references/review-checklist.md line 50); [high] PII Scan: Personal macOS user path: /Users/overleazhou/; [high] PII Scan: Personal macOS user path: /Users/xxx/ — 2 occurrences (SKILL.md lines 207, 208) |
| `cxx-style-review` | failed | FAIL | failed | passed | 84.8 (B) | 0/9/9/22 | [high] Security Scan: Prompt Injection: ‌; [high] Security Scan: Prompt Injection: ‌; [high] Security Scan: Prompt Injection: ‌; [high] Security Scan: Prompt Injection: ‌ |
| `diff-analysis-report` | failed | FAIL | failed | passed | 80.2 (B) | 0/1/336/18 | [high] PII Scan: Personal Windows user path: C:\Users\cvter — 2 occurrences (使用说明.md lines 52, 118) |
| `embedded-code-review` | incomplete | pass | passed | passed | 86.5 (B) | 0/0/5/9 |  |
| `local-code-review` | failed | FAIL | passed | passed | 89.0 (B) | 0/1/5/8 | [high] Security Scan: Privilege Escalation: Access Token |
| `mr-suggestion` | passed | pass | passed | passed | 82.0 (B) | 0/0/8/9 |  |

## G4（8 个）

- 总体通过：4/8；安全类通过：5/8

| Skill | 总体 | 安全 | PII | 依赖 | 质量分 | C/H/M/L | 关键 finding |
|---|---|---|---|---|---:|---|---|
| `BizSolution` | failed | FAIL | failed | passed | 78.8 (C) | 0/4/3/8 | [high] Security Scan: Tool Misuse: rm -rf ./BizSolution)",; [high] PII Scan: Personal macOS user path: /Users/malanjun/ — 2 occurrences (SKILL.md lines 450, 453) |
| `fullstack-feature-delivery` | failed | FAIL | passed | passed | 89.0 (B) | 0/2/7/11 | [high] Security Scan: Supply Chain: curl -s "https://get.sdkman.io" | bash; [high] Security Scan: Tool Misuse: | bash |
| `grill-requirements` | passed | pass | passed | passed | 86.5 (B) | 0/0/6/12 |  |
| `project-prd` | failed | FAIL | passed | passed | 77.0 (C) | 0/8/45/17 | [high] Security Scan: MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to crea; [high] Security Scan: MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to crea; [high] Security Scan: MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to crea; [high] Security Scan: MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to crea |
| `requirement-analysis-pro` | passed | pass | passed | passed | 78.0 (C) | 0/0/9/13 |  |
| `requirement-spec` | passed | pass | passed | passed | 86.5 (B) | 0/0/5/17 |  |
| `requirement_completion_skill` | failed | pass | passed | passed | 79.5 (C) | 0/2/2/7 |  |
| `requirements-analyst` | passed | pass | passed | passed | 84.8 (B) | 0/0/5/10 |  |

## G9（21 个）

- 总体通过：6/21；安全类通过：11/21

| Skill | 总体 | 安全 | PII | 依赖 | 质量分 | C/H/M/L | 关键 finding |
|---|---|---|---|---|---:|---|---|
| `android-log-analysis` | failed | FAIL | passed | passed | 90.2 (A) | 0/2/7/11 | [high] Security Scan: analysis-evasion: decode_xlog_py2.py (partial); [high] Security Scan: System Prompt Leakage: Output Rules |
| `aosp-log-analyzer` | incomplete | pass | passed | passed | 84.2 (B) | 0/0/6/10 |  |
| `banpai-log-diagnosis` | incomplete | pass | passed | passed | 84.8 (B) | 0/0/5/10 |  |
| `chrome-trace-analysis` | passed | pass | passed | passed | 81.8 (B) | 0/0/6/14 |  |
| `crashmonitor` | failed | pass | failed | passed | 86.0 (B) | 0/1/6/9 | [high] PII Scan: Non-placeholder email address: git@gitlab.gz.cvte.cn |
| `diagnostic-logging` | failed | FAIL | passed | passed | 80.5 (B) | 0/3/13/9 | [high] Security Scan: analysis-evasion: references/android-kotlin.md (partial); [high] Security Scan: Privilege Escalation: access token; [high] Security Scan: Output Handling:         success = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(path),  |
| `es-log-query` | failed | FAIL | passed | passed | 89.0 (B) | 0/6/8/10 | [high] Security Scan: Privilege Escalation: .env ; [high] Security Scan: Privilege Escalation: .env ; [high] Security Scan: Privilege Escalation: .env ; [high] Security Scan: Privilege Escalation: .env  |
| `general-problem-handling` | passed | pass | passed | passed | 72.8 (C) | 0/0/10/12 |  |
| `ios-crash-analysis` | passed | pass | passed | passed | 89.0 (B) | 0/0/5/8 |  |
| `jira-log-assistant` | failed | FAIL | passed | passed | 90.2 (A) | 0/2/8/8 | [high] Security Scan: Privilege Escalation: Access Token; [high] Security Scan: Supply Chain: curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" \
  "https://jira.cvte.com/rest/api/2/myself" | py |
| `merge-xbug-xlog` | failed | pass | failed | passed | 86.5 (B) | 0/1/5/11 | [high] PII Scan: Personal macOS user path: /Users/robinyeung/ |
| `mofang-troubleshooting` | failed | FAIL | failed | passed | 78.0 (C) | 2/2/10/10 | [high] Security Scan: Supply Chain: curl -sSL https://mom.seewo.com/cli/install | bash; [high] Security Scan: Tool Misuse: | bash; [critical] PII Scan: Hardcoded secret/credential in code: [REDACTED]; [critical] Secrets Detection: Detected a Generic API Key, potentially exposing access to various services and sensitive operations. in scripts/wise.py |
| `qa-skill` | passed | pass | passed | passed | 76.5 (C) | 0/0/7/11 |  |
| `qa-troubleshooting-router` | failed | FAIL | passed | passed | 77.8 (C) | 1/0/8/18 | [critical] Security Scan: Data Flow: opener.open(request, timeout=3) |
| `service-stability-check` | passed | pass | passed | passed | 82.5 (B) | 0/0/6/11 |  |
| `third-party-sync-troubleshooting` | passed | pass | passed | passed | 86.5 (B) | 0/0/5/9 |  |
| `usb-diag` | failed | pass | passed | passed | 87.2 (B) | 0/1/5/20 |  |
| `windbg-dump-analysis` | MISSING | - | - | - | - | - | - |
| `xbug` | MISSING | - | - | - | - | - | - |
| `yunban-log-diagnosis` | MISSING | - | - | - | - | - | - |
| `zipkin-trace-lookup` | MISSING | - | - | - | - | - | - |

