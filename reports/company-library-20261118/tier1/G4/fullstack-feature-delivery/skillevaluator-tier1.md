# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:02 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 26 unique findings (2 high, 7 medium) / 26 occurrences / 26 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-5644322365b3fb515e6f` | HIGH | Supply Chain: curl -s "https://get.sdkman.io" &#124; bash | 1 | Security Scan |
| `SEF-cd62b9b66b0bc778e56f` | HIGH | Tool Misuse: &#124; bash | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-628a7d771747714032a3` | MEDIUM | Prompt Injection: U+0020 x140 | 1 | Security Scan |
| `SEF-8d40952ee87f1cd10646` | MEDIUM | Non-RFC1918 IP address: 8.0.504.1 | 1 | PII Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-0f13c9a2b82dbd00de46` | LOW | Unexpected 'examples.md' in skill root | 1 | Schema &amp; Repository Governance |
| ... | | *16 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| fullstack-feature-delivery | 89.0 | B | guide-only | 90.0 | 85.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'fullstack-feature-delivery'
- [OK] **naming_convention**: Folder name 'fullstack-feature-delivery' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (158/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **name_consistency**: Directory name matches frontmatter: 'fullstack-feature-delivery'

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G4/fullstack-feature-delivery</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | Unexpected 'examples.md' in skill root | <code>/skills/library-20261118/G4/fullstack-feature-delivery/examples.md</code> |
| [LOW] LOW | Unexpected 'reference.md' in skill root | <code>/skills/library-20261118/G4/fullstack-feature-delivery/reference.md</code> |
| [LOW] LOW | Unexpected 'environment.md' in skill root | <code>/skills/library-20261118/G4/fullstack-feature-delivery/environment.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-a5ffce98c9399b09228b`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-a07fe3a699d530dbbd6f`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-7704576f04537b27f640`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'examples.md' in skill root**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/examples.md`
- Check: `unexpected_file`
- Finding ID: `SEF-0f13c9a2b82dbd00de46`
- Occurrence ID: `SEO-749bebf7db4fed8d0c3a`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Unexpected 'reference.md' in skill root**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/reference.md`
- Check: `unexpected_file`
- Finding ID: `SEF-851b71102bebf398accd`
- Occurrence ID: `SEO-33649a3677f8fe789258`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Unexpected 'environment.md' in skill root**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/environment.md`
- Check: `unexpected_file`
- Finding ID: `SEF-dd9b68f7120aa01d0d0c`
- Occurrence ID: `SEO-7f9dd8f7174789a74af7`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**7. Author not specified in metadata**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-f843f26de51549e3df39`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**8. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-78dddd6918c72599df43`
- Fix: State when to use the skill within the first 60 characters

**9. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-b0a9783aa61c4a3d744c`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**2 errors, 1 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Supply Chain: curl -s "https://get.sdkman.io" &#124; bash | <code>environment.md:80</code> |
| [HIGH] HIGH | Tool Misuse: &#124; bash<br> | <code>environment.md:80</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x140 | <code>reference.md:54</code> |

<details>
<summary>View Details</summary>

**1. Supply Chain: curl -s "https://get.sdkman.io" | bash**
- File: `environment.md:80`
- Check: `External Script Fetching (SC2)`
- Finding ID: `SEF-5644322365b3fb515e6f`
- Occurrence ID: `SEO-6bf19ce8e501e47c81b7`
- Content: `source ~/.zshrc

# 方式二：SDKMAN（多 JDK 并存、切版本方便）
curl -s "ht...`
- Fix: Remote code is downloaded and executed. This bypasses code review and could introduce malicious code. Avoid downloading and executing remote scripts. Use trusted packages from PyPI/npm. If remote fetch is required, verify checksums and use HTTPS.

**2. Tool Misuse: | bash**
- File: `environment.md:80`
- Check: `Chaining Abuse (TM2)`
- Finding ID: `SEF-cd62b9b66b0bc778e56f`
- Occurrence ID: `SEO-d4c1a1a1c454de0c7129`
- Content: `source ~/.zshrc

# 方式二：SDKMAN（多 JDK 并存、切版本方便）
curl -s "ht...`
- Fix: Tool calls are chained to bypass individual safety checks or escalate capabilities beyond what any single tool call would allow. Limit tool chaining depth and validate the output of each tool before passing it to the next. Require explicit user approval for multi-step chains.

**3. Prompt Injection: U+0020 x140**
- File: `reference.md:54`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-628a7d771747714032a3`
- Occurrence ID: `SEO-0540166dbcd6f0ba31c5`
- Content: `### 规范优先的两步判定

| 情形                                      ...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 4 files for PII

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Non-RFC1918 IP address: 8.0.504.1 | <code>environment.md:59</code> |

<details>
<summary>View Details</summary>

**1. Non-RFC1918 IP address: 8.0.504.1**
- File: `environment.md:59`
- Check: `ip_addresses`
- Finding ID: `SEF-8d40952ee87f1cd10646`
- Occurrence ID: `SEO-c066a2e60b09f462b14d`
- Content: `[Environment]::SetEnvironmentVariable('JAVA_HOME','C:\Pro...`
- Fix: Use private IP (10.x.x.x, 192.168.x.x) or placeholder like 0.0.0.0

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

- [OK] **dead_links_scan**: Checking 4 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 4 markdown file(s)
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
| Discoverability | 85.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 89.0/100 (Grade: B)

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-3a5d236b1732501efc6e`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-f2cfe10d4bf15c414955`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-02377da7cff19620c38e`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-44fd2e9d4a8f98c8d2c0`
- Fix: Add purpose section to clarify use cases

**5. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-d079a7611f6bfcca2b82`
- Fix: Document dependencies, API keys, or setup needed

**6. No limitations documented**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-1c966239d5557c4fdf87`
- Fix: Add '## Limitations' section with known issues/constraints

**7. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-68e06745f838c3720669`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [INFO] INFO | hermes: 3 files outside references/, templates/, assets/ and scripts/ (environment.md, examples.md, reference.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [INFO] INFO | openclaw: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-6b56fbf2faae8cdc3f15`

**2. copilot-cli: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `CP-DESC-ESCAPED`
- Finding ID: `SEF-5cf1d958d3582b4dd475`
- Occurrence ID: `SEO-68be690de4033a0f8227`
- Fix: Use single quotes in the description if the exact text matters.

**3. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-ce67428704e22679033d`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**4. hermes: 3 files outside references/, templates/, assets/ and scripts/ (environment.md, examples.md, reference.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-1ff36c073bcb7305eaa0`
- Occurrence ID: `SEO-33c0a62faacdf1e605bf`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**5. openclaw: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `OW-DESC-ESCAPED`
- Finding ID: `SEF-d97cf8343ff688501a4c`
- Occurrence ID: `SEO-799eedb6721a40b68be2`
- Fix: Use single quotes in the description if the exact text matters.

**6. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/fullstack-feature-delivery/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-93b63d101a7fef97f8fe`

</details>


---
*Generated by SkillEvaluator*