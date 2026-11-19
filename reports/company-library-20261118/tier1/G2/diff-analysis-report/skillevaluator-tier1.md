# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ❌ FAIL
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 12:55 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 11 |
| ❌ Failed | 2 |
| ⚠️ Incomplete | 0 |
| Total Issues | 162 unique findings (1 high, 134 medium) / 365 occurrences / 364 raw records; 3 warnings without a finding |
| Duplicate Occurrences Reconciled | 0 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-b63a6782581863ffe410` | HIGH | Personal Windows user path: C:&#92;Users&#92;cvter — 2 occurrences (使用说明.md lines 52, 118) | 2 | PII Scan |
| `SEF-8214a82df974ad97be61` | MEDIUM | Prompt Injection: U+0020 x161 | 7 | Security Scan |
| `SEF-8f2a42bec6de4b9e1ae4` | MEDIUM | Prompt Injection: U+0020 x112 | 7 | Security Scan |
| `SEF-cec7b3b3bfa34fefa927` | MEDIUM | Prompt Injection: U+0020 x117 | 7 | Security Scan |
| `SEF-280e3b05f9024e777a20` | MEDIUM | Prompt Injection: U+0020 x91 | 6 | Security Scan |
| `SEF-7fd8f1f71faa5392f2a7` | MEDIUM | Prompt Injection: U+0020 x108 | 6 | Security Scan |
| `SEF-be8d82ee7087681a37dd` | MEDIUM | Prompt Injection: U+0020 x118 | 6 | Security Scan |
| `SEF-360a57751e6077c0e47a` | MEDIUM | Prompt Injection: U+0020 x94 | 5 | Security Scan |
| `SEF-39ff038b5b09c17e2904` | MEDIUM | Prompt Injection: U+0020 x133 | 5 | Security Scan |
| `SEF-a058d5ee4f0d4938bc67` | MEDIUM | Prompt Injection: U+0020 x83 | 5 | Security Scan |
| ... | | *152 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| diff-analysis-report | 80.2 | B | script-based | 65.0 | 85.0 | 85.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'diff-analysis-report'
- [OK] **naming_convention**: Folder name 'diff-analysis-report' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (137/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: scripts
- [OK] **name_consistency**: Directory name matches frontmatter: 'diff-analysis-report'

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/diff-analysis-report</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | Unexpected '使用说明.md' in skill root | <code>/skills/library-20261118/G2/diff-analysis-report/使用说明.md</code> |
| [LOW] LOW | Unexpected 'report-template.md' in skill root | <code>/skills/library-20261118/G2/diff-analysis-report/report-template.md</code> |
| [LOW] LOW | Unexpected '业务知识' in skill root | <code>/skills/library-20261118/G2/diff-analysis-report/业务知识</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/diff-analysis-report`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-171bc18374b78e6a1f4f`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-61b5ed00b135cf5be58a`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-4817dfaecb5ce5edf27d`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Unexpected '使用说明.md' in skill root**
- File: `/skills/library-20261118/G2/diff-analysis-report/使用说明.md`
- Check: `unexpected_file`
- Finding ID: `SEF-996cd10708b40af3af1d`
- Occurrence ID: `SEO-7fbb1730fe3ced1e87ca`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**5. Unexpected 'report-template.md' in skill root**
- File: `/skills/library-20261118/G2/diff-analysis-report/report-template.md`
- Check: `unexpected_file`
- Finding ID: `SEF-259128f7026285d5dd91`
- Occurrence ID: `SEO-b9879b873d8583fd9f50`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**6. Unexpected '业务知识' in skill root**
- File: `/skills/library-20261118/G2/diff-analysis-report/业务知识`
- Check: `unexpected_file`
- Finding ID: `SEF-22235d716ef64b3d6d1c`
- Occurrence ID: `SEO-8923984a0b3e45897961`
- Fix: Consider moving to one of: agents/, assets/, config/, evals/, references/, scripts/, tests/, tools/. To allow additional directories, set $SKILLEVALUATOR_SCHEMA_ALLOWED_DIRS.

**7. Author not specified in metadata**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-39eb9e238cf28af16322`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**8. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-073ad0ea24c90ec4154b`
- Fix: State when to use the skill within the first 60 characters

**9. Frontmatter field(s) outside the agentskills.io spec: author, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-b28f818a5fc2daa26f71`
- Occurrence ID: `SEO-8b819a02ea7fa2b26ef0`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ✅ Security Scan
*Detect security vulnerabilities and PII/secrets*

