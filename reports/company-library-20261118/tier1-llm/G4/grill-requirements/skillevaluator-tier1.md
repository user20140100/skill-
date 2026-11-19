# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:03 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 13 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 32 unique findings (1 high, 8 medium) / 34 occurrences / 34 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-9afa5f4fc6f0ffc839a2` | HIGH | Rubric evaluation failed: criteria below 7/10: example&#95;quality, error&#95;handling&#95;quality | 1 | RUBRIC&#95;EVAL |
| `SEF-0742370606b64bb7113d` | MEDIUM | The trigger surface is overly broad. The skill activates on generic phrases such as “我想要做个 X”, “需求、想法或功能”, and similar c | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-557a6412a2e8ef047c61` | MEDIUM | &#91;5/10&#93; Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | 1 | RUBRIC&#95;EVAL |
| `SEF-975cec5e5aad0b33739c` | MEDIUM | &#91;5/10&#93; Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | 1 | RUBRIC&#95;EVAL |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-6b66555d1029e567b59c` | LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | 3 | Unicode Smuggling Detection |
| ... | | *22 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| grill-requirements | 86.5 | B | guide-only | 90.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'grill-requirements'
- [OK] **naming_convention**: Folder name 'grill-requirements' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (205/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Skill directory contains only expected files
- [OK] **name_consistency**: Directory name matches frontmatter: 'grill-requirements'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G4/grill-requirements</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G4/grill-requirements`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-50652c4a7f254ce3f0bc`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-bec65eeff4ee6a90855f`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-c7f150e7779559ad6205`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-a7c548ea692577c084dd`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-5e661e757efa2eed2acf`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-8863309fab6c0f94930f`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: Security scan completed - 1 advisory finding(s) (no critical/high issues)
- [OK] **skillspector**: Security scan completed - 2 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | analysis-evasion: Suspicious Unicode normalization or mixed-script content<br><strong>LLM verification:</strong> False positive (high confidence)<br>Reasoning: Mixed Chinese/English content is expected in a Chinese-language skill definition; there is no evidence of Unicode normalization evasion or hidden malicious characters in the provided context.<br>Verifier recorded a downgrade to INFO; reported severity: INFO. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | The trigger surface is overly broad. The skill activates on generic phrases such as “我想要做个 X”, “需求、想法或功能”, and similar c<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: The skill can activate on broad phrases like “我想要做个 X” and then ask for sensitive business/PII fields such as salary and headcount; while file writing requires confirmation, unintended activation can still lead to unwanted sensitive data collection.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:5</code> |

<details>
<summary>View Details</summary>

**1. analysis-evasion: Suspicious Unicode normalization or mixed-script content**
- File: `SKILL.md:1`
- Check: `Unknown (AE4)`
- Finding ID: `SEF-418fdc54080e003ab71d`
- Occurrence ID: `SEO-e45a6d8900da06cdbcd4`
- Fix: Suspicious Unicode normalization or mixed-script content Review the flagged content for security risks. Ensure no credentials, secrets, or sensitive data are exposed.

**2. The trigger surface is overly broad. The skill activates on generic phrases such as “我想要做个 X”, “需求、想法或功能”, and similar c**
- File: `SKILL.md:5`
- Check: `Unknown (SQP-1)`
- Finding ID: `SEF-0742370606b64bb7113d`
- Occurrence ID: `SEO-203719268efa6a14c818`
- Fix: The trigger surface is overly broad. The skill activates on generic phrases such as “我想要做个 X”, “需求、想法或功能”, and similar casual expressions. These phrases can easily appear in non-requirement contexts, such as personal tasks, ordinary conversation, marketing copy, or ambiguous requests. Once triggered, the skill begins a structured interrogation that can collect sensitive organizational information, including roles, headcount, salary information, process times, and business assumptions. It also instructs the agent to generate a `.md` file in the current working directory using the Write tool. If an agent framework automatically selects this skill based on the broad trigger, an unintended or adversarial utterance could cause unwanted data collection, unwanted file creation, workspace pollution, accidental commit of sensitive business information, or user confusion. Reduce the trigger scope and add explicit opt-in before data collection or file writing. Restrict activation to explicit invocations such as `/grill-requirements`, “需求提报”, or unambiguous phrases that clearly refer to internal product/business requirement submission. Add negative examples such as “我想做个饭”, “我想要做个梦”, “帮我做个表格”, “我想要买点东西”, or “帮我理一下人生”, which should not activate the skill. Before asking for sensitive fields such as salary, job title, team names, or business process data, state the purpose, ask for confirmation, and allow the user to skip. Before writing the final `.md`, require explicit confirmation and prefer writing to a temporary or user-selected safe output directory. Add a guard that rejects ambiguous personal/casual requests. Also add tests proving that common non-requirement utterances do not trigger the skill.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 1 files for PII
- [OK] **pii_detection**: No PII detected in 1 files (emails, SSNs, phone numbers, paths)

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

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:88</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:153</code> |
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>SKILL.md:154</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:88`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-1f0dc7fe6a98065047d7`
- Content: `这是**量级估算，不是精确承诺**。文档里必须标注"⚠️ 此评估为 Agent 量级估算，需开发复核"。若需求落在...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:153`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-129992ec30e5cc4fae40`
- Content: `- **风险/不确定**：⚠️ <项>（+X 人天）`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**3. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `SKILL.md:154`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-c501f2ced7543806423a`
- Content: `> ⚠️ 此评估为 Agent 量级估算，需开发复核。`
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
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-989942efae9a75ea7acf`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-f3fbed697c5c92680628`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-92cd08a502531acd4c74`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-a3528d41a9d977e5654e`
- Fix: Add purpose section to clarify use cases

**5. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-31b9101a7024e06f061d`
- Fix: Document expected errors and how to handle them

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-4d5ffd929969709157c9`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-6b2b69bf5a7b2f11bd24`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-f1c72667f26a0f516681`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [INFO] INFO | openclaw: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-a73c818edd210092565b`

**2. copilot-cli: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `CP-DESC-ESCAPED`
- Finding ID: `SEF-5cf1d958d3582b4dd475`
- Occurrence ID: `SEO-6ec888fd7d121373bb5f`
- Fix: Use single quotes in the description if the exact text matters.

**3. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-86e49e611301a68b261b`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**4. openclaw: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `OW-DESC-ESCAPED`
- Finding ID: `SEF-d97cf8343ff688501a4c`
- Occurrence ID: `SEO-c33bc62c7a53e0195d54`
- Fix: Use single quotes in the description if the exact text matters.

**5. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-76d765f50005a3efa06f`

</details>


### ❌ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

**1 errors, 9 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [9/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [MED] MEDIUM | [5/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [8/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [LOW] LOW | [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [MED] MEDIUM | [5/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |
| [HIGH] HIGH | Rubric evaluation failed: criteria below 7/10: example_quality, error_handling_quality | <code>/skills/library-20261118/G4/grill-requirements/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-db6cfaec190ff334af3b`
- Occurrence ID: `SEO-b9b93903744fc8fd71a6`
- Fix: The description clearly defines the skill as a requirements-grilling agent and lists concrete trigger phrases and scenarios.

**2. [9/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-030ee1126ed88f6719d1`
- Occurrence ID: `SEO-a1be54b4e96b7bfbd843`
- Fix: The phased workflow, questioning rules, formulas, and document template are highly actionable and easy to follow.

**3. [5/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-557a6412a2e8ef047c61`
- Occurrence ID: `SEO-4184f202db4c9eee2bc7`
- Fix: Trigger phrases are provided, but there are no full usage examples, sample questions, or varied user scenarios to demonstrate proper execution.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-1730b4619ac61f3e0e4b`
- Occurrence ID: `SEO-a4b7596938dbf942c3ad`
- Fix: Purpose, parameters, formulas, and output format are complete; scripts are not needed for this prompt-based skill.

**5. [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-23aeeebfd65bb115d5e1`
- Occurrence ID: `SEO-12c2ce32d82d02082715`
- Fix: Scope is clearly bounded to requirement clarification and reviewable demand submission, with explicit separation from developer-facing technical work.

**6. [8/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-7d672f0f2be52d2a830b`
- Occurrence ID: `SEO-1d0b6f66ec8eefec3892`
- Fix: The tone is direct and professional, with consistent headings and structured formatting, though it is primarily in Chinese.

**7. [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-9039ab8ca79a814d8bcb`
- Occurrence ID: `SEO-6069239d96a28814efe2`
- Fix: Likely requirement-submission queries should trigger it, while coding/debugging queries should not; however, generic phrases like 'I want to make X' may overlap with implementation skills.

**8. [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-a708cf185063f38c3c5f`
- Occurrence ID: `SEO-3a03f29e3fcde320154a`
- Fix: The workflow covers questioning, complexity estimation, ROI calculation, confirmation, and document generation end-to-end with minimal ambiguity.

**9. [5/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-975cec5e5aad0b33739c`
- Occurrence ID: `SEO-2035bdd7cd6e7fbd3cb4`
- Fix: It defines stopping and confirmation rules but lacks guidance for missing salary data, invalid inputs, user refusal, calculation conflicts, or write failures.

**10. Rubric evaluation failed: criteria below 7/10: example_quality, error_handling_quality**
- File: `/skills/library-20261118/G4/grill-requirements/SKILL.md`
- Check: `rubric_overall`
- Finding ID: `SEF-9afa5f4fc6f0ffc839a2`
- Occurrence ID: `SEO-df9ecd3d928d1bcb0bd3`
- Fix: Address the failed rubric criteria and rerun the evaluation

</details>


---
*Generated by SkillEvaluator*