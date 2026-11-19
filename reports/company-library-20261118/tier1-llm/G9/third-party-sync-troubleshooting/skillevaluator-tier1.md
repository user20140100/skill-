# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:19 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 14 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 27 unique findings (5 medium) / 27 occurrences / 27 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-035ac0103677ab4d660b` | LOW | &#91;9/10&#93; Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | 1 | RUBRIC&#95;EVAL |
| `SEF-09421907cbfc932b865e` | LOW | &#91;9/10&#93; Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | 1 | RUBRIC&#95;EVAL |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-28fce7fe359252745e94` | LOW | This is a real operational safety weakness, though not a malicious vulnerability. The skill instructs the analyst/operat | 1 | Security Scan |
| `SEF-29923f4d680e578e37e3` | LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | 1 | Schema &amp; Repository Governance |
| ... | | *17 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| third-party-sync-troubleshooting | 86.5 | B | guide-only | 90.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'third-party-sync-troubleshooting'
- [OK] **naming_convention**: Folder name 'third-party-sync-troubleshooting' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (116/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: references
- [OK] **name_consistency**: Directory name matches frontmatter: 'third-party-sync-troubleshooting'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-164902a275e5f2b267d8`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-de1c03beaf056e8ee208`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-a511a2f7b96a29c726b1`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-ce6f6fed62ee27b4ed60`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-4761c7fa7b90557e92aa`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-483c504e146197bc3b14`
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
| [LOW] LOW | This is a real operational safety weakness, though not a malicious vulnerability. The skill instructs the analyst/operat<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: The skill appears to direct a state-changing production sync without explicit approval, rollback, or side-effect warnings, which is a genuine low-severity operational safety issue for an agent skill.<br>Reported severity: LOW; only high-confidence false positives are downgraded to INFO by verification. | <code>references/timetable-sync-anomaly.md:496</code> |

<details>
<summary>View Details</summary>

**1. This is a real operational safety weakness, though not a malicious vulnerability. The skill instructs the analyst/operat**
- File: `references/timetable-sync-anomaly.md:496`
- Check: `Unknown (SQP-2)`
- Finding ID: `SEF-28fce7fe359252745e94`
- Occurrence ID: `SEO-e0d2b79176423de13d4b`
- Fix: This is a real operational safety weakness, though not a malicious vulnerability. The skill instructs the analyst/operator to manually trigger a third-party data sync to verify whether a missing timetable entry can be restored. A manual sync is a state-changing operation: it can pull fresh third-party data, overwrite or insert timetable-related records, update sync metadata, affect downstream product behavior, or temporarily expose users to inconsistent data if the source is unhealthy. The document does not include an explicit warning, confirmation requirement, rollback note, or instruction to obtain user/operator approval before triggering the sync. If an AI agent or junior operator follows the skill mechanically, this could lead to unintended production changes. However, the skill is framed as a troubleshooting guide for authorized internal operators, and manually triggering sync is a legitimate diagnostic step in that context, so the likely intent is benign/negligent rather than adversarial. The impact is low because the action generally requires access to XXL-JOB, an edge job handler, or internal operational tooling, and the sync is usually expected behavior for the troubleshooting scenario. Still, for an agent skill, missing side-effect warnings around state-changing actions should be treated as a low-severity vulnerability. Add an explicit safety warning immediately before the manual trigger step. The warning should state that manually triggering a timetable sync is a state-changing operation that may update or overwrite timetable data, change third-party sync records, or affect product-facing behavior. Require confirmation from the user or operations owner before proceeding, especially in production. Recommend first recording the affected tenant/unit/thirdCode, current sync record state, and planned verification steps. Prefer a controlled or dry-run approach if available. Explicitly forbid creating fake sync records or manually modifying database rows to simulate execution. If the agent lacks approval or cannot verify the safety of the operation, instruct it to stop and escalate to a human maintainer.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 2 files for PII
- [OK] **pii_detection**: No PII detected in 2 files (emails, SSNs, phone numbers, paths)

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

- [OK] **dead_links_scan**: Checking 2 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 2 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 2 file(s)

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
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Description very long (250 chars, recommend 50-150) | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-097b193dafed4d461800`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-694d69f7efc54da6d53a`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description very long (250 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-87332366f5f7f4cb6384`
- Occurrence ID: `SEO-f8a9ef493509e710a8d1`
- Fix: Keep descriptions concise for progressive disclosure

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-9cd658ff920728118d3f`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No mention of error handling or validation**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-2ac050fd74b6367cdace`
- Fix: Document expected errors and how to handle them

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-5d5f51c3dd79ca8c80f3`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-db16687706a8cd18ef25`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-1c921a1471002e638e4c`
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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-f67104fae9810bae63ed`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-9fa37ea017b8a3c7dd8a`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-de9f378ed2af10f97bbd`

</details>


### ✅ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

- [OK] **rubric_eval**: LLM Rubric Score: 83.2/100

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [9/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [7/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [9/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [7/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |
| [LOW] LOW | [9/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-c9f81e25651d4e2d0908`
- Occurrence ID: `SEO-3aea8bb3bbbac228b128`
- Fix: The description clearly lists applicable sync troubleshooting scenarios, tables, and keywords. It is specific to third-party data sync in the current repository.

**2. [9/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-4037b9540ace489a4b50`
- Occurrence ID: `SEO-d79f9c7b1078a46f0627`
- Fix: The usage steps are explicit, ordered, and emphasize classification before reading branch documents. The workflow is easy for an agent to follow.

**3. [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-71d57f4bb9179c1db1c6`
- Occurrence ID: `SEO-94e10493b32fc42cddf2`
- Fix: SQL examples and enum mappings are practical and relevant. Detection coverage is strong for timetable issues but narrower for other sync types mentioned in the description.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-deb3f71606250e69d5cb`
- Occurrence ID: `SEO-a10cf75c3515f6633201`
- Fix: Purpose, tables, SQL templates, parameters, and constraints are well documented. There are no executable scripts, but the SQL-based workflow is sufficiently complete.

**5. [7/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-bb1d2b633590aaec5edd`
- Occurrence ID: `SEO-8da52e2e2ddaebda8aa8`
- Fix: The implemented branch is clearly scoped to timetable sync anomalies. The frontmatter description is somewhat broader than the currently supported workflow.

**6. [9/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-bf8473e4c9dcbfaa4eef`
- Occurrence ID: `SEO-a51562f3cffca2915ddb`
- Fix: The documentation is consistently structured with headings, tables, and clear Chinese operational language. Formatting is professional and easy to scan.

**7. [7/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-d06844a7d4c2f50392d4`
- Occurrence ID: `SEO-456e745c3080e11a4c90`
- Fix: It would correctly trigger for classroom timetable missing, sync not updated, black/white filter, sync log error, and manual sync questions. It may overtrigger for non-timetable third-party sync issues because the description is broad while only one branch exists.

**8. [9/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-035ac0103677ab4d660b`
- Occurrence ID: `SEO-2740b4f4890ed82be013`
- Fix: The timetable troubleshooting path is end-to-end from input validation through prechecks, SQL, filters, errors, manual sync, and conclusions. Cloud-side log inspection details are slightly less explicit than edge-side guidance.

**9. [9/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G9/third-party-sync-troubleshooting/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-09421907cbfc932b865e`
- Occurrence ID: `SEO-9cad334717e203fa82e2`
- Fix: Error cases are realistic and actionable, including missing cron config, no sync record, missing room relation, filtering, and sync exceptions. The guidance avoids generic boilerplate and ties conclusions to concrete data checks.

</details>


---
*Generated by SkillEvaluator*