- [OK] **skillspector**: Security scan completed - 328 advisory finding(s) (no critical/high issues)

**Non-blocking findings: 328**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | Dangerous Code Execution: subprocess.run(cmd, cwd=repo, capture_output=True) | <code>scripts/grep_features.py:52</code> |
| [MED] MEDIUM | Memory Poisoning:                                                                                                                                                                                                          | <code>业务知识/校园安防主流程测试用例.md:3</code> |
| [MED] MEDIUM | Memory Poisoning:                                                                                                                                                                                                          | <code>业务知识/校园安防核心功能说明.md:7</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x168 | <code>业务知识/校园安防主流程测试用例.md:3</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x168 | <code>业务知识/校园安防主流程测试用例.md:77</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x283 | <code>业务知识/校园安防主流程测试用例.md:3</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x125 | <code>业务知识/校园安防主流程测试用例.md:5</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x125 | <code>业务知识/校园安防主流程测试用例.md:23</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x125 | <code>业务知识/校园安防主流程测试用例.md:40</code> |
| ... | *318 more issues* | |

<details>
<summary>View Details</summary>

**1. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**2. Dangerous Code Execution: subprocess.run(cmd, cwd=repo, capture_output=True)**
- File: `scripts/grep_features.py:52`
- Check: `subprocess module call (AST4)`
- Finding ID: `SEF-9211eae3cb7f18e0adfb`
- Occurrence ID: `SEO-c98af5cb584da09021e7`
- Content: `for s in strings:
        cmd += ["-e", s]
    cmd += [br...`
- Fix: subprocess module calls execute external commands. Without careful input validation, this enables command injection. Use subprocess.run() with shell=False and an explicit argument list. Validate all inputs and avoid passing user-controlled data to commands.

**3. Memory Poisoning:                                                                                                                                                                                                         **
- File: `业务知识/校园安防主流程测试用例.md:3`
- Check: `Context Window Stuffing (MP2)`
- Finding ID: `SEF-bee9c10a7b38d6bda83f`
- Occurrence ID: `SEO-78ef8e736ca3e332e5c2`
- Content: `# 校园安防主流程测试用例

| 终端      | 主模块  | 子模块       | 用例标题       ...`
- Fix: Skill attempts to fill the context window with filler content, displacing legitimate instructions and safety constraints. This can degrade agent performance or bypass safety boundaries. Implement context-window management that detects and rejects padding or stuffing attempts. Prioritize system instructions over user-injected content.

**4. Memory Poisoning:                                                                                                                                                                                                         **
- File: `业务知识/校园安防核心功能说明.md:7`
- Check: `Context Window Stuffing (MP2)`
- Finding ID: `SEF-bee9c10a7b38d6bda83f`
- Occurrence ID: `SEO-f64d1df1546ff1dbf6ab`
- Content: `### 1\.1 核心功能

| **功能模块**             | **核心功能点**        ...`
- Fix: Skill attempts to fill the context window with filler content, displacing legitimate instructions and safety constraints. This can degrade agent performance or bypass safety boundaries. Implement context-window management that detects and rejects padding or stuffing attempts. Prioritize system instructions over user-injected content.

**5. Prompt Injection: U+0020 x168**
- File: `业务知识/校园安防主流程测试用例.md:3`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-d4b0ff4601dc794d0e3b`
- Occurrence ID: `SEO-b5e9033e9662254590cd`
- Content: `# 校园安防主流程测试用例

| 终端      | 主模块  | 子模块       | 用例标题       ...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**6. Prompt Injection: U+0020 x168**
- File: `业务知识/校园安防主流程测试用例.md:77`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-d4b0ff4601dc794d0e3b`
- Occurrence ID: `SEO-a20ceaf943706f934c14`
- Content: `|
| Web 管理端 | 宿舍管理 | 停宿记录      | 检查临时非行政班补配            | ...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**7. Prompt Injection: U+0020 x283**
- File: `业务知识/校园安防主流程测试用例.md:3`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-ed5f8de19b2a8cca5126`
- Occurrence ID: `SEO-111ba5ec96f8dbfef7a2`
- Content: `# 校园安防主流程测试用例

