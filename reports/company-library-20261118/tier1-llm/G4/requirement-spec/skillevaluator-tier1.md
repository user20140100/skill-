# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:05 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 14 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 36 unique findings (5 medium) / 41 occurrences / 41 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-6b66555d1029e567b59c` | LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | 6 | Unicode Smuggling Detection |
| `SEF-05db62c711970b800938` | LOW | &#91;7/10&#93; Documentation uses professional, consistent tone and formatting | 1 | RUBRIC&#95;EVAL |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-1656313038360319cbe3` | LOW | &#91;9/10&#93; Instructions are easy to follow with clear action steps | 1 | RUBRIC&#95;EVAL |
| `SEF-1cceef2f7b2cba5b5a86` | LOW | &#91;9/10&#93; Description is clear, specific, and explains WHEN to use the skill | 1 | RUBRIC&#95;EVAL |
| ... | | *26 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| requirement-spec | 86.5 | B | guide-only | 90.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'requirement-spec'
- [OK] **naming_convention**: Folder name 'requirement-spec' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (263/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **name_consistency**: Directory name matches frontmatter: 'requirement-spec'

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G4/requirement-spec</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | Unexpected 'docs' in skill root | <code>/skills/library-20261118/G4/requirement-spec/docs</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, intent, keywords, layer, owner, status, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G4/requirement-spec`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-5afcf21373860c3c9ae0`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-e281f69a18571b533e28`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-6172a2786611c2ca2784`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'docs' in skill root**
- File: `/skills/library-20261118/G4/requirement-spec/docs`
- Check: `unexpected_file`
- Finding ID: `SEF-f14ce38b80a35916e803`
- Occurrence ID: `SEO-d18f05d6bbd7c669e78f`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Author not specified in metadata**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-e4a496d871aeae5190d7`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**6. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-1af72e166a86868c6162`
- Fix: State when to use the skill within the first 60 characters

**7. Frontmatter field(s) outside the agentskills.io spec: author, intent, keywords, layer, owner, status, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-f52d28d195f5c9274025`
- Occurrence ID: `SEO-4016b048d95aba623c2c`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)
- [OK] **skillspector**: Security scan completed - 1 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | The skill description uses a broad catch-all trigger condition: “等类似表达时触发” (“or similar expressions”). This is not merel<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: Broad trigger phrasing like 'or similar expressions' is normal for skill routing descriptions and is not a concrete security vulnerability. The skill only guides requirement documentation and writes benign docs; unintended activation would be a UX/routing concern, not a genuine secret, PII, or exploitable security issue.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>SKILL.md:3</code> |

<details>
<summary>View Details</summary>

**1. The skill description uses a broad catch-all trigger condition: “等类似表达时触发” (“or similar expressions”). This is not merel**
- File: `SKILL.md:3`
- Check: `Unknown (SQP-1)`
- Finding ID: `SEF-9d18f50771edc5e9c958`
- Occurrence ID: `SEO-fd69506a5e22d4915f23`
- Fix: The skill description uses a broad catch-all trigger condition: “等类似表达时触发” (“or similar expressions”). This is not merely stylistic ambiguity in a prompt; for an agent skill, trigger conditions control routing and can affect which instructions get loaded into the model context. A loosely related user request may unintentionally activate this skill, especially if the routing system lacks a stricter intent classifier or explicit exclusion logic. The skill also instructs the agent to create/update files such as `docs/requirements/<功能名>.md` and `.progress/<功能名>.md`, so unintended activation can cause unwanted document creation or pollution of project state. In an adversarial context, an attacker could craft a superficially requirements-adjacent message to force this skill into play, potentially causing prompt-routing interference, excessive token consumption, creation of misleading requirement artifacts, or downstream confusion if those artifacts are later used by developers or modeling systems. This is a real operational/security weakness, though it is low-to-medium severity because the skill itself is benign, does not execute code, and mainly affects requirement documentation behavior. Replace vague activation language with precise, closed trigger conditions. For example, require explicit phrases such as “帮我写需求文档”, “把这份需求初稿整理成标准需求文档”, or “从原型反推需求”, and add negative examples such as “不要用于普通问答”“不要用于代码修改”“不要用于发布部署”. Add explicit exclusion conditions: the skill should not activate for general conversation, code review, bug fixing, model training, file deletion, secrets handling, or any request that does not explicitly ask for requirement documentation. Additionally, require user confirmation before writing files, confine all writes to an explicitly configured project directory, and prefer a stricter router/classifier over fuzzy semantic matching for activation.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 5 files for PII
- [OK] **pii_detection**: No PII detected in 5 files (emails, SSNs, phone numbers, paths)

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

- [OK] **dead_links_scan**: Checking 5 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 5 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:251</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:252</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>docs/template.md:67</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>docs/dimensions.md:68</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>docs/prototype-input.md:19</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>docs/prototype-input.md:34</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:251`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-d19c4232d65ed07afc65`
- Content: `2. 拿初稿对照 8 大维度，**逐项标注**：初稿里讲清楚了 ✅、没讲到 ⬜、讲得有冲突 ⚠️。`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:252`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-de7c8fd76f77cd61029c`
- Content: `3. 把 ⬜ 和 ⚠️ 的项挑出来，逐个追问补全。`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**3. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `docs/template.md:67`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-67d17c1a3f19c8fc157c`
- Content: `> ⚠️ 本表所有规则默认要求"前端详情页真实生效"，开发须照此实现。`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**4. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `docs/dimensions.md:68`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-ecfd94c0fc3b1a5ee0b2`
- Content: `**⚠️ 特别强调（针对历史踩坑）：**`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**5. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `docs/prototype-input.md:19`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-3cd0174e7c97b1bd277b`
- Content: `| 维度 1 功能边界 | ⚠️ 部分 | 页面结构看得到，但"走不走审批"看不到 |`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**6. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `docs/prototype-input.md:34`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-9a7293595625825268b0`
- Content: `把第 2 步所有 ⬜（和 ⚠️ 里看不到的部分）汇成一张"待问清单"，逐条用大白话问（问法见 [dimension...`
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
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-8e95b7818a01525b4531`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-7f825c49d3ebfc5f2e3a`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-b8096d16872710601936`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-184f744203bf658d71bf`
- Fix: Add purpose section to clarify use cases

**5. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-9377acdfb0c10296e5eb`
- Fix: Document expected errors and how to handle them

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-0ae07c15dd8c6cd80fde`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-a84ef124d677061cecf7`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-f5594cd8a2abab91f8e0`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 10**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | claude-code: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | hermes: 4 files outside references/, templates/, assets/ and scripts/ (docs) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 17,109 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | openclaw: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [INFO] INFO | opencode: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. claude-code: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `CC-FM-STRIPPED`
- Finding ID: `SEF-970be9580349339dbdb9`
- Occurrence ID: `SEO-be77379bc27b0a876327`
- Fix: Move instructions from frontmatter into the SKILL.md body.

**2. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-11e92440f76c653edcb9`

**3. copilot-cli: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `CP-FM-STRIPPED`
- Finding ID: `SEF-aeca7c7836da523395ee`
- Occurrence ID: `SEO-84104aa9617865b1a4d2`
- Fix: Move instructions from frontmatter into the SKILL.md body.

**4. copilot-cli: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `CP-DESC-ESCAPED`
- Finding ID: `SEF-5cf1d958d3582b4dd475`
- Occurrence ID: `SEO-1392564b931043441e25`
- Fix: Use single quotes in the description if the exact text matters.

**5. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-0b62fea1a1714dadc7a1`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**6. hermes: 4 files outside references/, templates/, assets/ and scripts/ (docs) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-52a186aa73545b962846`
- Occurrence ID: `SEO-a5348761b23bc4d3fd33`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**7. openclaw: SKILL.md reads as 17,109 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-58c1836ef0ce8d798298`
- Occurrence ID: `SEO-7b443c81624a488c5c36`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**8. openclaw: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `OW-DESC-ESCAPED`
- Finding ID: `SEF-d97cf8343ff688501a4c`
- Occurrence ID: `SEO-c934f914cdc3cabae40c`
- Fix: Use single quotes in the description if the exact text matters.

**9. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-fad22bd1afdb2389aea4`

**10. opencode: Frontmatter is stripped when the skill is used, so the text in layer, keywords, intent, owner, status never reaches the model.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `OC-FM-STRIPPED`
- Finding ID: `SEF-3be41c9d8e1b94dbb136`
- Occurrence ID: `SEO-509f0e959d9c4b820e00`
- Fix: Move instructions from frontmatter into the SKILL.md body.

</details>


### ✅ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

- [OK] **rubric_eval**: LLM Rubric Score: 84.1/100

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [9/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [7/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |
| [LOW] LOW | [9/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G4/requirement-spec/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-1cceef2f7b2cba5b5a86`
- Occurrence ID: `SEO-ffb8e1ee3122205281d1`
- Fix: The description clearly lists trigger phrases and states the skill’s purpose. It also explicitly excludes modeling, coding, and publishing.

**2. [9/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-1656313038360319cbe3`
- Occurrence ID: `SEO-a4dad8e0caf8eb4cfde0`
- Fix: The workflow is divided into concrete phases, dimensions, progress files, and finalization steps. It is dense but very actionable.

**3. [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-c4bad029cf3dd7f1de24`
- Occurrence ID: `SEO-02eb18e1982f8856576e`
- Fix: It provides many plain-language interview examples and several trigger phrases. It lacks explicit negative or edge-case queries for robust routing.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-26027b1f2ffe27366482`
- Occurrence ID: `SEO-d9e5da24f8643ed76cca`
- Fix: Purpose, linked documents, templates, file paths, and completion conditions are all present. Scripts are not needed for this guidance skill.

**5. [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-7fa661b6c914b886db23`
- Occurrence ID: `SEO-c97a7ca9249db88ebb50`
- Fix: The scope is clearly limited to requirement clarification and document production. Module, prototype, and draft inputs are handled as bounded variants.

**6. [7/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-05db62c711970b800938`
- Occurrence ID: `SEO-4097daf701d6f4965f9a`
- Fix: Formatting is consistent and structured. The tone is intentionally colloquial and forceful, which is less formally professional but suitable for non-technical users.

**7. [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-7e217c87cb240f462ba5`
- Occurrence ID: `SEO-b77ea5a61a6aad9d0626`
- Fix: Most requirement-document requests would route correctly, and the no-code/no-model boundary reduces false positives. Phrases like “develop a feature” could still overlap with implementation requests.

**8. [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-d3a0a8c743a0ef82ca10`
- Occurrence ID: `SEO-623b337a63651fd228a6`
- Fix: The skill covers intent clarification, structured interviews, conflict checking, progress persistence, finalization, and special input modes. It is nearly end-to-end for its scope.

**9. [9/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G4/requirement-spec/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-b9a21d560e8f541030d4`
- Occurrence ID: `SEO-d7f47754eb642d0b6152`
- Fix: It addresses real failure modes such as context loss, contradictions, prototype placeholders, and premature closure. The mitigations are concrete and operationally useful.

</details>


---
*Generated by SkillEvaluator*