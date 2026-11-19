# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:39 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 11 |
| ❌ Failed | 2 |
| ⚠️ Incomplete | 0 |
| Total Issues | 28 unique findings (2 high, 7 medium) / 33 occurrences / 33 raw records; 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-0a046cedaad0ac6f0723` | HIGH | Privilege Escalation: .env | 5 | Security Scan |
| `SEF-5f18925f4e26c7738c9f` | HIGH | Privilege Escalation: .env' | 1 | Security Scan |
| `SEF-7ce154d64f02bb16a5ee` | MEDIUM | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (CWE-22) | 2 | Code Risk Analysis |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-8e1fcdbf37b720508663` | MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | 1 | Security Scan |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| `SEF-e3f5c930756d6b8f695b` | MEDIUM | Missing recommended section: '&#35;&#35; Examples' | 1 | Schema &amp; Repository Governance |
| `SEF-0f3cde56a46498377f1a` | LOW | Description doesn't mention WHEN to use this skill | 1 | QUALITY |
| ... | | *18 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| es-log-query | 89.0 | B | guide-only | 90.0 | 85.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'es-log-query'
- [OK] **naming_convention**: Folder name 'es-log-query' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (162/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **name_consistency**: Directory name matches frontmatter: 'es-log-query'

**Non-blocking findings: 8**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G9/es-log-query</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | Unexpected 'es_log_query.py' in skill root | <code>/skills/library-20261118/G9/es-log-query/es_log_query.py</code> |
| [LOW] LOW | Unexpected 'skill.json' in skill root | <code>/skills/library-20261118/G9/es-log-query/skill.json</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: argument-hint, author, tags, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G9/es-log-query`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-cbf3318f37ffee61bf4c`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-db40fd3c6d3fa147b3ec`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-17b5dd7f7b76c8aca5ef`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected 'es_log_query.py' in skill root**
- File: `/skills/library-20261118/G9/es-log-query/es_log_query.py`
- Check: `unexpected_file`
- Finding ID: `SEF-2f0dd915a2f184be91f0`
- Occurrence ID: `SEO-f785f2b82413cdebb099`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Unexpected 'skill.json' in skill root**
- File: `/skills/library-20261118/G9/es-log-query/skill.json`
- Check: `unexpected_file`
- Finding ID: `SEF-c468e27696e6ce3176ba`
- Occurrence ID: `SEO-60969f2992f8ae14bf34`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Author not specified in metadata**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-8c08aed4d426703843d9`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**7. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-f63131e56faddbd269fd`
- Fix: State when to use the skill within the first 60 characters

**8. Frontmatter field(s) outside the agentskills.io spec: argument-hint, author, tags, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-8fc20d858b74a90f4136`
- Occurrence ID: `SEO-8e68652672ab9885e43d`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**6 errors, 1 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Privilege Escalation: .env  | <code>.env.example:2</code> |
| [HIGH] HIGH | Privilege Escalation: .env  | <code>es_log_query.py:22</code> |
| [HIGH] HIGH | Privilege Escalation: .env  | <code>es_log_query.py:37</code> |
| [HIGH] HIGH | Privilege Escalation: .env  | <code>es_log_query.py:51</code> |
| [HIGH] HIGH | Privilege Escalation: .env  | <code>es_log_query.py:56</code> |
| [HIGH] HIGH | Privilege Escalation: .env' | <code>es_log_query.py:24</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |

<details>
<summary>View Details</summary>

**1. Privilege Escalation: .env **
- File: `.env.example:2`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-0a046cedaad0ac6f0723`
- Occurrence ID: `SEO-1c6dcff5d61e50ebdab1`
- Content: `# ES Log Query 配置
# 复制此文件为 .env 并填写你的账号密码

# ES 集群地址（可选，有...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**2. Privilege Escalation: .env **
- File: `es_log_query.py:22`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-0a046cedaad0ac6f0723`
- Occurrence ID: `SEO-ee48c78676099ded6df0`
- Content: `def _load_env() -> Dict[str, str]:
    """从 skill 目录下的 .e...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**3. Privilege Escalation: .env **
- File: `es_log_query.py:37`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-0a046cedaad0ac6f0723`
- Occurrence ID: `SEO-072bbb53fe151d969d18`
- Content: `def _get_es_config() -> Dict[str, str]:
    """获取 ES 配置，优...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**4. Privilege Escalation: .env **
- File: `es_log_query.py:51`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-0a046cedaad0ac6f0723`
- Occurrence ID: `SEO-0f2882743daa213b8f77`
- Content: `"""检查账号密码，缺失时提示用户"""
    if not config.get('user') or not...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**5. Privilege Escalation: .env **
- File: `es_log_query.py:56`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-0a046cedaad0ac6f0723`
- Occurrence ID: `SEO-1f2aa5a197f65677ae7a`
- Content: `sys.exit(1)


# 默认配置（不含敏感信息，实际值从 .env 加载）
ES_CONFIG = _ge...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**6. Privilege Escalation: .env'**
- File: `es_log_query.py:24`
- Check: `Credential Access (PE3)`
- Finding ID: `SEF-5f18925f4e26c7738c9f`
- Occurrence ID: `SEO-c1ac07133dc554b555f3`
- Content: `def _load_env() -> Dict[str, str]:
    """从 skill 目录下的 .e...`
- Fix: Code accesses credential files (SSH keys, AWS credentials, etc.). This could indicate credential theft attempts. Remove references to credential paths. Use environment variables or secrets managers. For docs, use placeholder paths (e.g., /path/to/config). Never load .env or token files in production code paths.

**7. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 3 files for PII
- [OK] **pii_detection**: No PII detected in 3 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ❌ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

**2 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (CWE-22) | <code>/skills/library-20261118/G9/es-log-query/es_log_query.py:168</code> |
| [MED] MEDIUM | Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (CWE-22) | <code>/skills/library-20261118/G9/es-log-query/es_log_query.py:226</code> |

<details>
<summary>View Details</summary>

**1. Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (CWE-22)**
- File: `/skills/library-20261118/G9/es-log-query/es_log_query.py:168`
- Check: `B310:blacklist`
- Finding ID: `SEF-7ce154d64f02bb16a5ee`
- Occurrence ID: `SEO-cbd76cc51edbd0804cad`
- Fix: Review blacklist (B310) (CWE-22)

**2. Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (CWE-22)**
- File: `/skills/library-20261118/G9/es-log-query/es_log_query.py:226`
- Check: `B310:blacklist`
- Finding ID: `SEF-7ce154d64f02bb16a5ee`
- Occurrence ID: `SEO-0a238088c4e0b664d85f`
- Fix: Review blacklist (B310) (CWE-22)

</details>


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

- [OK] **unicode_scan**: No invisible Unicode characters detected in 3 file(s)

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
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-454203452211b16f39a5`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**2. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-1b3baef9b1ab01c11085`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**3. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-866518e9b3c55a2d3be2`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**4. No '## Purpose' section**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-ce137c40220a391a1315`
- Fix: Add purpose section to clarify use cases

**5. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-8aec542571117a605640`
- Fix: Document dependencies, API keys, or setup needed

**6. No limitations documented**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-3aef8f74f769a774eec9`
- Fix: Add '## Limitations' section with known issues/constraints

**7. No troubleshooting section documented**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-3f3be5e1b198d702437b`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- [OK] **lint**: No scripts/ or tools/ directory found

### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | codex: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | hermes: 3 files outside references/, templates/, assets/ and scripts/ (.env.example, es_log_query.py, skill.json) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | hermes: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | openclaw: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |
| [INFO] INFO | opencode: Ignored here (Claude Code only): argument-hint. | <code>/skills/library-20261118/G9/es-log-query/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. codex: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `CX-CLAUDE-ONLY`
- Finding ID: `SEF-3c14903aa6a36408a8d2`
- Occurrence ID: `SEO-ca8374e443a0e635e434`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**2. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-ee3494dbdb77cd4be9d6`

**3. copilot-cli: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `CP-CLAUDE-ONLY`
- Finding ID: `SEF-9dcf632d2f32abd5d60c`
- Occurrence ID: `SEO-d84a63a515f4afe4381f`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**4. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-b88cef80230ccd648704`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**5. hermes: 3 files outside references/, templates/, assets/ and scripts/ (.env.example, es_log_query.py, skill.json) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-e1e9a6faee7311afd38b`
- Occurrence ID: `SEO-419ce7d456413eef62fa`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**6. hermes: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `HM-CLAUDE-ONLY`
- Finding ID: `SEF-ea696edc4782d72e08ce`
- Occurrence ID: `SEO-453965355279a0c98cb3`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**7. openclaw: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `OW-CLAUDE-ONLY`
- Finding ID: `SEF-6bc3d5578c3fefa78d68`
- Occurrence ID: `SEO-defc34f7ca049fc4aafa`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

**8. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-151f7932c3957614f0b3`

**9. opencode: Ignored here (Claude Code only): argument-hint.**
- File: `/skills/library-20261118/G9/es-log-query/SKILL.md`
- Check: `OC-CLAUDE-ONLY`
- Finding ID: `SEF-a79a1e72ae60b486b70d`
- Occurrence ID: `SEO-bfb220dd4501f80c0c91`
- Fix: Fine to keep for Claude Code; don't depend on them elsewhere.

</details>


---
*Generated by SkillEvaluator*