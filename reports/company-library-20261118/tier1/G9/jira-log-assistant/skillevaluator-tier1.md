# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:52 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 0 |
| Total Issues | 22 unique findings (2 high, 8 medium) / 22 occurrences / 22 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-84d95de439d61838eebd` | HIGH | Privilege Escalation: Access Token | 1 | Security Scan |
| `SEF-a24f3809a735be5a155c` | HIGH | Supply Chain: curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" &#92; "https://jira.cvte.com/rest/api/2/myself" &#124; python | 1 | Security Scan |
| `SEF-188498992bdf48b1be40` | MEDIUM | Data Exfiltration: curl -s --max-time 30 &#92; -H 'Authorization: Bearer $TOKEN' &#92; -H 'Content-Type: application/json' &#92; -X POST &#92; "https://jira.cvte.com/rest/api/2/issue/${ISSUE&#95;KEY}/comment" &#92; -d | 1 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-578a65f8c90a3bfc1eed` | MEDIUM | Data Exfiltration: curl -s --max-time 30 &#92; -H "Authorization: Bearer $TOKEN" &#92; -H "Content-Type: application/json" &#92; -X POST &#92; "https://jira.cvte.com/rest/api/2/issue/${ISSUE&#95;KEY}/comment" &#92; -d | 1 | Security Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-ea72214cbe34a0f00121` | MEDIUM | Agent Snooping: skills/android-log-analysis/SKILL.md | 1 | Security Scan |
| ... | | *12 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| jira-log-assistant | 90.2 | A | guide-only | 90.0 | 90.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'jira-log-assistant'
- [OK] **naming_convention**: Folder name 'jira-log-assistant' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (236/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: README.md
- [OK] **name_consistency**: Directory name matches frontmatter: 'jira-log-assistant'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/jira-log-assistant</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | Description has its trigger at characters 179-187; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/jira-log-assistant`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-e6726aadb0901d89c897`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-7d03718569e120d67fd7`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-c513c65e4513e58e215e`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-c56196b3e034bca6abe5`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has its trigger at characters 179-187; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-d99dff18527ecbe97675`
- Occurrence ID: `SEO-f1e6d112783f7975f9b6`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-fd081a68fd6cb72673df`
- Occurrence ID: `SEO-123221fc0e59693cc011`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**2 errors, 4 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Privilege Escalation: Access Token | <code>SKILL.md:36</code> |
| [HIGH] HIGH | Supply Chain: curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" \<br>  "https://jira.cvte.com/rest/api/2/myself" &#124; python | <code>SKILL.md:40</code> |
| [MED] MEDIUM | Agent Snooping: skills/android-log-analysis/SKILL.md | <code>SKILL.md:135</code> |
| [MED] MEDIUM | Data Exfiltration: curl -s --max-time 30 \<br>  -H "Authorization: Bearer $TOKEN" \<br>  -H "Content-Type: application/json" \<br>  -X POST \<br>  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \<br>  -d  | <code>SKILL.md:180</code> |
| [MED] MEDIUM | Data Exfiltration: curl -s --max-time 30 \<br>  -H 'Authorization: Bearer $TOKEN' \<br>  -H 'Content-Type: application/json' \<br>  -X POST \<br>  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \<br>  -d  | <code>SKILL.md:201</code> |

<details>
<summary>View Details</summary>

**1. Privilege Escalation: Access Token**
- File: `SKILL.md:36`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-84d95de439d61838eebd`
- Occurrence ID: `SEO-aee606eaf74151582446`
- Content: `1. 读取环境变量 `SKILL_JIRA_ASSISTANT_TOKEN`
2. 若为空，**必须要求用户提供*...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**2. Supply Chain: curl -s --max-time 15 -H "Authorization: Bearer $TOKEN" \
  "https://jira.cvte.com/rest/api/2/myself" | python**
- File: `SKILL.md:40`
- Check: `External Script Fetching (SC2)`
- Finding ID: `SEF-a24f3809a735be5a155c`
- Occurrence ID: `SEO-aea26141cb64c7468512`
- Content: `3. 收到 token 后，用以下命令验证有效性：

```bash
curl -s --max-time 15 ...`
- Fix: Remote code is downloaded and executed. This bypasses code review and could introduce malicious code. Avoid downloading and executing remote scripts. Use trusted packages from PyPI/npm. If remote fetch is required, verify checksums and use HTTPS.

**3. Agent Snooping: skills/android-log-analysis/SKILL.md**
- File: `SKILL.md:135`
- Check: `Skill Enumeration (AS3)`
- Finding ID: `SEF-ea72214cbe34a0f00121`
- Occurrence ID: `SEO-8d3a80847246259f2e1f`
- Content: `### 3.1 调用 android-log-analysis Skill

读取并执行 `android-log...`
- Fix: Skill enumerates or reads other installed skills. Access to other skills' SKILL.md files or the skills directory reveals prompt instructions, capabilities, and secrets that should be invisible to peer skills. Remove all code or instructions that list or read other skills' files or directories. Skills should operate independently; cross-skill access is a privilege escalation.

**4. Data Exfiltration: curl -s --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \
  -d **
- File: `SKILL.md:180`
- Check: `External Transmission (E1)`
- Finding ID: `SEF-578a65f8c90a3bfc1eed`
- Occurrence ID: `SEO-2b96a0ff0c6b41883254`
- Content: `### 4.2 发送评论到 Jira

```bash
curl -s --max-time 30 \
  -H ...`
- Fix: Data is being sent to an external URL. This could be legitimate telemetry or data exfiltration. Manual review is recommended. Verify the destination URL is trusted and necessary. Remove or replace with documented APIs. Ensure no secrets, tokens, or PII are transmitted.

**5. Data Exfiltration: curl -s --max-time 30 \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -X POST \
  "https://jira.cvte.com/rest/api/2/issue/${ISSUE_KEY}/comment" \
  -d **
- File: `SKILL.md:201`
- Check: `External Transmission (E1)`
- Finding ID: `SEF-188498992bdf48b1be40`
- Occurrence ID: `SEO-a6ee598f1ec77782eff7`
- Content: `header = '{panel:title=AI 日志分析报告|borderColor=#0747A6|bgCo...`
- Fix: Data is being sent to an external URL. This could be legitimate telemetry or data exfiltration. Manual review is recommended. Verify the destination URL is trusted and necessary. Remove or replace with documented APIs. Ensure no secrets, tokens, or PII are transmitted.

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

### ✅ A QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 90.2/100 (Grade: A)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 90.0 | 35% |
| Discoverability | 90.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 90.2/100 (Grade: A)

**Non-blocking findings: 7**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | Description very long (340 chars, recommend 50-150) | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-85f65fe674e4078f52e0`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-777d381a210aa0104ab6`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description very long (340 chars, recommend 50-150)**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-60c56d58120eadc46777`
- Occurrence ID: `SEO-861802600cba999f69a3`
- Fix: Keep descriptions concise for progressive disclosure

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-b7e6b245af1f89e11c31`
- Fix: Add purpose section to clarify use cases

**5. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-c987002e8858d4c5d4c4`
- Fix: Document dependencies, API keys, or setup needed

**6. No limitations documented**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-4711da34a159c4fbe872`
- Fix: Add '## Limitations' section with known issues/constraints

**7. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-1a36d30038c73dcc34ac`
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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (README.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/jira-log-assistant/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-ed3aacb8c7b1b1d73c4b`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-0be1971f6b73a052cd34`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 1 files outside references/, templates/, assets/ and scripts/ (README.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-0a2cf18d1dd5f0b5d3e5`
- Occurrence ID: `SEO-653558870c696d26055d`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/jira-log-assistant/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-96682fe9e6e38c57fd7e`

</details>


---
*Generated by SkillEvaluator*