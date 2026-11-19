# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 12:54 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 11 |
| ❌ Failed | 2 |
| ⚠️ Incomplete | 1 |
| Total Issues | 29 unique findings (4 high, 7 medium) / 41 occurrences / 46 raw records; 1 error and 2 warnings without a finding |
| Duplicate Occurrences Reconciled | 6 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-8653030473307007c8c6` | HIGH | Prompt Injection: | 4 | Security Scan |
| `SEF-978b2c3d6919bf230525` | HIGH | Non-placeholder email address: liuguangyi&#64;cviauto.com — 2 occurrences (references/cpp-style-spec/style-comments.md line 37; references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md line 893) | 2 | PII Scan |
| `SEF-c0c7dab687f6e3118c0c` | HIGH | Tool Misuse: delete // | 2 | Security Scan |
| `SEF-e9ee779440dec4ad4368` | HIGH | Prompt Injection: | 2 | Security Scan |
| `SEF-6c2f5d080972d18524b0` | MEDIUM | Prompt Injection: U+0020 x89 | 2 | Security Scan |
| `SEF-b9762d11eda0e5e553d8` | MEDIUM | Prompt Injection: U+0020 x82 | 2 | Security Scan |
| `SEF-18a7f8cc53f607ef9645` | MEDIUM | Unexpected nesting depth for general skill | 1 | Schema &amp; Repository Governance |
| `SEF-2ab016a817c566724ba9` | MEDIUM | Missing recommended section: '&#35;&#35; Instructions' | 1 | Schema &amp; Repository Governance |
| `SEF-bf2d85d8c9d7a282e7ad` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.author' | 1 | QUALITY |
| `SEF-dd828fd8f6476dc5f3c7` | MEDIUM | SKILL&#95;SPEC recommended field missing: 'metadata.tags' | 1 | QUALITY |
| ... | | *19 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| cxx-style-review | 84.8 | B | guide-only | 85.0 | 85.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'cxx-style-review'
- [OK] **naming_convention**: Folder name 'cxx-style-review' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (144/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: agents, references
- [OK] **name_consistency**: Directory name matches frontmatter: 'cxx-style-review'

**Non-blocking findings: 6**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G2/cxx-style-review</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | Frontmatter field(s) outside the agentskills.io spec: author, tags, version; agent harnesses do not pass them to the model | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G2/cxx-style-review`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-cd1d20fa1dbeac9d8fbf`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-bd52e1369e0e2b59a1fa`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-7405d2ca6e56a04d4f0b`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-8370dac4e15d975ae50c`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-b1150e2842703a15a0a0`
- Fix: State when to use the skill within the first 60 characters

**6. Frontmatter field(s) outside the agentskills.io spec: author, tags, version; agent harnesses do not pass them to the model**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `unknown_field`
- Finding ID: `SEF-2e27b4a077c9ee29b6f8`
- Occurrence ID: `SEO-751891c6f8591f9ed7ea`
- Fix: Remove them or move them under 'metadata'

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**Incomplete scanners:** skillspector

**9 errors, 4 warnings**

**Execution errors:**

- ❌ skillspector JSON field 'analysis_completeness' reports incomplete analysis (status 'partial'): SKILL.md:102 [reference_resolution; reference_missing]; references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md [static; static_parse_limit; analyzers=static_patterns_tool_misuse]; security scan did not complete

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/practice-cpp-specific.md:146</code> |
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/practice-cpp-specific.md:147</code> |
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1707</code> |
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1708</code> |
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/safety-threading-and-build.md:21</code> |
| [HIGH] HIGH | Prompt Injection:   | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1909</code> |
| [HIGH] HIGH | Tool Misuse: delete           // | <code>references/cpp-style-spec/safety-threading-and-build.md:139</code> |
| [HIGH] HIGH | Tool Misuse: delete           // | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:2027</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x89 | <code>references/cpp-style-spec/safety-types-and-data.md:17</code> |
| [MED] MEDIUM | Prompt Injection: U+0020 x89 | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1739</code> |
| ... | *2 more issues* | |

<details>
<summary>View Details</summary>

**1. Prompt Injection: ‌**
- File: `references/cpp-style-spec/practice-cpp-specific.md:146`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-8653030473307007c8c6`
- Occurrence ID: `SEO-40cae9816a2f7cb3b286`
- Content: `2-6-5-1、\[SC] C++代码中，设计类型转换时请不要使用C式的类型强转，而是使用C++标准库中提供的类型...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**2. Prompt Injection: ‌**
- File: `references/cpp-style-spec/practice-cpp-specific.md:147`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-8653030473307007c8c6`
- Occurrence ID: `SEO-a9f0c02638710564e4c8`
- Content: `static_cast：用于基本类型之间转换、派生类对象（指针）转换为基类对象（指针）的上行转化，编译器会做安全检...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**3. Prompt Injection: ‌**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1707`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-8653030473307007c8c6`
- Occurrence ID: `SEO-3c9bfaca2a1cdc65d381`
- Content: `2-6-5-1、\[SC] C++代码中，设计类型转换时请不要使用C式的类型强转，而是使用C++标准库中提供的类型...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**4. Prompt Injection: ‌**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1708`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-8653030473307007c8c6`
- Occurrence ID: `SEO-c5a4007e718aab0040a2`
- Content: `static_cast：用于基本类型之间转换、派生类对象（指针）转换为基类对象（指针）的上行转化，编译器会做安全检...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**5. Prompt Injection: ​**
- File: `references/cpp-style-spec/safety-threading-and-build.md:21`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-e9ee779440dec4ad4368`
- Occurrence ID: `SEO-732ee68167cbdf2bec2f`
- Content: `【设计类问题】

3-3-1-1、\[SC] 在设计加密验证相关的随机数产生上，必须使用跨平台通用的专用密码学库，...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**6. Prompt Injection: ​**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1909`
- Check: `Hidden Instructions (P2)`
- Finding ID: `SEF-e9ee779440dec4ad4368`
- Occurrence ID: `SEO-4ffda41ffced34513847`
- Content: `【设计类问题】

3-3-1-1、\[SC] 在设计加密验证相关的随机数产生上，必须使用跨平台通用的专用密码学库，...`
- Fix: Hidden instructions were detected in comments or invisible text. These could contain malicious directives. Manual review is recommended. Audit all comments and invisible characters. Remove any instructions that direct the agent to perform unauthorized actions. Use plain, reviewable content.

