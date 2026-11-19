# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:19 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 14 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 38 unique findings (7 medium) / 39 occurrences / 39 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2173d3d6eb4577234bd5` | MEDIUM | This is a true privacy/security-quality vulnerability, although not malicious code. Chrome Performance traces and genera | 1 | Security Scan |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-6b66555d1029e567b59c` | LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | 2 | Unicode Smuggling Detection |
| `SEF-0f13c9a2b82dbd00de46` | LOW | Unexpected 'examples.md' in skill root | 1 | Schema &amp; Repository Governance |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| ... | | *28 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| chrome-trace-analysis | 81.8 | B | script-based | 80.0 | 80.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'chrome-trace-analysis'
- [OK] **naming_convention**: Folder name 'chrome-trace-analysis' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (94/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'chrome-trace-analysis'

**Non-blocking findings: 8**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/chrome-trace-analysis</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | Unexpected 'examples.md' in skill root | <code>/skills/library-20261118/G9/chrome-trace-analysis/examples.md</code> |
| [LOW] LOW | Unexpected 'reference.md' in skill root | <code>/skills/library-20261118/G9/chrome-trace-analysis/reference.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/chrome-trace-analysis`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-de0d564cf92046013378`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-e42bd32280d9eb366d71`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-034ff84dbdc4c1e0e99a`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'examples.md' in skill root**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/examples.md`
- Check: `unexpected_file`
- Finding ID: `SEF-0f13c9a2b82dbd00de46`
- Occurrence ID: `SEO-5d44ed74bcf13e69f068`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Unexpected 'reference.md' in skill root**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/reference.md`
- Check: `unexpected_file`
- Finding ID: `SEF-851b71102bebf398accd`
- Occurrence ID: `SEO-5a882a3438138f0f09a4`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Author not specified in metadata**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-097e1b7c6def2eaf1238`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**7. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-c6342a199aef087e4a96`
- Fix: State when to use the skill within the first 60 characters

**8. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-a47b04693a9c1fa335a4`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | MCP Tool Poisoning: The code's primary purpose matches the description: performance-trace CPU and long-task analysis. However, the descripti<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: No hidden dangerous capability, prompt injection, or undeclared access is present; this is only a documentation/capability mismatch, not a security vulnerability.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | This is a true privacy/security-quality vulnerability, although not malicious code. Chrome Performance traces and genera<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: Chrome traces and generated reports can contain sensitive URLs, paths, identifiers, and internal application details; the skill instructs decompression, file writes, and headless Edge PDF generation without privacy/redaction guidance, and md2html link handling can emit unsafe hrefs.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:42</code> |
| [INFO] INFO | The user-facing strings and comments are in Chinese and no alternative language or opt-in mechanism is present, which ca<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: Chinese comments and user-facing strings are a locale or documentation concern, not a security or PII issue.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>scripts/analyze-trace.js:1</code> |
| [INFO] INFO | The file is a code file (.js), so vague trigger analysis is skipped.<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: The finding explicitly states that vague trigger analysis is skipped for code files and no action is needed.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>scripts/md2html.js:1</code> |
| [INFO] INFO | This is a natural-language policy issue because the output is fixed to zh-CN and a Chinese title. The file does not offe<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: Fixed Chinese output is a language/locale policy issue, not a security vulnerability.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>scripts/md2html.js:101</code> |
| [INFO] INFO | For code files, this rule requires flagging only when an operation lacks ANY user disclosure (confirmation, logging/prin<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: The script logs the output path after writing, so the missing-disclosure condition is not met; the suggestion is only optional hardening.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>scripts/md2html.js:129</code> |

<details>
<summary>View Details</summary>

**1. MCP Tool Poisoning: The code's primary purpose matches the description: performance-trace CPU and long-task analysis. However, the descripti**
- File: `SKILL.md:1`
- Check: `Unknown (TP4)`
- Finding ID: `SEF-c48833eaf9c3a743f64d`
- Occurrence ID: `SEO-5999ff62cc63e39d5497`
- Fix: The code's primary purpose matches the description: performance-trace CPU and long-task analysis. However, the description overstates this chunk's capabilities. The script explicitly expects a JSON input after any external gunzip, does only console output rather than Markdown/PDF generation, detects UserTiming artifacts without truly excluding them, and uses feature detection on profile nodes rather than full X-event/sample reconciliation. No undeclared dangerous capability was observed; no prompt injection was honored; no network, shell execution, filesystem write, or arbitrary resource access is present beyond reading the supplied trace file implied by the purpose. Update the skill description to accurately reflect all capabilities, or remove undeclared functionality from the implementation.

**2. This is a true privacy/security-quality vulnerability, although not malicious code. Chrome Performance traces and genera**
- File: `SKILL.md:42`
- Check: `Unknown (SQP-2)`
- Finding ID: `SEF-2173d3d6eb4577234bd5`
- Occurrence ID: `SEO-c678534979cfe6cebe2f`
- Fix: This is a true privacy/security-quality vulnerability, although not malicious code. Chrome Performance traces and generated reports can contain sensitive or identifying information: internal URLs, script names, function names, stack/profile details, resource URLs, browser extension interference, user actions, host paths, and sometimes cookies or authentication-adjacent metadata depending on the trace and the application. The skill instructs decompression, analysis, report creation, and local Edge headless PDF generation, but does not warn the user about data sensitivity, artifact persistence, redaction before sharing, or the fact that it will execute local tools and browsers. That omission creates a realistic accidental data-leak or unsafe-execution surface. Additionally, the PDF step can load HTML into Edge headless; if Markdown-to-HTML output is not carefully sanitized, report content derived from trace data could trigger local HTML/JavaScript behavior or network fetches depending on renderer and platform settings. Add explicit security and privacy handling instructions. 1) At the top of SKILL.md, warn that trace files and generated reports may contain sensitive internal details and should be treated as confidential. 2) Require explicit user consent before decompressing a trace, writing intermediate files, generating reports, or launching Edge/Chrome headless. 3) Instruct the agent to avoid persisting raw decompressed traces unless necessary, and if necessary, write them to a temporary directory with a clear cleanup step. 4) Add a redaction/sanitization step before sharing or exporting: remove or replace user identifiers, URLs containing tokens, internal paths, environment-specific names, stack fragments, and sensitive script/function names when they are not essential to the report. 5) Generate PDF only from sanitized HTML, with HTML escaping enforced and raw HTML disabled or strictly allow-listed in md2html. 6) Prefer sandboxed or isolated PDF rendering; if local Edge is required, document that it runs locally, avoid --no-sandbox, and use flags or platform mechanisms that block background networking where supported, e.g. isolated temp user-data-dir, disabled extensions, and network restrictions if available. 7) Quote and validate file paths used in commands; reject traversal or shell metacharacters in user-supplied filenames. Suggested warning block: 'Security note: Performance traces can reveal internal application structure, URLs, scripts, functions, and user-related behavior. Decompressed traces and reports may persist sensitive data. Do not share raw traces or unredacted reports. The analysis may write files and launch a local headless browser for PDF output. Use a controlled environment, redact sensitive details, and clean up artifacts before sharing.'

**3. The user-facing strings and comments are in Chinese and no alternative language or opt-in mechanism is present, which ca**
- File: `scripts/analyze-trace.js:1`
- Check: `Unknown (SQP-3)`
- Finding ID: `SEF-404f19582b0422e6ed2a`
- Occurrence ID: `SEO-283b7f06d9595e03613a`
- Fix: The user-facing strings and comments are in Chinese and no alternative language or opt-in mechanism is present, which can be treated as a language/locale policy concern. Add explicit language/locale support or documentation if this tool must comply with a language policy. If Chinese is intentional, document the assumption and consider exposing English strings or a user-selectable locale.

**4. The file is a code file (.js), so vague trigger analysis is skipped.**
- File: `scripts/md2html.js:1`
- Check: `Unknown (SQP-1)`
- Finding ID: `SEF-c08e3401dec79310ca0b`
- Occurrence ID: `SEO-8a2819daaf292800b13f`
- Fix: The file is a code file (.js), so vague trigger analysis is skipped. No action needed for this file.

**5. This is a natural-language policy issue because the output is fixed to zh-CN and a Chinese title. The file does not offe**
- File: `scripts/md2html.js:101`
- Check: `Unknown (SQP-3)`
- Finding ID: `SEF-94643005c452569ab01e`
- Occurrence ID: `SEO-cd1b11f71fc342912add`
- Fix: This is a natural-language policy issue because the output is fixed to zh-CN and a Chinese title. The file does not offer a language/locale option or explicitly document that the skill is restricted to this region/language. Make the language/locale configurable (e.g., derive it from input, expose a CLI flag such as `--lang`, or allow the title to come from the Markdown document). If the output must always be Chinese, document that restriction clearly and justify it as a region/language-specific compliance requirement.

**6. For code files, this rule requires flagging only when an operation lacks ANY user disclosure (confirmation, logging/prin**
- File: `scripts/md2html.js:129`
- Check: `Unknown (SQP-2)`
- Finding ID: `SEF-7ebf176f2541f6a7dee0`
- Occurrence ID: `SEO-9c6296f796ff8678d186`
- Fix: For code files, this rule requires flagging only when an operation lacks ANY user disclosure (confirmation, logging/print, explanatory comment, or README mention). Here the script logs the output path after writing, so the specific “missing warning” condition is not met, even if the log is not a pre-write confirmation. Optional hardening: print a warning before overwriting an existing `OUT` file, or require an explicit overwrite flag, but this is not required under the current auditing criteria.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 3 files for PII
- [OK] **pii_detection**: No PII detected in 3 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- Found 0 Python, 0 Shell, 2 JavaScript/TypeScript files
- Semgrep not installed; skipped. Optional; install separately with: brew install semgrep (macOS) or uv tool install semgrep

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 3 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 3 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>examples.md:39</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>examples.md:137</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `examples.md:39`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-e8b201a9df8e81911a12`
- Content: `| 动画帧数 / rAF 回调数 | 3,654 帧 / 13,755 次（**每帧 ~3.8 个回调**） | ...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `examples.md:137`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-6408722aff518b700bbe`
- Content: `### ⚠️ 危险度 4：启动期长任务 + 掉帧爆发`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 81.8/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 80.0 | 35% |
| Discoverability | 80.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 81.8/100 (Grade: B)

**Non-blocking findings: 10**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | Description very long (437 chars, recommend 50-150) | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-9204f3dcaa40b1468c23`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-aaa7de31ec7819f877e7`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-e5ed5f2d75cabf8cf346`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description very long (437 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-acaf2305bb2ad3fd6551`
- Occurrence ID: `SEO-0044d0004890c880130c`
- Fix: Keep descriptions concise for progressive disclosure

**5. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-b64deb83151918443b91`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**6. No '## Purpose' section**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-fad988cb20790ccbd3b8`
- Fix: Add purpose section to clarify use cases

**7. No mention of error handling or validation**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-2e9b1568040302752b20`
- Fix: Document expected errors and how to handle them

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-5e8b50de41fc577274ad`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-f92bb43087f1bfcc8440`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-6651d3ebbb67a644ded6`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No Python scripts found in scripts/ or tools/; 2 Node script(s) not linted (script lint parses Python only)

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [INFO] INFO | hermes: 2 files outside references/, templates/, assets/ and scripts/ (examples.md, reference.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-76ef8e6f3c03a5667d2d`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-7babc83f84ccae1aa788`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 2 files outside references/, templates/, assets/ and scripts/ (examples.md, reference.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-b45b6612adad766bca04`
- Occurrence ID: `SEO-c9dc695e32933c41638e`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-47b7b9ec002a3abcb3a1`

</details>


### ✅ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

- [OK] **rubric_eval**: LLM Rubric Score: 85.9/100

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [8/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |
| [LOW] LOW | [8/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-1943ff5df6d6f5e180c3`
- Occurrence ID: `SEO-ba4a5f813b9eac4ff979`
- Fix: Description precisely states file types, symptoms, and scope, making when to use obvious. It includes strong trigger phrases such as Chrome DevTools Performance trace, CPU hotspot, long task, and page freeze.

**2. [9/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-b64defa39d2a89423425`
- Occurrence ID: `SEO-9c073376d8c6f30619fa`
- Fix: Steps are concrete with commands, placeholders, and interpretation rules, and the workflow checklist guides the agent. Some Windows-specific redirection details could distract non-Windows users but are still actionable.

**3. [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-71d8b11b02859ed46a0d`
- Occurrence ID: `SEO-2e2a384ed11e76e96e71`
- Fix: The full report and reference cases show high-quality usage and interpretation. It lacks explicit sample user queries, so query variation coverage is inferred from the description.

**4. [9/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-2b271f008c7b14831c46`
- Occurrence ID: `SEO-0a30cac31a20782d0bdd`
- Fix: Purpose, scripts, parameters, outputs, and linked references are present. The script listing is truncated here, but the documented interface is sufficiently complete.

**5. [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-b51813109e621bc47496`
- Occurrence ID: `SEO-07de4c611345e19f07aa`
- Fix: Scope is tightly bounded to Chrome DevTools Performance traces and page CPU/jank analysis. PDF/report generation is a reasonable adjacent capability.

**6. [8/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-d967b9542b555e69bb92`
- Occurrence ID: `SEO-eb2201097d46919be1fd`
- Fix: Tone is technical, consistent, and practical. Emojis and a very long Chinese description are slightly less formal but still appropriate for operational docs.

**7. [9/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-3b272bf284ce0c70f7a8`
- Occurrence ID: `SEO-a3529067a4099c348ca4`
- Fix: It should correctly trigger for Chrome trace files, page freeze, CPU hotspot, long task, and dropped-frame requests. It likely avoids non-Chrome profiling or generic Lighthouse queries due to explicit Chrome/trace wording.

**8. [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-c62bed15830200e0f385`
- Occurrence ID: `SEO-3194d9e0b22c1a692d20`
- Fix: Covers recording, decompression, analysis, artifact filtering, reporting, and optional PDF generation. Minor gaps include handling missing files or non-Chrome trace formats, but they are outside core scope.

**9. [8/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G9/chrome-trace-analysis/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-c8429d5f9146312045d0`
- Occurrence ID: `SEO-551f469aa04b21ac8b99`
- Fix: Error guidance is realistic and actionable, including heap limits, encoding pitfalls, false hotspots, and profiler artifacts. It could add a short troubleshooting section for script failures or invalid trace files.

</details>


---
*Generated by SkillEvaluator*