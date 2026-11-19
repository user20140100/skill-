# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 09:56 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 13 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 22 unique findings (6 medium) / 22 occurrences / 22 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-29923f4d680e578e37e3` | LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | 1 | Schema &amp; Repository Governance |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| ... | | *12 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| calc-pro | 80.0 | B | script-based | 75.0 | 85.0 | 70.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'calc-pro'
- [OK] **naming_convention**: Folder name 'calc-pro' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (82/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: evals, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'calc-pro'

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/positive/calc-pro</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [INFO] INFO | Author has no email address: 杨宇涵 | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/positive/calc-pro/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/positive/calc-pro`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-9f6d3798f580117f7462`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-33c15e553c987b1d603b`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-37eefd50b8240b2448c0`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author has no email address: 杨宇涵**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `author_without_email`
- Finding ID: `SEF-f0bfc06160374b4279da`
- Occurrence ID: `SEO-c2286d513901e5c80e32`
- Content: `author: 杨宇涵`
- Fix: A name is accepted as attribution unless the profile requires a contact address (such as 'registry'); then use 'Name <email@example.com>'

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-5cc04e98949d63692752`
- Fix: State when to use the skill within the first 60 characters

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)

### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 5 files for PII
- [OK] **pii_detection**: No PII detected in 5 files (emails, SSNs, phone numbers, paths)

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

- [OK] **dead_links_scan**: Checking 1 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 1 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 5 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 80.0/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 75.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 70.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 80.0/100 (Grade: B)

**Non-blocking findings: 10**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | Scripts may lack error handling: cli.py, finance.py | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/positive/calc-pro/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-db3b1a4e555c5f28a95c`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-a134e6857ff7a75a4ad4`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-e85e4415b54c8d7a5510`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-ab72274ce4a5bd0837fe`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No '## Purpose' section**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-aca95b72f3e6e4a419e2`
- Fix: Add purpose section to clarify use cases

**6. No mention of error handling or validation**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-31096f8ea3d7fa9b2e98`
- Fix: Document expected errors and how to handle them

**7. Scripts may lack error handling: cli.py, finance.py**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-b6aeaebd5281b2cbe6e0`
- Occurrence ID: `SEO-f745ca58391ed8ff3eb1`
- Fix: Scripts should handle errors explicitly

**8. No prerequisites/requirements documented**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-2c737abdb71c9f9dcff9`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-a44e409dad6a40170ef5`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-04b0dde85d7429f4e897`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | calc.py contains magic numbers | <code>/skills/positive/calc-pro/scripts/calc.py</code> |
| [LOW] LOW | finance.py contains magic numbers | <code>/skills/positive/calc-pro/scripts/finance.py</code> |
| [LOW] LOW | stats.py contains magic numbers | <code>/skills/positive/calc-pro/scripts/stats.py</code> |

<details>
<summary>View Details</summary>

**1. calc.py contains magic numbers**
- File: `/skills/positive/calc-pro/scripts/calc.py`
- Check: `magic_numbers`
- Finding ID: `SEF-fd5f99a26a70f6058e51`
- Occurrence ID: `SEO-264a6151e5915b75627d`
- Fix: Extract magic numbers to named constants

**2. finance.py contains magic numbers**
- File: `/skills/positive/calc-pro/scripts/finance.py`
- Check: `magic_numbers`
- Finding ID: `SEF-aeb6f7a3e8e6331389a3`
- Occurrence ID: `SEO-d526565e34e3fe3357a4`
- Fix: Extract magic numbers to named constants

**3. stats.py contains magic numbers**
- File: `/skills/positive/calc-pro/scripts/stats.py`
- Check: `magic_numbers`
- Finding ID: `SEF-e7a649710617df86ac5a`
- Occurrence ID: `SEO-8899e9e98ba92a1ebcc3`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [INFO] INFO | hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/positive/calc-pro/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/positive/calc-pro/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-fe94bff7e01d47368e71`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-e9645d55d04310e232b1`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-5995c1ef72651542c573`
- Occurrence ID: `SEO-c1c9250cf41afeaf1f60`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/positive/calc-pro/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-a5bcbadf863652a09ead`

</details>


---
*Generated by SkillEvaluator*