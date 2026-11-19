# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:59 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 39 unique findings (1 high, 5 medium) / 41 occurrences / 41 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-81f6948a728344c5d6c6` | HIGH | Missing top-level heading (&#35; Title) in SKILL.md body | 1 | Schema &amp; Repository Governance |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-6b66555d1029e567b59c` | LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | 3 | Unicode Smuggling Detection |
| `SEF-0d2215183b14101ae2c2` | LOW | No examples provided | 1 | QUALITY |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-13888f89572b529ff564` | LOW | Frontmatter field(s) outside the agentskills.io spec: argument-hint, author, version; agent harnesses do not pass them to the model | 1 | Schema &amp; Repository Governance |
| ... | | *29 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| usb-diag | 87.2 | B | guide-only | 85.0 | 85.0 | 85.0 | 100.0 |

## Results

### ❌ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

**1 errors, 10 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/usb-diag</code> |
| [HIGH] HIGH | Missing top-level heading (# Title) in SKILL.md body | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | Unexpected 'diagnostic-rules.md' in skill root | <code>/skills/library-20261118/G9/usb-diag/diagnostic-rules.md</code> |
| [LOW] LOW | Unexpected 'usb-treeview-format.md' in skill root | <code>/skills/library-20261118/G9/usb-diag/usb-treeview-format.md</code> |
| [LOW] LOW | Unexpected 'usb-device-kb.md' in skill root | <code>/skills/library-20261118/G9/usb-diag/usb-device-kb.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: argument-hint, author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/usb-diag`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-9027b4c3d85312545bbd`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing top-level heading (# Title) in SKILL.md body**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `body_heading`
- Finding ID: `SEF-81f6948a728344c5d6c6`
- Occurrence ID: `SEO-6634f7025f5de6e6595a`
- Fix: Add a top-level heading after the frontmatter, e.g. '# My Skill'

**3. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-10498300ac5f6d066e2b`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**4. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-c6d887eb3cb57cca1e3e`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**5. Unexpected 'diagnostic-rules.md' in skill root**
- File: `/skills/library-20261118/G9/usb-diag/diagnostic-rules.md`
- Check: `unexpected_file`
- Finding ID: `SEF-fcea52a7e261f4177e97`
- Occurrence ID: `SEO-fa6bb9ca467616191be9`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Unexpected 'usb-treeview-format.md' in skill root**
- File: `/skills/library-20261118/G9/usb-diag/usb-treeview-format.md`
- Check: `unexpected_file`
- Finding ID: `SEF-26226bb47434e24c3199`
- Occurrence ID: `SEO-6defff4bf6bf0bc8e4b7`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**7. Unexpected 'usb-device-kb.md' in skill root**
- File: `/skills/library-20261118/G9/usb-diag/usb-device-kb.md`
- Check: `unexpected_file`
- Finding ID: `SEF-2ace50cd792180f1ce8c`
- Occurrence ID: `SEO-97d514b41b344f5bda22`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**8. Author not specified in metadata**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-0724757d1113c04505be`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**9. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-64c5344a5003efe5a9f6`
- Fix: State when to use the skill within the first 60 characters

**10. Frontmatter field(s) outside the agentskills.io spec: argument-hint, author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-13888f89572b529ff564`
- Occurrence ID: `SEO-fdcc5a786c97d86a5423`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)

### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 4 files for PII
- [OK] **pii_detection**: No PII detected in 4 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **code_file_discovery**: No code files found - code risk analysis is not applicable

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 4 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 4 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>diagnostic-rules.md:223</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>diagnostic-rules.md:228</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>diagnostic-rules.md:242</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `diagnostic-rules.md:223`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-bf0045153aa3326773e9`
- Content: `| 1 | ... | ... | ... | HID/USB/Video | ... | ... | ✅/❌ |...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `diagnostic-rules.md:228`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-34acee75dc7e59698873`
- Content: `#### ⚠️ 警告 ({count})`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**3. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `diagnostic-rules.md:242`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-a7f6a801248cded55e07`
- Content: `- **结论**: 应用能否枚举 → ✅ 可以 / ❌ 不可以 / ⚠️ 不确定`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 87.2/100 (Grade: B)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 85.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 87.2/100 (Grade: B)

