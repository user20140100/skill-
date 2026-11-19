# SkillEvaluator Validation Report

**Status:** ✅ PASSED
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
| ✅ Passed | 13 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 23 unique findings (6 medium) / 24 occurrences / 24 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-6b66555d1029e567b59c` | LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | 2 | Unicode Smuggling Detection |
| `SEF-0f13c9a2b82dbd00de46` | LOW | Unexpected 'examples.md' in skill root | 1 | Schema &amp; Repository Governance |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-29923f4d680e578e37e3` | LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | 1 | Schema &amp; Repository Governance |
| ... | | *13 more unique findings* | | |

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


---
*Generated by SkillEvaluator*