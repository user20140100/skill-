# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:40 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 13 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 25 unique findings (10 medium) / 25 occurrences / 25 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-0779d5fe291572577573` | MEDIUM | Agent Snooping: ls metadata 的 &#96;canonicalPath&#96; 为事实源，不以 &#96;.claude/skills&#96; 或 &#96;.codex/skills | 1 | Security Scan |
| `SEF-14fd6942eaddb9a936a8` | MEDIUM | Agent Snooping: ls metadata 的 &#96;canonicalPath&#96; 为事实源,不以 &#96;.claude/skills&#96; 或 &#96;.codex/skills | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-e6bee2b3f281ff07e52f` | MEDIUM | Description contains vague words | 1 | QUALITY |
| ... | | *15 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| general-problem-handling | 72.8 | C | script-based | 65.0 | 65.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'general-problem-handling'
- [OK] **naming_convention**: Folder name 'general-problem-handling' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (67/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: references, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'general-problem-handling'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/general-problem-handling</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/general-problem-handling`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-ac30d895312f5de85ced`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-60634961a5fd19135962`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-3c4cccb9060160fa1031`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-dbab0db28ec237e17715`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-62b93350e6b4736ad73f`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-b1419294638d9a7fa665`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: Security scan completed - 2 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Agent Snooping: ls metadata 的 &#96;canonicalPath&#96; 为事实源,不以 &#96;.claude/skills&#96; 或 &#96;.codex/skills | <code>references/cskills-loading.md:18</code> |
| [MED] MEDIUM | Agent Snooping: ls metadata 的 &#96;canonicalPath&#96; 为事实源，不以 &#96;.claude/skills&#96; 或 &#96;.codex/skills | <code>references/cskills-loading.md:18</code> |

<details>
<summary>View Details</summary>

**1. Agent Snooping: ls metadata 的 `canonicalPath` 为事实源,不以 `.claude/skills` 或 `.codex/skills**
- File: `references/cskills-loading.md:18`
- Check: `Skill Enumeration (AS3)`
- Finding ID: `SEF-14fd6942eaddb9a936a8`
- Occurrence ID: `SEO-9001da9ce1f380aa10a1`
- Content: `## 本地选择与安装

1. 按“当前项目 canonical → 全局 canonical → 未安装”检查;以...`
- Fix: Skill enumerates or reads other installed skills. Access to other skills' SKILL.md files or the skills directory reveals prompt instructions, capabilities, and secrets that should be invisible to peer skills. Remove all code or instructions that list or read other skills' files or directories. Skills should operate independently; cross-skill access is a privilege escalation.

**2. Agent Snooping: ls metadata 的 `canonicalPath` 为事实源，不以 `.claude/skills` 或 `.codex/skills**
- File: `references/cskills-loading.md:18`
- Check: `Skill Enumeration (AS3)`
- Finding ID: `SEF-0779d5fe291572577573`
- Occurrence ID: `SEO-9595137359970109c9e1`
- Content: `## 本地选择与安装

1. 按“当前项目 canonical → 全局 canonical → 未安装”检查；以...`
- Fix: Skill enumerates or reads other installed skills. Access to other skills' SKILL.md files or the skills directory reveals prompt instructions, capabilities, and secrets that should be invisible to peer skills. Remove all code or instructions that list or read other skills' files or directories. Skills should operate independently; cross-skill access is a privilege escalation.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 15 files for PII
- [OK] **pii_detection**: No PII detected in 15 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- Found 0 Python, 1 Shell, 0 JavaScript/TypeScript files
- Semgrep not installed; skipped. Optional; install separately with: brew install semgrep (macOS) or uv tool install semgrep

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 14 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 14 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>references/decision-rules.md:264</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `references/decision-rules.md:264`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-7e116fe772524f2770db`
- Content: `- ⚠️ 阶段产物校验失败：{阶段名} 的 {文件名} 缺失或不合格`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ✅ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 72.8/100 (Grade: C)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 65.0 | 35% |
| Discoverability | 65.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 72.8/100 (Grade: C)

**Non-blocking findings: 13**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | Description very long (289 chars, recommend 50-150) | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [MED] MEDIUM | Description contains vague words | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| ... | *3 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-0a2e2d0e8c16e8269d1b`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-1e8324988244f0caf8ec`
- Fix: Add explicit run_script() call examples

**3. No examples provided**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-50500ad5928868e88a76`
- Fix: Add example usage with code blocks

**4. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-e4ce3d069e6bc6d56470`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**5. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-6b469df366b17b0357c0`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**6. Description very long (289 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-c7c369d46f4692f822e5`
- Occurrence ID: `SEO-76f57b7ace55a5f7044a`
- Fix: Keep descriptions concise for progressive disclosure

**7. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-c6c0c61b90e27d91cd1f`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**8. Description contains vague words**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-e6bee2b3f281ff07e52f`
- Occurrence ID: `SEO-235f2a153300cf8a97f5`
- Fix: Be specific about what this skill does

**9. No '## Purpose' section**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-4d5affb11934f675a557`
- Fix: Add purpose section to clarify use cases

**10. No mention of error handling or validation**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-bf8aa50d73c9a171226d`
- Fix: Document expected errors and how to handle them

*... and 3 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No Python scripts found in scripts/ or tools/

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/general-problem-handling/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-d3eab232762d7bf3815c`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-61d9d300e36838f2f161`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/general-problem-handling/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-9bdb6bff20e28bdaf173`

</details>


---
*Generated by SkillEvaluator*