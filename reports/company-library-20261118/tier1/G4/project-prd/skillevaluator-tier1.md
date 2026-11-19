# SkillEvaluator Validation Report

**Status:** ❌ FAILED
**Publication status:** ⚠️ INCOMPLETE
**Profile:** default
**Policy digest:** `sha256:64a069b8853f7123049a675d6853ef8d8b424792bb9a2a5157a73ec312f38ed4`
**Quality config:** packaged, `sha256:298ff2bf62132c8154217b7aa59fc1fd04f28cf75372f55620a2cbcd951d6549`, min score 70
**Generated:** November 18, 2026 at 01:11 AM UTC

## Summary

| Metric | Value |
|--------|-------|
| Validator Results | 13 |
| Validators Run | 13 |
| ✅ Passed | 12 |
| ❌ Failed | 1 |
| ⚠️ Incomplete | 1 |
| Total Issues | 60 unique findings (2 high, 29 medium) / 76 occurrences / 82 raw records; 1 error and 1 warning without a finding |
| Duplicate Occurrences Reconciled | 6 |

## Finding Reconciliation

| Finding ID | Severity | Finding | Occurrences | Validators |
|------------|----------|---------|-------------|------------|
| `SEF-0b791416cf84aa82b872` | HIGH | Data Exfiltration: dict(os.environ) | 2 | Security Scan |
| `SEF-1e083edfa44b2d1eb697` | HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | 1 | Security Scan |
| `SEF-5a78eaab07748c269628` | MEDIUM | Agent Snooping: skills/project-prd-writer/SKILL.md | 5 | Security Scan |
| `SEF-3ba83f5c183fc7b7758c` | MEDIUM | Dangerous Code Execution: subprocess.run(&#91;"git", "add", "."&#93;, cwd=self.root, check=True, capture&#95;output=True) | 4 | Security Scan |
| `SEF-1f501f96dd7342aa693c` | MEDIUM | Dangerous Code Execution: subprocess.run( &#91;"git", "-c", "user.name=Project PRD Test", "-c", "user.email=test&#64;example.com", "commit", "-m", commit&#95;message&#93;, cwd=self.root, check=True, captur | 2 | Security Scan |
| `SEF-3a6d95e70386bf224d4f` | MEDIUM | Agent Snooping: skills/project-prd-clear/SKILL.md | 2 | Security Scan |
| `SEF-53f0d09191614692d19d` | MEDIUM | Agent Snooping: skills/project-prd-serve/SKILL.md | 2 | Security Scan |
| `SEF-63f7398fc663022e64ea` | MEDIUM | Dangerous Code Execution: subprocess.run(&#91;"git", "init"&#93;, cwd=self.root, check=True, capture&#95;output=True) | 2 | Security Scan |
| `SEF-813a112beaaca49e0fe8` | MEDIUM | Dangerous Code Execution: subprocess.run( &#91;sys.executable, str(trusted&#95;guard), "ci", "--project-root", str(self.root), "--base-ref", base&#95;ref&#93;, cwd=self.root, text=True, capture&#95;output=True, check=False | 2 | Security Scan |
| `SEF-a16219cb5db8cad27c7c` | MEDIUM | Agent Snooping: skills/project-prd-verify/SKILL.md | 2 | Security Scan |
| ... | | *50 more unique findings* | | |

## Quality Score

| Skill | Score | Grade | Type | Correctness | Discoverability | Reliability | Efficiency |
|-------|-------|-------|------|-------------|-----------------|-------------|------------|
| project-prd | 77.0 | C | hybrid | 70.0 | 75.0 | 75.0 | 100.0 |

## Results

### ✅ Schema & Repository Governance
*Validate SKILL.md frontmatter and repository structure*

- [OK] **manifest_exists**: Found skill manifest: SKILL.md
- [OK] **frontmatter_valid**: Valid frontmatter for skill 'project-prd'
- [OK] **naming_convention**: Folder name 'project-prd' follows kebab-case convention
- [OK] **line_count**: SKILL.md within line limit (77/500)
- [OK] **body_heading**: Body contains a top-level heading
- [OK] **optional_files**: Found optional supporting files: README.md, agents, assets, references, scripts, tests
- [OK] **name_consistency**: Directory name matches frontmatter: 'project-prd'

**Non-blocking findings: 11**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | Unexpected nesting depth for general skill | <code>/skills/library-20261118/G4/project-prd</code> |
| [MED] MEDIUM | Missing recommended section: '## Instructions' | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [MED] MEDIUM | Missing recommended section: '## Examples' | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | Author not specified in metadata | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [MED] MEDIUM | Nested skill manifest 'assets/internal-skills/project-prd-writer/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it | <code>/skills/library-20261118/G4/project-prd/assets/internal-skills/project-prd-writer/SKILL.md</code> |
| [MED] MEDIUM | Nested skill manifest 'assets/project-skills/project-prd-clear/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it | <code>/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-clear/SKILL.md</code> |
| [MED] MEDIUM | Nested skill manifest 'assets/project-skills/project-prd-edit/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it | <code>/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-edit/SKILL.md</code> |
| [MED] MEDIUM | Nested skill manifest 'assets/project-skills/project-prd-serve/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it | <code>/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-serve/SKILL.md</code> |
| [MED] MEDIUM | Nested skill manifest 'assets/project-skills/project-prd-verify/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it | <code>/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-verify/SKILL.md</code> |
| [LOW] LOW | Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| ... | *1 more issues* | |

<details>
<summary>View Details</summary>

**1. Unexpected nesting depth for general skill**
- File: `/skills/library-20261118/G4/project-prd`
- Check: `folder_hierarchy`
- Finding ID: `SEF-18a7f8cc53f607ef9645`
- Occurrence ID: `SEO-a5bd3754d556bc636a36`
- Fix: General skills should be at: skills/<skill-name>/

**2. Missing recommended section: '## Instructions'**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-2ab016a817c566724ba9`
- Occurrence ID: `SEO-acb8834ba07cd83cbb65`
- Fix: Consider adding a '## Instructions' or '## Usage' section. Per agentskills.io the body format is unrestricted, so this is a convention nudge — it also gives the quality scorer a stable anchor for instruction-quality heuristics.

**3. Missing recommended section: '## Examples'**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `body_recommended_section`
- Finding ID: `SEF-e3f5c930756d6b8f695b`
- Occurrence ID: `SEO-c67d35b0bf65b139f9cb`
- Fix: Consider adding a '## Examples' section. If examples are already inline under instructions, this can be skipped.

**4. Author not specified in metadata**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `author_missing`
- Finding ID: `SEF-7d8d9f72f99ec61dbf58`
- Occurrence ID: `SEO-288c29dec365b7ff3fd4`
- Fix: Add 'metadata.author' with a person, team, or organization name, or 'Name <email@example.com>' to include a contact address

**5. Nested skill manifest 'assets/internal-skills/project-prd-writer/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it**
- File: `/skills/library-20261118/G4/project-prd/assets/internal-skills/project-prd-writer/SKILL.md`
- Check: `nested_manifest`
- Finding ID: `SEF-d1900a0b496a721d852b`
- Occurrence ID: `SEO-84cd6a87c5beeec2a68c`
- Fix: Rename the nested file or move it out of the skill folder

**6. Nested skill manifest 'assets/project-skills/project-prd-clear/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it**
- File: `/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-clear/SKILL.md`
- Check: `nested_manifest`
- Finding ID: `SEF-b3010a2c75b64b875f38`
- Occurrence ID: `SEO-98d084a70b831f23e875`
- Fix: Rename the nested file or move it out of the skill folder

**7. Nested skill manifest 'assets/project-skills/project-prd-edit/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it**
- File: `/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-edit/SKILL.md`
- Check: `nested_manifest`
- Finding ID: `SEF-6e9a0dff9ac19a9727d4`
- Occurrence ID: `SEO-c50846e2fdce8121e76e`
- Fix: Rename the nested file or move it out of the skill folder

**8. Nested skill manifest 'assets/project-skills/project-prd-serve/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it**
- File: `/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-serve/SKILL.md`
- Check: `nested_manifest`
- Finding ID: `SEF-2eb3906b9d6ced64921c`
- Occurrence ID: `SEO-ebbaff4fdd447efd87f9`
- Fix: Rename the nested file or move it out of the skill folder

**9. Nested skill manifest 'assets/project-skills/project-prd-verify/SKILL.md' inside this skill; Codex, OpenCode and Hermes load it as a separate skill, others ignore it**
- File: `/skills/library-20261118/G4/project-prd/assets/project-skills/project-prd-verify/SKILL.md`
- Check: `nested_manifest`
- Finding ID: `SEF-edb585d8c6f7c746207e`
- Occurrence ID: `SEO-877b09976d67144a6406`
- Fix: Rename the nested file or move it out of the skill folder

**10. Description has no 'Use when ...' trigger; some harnesses show only the first ~60 characters in their skill list**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `description_trigger`
- Finding ID: `SEF-29923f4d680e578e37e3`
- Occurrence ID: `SEO-039aa4fbf16ddbcc309b`
- Fix: State when to use the skill within the first 60 characters

*... and 1 more issues*

</details>


### ✅ Semantic Version Validation
*Validate optional metadata.version labels and require strict bumps*

- [OK] **version_optional**: No semantic version label present; resource will use commit-hash history

### ❌ Security Scan
*Detect security vulnerabilities and PII/secrets*

**Incomplete scanners:** skillspector

**9 errors, 32 warnings**

**Execution errors:**

- ❌ skillspector JSON field 'analysis_completeness' reports incomplete analysis (status 'partial'): SKILL.md:40 [reference_resolution; reference_missing]; SKILL.md:49 [reference_resolution; reference_missing]; SKILL.md:51 [reference_resolution; reference_missing]; and 4 more (incomplete files by reason: static_parse_limit 3, reference_missing 1, obfuscated_instruction_text 1); security scan did not complete

| Severity | Issue | Location |
|----------|-------|----------|
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou | <code>SKILL.md:1</code> |
| [HIGH] HIGH | Data Exfiltration: dict(os.environ) | <code>tests/test_workflow.py:1264</code> |
| [HIGH] HIGH | Data Exfiltration: dict(os.environ) | <code>tests/test_workflow.py:1309</code> |
| [MED] MEDIUM | MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated. | <code>SKILL.md:1</code> |
| [MED] MEDIUM | Agent Snooping: skills/project-prd-writer/SKILL.md | <code>SKILL.md:50</code> |
| ... | *30 more issues* | |

<details>
<summary>View Details</summary>

**1. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**2. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**3. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**4. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**5. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**6. MCP Tool Poisoning: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguou**
- File: `SKILL.md:1`
- Check: `Unknown (TP2)`
- Finding ID: `SEF-1e083edfa44b2d1eb697`
- Occurrence ID: `SEO-7cf3bf45f2b335ff0408`
- Fix: Mixing characters from multiple Unicode scripts in a single identifier is a common technique to create visually ambiguous tool names. Restrict identifier fields to a single Unicode script. Prefer ASCII-only identifiers.

**7. Data Exfiltration: dict(os.environ)**
- File: `tests/test_workflow.py:1264`
- Check: `Env Variable Harvesting (E2)`
- Finding ID: `SEF-0b791416cf84aa82b872`
- Occurrence ID: `SEO-f9b874c4c416d1f393f1`
- Content: `)

        trusted_guard = SKILL_ROOT / "assets" / "runti...`
- Fix: Code enumerates, copies, or searches environment variables for secrets. Bulk environment access can collect credentials unrelated to the skill's stated purpose. Read only explicitly required environment variables by name. Avoid enumerating or copying the full environment, and never log or transmit credentials to untrusted destinations.

**8. Data Exfiltration: dict(os.environ)**
- File: `tests/test_workflow.py:1309`
- Check: `Env Variable Harvesting (E2)`
- Finding ID: `SEF-0b791416cf84aa82b872`
- Occurrence ID: `SEO-96a7b29b9f6ccfebf24e`
- Content: `)

        trusted_guard = SKILL_ROOT / "assets" / "runti...`
- Fix: Code enumerates, copies, or searches environment variables for secrets. Bulk environment access can collect credentials unrelated to the skill's stated purpose. Read only explicitly required environment variables by name. Avoid enumerating or copying the full environment, and never log or transmit credentials to untrusted destinations.

**9. MCP Least Privilege: Without declared permissions the skill's intent is opaque and cannot be validated.**
- File: `SKILL.md:1`
- Check: `Unknown (LP3)`
- Finding ID: `SEF-8e1fcdbf37b720508663`
- Occurrence ID: `SEO-c04b8c5539e90a8aac9b`
- Fix: Without declared permissions the skill's intent is opaque and cannot be validated. Declare the skill's tool scope: for Claude Code / Agent Skills SKILL.md, list the tools the skill may invoke in the 'allowed-tools' frontmatter field; for MCP server manifests, add a 'permissions' list naming the required capabilities.

**10. Agent Snooping: skills/project-prd-writer/SKILL.md**
- File: `SKILL.md:50`
- Check: `Skill Enumeration (AS3)`
- Finding ID: `SEF-5a78eaab07748c269628`
- Occurrence ID: `SEO-ee68c9ecefae1be8aaaf`
- Content: `ory_contract` 的分类契约，并为每个成员记录至少两个 `category_fit` 源码证据，再建立一...`
- Fix: Skill enumerates or reads other installed skills. Access to other skills' SKILL.md files or the skills directory reveals prompt instructions, capabilities, and secrets that should be invisible to peer skills. Remove all code or instructions that list or read other skills' files or directories. Skills should operate independently; cross-skill access is a privilege escalation.

*... and 30 more issues*

</details>


### ✅ PII Scan
*Detect PII and local identifiers*

- [OK] **pii_scan_start**: Scanning 27 files for PII
- [OK] **pii_detection**: No PII detected in 27 files (emails, SSNs, phone numbers, paths)

### ✅ License Compliance
*Validate license compliance for Skills, Rules, and Workflows*

- [OK] **license_compliance**: License compliance scan completed (not detected)

### ✅ Code Risk Analysis
*Static code analysis using Bandit and packaged Semgrep rules*

- [OK] **bandit**: Bandit: No security issues found

### ✅ Secrets Detection
*Detect hardcoded secrets, API keys, and credentials using Gitleaks*

- [OK] **gitleaks**: No secrets detected by Gitleaks

### ✅ Code Integrity & Hygiene
*Validate dead links, dependencies, and static Python test-file discovery*

- [OK] **dead_links_scan**: Checking 15 markdown files for dead links
- [OK] **dead_links**: All relative links valid in 15 markdown file(s)
- [OK] **dependencies**: No dependency files found (requirements.txt, pyproject.toml)
- [OK] **test_discovery**: Found 2 standard Python test-file candidate(s); target tests were not executed and coverage was not measured

### ✅ Dependency Vulnerability Audit
*Scan dependencies for CVE vulnerabilities using pip-audit and Safety*

- [OK] **dependency_file_discovery**: No dependency files found - vulnerability audit is not applicable

### ✅ Unicode Smuggling Detection
*Detect invisible Unicode characters and ASCII smuggling*

- All checks passed

**Non-blocking findings: 1**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | Isolated invisible character(s) (1): VARIATION SELECTOR-16 | <code>README.md:6</code> |

<details>
<summary>View Details</summary>

**1. Isolated invisible character(s) (1): VARIATION SELECTOR-16**
- File: `README.md:6`
- Check: `isolated_invisible_char`
- Finding ID: `SEF-6b66555d1029e567b59c`
- Occurrence ID: `SEO-132b00170693efd7ec30`
- Content: `> ⚠️ **重要提示：`project-prd` 首次初始化会整体阅读项目源码、提炼功能边界、拆分 Featur...`
- Fix: Likely a copy-paste artifact. Remove if not intentional.

</details>


### ✅ C QUALITY
*Skill quality scoring across Correctness (35%), Discoverability (25%), Reliability (25%), and Efficiency (15%)*

**Overall: 77.0/100 (Grade: C)** | Skill Type: hybrid

| Dimension | Score | Weight |
|-----------|-------|--------|
| Correctness | 70.0 | 35% |
| Discoverability | 75.0 | 25% |
| Reliability | 75.0 | 25% |
| Efficiency | 100.0 | 15% |

- [OK] **quality_score**: Score: 77.0/100 (Grade: C)

**Non-blocking findings: 12**

| Severity | Issue | Location |
|----------|-------|----------|
| [MED] MEDIUM | No documented scripts in table format | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [MED] MEDIUM | Instructions don't mention 'run_script' | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.author' | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [MED] MEDIUM | SKILL_SPEC recommended field missing: 'metadata.tags' | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | Description very long (314 chars, recommend 50-150) | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | Description doesn't mention WHEN to use this skill | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | Broad description without negative triggers may cause over-triggering | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | No '## Purpose' section | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | No mention of error handling or validation | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | No prerequisites/requirements documented | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| ... | *2 more issues* | |

<details>
<summary>View Details</summary>

**1. No documented scripts in table format**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-740453e5661b3b5b6f1e`
- Occurrence ID: `SEO-e7d47023fe2869c62086`
- Fix: Add '## Available Scripts' with table: | Script | Purpose | Arguments |

**2. Instructions don't mention 'run_script'**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-6d68dab37ccc357a6814`
- Occurrence ID: `SEO-1baad01504f4a1f08ae9`
- Fix: Add explicit run_script() call examples

**3. SKILL_SPEC recommended field missing: 'metadata.author'**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-bf2d85d8c9d7a282e7ad`
- Occurrence ID: `SEO-93636588ec23c98ac16c`
- Fix: Add 'author' under metadata: — Author name or team (under metadata:)

**4. SKILL_SPEC recommended field missing: 'metadata.tags'**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_correctness`
- Finding ID: `SEF-dd828fd8f6476dc5f3c7`
- Occurrence ID: `SEO-4070d9358f06fd578afb`
- Fix: Add 'tags' under metadata: — Categorization tags (under metadata:, list of 1-5 items)

**5. Description very long (314 chars, recommend 50-150)**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-98b1acf530376cbc51f7`
- Occurrence ID: `SEO-c6a412220ef2264e914d`
- Fix: Keep descriptions concise for progressive disclosure

**6. Description doesn't mention WHEN to use this skill**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-0f3cde56a46498377f1a`
- Occurrence ID: `SEO-d04744e277f41153421b`
- Fix: Add trigger context: 'Use for...', 'When you need to...'

**7. Broad description without negative triggers may cause over-triggering**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-1017300978cb9cb0eae9`
- Occurrence ID: `SEO-951fcd1f8911ab15aa76`
- Fix: Add boundary phrases like 'Do NOT use for...'

**8. No '## Purpose' section**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_discoverability`
- Finding ID: `SEF-b6533ad44b39dbc6d0d2`
- Occurrence ID: `SEO-2b0cfdf8573e60d1f52e`
- Fix: Add purpose section to clarify use cases

**9. No mention of error handling or validation**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-9612bbfb3f32d491ac5d`
- Occurrence ID: `SEO-ad2918237d78aa0815cd`
- Fix: Document expected errors and how to handle them

**10. No prerequisites/requirements documented**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `quality_reliability`
- Finding ID: `SEF-4a6560f4aec006f302f9`
- Occurrence ID: `SEO-32642532206a247b0b85`
- Fix: Document dependencies, API keys, or setup needed

*... and 2 more issues*

</details>


### ✅ SCRIPT_LINT
*AST-based code quality checks for skill scripts*

- All checks passed

**Non-blocking findings: 3**

| Severity | Issue | Location |
|----------|-------|----------|
| [LOW] LOW | bootstrap.py contains magic numbers | <code>/skills/library-20261118/G4/project-prd/scripts/bootstrap.py</code> |
| [MED] MEDIUM | project_prd_lib.py has deeply nested code (depth 9, max 6) | <code>/skills/library-20261118/G4/project-prd/scripts/project_prd_lib.py</code> |
| [LOW] LOW | project_prd_lib.py contains magic numbers | <code>/skills/library-20261118/G4/project-prd/scripts/project_prd_lib.py</code> |

<details>
<summary>View Details</summary>

**1. bootstrap.py contains magic numbers**
- File: `/skills/library-20261118/G4/project-prd/scripts/bootstrap.py`
- Check: `magic_numbers`
- Finding ID: `SEF-adb2fa0e642297608620`
- Occurrence ID: `SEO-40cd788927895112d99d`
- Fix: Extract magic numbers to named constants

**2. project_prd_lib.py has deeply nested code (depth 9, max 6)**
- File: `/skills/library-20261118/G4/project-prd/scripts/project_prd_lib.py`
- Check: `deep_nesting`
- Finding ID: `SEF-2dd1395726ab47ae9f9c`
- Occurrence ID: `SEO-6a15a8f42e768d037700`
- Fix: Refactor into smaller functions to reduce complexity

**3. project_prd_lib.py contains magic numbers**
- File: `/skills/library-20261118/G4/project-prd/scripts/project_prd_lib.py`
- Check: `magic_numbers`
- Finding ID: `SEF-9c7805c625bce98faee1`
- Occurrence ID: `SEO-8cddb6529a18729ef918`
- Fix: Extract magic numbers to named constants

</details>


### ✅ Harness Compatibility
*Advisory: whether each agent harness loads, degrades or drops the skill*

- All checks passed

**Non-blocking findings: 15**

| Severity | Issue | Location |
|----------|-------|----------|
| [INFO] INFO | claude-code: Frontmatter is stripped when the skill is used, so the text in triggers, requires never reaches the model. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | codex: The nested SKILL.md is loaded as a second, separate skill. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Nested SKILL.md is ignored. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | copilot-cli: New skills appear only after &#96;/skills reload&#96; or a restart; edits to existing skills apply at once. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | copilot-cli: Frontmatter is stripped when the skill is used, so the text in triggers, requires never reaches the model. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [LOW] LOW | hermes: The nested SKILL.md is loaded as a second, separate skill (hidden folders are walked too). | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | hermes: 5 files outside references/, templates/, assets/ and scripts/ (README.md, agents, tests) are left out of the skill's file list; the model finds them only if SKILL.md names their paths. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | openclaw: Nested SKILL.md is ignored. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| [INFO] INFO | openclaw: 2 files over 64,000 bytes (scripts/project_prd_lib.py, tests/test_workflow.py): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads. | <code>/skills/library-20261118/G4/project-prd/SKILL.md</code> |
| ... | *5 more issues* | |

<details>
<summary>View Details</summary>

**1. claude-code: Frontmatter is stripped when the skill is used, so the text in triggers, requires never reaches the model.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `CC-FM-STRIPPED`
- Finding ID: `SEF-601ac774197bd878e4e1`
- Occurrence ID: `SEO-451a2ac3c405a850c806`
- Fix: Move instructions from frontmatter into the SKILL.md body.

**2. codex: The nested SKILL.md is loaded as a second, separate skill.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `CX-NESTED`
- Finding ID: `SEF-eec472f948fb7912b1e7`
- Occurrence ID: `SEO-79664c00ecc19bf59698`
- Fix: Move the nested skill to its own folder under the skills root, or rename its SKILL.md.

**3. copilot-cli: Nested SKILL.md is ignored.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `CP-NESTED`
- Finding ID: `SEF-8c58fb76e06a319c3c4a`
- Occurrence ID: `SEO-77505270deeed0ddf013`
- Fix: Move the nested skill to its own folder under the skills root, or rename its SKILL.md.

**4. copilot-cli: New skills appear only after `/skills reload` or a restart; edits to existing skills apply at once.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `CP-RELOAD`
- Finding ID: `SEF-3661379ea9e5c1072875`
- Occurrence ID: `SEO-2a95111675f1c78324a1`

**5. copilot-cli: Frontmatter is stripped when the skill is used, so the text in triggers, requires never reaches the model.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `CP-FM-STRIPPED`
- Finding ID: `SEF-c0e7216e7caced696a99`
- Occurrence ID: `SEO-11cac5f7d607d562c4d6`
- Fix: Move instructions from frontmatter into the SKILL.md body.

**6. hermes: The skill list shows only the first ~60 chars of the description (57 + '...' in 0.16, a word boundary near 59 on main), and the trigger isn't in them.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `HM-DESC-60`
- Finding ID: `SEF-e0623bdfb91d6bbb829f`
- Occurrence ID: `SEO-7ca5be348549cf0227d3`
- Fix: Put the trigger ("Use when …") in the first 57 characters.

**7. hermes: The nested SKILL.md is loaded as a second, separate skill (hidden folders are walked too).**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `HM-NESTED`
- Finding ID: `SEF-9177da53332cc5f39682`
- Occurrence ID: `SEO-f9964fdf6c35c20e0173`
- Fix: Move the nested skill to its own folder under the skills root, or rename its SKILL.md.

**8. hermes: 5 files outside references/, templates/, assets/ and scripts/ (README.md, agents, tests) are left out of the skill's file list; the model finds them only if SKILL.md names their paths.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `HM-LINKED-LAYOUT`
- Finding ID: `SEF-ed2d9b99e7a10ce01550`
- Occurrence ID: `SEO-3d7ec8a552387dc6e7c0`
- Fix: Move supporting files under references/, templates/, assets/ or scripts/.

**9. openclaw: Nested SKILL.md is ignored.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `OW-NESTED`
- Finding ID: `SEF-72f27d1ea0644635a986`
- Occurrence ID: `SEO-65d9adbf35d0c6ff00b8`
- Fix: Move the nested skill to its own folder under the skills root, or rename its SKILL.md.

**10. openclaw: 2 files over 64,000 bytes (scripts/project_prd_lib.py, tests/test_workflow.py): OpenClaw's read cap is 16,000-64,000 UTF-8 bytes by model context, so each takes several reads.**
- File: `/skills/library-20261118/G4/project-prd/SKILL.md`
- Check: `OW-REF-BUDGET`
- Finding ID: `SEF-5e6866972ad60e923fd9`
- Occurrence ID: `SEO-49a60bcd71c3ac4ecb85`
- Fix: Split large reference files into pieces under 16,000 UTF-8 bytes.

*... and 5 more issues*

</details>


---
*Generated by SkillEvaluator*