**7. Tool Misuse: delete           //**
- File: `references/cpp-style-spec/safety-threading-and-build.md:139`
- Check: `Tool Parameter Abuse (TM1)`
- Finding ID: `SEF-c0c7dab687f6e3118c0c`
- Occurrence ID: `SEO-4aa1d02e8777a46fb217`
- Content: `malloc()         // 内存分配
free()           // 内存释放
new    ...`
- Fix: Tool parameters are crafted to achieve unintended or unsafe behavior. Parameter abuse can bypass intended safety checks (e.g. shell=True, --force, dangerous glob patterns). Validate all tool parameters against an allowlist. Reject dangerous parameter values (shell=True, --force, -rf /) and use safe defaults.

**8. Tool Misuse: delete           //**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:2027`
- Check: `Tool Parameter Abuse (TM1)`
- Finding ID: `SEF-c0c7dab687f6e3118c0c`
- Occurrence ID: `SEO-3edef7bf7ef2a794669f`
- Content: `malloc()         // 内存分配
free()           // 内存释放
new    ...`
- Fix: Tool parameters are crafted to achieve unintended or unsafe behavior. Parameter abuse can bypass intended safety checks (e.g. shell=True, --force, dangerous glob patterns). Validate all tool parameters against an allowlist. Reject dangerous parameter values (shell=True, --force, -rf /) and use safe defaults.

**9. Prompt Injection: U+0020 x89**
- File: `references/cpp-style-spec/safety-types-and-data.md:17`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-6c2f5d080972d18524b0`
- Occurrence ID: `SEO-8e9b6b28eadb0ed1e9ce`
- Content: `3-1-1-1、\[SC]\[P] 变量定义时，请不要使用未定义长度（在不同平台下占用字节数不同）的基本类型变量，...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

