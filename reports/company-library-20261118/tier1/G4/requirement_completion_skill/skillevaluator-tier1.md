# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:14 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 10 |
| ❌ Failed | 2 |
| ⚠️ Incomplete | 1 |
| Total Issues | 15 unique findings (2 high, 2 medium) / 15 occurrences / 15 raw records; 1 error and 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-1e025a7a0e11eb6072b2` | HIGH | Invalid name format: 'requirement&#95;completion&#95;skill' (lowercase/numbers/hyphens only) | 1 | QUALITY |
| `SEF-c4e0ec128c9888e2e2b8` | HIGH | Field 'name': Value error, Skill name 'requirement&#95;completion&#95;skill' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter) | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-0d2215183b14101ae2c2` | LOW | No examples provided | 1 | QUALITY |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| `SEF-9612bbfb3f32d491ac5d` | LOW | No mention of error handling or validation | 1 | QUALITY |
| `SEF-b6533ad44b39dbc6d0d2` | LOW | No '&#35;&#35; Purpose' section | 1 | QUALITY |
| ... | | *5 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| requirement_completion_skill | 79.5 | C | guide-only | 70.0 | 85.0 | 75.0 | 100.0 |

## Results

### ❌ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

**1 errors, 1 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Field 'name': Value error, Skill name 'requirement_completion_skill' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter) | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Field 'name': Value error, Skill name 'requirement_completion_skill' must be in kebab-case format (lowercase letters, numbers, and hyphens only, starting with a letter)**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `frontmatter_field`
- Finding ID: `SEF-c4e0ec128c9888e2e2b8`
- Occurrence ID: `SEO-a9d718d028667d136227`
- Fix: Fix the 'name' field in frontmatter according to schema requirements

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ⚠️ INCOMPLETE Security Scan
*Detect security vulnerabilities and PII/secrets*

**Incomplete scanners:** skillspector

**1 errors, 0 warnings**

**Execution errors:**

- ❌ skillspector failed with unexpected exit code 2: scanner diagnostics were redacted


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 48 files for PII
- [OK] **pii_detection**: No PII detected in 48 files (emails, SSNs, phone numbers, paths)

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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 48 file(s)

### ❌ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 79.5/100 (Grade: C)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 70.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

**1 errors, 9 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Invalid name format: 'requirement_completion_skill' (lowercase/numbers/hyphens only) | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Invalid name format: 'requirement_completion_skill' (lowercase/numbers/hyphens only)**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-1e025a7a0e11eb6072b2`
- Occurrence ID: `SEO-8f3195f08c6d1c9eb22f`
- Fix: Use only lowercase letters, numbers, and hyphens

**2. No examples provided**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-2daf50cddc0f4f8277c0`
- Fix: Add example usage with code blocks

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-2e2ae3af134d15bee67b`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-9f881b5644184729f833`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-e600c6dd2937cf717e06`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**6. No '## Purpose' section**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-334708d8ccac34cad842`
- Fix: Add purpose section to clarify use cases

**7. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-bbddc5982407e7fe6139`
- Fix: Document expected errors and how to handle them

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-e006056bf38fd84275a2`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-6ba1ebeff71323a0d444`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-45c5f1a5fb66b1d2c0a5`
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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [INFO] INFO | hermes: 47 files outside references/, templates/, assets/ and scripts/ (core\common_requirement_framework.json, core\task_templates.json, core\维护规范.md +44 more) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/requirement_completion_skill/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-5be991c96abf021258df`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-6d3712c36ee1ffb5a6f7`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 47 files outside references/, templates/, assets/ and scripts/ (core\common_requirement_framework.json, core\task_templates.json, core\维护规范.md +44 more) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-d8ddb017bc4c3f849280`
- Occurrence ID: `SEO-904cf34accc7dc63a917`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/requirement_completion_skill/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-8683d4da258c4a7792e3`

</details>


---
*Generated by SkillEvaluator*