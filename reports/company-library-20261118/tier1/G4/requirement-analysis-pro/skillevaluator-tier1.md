# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:10 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 13 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 26 unique findings (9 medium) / 26 occurrences / 26 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-cb5595dbd2b0cdf60c1d` | MEDIUM | Deeply nested references in doc-structure-common.md | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-0aaee0a3095e4d3bd9ab` | LOW | validate&#95;skill.py contains magic numbers | 1 | SCRIPT&#95;LINT |
| ... | | *16 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| requirement-analysis-pro | 78.0 | C | script-based | 70.0 | 85.0 | 75.0 | 90.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'requirement-analysis-pro'
- [OK] **naming_convention**: Folder name 'requirement-analysis-pro' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (258/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: references, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'requirement-analysis-pro'

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G4/requirement-analysis-pro</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | Unexpected '修改日志.md' in skill root | <code>/skills/library-20261118/G4/requirement-analysis-pro/修改日志.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G4/requirement-analysis-pro`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-44367298b67432762536`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-139cb7393070ceca6994`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-2bb03e5d21275005b540`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected '修改日志.md' in skill root**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/修改日志.md`
- Check: `unexpected_file`
- Finding ID: `SEF-d3ede74918e5bc14931a`
- Occurrence ID: `SEO-3fa84386cc2c5d2b8bce`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Author not specified in metadata**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-24a275de1126b8b60481`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**6. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-5f8fb87945e27c008589`
- Fix: State when to use the skill within the first 60 characters

**7. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-bab78b1b1ffb795d7cb0`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: Security scan completed - 1 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |

<details>
<summary>View Details</summary>

**1. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 12 files for PII
- [OK] **pii_detection**: No PII detected in 12 files (emails, SSNs, phone numbers, paths)

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

- [OK] **dead_links_scan**: Checking 11 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 11 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 12 file(s)

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
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| ... | *1 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-0563318af07941c1f815`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-a42de55b314efddb157c`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-8ae8376904d292866df7`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-34f38e092ca2680c509a`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-3140b90d5b4b3ab2fc5e`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**6. No '## Purpose' section**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-a02b32ab8fc8c6ffac61`
- Fix: Add purpose section to clarify use cases

**7. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-e12fcfeb8f75a01a7d56`
- Fix: Document expected errors and how to handle them

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-4b37ca324f9bccdec454`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-53660691e759962b957d`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-21807f02c1bb0f205443`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

*... and 1 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | validate_skill.py contains magic numbers | <code>/skills/library-20261118/G4/requirement-analysis-pro/scripts/validate_skill.py</code> |
| [LOW] LOW | validate_skill.py may lack input validation | <code>/skills/library-20261118/G4/requirement-analysis-pro/scripts/validate_skill.py</code> |

<details>
<summary>View Details</summary>

**1. validate_skill.py contains magic numbers**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/scripts/validate_skill.py`
- Check: `magic_numbers`
- Finding ID: `SEF-0aaee0a3095e4d3bd9ab`
- Occurrence ID: `SEO-d6b3c7fc1ae33b8902fb`
- Fix: Extract magic numbers to named constants

**2. validate_skill.py may lack input validation**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/scripts/validate_skill.py`
- Check: `no_input_validation`
- Finding ID: `SEF-528faef4d174d8d7975c`
- Occurrence ID: `SEO-c0a42890351abfcb3cf8`
- Fix: Add argument checks and raise descriptive errors

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (修改日志.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 26,643 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-b0e22efd0ecb6ca6bf08`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-2fc1040dafcdaa865679`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 1 files outside references/, templates/, assets/ and scripts/ (修改日志.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-001f67a780f72ee0caaa`
- Occurrence ID: `SEO-28b929d91f92a9dcc31f`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. openclaw: SKILL.md reads as 26,643 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-b1a07237bfde3ea80e8b`
- Occurrence ID: `SEO-44592412ef45ba698844`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**5. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/requirement-analysis-pro/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-b1d4afed47c01f4f6078`

</details>


---
*Generated by SkillEvaluator*