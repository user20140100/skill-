# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 03:18 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 13 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 25 unique findings (1 high, 6 medium) / 25 occurrences / 25 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-2125cfc44adf59f54fe2` | HIGH | Rubric evaluation failed: criteria below 7/10: workflow&#95;completeness | 1 | RUBRIC&#95;EVAL |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-eeac075903ab5cc0f784` | MEDIUM | &#91;6/10&#93; Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | 1 | RUBRIC&#95;EVAL |
| `SEF-059cd11cb393b1e4f415` | LOW | &#91;9/10&#93; Documentation uses professional, consistent tone and formatting | 1 | RUBRIC&#95;EVAL |
| `SEF-0a51360e550d1adb81e7` | LOW | &#91;8/10&#93; Skill scope is well-defined (clear boundaries, not too broad/narrow) | 1 | RUBRIC&#95;EVAL |
| `SEF-0cb4c1cbb173aca8e597` | LOW | &#91;9/10&#93; Description is clear, specific, and explains WHEN to use the skill | 1 | RUBRIC&#95;EVAL |
| ... | | *15 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| ios-crash-analysis | 89.0 | B | guide-only | 90.0 | 85.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'ios-crash-analysis'
- [OK] **naming_convention**: Folder name 'ios-crash-analysis' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (137/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Skill directory contains only expected files
- [OK] **name_consistency**: Directory name matches frontmatter: 'ios-crash-analysis'

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/ios-crash-analysis</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/ios-crash-analysis`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-5e6175001632b14e1c50`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-da03b37eacb3b0100176`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-26c5a10bd0ef9a5dd5ad`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-2474a59e61bd9db5c889`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-2d3264a40e92cf96fb80`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)
- [OK] **skillspector**: No security vulnerabilities detected (secrets, API keys, credentials)

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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 1 file(s)

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

**Non-blocking findings: 8**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | Description very long (212 chars, recommend 50-150) | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | Broad description without negative triggers may cause over-triggering | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-5437b96ab50d6803bd35`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-3a1fe15b8ef3711c2cd9`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description very long (212 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-7090465d13d1a6d92a07`
- Occurrence ID: `SEO-027f0eb6d12c812641ad`
- Fix: Keep descriptions concise for progressive disclosure

**4. Broad description without negative triggers may cause over-triggering**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-1017300978cb9cb0eae9`
- Occurrence ID: `SEO-6646ab75d10f463050af`
- Fix: Add boundary phrases like 'Do NOT use for...'

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-5d15b4bd5eecda954908`
- Fix: Add purpose section to clarify use cases

**6. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-bd137180460f9a89f483`
- Fix: Document dependencies, API keys, or setup needed

**7. No limitations documented**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-98163ed825773e02322f`
- Fix: Add '## Limitations' section with known issues/constraints

**8. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-5a07e19cf41973a4b450`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-4606571f415cd9e35b96`

**2. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-95dccc2021dfbf3d9a1a`

</details>


### ❌ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

**1 errors, 9 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Instructions are easy to follow with clear action steps | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [7/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [8/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [9/10] Documentation uses professional, consistent tone and formatting | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [MED] MEDIUM | [6/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [LOW] LOW | [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |
| [HIGH] HIGH | Rubric evaluation failed: criteria below 7/10: workflow_completeness | <code>/skills/library-20261118/G9/ios-crash-analysis/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-0cb4c1cbb173aca8e597`
- Occurrence ID: `SEO-0e56e37da383a0570c42`
- Fix: The description clearly identifies crash report files, symbolication/root cause analysis, and relevant trigger terms including Chinese.

**2. [9/10] Instructions are easy to follow with clear action steps**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-4ee8fd97f4b56ef2aaa7`
- Occurrence ID: `SEO-ddb47be67626e46f856d`
- Fix: The checklist and numbered steps provide a clear, ordered workflow with concrete commands and expected outputs.

**3. [7/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-fb1238b1f0b8660d65f5`
- Occurrence ID: `SEO-5ee04eb09e6aab97a165`
- Fix: atos and report examples are useful, but the documentation could include more user query variations to improve routing robustness.

**4. [7/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-ba753cc9ded8d89e5f9d`
- Occurrence ID: `SEO-6e9cabd409f2726f10f9`
- Fix: Purpose, inputs, commands, parsing rules, and output format are present, but project/source-code context handling is under-specified.

**5. [8/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-0a51360e550d1adb81e7`
- Occurrence ID: `SEO-4fe79d1346b5d3e5d5db`
- Fix: Scope is focused on iOS/Mac crash report symbolication and root cause analysis without being overly broad.

**6. [9/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-059cd11cb393b1e4f415`
- Occurrence ID: `SEO-49f15dc29ce46ce2374f`
- Fix: The tone is direct and professional, with consistent headings, checklists, and code blocks.

**7. [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-0f9e0edaf28628e88e0b`
- Occurrence ID: `SEO-8ff8c81e12cc26d807f7`
- Fix: It should trigger for crash log/report requests, though non-crash terms like 'app terminated unexpectedly' or 'stack trace' may be missed.

**8. [6/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-eeac075903ab5cc0f784`
- Occurrence ID: `SEO-77f7a225ef2b102f2769`
- Fix: The workflow stops short of telling the agent how to obtain the project path, map symbols to source files, or parse iOS .ips reports.

**9. [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-ec9a2aacd8b20b240f4d`
- Occurrence ID: `SEO-5faaf45011454c6f9d36`
- Fix: UUID mismatch, architecture mismatch, load address issues, and redacted frames are practical, though missing dSYM and malformed report handling could be expanded.

**10. Rubric evaluation failed: criteria below 7/10: workflow_completeness**
- File: `/skills/library-20261118/G9/ios-crash-analysis/SKILL.md`
- Check: `rubric_overall`
- Finding ID: `SEF-2125cfc44adf59f54fe2`
- Occurrence ID: `SEO-8c967ff16126838e379a`
- Fix: Address the failed rubric criteria and rerun the evaluation

</details>


---
*Generated by SkillEvaluator*