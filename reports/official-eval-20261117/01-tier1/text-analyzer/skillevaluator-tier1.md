# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 17, 2026 at 03:01 PM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 14 |
| Validators Run | 14 |
| ✅ Passed | 13 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 24 unique findings (1 high, 7 medium) / 24 occurrences / 24 raw records; 1 warning without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-d227d8fa7e50299e84f8` | HIGH | Rubric evaluation failed: criteria below 7/10: trigger&#95;simulation | 1 | RUBRIC&#95;EVAL |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-6d68dab37ccc357a6814` | MEDIUM | Instructions don't mention 'run&#95;script' | 1 | QUALITY |
| `SEF-740453e5661b3b5b6f1e` | MEDIUM | No documented scripts in table format | 1 | QUALITY |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| `SEF-9e47eb4416d98778cbca` | MEDIUM | MCP Least Privilege: This is a true scope/least-privilege issue. The skill intentionally supports reading files through &#96;--file /path/to/file | 1 | Security Scan |
| `SEF-bc0939ffa25431c513d4` | MEDIUM | &#91;6/10&#93; Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | 1 | RUBRIC&#95;EVAL |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-17679b593e006f8c575d` | LOW | &#91;8/10&#93; Instructions are easy to follow with clear action steps | 1 | RUBRIC&#95;EVAL |
| `SEF-3d5073c9c3cad6c846fa` | LOW | Description very long (312 chars, recommend 50-150) | 1 | QUALITY |
| ... | | *14 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| text-analyzer | 88.8 | B | script-based | 75.0 | 95.0 | 95.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'text-analyzer'
- [OK] **naming_convention**: Folder name 'text-analyzer' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (61/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **body_recommended_section**: Found recommended section: '## Instructions' (or '## Usage')
- [OK] **body_recommended_section**: Found recommended section: '## Examples'
- [OK] **optional_files**: Found optional supporting files: evals, scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'text-analyzer'
- [OK] **author_format**: Valid author format: SkillEvaluator Maintainers <maintainers@example.com>

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/official/text-analyzer</code> |
| [LOW] LOW | Description has its trigger at characters 157-165; some harnesses show only the first ~60 characters in their skill list | <code>/skills/official/text-analyzer/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/official/text-analyzer`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-07db021fffa60407462c`
- Fix: General skills should be at: skills/<skill-name>/

**2. Description has its trigger at characters 157-165; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-6d59a51256291da6dbce`
- Occurrence ID: `SEO-16d7aff90295558a64b6`
- Fix: State when to use the skill within the first 60 characters

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: Security scan completed - 1 advisory finding(s) (no critical/high issues)
- [OK] **skillspector**: Security scan completed - 1 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 2**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: The skill instructs running a script that can access files but declares no allowed-tools or permissions, so its least-privilege scope is not validated.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | MCP Least Privilege: This is a true scope/least-privilege issue. The skill intentionally supports reading files through &#96;--file /path/to/file<br><strong>LLM verification:</strong> True positive (medium confidence)<br>Reasoning: The documented --file option enables arbitrary file reads, and the skill lacks declared file&#95;read permissions or path restrictions, creating a plausible least-privilege and data-exposure risk.<br>Reported severity: MEDIUM; only high-confidence false positives are downgraded to INFO by verification. | <code>SKILL.md:1</code> |

<details>
<summary>View Details</summary>

**1. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**2. MCP Least Privilege: This is a true scope/least-privilege issue. The skill intentionally supports reading files through `--file /path/to/file**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-9e47eb4416d98778cbca`
- Occurrence ID: `SEO-97a780d9bdaa4a20c737`
- Fix: This is a true scope/least-privilege issue. The skill intentionally supports reading files through `--file /path/to/file.txt`, and static analysis detected a `file_read` capability, but the skill does not declare any `permissions` or `allowed-tools` scope to constrain what file access is allowed. That omission increases the risk that an agent may execute the script with arbitrary or sensitive file paths supplied by the user or injected through untrusted text. Because `analyze_text.py` is not included in the finding context, the exact safety of its path handling is unknown; if it accepts arbitrary paths without validation, this can leak existence, length, encoding behavior, and partial content via word statistics, especially most frequent words. The skill is not clearly malicious, but the missing tool scope makes it unsafe under a strict agent-security model. Declare an explicit read permission and constrain it. Example: add `permissions: file_read` with allowed paths or directories, or define `allowed-tools` that only includes the analyzer and restricts `--file` access to a sandboxed input directory. Modify `analyze_text.py` to reject absolute paths, parent-directory traversal, environment-dependent paths, sensitive locations such as `/etc`, `~/.ssh`, `.env`, credential stores, and home-directory dotfiles unless explicitly approved. Prefer inline `--text` by default and require explicit user confirmation for file reads. Run the script in a sandboxed or read-only working directory with path normalization and a denylist/allowlist check before opening any file.

</details>


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

**Overall: 88.8/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 75.0 | 35% |
| Discoverability | 95.0 | 25% |
| Reliability | 95.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 88.8/100 (Grade: B)

**Non-blocking findings: 5**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | Description very long (312 chars, recommend 50-150) | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/official/text-analyzer/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-3348e92bcfe1ef62ca7f`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-c1c5d3f8cca219fd2ddd`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-26fdc264b62da801040a`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description very long (312 chars, recommend 50-150)**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-3d5073c9c3cad6c846fa`
- Occurrence ID: `SEO-d61afebd4d2a5f9fe614`
- Fix: Keep descriptions concise for progressive disclosure

**5. No prerequisites/requirements documented**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-49688e69f18975cf3b3d`
- Fix: Document dependencies, API keys, or setup needed

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | analyze_text.py contains magic numbers | <code>/skills/official/text-analyzer/scripts/analyze_text.py</code> |

<details>
<summary>View Details</summary>

**1. analyze_text.py contains magic numbers**
- File: `/skills/official/text-analyzer/scripts/analyze_text.py`
- Check: `magic_numbers`
- Finding ID: `SEF-6a3bcfca5704358ead2b`
- Occurrence ID: `SEO-ae4dd2f3a35284bad52d`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 4**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [INFO] INFO | hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/official/text-analyzer/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-3b2d975baf15650e86c5`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-da6efdbe6beb0dac2af6`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 2 files outside references/, templates/, assets/ and scripts/ (evals) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-5995c1ef72651542c573`
- Occurrence ID: `SEO-7f690096f18e6d3298d5`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-dec2b317d2a825a15d3b`

</details>


### ❌ RUBRIC_EVAL
*LLM-as-Judge qualitative evaluation across 9 criteria (description clarity, instruction quality, trigger simulation, etc.)*

**1 errors, 9 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | [8/10] Description is clear, specific, and explains WHEN to use the skill | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [8/10] Instructions are easy to follow with clear action steps | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [8/10] All necessary information is present (purpose, scripts, parameters) | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [7/10] Skill scope is well-defined (clear boundaries, not too broad/narrow) | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [9/10] Documentation uses professional, consistent tone and formatting | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [MED] MEDIUM | [6/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives? | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance. | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [LOW] LOW | [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate? | <code>/skills/official/text-analyzer/SKILL.md</code> |
| [HIGH] HIGH | Rubric evaluation failed: criteria below 7/10: trigger_simulation | <code>/skills/official/text-analyzer/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. [8/10] Description is clear, specific, and explains WHEN to use the skill**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_description_clarity`
- Finding ID: `SEF-43cc06598a99d3bcc9b6`
- Occurrence ID: `SEO-67258b41acd7b1af3af4`
- Fix: The description clearly lists supported statistics and input forms, but 'summarize' is misleading because the skill does not produce semantic summaries.

**2. [8/10] Instructions are easy to follow with clear action steps**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_instruction_clarity`
- Finding ID: `SEF-17679b593e006f8c575d`
- Occurrence ID: `SEO-4164186e067ba9cc40ef`
- Fix: The agent steps are simple and actionable, though 'appropriate arguments' could be more explicit about choosing --text, --file, and --json.

**3. [8/10] Examples are helpful, relevant, show proper usage, AND cover sufficient query variations for robust skill detection**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_example_quality`
- Finding ID: `SEF-c20d009e607a4fd7bb84`
- Occurrence ID: `SEO-b9c97d91adbc33c7430c`
- Fix: Command examples are relevant and cover inline text, file input, and JSON output, but user-query variations for detection are limited.

**4. [8/10] All necessary information is present (purpose, scripts, parameters)**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_documentation_completeness`
- Finding ID: `SEF-8a24502b3877c389f6ba`
- Occurrence ID: `SEO-b434bb8f05e50fab8812`
- Fix: Purpose, script path, parameters, output fields, and limitations are present, though a fuller CLI reference would improve completeness.

**5. [7/10] Skill scope is well-defined (clear boundaries, not too broad/narrow)**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_scope_definition`
- Finding ID: `SEF-ec68fd50f7b207366a7f`
- Occurrence ID: `SEO-b8b356e669211af9e6ce`
- Fix: Scope is mostly clear for plain-text statistics, but the mention of summarization slightly broadens it beyond the implemented capability.

**6. [9/10] Documentation uses professional, consistent tone and formatting**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_professional_tone`
- Finding ID: `SEF-73720614f42d304aa9d9`
- Occurrence ID: `SEO-664fcf17eea48135c863`
- Fix: The documentation is clean, consistent, and professionally formatted with clear sections and examples.

**7. [6/10] Mentally test the skill description against 5 plausible user queries that SHOULD trigger it and 3 that should NOT. Does the description enable correct routing without false positives or false negatives?**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_trigger_simulation`
- Finding ID: `SEF-bc0939ffa25431c513d4`
- Occurrence ID: `SEO-e506e16b343abd3bbe51`
- Fix: Word, line, character, sentence, and frequency queries should route correctly, but 'summarize this text' and broad 'analyze' requests may produce false positives.

**8. [7/10] Do the instructions cover a complete end-to-end workflow? Identify any steps where the user or agent would need to figure out what to do next without guidance.**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_workflow_completeness`
- Finding ID: `SEF-5f777f9e6294b2d207a5`
- Occurrence ID: `SEO-0c124486cce9d7afa6fd`
- Fix: The basic run-and-return workflow is covered, but guidance is thin on input selection, shell quoting, output format choice, and handling missing or empty input.

**9. [7/10] Are the documented error scenarios realistic and actionable? Would the solutions actually help resolve the issues, or are they generic boilerplate?**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_error_handling_quality`
- Finding ID: `SEF-98f09c467b68e7239891`
- Occurrence ID: `SEO-49422342382f59409cfb`
- Fix: FileNotFoundError and empty-output guidance are realistic and actionable, though non-UTF-8 handling is documented only as a limitation rather than an error scenario.

**10. Rubric evaluation failed: criteria below 7/10: trigger_simulation**
- File: `/skills/official/text-analyzer/SKILL.md`
- Check: `rubric_overall`
- Finding ID: `SEF-d227d8fa7e50299e84f8`
- Occurrence ID: `SEO-e5881db844a53c332264`
- Fix: Address the failed rubric criteria and rerun the evaluation

</details>


---
*Generated by SkillEvaluator*