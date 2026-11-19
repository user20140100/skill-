# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:38 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 1 |
| Total Issues | 29 unique findings (3 high, 13 medium) / 29 occurrences / 29 raw records; 1 error and 1 warning without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-504633eeb164342fd6f5` | HIGH | Output Handling: success = subprocess.run( &#91;sys.executable, str(SCRIPT&#95;PATH), "--input", str(path), "--output", str(output)&#93;, capture&#95;output=True, text=True, che | 1 | Security Scan |
| `SEF-8107216c67bc27c98d8b` | HIGH | analysis-evasion: references/android-kotlin.md (partial) | 1 | Security Scan |
| `SEF-84d95de439d61838eebd` | HIGH | Privilege Escalation: access token | 1 | Security Scan |
| `SEF-0670cf2cb2271a4bd1f4` | MEDIUM | Dangerous Code Execution: subprocess.run(command, capture&#95;output=True, text=True, check=False) | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-1aa782d848011b7c5ecb` | MEDIUM | Dangerous Code Execution: subprocess.run( &#91;sys.executable, str(SCRIPT&#95;PATH), "--input", str(self.root / "missing.log")&#93;, capture&#95;output=True, text=True, check=False, ) | 1 | Security Scan |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-421e427fba0a3e95c956` | MEDIUM | Deeply nested references in methodology.md | 1 | QUALITY |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| ... | | *19 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| diagnostic-logging | 80.5 | B | hybrid | 70.0 | 85.0 | 85.0 | 90.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'diagnostic-logging'
- [OK] **naming_convention**: Folder name 'diagnostic-logging' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (120/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: README.md, agents, assets, references, scripts, tests
- [OK] **name_consistency**: Directory name matches frontmatter: 'diagnostic-logging'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/diagnostic-logging</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | Description has its trigger at characters 107-114; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/diagnostic-logging`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-8376bf27a8cc9fad1255`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-ae4e6e5c916bda633b1e`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-db7d3826d02ddb642ce3`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-9de5f807857b1e1f1531`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has its trigger at characters 107-114; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-2e2374d8c4c89c795e70`
- Occurrence ID: `SEO-144f6624740cedc1cf48`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-ef51dc3e66e4c692216c`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

- skillspector could not completely inspect 1 referenced artifact(s) across 1 reference occurrence(s); each AE1 finding names the artifact and any reasons SkillSpector gave

**Incomplete scanners:** skillspector

**4 errors, 5 warnings**

**Execution errors:**

- ❌ skillspector JSON field 'analysis_completeness' reports incomplete analysis (status 'partial'): SKILL.md:25 [reference_resolution; reference_missing]; SKILL.md:59 [reference_resolution; reference_missing]; references/android-kotlin.md [static; static_parse_limit; analyzers=static_patterns_tool_misuse]; and 1 more (incomplete files by reason: static_parse_limit 2, reference_missing 1); security scan did not complete

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | analysis-evasion: references/android-kotlin.md (partial) | <code>SKILL.md:40</code> |
| [HIGH] HIGH | Privilege Escalation: access token | <code>references/environment-layer.md:112</code> |
| [HIGH] HIGH | Output Handling:         success = subprocess.run(<br>            [sys.executable, str(SCRIPT_PATH), "--input", str(path), "--output", str(output)],<br>            capture_output=True,<br>            text=True,<br>            che | <code>tests/test_analyze_log.py:375</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run(<br>            [sys.executable, str(SCRIPT_PATH), "--input", str(path), "--output", str(output)],<br>            capture_output=True,<br>            text=True,<br>            check=False,<br>         | <code>tests/test_analyze_log.py:375</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run(<br>            [sys.executable, str(SCRIPT_PATH), "--input", str(self.root / "missing.log")],<br>            capture_output=True,<br>            text=True,<br>            check=False,<br>        ) | <code>tests/test_analyze_log.py:381</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run(command, capture_output=True, text=True, check=False) | <code>tests/test_init_project.py:145</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run(<br>            [sys.executable, str(SCRIPT_PATH), "--project-root", str(self.root / "nope")],<br>            capture_output=True,<br>            text=True,<br>            check=False,<br>        ) | <code>tests/test_init_project.py:152</code> |

<details>
<summary>View Details</summary>

**1. analysis-evasion: references/android-kotlin.md (partial)**
- File: `SKILL.md:40`
- Check: `Incomplete referenced artifact analysis (AE1)`
- Finding ID: `SEF-8107216c67bc27c98d8b`
- Occurrence ID: `SEO-48653f982d3358c3ff28`
- Content: `act](references/instrumentation-safety.md). Read [the And...`
- Fix: Referenced artifact references/android-kotlin.md was not completely inspected (partial). static_parse_limit (static_patterns_tool_misuse): A security-relevant expression could not be fully resolved by the bounded static parser. Review the reported expression and analyzer's parsing limitation; correct the scanner if it misinterprets valid source, then rerun the scan. Keep required references; incomplete analysis is not proof of malicious evasion.

**2. Privilege Escalation: access token**
- File: `references/environment-layer.md:112`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-84d95de439d61838eebd`
- Occurrence ID: `SEO-30bf04d35d4b969cea1f`
- Content: `## Repository identity safety

`vcs_repository` is a repo...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**3. Output Handling:         success = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(path), "--output", str(output)],
            capture_output=True,
            text=True,
            che**
- File: `tests/test_analyze_log.py:375`
- Check: `Unvalidated Output Injection (OH1)`
- Finding ID: `SEF-504633eeb164342fd6f5`
- Occurrence ID: `SEO-f8c5522b1e9648afef7f`
- Content: `)
        output = self.root / "evidence.json"

        s...`
- Fix: Model output is used without validation or sanitization. Unvalidated output injected into downstream contexts (SQL, shell, HTML) enables injection attacks and arbitrary code execution. Validate and sanitize all model output before using it in downstream contexts. Use parameterized queries for SQL, shell quoting for commands, and HTML encoding for web output.

**4. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**5. Dangerous Code Execution: subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(path), "--output", str(output)],
            capture_output=True,
            text=True,
            check=False,
        **
- File: `tests/test_analyze_log.py:375`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-c6a7fd4a84063a84c284`
- Occurrence ID: `SEO-cd4634b119014e35c147`
- Content: `)
        output = self.root / "evidence.json"

        s...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

**6. Dangerous Code Execution: subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--input", str(self.root / "missing.log")],
            capture_output=True,
            text=True,
            check=False,
        )**
- File: `tests/test_analyze_log.py:381`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-1aa782d848011b7c5ecb`
- Occurrence ID: `SEO-0f40f841a5c406c2771f`
- Content: `text=True,
            check=False,
        )
        fai...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

**7. Dangerous Code Execution: subprocess.run(command, capture_output=True, text=True, check=False)**
- File: `tests/test_init_project.py:145`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-0670cf2cb2271a4bd1f4`
- Occurrence ID: `SEO-0246304215b35f82156c`
- Content: `def test_cli_emits_json_on_success_and_stderr_on_validati...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

**8. Dangerous Code Execution: subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--project-root", str(self.root / "nope")],
            capture_output=True,
            text=True,
            check=False,
        )**
- File: `tests/test_init_project.py:152`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-c3c7592866d7f2e71098`
- Occurrence ID: `SEO-b738425872f7a1d40168`
- Content: `self.assertEqual("created", payload["status"])
        se...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 16 files for PII
- [OK] **pii_detection**: No PII detected in 16 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **bandit**: Bandit: No security issues found

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 10 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 10 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: Found 3 standard Python test-file candidate(s); target tests were not executed and coverage was not measured

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 16 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 80.5/100 (Grade: B)** | Skill Type: hybrid

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 70.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 90.0 | 15% |

- [OK] **quality_score**: Score: 80.5/100 (Grade: B)

**Non-blocking findings: 11**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | Description very long (396 chars, recommend 50-150) | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | Broad description without negative triggers may cause over-triggering | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| ... | *1 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-8d1565fe9d8ea5eb9dc0`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-51a9fadb1e234a668b47`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-f364dacd644ff48ff746`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-6239c57db0368563e296`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. Description very long (396 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-d2686e20fade575c8851`
- Occurrence ID: `SEO-985bf90aa1de38764f8c`
- Fix: Keep descriptions concise for progressive disclosure

**6. Broad description without negative triggers may cause over-triggering**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-1017300978cb9cb0eae9`
- Occurrence ID: `SEO-e7e2145310982d9f66fa`
- Fix: Add boundary phrases like 'Do NOT use for...'

**7. No '## Purpose' section**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-5840228d8c2b00055505`
- Fix: Add purpose section to clarify use cases

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-4a6474a3a6b70db3bfb0`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-3633ca52ccc8cdb2210a`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-6a5156b0fe1b0096da7c`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

*... and 1 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: All 2 script(s) passed lint checks

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [INFO] INFO | hermes: 5 files outside references/, templates/, assets/ and scripts/ (README.md, agents, tests) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/diagnostic-logging/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-8bd9dce1237fa4831762`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-0163aa9c165dc6bb2ec9`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 5 files outside references/, templates/, assets/ and scripts/ (README.md, agents, tests) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-ed2d9b99e7a10ce01550`
- Occurrence ID: `SEO-49e07ad53bfa973be4ee`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/diagnostic-logging/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-99e11f298cb98e2dd97c`

</details>


---
*Generated by SkillEvaluator*