**10. Prompt Injection: U+0020 x89**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1739`
- Check: `Whitespace Padding (P9)`
- Finding ID: `SEF-6c2f5d080972d18524b0`
- Occurrence ID: `SEO-ad35341cbb08d59d5a19`
- Content: `3-1-1-1、\[SC]\[P] 变量定义时，请不要使用未定义长度（在不同平台下占用字节数不同）的基本类型变量，...`
- Fix: Large whitespace padding was detected (a block of blank lines or a long run of spaces). This can push injected instructions below or to the right of the visible area so a human reviewer never sees them while the agent still reads them. Manual review of the hidden content is recommended. Remove the large whitespace padding (blank-line blocks or long space runs) and review any content hidden below or to the right of it. Keep skill files compact and reviewable so no instructions can be concealed off-screen.

*... and 2 more issues*

</details>


### ❌ PII Scan
*Detect PII and local identifiers*

**1 errors, 0 warnings**

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | Non-placeholder email address: liuguangyi@cviauto.com — 2 occurrences (references/cpp-style-spec/style-comments.md line 37; references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md line 893) | <code>references/cpp-style-spec/style-comments.md:37</code> |

<details>
<summary>View Details</summary>

**1. Non-placeholder email address: liuguangyi@cviauto.com — 2 occurrences (references/cpp-style-spec/style-comments.md line 37; references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md line 893)**
- File: `references/cpp-style-spec/style-comments.md:37`
- Check: `emails`
- Finding ID: `SEF-978b2c3d6919bf230525`
- Occurrence ID: `SEO-bbcafd99ccbaf11c5d3a`
- Content: `* Author: liuguangyi@cviauto.com / yuanchuqin@cviauto.com`
- Fix: Keep the metadata.author attribution. Replace other contact addresses with a handle, a contact-directory link, or user@example.com; use a reviewed --pii-waivers entry if the address is required.

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

- [OK] **dead_links_scan**: Checking 16 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 16 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: No standard Python test-file candidates found; target tests were not executed and coverage was not measured. Consider adding tests.

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 12**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/practice-cpp-specific.md:146</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/practice-cpp-specific.md:146</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/practice-cpp-specific.md:147</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/practice-cpp-specific.md:147</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/practice-cpp-specific.md:147</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH SPACE | <code>references/cpp-style-spec/safety-threading-and-build.md:21</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1707</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1707</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1708</code> |
| [LOW] LOW | Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER | <code>references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md:1708</code> |
| ... | *2 more issues* | |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/practice-cpp-specific.md:146`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-a2cd6d1c54761cd06796`
- Content: `dynamic_cast：支持␣安全的下行转换␣（基类指针转派生类指针）和多态类型转换，依赖RTTI在运行时检查类...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**2. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/practice-cpp-specific.md:146`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-a2cd6d1c54761cd06796`
- Content: `dynamic_cast：支持␣安全的下行转换␣（基类指针转派生类指针）和多态类型转换，依赖RTTI在运行时检查类...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**3. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/practice-cpp-specific.md:147`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-9d2d112a3a588ef1c148`
- Content: `reinterpret_cast：执行␣低级别的位模式重新解释␣，如将指针转换为不同类型的指针或整数，不进行类型检...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**4. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/practice-cpp-specific.md:147`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-9d2d112a3a588ef1c148`
- Content: `reinterpret_cast：执行␣低级别的位模式重新解释␣，如将指针转换为不同类型的指针或整数，不进行类型检...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**5. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/practice-cpp-specific.md:147`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-9d2d112a3a588ef1c148`
- Content: `reinterpret_cast：执行␣低级别的位模式重新解释␣，如将指针转换为不同类型的指针或整数，不进行类型检...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**6. Isolated invisible character(s) (1): ZERO WIDTH SPACE**
- File: `references/cpp-style-spec/safety-threading-and-build.md:21`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-188731305c957a99873b`
- Occurrence ID: `SEO-803743c942128587d522`
- Content: `3-3-1-1、\[SC] 在设计加密验证相关的随机数产生上，必须使用跨平台通用的专用密码学库，如OpenSSL、...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**7. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1707`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-4b7f5459c0bbd0d84671`
- Content: `dynamic_cast：支持␣安全的下行转换␣（基类指针转派生类指针）和多态类型转换，依赖RTTI在运行时检查类...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**8. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1707`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-4b7f5459c0bbd0d84671`
- Content: `dynamic_cast：支持␣安全的下行转换␣（基类指针转派生类指针）和多态类型转换，依赖RTTI在运行时检查类...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**9. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1708`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-05ca4a566e47392406c3`
- Content: `reinterpret_cast：执行␣低级别的位模式重新解释␣，如将指针转换为不同类型的指针或整数，不进行类型检...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

**10. Isolated invisible character(s) (1): ZERO WIDTH NON-JOINER**
- File: `references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md:1708`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-77cd94063d86ef41f4e2`
- Occurrence ID: `SEO-05ca4a566e47392406c3`
- Content: `reinterpret_cast：执行␣低级别的位模式重新解释␣，如将指针转换为不同类型的指针或整数，不进行类型检...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

*... and 2 more issues*

</details>


### ✅ B QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 84.8/100 (Grade: B)** | Skill Type: guide-only

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 85.0 | 35% |
| Discoverability | 85.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 84.8/100 (Grade: B)

**Non-blocking findings: 9**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | No examples provided | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | No limitations documented | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [LOW] LOW | No troubleshooting section documented | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. No examples provided**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-0d2215183b14101ae2c2`
- Occurrence ID: `SEO-ae055a75d055575c8d94`
- Fix: Add example usage with code blocks