| 终端      | 主模块  | 子模块       | 用例标题       ...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**8. Prompt Injection: U+0020 x125**
- File: `业务知识/校园安防主流程测试用例.md:5`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-e0c472bd43a5ed60d5c2`
- Occurrence ID: `SEO-a550cf761223693efb6c`
- Content: `------------------------------------- | -----------------...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**9. Prompt Injection: U+0020 x125**
- File: `业务知识/校园安防主流程测试用例.md:23`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-e0c472bd43a5ed60d5c2`
- Occurrence ID: `SEO-a548d3ca8ce64917398e`
- Content: `| 1. 详情页为左右布局：左侧事件列表+中部凭证轮播+右侧信息面板<br>2. 凭证缩略图带「关联图片/关联视频...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**10. Prompt Injection: U+0020 x125**
- File: `业务知识/校园安防主流程测试用例.md:40`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-e0c472bd43a5ed60d5c2`
- Occurrence ID: `SEO-27d615b5202f1f6c2e11`
- Content: `| 1. 触发浏览器下载，文件名格式「通行记录_起_止.xlsx」<br>2. 成功 toast「导出成功」，导出...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

*... and 318 more issues*

</details>


### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Personal Windows user path: C:\Users\cvter — 2 occurrences (使用说明.md lines 52, 118) | <code>使用说明.md:52</code> |

<details>
<summary>View Details</summary>

**1. Personal Windows user path: C:\Users\cvter — 2 occurrences (使用说明.md lines 52, 118)**
- File: `使用说明.md:52`
- Check: `personal_paths`
- Finding ID: `SEF-b63a6782581863ffe410`
- Occurrence ID: `SEO-f52ed6f5466666b72e5e`
- Content: `需求文档是 C:\Users\cvter\Downloads\希沃录播_校级安防_V0.18.2_通行规则_通行规...`
- Fix: Use generic path like C:\path\to\file or %USERPROFILE% variable

</details>


### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ❌ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Using xml.etree.ElementTree.fromstring to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree.fromstring with its defusedxml equivalent function or make sure defusedxml.defuse_stdlib() is called (CWE-20) | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py:82</code> |

<details>
<summary>View Details</summary>

**1. Using xml.etree.ElementTree.fromstring to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree.fromstring with its defusedxml equivalent function or make sure defusedxml.defuse_stdlib() is called (CWE-20)**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py:82`
- Check: `B314:blacklist`
- Finding ID: `SEF-6c3294c2b85362410fc8`
- Occurrence ID: `SEO-465ba5c3f431fa65f3e6`
- Fix: Review blacklist (B314) (CWE-20)

</details>


### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 6 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 6 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- [OK] **unicode_scan**: No invisible Unicode characters detected in 9 file(s)

### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 80.2/100 (Grade: B)** | Skill Type: script-based

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 65.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 85.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 80.2/100 (Grade: B)

**Non-blocking findings: 10**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-c639aa4708785bddd15c`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-0716393cd39182108817`
- Fix: Add explicit run_script() call examples

**3. No examples provided**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-18245a2a8bd164b7cf2b`
- Fix: Add example usage with code blocks

**4. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-e309aa30c12a14281a1d`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**5. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-47ea0c6a550bcd636ead`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**6. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-4f0b2e73cd56e078d965`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**7. No '## Purpose' section**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-99575e1e832c87df8a2c`
- Fix: Add purpose section to clarify use cases

**8. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-26515504740387aa1135`
- Fix: Document dependencies, API keys, or setup needed

**9. No limitations documented**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-6eb264a713333720e828`
- Fix: Add '## Limitations' section with known issues/constraints

**10. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-a0c0f8baeba1d17eeada`
- Fix: Add '## Troubleshooting' with Error/Cause/Solution patterns

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | grep_features.py contains magic numbers | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py</code> |
| [LOW] LOW | grep_features.py missing shebang line | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py</code> |
| [LOW] LOW | grep_features.py may lack input validation | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py</code> |
| [LOW] LOW | parse_xmind.py missing shebang line | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py</code> |
| [LOW] LOW | parse_xmind.py may lack input validation | <code>/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py</code> |
| [INFO] INFO | 1 Node script(s) not linted (script lint parses Python only) | <code>scripts</code> |

<details>
<summary>View Details</summary>

**1. grep_features.py contains magic numbers**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py`
- Check: `magic_numbers`
- Finding ID: `SEF-ecf3c2bb0db6cbd762a7`
- Occurrence ID: `SEO-62cd6b16284d72329e7a`
- Fix: Extract magic numbers to named constants

