# SkillEvaluator Validation Report

**Status:** ✅ PASSED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 17, 2026 at 11:58 PM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 14 |
| ❌ Failed | 0 |
| ⚠️ Incomplete | 0 |
| Total Issues | 21 unique findings (4 medium) / 21 occurrences / 21 raw records; 1 warning without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| `SEF-29923f4d680e578e37e3` | LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | 1 | Schema &amp; Repository Governance |
| `SEF-303c431451b7c05652fe` | LOW | &#91;9/10&#93; Description is clear, specific, and explains WHEN to use the skill | 1 | RUBRIC&#95;EVAL |
| `SEF-4a6560f4aec006f302f9` | LOW | No prerequisites/requirements documented | 1 | QUALITY |
| `SEF-4b285b0f474fff9a859e` | LOW | &#91;7/10&#93; Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | 1 | RUBRIC&#95;EVAL |
| `SEF-4e07b371874fccc7510b` | LOW | &#91;8/10&#93; Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | 1 | RUBRIC&#95;EVAL |
| ... | | *11 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| calculator | 87.5 | B | script-based | 75.0 | 90.0 | 95.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'calculator'
- [OK] **naming_convention**: Folder name 'calculator' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (66/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **body_recommended_section**: Found recommended section: '## Instructions' (or '## Usage')
- [OK] **body_recommended_section**: Found recommended section: '## Examples'
- [OK] **optional_files**: Found optional supporting files: evals, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'calculator'
- [OK] **author_format**: Valid author format: SkillEvaluator Maintainers <maintainers@example.com>

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/official/calculator</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/official/calculator/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/official/calculator`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-091c1b97144523a2b1fb`
- Fix: General skills should be at: skills/<skill-name>/

**2. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/official/calculator/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-2c26d623980983580300`
- Fix: State when to use the skill within the first 60 characters

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

- [OK] **pii_scan_start**: Scanning 2 files for PII
- [OK] **pii_detection**: No PII detected in 2 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (allowed)

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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 2 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 87.5/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 75.0 | 35% |
| Discoverability | 90.0 | 25% |
| Reliability | 95.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 87.5/100 (Grade: B)

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/official/calculator/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/official/calculator/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/official/calculator/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/official/calculator/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-3647bf608e2e24ddf09b`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/official/calculator/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-ae085ffa28bc6bd722af`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/official/calculator/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-7e59929cf3af53e0a395`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/official/calculator/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-86db7bb57a4960ff64ee`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No prerequisites/requirements documented**
- File: `/skills/official/calculator/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-297e3ad508d1c58f90f6`
- Fix: Document dependencies, API keys, or setup needed

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | calc.py contains magic numbers | <code>/skills/official/calculator/scripts/calc.py</code> |

<details>
<summary>View Details</summary>

**1. calc.py contains magic numbers**
- File: `/skills/official/calculator/scripts/calc.py`
- Check: `magic_numbers`
- Finding ID: `SEF-fd5f99a26a70f6058e51`
- Occurrence ID: `SEO-4c4cd9844408a7c165b0`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/official/calculator/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/official/calculator/SKILL.md</code> |
| [INFO] INFO | hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/official/calculator/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/official/calculator/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/official/calculator/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-272180df23d1158e35b3`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/official/calculator/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-95c7d7fe16bdd053f549`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/official/calculator/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-5995c1ef72651542c573`
- Occurrence ID: `SEO-69238ef4a5311336ae91`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/official/calculator/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-34322e3fc320f6c7e8fd`

</details>


### ✅ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

- [OK] **rubric_eval**: LLM Rubric Score: 80.5/100

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [9/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [8/10] Instructions are easy to follow with clear action steps | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [9/10] Documentation uses professional, consistent tone and formatting | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/official/calculator/SKILL.md</code> |
| [LOW] LOW | [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/official/calculator/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [9/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-303c431451b7c05652fe`
- Occurrence ID: `SEO-687e6f91c5ea4bd964ed`
- Fix: The description clearly states the calculator evaluates arithmetic, percentages, exponents, and common unit conversions. It also mentions no external dependencies, which helps set expectations.

**2. [8/10] Instructions are easy to follow with clear action steps**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-a5f81ec9846db09acafe`
- Occurrence ID: `SEO-10a6e956b5842a68b71f`
- Fix: The three-step agent instructions are simple and actionable. More detail about input quoting, error handling, and result formatting would improve clarity.

**3. [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-4e07b371874fccc7510b`
- Occurrence ID: `SEO-ced1d66a02ebf1cce868`
- Fix: Examples cover arithmetic, percentages, and several unit conversions. Additional edge cases or negative examples would better support robust detection and usage.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-68b29e45f1fa2641fbe4`
- Occurrence ID: `SEO-d04eac60e7343ee16cba`
- Fix: Purpose, script location, compatibility, limitations, and examples are present. CLI parameters are implied but not formally documented.

**5. [9/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-544de964e7a872b46c41`
- Occurrence ID: `SEO-412974d41b9ad4565791`
- Fix: The limitations section clearly defines supported operations and conversion units. Scope is appropriately narrow for a safe calculator skill.

**6. [9/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-527523eea1d8884ff4be`
- Occurrence ID: `SEO-b6c96542d74de909c9ad`
- Fix: The documentation is concise, consistent, and professionally formatted. Metadata and compatibility information are clean and useful.

**7. [8/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-8fc7b194e255203476b2`
- Occurrence ID: `SEO-a5b7fe6a9c353cea5371`
- Fix: The description should correctly trigger for arithmetic, percentage, and supported conversion queries. It may under-trigger for broader math requests like solving equations, but that is appropriate given the limitations.

**8. [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-4b285b0f474fff9a859e`
- Occurrence ID: `SEO-b49104b0b8fcd1fa9872`
- Fix: The basic run-and-return workflow is complete. Guidance is missing for malformed input, unsupported conversions, script failures, and exact output handling.

**9. [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/official/calculator/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-69dfa61e380b41fc47dc`
- Occurrence ID: `SEO-e38747cf8ca45d34c097`
- Fix: The troubleshooting table identifies realistic invalid expression and unknown conversion cases with useful fixes. It could be stronger with exact error messages, exit codes, or fallback behavior.

</details>


---
*Generated by SkillEvaluator*