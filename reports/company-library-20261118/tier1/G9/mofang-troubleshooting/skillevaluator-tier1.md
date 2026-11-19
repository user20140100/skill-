# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:52 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 10 |
| ❌ Failed | 3 |
| ⚠️ Incomplete | 0 |
| Total Issues | 27 unique findings (2 critical, 2 high, 10 medium) / 27 occurrences / 27 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-311bfc700171c8f9c9bd` | CRITICAL | Hardcoded secret/credential in code: &#91;REDACTED&#93; | 1 | PII Scan |
| `SEF-726dde0df6c5351442dd` | CRITICAL | Detected a Generic API Key, potentially exposing access to various services and sensitive operations. in scripts/wise.py:11 &#91;generic-api-key&#93; | 1 | Secrets Detection |
| `SEF-0d49a11b546ddb1e4afe` | HIGH | Supply Chain: curl -sSL https://mom.seewo.com/cli/install &#124; bash | 1 | Security Scan |
| `SEF-cd62b9b66b0bc778e56f` | HIGH | Tool Misuse: &#124; bash | 1 | Security Scan |
| `SEF-0c82b545f9cd036bc3c0` | MEDIUM | Dangerous Code Execution: subprocess.run(&#91; "curl", "--disable", "--silent", "--show-error", "--max-time", "45", "--max-filesize", "8388608", "--request", method, "--header", "Content-Type: a | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| ... | | *17 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| mofang-troubleshooting | 78.0 | C | script-based | 70.0 | 85.0 | 75.0 | 90.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'mofang-troubleshooting'
- [OK] **naming_convention**: Folder name 'mofang-troubleshooting' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (54/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: references, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'mofang-troubleshooting'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/mofang-troubleshooting</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/mofang-troubleshooting`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-cab6ec2d9a591feb7416`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-046df28b6b339b4a316a`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-6aef032279ca8cee152a`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-d3d376f2470551e1ee01`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-89ea1fe032046a2c9f90`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-0dafd11f88c1785040a5`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**2 errors, 2 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Supply Chain: curl -sSL https://mom.seewo.com/cli/install &#124; bash | <code>references/cli-setup.md:20</code> |
| [HIGH] HIGH | Tool Misuse: &#124; bash | <code>references/cli-setup.md:20</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run([<br>            "curl", "--disable", "--silent", "--show-error", "--max-time", "45",<br>            "--max-filesize", "8388608", "--request", method,<br>            "--header", "Content-Type: a | <code>scripts/wise.py:20</code> |

<details>
<summary>View Details</summary>

**1. Supply Chain: curl -sSL https://mom.seewo.com/cli/install | bash**
- File: `references/cli-setup.md:20`
- Check: `External Script Fetching (SC2)`
- Finding ID: `SEF-0d49a11b546ddb1e4afe`
- Occurrence ID: `SEO-4efa26058aaffd6ce627`
- Content: `缺失时在 macOS/Linux 安装：

```bash
curl -sSL https://mom.seewo...`
- Fix: Remote code is downloaded and executed. This bypasses code review and could introduce malicious code. Avoid downloading and executing remote scripts. Use trusted packages from PyPI/npm. If remote fetch is required, verify checksums and use HTTPS.

**2. Tool Misuse: | bash**
- File: `references/cli-setup.md:20`
- Check: `Chaining Abuse (TM2)`
- Finding ID: `SEF-cd62b9b66b0bc778e56f`
- Occurrence ID: `SEO-694e9336caf12c581910`
- Content: `缺失时在 macOS/Linux 安装：

```bash
curl -sSL https://mom.seewo...`
- Fix: Tool calls are chained to bypass individual safety checks or escalate capabilities beyond what any single tool call would allow. Limit tool chaining depth and validate the output of each tool before passing it to the next. Require explicit user approval for multi-step chains.

**3. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**4. Dangerous Code Execution: subprocess.run([
            "curl", "--disable", "--silent", "--show-error", "--max-time", "45",
            "--max-filesize", "8388608", "--request", method,
            "--header", "Content-Type: a**
- File: `scripts/wise.py:20`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-0c82b545f9cd036bc3c0`
- Occurrence ID: `SEO-78aa382df94258cc347a`
- Content: `if body is not None:
        config += 'data = ' + json.d...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

</details>


### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [CRIT] CRITICAL | Hardcoded secret/credential in code: [REDACTED] | <code>scripts/wise.py:11</code> |

<details>
<summary>View Details</summary>

**1. Hardcoded secret/credential in code: [REDACTED]**
- File: `scripts/wise.py:11`
- Check: `hardcoded_secrets`
- Finding ID: `SEF-311bfc700171c8f9c9bd`
- Occurrence ID: `SEO-ab635fab4f1879e6eb52`
- Fix: Use environment variable or secrets manager instead of hardcoded value

</details>


### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **bandit**: Bandit: No security issues found

### ❌ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [CRIT] CRITICAL | Detected a Generic API Key, potentially exposing access to various services and sensitive operations. in scripts/wise.py:11 [generic-api-key] | <code>scripts/wise.py:11</code> |

<details>
<summary>View Details</summary>

**1. Detected a Generic API Key, potentially exposing access to various services and sensitive operations. in scripts/wise.py:11 [generic-api-key]**
- File: `scripts/wise.py:11`
- Check: `generic-api-key`
- Finding ID: `SEF-726dde0df6c5351442dd`
- Occurrence ID: `SEO-8c7bb6fef2279e85d2f0`
- Fix: Remove the secret from scripts/wise.py, revoke it, and read it from an environment variable

</details>


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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 4 file(s)

### ✅ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 78.0/100 (Grade: C)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 70.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 90.0 | 15% |

- [OK] **quality_score**: Score: 78.0/100 (Grade: C)

**Non-blocking findings: 11**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| ... | *1 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-dc90f1034628f3b9a4d8`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-53d2047b05a44a0125dd`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-4bb66f22e30c40b7bd05`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-db9ad22bbdd0ae992b68`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-7701eb96a189906e58d2`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**6. No '## Purpose' section**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-98610e6e3efd5361f822`
- Fix: Add purpose section to clarify use cases

**7. No mention of error handling or validation**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-9de4c462abbd5ee53757`
- Fix: Document expected errors and how to handle them

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-e125e6b7cfd673d94b71`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-2a8000ba084ab8f87dbc`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-7afb0e61b1efa240ff0f`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

*... and 1 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | wise.py contains magic numbers | <code>/skills/library-20261118/G9/mofang-troubleshooting/scripts/wise.py</code> |

<details>
<summary>View Details</summary>

**1. wise.py contains magic numbers**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/scripts/wise.py`
- Check: `magic_numbers`
- Finding ID: `SEF-e561ae226521f4b82ae0`
- Occurrence ID: `SEO-04a0c4832ff40263bf9a`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-0f5c44047ef68d880bb8`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-3e5fab57357d78cdb80e`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/mofang-troubleshooting/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-230d283767aaf2b7114c`

</details>


---
*Generated by SkillEvaluator*