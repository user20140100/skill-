# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 12:53 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 10 |
| ❌ Failed | 3 |
| ⚠️ Incomplete | 0 |
| Total Issues | 25 unique findings (5 high, 6 medium) / 29 occurrences / 27 raw records; 1 error and 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-36abbfe1d1016633e227` | HIGH | Personal macOS user path: /Users/xxx/ — 2 occurrences (SKILL.md lines 207, 208) | 2 | PII Scan |
| `SEF-b0462032a92971607328` | HIGH | Personal macOS user path: /Users/&#91;^/ — 2 occurrences (SKILL.md line 111; references/review-checklist.md line 50) | 2 | PII Scan |
| `SEF-bd0e680581769fe55848` | HIGH | Privilege Escalation: .env" | 1 | Security Scan |
| `SEF-e9c2cdcee124d83df413` | HIGH | Personal macOS user path: /Users/overleazhou/ | 1 | PII Scan |
| `SEF-f5063b518af8b30ce7d9` | HIGH | Personal Windows user path: C:&#92;Users&#92;&#96; | 1 | PII Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3845fe0d187e165b6e4` | MEDIUM | SKILL.md has 544 lines (limit: 500) | 1 | Schema &amp; Repository Governance |
| ... | | *15 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| code-review-and-teach | 86.5 | B | guide-only | 90.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'code-review-and-teach'
- [OK] **naming_convention**: Folder name 'code-review-and-teach' follows kebab-case convention
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: references
- [OK] **name_consistency**: Directory name matches frontmatter: 'code-review-and-teach'

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/code-review-and-teach</code> |
| [MED] MEDIUM | SKILL.md has 544 lines (limit: 500) | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/code-review-and-teach`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-025fb331ec87967f5d24`
- Fix: General skills should be at: skills/<skill-name>/

**2. SKILL.md has 544 lines (limit: 500)**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `line_count`
- Finding ID: `SEF-e3845fe0d187e165b6e4`
- Occurrence ID: `SEO-4cf552855f816bb589fa`
- Fix: Consider moving content to reference files in references/ directory

**3. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-ea84745e8cffd4cc4ce0`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**4. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-5fe58a5f661a0589a243`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**5. Author not specified in metadata**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-fec34b168d493c9c4ff5`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**6. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-e41c0430f9430db72a33`
- Fix: State when to use the skill within the first 60 characters

**7. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-3e20c0f56043f6fb7fef`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**1 errors, 1 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Privilege Escalation: .env" | <code>references/review-checklist.md:69</code> |

<details>
<summary>View Details</summary>

**1. Privilege Escalation: .env"**
- File: `references/review-checklist.md:69`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-bd0e680581769fe55848`
- Occurrence ID: `SEO-89b7aa2bf17b3003349a`
- Content: ````
1. find 目标目录下所有文本文件
   → find {dir} -type f \( -name ...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

</details>


### ❌ PII Scan
*Detect PII and local identifiers*

**4 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Personal macOS user path: /Users/[^/ — 2 occurrences (SKILL.md line 111; references/review-checklist.md line 50) | <code>SKILL.md:111</code> |
| [HIGH] HIGH | Personal macOS user path: /Users/overleazhou/ | <code>SKILL.md:152</code> |
| [HIGH] HIGH | Personal macOS user path: /Users/xxx/ — 2 occurrences (SKILL.md lines 207, 208) | <code>SKILL.md:207</code> |
| [HIGH] HIGH | Personal Windows user path: C:\Users\&#96; | <code>references/review-checklist.md:135</code> |

<details>
<summary>View Details</summary>

**1. Personal macOS user path: /Users/[^/ — 2 occurrences (SKILL.md line 111; references/review-checklist.md line 50)**
- File: `SKILL.md:111`
- Check: `personal_paths`
- Finding ID: `SEF-b0462032a92971607328`
- Occurrence ID: `SEO-2b0a62274fc3c0a23da1`
- Content: `| 🟡 警告 | 硬编码绝对路径 | `/Users/[^/\s"]+/[^\s"]+` |`
- Fix: Use generic path like /path/to/file or environment variable like $HOME

**2. Personal macOS user path: /Users/overleazhou/**
- File: `SKILL.md:152`
- Check: `personal_paths`
- Finding ID: `SEF-e9c2cdcee124d83df413`
- Occurrence ID: `SEO-bac7dc6383ce75ea3440`
- Content: `当前：OUTPUT = "/Users/overleazhou/data/"`
- Fix: Use generic path like /path/to/file or environment variable like $HOME

**3. Personal macOS user path: /Users/xxx/ — 2 occurrences (SKILL.md lines 207, 208)**
- File: `SKILL.md:207`
- Check: `personal_paths`
- Finding ID: `SEF-36abbfe1d1016633e227`
- Occurrence ID: `SEO-62dd61da382e94208532`
- Content: `- scripts/export.py:12 → /Users/xxx/data/ → _DIR/data/`
- Fix: Use generic path like /path/to/file or environment variable like $HOME

**4. Personal Windows user path: C:\Users\`**
- File: `references/review-checklist.md:135`
- Check: `personal_paths`
- Finding ID: `SEF-f5063b518af8b30ce7d9`
- Occurrence ID: `SEO-71de21ebd0e53156f6dd`
- Content: `- 搜索结果中无 `/Users/` 开头或 `C:\Users\` 开头的路径 → +1`
- Fix: Use generic path like C:\path\to\file or %USERPROFILE% variable

</details>


### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **code_file_discovery**: No code files found - code risk analysis is not applicable

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ❌ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

**1 errors, 1 warnings**

**Errors:**

- ❌ Dead link in tutorial-template.md: %7B%E6%88%AA%E5%9B%BE%E5%8D%A0%E4%BD%8D%7D


### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:523</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>references/tutorial-template.md:346</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>references/tutorial-template.md:401</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:523`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-7b0ccad30b2ee0565115`
- Content: `### ⚠️ 提交问题时请注意`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `references/tutorial-template.md:346`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-726a5e9aa5780aeccbc1`
- Content: `### ⚙️ 配置相关`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**3. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `references/tutorial-template.md:401`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-6fdee3477d6ebc360dba`
- Content: `### ⚠️ 提交问题时请注意`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 86.5/100 (Grade: B)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 90.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 86.5/100 (Grade: B)

**Non-blocking findings: 8**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-317bb6f4b0daf86d76c8`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-f568a9c0945b8b0f2ed0`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-af96ac0633346d58f965`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-76e38d8837da97838cbc`
- Fix: Add purpose section to clarify use cases

**5. No mention of error handling or validation**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-3e6818d6dd41c6bc2efc`
- Fix: Document expected errors and how to handle them

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-25d8d5f4fba0d2d76df2`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-882f02d31a9a255f34b4`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-00f0ae34fe7571b53303`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 20,702 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/code-review-and-teach/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-bda6cf0b8508c4bcf808`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-315eb7a28fad5b6a6b0f`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. openclaw: SKILL.md reads as 20,702 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-f916df208f03e46f8eb7`
- Occurrence ID: `SEO-a273a6b698d367274c9b`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/code-review-and-teach/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-6324a07177e4ec43113e`

</details>


---
*Generated by SkillEvaluator*