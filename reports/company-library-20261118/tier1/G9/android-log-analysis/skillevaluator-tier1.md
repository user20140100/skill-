# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:33 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 11 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 2 |
| Total Issues | 24 unique findings (2 high, 7 medium) / 24 occurrences / 24 raw records; 2 errors and 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-415e8061563fd7800b81` | HIGH | System Prompt Leakage: Output Rules | 1 | Security Scan |
| `SEF-4cea91af1fe04b189973` | HIGH | analysis-evasion: decode&#95;xlog&#95;py2.py (partial) | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-593e9fd29af8eeb18e0d` | MEDIUM | SKILL.md has 652 lines (limit: 500) | 1 | Schema &amp; Repository Governance |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| ... | | *14 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| android-log-analysis | 90.2 | A | guide-only | 90.0 | 90.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'android-log-analysis'
- [OK] **naming_convention**: Folder name 'android-log-analysis' follows kebab-case convention
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **name_consistency**: Directory name matches frontmatter: 'android-log-analysis'

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/android-log-analysis</code> |
| [MED] MEDIUM | SKILL.md has 652 lines (limit: 500) | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | Unexpected 'decode_xlog_py2.py' in skill root | <code>/skills/library-20261118/G9/android-log-analysis/decode_xlog_py2.py</code> |
| [LOW] LOW | Unexpected 'decode_xlog.py' in skill root | <code>/skills/library-20261118/G9/android-log-analysis/decode_xlog.py</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | Description has its trigger at characters 285-293; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/android-log-analysis`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-b71009bfde5aff7a942a`
- Fix: General skills should be at: skills/<skill-name>/

**2. SKILL.md has 652 lines (limit: 500)**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `line_count`
- Finding ID: `SEF-593e9fd29af8eeb18e0d`
- Occurrence ID: `SEO-5cd3a8f667b6a19557d1`
- Fix: Consider moving content to reference files in references/ directory

**3. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-44ef6ef232ea7006c25a`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**4. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-957eaa5a629cd76cf5eb`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**5. Unexpected 'decode_xlog_py2.py' in skill root**
- File: `/skills/library-20261118/G9/android-log-analysis/decode_xlog_py2.py`
- Check: `unexpected_file`
- Finding ID: `SEF-39ff758f0f0df7004a2e`
- Occurrence ID: `SEO-fa3c51bc05913ba0e786`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Unexpected 'decode_xlog.py' in skill root**
- File: `/skills/library-20261118/G9/android-log-analysis/decode_xlog.py`
- Check: `unexpected_file`
- Finding ID: `SEF-94350c3e12e100972b8b`
- Occurrence ID: `SEO-8c62756bde93c24c1f38`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**7. Author not specified in metadata**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-db55f8901f94c8a6e500`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**8. Description has its trigger at characters 285-293; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-a5e6b19374a7cd3704fb`
- Occurrence ID: `SEO-ffc528ce238c36a931ad`
- Fix: State when to use the skill within the first 60 characters

**9. Frontmatter field(s) outside the agentskills.io spec: author; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-fd081a68fd6cb72673df`
- Occurrence ID: `SEO-f7c11596b92aa782098e`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

- skillspector could not completely inspect 1 referenced artifact(s) across 1 reference occurrence(s); each AE1 finding names the artifact and any reasons SkillSpector gave

**Incomplete scanners:** skillspector

**3 errors, 1 warnings**

**Execution errors:**

- ❌ skillspector JSON field 'analysis_completeness' reports incomplete analysis (status 'partial'): SKILL.md [static; static_parse_limit; analyzers=static_patterns_tool_misuse]; SKILL.md:65 [reference_resolution; reference_missing]; SKILL.md:94 [reference_resolution; reference_missing]; and 7 more (incomplete files by reason: static_parse_limit 1, reference_missing 1, syntax_error 1); security scan did not complete

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | analysis-evasion: decode_xlog_py2.py (partial) | <code>SKILL.md:124</code> |
| [HIGH] HIGH | System Prompt Leakage: Output Rules | <code>SKILL.md:607</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |

<details>
<summary>View Details</summary>

**1. analysis-evasion: decode_xlog_py2.py (partial)**
- File: `SKILL.md:124`
- Check: `Incomplete referenced artifact analysis (AE1)`
- Finding ID: `SEF-4cea91af1fe04b189973`
- Occurrence ID: `SEO-dac458d69c30be2e5479`
- Content: `3. 若 Python 3 版本解码失败或输出异常（空文件/乱码），自动回退到 Python 2.7 版本 (`d...`
- Fix: Referenced artifact decode_xlog_py2.py was not completely inspected (partial). syntax_error (behavioral_ast, behavioral_taint_tracking, static_patterns_data_exfiltration, static_patterns_output_handling, static_patterns_tool_misuse): Python source could not be parsed. Review the target's analysis-completeness ledger and resolve all limitations. Keep required references; incomplete analysis is not proof of malicious evasion.

**2. System Prompt Leakage: Output Rules**
- File: `SKILL.md:607`
- Check: `Direct Prompt Extraction (P6)`
- Finding ID: `SEF-415e8061563fd7800b81`
- Occurrence ID: `SEO-3cf201d43295fa9e9aad`
- Content: `- 注意事项: <与客户沟通时需注意的要点>
```

### 4.3 Output Rules

1. **时空...`
- Fix: Skill contains instructions that could directly expose system prompts, internal rules, or hidden instructions to users or external parties. Remove any instructions that reveal, print, or output system prompts or internal rules. System instructions should never be exposed to end users.

**3. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 3 files for PII
- [OK] **pii_detection**: No PII detected in 3 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ⚠️ INCOMPLETE Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

**Incomplete scanners:** bandit

**1 errors, 0 warnings**

**Execution errors:**

- ❌ Bandit scan error: syntax error while parsing AST from file


### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 1 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 1 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 3 file(s)

### ✅ A QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 90.2/100 (Grade: A)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 90.0 | 35% |
| Discoverability | 90.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 90.2/100 (Grade: A)

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | Description very long (495 chars, recommend 50-150) | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-f7227350504a0d3456ba`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-8e77b37867a2e2c05f65`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description very long (495 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-faa711497c38bc45f480`
- Occurrence ID: `SEO-b25c1af94eeec1377d63`
- Fix: Keep descriptions concise for progressive disclosure

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-bfb9b87f7a9a4d2bf94f`
- Fix: Add purpose section to clarify use cases

**5. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-3096553fc6b78df50516`
- Fix: Document dependencies, API keys, or setup needed

**6. No limitations documented**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-9fb691eb2b2dc48b8088`
- Fix: Add '## Limitations' section with known issues/constraints

**7. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-f5b0293fc078b838c001`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [INFO] INFO | hermes: 2 files outside references/, templates/, assets/ and scripts/ (decode_xlog.py, decode_xlog_py2.py) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 35,613 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/android-log-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-fd4b2c2dd1b2289916e9`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-5a34ec75ae7c7e0c547c`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 2 files outside references/, templates/, assets/ and scripts/ (decode_xlog.py, decode_xlog_py2.py) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-20a6fadd3a0169ac480b`
- Occurrence ID: `SEO-5c05cdd4f7eaf16db886`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. openclaw: SKILL.md reads as 35,613 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-6255e668ba66e519ac3a`
- Occurrence ID: `SEO-c77e3de8d54be239c0b0`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**5. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/android-log-analysis/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-d214a876b8c694525020`

</details>


---
*Generated by SkillEvaluator*