**2. grep_features.py missing shebang line**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py`
- Check: `missing_shebang`
- Finding ID: `SEF-f6c26bc2ec431022973e`
- Occurrence ID: `SEO-28e83411e8f62034098c`
- Fix: Add: #!/usr/bin/env python3

**3. grep_features.py may lack input validation**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/grep_features.py`
- Check: `no_input_validation`
- Finding ID: `SEF-5570c9f9c46965104758`
- Occurrence ID: `SEO-88ea3ad763df0d4472f4`
- Fix: Add argument checks and raise descriptive errors

**4. parse_xmind.py missing shebang line**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py`
- Check: `missing_shebang`
- Finding ID: `SEF-02bcfc62ec6a937edbfc`
- Occurrence ID: `SEO-230af818ba1179010a71`
- Fix: Add: #!/usr/bin/env python3

**5. parse_xmind.py may lack input validation**
- File: `/skills/library-20261118/G2/diff-analysis-report/scripts/parse_xmind.py`
- Check: `no_input_validation`
- Finding ID: `SEF-41328efe5e5863cf997b`
- Occurrence ID: `SEO-f69450626bcc9fb7f423`
- Fix: Add argument checks and raise descriptive errors

**6. 1 Node script(s) not linted (script lint parses Python only)**
- File: `scripts`
- Check: `node_scripts_not_linted`
- Finding ID: `SEF-00db0b68cf190c628a62`
- Occurrence ID: `SEO-7fd2640adef67ad2cfda`

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | hermes: 5 files outside references/, templates/, assets/ and scripts/ (report-template.md, 业务知识, 使用说明.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [LOW] LOW | openclaw: SKILL.md reads as 22,233 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | openclaw: 1 files over 64,000 bytes (业务知识/校园安防主流程测试用例.md): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | openclaw: Double quotes in the description are shown to the model as &amp;quot; in the skill list. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |
| [INFO] INFO | opencode: 1 files are over 51,200 bytes or 2,000 lines (业务知识/校园安防主流程测试用例.md); OpenCode's read tool returns at most that per call, so the model must page. | <code>/skills/library-20261118/G2/diff-analysis-report/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-5a059a87cf0b073050bc`

**2. copilot-cli: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `CP-DESC-ESCAPED`
- Finding ID: `SEF-5cf1d958d3582b4dd475`
- Occurrence ID: `SEO-3e5c011ec471c7ed1bd6`
- Fix: Use single quotes in the description if the exact text matters.

**3. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-91569d35b50c2481eb6b`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**4. hermes: 5 files outside references/, templates/, assets/ and scripts/ (report-template.md, 业务知识, 使用说明.md) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-42f348b5a8826aa0f183`
- Occurrence ID: `SEO-2c9820f0617b1f2d07d0`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**5. openclaw: SKILL.md reads as 22,233 characters (OpenClaw counts each CJK character as 4 or more), over the read cap for this setup: the read is refused or returns a cut prefix with a truncation notice. The cap depends on the model context (16,000 under 100K tokens, 32,000 under 200K, 64,000 above; custom providers default to 128K). Pass --context-tokens to check your setup.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `OW-READ-BUDGET`
- Finding ID: `SEF-75bfbca8e8709127b25f`
- Occurrence ID: `SEO-d90c7226614ee3e939db`
- Fix: Keep SKILL.md under about 15,000 characters (about 3,700 CJK characters); move detail into references/ files.

**6. openclaw: 1 files over 64,000 bytes (业务知识/校园安防主流程测试用例.md): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `OW-REF-BUDGET`
- Finding ID: `SEF-3f61c194e58b647e7e45`
- Occurrence ID: `SEO-c1b01cbe32a64ec14a7e`
- Fix: Split large reference files into pieces under 16,000 UTF-8 bytes.

**7. openclaw: Double quotes in the description are shown to the model as &quot; in the skill list.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `OW-DESC-ESCAPED`
- Finding ID: `SEF-d97cf8343ff688501a4c`
- Occurrence ID: `SEO-c9e9a0f68cf0d1533e60`
- Fix: Use single quotes in the description if the exact text matters.

**8. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-014f9849607aba2c4b03`

**9. opencode: 1 files are over 51,200 bytes or 2,000 lines (业务知识/校园安防主流程测试用例.md); OpenCode's read tool returns at most that per call, so the model must page.**
- File: `/skills/library-20261118/G2/diff-analysis-report/SKILL.md`
- Check: `OC-REF-CUT`
- Finding ID: `SEF-14384cc5db26cce7cf92`
- Occurrence ID: `SEO-c1e8862406a602cd7175`
- Fix: Split large files into pieces under 51,200 bytes and 2,000 lines.

</details>


---
*Generated by SkillEvaluator*