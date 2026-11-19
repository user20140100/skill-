# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:01 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 17 unique findings (1 high, 5 medium) / 17 occurrences / 17 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-84d95de439d61838eebd` | HIGH | Privilege Escalation: Access Token | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| `SEF-7d8d9f72f99ec61dbf58` | LOW | Author not specified in metadata | 1 | Schema &amp; Repository Governance |
| `SEF-9612bbfb3f32d491ac5d` | LOW | No mention of error handling or validation | 1 | QUALITY |
| ... | | *7 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| local-code-review | 89.0 | B | guide-only | 90.0 | 95.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'local-code-review'
- [OK] **naming_convention**: Folder name 'local-code-review' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (83/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: README.md
- [OK] **name_consistency**: Directory name matches frontmatter: 'local-code-review'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/local-code-review</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | Unexpected 'reference' in skill root | <code>/skills/library-20261118/G2/local-code-review/reference</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/local-code-review`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-3aa13ced320bbc179c75`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-d608d91dc7d49ed13c9b`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-5ee4b1bf5836e3cc1ab5`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'reference' in skill root**
- File: `/skills/library-20261118/G2/local-code-review/reference`
- Check: `unexpected_file`
- Finding ID: `SEF-9fafd49f24fef593fe4f`
- Occurrence ID: `SEO-03bc6ae9c8c108572822`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Author not specified in metadata**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-4db78c954f79348509e3`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-7799ceee15d8353f0d6b`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Privilege Escalation: Access Token | <code>reference/gitlab-api.md:3</code> |

<details>
<summary>View Details</summary>

**1. Privilege Escalation: Access Token**
- File: `reference/gitlab-api.md:3`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-84d95de439d61838eebd`
- Occurrence ID: `SEO-fe0d292dc7812e11b594`
- Content: `# GitLab API Reference

需设置环境变量 `GITLAB_TOKEN`（Personal A...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

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

- [OK] **code_file_discovery**: No code files found - code risk analysis is not applicable

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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 4 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 89.0/100 (Grade: B)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 90.0 | 35% |
| Discoverability | 95.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 89.0/100 (Grade: B)

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-b0bf0230ef4302630ab1`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-72b45a6d4278240e7e1b`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. No '## Purpose' section**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-8853fa475d7573eede0f`
- Fix: Add purpose section to clarify use cases

**4. No mention of error handling or validation**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-b291b5f778b88781117d`
- Fix: Document expected errors and how to handle them

**5. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-55e5c98a1adfe05ef11e`
- Fix: Document dependencies, API keys, or setup needed

**6. No limitations documented**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-0914ab862a130f59ecc9`
- Fix: Add '## Limitations' section with known issues/constraints

**7. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-f5a38d8c7e82031f7a3e`
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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [INFO] INFO | hermes: 3 files outside references/, templates/, assets/ and scripts/ (README.md, reference) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/local-code-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-bdd52c2d9e06ee40c1b0`

**2. hermes: 3 files outside references/, templates/, assets/ and scripts/ (README.md, reference) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-a9b329eeb219a3da8dd8`
- Occurrence ID: `SEO-6a40d625bf1bd413f732`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/local-code-review/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-ee9fec7f7d82a3b19f2f`

</details>


---
*Generated by SkillEvaluator*