**2. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-9471d86d3685d33571a2`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**3. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-6c2aa1642dbedc3759c6`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**4. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-58f50fe6b424caa5604e`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**5. No '## Purpose' section**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-08a3a5507a44393107dc`
- Fix: Add purpose section to clarify use cases

**6. No mention of error handling or validation**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-307e401c0fbfbf17b020`
- Fix: Document expected errors and how to handle them

**7. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-3b177c99328a7205057f`
- Fix: Document dependencies, API keys, or setup needed

**8. No limitations documented**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-fc6fe3747c071963a76e`
- Occurrence ID: `SEO-0feb6ea79131bf0e381c`
- Fix: Add '## Limitations' section with known issues/constraints

**9. No troubleshooting section documented**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-378f24adfec67572e606`
- Occurrence ID: `SEO-b9b33763279d15900e00`
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
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [INFO] INFO | hermes: 1 files outside references/, templates/, assets/ and scripts/ (agents) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [INFO] INFO | openclaw: 1 files over 64,000 bytes (references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [INFO] INFO | opencode: Skill list and text are cached at startup; edits need a restart. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |
| [INFO] INFO | opencode: 1 files are over 51,200 bytes or 2,000 lines (references/cpp-style-spec/source-of-truth/C&amp;Cpp编程规范-初稿v0.3.md); OpenCode's read tool returns at most that per call, so the model must page. | <code>/skills/library-20261118/G2/cxx-style-review/SKILL.md</code> |

<details>
<summary>View Details</summary>

**1. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-37446a8fb28cab29b391`

**2. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-3f36cf11e3df4ea1257f`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**3. hermes: 1 files outside references/, templates/, assets/ and scripts/ (agents) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-e843862971441e2bf711`
- Occurrence ID: `SEO-66e13a8e52cacd5647d6`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**4. openclaw: 1 files over 64,000 bytes (references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `OW-REF-BUDGET`
- Finding ID: `SEF-082fb053d8cd51583eab`
- Occurrence ID: `SEO-0e49d086176f406c68da`
- Fix: Split large reference files into pieces under 16,000 UTF-8 bytes.

**5. opencode: Skill list and text are cached at startup; edits need a restart.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `OC-RELOAD`
- Finding ID: `SEF-03e029934351881ba688`
- Occurrence ID: `SEO-5c46f1261c0fb44ed67c`

**6. opencode: 1 files are over 51,200 bytes or 2,000 lines (references/cpp-style-spec/source-of-truth/C&Cpp编程规范-初稿v0.3.md); OpenCode's read tool returns at most that per call, so the model must page.**
- File: `/skills/library-20261118/G2/cxx-style-review/SKILL.md`
- Check: `OC-REF-CUT`
- Finding ID: `SEF-e9710d8bc87e6bad3fa2`
- Occurrence ID: `SEO-986d385f0a5a868e87fa`
- Fix: Split large files into pieces under 51,200 bytes and 2,000 lines.

</details>


---
*Generated by SkillEvaluator*