**Non-blocking findings: 8**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No examples provided**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-28c9c113d47c3a113213`
- Fix: Add example usage with code blocks

**2. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-9c069e7b0233f1d1e562`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-8b4e921aaa93a7480aab`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-4eaacbbc1f10bdcc30f7`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-58ff43b64a95de5579a0`
- Fix: Add purpose section to clarify use cases

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-95907954674ba82a4065`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-1dc0833ca55712570193`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-51d8b04c95e497f3e396`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 20**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | claude-code: allowed-tools only pre-approves tools, never restricts, and applies only when the skill is invoked through the Skill tool (e.g. /name), not when the model reads the file. With --headless, see CC-ALLOWED-TOOLS-HEADLESS. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | codex: allowed-tools is ignored by Codex. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | codex: $ARGUMENTS is not substituted: the model sees the literal text. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | codex: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | copilot-cli: allowed-tools is ignored in -p (headless) mode; interactive behaviour unverified. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [LOW] LOW | copilot-cli: $ARGUMENTS is not substituted: the model sees the literal text. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| [INFO] INFO | hermes: allowed-tools is ignored by Hermes. | <code>/skills/library-20261118/G9/usb-diag/SKILL.md</code> |
| ... | *10 more issues* | |

<details>
<summary>View Details</summary>

**1. claude-code: allowed-tools only pre-approves tools, never restricts, and applies only when the skill is invoked through the Skill tool (e.g. /name), not when the model reads the file. With --headless, see CC-ALLOWED-TOOLS-HEADLESS.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CC-ALLOWED-TOOLS`
- Finding ID: `SEF-a491fddbd29ee4b6bdf1`
- Occurrence ID: `SEO-bf0f35b59bbdbd85e325`
- Fix: Don't rely on allowed-tools to restrict tools; use the harness's permission settings.

**2. codex: allowed-tools is ignored by Codex.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CX-ALLOWED-TOOLS`
- Finding ID: `SEF-0498456e344a658ba70e`
- Occurrence ID: `SEO-5d2726e25313ec4ae80b`
- Fix: Don't rely on allowed-tools to restrict tools; use the harness's permission settings.

**3. codex: $ARGUMENTS is not substituted: the model sees the literal text.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CX-ARGUMENTS`
- Finding ID: `SEF-948aad43a830863a1bec`
- Occurrence ID: `SEO-f33b288d6e227057b526`
- Fix: Describe the expected input in words instead of $ARGUMENTS.

**4. codex: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CX-CLAUDE-ONLY`
- Finding ID: `SEF-3c14903aa6a36408a8d2`
- Occurrence ID: `SEO-66a6f7e59f4c1cc08d14`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**5. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-608897e1e85e0e341817`

**6. copilot-cli: allowed-tools is ignored in -p (headless) mode; interactive behaviour unverified.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CP-ALLOWED-TOOLS`
- Finding ID: `SEF-8384ed85e117759caec1`
- Occurrence ID: `SEO-3dde27df122c00b9954a`
- Fix: Don't rely on allowed-tools to restrict tools; use the harness's permission settings.

**7. copilot-cli: $ARGUMENTS is not substituted: the model sees the literal text.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CP-ARGUMENTS`
- Finding ID: `SEF-4f5113ae253d86a0baf7`
- Occurrence ID: `SEO-a28dba47cb3f985d2ddc`
- Fix: Describe the expected input in words instead of $ARGUMENTS.

**8. copilot-cli: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `CP-CLAUDE-ONLY`
- Finding ID: `SEF-9dcf632d2f32abd5d60c`
- Occurrence ID: `SEO-976b67e13e3a783779ee`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**9. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-4ffbb2ea092804278200`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**10. hermes: allowed-tools is ignored by Hermes.**
- File: `/skills/library-20261118/G9/usb-diag/SKILL.md`
- Check: `HM-ALLOWED-TOOLS`
- Finding ID: `SEF-5e6a43e243ce82a1f952`
- Occurrence ID: `SEO-71e119aff710cda0dee1`
- Fix: Don't rely on allowed-tools to restrict tools; use the harness's permission settings.

*... and 10 more issues*

</details>


---
*Generated by SkillEvaluator*