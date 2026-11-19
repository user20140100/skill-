# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:28 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 11 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 1 |
| Total Issues | 22 unique findings (1 high, 6 medium) / 22 occurrences / 22 raw records; 1 error and 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-f780d705ad2e2c116555` | HIGH | Non-placeholder email address: git&#64;gitlab.gz.cvte.cn | 1 | PII Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-d9ddf78b25e0360b8da4` | MEDIUM | Windows-style paths detected | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-1017300978cb9cb0eae9` | LOW | Broad description without negative triggers may cause over-triggering | 1 | QUALITY |
| `SEF-378f24adfec67572e606` | LOW | No troubleshooting section documented | 1 | QUALITY |
| `SEF-7d8d9f72f99ec61dbf58` | LOW | Author not specified in metadata | 1 | Schema &amp; Repository Governance |
| ... | | *12 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| crashmonitor | 86.0 | B | guide-only | 80.0 | 85.0 | 90.0 | 95.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'crashmonitor'
- [OK] **naming_convention**: Folder name 'crashmonitor' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (171/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: evals, references
- [OK] **name_consistency**: Directory name matches frontmatter: 'crashmonitor'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/crashmonitor</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Description has its trigger at characters 140-163; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/crashmonitor`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-cbf2df41c8d444b3ad4f`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-33634d6834a6c795c620`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-88071923d8a786f56f60`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-e6cf1e643902bd494b4b`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has its trigger at characters 140-163; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-e4d7d269f616b58c0425`
- Occurrence ID: `SEO-59e2b845978f303baec8`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-0c9900d62cb71c5110ac`
- Fix: Remove them or move them under 'metadata'

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


### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Non-placeholder email address: git@gitlab.gz.cvte.cn | <code>SKILL.md:47</code> |

<details>
<summary>View Details</summary>

**1. Non-placeholder email address: git@gitlab.gz.cvte.cn**
- File: `SKILL.md:47`
- Check: `emails`
- Finding ID: `SEF-f780d705ad2e2c116555`
- Occurrence ID: `SEO-4e2bf7cc292e4aa158c4`
- Content: `**GitLab repo:** `git@gitlab.gz.cvte.cn:lixiang21514/cras...`
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

- [OK] **dead_links_scan**: Checking 3 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 3 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 3 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 86.0/100 (Grade: B)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 80.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 90.0 | 25% |
| Efficiency | 95.0 | 15% |

- [OK] **quality_score**: Score: 86.0/100 (Grade: B)

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Windows-style paths detected | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Description very long (758 chars, recommend 50-150) | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Broad description without negative triggers may cause over-triggering | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [LOW] LOW | Non-descriptive filename: cli.md | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Windows-style paths detected**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-d9ddf78b25e0360b8da4`
- Occurrence ID: `SEO-188318d145b1bc2ed8a7`
- Fix: Use forward slashes for cross-platform compatibility

**2. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-98aa870240365e7ef7d1`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-34ac5893c06337252e4f`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description very long (758 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-f6b6002ca1ca4797ad07`
- Occurrence ID: `SEO-103eb6f55f0af76981c8`
- Fix: Keep descriptions concise for progressive disclosure

**5. Broad description without negative triggers may cause over-triggering**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-1017300978cb9cb0eae9`
- Occurrence ID: `SEO-d8b2e3d11dcd30640ae3`
- Fix: Add boundary phrases like 'Do NOT use for...'

**6. No '## Purpose' section**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-bb6746d05450705afadf`
- Fix: Add purpose section to clarify use cases

**7. No limitations documented**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-61caf799dc4fc40e0573`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-cb88326751bdd924cf76`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

**9. Non-descriptive filename: cli.md**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `quality_efficiency`
- Finding ID: `SEF-d84506aaedf4230a61af`
- Occurrence ID: `SEO-71d87c95fdb4757bca57`
- Fix: Use descriptive names: 'form_validation_rules.md' not 'doc2.md'

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [INFO] INFO | openclaw: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/crashmonitor/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-280391b4b338864d59f8`

**2. copilot-cli: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `CP-DESC-ESCAPED`
- Finding ID: `SEF-5cf1d958d3582b4dd475`
- Occurrence ID: `SEO-ffeb77ded4dba08ac6a0`
- Fix: Use single quotes in the description if the exact text matters.

**3. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-5248c9e71584c96e0d73`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**4. hermes: 1 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-6cbbecba76bdeffda77b`
- Occurrence ID: `SEO-699ff39a3e51d584ca0d`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**5. openclaw: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `OW-DESC-ESCAPED`
- Finding ID: `SEF-d97cf8343ff688501a4c`
- Occurrence ID: `SEO-c3474a8909fd30aca4f2`
- Fix: Use single quotes in the description if the exact text matters.

**6. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/crashmonitor/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-26148591cada2f98412f`

</details>


---
*Generated by SkillEvaluator*