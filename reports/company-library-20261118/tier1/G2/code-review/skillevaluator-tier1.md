# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 12:51 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 19 unique findings (1 high, 5 medium) / 19 occurrences / 19 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-f780d705ad2e2c116555` | HIGH | Non-placeholder email address: git&#64;gitlab.gz.cvte.cn | 1 | PII Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-1017300978cb9cb0eae9` | LOW | Broad description without negative triggers may cause over-triggering | 1 | QUALITY |
| `SEF-26ae867438541f95b31a` | LOW | Description very long (282 chars, recommend 50-150) | 1 | QUALITY |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| ... | | *9 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| code-review | 86.5 | B | guide-only | 90.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'code-review'
- [OK] **naming_convention**: Folder name 'code-review' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (167/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Skill directory contains only expected files
- [OK] **name_consistency**: Directory name matches frontmatter: 'code-review'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/code-review</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | Description has its trigger at characters 68-87; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/code-review`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-fa627ecf315c877146c5`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-8bae42579217e27586e8`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-4d9b7ab6dcafe2a75f21`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-65ca9cbf80ce54b23ba5`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has its trigger at characters 68-87; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-777cec5b8a735acc617d`
- Occurrence ID: `SEO-7ffa0800038d04b04784`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-20d91d31359d8636ef9b`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)

### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Non-placeholder email address: git@gitlab.gz.cvte.cn | <code>SKILL.md:54</code> |

<details>
<summary>View Details</summary>

**1. Non-placeholder email address: git@gitlab.gz.cvte.cn**
- File: `SKILL.md:54`
- Check: `emails`
- Finding ID: `SEF-f780d705ad2e2c116555`
- Occurrence ID: `SEO-1b9733c1b8917fdd50ca`
- Content: `git clone git@gitlab.gz.cvte.cn:OSCore/screenshare/base_l...`
- Fix: Keep the metadata.author attribution. Replace other contact addresses with a handle, a contact-directory link, or user@example.com; use a reviewed --pii-waivers entry if the address is required.

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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 1 file(s)

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

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | Description very long (282 chars, recommend 50-150) | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | Broad description without negative triggers may cause over-triggering | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-a6719fd07146c97245ae`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-850b9ff682ae1ac0f614`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description very long (282 chars, recommend 50-150)**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-26ae867438541f95b31a`
- Occurrence ID: `SEO-2f7e175472d8f3cd374b`
- Fix: Keep descriptions concise for progressive disclosure

**4. Broad description without negative triggers may cause over-triggering**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-1017300978cb9cb0eae9`
- Occurrence ID: `SEO-a779a1bddd80afedc6b2`
- Fix: Add boundary phrases like 'Do NOT use for...'

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-32c1e4746c72dac95bf9`
- Fix: Add purpose section to clarify use cases

**6. No mention of error handling or validation**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-fdd753873da29be337b7`
- Fix: Document expected errors and how to handle them

**7. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-23245d0cefb0a13cbc8b`
- Fix: Document dependencies, API keys, or setup needed

**8. No limitations documented**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-9d8c66ec4623b9d07ab2`
- Fix: Add '## Limitations' section with known issues/constraints

**9. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-f9dac0411ac594e6db07`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-b489fad8d6063ee9a02d`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-ebba846eda490c9acf9b`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/code-review/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-61d24b144fcaef89b743`

</details>


---
*Generated by SkillEvaluator*